from __future__ import annotations

from typing import Any

from .app import mcp
from .escrita_segura import (
    lancar_pagamento_seguro,
    lancar_recebimento_seguro,
    upsert_cliente_seguro,
    upsert_conta_pagar_seguro,
    upsert_conta_receber_seguro,
)


@mcp.tool()
async def omie_cliente_upsert_seguro(cadastro: dict[str, Any], confirmar: bool = False, motivo: str = "") -> dict[str, Any]:
    """Cria/atualiza cliente ou fornecedor. Exige writes habilitadas, confirmar=true e motivo auditável."""
    return await upsert_cliente_seguro(cadastro=cadastro, confirmar=confirmar, motivo=motivo)


@mcp.tool()
async def omie_conta_pagar_upsert_seguro(conta: dict[str, Any], confirmar: bool = False, motivo: str = "") -> dict[str, Any]:
    """Cria/atualiza Conta a Pagar com dupla confirmação e validação mínima."""
    return await upsert_conta_pagar_seguro(conta=conta, confirmar=confirmar, motivo=motivo)


@mcp.tool()
async def omie_conta_receber_upsert_seguro(conta: dict[str, Any], confirmar: bool = False, motivo: str = "") -> dict[str, Any]:
    """Cria/atualiza Conta a Receber com dupla confirmação e validação mínima."""
    return await upsert_conta_receber_seguro(conta=conta, confirmar=confirmar, motivo=motivo)


@mcp.tool()
async def omie_pagamento_lancar_seguro(
    codigo_lancamento: int,
    codigo_conta_corrente: int,
    valor: float,
    data: str,
    confirmar: bool = False,
    motivo: str = "",
    desconto: float = 0,
    juros: float = 0,
    multa: float = 0,
    observacao: str = "",
) -> dict[str, Any]:
    """Baixa Conta a Pagar. É mutação financeira e exige confirmação explícita e motivo."""
    return await lancar_pagamento_seguro(
        codigo_lancamento=codigo_lancamento,
        codigo_conta_corrente=codigo_conta_corrente,
        valor=valor,
        data=data,
        confirmar=confirmar,
        motivo=motivo,
        desconto=desconto,
        juros=juros,
        multa=multa,
        observacao=observacao,
    )


@mcp.tool()
async def omie_recebimento_lancar_seguro(
    codigo_lancamento: int,
    codigo_conta_corrente: int,
    valor: float,
    data: str,
    confirmar: bool = False,
    motivo: str = "",
    observacao: str = "",
) -> dict[str, Any]:
    """Baixa Conta a Receber. É mutação financeira e exige confirmação explícita e motivo."""
    return await lancar_recebimento_seguro(
        codigo_lancamento=codigo_lancamento,
        codigo_conta_corrente=codigo_conta_corrente,
        valor=valor,
        data=data,
        confirmar=confirmar,
        motivo=motivo,
        observacao=observacao,
    )


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
