from __future__ import annotations

from typing import Any

from .client import client


def normalizar_categoria(item: dict[str, Any]) -> dict[str, Any]:
    dre = item.get("dadosDRE") or {}
    inativa = str(item.get("conta_inativa") or "N").upper() == "S"
    totalizadora = str(item.get("totalizadora") or "N").upper() == "S"

    tipo_movimento = None
    if str(item.get("conta_receita") or "N").upper() == "S":
        tipo_movimento = "Receita"
    elif str(item.get("conta_despesa") or "N").upper() == "S":
        tipo_movimento = "Despesa"

    return {
        "codigo": item.get("codigo"),
        "descricao": item.get("descricao"),
        "descricao_padrao": item.get("descricao_padrao"),
        "situacao": "Inativo" if inativa else ("Grupo" if totalizadora else "Ativo"),
        "tipo_movimento": tipo_movimento,
        "conta_inativa": item.get("conta_inativa"),
        "totalizadora": item.get("totalizadora"),
        "categoria_superior": item.get("categoria_superior"),
        "natureza": item.get("natureza"),
        "tipo_categoria": item.get("tipo_categoria"),
        "conta_despesa": item.get("conta_despesa"),
        "conta_receita": item.get("conta_receita"),
        "codigo_dre": item.get("codigo_dre") or dre.get("codigoDRE"),
        "conta_dre": dre.get("descricaoDRE"),
        "dre": {
            "codigo": dre.get("codigoDRE"),
            "descricao": dre.get("descricaoDRE"),
            "nivel": dre.get("nivelDRE"),
            "sinal": dre.get("sinalDRE"),
            "totalizadora": dre.get("totalizaDRE"),
            "nao_exibir": dre.get("naoExibirDRE"),
        },
        "definida_pelo_usuario": item.get("definida_pelo_usuario"),
        "id_conta_contabil": item.get("id_conta_contabil"),
        "tag_conta_contabil": item.get("tag_conta_contabil"),
        "nao_exibir": item.get("nao_exibir"),
        "transferencia": item.get("transferencia"),
        "raw": item,
    }


async def listar_categorias_semanticas(
    pagina: int = 1,
    registros_por_pagina: int = 100,
    apenas_ativas: bool = False,
    tipo: str | None = None,
    descricao: str | None = None,
) -> dict[str, Any]:
    """Lista categorias do Omie com DRE e atributos gerenciais normalizados."""
    if tipo is not None:
        tipo = tipo.upper().strip()
        if tipo not in {"R", "D"}:
            raise ValueError("tipo deve ser 'R' (Receita) ou 'D' (Despesa).")

    param: dict[str, Any] = {
        "pagina": pagina,
        "registros_por_pagina": registros_por_pagina,
    }
    if apenas_ativas:
        param["filtrar_apenas_ativo"] = "S"
    if tipo:
        param["filtrar_por_tipo"] = tipo
    if descricao:
        param["descricao"] = descricao

    resposta = await client.call("geral/categorias", "ListarCategorias", param)
    itens = resposta.get("categoria_cadastro") or []

    return {
        "pagina": resposta.get("pagina"),
        "total_de_paginas": resposta.get("total_de_paginas"),
        "registros": resposta.get("registros"),
        "total_de_registros": resposta.get("total_de_registros"),
        "filtros": {
            "apenas_ativas": apenas_ativas,
            "tipo": tipo,
            "descricao": descricao,
        },
        "categorias": [normalizar_categoria(item) for item in itens if isinstance(item, dict)],
        "fonte": "Omie /geral/categorias/ ListarCategorias",
    }


async def consultar_categoria_semantica(codigo: str) -> dict[str, Any]:
    """Consulta uma categoria específica pelo código e devolve sua leitura gerencial."""
    resposta = await client.call("geral/categorias", "ConsultarCategoria", {"codigo": codigo})
    return {
        "encontrado": True,
        "categoria": normalizar_categoria(resposta),
        "fonte": "Omie /geral/categorias/ ConsultarCategoria",
    }


async def resolver_categorias_dos_titulos(
    contas: list[dict[str, Any]],
    *,
    chave_categoria: str = "categoria_codigo",
) -> dict[str, dict[str, Any]]:
    """Resolve apenas as categorias presentes nos títulos, uma vez por código.

    Evita depender da primeira página de ListarCategorias e mantém o relatório
    operacional mesmo se uma categoria auxiliar específica falhar.
    """
    codigos = sorted({str(conta[chave_categoria]) for conta in contas if conta.get(chave_categoria) not in (None, "")})
    resolvidas: dict[str, dict[str, Any]] = {}
    for codigo in codigos:
        try:
            consulta = await consultar_categoria_semantica(codigo)
            categoria = consulta.get("categoria") or {}
            resolvidas[codigo] = categoria
        except Exception as exc:
            resolvidas[codigo] = {
                "codigo": codigo,
                "encontrado": False,
                "erro_enriquecimento": str(exc),
            }
    return resolvidas
