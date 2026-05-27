-- =============================================================================
-- MÓDULO 1: GERAL
-- 17 tabelas
-- Endpoints: /geral/clientes/, /geral/clientescaract/, /geral/clientetag/,
--            /geral/projetos/, /geral/empresas/, /geral/departamentos/,
--            /geral/categorias/, /geral/parcelas/, /geral/tpativ/,
--            /produtos/cnae/, /geral/cidades/, /geral/paises/,
--            /geral/tiposanexo/, /geral/anexo/, /geral/tiposentrega/,
--            /geral/tipoassinante/, /geral/tarefas/
-- =============================================================================

-- 1.1 Clientes, Fornecedores, Transportadoras
CREATE TABLE IF NOT EXISTS clientes (
  id                          UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  codigo_cliente_omie         BIGINT UNIQUE,
  codigo_cliente_integracao   TEXT,
  razao_social                TEXT,
  cnpj_cpf                    TEXT,
  nome_fantasia               TEXT,
  email                       TEXT,
  telefone1_ddd               TEXT,
  telefone1_numero            TEXT,
  endereco                    TEXT,
  endereco_numero             TEXT,
  bairro                      TEXT,
  complemento                 TEXT,
  estado                      TEXT,
  cidade                      TEXT,
  cep                         TEXT,
  pais                        TEXT,
  pessoa_fisica               TEXT,
  inativo                     TEXT,
  bloqueado                   TEXT,
  tipo_atividade              TEXT,
  cnae                        TEXT,
  tags_json                   JSONB DEFAULT '[]'::jsonb,
  dados_raw                   JSONB DEFAULT '{}'::jsonb,
  created_at                  TIMESTAMPTZ DEFAULT NOW(),
  updated_at                  TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE clientes ENABLE ROW LEVEL SECURITY;
CREATE INDEX IF NOT EXISTS idx_clientes_codigo_omie ON clientes(codigo_cliente_omie);
CREATE INDEX IF NOT EXISTS idx_clientes_cnpj       ON clientes(cnpj_cpf);
CREATE INDEX IF NOT EXISTS idx_clientes_estado     ON clientes(estado);
CREATE TRIGGER set_updated_at BEFORE UPDATE ON clientes
  FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();

-- 1.2 Clientes - Características
CREATE TABLE IF NOT EXISTS clientes_caract (
  id                    UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  codigo_cliente_omie   BIGINT,
  cCaractItem           TEXT,
  cCaractDescricao      TEXT,
  cCaractValor          TEXT,
  dados_raw             JSONB DEFAULT '{}'::jsonb,
  created_at            TIMESTAMPTZ DEFAULT NOW(),
  updated_at            TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(codigo_cliente_omie, cCaractItem)
);
ALTER TABLE clientes_caract ENABLE ROW LEVEL SECURITY;
CREATE INDEX IF NOT EXISTS idx_clientes_caract_codigo ON clientes_caract(codigo_cliente_omie);
CREATE TRIGGER set_updated_at BEFORE UPDATE ON clientes_caract
  FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();

-- 1.3 Tags de Clientes
CREATE TABLE IF NOT EXISTS cliente_tags (
  id          UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  codigo      BIGINT UNIQUE,
  descricao   TEXT,
  dados_raw   JSONB DEFAULT '{}'::jsonb,
  created_at  TIMESTAMPTZ DEFAULT NOW(),
  updated_at  TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE cliente_tags ENABLE ROW LEVEL SECURITY;
CREATE TRIGGER set_updated_at BEFORE UPDATE ON cliente_tags
  FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();

-- 1.4 Projetos
CREATE TABLE IF NOT EXISTS projetos (
  id              UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  codigo_projeto  BIGINT UNIQUE,
  descricao       TEXT,
  inativo         TEXT,
  dados_raw       JSONB DEFAULT '{}'::jsonb,
  created_at      TIMESTAMPTZ DEFAULT NOW(),
  updated_at      TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE projetos ENABLE ROW LEVEL SECURITY;
CREATE TRIGGER set_updated_at BEFORE UPDATE ON projetos
  FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();

-- 1.5 Empresas
CREATE TABLE IF NOT EXISTS empresas (
  id              UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  codigo_empresa  BIGINT UNIQUE,
  razao_social    TEXT,
  cnpj            TEXT,
  fantasia        TEXT,
  endereco        TEXT,
  cidade          TEXT,
  estado          TEXT,
  dados_raw       JSONB DEFAULT '{}'::jsonb,
  created_at      TIMESTAMPTZ DEFAULT NOW(),
  updated_at      TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE empresas ENABLE ROW LEVEL SECURITY;
CREATE TRIGGER set_updated_at BEFORE UPDATE ON empresas
  FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();

-- 1.6 Departamentos
CREATE TABLE IF NOT EXISTS departamentos (
  id          UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  codigo      TEXT UNIQUE,
  descricao   TEXT,
  inativo     TEXT,
  estrutura   TEXT,
  dados_raw   JSONB DEFAULT '{}'::jsonb,
  created_at  TIMESTAMPTZ DEFAULT NOW(),
  updated_at  TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE departamentos ENABLE ROW LEVEL SECURITY;
CREATE TRIGGER set_updated_at BEFORE UPDATE ON departamentos
  FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();

-- 1.7 Categorias
CREATE TABLE IF NOT EXISTS categorias (
  id          UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  codigo      TEXT UNIQUE,
  descricao   TEXT,
  inativo     TEXT,
  dados_raw   JSONB DEFAULT '{}'::jsonb,
  created_at  TIMESTAMPTZ DEFAULT NOW(),
  updated_at  TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE categorias ENABLE ROW LEVEL SECURITY;
CREATE TRIGGER set_updated_at BEFORE UPDATE ON categorias
  FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();

-- 1.8 Parcelas
CREATE TABLE IF NOT EXISTS parcelas (
  id              UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  codigo          TEXT UNIQUE,
  descricao       TEXT,
  qtde_parcelas   INTEGER,
  tipo_boleto     TEXT,
  dados_raw       JSONB DEFAULT '{}'::jsonb,
  created_at      TIMESTAMPTZ DEFAULT NOW(),
  updated_at      TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE parcelas ENABLE ROW LEVEL SECURITY;
CREATE TRIGGER set_updated_at BEFORE UPDATE ON parcelas
  FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();

-- 1.9 Tipos de Atividade
CREATE TABLE IF NOT EXISTS tipos_atividade (
  id          UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  codigo      TEXT UNIQUE,
  descricao   TEXT,
  dados_raw   JSONB DEFAULT '{}'::jsonb,
  created_at  TIMESTAMPTZ DEFAULT NOW(),
  updated_at  TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE tipos_atividade ENABLE ROW LEVEL SECURITY;
CREATE TRIGGER set_updated_at BEFORE UPDATE ON tipos_atividade
  FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();

-- 1.10 CNAE
CREATE TABLE IF NOT EXISTS cnae (
  id          UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  codigo      TEXT UNIQUE,
  descricao   TEXT,
  dados_raw   JSONB DEFAULT '{}'::jsonb,
  created_at  TIMESTAMPTZ DEFAULT NOW(),
  updated_at  TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE cnae ENABLE ROW LEVEL SECURITY;
CREATE TRIGGER set_updated_at BEFORE UPDATE ON cnae
  FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();

-- 1.11 Cidades
CREATE TABLE IF NOT EXISTS cidades (
  id                    UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  codigo_municipio_ibge TEXT UNIQUE,
  nome                  TEXT,
  estado                TEXT,
  estado_ibge           TEXT,
  dados_raw             JSONB DEFAULT '{}'::jsonb,
  created_at            TIMESTAMPTZ DEFAULT NOW(),
  updated_at            TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE cidades ENABLE ROW LEVEL SECURITY;
CREATE INDEX IF NOT EXISTS idx_cidades_estado ON cidades(estado);
CREATE TRIGGER set_updated_at BEFORE UPDATE ON cidades
  FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();

-- 1.12 Países
CREATE TABLE IF NOT EXISTS paises (
  id          UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  codigo      TEXT UNIQUE,
  descricao   TEXT,
  dados_raw   JSONB DEFAULT '{}'::jsonb,
  created_at  TIMESTAMPTZ DEFAULT NOW(),
  updated_at  TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE paises ENABLE ROW LEVEL SECURITY;
CREATE TRIGGER set_updated_at BEFORE UPDATE ON paises
  FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();

-- 1.13 Tipos de Anexos
CREATE TABLE IF NOT EXISTS tipos_anexo (
  id          UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  codigo      TEXT UNIQUE,
  descricao   TEXT,
  dados_raw   JSONB DEFAULT '{}'::jsonb,
  created_at  TIMESTAMPTZ DEFAULT NOW(),
  updated_at  TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE tipos_anexo ENABLE ROW LEVEL SECURITY;
CREATE TRIGGER set_updated_at BEFORE UPDATE ON tipos_anexo
  FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();

-- 1.14 Documentos Anexos
CREATE TABLE IF NOT EXISTS anexos (
  id          UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  cEntidade   TEXT,
  cTabela     TEXT,
  nCodigo     BIGINT,
  cNome       TEXT,
  cDescricao  TEXT,
  cTipo       TEXT,
  cMimeType   TEXT,
  cHash       TEXT,
  cUrl        TEXT,
  dados_raw   JSONB DEFAULT '{}'::jsonb,
  created_at  TIMESTAMPTZ DEFAULT NOW(),
  updated_at  TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE anexos ENABLE ROW LEVEL SECURITY;
CREATE INDEX IF NOT EXISTS idx_anexos_entidade ON anexos(cEntidade, nCodigo);
CREATE TRIGGER set_updated_at BEFORE UPDATE ON anexos
  FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();

-- 1.15 Tipo de Entrega
CREATE TABLE IF NOT EXISTS tipos_entrega (
  id          UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  codigo      TEXT UNIQUE,
  descricao   TEXT,
  dados_raw   JSONB DEFAULT '{}'::jsonb,
  created_at  TIMESTAMPTZ DEFAULT NOW(),
  updated_at  TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE tipos_entrega ENABLE ROW LEVEL SECURITY;
CREATE TRIGGER set_updated_at BEFORE UPDATE ON tipos_entrega
  FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();

-- 1.16 Tipo de Assinante
CREATE TABLE IF NOT EXISTS tipos_assinante (
  id          UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  codigo      TEXT UNIQUE,
  descricao   TEXT,
  dados_raw   JSONB DEFAULT '{}'::jsonb,
  created_at  TIMESTAMPTZ DEFAULT NOW(),
  updated_at  TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE tipos_assinante ENABLE ROW LEVEL SECURITY;
CREATE TRIGGER set_updated_at BEFORE UPDATE ON tipos_assinante
  FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();

-- 1.17 Tarefas (Geral)
CREATE TABLE IF NOT EXISTS tarefas_geral (
  id            UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  nCodigo       BIGINT UNIQUE,
  cAssunto      TEXT,
  cDescricao    TEXT,
  cStatus       TEXT,
  dPrazo        DATE,
  cResponsavel  TEXT,
  nCodCliente   BIGINT,
  nCodProjeto   BIGINT,
  dados_raw     JSONB DEFAULT '{}'::jsonb,
  created_at    TIMESTAMPTZ DEFAULT NOW(),
  updated_at    TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE tarefas_geral ENABLE ROW LEVEL SECURITY;
CREATE TRIGGER set_updated_at BEFORE UPDATE ON tarefas_geral
  FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();
