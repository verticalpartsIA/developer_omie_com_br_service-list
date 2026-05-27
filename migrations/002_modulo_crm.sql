-- =============================================================================
-- MÓDULO 2: CRM
-- 19 tabelas
-- Endpoints: /crm/contas/, /crm/contascaract/, /crm/contatos/,
--            /crm/oportunidades/, /crm/oportunidades-resumo/,
--            /crm/tarefas/, /crm/tarefas-resumo/, /crm/solucoes/,
--            /crm/fases/, /crm/usuarios/, /crm/status/, /crm/motivos/,
--            /crm/tipos/, /crm/parceiros/, /crm/finders/, /crm/origens/,
--            /crm/concorrentes/, /crm/verticais/, /crm/tipostarefa/
-- =============================================================================

-- 2.1 Contas CRM
CREATE TABLE IF NOT EXISTS crm_contas (
  id            UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  codigo_conta  BIGINT UNIQUE,
  nome          TEXT,
  email         TEXT,
  telefone      TEXT,
  cnpj_cpf      TEXT,
  tipo          TEXT,
  status        TEXT,
  dados_raw     JSONB DEFAULT '{}'::jsonb,
  created_at    TIMESTAMPTZ DEFAULT NOW(),
  updated_at    TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE crm_contas ENABLE ROW LEVEL SECURITY;
CREATE INDEX IF NOT EXISTS idx_crm_contas_codigo ON crm_contas(codigo_conta);
CREATE TRIGGER set_updated_at BEFORE UPDATE ON crm_contas
  FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();

-- 2.2 Contas - Características
CREATE TABLE IF NOT EXISTS crm_contas_caract (
  id              UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  codigo_conta    BIGINT,
  codigo_caract   BIGINT,
  descricao       TEXT,
  valor           TEXT,
  dados_raw       JSONB DEFAULT '{}'::jsonb,
  created_at      TIMESTAMPTZ DEFAULT NOW(),
  updated_at      TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(codigo_conta, codigo_caract)
);
ALTER TABLE crm_contas_caract ENABLE ROW LEVEL SECURITY;
CREATE TRIGGER set_updated_at BEFORE UPDATE ON crm_contas_caract
  FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();

-- 2.3 Contatos
CREATE TABLE IF NOT EXISTS crm_contatos (
  id              UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  codigo_contato  BIGINT UNIQUE,
  nome            TEXT,
  email           TEXT,
  telefone        TEXT,
  cargo           TEXT,
  codigo_conta    BIGINT,
  dados_raw       JSONB DEFAULT '{}'::jsonb,
  created_at      TIMESTAMPTZ DEFAULT NOW(),
  updated_at      TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE crm_contatos ENABLE ROW LEVEL SECURITY;
CREATE INDEX IF NOT EXISTS idx_crm_contatos_conta ON crm_contatos(codigo_conta);
CREATE TRIGGER set_updated_at BEFORE UPDATE ON crm_contatos
  FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();

-- 2.4 Oportunidades
CREATE TABLE IF NOT EXISTS crm_oportunidades (
  id                    UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  codigo_oportunidade   BIGINT UNIQUE,
  titulo                TEXT,
  valor                 NUMERIC(15,2),
  codigo_fase           BIGINT,
  codigo_status         BIGINT,
  codigo_conta          BIGINT,
  data_previsao         DATE,
  dados_raw             JSONB DEFAULT '{}'::jsonb,
  created_at            TIMESTAMPTZ DEFAULT NOW(),
  updated_at            TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE crm_oportunidades ENABLE ROW LEVEL SECURITY;
CREATE INDEX IF NOT EXISTS idx_crm_op_conta ON crm_oportunidades(codigo_conta);
CREATE TRIGGER set_updated_at BEFORE UPDATE ON crm_oportunidades
  FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();

-- 2.5 Oportunidades - Resumo
CREATE TABLE IF NOT EXISTS crm_oportunidades_resumo (
  id                    UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  codigo_fase           BIGINT UNIQUE,
  descricao_fase        TEXT,
  total_oportunidades   INTEGER,
  valor_total           NUMERIC(15,2),
  dados_raw             JSONB DEFAULT '{}'::jsonb,
  created_at            TIMESTAMPTZ DEFAULT NOW(),
  updated_at            TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE crm_oportunidades_resumo ENABLE ROW LEVEL SECURITY;
CREATE TRIGGER set_updated_at BEFORE UPDATE ON crm_oportunidades_resumo
  FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();

-- 2.6 Tarefas CRM
CREATE TABLE IF NOT EXISTS crm_tarefas (
  id              UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  codigo_tarefa   BIGINT UNIQUE,
  assunto         TEXT,
  descricao       TEXT,
  status          TEXT,
  data_prazo      DATE,
  responsavel     TEXT,
  codigo_conta    BIGINT,
  dados_raw       JSONB DEFAULT '{}'::jsonb,
  created_at      TIMESTAMPTZ DEFAULT NOW(),
  updated_at      TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE crm_tarefas ENABLE ROW LEVEL SECURITY;
CREATE TRIGGER set_updated_at BEFORE UPDATE ON crm_tarefas
  FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();

-- 2.7 Tarefas CRM - Resumo
CREATE TABLE IF NOT EXISTS crm_tarefas_resumo (
  id          UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  status      TEXT UNIQUE,
  total       INTEGER,
  valor       NUMERIC(15,2),
  dados_raw   JSONB DEFAULT '{}'::jsonb,
  created_at  TIMESTAMPTZ DEFAULT NOW(),
  updated_at  TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE crm_tarefas_resumo ENABLE ROW LEVEL SECURITY;
CREATE TRIGGER set_updated_at BEFORE UPDATE ON crm_tarefas_resumo
  FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();

-- 2.8 Soluções
CREATE TABLE IF NOT EXISTS crm_solucoes (
  id          UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  codigo      BIGINT UNIQUE,
  descricao   TEXT,
  dados_raw   JSONB DEFAULT '{}'::jsonb,
  created_at  TIMESTAMPTZ DEFAULT NOW(),
  updated_at  TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE crm_solucoes ENABLE ROW LEVEL SECURITY;
CREATE TRIGGER set_updated_at BEFORE UPDATE ON crm_solucoes
  FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();

-- 2.9 Fases
CREATE TABLE IF NOT EXISTS crm_fases (
  id          UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  codigo      BIGINT UNIQUE,
  descricao   TEXT,
  ordem       INTEGER,
  percentual  NUMERIC(5,2),
  dados_raw   JSONB DEFAULT '{}'::jsonb,
  created_at  TIMESTAMPTZ DEFAULT NOW(),
  updated_at  TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE crm_fases ENABLE ROW LEVEL SECURITY;
CREATE TRIGGER set_updated_at BEFORE UPDATE ON crm_fases
  FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();

-- 2.10 Usuários CRM (Vendedores / Telemarketing / Pré-Vendas compartilham o mesmo endpoint)
CREATE TABLE IF NOT EXISTS crm_usuarios (
  id          UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  codigo      BIGINT UNIQUE,
  nome        TEXT,
  email       TEXT,
  tipo        TEXT,
  inativo     TEXT,
  dados_raw   JSONB DEFAULT '{}'::jsonb,
  created_at  TIMESTAMPTZ DEFAULT NOW(),
  updated_at  TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE crm_usuarios ENABLE ROW LEVEL SECURITY;
CREATE TRIGGER set_updated_at BEFORE UPDATE ON crm_usuarios
  FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();

-- 2.11 Status CRM
CREATE TABLE IF NOT EXISTS crm_status (
  id          UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  codigo      BIGINT UNIQUE,
  descricao   TEXT,
  tipo        TEXT,
  dados_raw   JSONB DEFAULT '{}'::jsonb,
  created_at  TIMESTAMPTZ DEFAULT NOW(),
  updated_at  TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE crm_status ENABLE ROW LEVEL SECURITY;
CREATE TRIGGER set_updated_at BEFORE UPDATE ON crm_status
  FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();

-- 2.12 Motivos CRM
CREATE TABLE IF NOT EXISTS crm_motivos (
  id          UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  codigo      BIGINT UNIQUE,
  descricao   TEXT,
  tipo        TEXT,
  dados_raw   JSONB DEFAULT '{}'::jsonb,
  created_at  TIMESTAMPTZ DEFAULT NOW(),
  updated_at  TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE crm_motivos ENABLE ROW LEVEL SECURITY;
CREATE TRIGGER set_updated_at BEFORE UPDATE ON crm_motivos
  FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();

-- 2.13 Tipos CRM
CREATE TABLE IF NOT EXISTS crm_tipos (
  id          UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  codigo      BIGINT UNIQUE,
  descricao   TEXT,
  dados_raw   JSONB DEFAULT '{}'::jsonb,
  created_at  TIMESTAMPTZ DEFAULT NOW(),
  updated_at  TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE crm_tipos ENABLE ROW LEVEL SECURITY;
CREATE TRIGGER set_updated_at BEFORE UPDATE ON crm_tipos
  FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();

-- 2.14 Parceiros
CREATE TABLE IF NOT EXISTS crm_parceiros (
  id          UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  codigo      BIGINT UNIQUE,
  descricao   TEXT,
  dados_raw   JSONB DEFAULT '{}'::jsonb,
  created_at  TIMESTAMPTZ DEFAULT NOW(),
  updated_at  TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE crm_parceiros ENABLE ROW LEVEL SECURITY;
CREATE TRIGGER set_updated_at BEFORE UPDATE ON crm_parceiros
  FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();

-- 2.15 Finders (novo — não estava no plano original)
CREATE TABLE IF NOT EXISTS crm_finders (
  id          UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  codigo      BIGINT UNIQUE,
  descricao   TEXT,
  dados_raw   JSONB DEFAULT '{}'::jsonb,
  created_at  TIMESTAMPTZ DEFAULT NOW(),
  updated_at  TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE crm_finders ENABLE ROW LEVEL SECURITY;
CREATE TRIGGER set_updated_at BEFORE UPDATE ON crm_finders
  FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();

-- 2.16 Origens CRM
CREATE TABLE IF NOT EXISTS crm_origens (
  id          UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  codigo      BIGINT UNIQUE,
  descricao   TEXT,
  dados_raw   JSONB DEFAULT '{}'::jsonb,
  created_at  TIMESTAMPTZ DEFAULT NOW(),
  updated_at  TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE crm_origens ENABLE ROW LEVEL SECURITY;
CREATE TRIGGER set_updated_at BEFORE UPDATE ON crm_origens
  FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();

-- 2.17 Concorrentes
CREATE TABLE IF NOT EXISTS crm_concorrentes (
  id          UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  codigo      BIGINT UNIQUE,
  descricao   TEXT,
  dados_raw   JSONB DEFAULT '{}'::jsonb,
  created_at  TIMESTAMPTZ DEFAULT NOW(),
  updated_at  TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE crm_concorrentes ENABLE ROW LEVEL SECURITY;
CREATE TRIGGER set_updated_at BEFORE UPDATE ON crm_concorrentes
  FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();

-- 2.18 Verticais
CREATE TABLE IF NOT EXISTS crm_verticais (
  id          UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  codigo      BIGINT UNIQUE,
  descricao   TEXT,
  dados_raw   JSONB DEFAULT '{}'::jsonb,
  created_at  TIMESTAMPTZ DEFAULT NOW(),
  updated_at  TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE crm_verticais ENABLE ROW LEVEL SECURITY;
CREATE TRIGGER set_updated_at BEFORE UPDATE ON crm_verticais
  FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();

-- 2.19 Tipos de Tarefas CRM
CREATE TABLE IF NOT EXISTS crm_tipos_tarefa (
  id          UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  codigo      BIGINT UNIQUE,
  descricao   TEXT,
  dados_raw   JSONB DEFAULT '{}'::jsonb,
  created_at  TIMESTAMPTZ DEFAULT NOW(),
  updated_at  TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE crm_tipos_tarefa ENABLE ROW LEVEL SECURITY;
CREATE TRIGGER set_updated_at BEFORE UPDATE ON crm_tipos_tarefa
  FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();
