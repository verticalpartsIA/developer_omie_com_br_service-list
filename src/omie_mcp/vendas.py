from __future__ import annotations

from typing import Any

from .client import client


async def listar_pedidos_venda(
    *,
    pagina: int = 1,
    registros_por_pagina: int = 100,
    apenas_importado_api: str = "N",
) -> dict[str, Any]:
    return await client.call(
        "produtos/pedido",
        "ListarPedidos",
        {
            "pagina": pagina,
            "registros_por_pagina": registros_por_pagina,
            "apenas_importado_api": apenas_importado_api,
        },
    )


async def consultar_pedido_venda(
    *,
    codigo_pedido: int | None = None,
    codigo_integracao: str | None = None,
) -> dict[str, Any]:
    if not any([codigo_pedido, codigo_integracao]):
        raise ValueError("Informe codigo_pedido ou codigo_integracao")
    payload = {
        key: value
        for key, value in {
            "codigo_pedido": codigo_pedido,
            "codigo_pedido_integracao": codigo_integracao,
        }.items()
        if value not in (None, "")
    }
    return await client.call("produtos/pedido", "ConsultarPedido", payload)


async def status_pedido_venda(
    *,
    codigo_pedido: int | None = None,
    codigo_integracao: str | None = None,
) -> dict[str, Any]:
    if not any([codigo_pedido, codigo_integracao]):
        raise ValueError("Informe codigo_pedido ou codigo_integracao")
    payload = {
        key: value
        for key, value in {
            "codigo_pedido": codigo_pedido,
            "codigo_pedido_integracao": codigo_integracao,
        }.items()
        if value not in (None, "")
    }
    return await client.call("produtos/pedido", "StatusPedido", payload)


async def pedidos_prontos_faturar(etapa: str = "50") -> dict[str, Any]:
    """Lista pedidos encontrados na etapa de faturamento informada."""
    return await client.call("produtos/pedidovendafat", "ObterPedidosVenda", {"cEtapa": etapa})


async def validar_pedido_faturamento(
    *,
    codigo_pedido: int | None = None,
    codigo_integracao: str | None = None,
) -> dict[str, Any]:
    """Valida o pedido para faturamento sem efetuar o faturamento."""
    if not any([codigo_pedido, codigo_integracao]):
        raise ValueError("Informe codigo_pedido ou codigo_integracao")
    payload = {
        key: value
        for key, value in {
            "nCodPed": codigo_pedido,
            "cCodIntPed": codigo_integracao,
        }.items()
        if value not in (None, "")
    }
    return await client.call("produtos/pedidovendafat", "ValidarPedidoVenda", payload)


async def listar_nfe(
    *,
    pagina: int = 1,
    registros_por_pagina: int = 20,
    ordenar_por: str = "CODIGO",
) -> dict[str, Any]:
    return await client.call(
        "produtos/nfconsultar",
        "ListarNF",
        {
            "pagina": pagina,
            "registros_por_pagina": registros_por_pagina,
            "ordenar_por": ordenar_por,
        },
    )


async def consultar_nfe(
    *,
    codigo_nfe: int | None = None,
    numero_nfe: str | None = None,
) -> dict[str, Any]:
    if not any([codigo_nfe, numero_nfe]):
        raise ValueError("Informe codigo_nfe ou numero_nfe")
    payload = {
        key: value
        for key, value in {
            "nCodNF": codigo_nfe,
            "nNF": numero_nfe,
        }.items()
        if value not in (None, "")
    }
    return await client.call("produtos/nfconsultar", "ConsultarNF", payload)


async def pedido_venda_ciclo(
    *,
    codigo_pedido: int,
) -> dict[str, Any]:
    """Visão composta e somente leitura do ciclo de venda de um pedido."""
    pedido = await consultar_pedido_venda(codigo_pedido=codigo_pedido)
    status = await status_pedido_venda(codigo_pedido=codigo_pedido)
    return {
        "codigo_pedido": codigo_pedido,
        "pedido": pedido,
        "status": status,
        "regra": (
            "Pedido, NF-e e Contas a Receber devem ser correlacionados pelos IDs/números oficiais "
            "retornados pelo Omie; não inferir faturamento apenas pela etapa do pedido."
        ),
    }
