import pytest

from omie_mcp import financeiro, receber


@pytest.mark.asyncio
async def test_contas_pagar_todas_percorre_paginas(monkeypatch):
    async def fake_listar(*, pagina=1, **kwargs):
        return {
            "total_paginas": 2,
            "total_registros": 2,
            "fonte": "x",
            "regra_valor_pago": "pago",
            "regra_valor_a_pagar": "aberto",
            "contas": [{"pagina": pagina}],
        }

    monkeypatch.setattr(financeiro, "listar_contas_pagar_financeiro", fake_listar)
    result = await financeiro.listar_contas_pagar_financeiro_todas()

    assert result["completo"] is True
    assert result["paginas_lidas"] == 2
    assert [item["pagina"] for item in result["contas"]] == [1, 2]


@pytest.mark.asyncio
async def test_contas_receber_todas_respeita_limite(monkeypatch):
    async def fake_listar(*, pagina=1, **kwargs):
        return {
            "total_paginas": 5,
            "total_registros": 5,
            "fonte": "x",
            "regra_valor_recebido": "pago",
            "regra_valor_a_receber": "aberto",
            "contas": [{"pagina": pagina}],
        }

    monkeypatch.setattr(receber, "listar_contas_receber_financeiro", fake_listar)
    result = await receber.listar_contas_receber_financeiro_todas(max_paginas=2)

    assert result["completo"] is False
    assert result["paginas_lidas"] == 2
    assert len(result["contas"]) == 2
