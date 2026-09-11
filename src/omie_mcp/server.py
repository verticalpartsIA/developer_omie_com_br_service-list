from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP

from .cadastros import consultar_cliente_fornecedor, listar_clientes_fornecedores_completo, normalizar_cliente_fornecedor
from .catalog import fetch_service_catalog, inspect_service, serialize_catalog
from .client import client
from .compras import (
    consultar_nota_entrada,
    consultar_pedido_compra,
    consultar_recebimento_nfe,
    consultar_requisicao_compra,
    listar_notas_entrada,
    listar_produtos_fornecedor,
    listar_recebimentos_nfe,
    pesquisar_pedidos_compra,
    pesquisar_requisicoes_compra,
    produto_ciclo_compra,
)
from .financeiro import consultar_situacao_financeira_conta_pagar, listar_contas_pagar_financeiro
from .produtos_estoque import (
    consultar_produto,
    listar_movimentos_estoque,
    listar_posicao_estoque,
    listar_produtos_completo,
    posicao_estoque,
)
from .receber import consultar_situacao_conta_receber, listar_contas_receber_financeiro
from .vendas import (
    consultar_nfe,
    consultar_pedido_venda,
    listar_nfe,
    listar_pedidos_venda,
    pedido_venda_ciclo,
    pedidos_prontos_faturar,
    status_pedido_venda,
    validar_pedido_faturamento,
)
from .watcher import diff_official_docs


mcp = FastMCP(
    "VerticalParts Omie MCP",
    instructions=(
        "MCP vivo para o ERP Omie. Prefira ferramentas semânticas quando existirem; use descoberta antes de operações "
        "desconhecidas e omie_chamar_api como fallback universal. Leituras são permitidas; escritas exigem "
        "OMIE_ALLOW_WRITES=true e confirm_write=true. Use omie_documentacao_diff para detectar mudanças oficiais."
    ),
)


# Descoberta e fallback universal
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
    """Fallback universal para qualquer endpoint/call oficial do Omie."""
    return await client.call(endpoint, call, param, confirm_write=confirm_write)


@mcp.tool()
async def omie_documentacao_diff(persistir_snapshot: bool = True) -> dict[str, Any]:
    """Compara a documentação oficial atual com o snapshot anterior."""
    return await diff_official_docs(persist_new_snapshot=persistir_snapshot)


# Clientes / fornecedores
@mcp.tool()
async def omie_clientes_listar(
    pagina: int = 1,
    registros_por_pagina: int = 50,
    apenas_importado_api: str = "N",
) -> dict[str, Any]:
    return await client.call(
        "geral/clientes",
        "ListarClientes",
        {"pagina": pagina, "registros_por_pagina": registros_por_pagina, "apenas_importado_api": apenas_importado_api},
    )


@mcp.tool()
async def omie_clientes_fornecedores_listar_completo(
    pagina: int = 1,
    registros_por_pagina: int = 50,
    apenas_importado_api: str = "N",
    exibir_caracteristicas: str = "S",
    exibir_obs: str = "S",
) -> dict[str, Any]:
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
    bruto = await consultar_cliente_fornecedor(
        codigo_cliente_omie=codigo_cliente_omie,
        codigo_cliente_integracao=codigo_cliente_integracao,
    )
    return {"bruto": bruto, "visao_normalizada": normalizar_cliente_fornecedor(bruto)}


# Produtos / estoque
@mcp.tool()
async def omie_produtos_listar(pagina: int = 1, registros_por_pagina: int = 50) -> dict[str, Any]:
    return await listar_produtos_completo(pagina=pagina, registros_por_pagina=registros_por_pagina)


@mcp.tool()
async def omie_produto_consultar(
    codigo_produto: int | None = None,
    codigo_produto_integracao: str | None = None,
    codigo: str | None = None,
) -> dict[str, Any]:
    return await consultar_produto(
        codigo_produto=codigo_produto,
        codigo_produto_integracao=codigo_produto_integracao,
        codigo=codigo,
    )


@mcp.tool()
async def omie_estoque_posicao(
    codigo_produto: int,
    codigo_local_estoque: int = 0,
    data: str | None = None,
) -> dict[str, Any]:
    return await posicao_estoque(codigo_produto=codigo_produto, codigo_local_estoque=codigo_local_estoque, data=data)


@mcp.tool()
async def omie_estoque_listar_posicao(
    pagina: int = 1,
    registros_por_pagina: int = 50,
    data_posicao: str | None = None,
    exibir_todos: str = "N",
    codigo_local_estoque: int = 0,
) -> dict[str, Any]:
    return await listar_posicao_estoque(
        pagina=pagina,
        registros_por_pagina=registros_por_pagina,
        data_posicao=data_posicao,
        exibir_todos=exibir_todos,
        codigo_local_estoque=codigo_local_estoque,
    )


@mcp.tool()
async def omie_estoque_movimentos(
    pagina: int = 1,
    registros_por_pagina: int = 50,
    codigo_produto: int = 0,
    codigo_local_estoque: int = 0,
    data_inicial: str | None = None,
    data_final: str | None = None,
) -> dict[str, Any]:
    return await listar_movimentos_estoque(
        pagina=pagina,
        registros_por_pagina=registros_por_pagina,
        codigo_produto=codigo_produto,
        codigo_local_estoque=codigo_local_estoque,
        data_inicial=data_inicial,
        data_final=data_final,
    )


# Financeiro
@mcp.tool()
async def omie_contas_pagar_listar(pagina: int = 1, registros_por_pagina: int = 50) -> dict[str, Any]:
    return await client.call("financas/contapagar", "ListarContasPagar", {"pagina": pagina, "registros_por_pagina": registros_por_pagina})


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
    return await consultar_situacao_financeira_conta_pagar(codigo_lancamento_omie)


@mcp.tool()
async def omie_contas_receber_listar(pagina: int = 1, registros_por_pagina: int = 50) -> dict[str, Any]:
    return await client.call("financas/contareceber", "ListarContasReceber", {"pagina": pagina, "registros_por_pagina": registros_por_pagina})


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
    return await consultar_situacao_conta_receber(codigo_lancamento_omie)


# Compras
@mcp.tool()
async def omie_produtos_fornecedor_listar(
    pagina: int = 1,
    registros_por_pagina: int = 10,
    apenas_importado_api: str = "N",
) -> dict[str, Any]:
    """Lista a relação oficial Produto x Fornecedor."""
    return await listar_produtos_fornecedor(
        pagina=pagina,
        registros_por_pagina=registros_por_pagina,
        apenas_importado_api=apenas_importado_api,
    )


@mcp.tool()
async def omie_requisicoes_compra_pesquisar(
    pagina: int = 1,
    registros_por_pagina: int = 50,
    data_de: str | None = None,
    data_ate: str | None = None,
) -> dict[str, Any]:
    return await pesquisar_requisicoes_compra(
        pagina=pagina,
        registros_por_pagina=registros_por_pagina,
        data_de=data_de,
        data_ate=data_ate,
    )


@mcp.tool()
async def omie_requisicao_compra_consultar(
    codigo_requisicao: int | None = None,
    codigo_integracao: str | None = None,
) -> dict[str, Any]:
    return await consultar_requisicao_compra(codigo_requisicao=codigo_requisicao, codigo_integracao=codigo_integracao)


@mcp.tool()
async def omie_pedidos_compra_pesquisar(
    pagina: int = 1,
    registros_por_pagina: int = 50,
    pendentes: bool = True,
    faturados: bool = True,
    recebidos: bool = True,
    cancelados: bool = False,
    encerrados: bool = True,
    recebidos_parcialmente: bool = True,
    faturados_parcialmente: bool = True,
    data_inicial: str | None = None,
    data_final: str | None = None,
) -> dict[str, Any]:
    return await pesquisar_pedidos_compra(
        pagina=pagina,
        registros_por_pagina=registros_por_pagina,
        pendentes=pendentes,
        faturados=faturados,
        recebidos=recebidos,
        cancelados=cancelados,
        encerrados=encerrados,
        recebidos_parcialmente=recebidos_parcialmente,
        faturados_parcialmente=faturados_parcialmente,
        data_inicial=data_inicial,
        data_final=data_final,
    )


@mcp.tool()
async def omie_pedido_compra_consultar(
    codigo_pedido: int | None = None,
    codigo_integracao: str | None = None,
    numero: str | None = None,
) -> dict[str, Any]:
    return await consultar_pedido_compra(codigo_pedido=codigo_pedido, codigo_integracao=codigo_integracao, numero=numero)


@mcp.tool()
async def omie_notas_entrada_listar(pagina: int = 1, registros_por_pagina: int = 50) -> dict[str, Any]:
    return await listar_notas_entrada(pagina=pagina, registros_por_pagina=registros_por_pagina)


@mcp.tool()
async def omie_nota_entrada_consultar(
    codigo_nota_entrada: int | None = None,
    codigo_integracao: str | None = None,
) -> dict[str, Any]:
    return await consultar_nota_entrada(codigo_nota_entrada=codigo_nota_entrada, codigo_integracao=codigo_integracao)


@mcp.tool()
async def omie_recebimentos_nfe_listar(pagina: int = 1, registros_por_pagina: int = 50) -> dict[str, Any]:
    return await listar_recebimentos_nfe(pagina=pagina, registros_por_pagina=registros_por_pagina)


@mcp.tool()
async def omie_recebimento_nfe_consultar(
    id_recebimento: int | None = None,
    chave_nfe: str | None = None,
) -> dict[str, Any]:
    return await consultar_recebimento_nfe(id_recebimento=id_recebimento, chave_nfe=chave_nfe)


@mcp.tool()
async def omie_produto_ciclo_compra(codigo_produto: int, pagina: int = 1, registros_por_pagina: int = 50) -> dict[str, Any]:
    return await produto_ciclo_compra(codigo_produto=codigo_produto, pagina=pagina, registros_por_pagina=registros_por_pagina)


# Vendas / faturamento / NF-e
@mcp.tool()
async def omie_pedidos_venda_listar(
    pagina: int = 1,
    registros_por_pagina: int = 100,
    apenas_importado_api: str = "N",
) -> dict[str, Any]:
    return await listar_pedidos_venda(
        pagina=pagina,
        registros_por_pagina=registros_por_pagina,
        apenas_importado_api=apenas_importado_api,
    )


@mcp.tool()
async def omie_pedido_venda_consultar(
    codigo_pedido: int | None = None,
    codigo_integracao: str | None = None,
) -> dict[str, Any]:
    return await consultar_pedido_venda(codigo_pedido=codigo_pedido, codigo_integracao=codigo_integracao)


@mcp.tool()
async def omie_pedido_venda_status(
    codigo_pedido: int | None = None,
    codigo_integracao: str | None = None,
) -> dict[str, Any]:
    return await status_pedido_venda(codigo_pedido=codigo_pedido, codigo_integracao=codigo_integracao)


@mcp.tool()
async def omie_pedidos_prontos_faturar(etapa: str = "50") -> dict[str, Any]:
    return await pedidos_prontos_faturar(etapa=etapa)


@mcp.tool()
async def omie_pedido_validar_faturamento(
    codigo_pedido: int | None = None,
    codigo_integracao: str | None = None,
) -> dict[str, Any]:
    """Valida um pedido para faturamento sem faturá-lo."""
    return await validar_pedido_faturamento(codigo_pedido=codigo_pedido, codigo_integracao=codigo_integracao)


@mcp.tool()
async def omie_nfe_listar(
    pagina: int = 1,
    registros_por_pagina: int = 20,
    ordenar_por: str = "CODIGO",
) -> dict[str, Any]:
    return await listar_nfe(pagina=pagina, registros_por_pagina=registros_por_pagina, ordenar_por=ordenar_por)


@mcp.tool()
async def omie_nfe_consultar(codigo_nfe: int | None = None, numero_nfe: str | None = None) -> dict[str, Any]:
    return await consultar_nfe(codigo_nfe=codigo_nfe, numero_nfe=numero_nfe)


@mcp.tool()
async def omie_pedido_venda_ciclo(codigo_pedido: int) -> dict[str, Any]:
    return await pedido_venda_ciclo(codigo_pedido=codigo_pedido)


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
