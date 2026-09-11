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

    resultado = enriquecer_titulos(contas, catalogos=catalogos, parceiros=parceiros, tipo="PAGAR")
    enr = resultado[0]["enriquecido"]

    assert enr["parceiro"]["razao_social"] == "Fornecedor Teste"
    assert enr["categoria_descricao"] == "Compras"
    assert enr["vendedor_nome"] == "Ana"
    assert enr["projeto_nome"] == "Obra X"
    assert enr["conta_corrente_descricao"] == "Banco Principal"
    assert enr["conta_corrente_banco_codigo"] == "341"
    assert enr["tipo_documento_descricao"] == "Nota Fiscal"


def test_normalizar_catalogos_tolera_nome_de_lista_alternativo():
    catalogos = normalizar_catalogos(
        categorias={"qualquer_nome": [{"codigo": "1", "descricao": "Receita"}]},
        vendedores={"cadastro": []},
        projetos={"cadastro": []},
        contas_correntes={"conta_corrente_lista": []},
        tipos_documento={"tipo_documento_cadastro": []},
    )
    assert catalogos["categorias"]["1"]["descricao"] == "Receita"
