from __future__ import annotations

from typing import Any

from .server import mcp
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


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
