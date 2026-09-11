from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP

from .cadastros import (
    consultar_cliente_fornecedor,
    listar_clientes_fornecedores_completo,
    normalizar_cliente_fornecedor,
)
from .catalog import fetch_service_catalog, inspect_service, serialize_catalog
from .client import client
from .financeiro import (
    consultar_situacao_financeira_conta_pagar,
    listar_contas_pagar_financeiro,
)
from .receber import (
    consultar_situacao_conta_receber,
    listar_contas_receber_financeiro,
)
from .watcher import diff_official_docs


mcp = FastMCP(
    "VerticalParts Omie MCP",
    instructions=(
        "MCP para acesso amplo ao ERP Omie. Prefira ferramentas de descoberta antes de chamar operações desconhecidas. "
        "Leituras são permitidas; escritas exigem OMIE_ALLOW_WRITES=true e confirm_write=true. "
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
async def omie_clientes_fornecedores_listar_completo(
    pagina: int = 1,
    registros_por_pagina: int = 50,
    apenas_importado_api: str = "N",
    exibir_caracteristicas: str = "S",
    exibir_obs: str = "S",
) -> dict[str, Any]:
    """Lista o cadastro completo de clientes/fornecedores/transportadoras.

    Solicita características e observações para aproximar a visão do relatório exportado pelo Omie.
    """
    return await listar_clientes_fornecedores_completo(
        pagina=pagina,
        registros_por_pagina=registros_por_pagina,
        apenas_importado_api=apenas_importado_api,
        exibir_caracteristicas=exibir_caracteristicas,
        exibir_obs=exibir_obs,
    )


@mcp.tool()
async def omie_cliente_fornecedor_consultar(
    codigo_cliente_omie: int | None = None,
    codigo_cliente_integracao: str | None = None,
) -> dict[str, Any]:
    """Consulta um cliente/fornecedor e retorna também uma visão normalizada para uso pelo Claude."""
    bruto = await consultar_cliente_fornecedor(
        codigo_cliente_omie=codigo_cliente_omie,
        codigo_cliente_integracao=codigo_cliente_integracao,
    )
    return {"bruto": bruto, "visao_normalizada": normalizar_cliente_fornecedor(bruto)}


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
    """Lista contas a pagar pelo endpoint cadastral de títulos."""
    return await client.call(
        "financas/contapagar",
        "ListarContasPagar",
        {"pagina": pagina, "registros_por_pagina": registros_por_pagina},
    )


@mcp.tool()
async def omie_contas_pagar_financeiro(
    pagina: int = 1,
    registros_por_pagina: int = 50,
    status: str | None = None,
    codigo_fornecedor: int | None = None,
    cpf_cnpj: str | None = None,
    codigo_projeto: int | None = None,
    vencimento_de: str | None = None,
    vencimento_ate: str | None = None,
) -> dict[str, Any]:
    """Lista contas a pagar com valor pago e saldo em aberto vindos de Movimentos Financeiros."""
    return await listar_contas_pagar_financeiro(
        pagina=pagina,
        registros_por_pagina=registros_por_pagina,
        status=status,
        codigo_fornecedor=codigo_fornecedor,
        cpf_cnpj=cpf_cnpj,
        codigo_projeto=codigo_projeto,
        vencimento_de=vencimento_de,
        vencimento_ate=vencimento_ate,
    )


@mcp.tool()
async def omie_conta_pagar_situacao_financeira(codigo_lancamento_omie: int) -> dict[str, Any]:
    """Consulta um título a pagar e retorna valor pago, valor em aberto e demais componentes financeiros."""
    return await consultar_situacao_financeira_conta_pagar(codigo_lancamento_omie)


@mcp.tool()
async def omie_contas_receber_listar(
    pagina: int = 1,
    registros_por_pagina: int = 50,
) -> dict[str, Any]:
    """Lista contas a receber pelo endpoint cadastral de títulos."""
    return await client.call(
        "financas/contareceber",
        "ListarContasReceber",
        {"pagina": pagina, "registros_por_pagina": registros_por_pagina},
    )


@mcp.tool()
async def omie_contas_receber_financeiro(
    pagina: int = 1,
    registros_por_pagina: int = 50,
    status: str | None = None,
    codigo_cliente: int | None = None,
    cpf_cnpj: str | None = None,
    codigo_projeto: int | None = None,
    vencimento_de: str | None = None,
    vencimento_ate: str | None = None,
) -> dict[str, Any]:
    """Lista contas a receber com valor recebido e saldo em aberto vindos de Movimentos Financeiros."""
    return await listar_contas_receber_financeiro(
        pagina=pagina,
        registros_por_pagina=registros_por_pagina,
        status=status,
        codigo_cliente=codigo_cliente,
        cpf_cnpj=cpf_cnpj,
        codigo_projeto=codigo_projeto,
        vencimento_de=vencimento_de,
        vencimento_ate=vencimento_ate,
    )


@mcp.tool()
async def omie_conta_receber_situacao_financeira(codigo_lancamento_omie: int) -> dict[str, Any]:
    """Consulta um título a receber e retorna valor recebido, valor em aberto e componentes financeiros."""
    return await consultar_situacao_conta_receber(codigo_lancamento_omie)


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
