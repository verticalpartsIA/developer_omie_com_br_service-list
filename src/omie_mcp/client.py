from __future__ import annotations

import asyncio
import hashlib
import json
import time
from dataclasses import dataclass
from typing import Any

import httpx

from .config import settings


READ_PREFIXES = (
    "listar",
    "consultar",
    "obter",
    "pesquisar",
    "resumo",
    "status",
    "listar",
    "buscar",
)


class OmieError(RuntimeError):
    pass


class OmieWriteBlocked(OmieError):
    pass


@dataclass(slots=True)
class RecentRequest:
    fingerprint: str
    timestamp: float


class OmieClient:
    def __init__(self) -> None:
        self._recent: RecentRequest | None = None
        self._lock = asyncio.Lock()

    @staticmethod
    def normalize_endpoint(endpoint: str) -> str:
        endpoint = endpoint.strip()
        if endpoint.startswith("http://") or endpoint.startswith("https://"):
            allowed = settings.omie_api_base.rstrip("/") + "/"
            if not endpoint.startswith(allowed):
                raise OmieError("Endpoint externo bloqueado. Use apenas a API oficial do Omie.")
            return endpoint.rstrip("/") + "/"
        return f"{settings.omie_api_base.rstrip('/')}/{endpoint.strip('/')}/"

    @staticmethod
    def is_read_call(call: str) -> bool:
        normalized = "".join(ch for ch in call.lower() if ch.isalnum())
        return normalized.startswith(READ_PREFIXES)

    @staticmethod
    def fingerprint(endpoint: str, call: str, param: list[dict[str, Any]]) -> str:
        payload = json.dumps(
            {"endpoint": endpoint, "call": call, "param": param},
            sort_keys=True,
            ensure_ascii=False,
            default=str,
        )
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    async def call(
        self,
        endpoint: str,
        call: str,
        param: list[dict[str, Any]] | dict[str, Any] | None = None,
        *,
        confirm_write: bool = False,
    ) -> dict[str, Any]:
        settings.require_credentials()
        url = self.normalize_endpoint(endpoint)
        params = param if isinstance(param, list) else [param or {}]

        read_only = self.is_read_call(call)
        if not read_only:
            if not settings.omie_allow_writes:
                raise OmieWriteBlocked(
                    "Operação de escrita bloqueada por OMIE_ALLOW_WRITES=false."
                )
            if not confirm_write:
                raise OmieWriteBlocked(
                    "Operação potencialmente mutável exige confirm_write=true."
                )

        fp = self.fingerprint(url, call, params)
        async with self._lock:
            now = time.monotonic()
            if self._recent and self._recent.fingerprint == fp:
                elapsed = now - self._recent.timestamp
                if elapsed < 1.2:
                    await asyncio.sleep(1.2 - elapsed)
            self._recent = RecentRequest(fp, time.monotonic())

        body = {
            "call": call,
            "app_key": settings.omie_app_key,
            "app_secret": settings.omie_app_secret,
            "param": params,
        }

        timeout = httpx.Timeout(settings.omie_http_timeout)
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(url, json=body)

        try:
            data = response.json()
        except ValueError as exc:
            raise OmieError(f"Resposta não-JSON do Omie: HTTP {response.status_code}") from exc

        if response.is_error:
            message = data.get("faultstring") or data.get("message") or str(data)
            raise OmieError(f"Omie HTTP {response.status_code}: {message}")

        if isinstance(data, dict) and ("faultcode" in data or "faultstring" in data):
            raise OmieError(data.get("faultstring") or str(data))

        return data


client = OmieClient()
