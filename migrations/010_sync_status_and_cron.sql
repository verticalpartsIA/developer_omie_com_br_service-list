-- ============================================================
-- 010_sync_status_and_cron
-- Tabela de controle de sincronização + jobs pg_cron horários
-- ============================================================

-- ── Tabela _sync_status ──────────────────────────────────────
CREATE TABLE IF NOT EXISTS _sync_status (
    table_name   TEXT        PRIMARY KEY,
    last_sync_at TIMESTAMPTZ,
    last_count   INTEGER,
    status       TEXT,        -- 'ok' | 'api_unavailable' | 'sem_dados'
    created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

ALTER TABLE _sync_status ENABLE ROW LEVEL SECURITY;

CREATE TRIGGER set_updated_at
    BEFORE UPDATE ON _sync_status
    FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();

-- ── Habilitar extensão pg_cron ───────────────────────────────
-- (já habilitada no Supabase por padrão — só garante)
CREATE EXTENSION IF NOT EXISTS pg_cron;

-- ── Remover jobs antigos (idempotente) ───────────────────────
SELECT cron.unschedule(jobname)
FROM cron.job
WHERE jobname LIKE 'sync-omie-m%';

-- ── Criar 7 jobs pg_cron — um por módulo, distribuídos na hora ─
-- Módulo 1 – Geral                  → XX:00
SELECT cron.schedule(
    'sync-omie-m1',
    '0 * * * *',
    $$
    SELECT net.http_post(
        url     := current_setting('app.supabase_url') || '/functions/v1/sync-omie',
        headers := jsonb_build_object(
            'Content-Type',  'application/json',
            'Authorization', 'Bearer ' || current_setting('app.service_role_key')
        ),
        body    := '{"modulo":1}'::jsonb
    );
    $$
);

-- Módulo 2 – CRM                    → XX:10
SELECT cron.schedule(
    'sync-omie-m2',
    '10 * * * *',
    $$
    SELECT net.http_post(
        url     := current_setting('app.supabase_url') || '/functions/v1/sync-omie',
        headers := jsonb_build_object(
            'Content-Type',  'application/json',
            'Authorization', 'Bearer ' || current_setting('app.service_role_key')
        ),
        body    := '{"modulo":2}'::jsonb
    );
    $$
);

-- Módulo 3 – Financeiro             → XX:20
SELECT cron.schedule(
    'sync-omie-m3',
    '20 * * * *',
    $$
    SELECT net.http_post(
        url     := current_setting('app.supabase_url') || '/functions/v1/sync-omie',
        headers := jsonb_build_object(
            'Content-Type',  'application/json',
            'Authorization', 'Bearer ' || current_setting('app.service_role_key')
        ),
        body    := '{"modulo":3}'::jsonb
    );
    $$
);

-- Módulo 4 – Produtos & Estoque     → XX:30
SELECT cron.schedule(
    'sync-omie-m4',
    '30 * * * *',
    $$
    SELECT net.http_post(
        url     := current_setting('app.supabase_url') || '/functions/v1/sync-omie',
        headers := jsonb_build_object(
            'Content-Type',  'application/json',
            'Authorization', 'Bearer ' || current_setting('app.service_role_key')
        ),
        body    := '{"modulo":4}'::jsonb
    );
    $$
);

-- Módulo 5 – Vendas & NF-e          → XX:40
SELECT cron.schedule(
    'sync-omie-m5',
    '40 * * * *',
    $$
    SELECT net.http_post(
        url     := current_setting('app.supabase_url') || '/functions/v1/sync-omie',
        headers := jsonb_build_object(
            'Content-Type',  'application/json',
            'Authorization', 'Bearer ' || current_setting('app.service_role_key')
        ),
        body    := '{"modulo":5}'::jsonb
    );
    $$
);

-- Módulo 6 – Serviços & NFS-e       → XX:50
SELECT cron.schedule(
    'sync-omie-m6',
    '50 * * * *',
    $$
    SELECT net.http_post(
        url     := current_setting('app.supabase_url') || '/functions/v1/sync-omie',
        headers := jsonb_build_object(
            'Content-Type',  'application/json',
            'Authorization', 'Bearer ' || current_setting('app.service_role_key')
        ),
        body    := '{"modulo":6}'::jsonb
    );
    $$
);

-- Módulo 7 – Painel do Contador     → XX:55
SELECT cron.schedule(
    'sync-omie-m7',
    '55 * * * *',
    $$
    SELECT net.http_post(
        url     := current_setting('app.supabase_url') || '/functions/v1/sync-omie',
        headers := jsonb_build_object(
            'Content-Type',  'application/json',
            'Authorization', 'Bearer ' || current_setting('app.service_role_key')
        ),
        body    := '{"modulo":7}'::jsonb
    );
    $$
);
