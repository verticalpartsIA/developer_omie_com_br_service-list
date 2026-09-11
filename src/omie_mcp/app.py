from __future__ import annotations

from typing import Any

from .crm import consultar_oportunidade, listar_oportunidades, listar_tarefas_crm, oportunidade_360, resumo_oportunidades
from .fiscal import documento_fiscal_por_chave, listar_documentos_fiscais, resumo_contador
from .reforma_tributaria import (
    listar_classificacoes_ibs_cbs,
    listar_cst_ibs_cbs,
    listar_indicadores_operacao,
    mapa_reforma_tributaria,
)
from .server import mcp
from .servicos import consultar_os, consultar_servico, listar_contratos, listar_nfse, listar_os, listar_servicos, os_ciclo_servico, status_os
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
    return await fornecedor_360(
        codigo_fornecedor_omie,
        pagina_financeiro=pagina_financeiro,
        registros_financeiro=registros_financeiro,
    )


@mcp.tool()
async def omie_ciclo_venda_financeiro(codigo_pedido: int) -> dict[str, Any]:
    return await ciclo_venda_financeiro(codigo_pedido)


@mcp.tool()
async def omie_ciclo_recebimento_compra_financeiro(
    id_recebimento: int | None = None,
    chave_nfe: str | None = None,
) -> dict[str, Any]:
    return await ciclo_recebimento_compra_financeiro(id_recebimento=id_recebimento, chave_nfe=chave_nfe)


# CRM
@mcp.tool()
async def omie_crm_oportunidades_listar(
    pagina: int = 1,
    registros_por_pagina: int = 50,
    status: str | None = None,
    fase: int | None = None,
    codigo_vendedor: int | None = None,
    filtrar_por_conta: int | None = None,
) -> dict[str, Any]:
    return await listar_oportunidades(
        pagina=pagina,
        registros_por_pagina=registros_por_pagina,
        status=status,
        fase=fase,
        codigo_vendedor=codigo_vendedor,
        filtrar_por_conta=filtrar_por_conta,
    )


@mcp.tool()
async def omie_crm_oportunidade_consultar(codigo_oportunidade: int | None = None, codigo_integracao: str | None = None) -> dict[str, Any]:
    return await consultar_oportunidade(codigo_oportunidade=codigo_oportunidade, codigo_integracao=codigo_integracao)


@mcp.tool()
async def omie_crm_tarefas_listar(
    pagina: int = 1,
    registros_por_pagina: int = 50,
    codigo_oportunidade: int | None = None,
    codigo_vendedor: int | None = None,
    data_inicial: str | None = None,
    data_final: str | None = None,
) -> dict[str, Any]:
    return await listar_tarefas_crm(
        pagina=pagina,
        registros_por_pagina=registros_por_pagina,
        codigo_oportunidade=codigo_oportunidade,
        codigo_vendedor=codigo_vendedor,
        data_inicial=data_inicial,
        data_final=data_final,
    )


@mcp.tool()
async def omie_crm_resumo_oportunidades(mes_ano: str, codigo_vendedor: int = 0, codigo_parceiro: int = 0) -> dict[str, Any]:
    return await resumo_oportunidades(mes_ano=mes_ano, codigo_vendedor=codigo_vendedor, codigo_parceiro=codigo_parceiro)


@mcp.tool()
async def omie_crm_oportunidade_360(codigo_oportunidade: int) -> dict[str, Any]:
    return await oportunidade_360(codigo_oportunidade)


# Serviços / NFS-e
@mcp.tool()
async def omie_servicos_listar(pagina: int = 1, registros_por_pagina: int = 50) -> dict[str, Any]:
    return await listar_servicos(pagina=pagina, registros_por_pagina=registros_por_pagina)


@mcp.tool()
async def omie_servico_consultar(codigo_servico: int | None = None, codigo_integracao: str | None = None) -> dict[str, Any]:
    return await consultar_servico(codigo_servico=codigo_servico, codigo_integracao=codigo_integracao)


@mcp.tool()
async def omie_os_listar(pagina: int = 1, registros_por_pagina: int = 50) -> dict[str, Any]:
    return await listar_os(pagina=pagina, registros_por_pagina=registros_por_pagina)


@mcp.tool()
async def omie_os_consultar(codigo_os: int | None = None, codigo_integracao: str | None = None, numero_os: str | None = None) -> dict[str, Any]:
    return await consultar_os(codigo_os=codigo_os, codigo_integracao=codigo_integracao, numero_os=numero_os)


@mcp.tool()
async def omie_os_status(codigo_os: int | None = None, codigo_integracao: str | None = None) -> dict[str, Any]:
    return await status_os(codigo_os=codigo_os, codigo_integracao=codigo_integracao)


@mcp.tool()
async def omie_contratos_servico_listar(pagina: int = 1, registros_por_pagina: int = 50) -> dict[str, Any]:
    return await listar_contratos(pagina=pagina, registros_por_pagina=registros_por_pagina)


@mcp.tool()
async def omie_nfse_listar(
    pagina: int = 1,
    registros_por_pagina: int = 20,
    codigo_cliente: int | None = None,
    codigo_os: int | None = None,
    codigo_contrato: int | None = None,
    status_nfse: str | None = None,
) -> dict[str, Any]:
    return await listar_nfse(
        pagina=pagina,
        registros_por_pagina=registros_por_pagina,
        codigo_cliente=codigo_cliente,
        codigo_os=codigo_os,
        codigo_contrato=codigo_contrato,
        status_nfse=status_nfse,
    )


@mcp.tool()
async def omie_os_ciclo_servico(codigo_os: int) -> dict[str, Any]:
    return await os_ciclo_servico(codigo_os)


# Fiscal / contador
@mcp.tool()
async def omie_documentos_fiscais_listar(
    pagina: int = 1,
    registros_por_pagina: int = 20,
    modelo: str = "55",
    operacao: str = "1",
    ambiente: str = "P",
    emissao_inicial: str | None = None,
    emissao_final: str | None = None,
) -> dict[str, Any]:
    return await listar_documentos_fiscais(
        pagina=pagina,
        registros_por_pagina=registros_por_pagina,
        modelo=modelo,
        operacao=operacao,
        ambiente=ambiente,
        emissao_inicial=emissao_inicial,
        emissao_final=emissao_final,
    )


@mcp.tool()
async def omie_documento_fiscal_por_chave(chave: str, modelo: str = "55", operacao: str = "1") -> dict[str, Any]:
    return await documento_fiscal_por_chave(chave, modelo=modelo, operacao=operacao)


@mcp.tool()
async def omie_resumo_contador(data_inicio: str, data_fim: str) -> dict[str, Any]:
    return await resumo_contador(data_inicio=data_inicio, data_fim=data_fim)


# Reforma Tributária IBS/CBS
@mcp.tool()
async def omie_ibs_cbs_cst_listar(
    pagina: int = 1,
    registros_por_pagina: int = 50,
    descricao: str | None = None,
) -> dict[str, Any]:
    return await listar_cst_ibs_cbs(
        pagina=pagina,
        registros_por_pagina=registros_por_pagina,
        descricao=descricao,
    )


@mcp.tool()
async def omie_ibs_cbs_classificacoes_listar(
    pagina: int = 1,
    registros_por_pagina: int = 50,
    descricao: str | None = None,
    cst: str | None = None,
) -> dict[str, Any]:
    return await listar_classificacoes_ibs_cbs(
        pagina=pagina,
        registros_por_pagina=registros_por_pagina,
        descricao=descricao,
        cst=cst,
    )


@mcp.tool()
async def omie_indicadores_operacao_listar(
    pagina: int = 1,
    registros_por_pagina: int = 50,
    descricao: str | None = None,
) -> dict[str, Any]:
    return await listar_indicadores_operacao(
        pagina=pagina,
        registros_por_pagina=registros_por_pagina,
        descricao=descricao,
    )


@mcp.tool()
async def omie_reforma_tributaria_mapa(
    pagina: int = 1,
    registros_por_pagina: int = 50,
) -> dict[str, Any]:
    return await mapa_reforma_tributaria(
        pagina=pagina,
        registros_por_pagina=registros_por_pagina,
    )


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
