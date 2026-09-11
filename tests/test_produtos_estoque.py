from omie_mcp.produtos_estoque import normalizar_produto


def test_normalizar_produto_campos_principais():
    produto = {
        "codigo_produto": 123,
        "codigo_produto_integracao": "P-123",
        "codigo": "ABC",
        "descricao": "Motor",
        "unidade": "UN",
        "ncm": "8501.52.10",
        "valor_unitario": 1000.0,
        "marca": "VP",
        "caracteristicas": [{"cNomeCaract": "Potência", "cConteudo": "10cv"}],
        "info": {"dInc": "10/09/2026", "uInc": "USR"},
    }
    result = normalizar_produto(produto)
    assert result["codigo_produto"] == 123
    assert result["descricao"] == "Motor"
    assert result["ncm"] == "8501.52.10"
    assert result["caracteristicas"][0]["cNomeCaract"] == "Potência"
    assert result["incluido_por"] == "USR"
