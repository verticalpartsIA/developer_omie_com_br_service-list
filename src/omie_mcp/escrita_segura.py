from __future__ import annotations

from typing import Any

from .client import OmieWriteBlocked, client


def _confirmar(confirmar: bool, motivo: str) -> None:
    if not confirmar:
        raise OmieWriteBlocked("Operação de escrita exige confirmar=True no tool semântico.")
    if not motivo or len(motivo.strip()) < 5:
        raise OmieWriteBlocked("Informe um motivo auditável com pelo menos 5 caracteres.")


async def upsert_cliente_seguro(*, cadastro: dict[str, Any], confirmar: bool, motivo: str) -> dict[str, Any]:
    _confirmar(confirmar, motivo)
    if not any(cadastro.get(k) for k in ("codigo_cliente_omie", "codigo_cliente_integracao", "cnpj_cpf")):
        raise ValueError("UpsertCliente exige codigo_cliente_omie, codigo_cliente_integracao ou cnpj_cpf.")
    resposta = await client.call("geral/clientes", "UpsertCliente", cadastro, confirm_write=True)
    return {"operacao": "UpsertCliente", "motivo": motivo.strip(), "resposta": resposta}


async def upsert_conta_pagar_seguro(*, conta: dict[str, Any], confirmar: bool, motivo: str) -> dict[str, Any]:
    _confirmar(confirmar, motivo)
    obrigatorios = ("codigo_lancamento_integracao", "codigo_cliente_fornecedor", "data_vencimento", "valor_documento", "codigo_categoria", "id_conta_corrente")
    faltando = [campo for campo in obrigatorios if conta.get(campo) in (None, "")]
    if faltando:
        raise ValueError(f"Campos obrigatórios ausentes para Conta a Pagar: {', '.join(faltando)}")
    resposta = await client.call("financas/contapagar", "UpsertContaPagar", conta, confirm_write=True)
    return {"operacao": "UpsertContaPagar", "motivo": motivo.strip(), "resposta": resposta}


async def upsert_conta_receber_seguro(*, conta: dict[str, Any], confirmar: bool, motivo: str) -> dict[str, Any]:
    _confirmar(confirmar, motivo)
    obrigatorios = ("codigo_lancamento_integracao", "codigo_cliente_fornecedor", "data_vencimento", "valor_documento", "codigo_categoria", "id_conta_corrente")
    faltando = [campo for campo in obrigatorios if conta.get(campo) in (None, "")]
    if faltando:
        raise ValueError(f"Campos obrigatórios ausentes para Conta a Receber: {', '.join(faltando)}")
    resposta = await client.call("financas/contareceber", "UpsertContaReceber", conta, confirm_write=True)
    return {"operacao": "UpsertContaReceber", "motivo": motivo.strip(), "resposta": resposta}


async def lancar_pagamento_seguro(
    *,
    codigo_lancamento: int,
    codigo_conta_corrente: int | str,
    valor: float,
    data: str,
    confirmar: bool,
    motivo: str,
    desconto: float = 0,
    juros: float = 0,
    multa: float = 0,
    observacao: str = "",
    codigo_baixa_integracao: str = "",
) -> dict[str, Any]:
    _confirmar(confirmar, motivo)
    if codigo_lancamento <= 0 or valor <= 0:
        raise ValueError("codigo_lancamento e valor devem ser maiores que zero.")
    payload = {
        "codigo_lancamento": codigo_lancamento,
        "codigo_baixa_integracao": codigo_baixa_integracao,
        "codigo_conta_corrente": codigo_conta_corrente,
        "valor": valor,
        "desconto": desconto,
        "juros": juros,
        "multa": multa,
        "data": data,
        "observacao": observacao or motivo.strip(),
    }
    resposta = await client.call("financas/contapagar", "LancarPagamento", payload, confirm_write=True)
    return {"operacao": "LancarPagamento", "motivo": motivo.strip(), "resposta": resposta}


async def lancar_recebimento_seguro(
    *,
    codigo_lancamento: int,
    codigo_conta_corrente: int,
    valor: float,
    data: str,
    confirmar: bool,
    motivo: str,
    observacao: str = "",
) -> dict[str, Any]:
    _confirmar(confirmar, motivo)
    if codigo_lancamento <= 0 or codigo_conta_corrente <= 0 or valor <= 0:
        raise ValueError("codigo_lancamento, codigo_conta_corrente e valor devem ser maiores que zero.")
    payload = {
        "codigo_lancamento": codigo_lancamento,
        "codigo_conta_corrente": codigo_conta_corrente,
        "valor": valor,
        "data": data,
        "observacao": observacao or motivo.strip(),
    }
    resposta = await client.call("financas/contareceber", "LancarRecebimento", payload, confirm_write=True)
    return {"operacao": "LancarRecebimento", "motivo": motivo.strip(), "resposta": resposta}
