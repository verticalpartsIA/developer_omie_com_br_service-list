# Relatório Diário Agendado via Telegram (Cron Determinístico) — Guia para IA

> Documenta o padrão de automação do **Borderô Financeiro diário** da VerticalParts: um job de cron que roda em dias úteis, coleta dados reais do Omie + Supabase, gera um PDF e envia via Telegram — **sem depender de nenhuma IA/LLM em tempo de execução**. Extraído por análise (somente leitura, incluindo o histórico de Issues) do repositório [`verticalpartsIA/008_BorderoDiario`](https://github.com/verticalpartsIA/008_BorderoDiario).

---

## Visão geral da arquitetura

```
Cron na VPS (crontab, timezone UTC)
   0 9 * * 1-5  → 09:00 UTC = 06:00 BRT, segunda a sexta
        │
        ▼
run_cron.sh (wrapper bash)
   - loga início/fim em cron.log
   - chama gerar_bordero.py --enviar gelson,diego
   - rede de segurança: se o .py morrer ANTES do seu próprio alerta interno,
     o bash ainda dispara um aviso de falha via Telegram (dupla camada de alerta)
        │
        ▼
gerar_bordero.py (determinístico — 100% Python + APIs, zero IA)
   1. calcula o "dia útil anterior" (pula sábado/domingo — NÃO considera feriados)
   2. Omie REST API (ListarMovimentos, ListarContasCorrentes) via curl direto
   3. Supabase — lê a tabela já mirrorada `omie_nfe_emitidas` via API de
      Management do Supabase (não é o client REST/anon normal)
   4. aplica regras de negócio: exclui contas Bepay/Devoluções (não são caixa
      real), consolida duplicidade "título aparece 2x" da API do Omie
   5. renderiza HTML → PDF (wkhtmltopdf + xvfb-run, precisa de X virtual)
   6. envia o PDF a cada destinatário via Telegram Bot API (sendDocument)
        │
        ▼
Falha em qualquer etapa → captura exceção → Telegram (mensagem de texto de alerta)
   para o chat_id do responsável, ANTES de propagar o erro (falha nunca é silenciosa)
```

## Por que "determinístico" é uma decisão de arquitetura deliberada
O próprio código comenta: *"NÃO depende de Claude nem do Hermes"* ("Hermes" é o agente de IA / "CFO digital" da VerticalParts, documentado em outras partes deste mesmo repositório de origem). Ou seja: para um relatório financeiro que roda todo dia útil e precisa de exatidão numérica, a equipe **optou por lógica determinística pura** em vez de deixar uma IA calcular/formatar os números — a IA (Hermes) aparece só como "marca" no rodapé do PDF, não participa do cálculo. **Esta é uma distinção de design importante ao decidir se um novo relatório agendado deve ou não envolver um LLM**: cálculos financeiros → determinístico; texto livre/resumo/interpretação → IA é aceitável.

## Componentes técnicos

### 1. Agendamento
- `crontab`: `CRON_TZ=UTC` + `0 9 * * 1-5` — fuso do cron fixado em UTC explicitamente para não depender do fuso do SO, com o offset para BRT (-3h) calculado manualmente na expressão (09:00 UTC = 06:00 BRT).
- **Regra de dia útil vem em duas camadas**: (a) o cron já só dispara seg-sex (`1-5`); (b) dentro do script, `dia_util_anterior()` calcula o dia de referência andando para trás e pulando sábado/domingo — necessário porque o relatório de **segunda-feira** deve mostrar dados de **sexta-feira**, não de domingo.
- **Limitação conhecida**: a lógica só pula fins de semana, não feriados nacionais/municipais — um feriado numa terça-feira, por exemplo, ainda geraria o relatório normalmente (possível melhoria futura).

### 2. Coleta de dados — duas fontes, dois protocolos diferentes
- **Omie**: chamadas HTTP diretas via `curl` (sem SDK), aos endpoints `financas/mf` (ListarMovimentos) e `geral/contacorrente` (ListarContasCorrentes) — mesmas APIs já mapeadas no repositório de conhecimento Omie deste projeto.
- **Supabase**: em vez do client REST/PostgREST padrão (anon/service key), o script usa a **API de Management do Supabase** (`https://api.supabase.com/v1/projects/{ref}/database/query`) autenticada com um **Personal Access Token (PAT)** — executa SQL bruto diretamente. Isso dá acesso total ao banco (equivalente a um superusuário de leitura/escrita via API), mais amplo do que o necessário para uma leitura simples — vale registrar como ponto de atenção de segurança (mesmo padrão de "escopo maior que o necessário" já visto no token GitHub org-wide).

### 3. Regras de negócio críticas (para não errar o número)
- **Deduplicação**: a API do Omie retorna cada título financeiro **duas vezes** (uma linha para o título, outra para a baixa/liquidação) — o script consolida por `nCodTitulo`, somando apenas as baixas efetivas, para não contar em dobro.
- **Isolamento de contas não-caixa-real**: contas correntes cujo nome contém "BEPAY" ou "DEVOLU" são excluídas do cálculo de recebido/pago — são fluxos internos, não caixa de fato.
- **Sem posição de caixa/saldo bancário** ainda (bloqueado por falta de conciliação bancária no Omie — ver achado histórico abaixo).

### 4. Geração e entrega
- HTML (com CSS inline, identidade visual VerticalParts) → PDF via `wkhtmltopdf` rodando sob `xvfb-run` (X virtual framebuffer — `wkhtmltopdf` precisa de um display mesmo headless).
- Envio via Telegram Bot API, método `sendDocument`, um `chat_id` por destinatário (mapa fixo `{gelson, diego}` no script — adicionar destinatário = adicionar entrada no dicionário + variável de ambiente).

### 5. Tratamento de falha (dupla camada)
- Dentro do Python: `try/except` em volta de `run()`; em caso de exceção, chama `alerta_falha()` que manda mensagem de texto ao Telegram do responsável **antes** de re-lançar a exceção (para o cron registrar exit code != 0).
- Dentro do bash (`run_cron.sh`): se o processo Python morrer de um jeito que nem o próprio alerta interno dispare, o wrapper bash extrai o token/chat direto do `.env` e manda um alerta de fallback. **Nunca fica em falha silenciosa.**

## Achados históricos relevantes (via leitura integral das Issues do repositório de origem)
| Issue | Tema | Status observado |
|---|---|---|
| [#2](https://github.com/verticalpartsIA/008_BorderoDiario/issues/2) | Incidente 04/06/2026: repositório ficou público momentaneamente com o **token do bot Telegram exposto** em texto (`hermes/telegram-setup.md`), presente em 33 commits do histórico git | **Aberta, checklist não concluído** — token pode ainda não ter sido rotacionado/histórico não limpo |
| [#4](https://github.com/verticalpartsIA/008_BorderoDiario/issues/4) | Scripts de produção existiam só na VPS, sem versionamento — risco de perda por falha de disco/`rm` acidental | Em andamento — este próprio repositório é o resultado dessa ação |
| [#5](https://github.com/verticalpartsIA/008_BorderoDiario/issues/5) | Borderô ainda não mostra saldo bancário real — bloqueado por conciliação bancária pendente no Omie | Aberta, bloqueada por dependência externa |
| [#6](https://github.com/verticalpartsIA/008_BorderoDiario/issues/6) | CFOP 5.917 (remessa por conta/ordem de terceiros) não está na lista de exclusão e pode estar inflando o faturamento reportado | Aberta — decisão de regra de negócio pendente |
| [#7](https://github.com/verticalpartsIA/008_BorderoDiario/issues/7) | Um cliente apareceu 4× com mesmo Doc/NF e valor no relatório — suspeita de duplicação real no Omie (não no script) | Aberta — apurar se é duplicidade genuína |

**Lição de arquitetura destas issues**: (a) nunca versionar segredo em texto plano, nem em arquivos de "setup"/documentação — o vazamento aqui não foi no código do bot, foi num `.md` de instruções; (b) um relatório determinístico ainda depende de **dados de origem corretos** — os bugs reais encontrados (#6, #7) estavam no Omie/CFOP, não no script, mas só foram descobertos *porque* o relatório expôs o número todo dia.

## Requisito de Banco de Dados (Supabase)

**Não precisa de Banco de Dados "Supabase" adicional** — este fluxo não cria nem exige nenhuma tabela nova. Ele **lê uma tabela já existente** (`omie_nfe_emitidas`, no projeto Supabase do mirror do Omie) via SQL direto pela API de Management. Não há tabela de controle de "estado de envio" (o script não registra se já enviou hoje — reexecutar manualmente no mesmo dia reenvia o PDF, não há trava de idempotência a nível de banco). Log de execução é só o arquivo texto `cron.log` na VPS, não uma tabela.

> ⚠️ **Cross-referência com o resto deste repositório**: a tabela `omie_nfe_emitidas` (dados de NF-e emitidas) já existe e está em uso em produção neste fluxo — porém a [issue #7 (Vendas e NF-e)](https://github.com/verticalpartsIA/developer_omie_com_br_service-list/issues/7) deste mesmo repositório de conhecimento listou "Importar/Consultar NF-e" como **gap não coberto** no espelho Omie↔Supabase. Ou seja: existe pelo menos uma tabela de NF-e em produção que não foi capturada no mapeamento original — recomenda-se revisitar a issue #7 e reconciliar com o schema real de `omie_nfe_emitidas`.

## Checklist para replicar em outro relatório agendado
1. Definir se o cálculo deve ser determinístico (financeiro/numérico) ou pode envolver IA (texto livre) — não misturar as duas responsabilidades no mesmo script.
2. Fixar o cron em UTC explicitamente e calcular o offset manualmente na expressão, documentando o horário local esperado.
3. Se o "dia de referência" for "o dia útil anterior", implementar a lógica no próprio script (o cron só filtra dia da semana, não sabe de feriados) — e documentar a limitação de feriados não cobertos.
4. Usar credenciais com o **menor escopo necessário** para a fonte de dados (evitar Personal Access Tokens de management/admin quando uma leitura simples via client padrão resolveria).
5. Implementar alerta de falha em pelo menos duas camadas (dentro do script + no wrapper que o invoca), sempre indo para um canal que alguém realmente monitora (aqui: Telegram pessoal do responsável).
6. Documentar e isolar regras de negócio de deduplicação/exclusão de dados no início do pipeline, com comentários explicando o *porquê* (ex.: "a API retorna 2x", "Bepay não é caixa real") — essas regras são fonte comum de bugs sutis.
7. Nunca colocar token/segredo em arquivo de documentação/instrução (`.md`) — mesmo fora do `.env`, esse tipo de arquivo é o que mais vaza (ver achado histórico #2 acima).

## Referência
Repositório de origem desta documentação (análise realizada em 2026-07-09, incluindo leitura integral das 7 Issues abertas): https://github.com/verticalpartsIA/008_BorderoDiario — `script/gerar_bordero.py`, `script/run_cron.sh`, `script/README.md`.
