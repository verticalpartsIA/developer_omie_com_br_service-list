from __future__ import annotations

from typing import Any

from .client import client


def _first_list(payload: dict[str, Any], candidates: tuple[str, ...]) -> list[dict[str, Any]]:
    for key in candidates:
        value = payload.get(key)
        if isinstance(value, list):
            return [item for item in value if isinstance(item, dict)]
    # tolera pequenas mudanças de nome no contrato: usa a primeira lista de objetos do nível raiz.
    for value in payload.values():
        if isinstance(value, list) and (not value or all(isinstance(item, dict) for item in value)):
            return list(value)
    return []


async def listar_categorias(pagina: int = 1, registros_por_pagina: int = 100) -> dict[str, Any]:
    return await client.call(
        "geral/categorias",
        "ListarCategorias",
        {"pagina": pagina, "registros_por_pagina": registros_por_pagina},
    )


async def listar_vendedores(pagina: int = 1, registros_por_pagina: int = 100) -> dict[str, Any]:
    return await client.call(
        "geral/vendedores",
        "ListarVendedores",
        {"pagina": pagina, "registros_por_pagina": registros_por_pagina, "apenas_importado_api": "N"},
    )


async def listar_projetos(pagina: int = 1, registros_por_pagina: int = 100) -> dict[str, Any]:
    return await client.call(
        "geral/projetos",
        "ListarProjetos",
        {"pagina": pagina, "registros_por_pagina": registros_por_pagina, "apenas_importado_api": "N"},
    )


async def listar_contas_correntes(pagina: int = 1, registros_por_pagina: int = 100) -> dict[str, Any]:
    return await client.call(
        "geral/contacorrente",
        "ListarContasCorrentes",
        {"pagina": pagina, "registros_por_pagina": registros_por_pagina, "apenas_importado_api": "N"},
    )


async def pesquisar_tipos_documento(codigo: str = "") -> dict[str, Any]:
    return await client.call("geral/tiposdoc", "PesquisarTipoDocumento", {"codigo": codigo})


def normalizar_catalogos(
    *,
    categorias: dict[str, Any],
    vendedores: dict[str, Any],
    projetos: dict[str, Any],
    contas_correntes: dict[str, Any],
    tipos_documento: dict[str, Any],
) -> dict[str, dict[Any, dict[str, Any]]]:
    cats = _first_list(categorias, ("categoria_cadastro", "categorias"))
    vends = _first_list(vendedores, ("cadastro", "vendedores"))
    projs = _first_list(projetos, ("cadastro", "projetos"))
    contas = _first_list(contas_correntes, ("ListarContasCorrentes", "conta_corrente_lista", "cadastro"))
    tipos = _first_list(tipos_documento, ("tipo_documento_cadastro", "tipos_documento"))

    return {
        "categorias": {item.get("codigo"): item for item in cats if item.get("codigo") is not None},
        "vendedores": {item.get("codigo"): item for item in vends if item.get("codigo") is not None},
        "projetos": {item.get("codigo"): item for item in projs if item.get("codigo") is not None},
        "contas_correntes": {item.get("nCodCC"): item for item in contas if item.get("nCodCC") is not None},
        "tipos_documento": {item.get("codigo"): item for item in tipos if item.get("codigo") is not None},
    }


async def carregar_catalogos_auxiliares() -> dict[str, dict[Any, dict[str, Any]]]:
    categorias = await listar_categorias()
    vendedores = await listar_vendedores()
    projetos = await listar_projetos()
    contas = await listar_contas_correntes()
    tipos = await pesquisar_tipos_documento()
    return normalizar_catalogos(
        categorias=categorias,
        vendedores=vendedores,
        projetos=projetos,
        contas_correntes=contas,
        tipos_documento=tipos,
    )
