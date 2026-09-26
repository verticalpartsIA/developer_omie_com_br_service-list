import pytest

from omie_mcp import projetos


def test_normalizar_projeto_seis_colunas_gerenciais():
    bruto = {
        "codigo": 77,
        "codInt": "OBRA-77",
        "nome": "Elevador Torre A",
        "inativo": "N",
        "info": {
            "data_inc": "10/09/2026",
            "hora_inc": "08:15:00",
            "user_inc": "GELSON",
            "data_alt": "11/09/2026",
            "hora_alt": "01:20:00",
            "user_alt": "ADM",
        },
    }

    item = projetos.normalizar_projeto(bruto)

    assert item["situacao"] == "Ativo"
    assert item["nome_projeto"] == "Elevador Torre A"
    assert item["inclusao"] == "10/09/2026 08:15:00"
    assert item["ultima_alteracao"] == "11/09/2026 01:20:00"
    assert item["incluido_por"] == "GELSON"
    assert item["alterado_por"] == "ADM"
    assert item["codigo_projeto"] == 77
    assert item["codigo_integracao"] == "OBRA-77"


@pytest.mark.asyncio
async def test_listar_projetos_semanticos_repassa_filtros(monkeypatch):
    async def fake_call(endpoint, call, param, **kwargs):
        assert endpoint == "geral/projetos"
        assert call == "ListarProjetos"
        assert param["nome_projeto"] == "Torre"
        assert param["filtrar_apenas_alteracao"] == "S"
        return {
            "pagina": 1,
            "total_de_paginas": 1,
            "registros": 1,
            "total_de_registros": 1,
            "cadastro": [{"codigo": 1, "nome": "Torre", "inativo": "S", "info": {}}],
        }

    monkeypatch.setattr(projetos.client, "call", fake_call)
    resposta = await projetos.listar_projetos_semanticos(nome_projeto="Torre", filtrar_apenas_alteracao="S")

    assert resposta["projetos"][0]["situacao"] == "Inativo"
    assert resposta["colunas_gerenciais"] == [
        "Situação",
        "Nome do Projeto",
        "Inclusão",
        "Última Alteração",
        "Incluído por",
        "Alterado por",
    ]


@pytest.mark.asyncio
async def test_consultar_projeto_semantico(monkeypatch):
    async def fake_call(endpoint, call, param, **kwargs):
        assert endpoint == "geral/projetos"
        assert call == "ConsultarProjeto"
        assert param == {"codigo": 9}
        return {"codigo": 9, "nome": "Projeto 9", "inativo": "N", "info": {}}

    monkeypatch.setattr(projetos.client, "call", fake_call)
    resposta = await projetos.consultar_projeto_semantico(codigo=9)

    assert resposta["encontrado"] is True
    assert resposta["projeto"]["nome_projeto"] == "Projeto 9"
