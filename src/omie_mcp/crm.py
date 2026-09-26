from __future__ import annotations

from typing import Any

from .client import client


async def listar_oportunidades(
    *,
    pagina: int = 1,
    registros_por_pagina: int = 50,
    status: str | None = None,
    fase: int | None = None,
    codigo_vendedor: int | None = None,
    filtrar_por_conta: int | None = None,
    exibir_detalhes: str = "S",
    exibir_obs: str = "S",
) -> dict[str, Any]:
    param: dict[str, Any] = {
        "pagina": pagina,
        "registros_por_pagina": min(registros_por_pagina, 50),
        "apenas_importado_api": "N",
        "exibir_detalhes": exibir_detalhes,
        "exibir_obs": exibir_obs,
    }
    opcionais = {
        "status": status,
        "fase": fase,
        "codigo_vendedor": codigo_vendedor,
        "filtrar_por_conta": filtrar_por_conta,
    }
    param.update({k: v for k, v in opcionais.items() if v is not None})
    return await client.call("crm/oportunidades", "ListarOportunidades", param)


async def consultar_oportunidade(*, codigo_oportunidade: int | None = None, codigo_integracao: str | None = None) -> dict[str, Any]:
    if not any([codigo_oportunidade, codigo_integracao]):
        raise ValueError("Informe codigo_oportunidade ou codigo_integracao")
    return await client.call(
        "crm/oportunidades",
        "ConsultarOportunidade",
        {k: v for k, v in {"nCodOp": codigo_oportunidade, "cCodIntOp": codigo_integracao}.items() if v not in (None, "")},
    )


async def listar_tarefas_crm(
    *,
    pagina: int = 1,
    registros_por_pagina: int = 50,
    codigo_oportunidade: int | None = None,
    codigo_vendedor: int | None = None,
    data_inicial: str | None = None,
    data_final: str | None = None,
    importante: str | None = None,
    urgente: str | None = None,
    em_execucao: str | None = None,
    realizada: str | None = None,
) -> dict[str, Any]:
    param: dict[str, Any] = {
        "pagina": pagina,
        "registros_por_pagina": min(registros_por_pagina, 50),
        "apenas_importado_api": "N",
        "exibir_detalhes": "S",
    }
    opcionais = {
        "nCodOp": codigo_oportunidade,
        "codigo_vendedor": codigo_vendedor,
        "data_inicial": data_inicial,
        "data_final": data_final,
        "cImportante": importante,
        "cUrgente": urgente,
        "cEmExecucao": em_execucao,
        "cRealizada": realizada,
    }
    param.update({k: v for k, v in opcionais.items() if v is not None})
    return await client.call("crm/tarefas", "ListarTarefas", param)


async def resumo_oportunidades(
    *,
    mes_ano: str,
    codigo_vendedor: int = 0,
    codigo_parceiro: int = 0,
    apenas_resumo: bool = False,
) -> dict[str, Any]:
    return await client.call(
        "crm/oportunidades-resumo",
        "ObterResumoOp",
        {
            "nIdVendedor": codigo_vendedor,
            "nIdParceiro": codigo_parceiro,
            "cMesAno": mes_ano,
            "lApenasResumo": apenas_resumo,
        },
    )


async def oportunidade_360(codigo_oportunidade: int) -> dict[str, Any]:
    oportunidade = await consultar_oportunidade(codigo_oportunidade=codigo_oportunidade)
    tarefas = await listar_tarefas_crm(codigo_oportunidade=codigo_oportunidade, registros_por_pagina=50)
    ident = oportunidade.get("identificacao") or {}
    return {
        "tipo_visao": "OPORTUNIDADE_360",
        "codigo_oportunidade": codigo_oportunidade,
        "oportunidade": oportunidade,
        "tarefas": tarefas,
        "chaves": {
            "conta": ident.get("nCodConta"),
            "contato": ident.get("nCodContato"),
            "vendedor": ident.get("nCodVendedor"),
            "origem": ident.get("nCodOrigem"),
            "solucao": ident.get("nCodSolucao"),
        },
    }
