import pytest

from omie_mcp import visoes360
from omie_mcp.client import OmieError


@pytest.mark.asyncio
async def test_cliente_360_cruza_cadastro_financeiro_e_vendas(monkeypatch):
    async def fake_consultar_cliente_fornecedor(**kwargs):
        return {
            "codigo_cliente_omie": 123,
            "razao_social": "Cliente Teste Ltda",
            "nome_fantasia": "Cliente Teste",
            "cnpj_cpf": "00000000000100",
            "inativo": "N",
        }

    async def fake_receber(**kwargs):
        assert kwargs["codigo_cliente"] == 123
        return {
            "fonte": "teste",
            "contas": [
                {"valor_conta": 1000.0, "valor_recebido": 400.0, "valor_a_receber": 600.0, "situacao": "PAGTOPARCIAL"},
                {"valor_conta": 500.0, "valor_recebido": 500.0, "valor_a_receber": 0.0, "situacao": "RECEBIDO"},
            ],
        }

    chamadas = []

    async def fake_call(endpoint, call, param, **kwargs):
        chamadas.append((endpoint, call, param))
        return {"pedido_venda_produto": []}

    monkeypatch.setattr(visoes360, "consultar_cliente_fornecedor", fake_consultar_cliente_fornecedor)
    monkeypatch.setattr(visoes360, "listar_contas_receber_financeiro", fake_receber)
    monkeypatch.setattr(visoes360.client, "call", fake_call)

    resposta = await visoes360.cliente_360(123)

    resumo = resposta["financeiro"]["resumo"]
    assert resumo["valor_total"] == 1500.0
    assert resumo["valor_realizado"] == 900.0
    assert resumo["valor_em_aberto"] == 600.0
    assert resposta["completo"] is True
    assert resposta["financeiro"]["sem_registros"] is False
    assert resposta["vendas"]["sem_registros"] is False
    assert chamadas[0][0:2] == ("produtos/pedido", "ListarPedidos")
    assert chamadas[0][2]["filtrar_por_cliente"] == 123


@pytest.mark.asyncio
async def test_cliente_360_trata_ausencia_de_financeiro_e_pedidos_como_vazio(monkeypatch):
    async def fake_consultar_cliente_fornecedor(**kwargs):
        return {
            "codigo_cliente_omie": 123,
            "razao_social": "Cliente Sem Movimento Ltda",
            "nome_fantasia": "Cliente Sem Movimento",
            "cnpj_cpf": "00000000000100",
            "inativo": "N",
        }

    async def fake_receber(**kwargs):
        raise OmieError("Omie HTTP 500: Não existem registros para a pesquisa realizada")

    async def fake_call(endpoint, call, param, **kwargs):
        raise OmieError("Omie HTTP 500: Nenhum registro encontrado")

    monkeypatch.setattr(visoes360, "consultar_cliente_fornecedor", fake_consultar_cliente_fornecedor)
    monkeypatch.setattr(visoes360, "listar_contas_receber_financeiro", fake_receber)
    monkeypatch.setattr(visoes360.client, "call", fake_call)

    resposta = await visoes360.cliente_360(123)

    assert resposta["completo"] is True
    assert resposta["financeiro"]["contas_receber"] == []
    assert resposta["financeiro"]["resumo"]["quantidade_titulos"] == 0
    assert resposta["financeiro"]["sem_registros"] is True
    assert resposta["vendas"]["pedidos"]["pedido_venda_produto"] == []
    assert resposta["vendas"]["sem_registros"] is True


@pytest.mark.asyncio
async def test_cliente_360_nao_esconde_erro_real(monkeypatch):
    async def fake_consultar_cliente_fornecedor(**kwargs):
        return {
            "codigo_cliente_omie": 123,
            "razao_social": "Cliente Teste Ltda",
            "nome_fantasia": "Cliente Teste",
            "cnpj_cpf": "00000000000100",
            "inativo": "N",
        }

    async def fake_receber(**kwargs):
        raise OmieError("Omie HTTP 403: A chave de acesso não é válida")

    monkeypatch.setattr(visoes360, "consultar_cliente_fornecedor", fake_consultar_cliente_fornecedor)
    monkeypatch.setattr(visoes360, "listar_contas_receber_financeiro", fake_receber)

    with pytest.raises(OmieError, match="403"):
        await visoes360.cliente_360(123)


@pytest.mark.asyncio
async def test_fornecedor_360_nao_inventa_pedidos_compra(monkeypatch):
    async def fake_consultar_cliente_fornecedor(**kwargs):
        return {
            "codigo_cliente_omie": 321,
            "razao_social": "Fornecedor Teste Ltda",
            "nome_fantasia": "Fornecedor Teste",
            "cnpj_cpf": "00000000000200",
            "inativo": "N",
        }

    async def fake_pagar(**kwargs):
        assert kwargs["codigo_fornecedor"] == 321
        return {
            "fonte": "teste",
            "contas": [
                {"valor_conta": 2000.0, "valor_pago": 500.0, "valor_a_pagar": 1500.0, "situacao": "PAGTOPARCIAL"}
            ],
        }

    monkeypatch.setattr(visoes360, "consultar_cliente_fornecedor", fake_consultar_cliente_fornecedor)
    monkeypatch.setattr(visoes360, "listar_contas_pagar_financeiro", fake_pagar)

    resposta = await visoes360.fornecedor_360(321)

    assert resposta["financeiro"]["resumo"]["valor_em_aberto"] == 1500.0
    assert resposta["financeiro"]["sem_registros"] is False
    assert "não documenta filtro por fornecedor" in resposta["compras"]["observacao"]


@pytest.mark.asyncio
async def test_fornecedor_360_trata_ausencia_financeira_como_vazio(monkeypatch):
    async def fake_consultar_cliente_fornecedor(**kwargs):
        return {
            "codigo_cliente_omie": 321,
            "razao_social": "Fornecedor Sem Movimento Ltda",
            "nome_fantasia": "Fornecedor Sem Movimento",
            "cnpj_cpf": "00000000000200",
            "inativo": "N",
        }

    async def fake_pagar(**kwargs):
        raise OmieError("Omie HTTP 500: Não há registros")

    monkeypatch.setattr(visoes360, "consultar_cliente_fornecedor", fake_consultar_cliente_fornecedor)
    monkeypatch.setattr(visoes360, "listar_contas_pagar_financeiro", fake_pagar)

    resposta = await visoes360.fornecedor_360(321)

    assert resposta["completo"] is True
    assert resposta["financeiro"]["contas_pagar"] == []
    assert resposta["financeiro"]["sem_registros"] is True


def test_app_importa_e_expoe_entrypoint():
    import omie_mcp.app as app

    assert app.mcp is not None
    assert callable(app.main)
