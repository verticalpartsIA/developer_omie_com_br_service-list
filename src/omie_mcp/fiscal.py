from __future__ import annotations

from typing import Any

from .client import client


async def listar_documentos_fiscais(
    *,
    pagina: int = 1,
    registros_por_pagina: int = 20,
    modelo: str = "55",
    operacao: str = "1",
    ambiente: str = "P",
    emissao_inicial: str | None = None,
    emissao_final: str | None = None,
    chave: str | None = None,
    id_nota: int | None = None,
) -> dict[str, Any]:
    param: dict[str, Any] = {
        "nPagina": pagina,
        "nRegPorPagina": registros_por_pagina,
        "cModelo": modelo,
        "cOperacao": operacao,
        "cAmbiente": ambiente,
    }
    opcionais = {
        "dEmiInicial": emissao_inicial,
        "dEmiFinal": emissao_final,
        "nChave": chave,
        "nIdNF": id_nota,
    }
    param.update({k: v for k, v in opcionais.items() if v is not None})
    return await client.call("contador/xml", "ListarDocumentos", param)


async def resumo_contador(*, data_inicio: str, data_fim: str) -> dict[str, Any]:
    return await client.call(
        "contador/resumo",
        "ObterResumoContador",
        {"dDataInicio": data_inicio, "dDataFim": data_fim},
    )


async def documento_fiscal_por_chave(chave: str, *, modelo: str = "55", operacao: str = "1") -> dict[str, Any]:
    resposta = await listar_documentos_fiscais(
        pagina=1,
        registros_por_pagina=20,
        modelo=modelo,
        operacao=operacao,
        chave=chave,
    )
    docs = resposta.get("documentosEncontrados") or []
    return {
        "encontrado": bool(docs),
        "chave": chave,
        "documentos": docs,
        "fonte": "Omie /contador/xml/ ListarDocumentos",
    }
