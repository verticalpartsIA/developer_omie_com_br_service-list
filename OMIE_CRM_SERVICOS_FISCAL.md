# Omie MCP — CRM, Serviços/NFS-e e Fiscal

Este documento registra a cobertura semântica adicionada ao MCP para CRM, Serviços/NFS-e e Painel do Contador.

## CRM

Endpoints oficiais usados:

- `/api/v1/crm/oportunidades/`
- `/api/v1/crm/oportunidades-resumo/`
- `/api/v1/crm/tarefas/`

Ferramentas MCP:

- `omie_crm_oportunidades_listar`
- `omie_crm_oportunidade_consultar`
- `omie_crm_tarefas_listar`
- `omie_crm_resumo_oportunidades`
- `omie_crm_oportunidade_360`

A oportunidade expõe conta, contato, origem, solução, vendedor, fase/status, ticket, previsão/temperatura, observações, envolvidos, concorrentes e tarefas.

## Serviços e NFS-e

Endpoints oficiais usados:

- `/api/v1/servicos/servico/`
- `/api/v1/servicos/os/`
- `/api/v1/servicos/contrato/`
- `/api/v1/servicos/nfse/`

Ferramentas MCP:

- `omie_servicos_listar`
- `omie_servico_consultar`
- `omie_os_listar`
- `omie_os_consultar`
- `omie_os_status`
- `omie_contratos_servico_listar`
- `omie_nfse_listar`
- `omie_os_ciclo_servico`

A listagem de NFS-e permite filtrar diretamente por cliente, OS e contrato. Isso permite uma ligação segura entre ordem de serviço, contrato, NFS-e e cliente.

## Painel do Contador / Documentos Fiscais

Endpoints oficiais usados:

- `/api/v1/contador/xml/`
- `/api/v1/contador/resumo/`

Ferramentas MCP:

- `omie_documentos_fiscais_listar`
- `omie_documento_fiscal_por_chave`
- `omie_resumo_contador`

`ListarDocumentos` devolve XML e identificadores de ligação como `nIdPedido`, `nIdOS`, `nIdReceb`, `nIdNF` e chave fiscal. Esses identificadores são estratégicos para auditoria e rastreabilidade entre operação, documento fiscal e financeiro.

## Princípio de fidelidade

Ferramentas compostas só afirmam vínculos quando existe chave oficial publicada pelo Omie. Paginação, ausência de filtro seletivo ou ambiguidade devem ser explicitadas na resposta em vez de produzir falsa certeza.
