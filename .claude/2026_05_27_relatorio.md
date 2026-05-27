# Relatório de Trabalho — 27/05/2026

**Projeto:** `developer_omie_com_br_service-list`  
**Repo:** https://github.com/verticalpartsIA/developer_omie_com_br_service-list  
**Supabase:** https://hrhwplqlbuwfextznkea.supabase.co  

---

## 1. Migrações aplicadas no Supabase

### Módulo 5 — Vendas e NF-e (`migrations/009_m5.sql`)
- **129 tabelas** criadas (5.1.x até 5.32.x)
- Migration aplicada como `009_m5_vendas_nfe`

### Módulo 6 — Serviços e NFS-e (`migrations/009_m6.sql`)
- **66 tabelas** criadas (6.1.x até 6.21.x)
- Migration aplicada como `009_m6_servicos_nfse`

### Módulo 7 — Painel do Contador (`migrations/009_m7.sql`)
- **2 tabelas** criadas (7.1.1 e 7.2.1)
- Migration aplicada como `009_m7_painel_contador`

### Total de tabelas no Supabase
```
500 tabelas — confirmado via: SELECT COUNT(*) FROM pg_stat_user_tables
```

---

## 2. ETL Python — `etl/sync_omie_v2.py`

Script completo criado do zero para sincronizar a API Omie → Supabase.

### Classificação das 500 tabelas

| Categoria | Qtd | Comportamento |
|-----------|-----|---------------|
| `LISTAR_SYNC` | 138 | Sync paginado automático |
| `OBTER_TRY` | 93 | Tenta sem ID; pula se exigir código |
| `WRITE_OP` | 205 | Populada pela app ao executar operação |
| `SKIP` | 64 | **Nunca chamadas** (Excluir/Cancelar — destrutivas) |

### Flags CLI disponíveis
```bash
python -X utf8 sync_omie_v2.py                      # sync completo
python -X utf8 sync_omie_v2.py --fresh              # limpa e repopula
python -X utf8 sync_omie_v2.py --modulo 1           # só módulo 1
python -X utf8 sync_omie_v2.py --categoria LISTAR_SYNC
python -X utf8 sync_omie_v2.py --tabela clientes
python -X utf8 sync_omie_v2.py --dry-run
python -X utf8 sync_omie_v2.py --listar-plano
```

### Configurações de rate limit respeitadas
| Parâmetro | Valor |
|-----------|-------|
| `SLEEP_BETWEEN` | `0.35s` → ~170 req/min |
| `SLEEP_RATE_LIMIT` | `65s` (aguarda em caso de 429) |
| `MAX_RETRIES` | `3` com backoff exponencial (2^n) |
| `PAGE_SIZE` | `500` registros/página |

### Documentação: `etl/README_ETL.md`
Criado com explicações de categorias, uso, agendamento e variáveis de ambiente.

---

## 3. Execução do ETL — Módulo 1 (LISTAR_SYNC)

**Comando executado:**
```bash
python -X utf8 sync_omie_v2.py --modulo 1 --categoria LISTAR_SYNC
```

**Resultado (639 segundos):**

| Tabela | Registros |
|--------|----------:|
| `1.1.7. ListarClientes` | 14.377 |
| `1.1.8. ListarClientesResumido` | 14.377 |
| `1.11.1. PesquisarCidades` | 5.734 |
| `1.10.1. ListarCNAE` | 4.291 |
| `1.7.6. ListarCategorias` | 347 |
| `1.8.2. ListarParcelas` | 220 |
| `1.4.5. ListarProjetos` | 108 |
| `1.6.5. ListarDepartamentos` | 26 |
| `1.6.6. ListarDepatartamentos` | 26 |
| `1.16.1. ListarTipoAssinante` | 6 |
| `1.5.2. ListarEmpresas` | 1 |

**7 endpoints com HTTP 500** (indisponíveis nesta conta Omie):
- `ListarTags`, `ListarTipoAtiv`, `ListarPaises`, `ListarTiposAnexos`, `ListarAnexo`, `ListarTipoEntrega`, `ListarTarefas`

---

## 4. Execução do ETL — Módulos 2+ (LISTAR_SYNC em background)

**Comando em execução:**
```bash
python -X utf8 sync_omie_v2.py --categoria LISTAR_SYNC
```

Tabelas populadas enquanto esta sessão ocorria:

| Tabela | Registros |
|--------|----------:|
| `2.1.5. ListarContas` | 15.490 |
| `2.3.5. ListarContatos` | 12.451 |
| `2.4.5. ListarOportunidades` | ~19.900 (em andamento) |

---

## 5. Edge Function — `sync-omie` (Deno)

### Arquivo
```
supabase/functions/sync-omie/index.ts
```

### Deploy
- **Versão:** 2
- **Status:** ACTIVE
- **verify_jwt:** true
- **URL:** `https://hrhwplqlbuwfextznkea.supabase.co/functions/v1/sync-omie`

### Lógica incremental (sem re-sync desnecessário)
1. Chama página 1 da Omie → obtém `total_de_registros`
2. Compara com `COUNT(*)` no Supabase
3. Se Supabase ≥ Omie → **skip** (zero chamadas adicionais)
4. Se Omie > Supabase → busca todas as páginas e faz `INSERT`
5. Atualiza `_sync_status` com timestamp e contagem
6. Budget de tempo: **110s** por invocação (limite Edge Function = 150s)

### Uso manual
```bash
# Sincronizar módulo 2 (CRM)
curl -X POST https://hrhwplqlbuwfextznkea.supabase.co/functions/v1/sync-omie \
  -H "Authorization: Bearer <SERVICE_ROLE_KEY>" \
  -H "Content-Type: application/json" \
  -d '{"modulo": 2}'

# Sincronizar todos os módulos
curl -X POST https://hrhwplqlbuwfextznkea.supabase.co/functions/v1/sync-omie \
  -H "Authorization: Bearer <SERVICE_ROLE_KEY>" \
  -H "Content-Type: application/json" \
  -d '{}'
```

---

## 6. Agendamento automático — pg_cron (7 jobs)

### Migration aplicada
```
migrations/010_sync_status_and_cron.sql
```

### Jobs criados no Supabase

| Job | Cron | Módulo | Tabelas |
|-----|------|--------|---------|
| `sync-omie-m1` | `0 * * * *` (XX:00) | 1 — Geral | 18 |
| `sync-omie-m2` | `10 * * * *` (XX:10) | 2 — CRM | 20 |
| `sync-omie-m3` | `20 * * * *` (XX:20) | 3 — Financeiro | 18 |
| `sync-omie-m4` | `30 * * * *` (XX:30) | 4 — Produtos & Estoque | 35 |
| `sync-omie-m5` | `40 * * * *` (XX:40) | 5 — Vendas & NF-e | 24 |
| `sync-omie-m6` | `50 * * * *` (XX:50) | 6 — Serviços & NFS-e | 21 |
| `sync-omie-m7` | `55 * * * *` (XX:55) | 7 — Painel do Contador | 1 |

**Status de todos os jobs:** `active = true` ✅

### Como verificar execuções passadas
```sql
SELECT jobname, start_time, end_time, status, return_message
FROM cron.job_run_details
WHERE jobname LIKE 'sync-omie-m%'
ORDER BY start_time DESC
LIMIT 20;
```

---

## 7. Tabela `_sync_status` (controle de sincronização)

### Migration aplicada como `010_sync_status`

```sql
-- Ver status de sincronização por tabela
SELECT table_name, last_sync_at, last_count, status
FROM _sync_status
ORDER BY last_sync_at DESC;
```

---

## 8. Estrutura de arquivos criados/modificados hoje

```
developer_omie_com_br_service-list/
├── migrations/
│   ├── 009_m5.sql                  ← CRIADO — 129 tabelas Vendas/NF-e
│   ├── 009_m6.sql                  ← CRIADO — 66 tabelas Serviços/NFS-e
│   ├── 009_m7.sql                  ← CRIADO — 2 tabelas Contador
│   └── 010_sync_status_and_cron.sql← CRIADO — _sync_status + pg_cron
├── etl/
│   ├── sync_omie_v2.py             ← CRIADO — ETL principal (500 tabelas)
│   ├── README_ETL.md               ← CRIADO — Documentação ETL
│   └── logs/
│       └── sync_20260527_*.json    ← GERADO — Log da execução
├── supabase/
│   └── functions/
│       └── sync-omie/
│           └── index.ts            ← CRIADO — Edge Function Deno
└── .claude/
    └── 2026_05_27_relatorio.md     ← ESTE ARQUIVO
```

---

## 9. Tabelas com dados disponíveis para consulta (fim do dia)

```sql
SELECT relname AS tabela, n_live_tup AS registros
FROM pg_stat_user_tables
WHERE n_live_tup > 0
ORDER BY n_live_tup DESC;
```

| Tabela | Registros |
|--------|----------:|
| `2.1.5. ListarContas` | 15.490 |
| `1.1.7. ListarClientes` | 14.377 |
| `1.1.8. ListarClientesResumido` | 14.377 |
| `2.3.5. ListarContatos` | 12.451 |
| `1.11.1. PesquisarCidades` | 5.734 |
| `1.10.1. ListarCNAE` | 4.291 |
| `1.7.6. ListarCategorias` | 347 |
| `1.8.2. ListarParcelas` | 220 |
| `1.4.5. ListarProjetos` | 108 |
| `1.6.5. ListarDepartamentos` | 26 |
| `1.6.6. ListarDepatartamentos` | 26 |
| `1.16.1. ListarTipoAssinante` | 6 |
| `1.5.2. ListarEmpresas` | 1 |

---

## 10. Pendências / Próximos passos

- [ ] Aguardar conclusão do ETL Python em background (módulos 2–7 LISTAR_SYNC)
- [ ] Rodar `OBTER_TRY` (93 tabelas — Obter*/Consultar*/Get*)
- [ ] Investigar 7 endpoints com HTTP 500 persistente (podem precisar de params específicos)
- [ ] Monitorar primeiras execuções automáticas do pg_cron (toda hora)
- [ ] Verificar `_sync_status` após primeiro ciclo automático

---

*Gerado automaticamente por Claude — Sessão de 27/05/2026*
