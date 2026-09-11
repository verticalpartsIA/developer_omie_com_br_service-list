import pytest

from omie_mcp import produtos_estoque
from omie_mcp.produtos_estoque import normalizar_produto


def test_normalizar_produto_campos_principais():
    produto = {
        "codigo_produto": 123,
        "codigo_produto_integracao": "P-123",
        "codigo": "ABC",
        "descricao": "Motor",
        "unidade": "UN",
        "ncm": "8501.52.10",
        "ean": "7891234567890",
        "valor_unitario": 1000.0,
        "codigo_familia": 10,
        "descricao_familia": "Motores",
        "tipoItem": "00",
        "peso_liq": 10.5,
        "peso_bruto": 11.0,
        "altura": 20.0,
        "largura": 30.0,
        "profundidade": 40.0,
        "marca": "VP",
        "modelo": "M10",
        "dias_garantia": 365,
        "dias_crossdocking": 3,
        "lead_time": 15,
        "inativo": "N",
        "caracteristicas": [{"cNomeCaract": "Potência", "cConteudo": "10cv"}],
        "recomendacoes_fiscais": {
            "id_cest": "12.345.67",
            "origem_mercadoria": "1",
            "id_preco_tabelado": 44,
            "cupom_fiscal": "S",
            "market_place": "N",
            "indicador_escala": "S",
            "cnpj_fabricante": "12345678000199",
        },
        "info": {
            "dInc": "10/09/2026",
            "hInc": "08:00:00",
            "uInc": "USR",
            "dAlt": "11/09/2026",
            "hAlt": "09:00:00",
            "uAlt": "USR2",
        },
    }
    result = normalizar_produto(produto)
    assert result["codigo_produto"] == 123
    assert result["situacao"] == "Ativo"
    assert result["descricao"] == "Motor"
    assert result["familia_produto"] == "Motores"
    assert result["ncm"] == "8501.52.10"
    assert result["cest"] == "12.345.67"
    assert result["ean_gtin"] == "7891234567890"
    assert result["preco_unitario_venda"] == 1000.0
    assert result["origem_mercadoria"] == "1"
    assert result["cupom_fiscal_pdv"] == "S"
    assert result["marketplace"] == "N"
    assert result["produzido_escala_relevante"] == "S"
    assert result["leadtime_ressuprimento"] == 15
    assert result["caracteristicas"][0]["cNomeCaract"] == "Potência"
    assert result["incluido_por"] == "USR"
    assert result["alterado_por"] == "USR2"


@pytest.mark.asyncio
async def test_produto_360_combina_cadastro_e_estoque(monkeypatch):
    async def fake_consultar_produto(**kwargs):
        return {
            "bruto": {},
            "visao_normalizada": {
                "codigo_produto": 123,
                "codigo_produto_integracao": "P-123",
                "codigo": "ABC",
                "descricao": "Motor",
            },
        }

    async def fake_posicao_estoque(**kwargs):
        assert kwargs["codigo_produto"] == 123
        return {
            "posicao": {
                "fisico": 20.0,
                "reservado": 5.0,
                "saldo": 15.0,
                "pendente": 2.0,
                "estoque_minimo": 3.0,
                "cmc": 800.0,
                "codigo_local_estoque": 1,
            }
        }

    monkeypatch.setattr(produtos_estoque, "consultar_produto", fake_consultar_produto)
    monkeypatch.setattr(produtos_estoque, "posicao_estoque", fake_posicao_estoque)

    resposta = await produtos_estoque.produto_360(codigo_produto=123, codigo_local_estoque=1)

    assert resposta["tipo_visao"] == "PRODUTO_360"
    assert resposta["completo"] is True
    assert resposta["estoque"]["estoque_fisico"] == 20.0
    assert resposta["estoque"]["reservado"] == 5.0
    assert resposta["estoque"]["estoque_disponivel"] == 15.0
    assert len(resposta["cabecalho_referencia"]) == 34
