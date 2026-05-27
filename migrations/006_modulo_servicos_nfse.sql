-- =============================================================================
-- MÓDULO 6: SERVIÇOS E NFS-e
-- 18 tabelas
-- Endpoints: /servicos/servico/, /servicos/os/, /servicos/osp/,
--            /servicos/oslote/, /servicos/contrato/, /servicos/contratofat/,
--            /servicos/contratolote/, /servicos/resumo/, /servicos/osdocs/,
--            /servicos/nfse/, /servicos/listaservico/, /servicos/tipotrib/,
--            /servicos/lc116/, /servicos/nbs/, /servicos/ibpt/,
--            /servicos/contratotpfat/, /servicos/tipoutilizacao/,
--            /servicos/classificacaoservico/
-- =============================================================================

-- 6.1 Serviços
CREATE TABLE IF NOT EXISTS servicos (
  id                          UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  codigo_servico              BIGINT UNIQUE,
  codigo_servico_integracao   TEXT,
  descricao                   TEXT,
  codigo_nbs                  TEXT,
  codigo_lc116                TEXT,
  tributacao                  TEXT,
  aliquota_iss                NUMERIC(8,4),
  dados_raw                   JSONB DEFAULT '{}'::jsonb,
  created_at                  TIMESTAMPTZ DEFAULT NOW(),
  updated_at                  TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE servicos ENABLE ROW LEVEL SECURITY;
CREATE TRIGGER set_updated_at BEFORE UPDATE ON servicos
  FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();

-- 6.2 Ordens de Serviço
CREATE TABLE IF NOT EXISTS ordens_servico (
  id                    UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  numero_os             BIGINT UNIQUE,
  codigo_os_integracao  TEXT,
  codigo_cliente        BIGINT,
  data_previsao         DATE,
  status                TEXT,
  valor_total           NUMERIC(15,2),
  descricao             TEXT,
  dados_raw             JSONB DEFAULT '{}'::jsonb,
  created_at            TIMESTAMPTZ DEFAULT NOW(),
  updated_at            TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE ordens_servico ENABLE ROW LEVEL SECURITY;
CREATE INDEX IF NOT EXISTS idx_os_cliente ON ordens_servico(codigo_cliente);
CREATE INDEX IF NOT EXISTS idx_os_status  ON ordens_servico(status);
CREATE TRIGGER set_updated_at BEFORE UPDATE ON ordens_servico
  FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();

-- 6.3 Ordens de Serviço - Faturamento
CREATE TABLE IF NOT EXISTS ordens_servico_fat (
  id                  UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  numero_os           BIGINT UNIQUE,
  status_faturamento  TEXT,
  numero_nfse         TEXT,
  data_faturamento    DATE,
  dados_raw           JSONB DEFAULT '{}'::jsonb,
  created_at          TIMESTAMPTZ DEFAULT NOW(),
  updated_at          TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE ordens_servico_fat ENABLE ROW LEVEL SECURITY;
CREATE TRIGGER set_updated_at BEFORE UPDATE ON ordens_servico_fat
  FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();

-- 6.4 Ordens de Serviço - Faturamento em Lote
CREATE TABLE IF NOT EXISTS ordens_servico_lote (
  id                  UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  codigo_lote         BIGINT UNIQUE,
  total_os            INTEGER,
  status              TEXT,
  data_processamento  TIMESTAMPTZ,
  dados_raw           JSONB DEFAULT '{}'::jsonb,
  created_at          TIMESTAMPTZ DEFAULT NOW(),
  updated_at          TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE ordens_servico_lote ENABLE ROW LEVEL SECURITY;
CREATE TRIGGER set_updated_at BEFORE UPDATE ON ordens_servico_lote
  FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();

-- 6.5 Contratos de Serviço
CREATE TABLE IF NOT EXISTS contratos_servico (
  id                UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  codigo_contrato   BIGINT UNIQUE,
  codigo_cliente    BIGINT,
  descricao         TEXT,
  data_inicio       DATE,
  data_fim          DATE,
  valor_mensal      NUMERIC(15,2),
  status            TEXT,
  tipo_faturamento  TEXT,
  dados_raw         JSONB DEFAULT '{}'::jsonb,
  created_at        TIMESTAMPTZ DEFAULT NOW(),
  updated_at        TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE contratos_servico ENABLE ROW LEVEL SECURITY;
CREATE INDEX IF NOT EXISTS idx_cs_cliente ON contratos_servico(codigo_cliente);
CREATE TRIGGER set_updated_at BEFORE UPDATE ON contratos_servico
  FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();

-- 6.6 Contratos de Serviço - Faturamento
CREATE TABLE IF NOT EXISTS contratos_fat (
  id                UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  codigo_contrato   BIGINT,
  data_faturamento  DATE,
  numero_nfse       TEXT,
  valor             NUMERIC(15,2),
  status            TEXT,
  dados_raw         JSONB DEFAULT '{}'::jsonb,
  created_at        TIMESTAMPTZ DEFAULT NOW(),
  updated_at        TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE contratos_fat ENABLE ROW LEVEL SECURITY;
CREATE TRIGGER set_updated_at BEFORE UPDATE ON contratos_fat
  FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();

-- 6.7 Contratos de Serviço - Faturamento em Lote
CREATE TABLE IF NOT EXISTS contratos_lote (
  id                  UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  codigo_lote         BIGINT UNIQUE,
  total_contratos     INTEGER,
  status              TEXT,
  data_processamento  TIMESTAMPTZ,
  dados_raw           JSONB DEFAULT '{}'::jsonb,
  created_at          TIMESTAMPTZ DEFAULT NOW(),
  updated_at          TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE contratos_lote ENABLE ROW LEVEL SECURITY;
CREATE TRIGGER set_updated_at BEFORE UPDATE ON contratos_lote
  FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();

-- 6.8 Resumo de Serviços
CREATE TABLE IF NOT EXISTS servicos_resumo (
  id          UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  periodo     TEXT UNIQUE,
  total_os    INTEGER,
  valor_total NUMERIC(15,2),
  status      TEXT,
  dados_raw   JSONB DEFAULT '{}'::jsonb,
  created_at  TIMESTAMPTZ DEFAULT NOW(),
  updated_at  TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE servicos_resumo ENABLE ROW LEVEL SECURITY;
CREATE TRIGGER set_updated_at BEFORE UPDATE ON servicos_resumo
  FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();

-- 6.9 Documentos OS / NFS-e
CREATE TABLE IF NOT EXISTS os_docs (
  id              UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  numero_os       BIGINT,
  chave_nfse      TEXT UNIQUE,
  tipo_documento  TEXT,
  data_emissao    DATE,
  valor           NUMERIC(15,2),
  status          TEXT,
  dados_raw       JSONB DEFAULT '{}'::jsonb,
  created_at      TIMESTAMPTZ DEFAULT NOW(),
  updated_at      TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE os_docs ENABLE ROW LEVEL SECURITY;
CREATE TRIGGER set_updated_at BEFORE UPDATE ON os_docs
  FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();

-- 6.10 NFS-e Consultas
CREATE TABLE IF NOT EXISTS nfse_consultas (
  id                  UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  numero_nfse         TEXT,
  codigo_verificacao  TEXT,
  data_emissao        DATE,
  prestador           TEXT,
  tomador             TEXT,
  valor               NUMERIC(15,2),
  status              TEXT,
  municipio           TEXT,
  dados_raw           JSONB DEFAULT '{}'::jsonb,
  created_at          TIMESTAMPTZ DEFAULT NOW(),
  updated_at          TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(numero_nfse, municipio)
);
ALTER TABLE nfse_consultas ENABLE ROW LEVEL SECURITY;
CREATE TRIGGER set_updated_at BEFORE UPDATE ON nfse_consultas
  FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();

-- 6.11 Serviços no Município
CREATE TABLE IF NOT EXISTS servicos_municipio (
  id                        UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  codigo_municipio          TEXT,
  codigo_servico_municipio  TEXT,
  descricao                 TEXT,
  aliquota                  NUMERIC(8,4),
  dados_raw                 JSONB DEFAULT '{}'::jsonb,
  created_at                TIMESTAMPTZ DEFAULT NOW(),
  updated_at                TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(codigo_municipio, codigo_servico_municipio)
);
ALTER TABLE servicos_municipio ENABLE ROW LEVEL SECURITY;
CREATE TRIGGER set_updated_at BEFORE UPDATE ON servicos_municipio
  FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();

-- 6.12 Tipos de Tributação
CREATE TABLE IF NOT EXISTS tipos_tributacao (
  id          UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  codigo      TEXT UNIQUE,
  descricao   TEXT,
  dados_raw   JSONB DEFAULT '{}'::jsonb,
  created_at  TIMESTAMPTZ DEFAULT NOW(),
  updated_at  TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE tipos_tributacao ENABLE ROW LEVEL SECURITY;
CREATE TRIGGER set_updated_at BEFORE UPDATE ON tipos_tributacao
  FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();

-- 6.13 LC 116
CREATE TABLE IF NOT EXISTS lc116 (
  id            UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  codigo        TEXT UNIQUE,
  descricao     TEXT,
  sujeito_iss   TEXT,
  dados_raw     JSONB DEFAULT '{}'::jsonb,
  created_at    TIMESTAMPTZ DEFAULT NOW(),
  updated_at    TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE lc116 ENABLE ROW LEVEL SECURITY;
CREATE TRIGGER set_updated_at BEFORE UPDATE ON lc116
  FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();

-- 6.14 NBS
CREATE TABLE IF NOT EXISTS nbs (
  id          UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  codigo      TEXT UNIQUE,
  descricao   TEXT,
  dados_raw   JSONB DEFAULT '{}'::jsonb,
  created_at  TIMESTAMPTZ DEFAULT NOW(),
  updated_at  TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE nbs ENABLE ROW LEVEL SECURITY;
CREATE TRIGGER set_updated_at BEFORE UPDATE ON nbs
  FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();

-- 6.15 IBPT
CREATE TABLE IF NOT EXISTS ibpt (
  id                    UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  codigo_ncm_nbs        TEXT UNIQUE,
  descricao             TEXT,
  aliquota_nacional     NUMERIC(8,4),
  aliquota_importados   NUMERIC(8,4),
  aliquota_estadual     NUMERIC(8,4),
  aliquota_municipal    NUMERIC(8,4),
  dados_raw             JSONB DEFAULT '{}'::jsonb,
  created_at            TIMESTAMPTZ DEFAULT NOW(),
  updated_at            TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE ibpt ENABLE ROW LEVEL SECURITY;
CREATE TRIGGER set_updated_at BEFORE UPDATE ON ibpt
  FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();

-- 6.16 Tipo de Faturamento de Contrato
CREATE TABLE IF NOT EXISTS contrato_tipo_fat (
  id          UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  codigo      TEXT UNIQUE,
  descricao   TEXT,
  dados_raw   JSONB DEFAULT '{}'::jsonb,
  created_at  TIMESTAMPTZ DEFAULT NOW(),
  updated_at  TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE contrato_tipo_fat ENABLE ROW LEVEL SECURITY;
CREATE TRIGGER set_updated_at BEFORE UPDATE ON contrato_tipo_fat
  FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();

-- 6.17 Tipo de Utilização
CREATE TABLE IF NOT EXISTS tipo_utilizacao (
  id          UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  codigo      TEXT UNIQUE,
  descricao   TEXT,
  dados_raw   JSONB DEFAULT '{}'::jsonb,
  created_at  TIMESTAMPTZ DEFAULT NOW(),
  updated_at  TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE tipo_utilizacao ENABLE ROW LEVEL SECURITY;
CREATE TRIGGER set_updated_at BEFORE UPDATE ON tipo_utilizacao
  FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();

-- 6.18 Classificação do Serviço
CREATE TABLE IF NOT EXISTS classificacao_servico (
  id          UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  codigo      TEXT UNIQUE,
  descricao   TEXT,
  dados_raw   JSONB DEFAULT '{}'::jsonb,
  created_at  TIMESTAMPTZ DEFAULT NOW(),
  updated_at  TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE classificacao_servico ENABLE ROW LEVEL SECURITY;
CREATE TRIGGER set_updated_at BEFORE UPDATE ON classificacao_servico
  FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();
