import pytest

from omie_mcp import escrita_segura
from omie_mcp.client import OmieWriteBlocked


@pytest.mark.asyncio
async def test_escrita_exige_confirmacao_semantica():
    with pytest.raises(OmieWriteBlocked):
        await escrita_segura.upsert_cliente_seguro(
            cadastro={"codigo_cliente_integracao": "TESTE"},
            confirmar=False,
            motivo="teste controlado",
        )


@pytest.mark.asyncio
async def test_escrita_exige_motivo_auditavel():
    with pytest.raises(OmieWriteBlocked):
        await escrita_segura.upsert_cliente_seguro(
            cadastro={"codigo_cliente_integracao": "TESTE"},
            confirmar=True,
            motivo="x",
        )


@pytest.mark.asyncio
async def test_upsert_cliente_repassa_confirm_write(monkeypatch):
    capturado = {}

    async def fake_call(endpoint, call, param, **kwargs):
        capturado.update(endpoint=endpoint, call=call, param=param, kwargs=kwargs)
        return {"ok": True}

    monkeypatch.setattr(escrita_segura.client, "call", fake_call)
    resposta = await escrita_segura.upsert_cliente_seguro(
        cadastro={"codigo_cliente_integracao": "TESTE-001", "razao_social": "Teste"},
        confirmar=True,
        motivo="cadastro homologacao",
    )

    assert capturado["endpoint"] == "geral/clientes"
    assert capturado["call"] == "UpsertCliente"
    assert capturado["kwargs"]["confirm_write"] is True
    assert resposta["operacao"] == "UpsertCliente"


@pytest.mark.asyncio
async def test_baixa_pagamento_valida_valor():
    with pytest.raises(ValueError):
        await escrita_segura.lancar_pagamento_seguro(
            codigo_lancamento=1,
            codigo_conta_corrente=2,
            valor=0,
            data="11/09/2026",
            confirmar=True,
            motivo="teste pagamento",
        )


def test_entrypoint_seguro_importa():
    import omie_mcp.safe_app as safe_app
    assert safe_app.mcp is not None
