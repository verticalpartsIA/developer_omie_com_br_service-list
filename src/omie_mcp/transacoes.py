from __future__ import annotations

from typing import Any

from .client import client
from .compras import consultar_recebimento_nfe
from .receber import normalizar_movimento_conta_receber
from .financeiro import normalizar_movimento_conta_pagar
from .vendas import consultar_nfe, consultar_pedido_venda, status_pedido_venda


def _somar(contas: list[dict[str, Any]], campo: str) -> float:
    total = 0.0
    for conta in contas:
        valor = conta.get(campo)
        if isinstance(valor, (int, float)):
            total += float(valor)
    return round(total, 2)


def _primeiro_codigo_nfe(movimentos: list[dict[str, Any]]) -> int | None:
    for item in movimentos:
        detalhes = item.get("detalhes") or {}
        codigo = detalhes.get("nCodNF")
        if isinstance(codigo, int) and codigo > 0:
            return codigo
    return None


async def ciclo_venda_financeiro(codigo_pedido: int) -> dict[str, Any]:
    """Liga Pedido de Venda -> NF-e -> Contas a Receber -> recebimentos/saldo.

    O vínculo financeiro usa `ListarMovimentos.nCodOS`, documentado pelo Omie como
    "Código do Pedido de Venda / Ordem de Serviço". Assim o MCP evita heurística por texto.
    """
    pedido = await consultar_pedido_venda(codigo_pedido=codigo_pedido)
    status = await status_pedido_venda(codigo_pedido=codigo_pedido)

    financeiro_bruto = await client.call(
        "financas/mf",
        "ListarMovimentos",
        {
            "nPagina": 1,
            "nRegPorPagina": 500,
            "nCodOS": codigo_pedido,
            "cNatureza": "R",
            "cTpLancamento": "CR",
            "lDadosCad": True,
        },
    )
    movimentos = financeiro_bruto.get("movimentos") or []
    contas = [normalizar_movimento_conta_receber(item) for item in movimentos]

    codigo_nfe = _primeiro_codigo_nfe(movimentos)
    nfe: dict[str, Any] | None = None
    if codigo_nfe:
        try:
            nfe = await consultar_nfe(codigo_nfe=codigo_nfe)
        except Exception as exc:  # a visão financeira continua útil mesmo se a consulta fiscal falhar
            nfe = {"erro_consulta": str(exc), "codigo_nfe": codigo_nfe}

    return {
        "tipo_visao": "CICLO_VENDA_FINANCEIRO",
        "codigo_pedido": codigo_pedido,
        "pedido": pedido,
        "status": status,
        "nfe": nfe,
        "financeiro": {
            "contas_receber": contas,
            "quantidade_titulos": len(contas),
            "valor_original": _somar(contas, "valor_conta"),
            "valor_recebido": _somar(contas, "valor_recebido"),
            "valor_a_receber": _somar(contas, "valor_a_receber"),
            "total_paginas": financeiro_bruto.get("nTotPaginas"),
            "total_registros": financeiro_bruto.get("nTotRegistros"),
        },
        "regra_vinculo": "MovimentosFinanceiros.nCodOS = codigo_pedido",
        "fonte_vinculo": "Omie /financas/mf/ ListarMovimentos",
        "completo": (financeiro_bruto.get("nTotPaginas") or 1) <= 1,
    }


async def ciclo_recebimento_compra_financeiro(
    *,
    id_recebimento: int | None = None,
    chave_nfe: str | None = None,
) -> dict[str, Any]:
    """Liga Recebimento NF-e -> Fornecedor -> Contas a Pagar pela chave fiscal.

    A API financeira não publica filtro de requisição por `cChaveNFe`. O MCP reduz o
    universo pelo fornecedor e cruza localmente a chave NF-e retornada em `detalhes.cChaveNFe`.
    Se houver mais de uma página financeira, a resposta é marcada como incompleta em vez
    de fingir cobertura total.
    """
    recebimento = await consultar_recebimento_nfe(id_recebimento=id_recebimento, chave_nfe=chave_nfe)
    cabec = recebimento.get("cabec") or {}

    chave = str(cabec.get("cChaveNfe") or chave_nfe or "").strip()
    codigo_fornecedor = cabec.get("nIdFornecedor")
    cpf_cnpj = cabec.get("cCNPJ_CPF")
    numero_nfe = str(cabec.get("cNumeroNFe") or "").strip()

    if not chave:
        raise ValueError("O recebimento não retornou cChaveNfe; não é seguro correlacionar o financeiro sem chave fiscal")

    filtros: dict[str, Any] = {
        "nPagina": 1,
        "nRegPorPagina": 500,
        "cNatureza": "P",
        "cTpLancamento": "CP",
        "lDadosCad": True,
    }
    if isinstance(codigo_fornecedor, int) and codigo_fornecedor > 0:
        filtros["nCodCliente"] = codigo_fornecedor
    elif cpf_cnpj:
        filtros["cCPFCNPJCliente"] = cpf_cnpj

    financeiro_bruto = await client.call("financas/mf", "ListarMovimentos", filtros)
    movimentos = financeiro_bruto.get("movimentos") or []

    correspondentes: list[dict[str, Any]] = []
    for item in movimentos:
        detalhes = item.get("detalhes") or {}
        chave_mov = str(detalhes.get("cChaveNFe") or "").strip()
        doc_mov = str(detalhes.get("cNumDocFiscal") or "").strip()
        if chave_mov == chave or (not chave_mov and numero_nfe and doc_mov == numero_nfe):
            correspondentes.append(item)

    contas = [normalizar_movimento_conta_pagar(item) for item in correspondentes]
    total_paginas = financeiro_bruto.get("nTotPaginas") or 1

    return {
        "tipo_visao": "CICLO_RECEBIMENTO_COMPRA_FINANCEIRO",
        "recebimento": recebimento,
        "chave_nfe": chave,
        "codigo_fornecedor": codigo_fornecedor,
        "financeiro": {
            "contas_pagar_correspondentes": contas,
            "quantidade_titulos": len(contas),
            "valor_original": _somar(contas, "valor_conta"),
            "valor_pago": _somar(contas, "valor_pago"),
            "valor_a_pagar": _somar(contas, "valor_a_pagar"),
            "total_paginas_consultadas": 1,
            "total_paginas_disponiveis": total_paginas,
        },
        "regra_vinculo": "Recebimento.cabec.cChaveNfe = MovimentosFinanceiros.detalhes.cChaveNFe",
        "fallback_vinculo": "Se cChaveNFe não vier no movimento, usa cNumeroNFe = cNumDocFiscal dentro do mesmo fornecedor",
        "completo": total_paginas <= 1,
        "observacao": (
            "ListarMovimentos não documenta filtro por chave NF-e. Quando houver mais de uma página para o fornecedor, "
            "esta visão sinaliza completo=false para evitar falso negativo."
        ),
    }
