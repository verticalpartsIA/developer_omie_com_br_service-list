# instructions.md — Guia de Consumo para IA (Claude e outras)

> Este arquivo é o **ponto de entrada** para qualquer IA/LLM que precise entender o que este repositório oferece.
> Se você (IA) chegou aqui a partir de um link, leia este arquivo primeiro, depois o [README.md](README.md), depois a issue do módulo relevante.

## O que é este repositório
Espelho em Supabase (PostgreSQL) de todas as entidades expostas pelas APIs do **Omie ERP** (https://developer.omie.com.br/service-list/), usado pela **VerticalParts** para consultas analíticas, integrações internas (ex.: VP Pós-Venda 360°, vpsistema) e dashboards — sem depender de chamadas diretas à API do Omie a cada requisição.

Ver estrutura completa de tabelas em [README.md](README.md).

## Índice por módulo Omie
Cada módulo tem uma issue dedicada com: tabela de endpoints x tabela Supabase correspondente, gaps identificados e links para a documentação oficial do Omie.

| Módulo | Issue | Cobertura |
|---|---|---|
| Geral (clientes, produtos, cadastros base) | [#1](https://github.com/verticalpartsIA/developer_omie_com_br_service-list/issues/1) | quase completa — 1 gap (Características de Produtos) |
| CRM | [#2](https://github.com/verticalpartsIA/developer_omie_com_br_service-list/issues/2) | quase completa — 1 gap (Finders) |
| Finanças | [#3](https://github.com/verticalpartsIA/developer_omie_com_br_service-list/issues/3) | completa — 1 gap (Resumo agregado) |
| Compras (+ fluxo de importação) | [#4](https://github.com/verticalpartsIA/developer_omie_com_br_service-list/issues/4) | completa — 1 gap (Resumo agregado) |
| Impostos | [#5](https://github.com/verticalpartsIA/developer_omie_com_br_service-list/issues/5) | **100% completa** |
| Estoque | [#6](https://github.com/verticalpartsIA/developer_omie_com_br_service-list/issues/6) | completa — 1 gap (Resumo agregado) |
| Vendas e NF-e | [#7](https://github.com/verticalpartsIA/developer_omie_com_br_service-list/issues/7) | **maiores gaps** — NF-e, cupom fiscal, NFC-e, SAT ausentes |
| Serviços e NFS-e | [#8](https://github.com/verticalpartsIA/developer_omie_com_br_service-list/issues/8) | completa — gaps em NFS-e/resumo/documentos |
| Painel do Contador | [#9](https://github.com/verticalpartsIA/developer_omie_com_br_service-list/issues/9) | completa — 1 gap (Resumo agregado) |

## Índice por fluxo de negócio (VerticalParts)
Use isto quando a pergunta for orientada a processo, não a módulo técnico:

| Preciso saber sobre... | Onde olhar |
|---|---|
| Clientes reais (sem fornecedor/transportadora) | `clientes` — ver [#1](https://github.com/verticalpartsIA/developer_omie_com_br_service-list/issues/1) |
| Produtos com estoque, código, marca, família | `produtos`, `produtos_variacao`, `consulta_estoque` — ver [#6](https://github.com/verticalpartsIA/developer_omie_com_br_service-list/issues/6) |
| Compras já feitas (recebidas/faturadas) | `pedidos_compra` + `notas_entrada` + `recebimento_nfe` — ver [#4](https://github.com/verticalpartsIA/developer_omie_com_br_service-list/issues/4) |
| Compras de importação aguardando entrega | Omie não modela isso nativamente — ver recomendação de tabela própria `importacoes_status` em [#4](https://github.com/verticalpartsIA/developer_omie_com_br_service-list/issues/4) |
| Contas a pagar/receber em aberto | `contas_pagar`, `contas_receber` — ver [#3](https://github.com/verticalpartsIA/developer_omie_com_br_service-list/issues/3) |
| Pedidos de venda e faturamento | `pedidos_venda`, `pedidos_venda_fat`, `pedidos_venda_etapas` — ver [#7](https://github.com/verticalpartsIA/developer_omie_com_br_service-list/issues/7) |
| Emissão/consulta de NF-e | **Gap** — não implementado ainda, ver prioridades em [#7](https://github.com/verticalpartsIA/developer_omie_com_br_service-list/issues/7) |
| Oportunidades e funil de vendas (CRM) | `crm_oportunidades`, `crm_fases`, `crm_status` — ver [#2](https://github.com/verticalpartsIA/developer_omie_com_br_service-list/issues/2) |
| Ordens de serviço e contratos | `ordens_servico`, `contratos_servico` — ver [#8](https://github.com/verticalpartsIA/developer_omie_com_br_service-list/issues/8) |
| Tabelas fiscais auxiliares (CFOP, CST, NCM, CEST) | módulo Impostos — ver [#5](https://github.com/verticalpartsIA/developer_omie_com_br_service-list/issues/5) |

## Outras integrações da VerticalParts documentadas aqui
Este repositório não cobre só Omie — também centraliza conhecimento de outras integrações usadas em projetos da VerticalParts, para qualquer IA consumir:

| Assunto | Arquivo |
|---|---|
| WhatsApp (Evolution API) + Claude rodando na VPS Hostinger — arquitetura, fluxo de auto-resposta, Claude Code como agente de operação da VPS | [evolution-whatsapp-claude-vps.md](evolution-whatsapp-claude-vps.md) |
| Formulário público via token + envio por WhatsApp (sem login, captura de respostas e anexos) — extraído do Módulo 7 do `003_requisicoes` | [whatsapp-form-token-pattern.md](whatsapp-form-token-pattern.md) |
| Coleta e validação de assinatura digital via link público (Módulo Jurídico) — extraído do `010_vpprd` | [digital-signature-collection-pattern.md](digital-signature-collection-pattern.md) |
| Copiloto flutuante consciente da tela (DOM-aware, não visão computacional) — extraído do `010_vpprd` | [dom-aware-copilot-agent-pattern.md](dom-aware-copilot-agent-pattern.md) |

## Convenções do schema
- Tabelas em `snake_case`, em português
- Toda tabela tem `id UUID PRIMARY KEY`, `created_at`, `updated_at`
- Campos originais do Omie mantêm nome original da API (ex.: `codigo_cliente_omie`)
- RLS habilitado em todas as tabelas

## Referência oficial
Índice completo de todos os ~130 endpoints da API Omie: https://developer.omie.com.br/service-list/
