from __future__ import annotations

from typing import Any

from .client import client


def normalizar_projeto(item: dict[str, Any]) -> dict[str, Any]:
    info = item.get("info") or {}
    inativo = str(item.get("inativo") or "N").upper() == "S"

    inclusao_data = info.get("data_inc") or info.get("dInc")
    inclusao_hora = info.get("hora_inc") or info.get("hInc")
    alteracao_data = info.get("data_alt") or info.get("dAlt")
    alteracao_hora = info.get("hora_alt") or info.get("hAlt")
    incluido_por = info.get("user_inc") or info.get("uInc")
    alterado_por = info.get("user_alt") or info.get("uAlt")

    return {
        "situacao": "Inativo" if inativo else "Ativo",
        "nome_projeto": item.get("nome"),
        "inclusao": " ".join(v for v in [inclusao_data, inclusao_hora] if v) or None,
        "ultima_alteracao": " ".join(v for v in [alteracao_data, alteracao_hora] if v) or None,
        "incluido_por": incluido_por,
        "alterado_por": alterado_por,
        "codigo_projeto": item.get("codigo"),
        "codigo_integracao": item.get("codInt") or item.get("codint"),
        "raw": item,
    }


async def listar_projetos_semanticos(
    pagina: int = 1,
    registros_por_pagina: int = 50,
    apenas_importado_api: str = "N",
    nome_projeto: str | None = None,
    filtrar_por_data_de: str | None = None,
    filtrar_por_data_ate: str | None = None,
    filtrar_apenas_inclusao: str | None = None,
    filtrar_apenas_alteracao: str | None = None,
    ordenar_por: str | None = None,
    ordem_descrescente: str | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "pagina": pagina,
        "registros_por_pagina": registros_por_pagina,
        "apenas_importado_api": apenas_importado_api,
    }
    opcionais = {
        "nome_projeto": nome_projeto,
        "filtrar_por_data_de": filtrar_por_data_de,
        "filtrar_por_data_ate": filtrar_por_data_ate,
        "filtrar_apenas_inclusao": filtrar_apenas_inclusao,
        "filtrar_apenas_alteracao": filtrar_apenas_alteracao,
        "ordenar_por": ordenar_por,
        "ordem_descrescente": ordem_descrescente,
    }
    payload.update({k: v for k, v in opcionais.items() if v not in (None, "")})

    resposta = await client.call("geral/projetos", "ListarProjetos", payload)
    itens = resposta.get("cadastro") or []
    return {
        "pagina": resposta.get("pagina"),
        "total_de_paginas": resposta.get("total_de_paginas"),
        "registros": resposta.get("registros"),
        "total_de_registros": resposta.get("total_de_registros"),
        "projetos": [normalizar_projeto(item) for item in itens if isinstance(item, dict)],
        "colunas_gerenciais": [
            "Situação",
            "Nome do Projeto",
            "Inclusão",
            "Última Alteração",
            "Incluído por",
            "Alterado por",
        ],
        "fonte": "Omie /geral/projetos/ ListarProjetos",
        "raw": resposta,
    }


async def consultar_projeto_semantico(
    *,
    codigo: int | None = None,
    codint: str | None = None,
) -> dict[str, Any]:
    if codigo is None and not codint:
        raise ValueError("Informe codigo ou codint do projeto.")

    payload = {k: v for k, v in {"codigo": codigo, "codInt": codint}.items() if v not in (None, "")}
    resposta = await client.call("geral/projetos", "ConsultarProjeto", payload)
    return {
        "encontrado": True,
        "projeto": normalizar_projeto(resposta),
        "colunas_gerenciais": [
            "Situação",
            "Nome do Projeto",
            "Inclusão",
            "Última Alteração",
            "Incluído por",
            "Alterado por",
        ],
        "fonte": "Omie /geral/projetos/ ConsultarProjeto",
    }
