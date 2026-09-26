import pytest

from omie_mcp import reforma_tributaria as rt


@pytest.mark.asyncio
async def test_listar_cst_usa_endpoint_e_call_oficiais(monkeypatch):
    capturado = {}

    async def fake_call(endpoint, call, param, **kwargs):
        capturado.update(endpoint=endpoint, call=call, param=param)
        return {"cadastros": []}

    monkeypatch.setattr(rt.client, "call", fake_call)
    await rt.listar_cst_ibs_cbs(descricao="tributada")

    assert capturado["endpoint"] == "produtos/icbscst"
    assert capturado["call"] == "ListarCSTIbsCbs"
    assert capturado["param"]["cDescricao"] == "tributada"


@pytest.mark.asyncio
async def test_listar_classificacoes_filtra_por_cst(monkeypatch):
    capturado = {}

    async def fake_call(endpoint, call, param, **kwargs):
        capturado.update(endpoint=endpoint, call=call, param=param)
        return {"cadastros": []}

    monkeypatch.setattr(rt.client, "call", fake_call)
    await rt.listar_classificacoes_ibs_cbs(cst="000")

    assert capturado["endpoint"] == "produtos/classtrib"
    assert capturado["call"] == "ListarClassTrib"
    assert capturado["param"]["cCodCst"] == "000"


@pytest.mark.asyncio
async def test_indicadores_operacao_usa_servicos_indoper(monkeypatch):
    capturado = {}

    async def fake_call(endpoint, call, param, **kwargs):
        capturado.update(endpoint=endpoint, call=call, param=param)
        return {"cadastros": []}

    monkeypatch.setattr(rt.client, "call", fake_call)
    await rt.listar_indicadores_operacao()

    assert capturado["endpoint"] == "servicos/indoper"
    assert capturado["call"] == "ListarIndOper"


@pytest.mark.asyncio
async def test_mapa_reforma_agrega_tres_fontes(monkeypatch):
    async def fake_cst(**kwargs):
        return {"cadastros": [{"cCodigo": "000"}]}

    async def fake_cls(**kwargs):
        return {"cadastros": [{"cCodigo": "000001", "cCodCst": "000"}]}

    async def fake_ind(**kwargs):
        return {"cadastros": [{"cCodigo": "000001"}]}

    monkeypatch.setattr(rt, "listar_cst_ibs_cbs", fake_cst)
    monkeypatch.setattr(rt, "listar_classificacoes_ibs_cbs", fake_cls)
    monkeypatch.setattr(rt, "listar_indicadores_operacao", fake_ind)

    result = await rt.mapa_reforma_tributaria()

    assert result["tipo_visao"] == "REFORMA_TRIBUTARIA"
    assert result["ibs_cbs_cst"]["cadastros"][0]["cCodigo"] == "000"
