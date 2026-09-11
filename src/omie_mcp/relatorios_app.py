from __future__ import annotations

from typing import Any

from .app import mcp
from .categorias import consultar_categoria_semantica, listar_categorias_semanticas
from .produtos_estoque import produto_360
from .relatorios_completos import contas_pagar_relatorio_completo, contas_receber_relatorio_completo


@mcp.tool()
async def omie_categorias_listar(
    pagina: int = 1,
    registros_por_pagina: int = 100,
    apenas_ativas: bool = False,
    tipo: str | None = None,
    descricao: str | None = None,
) -> dict[str, Any]:
    """Lista categorias do Omie com situação, tipo, hierarquia e vínculo com a Conta do DRE.

    `tipo` aceita R (Receita) ou D (Despesa). Quando `apenas_ativas=true`, usa o filtro oficial do Omie.
    """
    return await listar_categorias_semanticas(
        pagina=pagina,
        registros_por_pagina=registros_por_pagina,
        apenas_ativas=apenas_ativas,
        tipo=tipo,
        descricao=descricao,
    )


@mcp.tool()
async def omie_categoria_consultar(codigo: str) -> dict[str, Any]:
    """Consulta uma categoria específica e devolve seus dados gerenciais, inclusive DRE quando disponível."""
    return await consultar_categoria_semantica(codigo)


@mcp.tool()
async def omie_produto_360(
    codigo_produto: int | None = None,
    codigo_produto_integracao: str | None = None,
    codigo: str | None = None,
    codigo_local_estoque: int = 0,
    data_estoque: str | None = None,
) -> dict[str, Any]:
    """Produto 360: cadastro, fiscal, logística e estoque em uma única visão gerencial."""
    return await produto_360(
        codigo_produto=codigo_produto,
        codigo_produto_integracao=codigo_produto_integracao,
        codigo=codigo,
        codigo_local_estoque=codigo_local_estoque,
        data_estoque=data_estoque,
    )


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
