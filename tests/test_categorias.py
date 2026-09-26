import pytest

from omie_mcp import categorias


@pytest.mark.asyncio
async def test_listar_categorias_semanticas_normaliza_dre_e_situacao(monkeypatch):
    chamadas = []

    async def fake_call(endpoint, call, param, **kwargs):
        chamadas.append((endpoint, call, param))
        return {
            "pagina": 1,
            "total_de_paginas": 1,
            "registros": 2,
            "total_de_registros": 2,
            "categoria_cadastro": [
                {
                    "codigo": "1.01",
                    "descricao": "Vendas de Peças",
                    "conta_inativa": "N",
                    "totalizadora": "N",
                    "conta_receita": "S",
                    "tipo_categoria": "VEN",
                    "codigo_dre": "100",
                    "dadosDRE": {
                        "codigoDRE": "100",
                        "descricaoDRE": "Receita Bruta de Vendas",
                        "nivelDRE": 3,
                        "sinalDRE": "+",
                        "totalizaDRE": "N",
                        "naoExibirDRE": "N",
                    },
                },
                {
                    "codigo": "2.01",
                    "descricao": "Despesas Operacionais",
                    "conta_inativa": "N",
                    "totalizadora": "S",
                },
            ],
        }

    monkeypatch.setattr(categorias.client, "call", fake_call)

    resposta = await categorias.listar_categorias_semanticas(apenas_ativas=True, tipo="R")

    assert chamadas[0][0:2] == ("geral/categorias", "ListarCategorias")
    assert chamadas[0][2]["filtrar_apenas_ativo"] == "S"
    assert chamadas[0][2]["filtrar_por_tipo"] == "R"
    assert resposta["categorias"][0]["situacao"] == "Ativo"
    assert resposta["categorias"][0]["conta_dre"] == "Receita Bruta de Vendas"
    assert resposta["categorias"][1]["situacao"] == "Grupo"


@pytest.mark.asyncio
async def test_consultar_categoria_semantica(monkeypatch):
    async def fake_call(endpoint, call, param, **kwargs):
        assert endpoint == "geral/categorias"
        assert call == "ConsultarCategoria"
        assert param == {"codigo": "2.02"}
        return {
            "codigo": "2.02",
            "descricao": "Frete de Compras",
            "conta_inativa": "N",
            "totalizadora": "N",
            "conta_despesa": "S",
            "dadosDRE": {"codigoDRE": "200", "descricaoDRE": "Outros Custos"},
        }

    monkeypatch.setattr(categorias.client, "call", fake_call)
    resposta = await categorias.consultar_categoria_semantica("2.02")

    assert resposta["encontrado"] is True
    assert resposta["categoria"]["descricao"] == "Frete de Compras"
    assert resposta["categoria"]["conta_dre"] == "Outros Custos"


def test_tipo_categoria_rejeita_valor_invalido():
    async def executar():
        await categorias.listar_categorias_semanticas(tipo="X")

    with pytest.raises(ValueError, match="Receita"):
        import asyncio
        asyncio.run(executar())
