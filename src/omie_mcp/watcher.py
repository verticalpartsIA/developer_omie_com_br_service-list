from __future__ import annotations

import asyncio
import difflib
import hashlib
import json
import re
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import httpx

from .catalog import fetch_service_catalog, serialize_catalog
from .config import settings

# O servidor do Omie gera um nonce de CSP novo a cada resposta HTTP (mesmo conteúdo,
# mesma página) — sem isso, TODA página aparenta ter mudado em TODA execução do radar.
_VOLATILE_NONCE_RE = re.compile(r'nonce="[^"]*"')


@dataclass(slots=True)
class Snapshot:
    captured_at: str
    service_list_hash: str
    service_list_text: str
    catalog: list[dict[str, Any]]
    service_pages: dict[str, dict[str, Any]]


def _normalize_text(text: str) -> str:
    text = _VOLATILE_NONCE_RE.sub('nonce="STRIPPED"', text)
    lines = [" ".join(line.split()) for line in text.splitlines()]
    return "\n".join(line for line in lines if line)


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _state_path() -> Path:
    path = settings.omie_state_dir
    path.mkdir(parents=True, exist_ok=True)
    return path / "service-list.snapshot.json"


async def _capture_service_pages(catalog: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    semaphore = asyncio.Semaphore(8)
    timeout = httpx.Timeout(settings.omie_http_timeout)

    async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as http:
        async def capture(entry: dict[str, Any]) -> tuple[str, dict[str, Any]]:
            endpoint = entry["endpoint"]
            async with semaphore:
                try:
                    response = await http.get(endpoint)
                    text = _normalize_text(response.text)
                    return endpoint, {
                        "status": response.status_code,
                        "content_type": response.headers.get("content-type"),
                        "hash": _sha(text),
                        "text": text,
                    }
                except Exception as exc:  # radar deve continuar mesmo se 1 serviço falhar
                    return endpoint, {
                        "status": None,
                        "content_type": None,
                        "hash": None,
                        "text": "",
                        "error": str(exc),
                    }

        pairs = await asyncio.gather(*(capture(entry) for entry in catalog))
    return dict(pairs)


async def capture_snapshot(*, deep: bool = True) -> Snapshot:
    async with httpx.AsyncClient(timeout=settings.omie_http_timeout, follow_redirects=True) as http:
        response = await http.get(settings.omie_service_list_url)
        response.raise_for_status()

    normalized = _normalize_text(response.text)
    catalog = serialize_catalog(await fetch_service_catalog())
    service_pages = await _capture_service_pages(catalog) if deep else {}

    return Snapshot(
        captured_at=datetime.now(timezone.utc).isoformat(),
        service_list_hash=_sha(normalized),
        service_list_text=normalized,
        catalog=catalog,
        service_pages=service_pages,
    )


def load_snapshot() -> Snapshot | None:
    path = _state_path()
    if not path.exists():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    data.setdefault("service_pages", {})
    return Snapshot(**data)


def save_snapshot(snapshot: Snapshot) -> None:
    _state_path().write_text(
        json.dumps(asdict(snapshot), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def _catalog_map(snapshot: Snapshot) -> dict[str, dict[str, Any]]:
    return {row["endpoint"]: row for row in snapshot.catalog}


def _text_diff(before: str, after: str, before_name: str, after_name: str, limit: int = 240) -> list[str]:
    return list(
        difflib.unified_diff(
            before.splitlines(),
            after.splitlines(),
            fromfile=before_name,
            tofile=after_name,
            lineterm="",
            n=2,
        )
    )[:limit]


async def diff_official_docs(*, persist_new_snapshot: bool = True, deep: bool = True) -> dict[str, Any]:
    previous = load_snapshot()
    current = await capture_snapshot(deep=deep)

    if previous is None:
        if persist_new_snapshot:
            save_snapshot(current)
        return {
            "status": "baseline_created",
            "captured_at": current.captured_at,
            "service_count": len(current.catalog),
            "deep_scan": deep,
            "message": "Primeiro snapshot criado; execute novamente para detectar mudanças.",
        }

    before = _catalog_map(previous)
    after = _catalog_map(current)
    added = [after[key] for key in sorted(after.keys() - before.keys())]
    removed = [before[key] for key in sorted(before.keys() - after.keys())]
    changed_entries = []
    for endpoint in sorted(before.keys() & after.keys()):
        if before[endpoint] != after[endpoint]:
            changed_entries.append({"before": before[endpoint], "after": after[endpoint]})

    text_changed = previous.service_list_hash != current.service_list_hash
    service_list_diff = []
    if text_changed:
        service_list_diff = _text_diff(
            previous.service_list_text,
            current.service_list_text,
            previous.captured_at,
            current.captured_at,
            limit=400,
        )

    changed_pages: list[dict[str, Any]] = []
    if deep:
        all_pages = sorted(set(previous.service_pages) | set(current.service_pages))
        for endpoint in all_pages:
            old = previous.service_pages.get(endpoint)
            new = current.service_pages.get(endpoint)
            if old is None or new is None or old.get("hash") != new.get("hash"):
                changed_pages.append(
                    {
                        "endpoint": endpoint,
                        "before_hash": old.get("hash") if old else None,
                        "after_hash": new.get("hash") if new else None,
                        "before_status": old.get("status") if old else None,
                        "after_status": new.get("status") if new else None,
                        "diff_preview": _text_diff(
                            old.get("text", "") if old else "",
                            new.get("text", "") if new else "",
                            f"{endpoint}@before",
                            f"{endpoint}@after",
                        ) if old and new else [],
                    }
                )

    changed = bool(text_changed or added or removed or changed_entries or changed_pages)
    result = {
        "status": "changed" if changed else "unchanged",
        "previous_captured_at": previous.captured_at,
        "current_captured_at": current.captured_at,
        "deep_scan": deep,
        "hash_before": previous.service_list_hash,
        "hash_after": current.service_list_hash,
        "text_changed": text_changed,
        "services_before": len(previous.catalog),
        "services_after": len(current.catalog),
        "added_services": added,
        "removed_services": removed,
        "changed_services": changed_entries,
        "changed_service_pages": changed_pages,
        "service_list_diff_preview": service_list_diff,
    }

    if persist_new_snapshot:
        save_snapshot(current)
    return result
