from __future__ import annotations

from typing import Any

from .client import client


def normalizar_produto(produto: dict[str, Any]) -> dict[str, Any]:
    info = produto.get("info") or {}
    caracteristicas = produto.get("caracteristicas") or []
    imagens = produto.get("imagens") or []
    return {
        "codigo_produto": produto.get("codigo_produto"),
        "codigo_produto_integracao": produto.get("codigo_produto_integracao"),
        "codigo": produto.get("codigo"),
        "descricao": produto.get("descricao"),
        "unidade": produto.get("unidade"),
        "ncm": produto.get("ncm"),
        "ean": produto.get("ean"),
        "valor_unitario": produto.get("valor_unitario"),
        "tipo_item": produto.get("tipoItem"),
        "familia_codigo": produto.get("codigo_familia"),
        "familia_descricao": produto.get("descricao_familia"),
        "marca": produto.get("marca"),
        "peso_liquido": produto.get("peso_liq"),
        "peso_bruto": produto.get("peso_bruto"),
        "bloqueado": produto.get("bloqueado"),
        "inativo": produto.get("inativo"),
        "caracteristicas": caracteristicas,
        "imagens": imagens,
        "inclusao_data": info.get("dInc"),
        "inclusao_hora": info.get("hInc"),
        "incluido_por": info.get("uInc"),
        "alteracao_data": info.get("dAlt"),
        "alteracao_hora": info.get("hAlt"),
        "alterado_por": info.get("uAlt"),
        "importado_api": info.get("cImpAPI"),
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
