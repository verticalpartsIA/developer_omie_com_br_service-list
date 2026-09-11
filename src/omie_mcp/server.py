from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP

from .catalog import fetch_service_catalog, inspect_service, serialize_catalog
from .client import client
from .financeiro import (
    consultar_situacao_financeira_conta_pagar,
    listar_contas_pagar_financeiro,
)
from .watcher import diff_official_docs


mcp = FastMCP(
    "VerticalParts Omie MCP",
    instructions=(
        "MCP para acesso amplo ao ERP Omie. Prefira ferramentas de descoberta antes de chamar operações desconhecidas. "
        "Leituras são permitidas; escritas exigem OMIE_ALLOW_WRITES=true e confirm_write=true. "
        "Para perguntas sobre Valor Pago e Valor a Pagar em Contas a Pagar, prefira as ferramentas financeiras baseadas em /financas/mf/, "
        "pois o Omie expõe nValPago e nValAberto no resumo dos Movimentos Financeiros. "
        "Use omie_documentacao_diff para verificar mudanças recentes na documentação oficial."
    ),
)


@mcp.tool()
async def omie_catalogo_servicos() -> list[dict[str, Any]]:
    """Descobre ao vivo os serviços publicados na lista oficial da API Omie."""
    return serialize_catalog(await fetch_service_catalog())


@mcp.tool()
async def omie_inspecionar_servico(endpoint: str) -> dict[str, Any]:
    """Inspeciona um endpoint oficial e tenta detectar operações/calls documentadas."""
    return await inspect_service(endpoint)


@mcp.tool()
async def omie_chamar_api(
    endpoint: str,
    call: str,
    param: list[dict[str, Any]] | dict[str, Any] | None = None,
    confirm_write: bool = False,
) -> dict[str, Any]:
    """Fallback universal da API Omie.

    Use quando ainda não existir uma ferramenta específica. `endpoint` pode ser relativo
    (ex.: `geral/clientes`) ou a URL oficial completa. `call` deve ser exatamente a operação
    esperada pelo Omie. Operações potencialmente mutáveis ficam bloqueadas por padrão.
    """
    return await client.call(endpoint, call, param, confirm_write=confirm_write)


@mcp.tool()
async def omie_documentacao_diff(persistir_snapshot: bool = True) -> dict[str, Any]:
    """Compara a documentação oficial atual com o snapshot anterior.

    Detecta mudança textual, serviço novo, serviço removido e alteração de metadados do catálogo.
    Na primeira execução cria a linha de base. Por padrão o snapshot atual vira a nova referência.
    """
    return await diff_official_docs(persist_new_snapshot=persistir_snapshot)


# Atalhos tipados de alto uso. A cobertura integral continua garantida por omie_chamar_api.
@mcp.tool()
async def omie_clientes_listar(
    pagina: int = 1,
    registros_por_pagina: int = 50,
    apenas_importado_api: str = "N",
) -> dict[str, Any]:
    """Lista clientes/fornecedores/transportadoras pelo cadastro geral do Omie."""
    return await client.call(
        "geral/clientes",
        "ListarClientes",
        {
            "pagina": pagina,
            "registros_por_pagina": registros_por_pagina,
            "apenas_importado_api": apenas_importado_api,
        },
    )


@mcp.tool()
async def omie_produtos_listar(
    pagina: int = 1,
    registros_por_pagina: int = 50,
) -> dict[str, Any]:
    """Lista produtos cadastrados no Omie."""
    return await client.call(
        "geral/produtos",
        "ListarProdutos",
        {"pagina": pagina, "registros_por_pagina": registros_por_pagina},
    )


@mcp.tool()
async def omie_contas_pagar_listar(
    pagina: int = 1,
    registros_por_pagina: int = 50,
) -> dict[str, Any]:
    """Lista o cadastro bruto de Contas a Pagar.

    Para perguntas sobre valores realizados, principalmente Valor Pago e Valor a Pagar,
    use `omie_contas_pagar_financeiro` ou `omie_conta_pagar_situacao_financeira`.
    """
    return await client.call(
        "financas/contapagar",
        "ListarContasPagar",
        {"pagina": pagina, "registros_por_pagina": registros_por_pagina},
    )


@mcp.tool()
async def omie_contas_pagar_financeiro(
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
    """Lista Contas a Pagar com situação financeira real do Omie.

    É a ferramenta preferencial para responder quanto já foi pago e quanto ainda falta pagar.
    Usa /financas/mf/ ListarMovimentos e expõe diretamente:
    - `valor_pago` <- `resumo.nValPago`
    - `valor_a_pagar` <- `resumo.nValAberto`
    - `valor_liquido` <- `resumo.nValLiquido`
    - desconto, juros, multa, situação e data de pagamento.
    Datas seguem o formato dd/mm/aaaa usado pelo Omie.
    """
    return await listar_contas_pagar_financeiro(
        pagina=pagina,
        registros_por_pagina=registros_por_pagina,
        status=status,
        codigo_fornecedor=codigo_fornecedor,
        cpf_cnpj=cpf_cnpj,
        codigo_projeto=codigo_projeto,
        vencimento_de=vencimento_de,
        vencimento_ate=vencimento_ate,
        pagamento_de=pagamento_de,
        pagamento_ate=pagamento_ate,
    )


@mcp.tool()
async def omie_conta_pagar_situacao_financeira(codigo_lancamento_omie: int) -> dict[str, Any]:
    """Consulta Valor Pago, Valor a Pagar e demais dados financeiros de um título específico."""
    return await consultar_situacao_financeira_conta_pagar(codigo_lancamento_omie)


@mcp.tool()
async def omie_contas_receber_listar(
    pagina: int = 1,
    registros_por_pagina: int = 50,
) -> dict[str, Any]:
    """Lista contas a receber."""
    return await client.call(
        "financas/contareceber",
        "ListarContasReceber",
        {"pagina": pagina, "registros_por_pagina": registros_por_pagina},
    )


@mcp.tool()
async def omie_pedidos_compra_listar(
    pagina: int = 1,
    registros_por_pagina: int = 50,
) -> dict[str, Any]:
    """Lista pedidos de compra."""
    return await client.call(
        "produtos/pedidocompra",
        "ListarPedidosCompra",
        {"pagina": pagina, "registros_por_pagina": registros_por_pagina},
    )


@mcp.tool()
async def omie_pedidos_venda_listar(
    pagina: int = 1,
    registros_por_pagina: int = 50,
) -> dict[str, Any]:
    """Lista pedidos de venda."""
    return await client.call(
        "produtos/pedido",
        "ListarPedidos",
        {"pagina": pagina, "registros_por_pagina": registros_por_pagina},
    )


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
