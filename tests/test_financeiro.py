from omie_mcp.financeiro import normalizar_movimento_conta_pagar


def test_normaliza_valor_pago_e_valor_a_pagar():
    movimento = {
        "detalhes": {
            "nCodTitulo": 123,
            "cNumTitulo": "NF-987",
            "cNumParcela": "001/002",
            "nValorTitulo": 1000.0,
            "cStatus": "PAGTOPARCIAL",
            "dDtPagamento": "10/09/2026",
        },
        "resumo": {
            "cLiquidado": "N",
            "nValPago": 400.0,
            "nValAberto": 600.0,
            "nDesconto": 0.0,
            "nJuros": 0.0,
            "nMulta": 0.0,
            "nValLiquido": 400.0,
        },
    }

    conta = normalizar_movimento_conta_pagar(movimento)

    assert conta["valor_conta"] == 1000.0
    assert conta["valor_pago"] == 400.0
    assert conta["valor_a_pagar"] == 600.0
    assert conta["situacao"] == "PAGTOPARCIAL"
    assert conta["ultimo_pagamento"] == "10/09/2026"
