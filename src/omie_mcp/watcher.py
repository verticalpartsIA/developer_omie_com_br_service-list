from __future__ import annotations

import difflib
import hashlib
import json
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import httpx

from .catalog import fetch_service_catalog, serialize_catalog
from .config import settings


@dataclass(slots=True)
class Snapshot:
    captured_at: str
    service_list_hash: str
    service_list_text: str
    catalog: list[dict[str, Any]]


def _normalize_text(text: str) -> str:
    lines = [" ".join(line.split()) for line in text.splitlines()]
    return "\n".join(line for line in lines if line)


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _state_path() -> Path:
    path = settings.omie_state_dir
    path.mkdir(parents=True, exist_ok=True)
    return path / "service-list.snapshot.json"


async def capture_snapshot() -> Snapshot:
    async with httpx.AsyncClient(timeout=settings.omie_http_timeout, follow_redirects=True) as http:
        response = await http.get(settings.omie_service_list_url)
        response.raise_for_status()
    normalized = _normalize_text(response.text)
    catalog = serialize_catalog(await fetch_service_catalog())
    return Snapshot(
        captured_at=datetime.now(timezone.utc).isoformat(),
        service_list_hash=_sha(normalized),
        service_list_text=normalized,
        catalog=catalog,
    )


def load_snapshot() -> Snapshot | None:
    path = _state_path()
    if not path.exists():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    return Snapshot(**data)


def save_snapshot(snapshot: Snapshot) -> None:
    _state_path().write_text(
        json.dumps(asdict(snapshot), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def _catalog_map(snapshot: Snapshot) -> dict[str, dict[str, Any]]:
    return {row["endpoint"]: row for row in snapshot.catalog}


async def diff_official_docs(*, persist_new_snapshot: bool = True) -> dict[str, Any]:
    previous = load_snapshot()
    current = await capture_snapshot()

    if previous is None:
        if persist_new_snapshot:
            save_snapshot(current)
        return {
            "status": "baseline_created",
            "captured_at": current.captured_at,
            "service_count": len(current.catalog),
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
    unified = []
    if text_changed:
        unified = list(
            difflib.unified_diff(
                previous.service_list_text.splitlines(),
                current.service_list_text.splitlines(),
                fromfile=previous.captured_at,
                tofile=current.captured_at,
                lineterm="",
                n=2,
            )
        )[:400]

    result = {
        "status": "changed" if (text_changed or added or removed or changed_entries) else "unchanged",
        "previous_captured_at": previous.captured_at,
        "current_captured_at": current.captured_at,
        "hash_before": previous.service_list_hash,
        "hash_after": current.service_list_hash,
        "text_changed": text_changed,
        "services_before": len(previous.catalog),
        "services_after": len(current.catalog),
        "added_services": added,
        "removed_services": removed,
        "changed_services": changed_entries,
        "text_diff_preview": unified,
    }

    if persist_new_snapshot:
        save_snapshot(current)
    return result
