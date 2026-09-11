from __future__ import annotations

from typing import Any

from .client import client


def normalizar_movimento_conta_pagar(movimento: dict[str, Any]) -> dict[str, Any]:
    detalhes = movimento.get("detalhes") or {}
    resumo = movimento.get("resumo") or {}

    return {
        "codigo_lancamento_omie": detalhes.get("nCodTitulo"),
        "codigo_lancamento_integracao": detalhes.get("cCodIntTitulo"),
        "numero_documento": detalhes.get("cNumTitulo"),
        "parcela": detalhes.get("cNumParcela"),
        "nota_fiscal": detalhes.get("cNumDocFiscal"),
        "codigo_fornecedor": detalhes.get("nCodCliente"),
        "fornecedor_cpf_cnpj": detalhes.get("cCPFCNPJCliente"),
        "previsao_pagamento": detalhes.get("dDtPrevisao"),
        "ultimo_pagamento": detalhes.get("dDtPagamento"),
        "vencimento": detalhes.get("dDtVenc"),
        "data_emissao": detalhes.get("dDtEmissao"),
        "data_registro": detalhes.get("dDtRegistro"),
        "valor_conta": detalhes.get("nValorTitulo"),
        "valor_pago": resumo.get("nValPago"),
        "valor_a_pagar": resumo.get("nValAberto"),
        "valor_liquido": resumo.get("nValLiquido"),
        "desconto": resumo.get("nDesconto"),
        "juros": resumo.get("nJuros"),
        "multa": resumo.get("nMulta"),
        "liquidado": resumo.get("cLiquidado"),
        "situacao": detalhes.get("cStatus"),
        "categoria_codigo": detalhes.get("cCodCateg"),
        "operacao_codigo": detalhes.get("cOperacao"),
        "vendedor_codigo": detalhes.get("cCodVendedor"),
        "projeto_codigo": detalhes.get("cCodProjeto"),
        "conta_corrente_codigo": detalhes.get("nCodCC"),
        "tipo_documento_codigo": detalhes.get("cTipo"),
        "observacao": detalhes.get("observacao"),
        "inclusao": detalhes.get("dDtInc"),
        "ultima_alteracao": detalhes.get("dDtAlt"),
        "incluido_por": detalhes.get("cUsInc"),
        "alterado_por": detalhes.get("cUsAlt"),
        "codigo_baixa": detalhes.get("nCodBaixa"),
        "nsu_comprovante": detalhes.get("cNSU"),
        "origem_codigo": detalhes.get("cOrigem"),
        "raw": movimento,
    }


async def listar_contas_pagar_financeiro(
    *,
    pagina: int = 1,
    registros_por_pagina: int = 100,
    status: str | None = None,
    codigo_fornecedor: int | None = None,
    cpf_cnpj: str | None = None,
    codigo_projeto: int | None = None,
    vencimento_de: str | None = None,
    vencimento_ate: str | None = None,
    pagamento_de: str | None = None,
    pagamento_ate: str | None = None,
) -> dict[str, Any]:
    param: dict[str, Any] = {
        "nPagina": pagina,
        "nRegPorPagina": registros_por_pagina,
        "cTpLancamento": "CP",
        "cNatureza": "P",
        "lDadosCad": True,
    }

    opcionais = {
        "cStatus": status,
        "nCodCliente": codigo_fornecedor,
        "cCPFCNPJCliente": cpf_cnpj,
        "nCodProjeto": codigo_projeto,
        "dDtVencDe": vencimento_de,
        "dDtVencAte": vencimento_ate,
        "dDtPagtoDe": pagamento_de,
        "dDtPagtoAte": pagamento_ate,
    }
    param.update({k: v for k, v in opcionais.items() if v is not None})

    response = await client.call("financas/mf", "ListarMovimentos", param)
    movimentos = response.get("movimentos") or []

    return {
        "pagina": response.get("nPagina"),
        "total_paginas": response.get("nTotPaginas"),
        "registros": response.get("nRegistros"),
        "total_registros": response.get("nTotRegistros"),
        "fonte": "Omie /financas/mf/ ListarMovimentos",
        "regra_valor_pago": "resumo.nValPago",
        "regra_valor_a_pagar": "resumo.nValAberto",
        "contas": [normalizar_movimento_conta_pagar(item) for item in movimentos],
    }


async def listar_contas_pagar_financeiro_todas(
    *,
    registros_por_pagina: int = 100,
    max_paginas: int = 100,
    **filtros: Any,
) -> dict[str, Any]:
    """Percorre páginas de Contas a Pagar até completar ou atingir o limite de segurança."""
    primeira = await listar_contas_pagar_financeiro(
        pagina=1,
        registros_por_pagina=registros_por_pagina,
        **filtros,
    )
    total_paginas = int(primeira.get("total_paginas") or 1)
    alvo = min(total_paginas, max_paginas)
    contas = list(primeira.get("contas") or [])

    for pagina in range(2, alvo + 1):
        atual = await listar_contas_pagar_financeiro(
            pagina=pagina,
            registros_por_pagina=registros_por_pagina,
            **filtros,
        )
        contas.extend(atual.get("contas") or [])

    return {
        "completo": total_paginas <= max_paginas,
        "paginas_lidas": alvo,
        "total_paginas": total_paginas,
        "total_registros_declarado": primeira.get("total_registros"),
        "total_itens_coletados": len(contas),
        "contas": contas,
        "fonte": primeira.get("fonte"),
        "regra_valor_pago": primeira.get("regra_valor_pago"),
        "regra_valor_a_pagar": primeira.get("regra_valor_a_pagar"),
    }


async def consultar_situacao_financeira_conta_pagar(codigo_lancamento_omie: int) -> dict[str, Any]:
    response = await client.call(
        "financas/mf",
        "ListarMovimentos",
        {
            "nPagina": 1,
            "nRegPorPagina": 100,
            "nCodTitulo": codigo_lancamento_omie,
            "cNatureza": "P",
            "cTpLancamento": "CP",
            "lDadosCad": True,
        },
    )
    movimentos = response.get("movimentos") or []
    if not movimentos:
        return {
            "encontrado": False,
            "codigo_lancamento_omie": codigo_lancamento_omie,
            "mensagem": "Nenhum movimento financeiro de Contas a Pagar encontrado para o título.",
        }

    normalizados = [normalizar_movimento_conta_pagar(item) for item in movimentos]
    return {
        "encontrado": True,
        "codigo_lancamento_omie": codigo_lancamento_omie,
        "movimentos_encontrados": len(normalizados),
        "conta": normalizados[0],
        "movimentos": normalizados,
    }
