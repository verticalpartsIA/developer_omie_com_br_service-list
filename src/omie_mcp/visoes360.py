from __future__ import annotations

from typing import Any

from .cadastros import consultar_cliente_fornecedor, normalizar_cliente_fornecedor
from .client import client
from .financeiro import listar_contas_pagar_financeiro
from .receber import listar_contas_receber_financeiro


def _somar(contas: list[dict[str, Any]], campo: str) -> float:
    total = 0.0
    for conta in contas:
        valor = conta.get(campo)
        if isinstance(valor, (int, float)):
            total += float(valor)
    return round(total, 2)


def _resumo_financeiro(contas: list[dict[str, Any]], *, pago: str, aberto: str) -> dict[str, Any]:
    por_status: dict[str, int] = {}
    for conta in contas:
        status = str(conta.get("situacao") or "SEM_STATUS")
        por_status[status] = por_status.get(status, 0) + 1
    return {
        "quantidade_titulos": len(contas),
        "valor_total": _somar(contas, "valor_conta"),
        "valor_realizado": _somar(contas, pago),
        "valor_em_aberto": _somar(contas, aberto),
        "por_status": por_status,
    }


async def cliente_360(
    codigo_cliente_omie: int,
    *,
    pagina_financeiro: int = 1,
    registros_financeiro: int = 100,
    pagina_pedidos: int = 1,
    registros_pedidos: int = 50,
) -> dict[str, Any]:
    """Visão 360 de cliente: cadastro + pedidos de venda + Contas a Receber.

    O vínculo é feito pelas chaves oficiais do Omie. A listagem de pedidos usa
    `filtrar_por_cliente`, documentado em `pvpListarRequest`.
    """
    cadastro_bruto = await consultar_cliente_fornecedor(codigo_cliente_omie=codigo_cliente_omie)
    cadastro = normalizar_cliente_fornecedor(cadastro_bruto)

    financeiro = await listar_contas_receber_financeiro(
        pagina=pagina_financeiro,
        registros_por_pagina=registros_financeiro,
        codigo_cliente=codigo_cliente_omie,
    )
    contas = financeiro.get("contas") or []

    pedidos = await client.call(
        "produtos/pedido",
        "ListarPedidos",
        {
            "pagina": pagina_pedidos,
            "registros_por_pagina": registros_pedidos,
            "apenas_importado_api": "N",
            "filtrar_por_cliente": codigo_cliente_omie,
            "apenas_resumo": "N",
        },
    )

    return {
        "tipo_visao": "CLIENTE_360",
        "codigo_cliente_omie": codigo_cliente_omie,
        "cadastro": cadastro,
        "financeiro": {
            "resumo": _resumo_financeiro(contas, pago="valor_recebido", aberto="valor_a_receber"),
            "contas_receber": contas,
            "fonte": financeiro.get("fonte"),
        },
        "vendas": {
            "pedidos": pedidos,
            "regra_vinculo": "ListarPedidos.filtrar_por_cliente = codigo_cliente_omie",
        },
        "chaves_de_correlacao": [
            "codigo_cliente_omie / detalhes.nCodCliente",
            "pedido.cabecalho.codigo_cliente",
            "movimento.detalhes.nCodOS / cNumOS para pedido/OS quando presente",
            "movimento.detalhes.nCodCtr / cNumCtr para contrato quando presente",
        ],
    }


async def fornecedor_360(
    codigo_fornecedor_omie: int,
    *,
    pagina_financeiro: int = 1,
    registros_financeiro: int = 100,
) -> dict[str, Any]:
    """Visão 360 de fornecedor: cadastro + exposição em Contas a Pagar.

    Pedidos de compra não são varridos indiscriminadamente aqui porque o método
    `PesquisarPedCompra` não publica filtro por fornecedor. O MCP não deve fingir
    uma correlação que a API não oferece de forma seletiva.
    """
    cadastro_bruto = await consultar_cliente_fornecedor(codigo_cliente_omie=codigo_fornecedor_omie)
    cadastro = normalizar_cliente_fornecedor(cadastro_bruto)

    financeiro = await listar_contas_pagar_financeiro(
        pagina=pagina_financeiro,
        registros_por_pagina=registros_financeiro,
        codigo_fornecedor=codigo_fornecedor_omie,
    )
    contas = financeiro.get("contas") or []

    return {
        "tipo_visao": "FORNECEDOR_360",
        "codigo_fornecedor_omie": codigo_fornecedor_omie,
        "cadastro": cadastro,
        "financeiro": {
            "resumo": _resumo_financeiro(contas, pago="valor_pago", aberto="valor_a_pagar"),
            "contas_pagar": contas,
            "fonte": financeiro.get("fonte"),
        },
        "compras": {
            "correlacao_disponivel": [
                "pedido_compra.cabecalho_consulta.nCodFor",
                "produto_fornecedor.cadastros[].nCodForn",
                "recebimento_nfe fornecedor/chave/documento",
            ],
            "observacao": (
                "A pesquisa oficial de pedidos de compra não documenta filtro por fornecedor. "
                "Para manter fidelidade, esta visão não pagina todos os pedidos só para filtrar localmente."
            ),
        },
        "chaves_de_correlacao": [
            "codigo_cliente_omie / detalhes.nCodCliente",
            "pedido_compra.cabecalho_consulta.nCodFor",
            "produto_fornecedor.cadastros[].nCodForn",
        ],
    }
