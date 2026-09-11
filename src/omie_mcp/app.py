from __future__ import annotations

from typing import Any

from .server import mcp
from .transacoes import ciclo_recebimento_compra_financeiro, ciclo_venda_financeiro
from .visoes360 import cliente_360, fornecedor_360


@mcp.tool()
async def omie_cliente_360(
    codigo_cliente_omie: int,
    pagina_financeiro: int = 1,
    registros_financeiro: int = 100,
    pagina_pedidos: int = 1,
    registros_pedidos: int = 50,
) -> dict[str, Any]:
    """Visão 360 de cliente: cadastro, pedidos de venda e Contas a Receber."""
    return await cliente_360(
        codigo_cliente_omie,
        pagina_financeiro=pagina_financeiro,
        registros_financeiro=registros_financeiro,
        pagina_pedidos=pagina_pedidos,
        registros_pedidos=registros_pedidos,
    )


@mcp.tool()
async def omie_fornecedor_360(
    codigo_fornecedor_omie: int,
    pagina_financeiro: int = 1,
    registros_financeiro: int = 100,
) -> dict[str, Any]:
    """Visão 360 de fornecedor: cadastro e exposição financeira em Contas a Pagar."""
    return await fornecedor_360(
        codigo_fornecedor_omie,
        pagina_financeiro=pagina_financeiro,
        registros_financeiro=registros_financeiro,
    )


@mcp.tool()
async def omie_ciclo_venda_financeiro(codigo_pedido: int) -> dict[str, Any]:
    """Liga Pedido de Venda, NF-e e Contas a Receber usando nCodOS como chave oficial."""
    return await ciclo_venda_financeiro(codigo_pedido)


@mcp.tool()
async def omie_ciclo_recebimento_compra_financeiro(
    id_recebimento: int | None = None,
    chave_nfe: str | None = None,
) -> dict[str, Any]:
    """Liga Recebimento de NF-e e Contas a Pagar pela chave fiscal do fornecedor."""
    return await ciclo_recebimento_compra_financeiro(id_recebimento=id_recebimento, chave_nfe=chave_nfe)


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
