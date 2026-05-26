# developer_omie_com_br_service-list

> **Espelho Supabase de todas as APIs do Omie ERP**  
> Referência: [developer.omie.com.br/service-list](https://developer.omie.com.br/service-list/)

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

*Projeto VerticalParts — Omie ERP Integration Layer*
