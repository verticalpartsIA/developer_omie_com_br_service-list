import pytest

from omie_mcp import compras, vendas


@pytest.mark.asyncio
async def test_produto_fornecedor_limita_pagina(monkeypatch):
    capturado = {}

    async def fake_call(endpoint, call, param, **kwargs):
        capturado.update(endpoint=endpoint, call=call, param=param)
        return {"ok": True}

    monkeypatch.setattr(compras.client, "call", fake_call)
    await compras.listar_produtos_fornecedor(registros_por_pagina=50)

    assert capturado["endpoint"] == "estoque/produtofornecedor"
    assert capturado["call"] == "ListarProdutoFornecedor"
    assert capturado["param"]["registros_por_pagina"] == 10


@pytest.mark.asyncio
async def test_requisicao_compra_usa_metodo_oficial(monkeypatch):
    capturado = {}

    async def fake_call(endpoint, call, param, **kwargs):
        capturado.update(endpoint=endpoint, call=call, param=param)
        return {"ok": True}

    monkeypatch.setattr(compras.client, "call", fake_call)
    await compras.pesquisar_requisicoes_compra(pagina=2, registros_por_pagina=25)

    assert capturado["endpoint"] == "produtos/requisicaocompra"
    assert capturado["call"] == "PesquisarReq"
    assert capturado["param"]["pagina"] == 2


@pytest.mark.asyncio
async def test_recebimento_nfe_consulta_por_chave(monkeypatch):
    capturado = {}

    async def fake_call(endpoint, call, param, **kwargs):
        capturado.update(endpoint=endpoint, call=call, param=param)
        return {"ok": True}

    monkeypatch.setattr(compras.client, "call", fake_call)
    await compras.consultar_recebimento_nfe(chave_nfe="1" * 44)

    assert capturado["endpoint"] == "produtos/recebimentonfe"
    assert capturado["call"] == "ConsultarRecebimento"
    assert capturado["param"]["cChaveNfe"] == "1" * 44


@pytest.mark.asyncio
async def test_venda_consulta_status_e_nfe(monkeypatch):
    chamadas = []

    async def fake_call(endpoint, call, param, **kwargs):
        chamadas.append((endpoint, call, param))
        return {"ok": True}

    monkeypatch.setattr(vendas.client, "call", fake_call)

    await vendas.consultar_pedido_venda(codigo_pedido=123)
    await vendas.status_pedido_venda(codigo_pedido=123)
    await vendas.consultar_nfe(numero_nfe="987")

    assert chamadas[0][0:2] == ("produtos/pedido", "ConsultarPedido")
    assert chamadas[1][0:2] == ("produtos/pedido", "StatusPedido")
    assert chamadas[2][0:2] == ("produtos/nfconsultar", "ConsultarNF")


def test_consultas_exigem_identificador():
    with pytest.raises(ValueError):
        import asyncio
        asyncio.run(compras.consultar_requisicao_compra())

    with pytest.raises(ValueError):
        import asyncio
        asyncio.run(vendas.consultar_pedido_venda())
