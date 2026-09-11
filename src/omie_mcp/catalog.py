from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from typing import Iterable

import httpx
from bs4 import BeautifulSoup

from .config import settings


API_URL_RE = re.compile(r"https://app\.omie\.com\.br/api/v1/[A-Za-z0-9_\-/]+/")
CALL_RE = re.compile(r"\b(?:Listar|Consultar|Obter|Pesquisar|Incluir|Alterar|Excluir|Upsert|Cancelar|Associar|Desassociar|Lancar|Faturar|Trocar|Gerar)[A-Za-z0-9_]+\b")


@dataclass(frozen=True, slots=True)
class ServiceEntry:
    module: str
    name: str
    endpoint: str
    source_url: str


def _module_from_endpoint(endpoint: str) -> str:
    suffix = endpoint.split("/api/v1/", 1)[-1].strip("/")
    return suffix.split("/", 1)[0] if suffix else "desconhecido"


def _clean(text: str) -> str:
    return " ".join(text.split())


async def fetch_service_catalog() -> list[ServiceEntry]:
    """Lê a lista oficial do Omie e descobre serviços dinamicamente.

    Não depende de uma enumeração fechada no código. Se o Omie adicionar um
    serviço à página oficial, ele passa a aparecer neste catálogo.
    """
    async with httpx.AsyncClient(timeout=settings.omie_http_timeout, follow_redirects=True) as http:
        response = await http.get(settings.omie_service_list_url)
        response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    entries: dict[str, ServiceEntry] = {}

    for tag in soup.find_all(["a", "code", "pre", "td", "li"]):
        text = _clean(tag.get_text(" ", strip=True))
        href = tag.get("href") if getattr(tag, "get", None) else None
        candidates = []
        if href:
            candidates.extend(API_URL_RE.findall(href))
        candidates.extend(API_URL_RE.findall(text))

        for endpoint in candidates:
            endpoint = endpoint.rstrip("/") + "/"
            name = text[:180] or endpoint.rsplit("/", 2)[-2]
            entries[endpoint] = ServiceEntry(
                module=_module_from_endpoint(endpoint),
                name=name,
                endpoint=endpoint,
                source_url=settings.omie_service_list_url,
            )

    # Fallback: alguns layouts escondem URLs no HTML/JS em vez de texto visível.
    for endpoint in API_URL_RE.findall(response.text):
        endpoint = endpoint.rstrip("/") + "/"
        entries.setdefault(
            endpoint,
            ServiceEntry(
                module=_module_from_endpoint(endpoint),
                name=endpoint.rsplit("/", 2)[-2],
                endpoint=endpoint,
                source_url=settings.omie_service_list_url,
            ),
        )

    return sorted(entries.values(), key=lambda item: (item.module, item.endpoint))


async def inspect_service(endpoint: str) -> dict:
    """Inspeciona uma página/endpoint oficial e tenta descobrir operações documentadas."""
    if not endpoint.startswith(settings.omie_api_base.rstrip("/") + "/"):
        raise ValueError("Somente endpoints oficiais do Omie podem ser inspecionados.")

    async with httpx.AsyncClient(timeout=settings.omie_http_timeout, follow_redirects=True) as http:
        response = await http.get(endpoint)
        text = response.text

    calls = sorted(set(CALL_RE.findall(text)))
    return {
        "endpoint": endpoint,
        "http_status": response.status_code,
        "calls_detectadas": calls,
        "content_type": response.headers.get("content-type"),
        "bytes": len(response.content),
    }


def serialize_catalog(entries: Iterable[ServiceEntry]) -> list[dict]:
    return [asdict(entry) for entry in entries]
