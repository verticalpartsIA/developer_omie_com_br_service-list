from __future__ import annotations

from typing import Any

from .client import client


async def listar_cst_ibs_cbs(
    *,
    pagina: int = 1,
    registros_por_pagina: int = 50,
    descricao: str | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "nPagina": pagina,
        "nRegistrosPorPagina": registros_por_pagina,
    }
    if descricao:
        payload["cDescricao"] = descricao
    return await client.call("produtos/icbscst", "ListarCSTIbsCbs", payload)


async def listar_classificacoes_ibs_cbs(
    *,
    pagina: int = 1,
    registros_por_pagina: int = 50,
    descricao: str | None = None,
    cst: str | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "nPagina": pagina,
        "nRegistrosPorPagina": registros_por_pagina,
    }
    if descricao:
        payload["cDescricao"] = descricao
    if cst:
        payload["cCodCst"] = cst
    return await client.call("produtos/classtrib", "ListarClassTrib", payload)


async def listar_indicadores_operacao(
    *,
    pagina: int = 1,
    registros_por_pagina: int = 50,
    descricao: str | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "nPagina": pagina,
        "nRegistrosPorPagina": registros_por_pagina,
    }
    if descricao:
        payload["cDescricao"] = descricao
    return await client.call("servicos/indoper", "ListarIndOper", payload)


async def mapa_reforma_tributaria(
    *,
    pagina: int = 1,
    registros_por_pagina: int = 50,
) -> dict[str, Any]:
    csts = await listar_cst_ibs_cbs(pagina=pagina, registros_por_pagina=registros_por_pagina)
    classificacoes = await listar_classificacoes_ibs_cbs(
        pagina=pagina,
        registros_por_pagina=registros_por_pagina,
    )
    indicadores = await listar_indicadores_operacao(
        pagina=pagina,
        registros_por_pagina=registros_por_pagina,
    )
    return {
        "tipo_visao": "REFORMA_TRIBUTARIA",
        "ibs_cbs_cst": csts,
        "ibs_cbs_classificacoes": classificacoes,
        "indicadores_operacao_servicos": indicadores,
        "relacoes": {
            "classificacao_para_cst": "cadastros[].cCodCst -> IBS/CBS CST.cCodigo",
            "indicador_operacao": "cadastro auxiliar de serviços para operações da Reforma Tributária",
        },
        "observacao": (
            "Esta visão consolida os cadastros auxiliares oficiais atuais. "
            "Ela não presume regra fiscal, alíquota ou enquadramento além do que a API devolve."
        ),
    }
