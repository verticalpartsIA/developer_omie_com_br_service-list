# ETL Omie → Supabase

## Arquivos

| Arquivo | Descrição |
|---------|-----------|
| `sync_omie_v2.py` | **ETL principal** — lê MD, classifica 500 métodos, sincroniza |
| `sync_omie.py` | ETL legado (schema antigo, substituído pelo v2) |

---

## Categorias de tabela

| Categoria | Prefixos de método | Ação ETL |
|-----------|-------------------|----------|
| **LISTAR_SYNC** | `Listar*`, `Pesquisar*` | ✅ Sync paginado automático |
| **OBTER_TRY** | `Obter*`, `Consultar*`, `Get*` | 🔄 Tenta sem ID; pula se exigir código |
| **WRITE_OP** | `Incluir*`, `Alterar*`, `Upsert*`, `Faturar*`, etc. | ✏️ Populada pela app ao executar operação |
| **SKIP** | `Excluir*`, `Cancelar*` | 🚫 **Nunca chamadas** (destrutivas) |

> **Por que WRITE_OP não é sincronizado?**
> Métodos como `IncluirCliente`, `AlterarPedido`, `FaturarOS` são **operações de escrita** — eles modificam dados no Omie. Chamá-los automaticamente sem dados reais causaria erros ou alterações indesejadas. Essas tabelas ficam como **log operacional**: cada vez que sua aplicação executa uma operação, registra a resposta nelas.

> **Por que SKIP (Excluir/Cancelar)?**
> São operações **destrutivas e irreversíveis**. Chamá-las automaticamente poderia excluir dados reais da conta Omie. Nunca são executadas pelo ETL.

---

## Como usar

### Primeira execução (popula tudo)
```bash
cd etl
python sync_omie_v2.py
```

### Re-sincronização completa (limpa e repopula)
```bash
python sync_omie_v2.py --fresh
```

### Só módulo 1 (Geral)
```bash
python sync_omie_v2.py --modulo 1
```

### Só tabelas Listar/Pesquisar
```bash
python sync_omie_v2.py --categoria LISTAR_SYNC
```

### Só tabelas que contêm "clientes"
```bash
python sync_omie_v2.py --tabela clientes
```

### Ver plano sem executar nada
```bash
python sync_omie_v2.py --listar-plano
python sync_omie_v2.py --dry-run
```

---

## Agendamento

### Windows — Task Scheduler
```bat
# diario_sync.bat
cd /d C:\Users\gelso\Projetos_Sites\developer_omie_com_br_service-list\etl
python sync_omie_v2.py >> logs\cron.log 2>&1
```

### Linux/Mac — Cron (exemplo diário às 3h)
```cron
0 3 * * * cd /path/to/etl && python sync_omie_v2.py >> logs/cron.log 2>&1
```

---

## Limites da API Omie respeitados

| Limite | Valor | Como respeitamos |
|--------|-------|-----------------|
| Total req/min por IP | 960 | `SLEEP_BETWEEN = 0.35s` → ~170 req/min |
| Req/min por IP+App+Método | 240 | Uma tabela por vez (serializado) |
| Simultâneas por IP+App+Método | 4 | Sempre 1 requisição ativa |
| Registros por página | 500 | `PAGE_SIZE = 500` |

---

## Logs

Cada execução gera um arquivo JSON em `etl/logs/`:
```
etl/logs/sync_20260527_030000.json
```

Contém resultado por tabela: status, registros buscados, inseridos.

---

## Variáveis de ambiente (produção)

Para não hardcodar credenciais:
```bash
export OMIE_APP_KEY=8463170967
export OMIE_APP_SECRET=69e22b773842044fdb218178521cac59
export SUPABASE_URL=https://hrhwplqlbuwfextznkea.supabase.co
export SUPABASE_KEY=eyJhbG...
```
