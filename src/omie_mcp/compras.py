from __future__ import annotations

from typing import Any

from .client import client


async def listar_produtos_fornecedor(
    *,
    pagina: int = 1,
    registros_por_pagina: int = 10,
    apenas_importado_api: str = "N",
) -> dict[str, Any]:
    """Lista a relação oficial Produto x Fornecedor.

    A documentação Omie limita registros_por_pagina a 10 neste serviço.
    """
    if registros_por_pagina > 10:
        registros_por_pagina = 10
    return await client.call(
        "estoque/produtofornecedor",
        "ListarProdutoFornecedor",
        {
            "pagina": pagina,
            "registros_por_pagina": registros_por_pagina,
            "apenas_importado_api": apenas_importado_api,
        },
    )


async def pesquisar_requisicoes_compra(
    *,
    pagina: int = 1,
    registros_por_pagina: int = 50,
    apenas_importado_api: str = "N",
    data_de: str | None = None,
    data_ate: str | None = None,
    apenas_inclusao: str | None = None,
    apenas_alteracao: str | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "pagina": pagina,
        "registros_por_pagina": registros_por_pagina,
        "apenas_importado_api": apenas_importado_api,
    }
    opcionais = {
        "filtrar_por_data_de": data_de,
        "filtrar_por_data_ate": data_ate,
        "filtrar_apenas_inclusao": apenas_inclusao,
        "filtrar_apenas_alteracao": apenas_alteracao,
    }
    payload.update({k: v for k, v in opcionais.items() if v is not None})
    return await client.call("produtos/requisicaocompra", "PesquisarReq", payload)


async def consultar_requisicao_compra(
    *,
    codigo_requisicao: int | None = None,
    codigo_integracao: str | None = None,
) -> dict[str, Any]:
    if not any([codigo_requisicao, codigo_integracao]):
        raise ValueError("Informe codigo_requisicao ou codigo_integracao")
    payload = {
        key: value
        for key, value in {
            "codReqCompra": codigo_requisicao,
            "codIntReqCompra": codigo_integracao,
        }.items()
        if value not in (None, "")
    }
    return await client.call("produtos/requisicaocompra", "ConsultarReq", payload)


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


async def listar_recebimentos_nfe(
    *,
    pagina: int = 1,
    registros_por_pagina: int = 50,
) -> dict[str, Any]:
    """Lista recebimentos de NF-e do fluxo de compras."""
    return await client.call(
        "produtos/recebimentonfe",
        "ListarRecebimentos",
        {"nPagina": pagina, "nRegistrosPorPagina": registros_por_pagina},
    )


async def consultar_recebimento_nfe(
    *,
    id_recebimento: int | None = None,
    chave_nfe: str | None = None,
) -> dict[str, Any]:
    if not any([id_recebimento, chave_nfe]):
        raise ValueError("Informe id_recebimento ou chave_nfe")
    payload = {
        key: value
        for key, value in {
            "nIdReceb": id_recebimento,
            "cChaveNfe": chave_nfe,
        }.items()
        if value not in (None, "")
    }
    return await client.call("produtos/recebimentonfe", "ConsultarRecebimento", payload)


async def produto_ciclo_compra(
    *,
    codigo_produto: int,
    pagina: int = 1,
    registros_por_pagina: int = 50,
) -> dict[str, Any]:
    """Visão composta de produto para compras/estoque.

    Entrega produto, posição de estoque, relação Produto x Fornecedor, requisições
    e pedidos como fontes separadas. O consumidor deve correlacionar por IDs oficiais,
    sem inventar vínculo quando o Omie não o expuser diretamente.
    """
    produto = await client.call("geral/produtos", "ConsultarProduto", {"codigo_produto": codigo_produto})
    estoque = await client.call(
        "estoque/consulta",
        "PosicaoEstoque",
        {"codigo_local_estoque": 0, "id_prod": codigo_produto, "cod_int": ""},
    )
    fornecedores = await listar_produtos_fornecedor(pagina=1, registros_por_pagina=10)
    requisicoes = await pesquisar_requisicoes_compra(pagina=pagina, registros_por_pagina=registros_por_pagina)
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
        "produto_fornecedor": fornecedores,
        "requisicoes_compra": requisicoes,
        "pedidos_compra_pesquisa": pedidos,
        "observacao": (
            "Filtrar/correlacionar fornecedores, requisições e pedidos pelo código oficial do produto "
            "presente nos itens retornados. Não presumir relacionamento apenas por descrição."
        ),
    }
