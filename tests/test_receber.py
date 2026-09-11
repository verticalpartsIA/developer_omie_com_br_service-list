from omie_mcp.receber import normalizar_movimento_conta_receber


def test_normalizar_movimento_conta_receber_valores_principais():
    movimento = {
        "detalhes": {
            "nCodTitulo": 123,
            "cNumTitulo": "CR-001",
            "nCodCliente": 456,
            "nValorTitulo": 1000.0,
            "cStatus": "PAGTOPARCIAL",
        },
        "resumo": {
            "nValPago": 400.0,
            "nValAberto": 600.0,
            "nValLiquido": 400.0,
            "nDesconto": 0.0,
            "nJuros": 0.0,
            "nMulta": 0.0,
        },
    }

    conta = normalizar_movimento_conta_receber(movimento)

    assert conta["codigo_lancamento_omie"] == 123
    assert conta["numero_documento"] == "CR-001"
    assert conta["valor_conta"] == 1000.0
    assert conta["valor_recebido"] == 400.0
    assert conta["valor_a_receber"] == 600.0
    assert conta["situacao"] == "PAGTOPARCIAL"
