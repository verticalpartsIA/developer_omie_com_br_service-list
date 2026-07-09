# Evolution API + Claude na VPS Hostinger — Guia de Integração para IA

> Este arquivo documenta um padrão de integração **WhatsApp (Evolution API) + Claude + VPS Hostinger** já em produção na VerticalParts, extraído por análise (somente leitura) do repositório [`verticalpartsIA/004_sac_posvenda360`](https://github.com/verticalpartsIA/004_sac_posvenda360) (projeto VP Pós-Venda 360°).
>
> Objetivo: qualquer IA (Claude ou outra) que precise implementar "WhatsApp com IA" em um novo projeto (ex.: vpsistema.com) pode usar este documento como referência de arquitetura, sem precisar reexplicar o padrão do zero.

---

## Visão geral da arquitetura

```
Cliente manda mensagem no WhatsApp
        │
        ▼
Evolution API (Docker, VPS Hostinger 72.61.48.156:8080)
   instância nomeada (ex.: "pv360")
        │  webhook "messages.upsert"
        ▼
App backend (Node/TanStack, hospedado na Hostinger)
   POST /api/webhook/evolution
        │
        ├─► grava mensagem recebida no Supabase (tabela de mensagens)
        ├─► cria/atualiza um "ticket"/thread vinculado ao número (se aplicável ao domínio)
        └─► dispara resposta automática (fire-and-forget, não bloqueia o 200 OK do webhook)
                 │
                 ▼
        Chamada direta à API Anthropic (sem SDK, fetch puro)
        POST https://api.anthropic.com/v1/messages
        headers: x-api-key, anthropic-version: 2023-06-01
        body: { model, max_tokens, system, messages: [...histórico] }
                 │
                 ▼
        Texto de resposta do Claude
                 │
                 ▼
        POST Evolution API — envia resposta de volta
        {EVOLUTION_URL}/message/sendText/{instancia}
                 │
                 ▼
        Cliente recebe a resposta no WhatsApp
        (a resposta também é salva no Supabase)
```

## Componentes

### 1. Evolution API (mensageria)
- Roda como container Docker na VPS (ex.: `atendai/evolution-api`), uma instância por número de WhatsApp conectado.
- Endpoints usados no fluxo:
  - `POST /message/sendText/{instancia}` — enviar texto (`{ "number": "<DDI+DDD+numero>", "text": "..." }`)
  - `GET /instance/connectionState/{instancia}` — checar se a instância está `open`/`close`/`connecting`
  - Webhook configurado na própria instância para `POST` cada evento `messages.upsert` recebido para uma URL do backend
- Autenticação via header `apikey` (mesmo valor tanto para chamar a Evolution quanto para validar o webhook recebido).
- Tipos de JID (identificador de contato) que a integração precisa tratar:
  - `numero@s.whatsapp.net` — contato normal
  - `numero@g.us` — grupo (geralmente ignorado para auto-resposta)
  - `numero@lid` — contato com "privacidade avançada" do WhatsApp; **a Evolution API não consegue enviar mensagens para `@lid` em algumas versões** — é preciso versão atualizada ou tratar como caso sem auto-resposta (encaminhar para atendimento humano).

### 2. Backend orquestrador (na VPS Hostinger)
- Recebe o webhook, extrai o corpo da mensagem (texto, ou marcador de mídia: imagem/vídeo/áudio/documento/sticker).
- Persiste tudo em uma tabela de mensagens no Supabase, com o JID, quem enviou (`from_me`), tipo de mídia e o payload bruto.
- Monta o histórico da conversa (ex.: últimas 20 mensagens) e alterna `user`/`assistant` para respeitar o formato exigido pela API Anthropic (mensagens consecutivas do mesmo papel precisam ser unidas; a primeira mensagem do array deve ser `user`).
- Chama a API Anthropic com um **system prompt fixo** definindo o papel do agente (ex.: atendente de pós-venda, tom, o que pode/não pode responder, o que fazer quando não souber).
- Envia a resposta de volta via Evolution API e persiste no banco.
- Um "kill switch" por variável de ambiente (ex.: `CLAUDE_AUTO_REPLY=true/false`) liga/desliga a auto-resposta sem precisar redeploy.

### 3. Variáveis de ambiente típicas
```
EVOLUTION_URL=http://<ip-da-vps>:8080
EVOLUTION_APIKEY=<chave da instância>
EVOLUTION_INSTANCE=<nome da instância>
ANTHROPIC_API_KEY=sk-ant-...
CLAUDE_MODEL=claude-haiku-4-5    # ou claude-sonnet-5 / claude-opus-4-8, conforme custo x qualidade
CLAUDE_AUTO_REPLY=true           # desliga com "false" sem precisar redeploy
```

### 4. Claude Code como agente de operação da VPS (uso diferente do chatbot)
Além do Claude-chatbot (item 2, chamado via API HTTP para gerar texto), existe um segundo padrão de uso: **Claude Code rodando com acesso a terminal dentro da própria VPS**, executando tarefas de infraestrutura (ex.: atualizar a imagem Docker da Evolution API, checar containers, fazer rollback). Isso é feito via um "runbook" em Markdown escrito para a IA seguir passo a passo (diagnóstico → backup → atualização → teste → rollback se necessário), citando explicitamente quais containers pode/não pode tocar (ex.: não mexer em `n8n`, `postgres`, `redis`, `traefik`, outros agentes de IA no mesmo host).

**Diferença importante para qualquer IA que for replicar este padrão:**
- *Claude-chatbot*: só recebe texto e devolve texto via API HTTPS — não tem acesso ao servidor.
- *Claude Code-operador*: tem acesso a shell/SSH na VPS e pode alterar infraestrutura — deve ser usado com escopo bem definido (o que pode e não pode tocar) e sempre com passo de diagnóstico/backup antes de qualquer mudança.

## Requisito de Banco de Dados (Supabase)

**Para que isso funcione você precisa criar no Supabase o seguinte:**

```sql
-- Caixa de entrada universal para eventos da Evolution API.
CREATE TABLE public.whatsapp_messages (
  id           UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
  instance     TEXT        NOT NULL DEFAULT 'pv360',
  remote_jid   TEXT        NOT NULL,                 -- ex.: 5511999887766@s.whatsapp.net
  push_name    TEXT,
  from_me      BOOLEAN     NOT NULL DEFAULT false,
  message_id   TEXT,
  body         TEXT        NOT NULL,
  media_type   TEXT,                                 -- image | video | audio | document | sticker
  media_url    TEXT,
  ticket_id    UUID        REFERENCES public.tickets(id) ON DELETE SET NULL,
  raw          JSONB,
  created_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_wa_msg_remote  ON public.whatsapp_messages(remote_jid, created_at DESC);
CREATE INDEX idx_wa_msg_ticket  ON public.whatsapp_messages(ticket_id);
ALTER TABLE public.whatsapp_messages ENABLE ROW LEVEL SECURITY;
CREATE POLICY "wa_msg_select" ON public.whatsapp_messages FOR SELECT TO authenticated USING (true);
-- INSERT é feito só pelo backend via service role (bypassa RLS) — sem policy de insert para anon/authenticated.

-- Tabela de tickets (mínimo exigido pela integração; o projeto de origem tem colunas adicionais de domínio)
CREATE TABLE public.tickets (
  id                 UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  customer           TEXT NOT NULL,
  part               TEXT NOT NULL,
  part_code          TEXT NOT NULL,
  reason             TEXT NOT NULL,
  occurrence_reason  TEXT NOT NULL DEFAULT 'outro',
  channel            TEXT NOT NULL DEFAULT 'whatsapp',
  whatsapp_thread_id TEXT,
  status             TEXT NOT NULL DEFAULT 'aberto', -- aberto | em_atendimento | aguardando_cliente | aguardando_interno | concluido | cancelado
  created_by         UUID REFERENCES auth.users(id) ON DELETE SET NULL,
  assigned_to        UUID REFERENCES auth.users(id) ON DELETE SET NULL,
  created_at         TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at         TIMESTAMPTZ NOT NULL DEFAULT now()
);
ALTER TABLE public.tickets ENABLE ROW LEVEL SECURITY;
```

> ⚠️ **Dependência não resolvida encontrada na análise:** o código de auto-resposta (`claude-reply.ts`) consulta `whatsapp_messages` filtrando por uma coluna `phone` (`.eq("phone", phone)`) que **não existe em nenhuma migration rastreada** no repositório de origem — é provavelmente uma coluna gerada (`GENERATED ALWAYS AS`) criada manualmente direto no Supabase, fora do controle de versão. **Antes de replicar este padrão em outro projeto, verifique e recrie essa coluna explicitamente** (ex.: `phone TEXT GENERATED ALWAYS AS (regexp_replace(remote_jid, '@.*$', '')) STORED`), em vez de assumir que ela existe.

## Checklist para replicar em um novo projeto (ex.: vpsistema.com)
1. Subir uma instância Evolution API (Docker) na VPS de destino, ou reutilizar uma existente com uma nova instância nomeada.
2. Configurar o webhook da instância apontando para um endpoint do novo projeto.
3. Implementar o endpoint de webhook: validar `apikey`, extrair mensagem, persistir, responder `200 OK` rápido (não esperar a resposta da IA).
4. Implementar a chamada à API Anthropic com um system prompt específico do domínio do novo projeto.
5. Implementar o envio de volta via `POST /message/sendText/{instancia}`.
6. Definir uma variável de "kill switch" para ligar/desligar auto-resposta.
7. Tratar o caso `@lid` (sem auto-resposta automática, ou validar se a versão da Evolution já suporta).
8. **Nunca commitar chaves reais** (`ANTHROPIC_API_KEY`, chave da Evolution, service role do Supabase) no código — usar variáveis de ambiente/secrets.

## Referência
Repositório de origem desta documentação (análise realizada em 2026-07-09): https://github.com/verticalpartsIA/004_sac_posvenda360
