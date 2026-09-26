from __future__ import annotations

import asyncio
import copy
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
    "buscar",
)
READ_CACHE_TTL_SECONDS = 45.0
REDUNDANT_RETRY_DELAYS = (1.5, 3.0)


class OmieError(RuntimeError):
    pass


class OmieWriteBlocked(OmieError):
    pass


@dataclass(slots=True)
class RecentRequest:
    fingerprint: str
    timestamp: float


@dataclass(slots=True)
class CachedResponse:
    timestamp: float
    data: dict[str, Any]


class OmieClient:
    def __init__(self) -> None:
        self._recent: RecentRequest | None = None
        self._read_cache: dict[str, CachedResponse] = {}
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

    def _get_cached(self, fingerprint: str) -> dict[str, Any] | None:
        cached = self._read_cache.get(fingerprint)
        if cached is None:
            return None
        if time.monotonic() - cached.timestamp > READ_CACHE_TTL_SECONDS:
            self._read_cache.pop(fingerprint, None)
            return None
        return copy.deepcopy(cached.data)

    def _set_cached(self, fingerprint: str, data: dict[str, Any]) -> None:
        self._read_cache[fingerprint] = CachedResponse(time.monotonic(), copy.deepcopy(data))
        if len(self._read_cache) > 256:
            oldest = min(self._read_cache, key=lambda key: self._read_cache[key].timestamp)
            self._read_cache.pop(oldest, None)

    @staticmethod
    def _fault_message(data: Any) -> str:
        if not isinstance(data, dict):
            return str(data)
        return str(data.get("faultstring") or data.get("message") or data.get("description") or data)

    @staticmethod
    def _is_redundant_fault(message: str) -> bool:
        normalized = message.casefold()
        return "consumo redundante" in normalized or "redundante detectado" in normalized

    async def _post(self, url: str, body: dict[str, Any]) -> dict[str, Any]:
        timeout = httpx.Timeout(settings.omie_http_timeout)
        async with httpx.AsyncClient(timeout=timeout) as http:
            response = await http.post(url, json=body)
        try:
            data = response.json()
        except ValueError as exc:
            raise OmieError(f"Resposta não-JSON do Omie: HTTP {response.status_code}") from exc

        if response.is_error:
            raise OmieError(f"Omie HTTP {response.status_code}: {self._fault_message(data)}")
        if isinstance(data, dict) and ("faultcode" in data or "faultstring" in data):
            raise OmieError(self._fault_message(data))
        if not isinstance(data, dict):
            raise OmieError("Resposta inesperada do Omie: objeto JSON não-dicionário.")
        return data

    async def call(
        self,
        endpoint: str,
        call: str,
        param: list[dict[str, Any]] | dict[str, Any] | None = None,
        *,
        confirm_write: bool = False,
        bypass_cache: bool = False,
    ) -> dict[str, Any]:
        settings.require_credentials()
        url = self.normalize_endpoint(endpoint)
        params = param if isinstance(param, list) else [param or {}]

        read_only = self.is_read_call(call)
        if not read_only:
            if not settings.omie_allow_writes:
                raise OmieWriteBlocked("Operação de escrita bloqueada por OMIE_ALLOW_WRITES=false.")
            if not confirm_write:
                raise OmieWriteBlocked("Operação potencialmente mutável exige confirm_write=true.")

        fp = self.fingerprint(url, call, params)
        if read_only and not bypass_cache:
            cached = self._get_cached(fp)
            if cached is not None:
                return cached

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

        attempts = 1 + (len(REDUNDANT_RETRY_DELAYS) if read_only else 0)
        for attempt in range(attempts):
            try:
                data = await self._post(url, body)
                if read_only:
                    self._set_cached(fp, data)
                return data
            except OmieError as exc:
                if (
                    read_only
                    and attempt < len(REDUNDANT_RETRY_DELAYS)
                    and self._is_redundant_fault(str(exc))
                ):
                    await asyncio.sleep(REDUNDANT_RETRY_DELAYS[attempt])
                    continue
                raise

        raise OmieError("Falha inesperada ao chamar a API Omie.")


client = OmieClient()
