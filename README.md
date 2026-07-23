# developer_omie_com_br_service-list

> **Espelho Supabase de todas as APIs do Omie ERP**  
> Referência: [developer.omie.com.br/service-list](https://developer.omie.com.br/service-list/)

## Natureza deste repositório (leia antes de tudo)

Este é um **Hub de Tutoriais e Metadados para consumo por LLMs/Agentes de IA** — não um repositório de código de produção. O schema Omie (tabelas abaixo) é a exceção documental necessária (é a própria informação a ser consumida); os demais arquivos (`*-pattern.md`, `*-tutorial.md`) são **guias de engenharia** ("como construir", "onde aprofundar"), não código de produção colado — cada um aponta para o repositório real de onde o padrão foi extraído. Ao adicionar novo conteúdo aqui, prefira ensinar o raciocínio e citar o arquivo de origem em vez de copiar código bruto.

---

## O que é este projeto?

Este repositório contém o **schema completo de tabelas Supabase (PostgreSQL)** que espelham todas as entidades expostas pelas APIs do **Omie ERP**. O objetivo é centralizar os dados do Omie em um banco relacional acessível, permitindo:

- Consultas analíticas avançadas sem bater na API do Omie a cada requisição
- Integração com sistemas internos (ex.: VP Pós-Venda 360°) via Supabase client
- Histórico e auditoria de dados que o Omie não persiste por padrão
- Dashboards e relatórios com dados combinados de múltiplos módulos

---

## Para que serve?

| Necessidade | Como este projeto atende |
|---|---|
| Listar clientes reais (sem fornecedores) | Tabela `ClientesReais` — sincronizada via ETL do Omie |
| Consultar produtos VP com estoque | Tabela `Produtos_VP` — com código, marca, família, bloqueado |
| Cruzar financeiro com pedidos | Tabelas `ContaReceber` + `PedidoVenda` no mesmo banco |
| Acesso sem rate-limit da API Omie | Leitura direta no Supabase, sincronização periódica |
| Segurança e RLS por role | Row Level Security habilitada em todas as tabelas |

---

## Estrutura dos Módulos

### 1. Geral

| Tabela Supabase | API Omie | Descrição |
|---|---|---|
| `clientes` | Clientes | Clientes, fornecedores, transportadoras |
| `clientes_caract` | ClientesCaract | Características de clientes |
| `cliente_tags` | ClienteTag | Tags de clientes |
| `projetos` | Projetos | Projetos |
| `empresas` | Empresas | Empresas cadastradas |
| `departamentos` | Departamentos | Departamentos |
| `categorias` | Categorias | Categorias financeiras |
| `parcelas` | Parcelas | Condições de parcelamento |
| `tipos_atividade` | TpAtiv | Tipos de atividade da empresa |
| `cnae` | CNAE | Classificação Nacional de Atividades Econômicas |
| `cidades` | Cidades | Cidades brasileiras |
| `paises` | Paises | Países |
| `tipos_anexo` | TiposAnexo | Tipos de anexos |
| `anexos` | Anexo | Documentos anexos |
| `tipos_entrega` | TiposEntrega | Tipos de entrega |
| `tipos_assinante` | TipoAssinante | Tipos de assinante |
| `tarefas_geral` | Tarefas | Tarefas gerais |

### 2. CRM

| Tabela Supabase | API Omie | Descrição |
|---|---|---|
| `crm_contas` | Contas | Contas CRM |
| `crm_contas_caract` | ContasCaract | Características de contas |
| `crm_contatos` | Contatos | Contatos CRM |
| `crm_oportunidades` | Oportunidades | Oportunidades de venda |
| `crm_oportunidades_resumo` | Oportunidades-Resumo | Resumo de oportunidades |
| `crm_tarefas` | Tarefas | Tarefas CRM |
| `crm_tarefas_resumo` | Tarefas-Resumo | Resumo de tarefas |
| `crm_solucoes` | Solucoes | Soluções CRM |
| `crm_fases` | Fases | Fases do funil |
| `crm_usuarios` | Usuarios | Usuários do CRM |
| `crm_status` | Status | Status de oportunidades |
| `crm_motivos` | Motivos | Motivos de perda |
| `crm_tipos` | Tipos | Tipos de oportunidade |
| `crm_parceiros` | Parceiros | Parceiros |
| `crm_origens` | Origens | Origens dos leads |
| `crm_concorrentes` | Concorrentes | Concorrentes |
| `crm_verticais` | Verticais | Verticais de mercado |
| `crm_tipos_tarefa` | TiposTarefa | Tipos de tarefas CRM |

### 3. Financas

| Tabela Supabase | API Omie | Descrição |
|---|---|---|
| `contas_correntes` | ContaCorrente | Contas bancárias |
| `contas_correntes_lancamentos` | ContaCorrenteLancamentos | Lançamentos bancários |
| `contas_pagar` | ContaPagar | Contas a pagar |
| `contas_receber` | ContaReceber | Contas a receber |
| `contas_receber_boletos` | ContaReceberBoleto | Boletos |
| `pix` | PIX | Cobranças PIX |
| `extrato` | Extrato | Extrato de conta corrente |
| `orcamento_caixa` | Caixa | Orçamento de caixa |
| `titulos_pesquisa` | PesquisarTitulos | Pesquisa de títulos |
| `movimentos_financeiros` | MF | Movimentos financeiros |
| `bancos` | Bancos | Bancos |
| `tipos_documento` | TiposDoc | Tipos de documento |
| `tipos_conta_corrente` | TiposCC | Tipos de contas correntes |
| `contas_dre` | DRE | Contas do DRE |
| `finalidade_transferencia` | FinalTransf | Finalidades de transferência |
| `origem_lancamento` | OrigemLancamento | Origem dos títulos |
| `bandeiras_cartao` | BandeiraCartao | Bandeiras de cartão |

### 4. Compras, Estoque e Producao

| Tabela Supabase | API Omie | Descrição |
|---|---|---|
| `produtos` | Produtos | Cadastro de produtos |
| `produtos_caract` | ProdCaract | Características de produtos |
| `produtos_estrutura` | Malha | Estrutura (BOM) de produtos |
| `produtos_kit` | ProdutosKit | Kits de produtos |
| `produtos_variacao` | Variacao | Variações de produtos |
| `produtos_lote` | ProdutosLote | Lotes de produtos |
| `requisicoes_compra` | RequisicaoCompra | Requisições de compra |
| `pedidos_compra` | PedidoCompra | Pedidos de compra |
| `ordens_producao` | OP | Ordens de produção |
| `notas_entrada` | NotaEntrada | Notas fiscais de entrada |
| `notas_entrada_fat` | NotaEntradaFat | Faturamento de NF entrada |
| `recebimento_nfe` | RecebimentoNFe | Recebimento de NF-e |
| `familias_produto` | Familias | Famílias de produto |
| `unidades` | Unidade | Unidades de medida |
| `compradores` | Comprador | Compradores |
| `produto_fornecedor` | ProdutoFornecedor | Relação produto x fornecedor |
| `formas_pagamento_compras` | FormasPagCompras | Formas de pagamento (compras) |
| `ncm` | NCM | NCM — Nomenclatura Comum do Mercosul |
| `cenarios_impostos` | Cenarios | Cenários de impostos |
| `cfop` | CFOP | CFOP |
| `icms_cst` | ICMSCST | ICMS CST |
| `icms_csosn` | ICMSCSOSN | ICMS CSOSN |
| `icms_origem` | ICMSOrigem | ICMS Origem da Mercadoria |
| `pis_cst` | PISCST | PIS CST |
| `cofins_cst` | COFINSCST | COFINS CST |
| `ipi_cst` | IPICST | IPI CST |
| `ipi_enquadramento` | IPIEnq | IPI Enquadramento |
| `tipo_calculo` | TpCalc | Tipos de cálculo |
| `cest` | CEST | CEST |
| `ajustes_estoque` | Ajuste | Ajustes de estoque |
| `consulta_estoque` | Consulta | Consulta de estoque |
| `movimento_estoque` | MovEstoque | Movimentos de estoque |
| `locais_estoque` | Local | Locais de estoque |

### 5. Vendas e NF-e

| Tabela Supabase | API Omie | Descrição |
|---|---|---|
| `pedidos_venda` | Pedido | Pedidos de venda completo |
| `pedidos_venda_resumo` | PedidoVenda | Pedidos de venda resumido |
| `pedidos_venda_fat` | PedidoVendaFat | Faturamento de pedidos |
| `pedidos_venda_etapas` | PedidoEtapas | Etapas dos pedidos |
| `cte` | CTe | CT-e / CT-e OS |
| `remessa_produtos` | Remessa | Remessa de produtos |
| `remessa_fat` | RemessaFat | Faturamento de remessas |
| `vendedores` | Vendedores | Vendedores |
| `formas_pagamento_vendas` | FormasPagVendas | Formas de pagamento (vendas) |
| `tabela_precos` | TabelaPrecos | Tabelas de preço |
| `etapas_faturamento` | EtapaFat | Etapas de faturamento |
| `meios_pagamento` | MeiosPagamento | Meios de pagamento |
| `origem_pedido` | OrigemPedido | Origens do pedido |
| `motivos_devolucao` | MotivoDevolucao | Motivos de devolução |

### 6. Servicos e NFS-e

| Tabela Supabase | API Omie | Descrição |
|---|---|---|
| `servicos` | Servico | Cadastro de serviços |
| `ordens_servico` | OS | Ordens de serviço |
| `ordens_servico_fat` | OSP | Faturamento de OS |
| `ordens_servico_lote` | OSLote | Faturamento em lote de OS |
| `contratos_servico` | Contrato | Contratos de serviço |
| `contratos_fat` | ContratoFat | Faturamento de contratos |
| `contratos_lote` | ContratoLote | Faturamento em lote de contratos |
| `servicos_municipio` | ListaServico | Serviços no município |
| `tipos_tributacao` | TipoTrib | Tipos de tributação |
| `lc116` | LC116 | LC 116 |
| `nbs` | NBS | NBS |
| `ibpt` | IBPT | IBPT |
| `contrato_tipo_fat` | ContratoTpFat | Tipo de faturamento de contrato |
| `tipo_utilizacao` | TipoUtilizacao | Tipos de utilização |
| `classificacao_servico` | ClassificacaoServico | Classificação do serviço |

### 7. Painel do Contador

| Tabela Supabase | API Omie | Descrição |
|---|---|---|
| `documentos_fiscais_xml` | XML | Documentos fiscais (XML) |

---

## Stack

| Camada | Tecnologia |
|---|---|
| Banco de dados | Supabase (PostgreSQL 15) |
| Sincronizacao | ETL via Omie REST API para Supabase |
| Seguranca | Row Level Security (RLS) em todas as tabelas |
| Referencia API | [developer.omie.com.br/service-list](https://developer.omie.com.br/service-list/) |

---

## Convencoes

- Todas as tabelas em **snake_case** e em **portugues**
- Toda tabela tem: `id UUID PRIMARY KEY`, `created_at TIMESTAMPTZ`, `updated_at TIMESTAMPTZ`
- Campos originais do Omie mantem os nomes originais da API (ex.: `codigo_cliente_omie`, `razao_social`)
- RLS habilitada — acesso controlado por role do Supabase

---

## Índice de Navegação para IA (LLM-Readable Index)

> Mapa exato de onde encontrar cada tipo de informação neste repositório. Todos os caminhos abaixo são relativos à raiz deste repo, exceto onde indicado como link externo.

### Documentação por arquivo

| Path | Conteúdo | Quando consultar |
|---|---|---|
| [`README.md`](README.md) | Este arquivo — schema completo das tabelas Omie↔Supabase, por módulo | Ver lista de tabelas e campos do espelho Omie |
| [`instructions.md`](instructions.md) | Ponto de entrada para qualquer LLM — índice por módulo Omie e por fluxo de negócio | Primeira leitura ao abrir este repositório |
| [`evolution-whatsapp-claude-vps.md`](evolution-whatsapp-claude-vps.md) | Evolution API + Claude na VPS Hostinger — auto-resposta de WhatsApp | Implementar chatbot de WhatsApp com IA |
| [`whatsapp-form-token-pattern.md`](whatsapp-form-token-pattern.md) | Formulário público via token + envio por WhatsApp (M7 Quadro de Comando) | Implementar formulário sem login, coleta de resposta/anexo por link |
| [`digital-signature-collection-pattern.md`](digital-signature-collection-pattern.md) | Coleta/validação de assinatura digital via link público (Módulo Jurídico) | Implementar assinatura de contrato/proposta sem login |
| [`dom-aware-copilot-agent-pattern.md`](dom-aware-copilot-agent-pattern.md) | Copiloto flutuante DOM-aware (preenche/revisa tela via IA) | Implementar assistente de IA que lê e preenche formulários da tela atual |
| [`scheduled-telegram-report-pattern.md`](scheduled-telegram-report-pattern.md) | Relatório diário agendado via Telegram (cron determinístico, sem IA) | Implementar automação de relatório/alerta agendado |
| [`modulo-alcadas-tutorial.md`](modulo-alcadas-tutorial.md) | Tutorial de engenharia: níveis de aprovação por valor (Alçadas) — passo a passo, não código bruto | Implementar sistema de aprovação hierárquica por faixa de valor |

### Regras de negócio, endpoints e schemas — por módulo Omie (Issues)

| Módulo Omie | Issue | O que tem lá |
|---|---|---|
| Geral (clientes/produtos/cadastros) | [#1](https://github.com/verticalpartsIA/developer_omie_com_br_service-list/issues/1) | Tabela endpoint↔tabela Supabase, gaps |
| CRM | [#2](https://github.com/verticalpartsIA/developer_omie_com_br_service-list/issues/2) | idem |
| Finanças | [#3](https://github.com/verticalpartsIA/developer_omie_com_br_service-list/issues/3) | idem |
| Compras (+ fluxo de importação) | [#4](https://github.com/verticalpartsIA/developer_omie_com_br_service-list/issues/4) | idem + fluxo "compras recebidas x aguardando importação" |
| Impostos | [#5](https://github.com/verticalpartsIA/developer_omie_com_br_service-list/issues/5) | idem (100% coberto) |
| Estoque | [#6](https://github.com/verticalpartsIA/developer_omie_com_br_service-list/issues/6) | idem |
| Vendas e NF-e | [#7](https://github.com/verticalpartsIA/developer_omie_com_br_service-list/issues/7) | idem (maiores gaps: NF-e, cupom fiscal, NFC-e, SAT) |
| Serviços e NFS-e | [#8](https://github.com/verticalpartsIA/developer_omie_com_br_service-list/issues/8) | idem |
| Painel do Contador | [#9](https://github.com/verticalpartsIA/developer_omie_com_br_service-list/issues/9) | idem |

### Rastreabilidade de portabilidade entre repositórios (Issues)

| Padrão recebido | Issue de recepção (aqui) | Issue de origem (repo doador) |
|---|---|---|
| WhatsApp/Claude/VPS | [#10](https://github.com/verticalpartsIA/developer_omie_com_br_service-list/issues/10) | [004_sac_posvenda360#10](https://github.com/verticalpartsIA/004_sac_posvenda360/issues/10) |
| Formulário via token + WhatsApp | [#11](https://github.com/verticalpartsIA/developer_omie_com_br_service-list/issues/11) | [003_requisicoes#33](https://github.com/verticalpartsIA/003_requisicoes/issues/33) |
| Assinatura digital | [#12](https://github.com/verticalpartsIA/developer_omie_com_br_service-list/issues/12) | [010_vpprd#19](https://github.com/verticalpartsIA/010_vpprd/issues/19) |
| Copiloto DOM-aware | [#13](https://github.com/verticalpartsIA/developer_omie_com_br_service-list/issues/13) | [010_vpprd#20](https://github.com/verticalpartsIA/010_vpprd/issues/20) |
| Relatório agendado via Telegram | [#14](https://github.com/verticalpartsIA/developer_omie_com_br_service-list/issues/14) | [008_BorderoDiario#8](https://github.com/verticalpartsIA/008_BorderoDiario/issues/8) |

---

## Glossário Técnico

> Termos operacionais da VerticalParts com definição verificada e ponteiro exato para onde a regra de negócio está detalhada. **Só entram aqui termos confirmados por leitura direta de código/schema** — nada é listado por suposição.

| Termo | Definição | Ponteiro (path / issue) |
|---|---|---|
| **Alçada (nível de aprovação)** | Faixa de valor que define quem pode aprovar uma requisição de compra: Nível 1 até R$ 1.500,00, Nível 2 de R$ 1.500,01 a R$ 3.500,00, Nível 3 acima de R$ 3.500,00 (limites configuráveis pelo Admin). | `003_requisicoes/src/lib/approval.ts`, `003_requisicoes/database/004_approval_tiers_and_admin.sql` |
| **Quadro de Comando (M7)** | Formulário técnico de levantamento de dados de motor/encoder/botoeira/portas de elevador, enviado ao cliente via link público por WhatsApp e preenchido sem login. | [whatsapp-form-token-pattern.md](whatsapp-form-token-pattern.md), `003_requisicoes/src/features/comando/*` |
| **Token de assinatura** | Identificador curto (16 hex) que autoriza acesso público a um contrato/proposta específico na página `/assinar/{token}`, sem exigir login; expira em 7 dias. | [digital-signature-collection-pattern.md](digital-signature-collection-pattern.md), `010_vpprd/src/assinar-app.jsx` |
| **Copiloto VP** | Widget de IA em bolinha flutuante presente em todas as telas do sistema `vpprd`; lê o DOM (não visão computacional) e responde/preenche/revisa. | [dom-aware-copilot-agent-pattern.md](dom-aware-copilot-agent-pattern.md), `010_vpprd/src/vp-copiloto.jsx` |
| **Hermes** | Nome/marca do agente de IA "CFO digital" da VerticalParts, citado no rodapé do Borderô e em runbooks de operação da VPS — distinto do Claude-chatbot (responde texto via API) e do Claude Code-operador (executa comandos na VPS). | `008_BorderoDiario/hermes/*`, [scheduled-telegram-report-pattern.md](scheduled-telegram-report-pattern.md) |
| **Borderô Financeiro** | Relatório diário (PDF) com notas emitidas, recebimentos e pagamentos de ontem + resumos de semana/mês/ano, gerado por cron determinístico e enviado via Telegram. | `008_BorderoDiario/script/gerar_bordero.py`, [scheduled-telegram-report-pattern.md](scheduled-telegram-report-pattern.md) |
| **Instância `pv360` (Evolution API)** | Nome da instância WhatsApp conectada na Evolution API (VPS `72.61.48.156:8080`), reutilizada por múltiplos projetos (`004_sac_posvenda360`, `003_requisicoes`) como gateway de envio/recebimento. | [evolution-whatsapp-claude-vps.md](evolution-whatsapp-claude-vps.md), [whatsapp-form-token-pattern.md](whatsapp-form-token-pattern.md) |
| **`@lid`** | Tipo de identificador de contato do WhatsApp com "privacidade avançada"; a Evolution API (em algumas versões) não consegue enviar mensagens para esse tipo de contato — cai para atendimento humano. | [evolution-whatsapp-claude-vps.md](evolution-whatsapp-claude-vps.md) |
| **RLS (Row Level Security)** | Mecanismo do Postgres/Supabase usado em todas as tabelas deste espelho Omie e nos padrões documentados para restringir acesso por role (`authenticated`/`anon`/`service_role`). | `README.md` (seção Stack), issues #1–#9 |
| **Service role vs anon key** | Duas formas de acessar o Supabase a partir de uma página pública: via server function com service role (mais seguro, usado no padrão de formulário) ou via client direto com `anon` key (usado no padrão de assinatura digital — sinalizado como risco a reforçar). | [whatsapp-form-token-pattern.md](whatsapp-form-token-pattern.md) vs [digital-signature-collection-pattern.md](digital-signature-collection-pattern.md) |
| **Dia útil anterior** | Regra de cálculo de data de referência de relatórios: pula sábado/domingo (não cobre feriados) — usada para o Borderô sempre mostrar o último dia útil fechado. | `008_BorderoDiario/script/gerar_bordero.py`, [scheduled-telegram-report-pattern.md](scheduled-telegram-report-pattern.md) |
| **NF-e / NFS-e / CT-e** | Documentos fiscais eletrônicos (Nota Fiscal eletrônica, Nota Fiscal de Serviço eletrônica, Conhecimento de Transporte eletrônico) — emissão/consulta de NF-e é o maior gap do mirror Omie atual. | Issues [#7](https://github.com/verticalpartsIA/developer_omie_com_br_service-list/issues/7), [#8](https://github.com/verticalpartsIA/developer_omie_com_br_service-list/issues/8) |
| **bd_Omie** | Nome do projeto Supabase que hospeda este espelho do Omie ERP; consumido em modo somente-leitura por outros sistemas da VerticalParts (ex.: `004_sac_posvenda360`, `003_requisicoes`). | `README.md`, `instructions.md` |
| **vpsistema.com (IdP)** | Portal central de identidade e SSO de todo o grupo VerticalParts — login único, catálogo de módulos, permissões e auditoria. Ver seção dedicada abaixo. | `001_vpsistema/README.md`, `001_vpsistema/supabase/functions/*` |
| **`profiles` (vpsistema)** | Tabela de colaboradores ativos da VerticalParts (nome, cargo, departamento, nível de acesso) — fonte canônica de identidade do grupo. | `001_vpsistema` — Supabase `ubdkoqxfwcraftesgmbw` |
| **`module_permissions`** | Tabela de allowlist de acesso por colaborador × módulo. Sem linhas para um usuário = acesso pleno a todos os módulos; com linhas = só os slugs listados. | `001_vpsistema` — Supabase `ubdkoqxfwcraftesgmbw` |
| **SSO — `token` vs `magiclink`** | Duas famílias de federação de identidade usadas pelo vpsistema: `token` (app satélite confia direto no JWT do vpsistema, sem Auth próprio) e `magiclink` (app satélite tem Supabase Auth separado; vpsistema cria/casa o usuário por e-mail via service role e gera magic link). Não confundir com o item "Service role vs anon key" acima — são mecanismos complementares. | `001_vpsistema/supabase/functions/_shared/apps.ts`, `sso-proxy/index.ts`, `provision-module-user/index.ts` |

---

## Identity Provider (IdP) — vpsistema.com

> **vpsistema.com é o Identity Provider (IdP) e hub de Single Sign-On (SSO) central de todo o ecossistema VerticalParts.** Login único, catálogo de sistemas (módulos), controle de acesso e auditoria para todos os colaboradores ativos. Repositório: [`verticalpartsIA/001_vpsistema`](https://github.com/verticalpartsIA/001_vpsistema).

### Onde estão os dados de "Usuários" — Supabase do vpsistema

| Tabela | Projeto Supabase | Descrição |
|---|---|---|
| `profiles` | `ubdkoqxfwcraftesgmbw` (`001_vpsistema`) | Colaboradores ativos: nome, e-mail, cargo, departamento, nível (`Colaborador`/`Lider`/`Administrador`) |
| `modules` | `ubdkoqxfwcraftesgmbw` (`001_vpsistema`) | Catálogo de sistemas satélites (slug, nome, URL, ícone, cor, `is_active`) |
| `module_permissions` | `ubdkoqxfwcraftesgmbw` (`001_vpsistema`) | Allowlist granular usuário × módulo |
| `activity_logs` | `ubdkoqxfwcraftesgmbw` (`001_vpsistema`) | Auditoria de login, acesso a módulo e ações administrativas |

### ⚠️ "Usuários" ≠ "Alçadas" — não são a mesma coisa, nem vivem no mesmo lugar
O termo **"Alçada"** (nível de aprovação por faixa de valor) é uma **regra de negócio local do módulo de Requisições**, não parte da identidade/SSO. Ela vive em um projeto Supabase **diferente** do vpsistema:

| O quê | Onde vive |
|---|---|
| Identidade do colaborador (quem é, cargo, se está ativo) | `001_vpsistema` → tabela `profiles`, Supabase `ubdkoqxfwcraftesgmbw` |
| Alçada de aprovação (quanto cada nível pode aprovar) | `003_requisicoes` → `database/004_approval_tiers_and_admin.sql` + `src/lib/approval.ts`, Supabase próprio do vprequisicoes (`vvgcrhtmzvssfdazkkzk`) |

Um novo sistema que precise saber **"este colaborador está ativo?"** consulta `profiles` no vpsistema. Um sistema que precise saber **"este colaborador pode aprovar R$ 2.000?"** consulta a lógica de alçada local do projeto que a implementa — são consultas a dois bancos diferentes, não uma tabela unificada.

### Federação de SSO — duas famílias (não existe um único `auth.users` compartilhado)
Não há uma tabela de usuários única usada por todos os sistemas. A identidade é federada de duas formas, configuradas em `001_vpsistema/supabase/functions/_shared/apps.ts`:

| Tipo | Apps | Como funciona |
|---|---|---|
| `token` | `vpclick`, `catraca`, `propostas`, `vpprd` | App satélite não tem Auth próprio — recebe e confia direto no JWT do vpsistema via `?sso_token=` |
| `magiclink` | `vprequisicoes`, `posvenda360`, `visitas` | App satélite tem seu **próprio** projeto Supabase Auth; o vpsistema cria/casa o usuário por e-mail (service role) e gera um magic link de login automático |

Provisionamento é automático: assim que um admin concede uma linha em `module_permissions`, um trigger dispara a Edge Function `provision-module-user`, que **revalida a permissão direto no banco** antes de provisionar (proteção contra chamada forjada, já que uma chamada disparada pelo Postgres não carrega JWT de usuário).

## Regras de Comportamento para LLMs/Agentes de IA (Consumo de Dados de Colaboradores)

Ao construir ou avaliar qualquer solução nova para a VerticalParts que precise saber **quem é o colaborador** ou **o que ele pode acessar**, siga esta ordem:

1. **Não crie uma tabela de usuários paralela.** Identidade canônica é `profiles` em `001_vpsistema` (Supabase `ubdkoqxfwcraftesgmbw`). Duplicar isso fragmenta a fonte de verdade.
2. **Para autenticação/login de um sistema novo**, prefira o padrão `token` (confiar no JWT do vpsistema) sempre que o novo sistema puder aceitar essa dependência — é mais simples e não duplica Auth. Só use o padrão `magiclink` (Supabase Auth próprio + provisionamento por e-mail) se o sistema tiver uma razão real para banco de auth separado.
3. **Para saber "quem pode acessar o quê"**, consulte `module_permissions` (ausência de linha = acesso pleno; presença = allowlist). Não implemente uma lógica de permissão equivalente do zero.
4. **Regras de negócio específicas de um módulo (ex.: Alçadas) não pertencem à identidade** — ficam no schema do próprio projeto que as usa. Não misture "quem é o usuário" com "o que esse módulo permite que ele faça no domínio X".
5. **Restrição de acesso**: este repositório de conhecimento **não contém credenciais reais** de nenhum Supabase (nem do vpsistema, nem de nenhum satélite) — apenas nomes de projeto, nomes de tabela e URLs. Uma IA que precise da chave real deve buscá-la na fonte segura de credenciais do usuário (ex.: `credenciais_master.md`) ou perguntar ao humano responsável — **nunca inventar, adivinhar ou reutilizar uma chave de outro contexto.**
6. **Antes de recomendar um caminho de integração**, confirme se o app-alvo já está listado em `_shared/apps.ts` do `001_vpsistema`. Se não estiver (ex.: `engenharia`, `suporte` — presentes no catálogo `modules` mas sem SSO configurado ainda), isso é um gap a sinalizar, não a assumir como resolvido.

---

*Projeto VerticalParts — Omie ERP Integration Layer*

---

## Contributors

- Gelson Simões — criador e responsável pelas soluções VerticalParts

---

**Feito por Gelson Simões**
