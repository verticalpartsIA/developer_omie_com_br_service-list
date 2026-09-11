from __future__ import annotations

from typing import Any, Awaitable, Callable

from .cadastros import consultar_cliente_fornecedor, normalizar_cliente_fornecedor
from .enriquecimento import carregar_catalogos_auxiliares
from .financeiro import listar_contas_pagar_financeiro_todas
from .receber import listar_contas_receber_financeiro_todas


def _nome(item: dict[str, Any] | None, *campos: str) -> Any:
    if not item:
        return None
    for campo in campos:
        valor = item.get(campo)
        if valor not in (None, ""):
            return valor
    return None


def enriquecer_titulos(
    contas: list[dict[str, Any]],
    *,
    catalogos: dict[str, dict[Any, dict[str, Any]]],
    parceiros: dict[int, dict[str, Any]],
    tipo: str,
) -> list[dict[str, Any]]:
    resultado: list[dict[str, Any]] = []
    chave_parceiro = "codigo_fornecedor" if tipo == "PAGAR" else "codigo_cliente"
    chave_doc = "tipo_documento_codigo"

    for conta in contas:
        parceiro_id = conta.get(chave_parceiro)
        parceiro = parceiros.get(parceiro_id) if isinstance(parceiro_id, int) else None
        categoria = catalogos.get("categorias", {}).get(conta.get("categoria_codigo"))
        vendedor = catalogos.get("vendedores", {}).get(conta.get("vendedor_codigo"))
        projeto = catalogos.get("projetos", {}).get(conta.get("projeto_codigo"))
        corrente = catalogos.get("contas_correntes", {}).get(conta.get("conta_corrente_codigo"))
        doc = catalogos.get("tipos_documento", {}).get(conta.get(chave_doc))

        enriquecido = {
            "parceiro": parceiro,
            "categoria_descricao": _nome(categoria, "descricao"),
            "vendedor_nome": _nome(vendedor, "nome"),
            "projeto_nome": _nome(projeto, "nome"),
            "conta_corrente_descricao": _nome(corrente, "descricao"),
            "conta_corrente_banco_codigo": _nome(corrente, "codigo_banco"),
            "tipo_documento_descricao": _nome(doc, "descricao"),
        }
        resultado.append({**conta, "enriquecido": enriquecido})
    return resultado


async def _carregar_parceiros(
    contas: list[dict[str, Any]],
    *,
    chave: str,
    consultar: Callable[..., Awaitable[dict[str, Any]]] = consultar_cliente_fornecedor,
) -> dict[int, dict[str, Any]]:
    ids = sorted({int(c[chave]) for c in contas if isinstance(c.get(chave), int)})
    parceiros: dict[int, dict[str, Any]] = {}
    for codigo in ids:
        try:
            bruto = await consultar(codigo_cliente_omie=codigo)
            parceiros[codigo] = normalizar_cliente_fornecedor(bruto)
        except Exception as exc:  # relatório deve continuar mesmo se um cadastro auxiliar falhar
            parceiros[codigo] = {"codigo_cliente_omie": codigo, "erro_enriquecimento": str(exc)}
    return parceiros


async def contas_pagar_relatorio_completo(
    *,
    registros_por_pagina: int = 100,
    max_paginas: int = 100,
    status: str | None = None,
    codigo_fornecedor: int | None = None,
) -> dict[str, Any]:
    financeiro = await listar_contas_pagar_financeiro_todas(
        registros_por_pagina=registros_por_pagina,
        max_paginas=max_paginas,
        status=status,
        codigo_fornecedor=codigo_fornecedor,
    )
    contas = financeiro.get("contas") or []
    catalogos = await carregar_catalogos_auxiliares()
    parceiros = await _carregar_parceiros(contas, chave="codigo_fornecedor")
    return {
        **financeiro,
        "tipo_relatorio": "CONTAS_PAGAR_COMPLETO",
        "contas": enriquecer_titulos(contas, catalogos=catalogos, parceiros=parceiros, tipo="PAGAR"),
        "enriquecimentos": ["fornecedor", "categoria", "vendedor", "projeto", "conta_corrente", "tipo_documento"],
    }


async def contas_receber_relatorio_completo(
    *,
    registros_por_pagina: int = 100,
    max_paginas: int = 100,
    status: str | None = None,
    codigo_cliente: int | None = None,
) -> dict[str, Any]:
    financeiro = await listar_contas_receber_financeiro_todas(
        registros_por_pagina=registros_por_pagina,
        max_paginas=max_paginas,
        status=status,
        codigo_cliente=codigo_cliente,
    )
    contas = financeiro.get("contas") or []
    catalogos = await carregar_catalogos_auxiliares()
    parceiros = await _carregar_parceiros(contas, chave="codigo_cliente")
    return {
        **financeiro,
        "tipo_relatorio": "CONTAS_RECEBER_COMPLETO",
        "contas": enriquecer_titulos(contas, catalogos=catalogos, parceiros=parceiros, tipo="RECEBER"),
        "enriquecimentos": ["cliente", "categoria", "vendedor", "projeto", "conta_corrente", "tipo_documento"],
    }
