from __future__ import annotations

from typing import Any

from .app import mcp
from .relatorios_completos import contas_pagar_relatorio_completo, contas_receber_relatorio_completo


@mcp.tool()
async def omie_contas_pagar_relatorio_completo(
    registros_por_pagina: int = 100,
    max_paginas: int = 100,
    status: str | None = None,
    codigo_fornecedor: int | None = None,
) -> dict[str, Any]:
    """Contas a Pagar completas com fornecedor e cadastros auxiliares resolvidos."""
    return await contas_pagar_relatorio_completo(
        registros_por_pagina=registros_por_pagina,
        max_paginas=max_paginas,
        status=status,
        codigo_fornecedor=codigo_fornecedor,
    )


@mcp.tool()
async def omie_contas_receber_relatorio_completo(
    registros_por_pagina: int = 100,
    max_paginas: int = 100,
    status: str | None = None,
    codigo_cliente: int | None = None,
) -> dict[str, Any]:
    """Contas a Receber completas com cliente e cadastros auxiliares resolvidos."""
    return await contas_receber_relatorio_completo(
        registros_por_pagina=registros_por_pagina,
        max_paginas=max_paginas,
        status=status,
        codigo_cliente=codigo_cliente,
    )


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
