-- Chaves de acesso para o servidor MCP remoto (conector do Claude).
create table if not exists public.mcp_api_keys (
  id uuid primary key default gen_random_uuid(),
  label text not null,
  token_hash text not null unique,
  created_at timestamp with time zone not null default now(),
  last_used_at timestamp with time zone,
  active boolean not null default true
);
alter table public.mcp_api_keys enable row level security;
grant select, insert, update, delete on public.mcp_api_keys to service_role;

-- Credenciais do Omie ERP (App Key / App Secret), usadas pela Edge Function
-- para chamar a API real do Omie. Nunca expostas ao Claude nem a nenhum cliente.
create table if not exists public.omie_credentials (
  id uuid primary key default gen_random_uuid(),
  label text not null,
  app_key text not null,
  app_secret text not null,
  active boolean not null default true,
  created_at timestamp with time zone not null default now()
);
alter table public.omie_credentials enable row level security;
grant select, insert, update, delete on public.omie_credentials to service_role;

-- Log de auditoria de toda chamada de escrita real feita no Omie via MCP.
create table if not exists public.omie_write_audit_log (
  id uuid primary key default gen_random_uuid(),
  endpoint text not null,
  chamada text not null,
  parametros jsonb,
  sucesso boolean not null,
  resultado jsonb,
  criado_em timestamp with time zone not null default now()
);
alter table public.omie_write_audit_log enable row level security;
grant select, insert, update, delete on public.omie_write_audit_log to service_role;
