import pytest

from omie_mcp import crm, fiscal, servicos


@pytest.mark.asyncio
async def test_crm_listar_oportunidades_usa_filtros(monkeypatch):
    capturado = {}

    async def fake_call(endpoint, call, param, **kwargs):
        capturado.update(endpoint=endpoint, call=call, param=param)
        return {"ok": True}

    monkeypatch.setattr(crm.client, "call", fake_call)
    await crm.listar_oportunidades(status="A,V", fase=2, codigo_vendedor=9, filtrar_por_conta=77)

    assert capturado["endpoint"] == "crm/oportunidades"
    assert capturado["call"] == "ListarOportunidades"
    assert capturado["param"]["status"] == "A,V"
    assert capturado["param"]["filtrar_por_conta"] == 77


@pytest.mark.asyncio
async def test_crm_tarefas_por_oportunidade(monkeypatch):
    capturado = {}

    async def fake_call(endpoint, call, param, **kwargs):
        capturado.update(endpoint=endpoint, call=call, param=param)
        return {"ok": True}

    monkeypatch.setattr(crm.client, "call", fake_call)
    await crm.listar_tarefas_crm(codigo_oportunidade=123)

    assert capturado["endpoint"] == "crm/tarefas"
    assert capturado["call"] == "ListarTarefas"
    assert capturado["param"]["nCodOp"] == 123


@pytest.mark.asyncio
async def test_os_e_nfse_usam_metodos_oficiais(monkeypatch):
    chamadas = []

    async def fake_call(endpoint, call, param, **kwargs):
        chamadas.append((endpoint, call, param))
        return {"ok": True}

    monkeypatch.setattr(servicos.client, "call", fake_call)
    await servicos.listar_os()
    await servicos.listar_nfse(codigo_os=456)

    assert chamadas[0][0:2] == ("servicos/os", "ListarOS")
    assert chamadas[1][0:2] == ("servicos/nfse", "ListarNFSEs")
    assert chamadas[1][2]["nCodigoOS"] == 456


@pytest.mark.asyncio
async def test_documentos_fiscais_painel_contador(monkeypatch):
    capturado = {}

    async def fake_call(endpoint, call, param, **kwargs):
        capturado.update(endpoint=endpoint, call=call, param=param)
        return {"documentosEncontrados": []}

    monkeypatch.setattr(fiscal.client, "call", fake_call)
    await fiscal.listar_documentos_fiscais(modelo="99", operacao="1", chave="1" * 44)

    assert capturado["endpoint"] == "contador/xml"
    assert capturado["call"] == "ListarDocumentos"
    assert capturado["param"]["cModelo"] == "99"
    assert capturado["param"]["nChave"] == "1" * 44


@pytest.mark.asyncio
async def test_resumo_contador(monkeypatch):
    capturado = {}

    async def fake_call(endpoint, call, param, **kwargs):
        capturado.update(endpoint=endpoint, call=call, param=param)
        return {"ok": True}

    monkeypatch.setattr(fiscal.client, "call", fake_call)
    await fiscal.resumo_contador(data_inicio="01/09/2026", data_fim="30/09/2026")

    assert capturado["endpoint"] == "contador/resumo"
    assert capturado["call"] == "ObterResumoContador"
