# Instructions — developer_omie_com_br_service-list

**Projeto:** Espelho Supabase de todas as APIs do Omie ERP  
**Referência:** https://developer.omie.com.br/service-list/  
**Data de criação:** 2026-05-26  
**Responsável:** VerticalParts — Gelson Simões

---

## O que é este projeto

Schema completo de tabelas Supabase (PostgreSQL) que espelham todas as entidades expostas pelas APIs do Omie ERP. O banco serve como camada de leitura centralizada para os sistemas da VerticalParts (VP Pós-Venda 360, WMS, Propostas Comerciais) sem depender do rate-limit da API Omie em tempo real.

---

## Supabase

```
ID:        hrhwplqlbuwfextznkea
URL:       https://hrhwplqlbuwfextznkea.supabase.co
GitHub:    https://github.com/verticalpartsIA/developer_omie_com_br_service-list
Compute:   MICRO — 1 GB RAM / 2-core ARM CPU
Região:    Americas
Org:       VerticalParts (PRO)
```

Credenciais completas (anon, service role, secret, publishable) em:
`C:\Users\gelso\VerticalParts\CredenciaisMD\credenciais_master.md` — seção [9]

---

## GitHub

Repositório: `verticalpartsIA/developer_omie_com_br_service-list` (privado)  
README completo com mapeamento de todas as tabelas: https://github.com/verticalpartsIA/developer_omie_com_br_service-list

---

## O que será criado — ~90 tabelas em 7 módulos

### Módulo 1 — Geral
`clientes`, `clientes_caract`, `cliente_tags`, `projetos`, `empresas`, `departamentos`, `categorias`, `parcelas`, `tipos_atividade`, `cnae`, `cidades`, `paises`, `tipos_anexo`, `anexos`, `tipos_entrega`, `tipos_assinante`, `tarefas_geral`

### Módulo 2 — CRM
`crm_contas`, `crm_contas_caract`, `crm_contatos`, `crm_oportunidades`, `crm_oportunidades_resumo`, `crm_tarefas`, `crm_tarefas_resumo`, `crm_solucoes`, `crm_fases`, `crm_usuarios`, `crm_status`, `crm_motivos`, `crm_tipos`, `crm_parceiros`, `crm_origens`, `crm_concorrentes`, `crm_verticais`, `crm_tipos_tarefa`

### Módulo 3 — Finanças
`contas_correntes`, `contas_correntes_lancamentos`, `contas_pagar`, `contas_receber`, `contas_receber_boletos`, `pix`, `extrato`, `orcamento_caixa`, `titulos_pesquisa`, `movimentos_financeiros`, `bancos`, `tipos_documento`, `tipos_conta_corrente`, `contas_dre`, `finalidade_transferencia`, `origem_lancamento`, `bandeiras_cartao`

### Módulo 4 — Compras, Estoque e Produção
`produtos`, `produtos_caract`, `produtos_estrutura`, `produtos_kit`, `produtos_variacao`, `produtos_lote`, `requisicoes_compra`, `pedidos_compra`, `ordens_producao`, `notas_entrada`, `notas_entrada_fat`, `recebimento_nfe`, `familias_produto`, `unidades`, `compradores`, `produto_fornecedor`, `formas_pagamento_compras`, `ncm`, `cenarios_impostos`, `cfop`, `icms_cst`, `icms_csosn`, `icms_origem`, `pis_cst`, `cofins_cst`, `ipi_cst`, `ipi_enquadramento`, `tipo_calculo`, `cest`, `ajustes_estoque`, `consulta_estoque`, `movimento_estoque`, `locais_estoque`

### Módulo 5 — Vendas e NF-e
`pedidos_venda`, `pedidos_venda_resumo`, `pedidos_venda_fat`, `pedidos_venda_etapas`, `cte`, `remessa_produtos`, `remessa_fat`, `vendedores`, `formas_pagamento_vendas`, `tabela_precos`, `etapas_faturamento`, `meios_pagamento`, `origem_pedido`, `motivos_devolucao`

### Módulo 6 — Serviços e NFS-e
`servicos`, `ordens_servico`, `ordens_servico_fat`, `ordens_servico_lote`, `contratos_servico`, `contratos_fat`, `contratos_lote`, `servicos_municipio`, `tipos_tributacao`, `lc116`, `nbs`, `ibpt`, `contrato_tipo_fat`, `tipo_utilizacao`, `classificacao_servico`

### Módulo 7 — Painel do Contador
`documentos_fiscais_xml`

---

## Convenções de Schema

- Todas as tabelas em **snake_case** e em **português**
- Toda tabela inclui:
  ```sql
  id          UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  created_at  TIMESTAMPTZ DEFAULT NOW(),
  updated_at  TIMESTAMPTZ DEFAULT NOW()
  ```
- Campos originais do Omie mantêm os nomes originais da API (ex.: `codigo_cliente_omie`, `razao_social`, `nCodPedido`)
- RLS habilitada em todas as tabelas (`ALTER TABLE ... ENABLE ROW LEVEL SECURITY`)
- Migrations em SQL puro, organizadas por módulo, commitadas no GitHub

---

## Estratégia de Sincronização (ETL)

- Fonte: API REST do Omie — `https://app.omie.com.br/api/v1/`
- Credenciais Omie:
  ```
  Token:   8463170967
  API Key: 69e22b773842044fdb218178521cac59
  ```
- Sincronização: UPSERT por chave primária do Omie (ex.: `codigo_cliente_omie`) para evitar duplicatas
- Padrão de UPSERT:
  ```sql
  INSERT INTO tabela (...) VALUES (...)
  ON CONFLICT (codigo_omie) DO UPDATE SET ...
  ```

---

## Status das Migrations

| Módulo | Tabelas | Status |
|---|---|---|
| 1 — Geral | 17 | ✅ Aplicado em 2026-05-26 |
| 2 — CRM | 19 | ✅ Aplicado em 2026-05-26 |
| 3 — Finanças | 18 | ✅ Aplicado em 2026-05-26 |
| 4 — Compras/Estoque/Produção | 35 | ✅ Aplicado em 2026-05-26 |
| 5 — Vendas/NF-e | 23 | ✅ Aplicado em 2026-05-26 |
| 6 — Serviços/NFS-e | 18 | ✅ Aplicado em 2026-05-26 |
| 7 — Painel Contador | 2 | ✅ Aplicado em 2026-05-26 |

**Total: 132 tabelas criadas no Supabase**

## Estrutura das Migrations

```
migrations/
  000_trigger_updated_at.sql   — função trigger updated_at
  001_modulo_geral.sql         — 17 tabelas
  002_modulo_crm.sql           — 19 tabelas
  003_modulo_financas.sql      — 18 tabelas
  004_modulo_compras_estoque.sql — 35 tabelas
  005_modulo_vendas_nfe.sql    — 23 tabelas
  006_modulo_servicos_nfse.sql — 18 tabelas
  007_modulo_contador.sql      — 2 tabelas
```

## Padrão de cada tabela

- Chave primária Omie como coluna indexada (ex.: `codigo_cliente_omie BIGINT UNIQUE`)
- Colunas tipadas para os campos mais consultados
- `dados_raw JSONB` para armazenar a resposta completa da API
- `id UUID`, `created_at`, `updated_at` (com trigger automático)
- RLS habilitada em todas as tabelas (sem policies — acesso via service_role)
- UPSERT via `ON CONFLICT (codigo_omie) DO UPDATE SET ...`

---

*Criado em 2026-05-26 · Claude Sonnet 4.6 · VerticalParts*
