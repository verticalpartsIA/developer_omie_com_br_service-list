from omie_mcp.enriquecimento import normalizar_catalogos
from omie_mcp.relatorios_completos import enriquecer_titulos


def test_normalizar_catalogos_e_enriquecer_titulo_pagar():
    catalogos = normalizar_catalogos(
        categorias={"categoria_cadastro": [{"codigo": "2.01", "descricao": "Compras"}]},
        vendedores={"cadastro": [{"codigo": 7, "nome": "Ana"}]},
        projetos={"cadastro": [{"codigo": 9, "nome": "Obra X"}]},
        contas_correntes={"ListarContasCorrentes": [{"nCodCC": 11, "descricao": "Banco Principal", "codigo_banco": "341"}]},
        tipos_documento={"tipo_documento_cadastro": [{"codigo": "NF", "descricao": "Nota Fiscal"}]},
    )
    contas = [{
        "codigo_fornecedor": 55,
        "categoria_codigo": "2.01",
        "vendedor_codigo": 7,
        "projeto_codigo": 9,
        "conta_corrente_codigo": 11,
        "tipo_documento_codigo": "NF",
        "valor_pago": 400.0,
        "valor_a_pagar": 600.0,
    }]
    parceiros = {55: {"razao_social": "Fornecedor Teste", "nome_fantasia": "Fornecedor"}}
    categorias_resolvidas = {
        "2.01": {
            "codigo": "2.01",
            "descricao": "Compras de Mercadorias",
            "situacao": "Ativo",
            "tipo_movimento": "Despesa",
            "natureza": "Compra para revenda",
            "categoria_superior": "2",
            "codigo_dre": "2.01",
            "conta_dre": "Deduções de Receita",
            "dre": {"codigo": "2.01", "descricao": "Deduções de Receita", "nivel": 2},
            "id_conta_contabil": "2.01.01",
            "tag_conta_contabil": "Compras",
        }
    }

    resultado = enriquecer_titulos(
        contas,
        catalogos=catalogos,
        parceiros=parceiros,
        tipo="PAGAR",
        categorias_resolvidas=categorias_resolvidas,
    )
    enr = resultado[0]["enriquecido"]

    assert enr["parceiro"]["razao_social"] == "Fornecedor Teste"
    assert enr["categoria_descricao"] == "Compras de Mercadorias"
    assert enr["categoria_tipo_movimento"] == "Despesa"
    assert enr["categoria_conta_dre"] == "Deduções de Receita"
    assert enr["categoria_natureza"] == "Compra para revenda"
    assert enr["categoria"]["codigo_dre"] == "2.01"
    assert enr["vendedor_nome"] == "Ana"
    assert enr["projeto_nome"] == "Obra X"
    assert enr["conta_corrente_descricao"] == "Banco Principal"
    assert enr["conta_corrente_banco_codigo"] == "341"
    assert enr["tipo_documento_descricao"] == "Nota Fiscal"


def test_enriquecimento_categoria_falha_sem_quebrar_relatorio():
    contas = [{"codigo_fornecedor": 55, "categoria_codigo": "9.99"}]
    resultado = enriquecer_titulos(
        contas,
        catalogos={"categorias": {}, "vendedores": {}, "projetos": {}, "contas_correntes": {}, "tipos_documento": {}},
        parceiros={},
        tipo="PAGAR",
        categorias_resolvidas={"9.99": {"codigo": "9.99", "erro_enriquecimento": "categoria não encontrada"}},
    )
    categoria = resultado[0]["enriquecido"]["categoria"]
    assert categoria["encontrado"] is False
    assert "não encontrada" in categoria["erro_enriquecimento"]


def test_normalizar_catalogos_tolera_nome_de_lista_alternativo():
    catalogos = normalizar_catalogos(
        categorias={"qualquer_nome": [{"codigo": "1", "descricao": "Receita"}]},
        vendedores={"cadastro": []},
        projetos={"cadastro": []},
        contas_correntes={"conta_corrente_lista": []},
        tipos_documento={"tipo_documento_cadastro": []},
    )
    assert catalogos["categorias"]["1"]["descricao"] == "Receita"
