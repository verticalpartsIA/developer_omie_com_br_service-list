from __future__ import annotations

from typing import Any

from .client import client


def normalizar_produto(produto: dict[str, Any]) -> dict[str, Any]:
    info = produto.get("info") or {}
    caracteristicas = produto.get("caracteristicas") or []
    imagens = produto.get("imagens") or []
    recomendacoes = produto.get("recomendacoes_fiscais") or {}
    inativo = str(produto.get("inativo") or "N").upper() == "S"

    return {
        "situacao": "Inativo" if inativo else "Ativo",
        "descricao": produto.get("descricao"),
        "codigo": produto.get("codigo"),
        "codigo_produto": produto.get("codigo_produto"),
        "codigo_produto_integracao": produto.get("codigo_produto_integracao"),
        "familia_produto": produto.get("descricao_familia"),
        "familia_codigo": produto.get("codigo_familia"),
        "ncm": produto.get("ncm"),
        "cest": recomendacoes.get("id_cest") or produto.get("cest"),
        "ean_gtin": produto.get("ean"),
        "preco_unitario_venda": produto.get("valor_unitario"),
        "unidade": produto.get("unidade"),
        "peso_liquido": produto.get("peso_liq"),
        "peso_bruto": produto.get("peso_bruto"),
        "altura": produto.get("altura"),
        "largura": produto.get("largura"),
        "profundidade": produto.get("profundidade"),
        "marca": produto.get("marca"),
        "modelo": produto.get("modelo"),
        "dias_garantia": produto.get("dias_garantia"),
        "dias_crossdocking": produto.get("dias_crossdocking"),
        "cupom_fiscal_pdv": recomendacoes.get("cupom_fiscal"),
        "marketplace": recomendacoes.get("market_place"),
        "tipo_item_bloco_k": produto.get("tipoItem"),
        "origem_mercadoria": recomendacoes.get("origem_mercadoria"),
        "preco_tabelado_pauta_id": recomendacoes.get("id_preco_tabelado"),
        "produzido_escala_relevante": recomendacoes.get("indicador_escala"),
        "cnpj_fabricante": recomendacoes.get("cnpj_fabricante"),
        "caracteristicas": caracteristicas,
        "leadtime_ressuprimento": produto.get("lead_time"),
        "inclusao_data": info.get("dInc"),
        "inclusao_hora": info.get("hInc"),
        "incluido_por": info.get("uInc"),
        "alteracao_data": info.get("dAlt"),
        "alteracao_hora": info.get("hAlt"),
        "alterado_por": info.get("uAlt"),
        "bloqueado": produto.get("bloqueado"),
        "inativo": produto.get("inativo"),
        "tipo_item": produto.get("tipoItem"),
        "ean": produto.get("ean"),
        "valor_unitario": produto.get("valor_unitario"),
        "familia_descricao": produto.get("descricao_familia"),
        "imagens": imagens,
        "importado_api": info.get("cImpAPI"),
        "recomendacoes_fiscais": recomendacoes,
        "raw": produto,
    }


async def listar_produtos_completo(
    pagina: int = 1,
    registros_por_pagina: int = 50,
    apenas_importado_api: str = "N",
    filtrar_apenas_omiepdv: str = "N",
) -> dict[str, Any]:
    resposta = await client.call(
        "geral/produtos",
        "ListarProdutos",
        {
            "pagina": pagina,
            "registros_por_pagina": registros_por_pagina,
            "apenas_importado_api": apenas_importado_api,
            "filtrar_apenas_omiepdv": filtrar_apenas_omiepdv,
            "exibir_caracteristicas": "S",
            "exibir_obs": "S",
        },
    )
    produtos = resposta.get("produto_servico_cadastro") or resposta.get("produtos") or []
    return {
        "pagina": resposta.get("pagina"),
        "total_paginas": resposta.get("total_de_paginas"),
        "registros": resposta.get("registros"),
        "total_registros": resposta.get("total_de_registros"),
        "produtos": [normalizar_produto(item) for item in produtos],
        "raw": resposta,
    }


async def consultar_produto(
    *,
    codigo_produto: int | None = None,
    codigo_produto_integracao: str | None = None,
    codigo: str | None = None,
) -> dict[str, Any]:
    if not any([codigo_produto, codigo_produto_integracao, codigo]):
        raise ValueError("Informe codigo_produto, codigo_produto_integracao ou codigo")
    payload = {
        key: value
        for key, value in {
            "codigo_produto": codigo_produto,
            "codigo_produto_integracao": codigo_produto_integracao,
            "codigo": codigo,
        }.items()
        if value not in (None, "")
    }
    bruto = await client.call("geral/produtos", "ConsultarProduto", payload)
    return {"bruto": bruto, "visao_normalizada": normalizar_produto(bruto)}


async def posicao_estoque(
    *,
    codigo_produto: int,
    codigo_local_estoque: int = 0,
    data: str | None = None,
    codigo_integracao_produto: str | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "codigo_local_estoque": codigo_local_estoque,
        "id_prod": codigo_produto,
        "cod_int": codigo_integracao_produto or "",
    }
    if data:
        payload["data"] = data
    resposta = await client.call("estoque/consulta", "PosicaoEstoque", payload)
    return {
        "fonte": "Omie /estoque/consulta/ PosicaoEstoque",
        "codigo_produto": codigo_produto,
        "codigo_local_estoque": codigo_local_estoque,
        "posicao": resposta,
    }


async def produto_360(
    *,
    codigo_produto: int | None = None,
    codigo_produto_integracao: str | None = None,
    codigo: str | None = None,
    codigo_local_estoque: int = 0,
    data_estoque: str | None = None,
) -> dict[str, Any]:
    """Visão gerencial de produto: cadastro completo + fiscal + posição de estoque."""
    consulta = await consultar_produto(
        codigo_produto=codigo_produto,
        codigo_produto_integracao=codigo_produto_integracao,
        codigo=codigo,
    )
    cadastro = consulta["visao_normalizada"]
    id_produto = cadastro.get("codigo_produto")

    estoque: dict[str, Any] = {
        "estoque_fisico": None,
        "reservado": None,
        "estoque_disponivel": None,
        "pendente": None,
        "estoque_minimo": None,
        "cmc": None,
        "codigo_local_estoque": codigo_local_estoque,
        "fonte": "Omie /estoque/consulta/ PosicaoEstoque",
    }
    if isinstance(id_produto, int):
        try:
            posicao = await posicao_estoque(
                codigo_produto=id_produto,
                codigo_local_estoque=codigo_local_estoque,
                data=data_estoque,
                codigo_integracao_produto=cadastro.get("codigo_produto_integracao"),
            )
            bruto_estoque = posicao.get("posicao") or {}
            estoque.update({
                "estoque_fisico": bruto_estoque.get("fisico"),
                "reservado": bruto_estoque.get("reservado"),
                "estoque_disponivel": bruto_estoque.get("saldo"),
                "pendente": bruto_estoque.get("pendente"),
                "estoque_minimo": bruto_estoque.get("estoque_minimo"),
                "cmc": bruto_estoque.get("cmc"),
                "codigo_local_estoque": bruto_estoque.get("codigo_local_estoque", codigo_local_estoque),
                "raw": bruto_estoque,
            })
        except Exception as exc:
            estoque["erro_consulta"] = str(exc)

    return {
        "tipo_visao": "PRODUTO_360",
        "completo": "erro_consulta" not in estoque,
        "cadastro": cadastro,
        "estoque": estoque,
        "cabecalho_referencia": [
            "Situação", "Descrição", "Código", "Família de Produto", "Código NCM", "CEST",
            "Código EAN (GTIN)", "Preço Unitário de Venda", "Estoque Físico", "Reservado",
            "Estoque Disponível", "Unidade", "Peso Líquido", "Peso Bruto", "Altura", "Largura",
            "Profundidade", "Marca", "Modelo", "Dias de Garantia", "Dias de Crossdocking",
            "Cupom Fiscal (PDV)", "Marketplace", "Tipo do Item (Bloco K)", "Origem da Mercadoria",
            "Preço Tabelado (Pauta)", "Produzido em Escala Relevante", "CNPJ Fabricante",
            "Características", "Leadtime de Ressuprimento", "Inclusão", "Última Alteração",
            "Incluído por", "Alterado por",
        ],
        "observacoes": {
            "estoque_disponivel": "Mapeado do campo saldo retornado por PosicaoEstoque.",
            "preco_tabelado_pauta": "A API de Produtos expõe id_preco_tabelado; por isso o MCP não inventa o valor monetário da pauta.",
        },
        "fontes": [
            "Omie /geral/produtos/ ConsultarProduto",
            "Omie /estoque/consulta/ PosicaoEstoque",
        ],
    }


async def listar_posicao_estoque(
    *,
    pagina: int = 1,
    registros_por_pagina: int = 50,
    data_posicao: str | None = None,
    exibir_todos: str = "N",
    codigo_local_estoque: int = 0,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "nPagina": pagina,
        "nRegPorPagina": registros_por_pagina,
        "cExibeTodos": exibir_todos,
        "codigo_local_estoque": codigo_local_estoque,
    }
    if data_posicao:
        payload["dDataPosicao"] = data_posicao
    return await client.call("estoque/consulta", "ListarPosEstoque", payload)


async def listar_movimentos_estoque(
    *,
    pagina: int = 1,
    registros_por_pagina: int = 50,
    codigo_produto: int = 0,
    codigo_local_estoque: int = 0,
    data_inicial: str | None = None,
    data_final: str | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "nPagina": pagina,
        "nRegPorPagina": registros_por_pagina,
        "codigo_local_estoque": codigo_local_estoque,
        "idProd": codigo_produto,
        "lista_local_estoque": "",
    }
    if data_inicial:
        payload["dDtInicial"] = data_inicial
    if data_final:
        payload["dDtFinal"] = data_final
    return await client.call("estoque/consulta", "ListarMovimentoEstoque", payload)
