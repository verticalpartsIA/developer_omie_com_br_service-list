# Formulário Público via Token + Envio por WhatsApp — Guia de Integração para IA

> Documenta um padrão de arquitetura em produção na VerticalParts: **envio de um link de formulário via WhatsApp, preenchimento público sem login, e captura estruturada das respostas**. Extraído por análise (somente leitura) do **Módulo 7 (M7) — Quadro de Comando** do repositório [`verticalpartsIA/003_requisicoes`](https://github.com/verticalpartsIA/003_requisicoes).
>
> Este padrão reutiliza o mesmo gateway WhatsApp (Evolution API) já documentado em [`evolution-whatsapp-claude-vps.md`](evolution-whatsapp-claude-vps.md) — a diferença é o **uso**: ali é conversa livre com auto-resposta por Claude; aqui é o **envio de um link transacional único** (o formulário), sem IA na conversa.

---

## Visão geral da arquitetura

```
Vendedor (painel autenticado, RLS)
   cria um "pedido" em rascunho (dados do cliente + projeto)
        │
        ▼
Vendedor marca como "enviado" → gera token único + expiração (7 dias)
        │
        ├─► Opção A: enviarWhatsAppComando() — server function com service role
        │            chama Evolution API (POST /message/sendText/{instancia})
        │            e manda a mensagem automaticamente para o cliente
        │
        └─► Opção B: wa.me/{numero}?text=... — abre o WhatsApp Web/app do
                     próprio vendedor com a mensagem pré-preenchida (fallback manual)
        │
        ▼
Cliente recebe o link https://.../pedido-comando/{token} no WhatsApp
        │
        ▼
Página pública (sem login) — acesso validado só pelo token
   - valida token: existe? expirou? já foi respondido?
   - ao abrir: marca status "visualizado" + grava evento de auditoria (IP, user-agent)
   - formulário multi-seção (dados técnicos do domínio) + upload de anexos (fotos/PDF)
        │
        ▼
Cliente envia respostas → grava JSONB livre + status "respondido"
        │
        ▼
Vendedor acompanha no painel interno (autenticado) e pode "reabrir" se precisar
que o cliente altere algo (gera nova expiração)
```

## Componentes técnicos

### 1. Modelagem de dados (3 tabelas)
- **`{modulo}_pedidos`** — cabeçalho do formulário: `token` (único, gerado com `gen_random_bytes`), `status` (`rascunho` → `enviado` → `visualizado` → `respondido`, reabrível), dados do cliente, `respostas jsonb` (schema livre — permite adicionar campos ao formulário sem migração), `expires_at`.
- **`{modulo}_anexos`** — arquivos enviados pelo cliente (fotos, PDF), referenciando um bucket privado do Supabase Storage.
- **`{modulo}_auditoria`** — trilha de eventos (`criado`/`enviado`/`visualizado`/`respondido`/`reaberto`) com IP e user-agent, para rastreabilidade de quando o cliente de fato abriu/respondeu.

### 2. Duas superfícies de acesso distintas
- **Painel interno (autenticado, RLS `to authenticated`)**: vendedor cria, lista, marca como enviado, reabre. Usa a sessão Supabase normal do usuário logado.
- **Página pública (sem login, token na URL)**: todo acesso é via *server functions* que usam a **service role** (bypassa RLS) e validam manualmuente o token, expiração e status antes de qualquer leitura/escrita. Não existe policy de `anon` nas tabelas — o token é o único controle de acesso, aplicado em código, não no banco.

### 3. Envio do link por WhatsApp — duas opções
```ts
// Opção A — envio automático via gateway Evolution (mesmo padrão do chatbot)
POST {EVOLUTION_URL}/message/sendText/{instancia}
headers: { apikey }
body: { number: "55DDDNUMERO", text: mensagem }

// Opção B — fallback manual, abre o WhatsApp do próprio vendedor
https://wa.me/{numero}?text={mensagem-url-encoded}
```
A opção B é útil como *fallback* quando não se quer depender do gateway automático, ou para dar ao vendedor controle manual do envio.

### 4. Upload de anexos sem login
O cliente (sem sessão) envia arquivo em base64 para uma server function, que:
1. valida token/expiração/status,
2. decodifica e checa tamanho máximo,
3. sobe para um bucket privado (`storage/v1/object/{bucket}`) usando service role,
4. grava metadados (`file_path`, `file_name`, `mime_type`) na tabela de anexos.

Bucket configurado como **privado** (`public: false`), com `allowed_mime_types` restrito (ex.: `image/jpeg`, `image/png`, `image/webp`, `application/pdf`) e limite de tamanho (ex.: 10MB). Leitura só para usuários autenticados — o lado público nunca lê o bucket diretamente, só escreve via server function.

## Requisito de Banco de Dados (Supabase)

**Para que isso funcione você precisa criar no Supabase o seguinte** (schema real do M7, use como template trocando o prefixo `comando_` pelo domínio novo):

```sql
create extension if not exists pgcrypto;

create type public.comando_pedido_status as enum ('rascunho','enviado','visualizado','respondido');

create sequence if not exists public.comando_pedidos_numero_seq;

create or replace function public.gerar_token_comando() returns text
language sql volatile as $$ select encode(gen_random_bytes(24), 'hex'); $$;

create table public.comando_pedidos (
  id uuid primary key default gen_random_uuid(),
  numero_documento text not null unique,
  token text not null unique default public.gerar_token_comando(),
  status public.comando_pedido_status not null default 'rascunho',
  cliente_nome text not null,
  cliente_telefone text not null,
  cliente_email text,
  projeto_numero text,
  observacoes_internas text,
  respostas jsonb not null default '{}'::jsonb,
  requisition_id uuid references public.requisitions(id) on delete set null,
  created_by uuid references auth.users(id) on delete set null,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  enviado_at timestamptz, enviado_by uuid references auth.users(id) on delete set null,
  visualizado_at timestamptz,
  respondido_at timestamptz,
  expires_at timestamptz,
  reaberto_at timestamptz, reaberto_by uuid references auth.users(id) on delete set null
);
create index comando_pedidos_status_idx on public.comando_pedidos (status);
create index comando_pedidos_token_idx on public.comando_pedidos (token);

create table public.comando_anexos (
  id uuid primary key default gen_random_uuid(),
  pedido_id uuid not null references public.comando_pedidos(id) on delete cascade,
  secao text,
  file_path text not null,
  file_name text not null,
  file_size bigint,
  mime_type text,
  created_at timestamptz not null default now()
);

create table public.comando_auditoria (
  id uuid primary key default gen_random_uuid(),
  pedido_id uuid not null references public.comando_pedidos(id) on delete cascade,
  evento text not null, -- criado | enviado | visualizado | respondido | reaberto
  ip text,
  user_agent text,
  created_at timestamptz not null default now()
);

alter table public.comando_pedidos enable row level security;
alter table public.comando_anexos enable row level security;
alter table public.comando_auditoria enable row level security;
create policy comando_pedidos_authenticated_all on public.comando_pedidos for all to authenticated using (true) with check (true);
create policy comando_anexos_authenticated_all on public.comando_anexos for all to authenticated using (true) with check (true);
create policy comando_auditoria_authenticated_all on public.comando_auditoria for all to authenticated using (true) with check (true);
-- Acesso público (sem login) é 100% via server function com service role — não há policy de "anon" de propósito.

-- Bucket privado para anexos
insert into storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
values ('comando-anexos', 'comando-anexos', false, 10485760, array['image/jpeg','image/png','image/webp','application/pdf'])
on conflict (id) do nothing;
create policy "Authenticated users can read comando anexos" on storage.objects for select to authenticated using (bucket_id = 'comando-anexos');
```

> Nota: `comando_pedidos.requisition_id` referencia `public.requisitions(id)`, uma tabela própria do domínio de origem (requisições de compra). Ao replicar em outro projeto, remova essa FK ou aponte para a tabela equivalente do novo domínio — ela não faz parte do padrão genérico.

## Checklist para replicar em um novo formulário/domínio
1. Criar as 3 tabelas (`pedidos`/`anexos`/`auditoria`) trocando o prefixo pelo domínio novo.
2. Gerar token único (`gen_random_bytes` + `encode(..., 'hex')`) e numeração de documento própria (sequence + prefixo).
3. Implementar server functions com service role para: buscar por token (+ marcar visualizado), enviar respostas (+ marcar respondido, bloquear reenvio), upload/remoção de anexo.
4. Implementar página pública `/{caminho}/$token` sem exigir sessão — toda validação de acesso é feita nas server functions, nunca confiar em RLS de `anon`.
5. Implementar as duas opções de envio de WhatsApp (gateway automático + `wa.me` manual).
6. Definir janela de expiração do link (ex.: 7 dias) e lógica de "reabrir" para permitir nova resposta.
7. Registrar cada evento relevante (visualizado/respondido/reaberto) numa tabela de auditoria com IP/user-agent.

## Referência
Repositório de origem desta documentação (análise realizada em 2026-07-09): https://github.com/verticalpartsIA/003_requisicoes (Módulo 7 — Quadro de Comando).
Ver também: [evolution-whatsapp-claude-vps.md](evolution-whatsapp-claude-vps.md) para o gateway WhatsApp compartilhado.
