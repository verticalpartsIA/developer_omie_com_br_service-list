from __future__ import annotations

from typing import Any

from .client import client


async def listar_servicos(*, pagina: int = 1, registros_por_pagina: int = 50) -> dict[str, Any]:
    return await client.call(
        "servicos/servico",
        "ListarCadastroServico",
        {"nPagina": pagina, "nRegPorPagina": registros_por_pagina},
    )


async def consultar_servico(*, codigo_servico: int | None = None, codigo_integracao: str | None = None) -> dict[str, Any]:
    if not any([codigo_servico, codigo_integracao]):
        raise ValueError("Informe codigo_servico ou codigo_integracao")
    return await client.call(
        "servicos/servico",
        "ConsultarCadastroServico",
        {k: v for k, v in {"nCodServ": codigo_servico, "cCodIntServ": codigo_integracao}.items() if v not in (None, "")},
    )


async def listar_os(*, pagina: int = 1, registros_por_pagina: int = 50) -> dict[str, Any]:
    return await client.call(
        "servicos/os",
        "ListarOS",
        {"pagina": pagina, "registros_por_pagina": registros_por_pagina, "apenas_importado_api": "N"},
    )


async def consultar_os(*, codigo_os: int | None = None, codigo_integracao: str | None = None, numero_os: str | None = None) -> dict[str, Any]:
    if not any([codigo_os, codigo_integracao, numero_os]):
        raise ValueError("Informe codigo_os, codigo_integracao ou numero_os")
    return await client.call(
        "servicos/os",
        "ConsultarOS",
        {k: v for k, v in {"nCodOS": codigo_os, "cCodIntOS": codigo_integracao, "cNumOS": numero_os}.items() if v not in (None, "")},
    )


async def status_os(*, codigo_os: int | None = None, codigo_integracao: str | None = None) -> dict[str, Any]:
    if not any([codigo_os, codigo_integracao]):
        raise ValueError("Informe codigo_os ou codigo_integracao")
    return await client.call(
        "servicos/os",
        "StatusOS",
        {k: v for k, v in {"nCodOS": codigo_os, "cCodIntOS": codigo_integracao}.items() if v not in (None, "")},
    )


async def listar_contratos(*, pagina: int = 1, registros_por_pagina: int = 50) -> dict[str, Any]:
    return await client.call(
        "servicos/contrato",
        "ListarContratos",
        {"pagina": pagina, "registros_por_pagina": registros_por_pagina, "apenas_importado_api": "N"},
    )


async def listar_nfse(
    *,
    pagina: int = 1,
    registros_por_pagina: int = 20,
    codigo_cliente: int | None = None,
    codigo_os: int | None = None,
    codigo_contrato: int | None = None,
    status_nfse: str | None = None,
    emissao_inicial: str | None = None,
    emissao_final: str | None = None,
) -> dict[str, Any]:
    param: dict[str, Any] = {"nPagina": pagina, "nRegPorPagina": registros_por_pagina, "cExibirDescricao": "S"}
    opcionais = {
        "nCodigoCliente": codigo_cliente,
        "nCodigoOS": codigo_os,
        "nCodigoContrato": codigo_contrato,
        "cStatusNFSe": status_nfse,
        "dEmiInicial": emissao_inicial,
        "dEmiFinal": emissao_final,
    }
    param.update({k: v for k, v in opcionais.items() if v is not None})
    return await client.call("servicos/nfse", "ListarNFSEs", param)


async def os_ciclo_servico(codigo_os: int) -> dict[str, Any]:
    os = await consultar_os(codigo_os=codigo_os)
    status = await status_os(codigo_os=codigo_os)
    nfse = await listar_nfse(codigo_os=codigo_os, registros_por_pagina=50)
    return {
        "tipo_visao": "OS_CICLO_SERVICO",
        "codigo_os": codigo_os,
        "ordem_servico": os,
        "status": status,
        "nfse": nfse,
        "regra_vinculo": "ListarNFSEs.nCodigoOS = codigo_os",
    }
