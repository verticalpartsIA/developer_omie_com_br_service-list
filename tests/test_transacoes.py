import pytest

from omie_mcp import transacoes


@pytest.mark.asyncio
async def test_ciclo_venda_usa_ncod_os(monkeypatch):
    chamadas = []

    async def fake_pedido(*, codigo_pedido=None, codigo_integracao=None):
        return {"cabecalho": {"codigo_pedido": codigo_pedido, "codigo_cliente": 55}}

    async def fake_status(*, codigo_pedido=None, codigo_integracao=None):
        return {"codigo_pedido": codigo_pedido, "status": "FATURADO"}

    async def fake_call(endpoint, call, param, **kwargs):
        chamadas.append((endpoint, call, param))
        return {
            "nTotPaginas": 1,
            "nTotRegistros": 1,
            "movimentos": [
                {
                    "detalhes": {"nCodOS": 123, "nCodTitulo": 1, "nCodNF": 999, "nValorTitulo": 100.0},
                    "resumo": {"nValPago": 40.0, "nValAberto": 60.0},
                }
            ],
        }

    async def fake_nfe(*, codigo_nfe=None, numero_nfe=None):
        return {"codigo_nfe": codigo_nfe}

    monkeypatch.setattr(transacoes, "consultar_pedido_venda", fake_pedido)
    monkeypatch.setattr(transacoes, "status_pedido_venda", fake_status)
    monkeypatch.setattr(transacoes.client, "call", fake_call)
    monkeypatch.setattr(transacoes, "consultar_nfe", fake_nfe)

    resultado = await transacoes.ciclo_venda_financeiro(123)

    assert chamadas[0][0:2] == ("financas/mf", "ListarMovimentos")
    assert chamadas[0][2]["nCodOS"] == 123
    assert resultado["financeiro"]["valor_recebido"] == 40.0
    assert resultado["financeiro"]["valor_a_receber"] == 60.0
    assert resultado["nfe"]["codigo_nfe"] == 999
    assert resultado["completo"] is True


@pytest.mark.asyncio
async def test_ciclo_compra_cruza_chave_nfe_e_sinaliza_paginacao(monkeypatch):
    chave = "1" * 44

    async def fake_recebimento(*, id_recebimento=None, chave_nfe=None):
        return {
            "cabec": {
                "nIdReceb": 10,
                "nIdFornecedor": 77,
                "cChaveNfe": chave,
                "cNumeroNFe": "321",
            }
        }

    async def fake_call(endpoint, call, param, **kwargs):
        return {
            "nTotPaginas": 2,
            "nTotRegistros": 600,
            "movimentos": [
                {
                    "detalhes": {
                        "nCodCliente": 77,
                        "cChaveNFe": chave,
                        "nCodTitulo": 5,
                        "nValorTitulo": 500.0,
                    },
                    "resumo": {"nValPago": 200.0, "nValAberto": 300.0},
                },
                {
                    "detalhes": {"nCodCliente": 77, "cChaveNFe": "2" * 44, "nCodTitulo": 6, "nValorTitulo": 10.0},
                    "resumo": {"nValPago": 0.0, "nValAberto": 10.0},
                },
            ],
        }

    monkeypatch.setattr(transacoes, "consultar_recebimento_nfe", fake_recebimento)
    monkeypatch.setattr(transacoes.client, "call", fake_call)

    resultado = await transacoes.ciclo_recebimento_compra_financeiro(chave_nfe=chave)

    assert resultado["financeiro"]["quantidade_titulos"] == 1
    assert resultado["financeiro"]["valor_pago"] == 200.0
    assert resultado["financeiro"]["valor_a_pagar"] == 300.0
    assert resultado["completo"] is False
