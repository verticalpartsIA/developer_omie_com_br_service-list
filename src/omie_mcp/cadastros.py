from __future__ import annotations

from typing import Any

from .client import client


async def listar_clientes_fornecedores_completo(
    pagina: int = 1,
    registros_por_pagina: int = 50,
    apenas_importado_api: str = "N",
    exibir_caracteristicas: str = "S",
    exibir_obs: str = "S",
) -> dict[str, Any]:
    """Lista o cadastro completo de clientes/fornecedores/transportadoras.

    Esta função prioriza fidelidade ao relatório do Omie e, por isso, solicita
    características e observações quando disponíveis.
    """
    return await client.call(
        "geral/clientes",
        "ListarClientes",
        {
            "pagina": pagina,
            "registros_por_pagina": registros_por_pagina,
            "apenas_importado_api": apenas_importado_api,
            "exibir_caracteristicas": exibir_caracteristicas,
            "exibir_obs": exibir_obs,
        },
    )


async def consultar_cliente_fornecedor(
    codigo_cliente_omie: int | None = None,
    codigo_cliente_integracao: str | None = None,
) -> dict[str, Any]:
    """Consulta um cadastro individual completo no Omie."""
    if not codigo_cliente_omie and not codigo_cliente_integracao:
        raise ValueError("Informe codigo_cliente_omie ou codigo_cliente_integracao")

    payload: dict[str, Any] = {}
    if codigo_cliente_omie:
        payload["codigo_cliente_omie"] = codigo_cliente_omie
    if codigo_cliente_integracao:
        payload["codigo_cliente_integracao"] = codigo_cliente_integracao

    return await client.call("geral/clientes", "ConsultarCliente", payload)


def normalizar_cliente_fornecedor(cadastro: dict[str, Any]) -> dict[str, Any]:
    """Produz uma visão amigável sem inventar campos derivados.

    Total a receber, crédito disponível, integração automática e monitoramento
    não são inferidos aqui, porque exigem fonte adicional ou validação semântica.
    """
    dados_bancarios = cadastro.get("dadosBancarios") or {}
    recomendacoes = cadastro.get("recomendacoes") or {}
    info = cadastro.get("info") or {}

    tags = cadastro.get("tags") or []
    caracteristicas = cadastro.get("caracteristicas") or []

    return {
        "codigo_cliente_omie": cadastro.get("codigo_cliente_omie"),
        "codigo_cliente_integracao": cadastro.get("codigo_cliente_integracao"),
        "situacao": "INATIVO" if cadastro.get("inativo") == "S" else "ATIVO",
        "tags": [item.get("tag") for item in tags if isinstance(item, dict)],
        "cnpj_cpf": cadastro.get("cnpj_cpf"),
        "razao_social": cadastro.get("razao_social"),
        "nome_fantasia": cadastro.get("nome_fantasia"),
        "telefone": " ".join(
            part for part in [cadastro.get("telefone1_ddd"), cadastro.get("telefone1_numero")] if part
        ),
        "contato": cadastro.get("contato"),
        "email": cadastro.get("email"),
        "cidade": cadastro.get("cidade"),
        "cidade_ibge": cadastro.get("cidade_ibge"),
        "estado": cadastro.get("estado"),
        "endereco": cadastro.get("endereco"),
        "endereco_numero": cadastro.get("endereco_numero"),
        "complemento": cadastro.get("complemento"),
        "bairro": cadastro.get("bairro"),
        "cep": cadastro.get("cep"),
        "banco_codigo": dados_bancarios.get("codigo_banco"),
        "agencia": dados_bancarios.get("agencia"),
        "conta_corrente": dados_bancarios.get("conta_corrente"),
        "chave_pix": dados_bancarios.get("cChavePix"),
        "inscricao_estadual": cadastro.get("inscricao_estadual"),
        "contribuinte_icms": cadastro.get("contribuinte"),
        "inscricao_municipal": cadastro.get("inscricao_municipal"),
        "tipo_atividade_codigo": cadastro.get("tipo_atividade"),
        "numero_parcelas_padrao": recomendacoes.get("numero_parcelas"),
        "vendedor_padrao_codigo": recomendacoes.get("codigo_vendedor"),
        "email_nfe_boleto": recomendacoes.get("email_fatura"),
        "boleto_ao_emitir_nfe": recomendacoes.get("gerar_boletos"),
        "faturamento_bloqueado": cadastro.get("bloquear_faturamento"),
        "credito_total": cadastro.get("valor_limite_credito"),
        "caracteristicas": caracteristicas,
        "transportadora_codigo": recomendacoes.get("codigo_transportadora"),
        "inclusao_data": info.get("dInc"),
        "inclusao_hora": info.get("hInc"),
        "ultima_alteracao_data": info.get("dAlt"),
        "ultima_alteracao_hora": info.get("hAlt"),
        "incluido_por": info.get("uInc"),
        "alterado_por": info.get("uAlt"),
        "importado_api": info.get("cImpAPI") or cadastro.get("importado_api"),
        "total_a_receber": None,
        "credito_disponivel": None,
        "integracao_automatica": None,
        "monitoramento": None,
        "campos_pendentes_enriquecimento": [
            "banco_nome",
            "tipo_atividade_descricao",
            "vendedor_padrao_nome",
            "transportadora_nome",
            "total_a_receber",
            "credito_disponivel",
            "integracao_automatica",
            "monitoramento",
        ],
    }
