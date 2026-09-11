from __future__ import annotations

from typing import Any

from .client import client


async def pesquisar_pedidos_compra(
    *,
    pagina: int = 1,
    registros_por_pagina: int = 50,
    pendentes: bool = True,
    faturados: bool = True,
    recebidos: bool = True,
    cancelados: bool = False,
    encerrados: bool = True,
    recebidos_parcialmente: bool = True,
    faturados_parcialmente: bool = True,
    data_inicial: str | None = None,
    data_final: str | None = None,
    apenas_alterados: bool = False,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "nPagina": pagina,
        "nRegsPorPagina": registros_por_pagina,
        "lApenasImportadoApi": "F",
        "lExibirPedidosPendentes": "T" if pendentes else "F",
        "lExibirPedidosFaturados": "T" if faturados else "F",
        "lExibirPedidosRecebidos": "T" if recebidos else "F",
        "lExibirPedidosCancelados": "T" if cancelados else "F",
        "lExibirPedidosEncerrados": "T" if encerrados else "F",
        "lExibirPedidosRecParciais": "T" if recebidos_parcialmente else "F",
        "lExibirPedidosFatParciais": "T" if faturados_parcialmente else "F",
        "lApenasAlterados": "T" if apenas_alterados else "F",
    }
    if data_inicial:
        payload["dDataInicial"] = data_inicial
    if data_final:
        payload["dDataFinal"] = data_final
    return await client.call("produtos/pedidocompra", "PesquisarPedCompra", payload)


async def consultar_pedido_compra(
    *,
    codigo_pedido: int | None = None,
    codigo_integracao: str | None = None,
    numero: str | None = None,
) -> dict[str, Any]:
    if not any([codigo_pedido, codigo_integracao, numero]):
        raise ValueError("Informe codigo_pedido, codigo_integracao ou numero")
    payload = {
        key: value
        for key, value in {
            "nCodPed": codigo_pedido,
            "cCodIntPed": codigo_integracao,
            "cNumero": numero,
        }.items()
        if value not in (None, "")
    }
    return await client.call("produtos/pedidocompra", "ConsultarPedCompra", payload)


async def listar_notas_entrada(
    *,
    pagina: int = 1,
    registros_por_pagina: int = 50,
) -> dict[str, Any]:
    return await client.call(
        "produtos/notaentrada",
        "ListarNotaEnt",
        {"nPagina": pagina, "nRegistrosPorPagina": registros_por_pagina},
    )


async def consultar_nota_entrada(
    *,
    codigo_nota_entrada: int | None = None,
    codigo_integracao: str | None = None,
) -> dict[str, Any]:
    if not any([codigo_nota_entrada, codigo_integracao]):
        raise ValueError("Informe codigo_nota_entrada ou codigo_integracao")
    payload = {
        key: value
        for key, value in {
            "nCodNotaEnt": codigo_nota_entrada,
            "cCodIntNotaEnt": codigo_integracao,
        }.items()
        if value not in (None, "")
    }
    return await client.call("produtos/notaentrada", "ConsultarNotaEnt", payload)


async def produto_ciclo_compra(
    *,
    codigo_produto: int,
    pagina: int = 1,
    registros_por_pagina: int = 50,
) -> dict[str, Any]:
    """Visão composta de produto para compras/estoque.

    Não inventa relacionamento que a API não exponha. Entrega as fontes brutas úteis
    para o Claude cruzar produto, posição de estoque e pedidos de compra pesquisados.
    """
    produto = await client.call("geral/produtos", "ConsultarProduto", {"codigo_produto": codigo_produto})
    estoque = await client.call(
        "estoque/consulta",
        "PosicaoEstoque",
        {"codigo_local_estoque": 0, "id_prod": codigo_produto, "cod_int": ""},
    )
    pedidos = await pesquisar_pedidos_compra(
        pagina=pagina,
        registros_por_pagina=registros_por_pagina,
        pendentes=True,
        faturados=True,
        recebidos=True,
        encerrados=True,
    )
    return {
        "codigo_produto": codigo_produto,
        "produto": produto,
        "estoque": estoque,
        "pedidos_compra_pesquisa": pedidos,
        "observacao": "A correlação fina por item deve usar os itens retornados em cada pedido; não presumir vínculo sem nCodProd correspondente.",
    }
