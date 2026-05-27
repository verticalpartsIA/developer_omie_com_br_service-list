-- =============================================================================
-- MÓDULO 3: FINANÇAS
-- 18 tabelas
-- Endpoints: /geral/contacorrente/, /financas/contacorrentelancamentos/,
--            /financas/contapagar/, /financas/contareceber/,
--            /financas/contareceberboleto/, /financas/pix/,
--            /financas/extrato/, /financas/caixa/, /financas/pesquisartitulos/,
--            /financas/mf/, /financas/resumo/, /geral/bancos/,
--            /geral/tiposdoc/, /geral/tipocc/, /geral/dre/,
--            /geral/finaltransf/, /geral/origemlancamento/, /geral/bandeiracartao/
-- =============================================================================

-- 3.1 Contas Correntes
CREATE TABLE IF NOT EXISTS contas_correntes (
  id                      UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  codigo_conta_corrente   BIGINT UNIQUE,
  descricao               TEXT,
  tipo                    TEXT,
  codigo_banco            TEXT,
  agencia                 TEXT,
  conta                   TEXT,
  saldo_inicial           NUMERIC(15,2),
  inativo                 TEXT,
  dados_raw               JSONB DEFAULT '{}'::jsonb,
  created_at              TIMESTAMPTZ DEFAULT NOW(),
  updated_at              TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE contas_correntes ENABLE ROW LEVEL SECURITY;
CREATE TRIGGER set_updated_at BEFORE UPDATE ON contas_correntes
  FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();

-- 3.2 Contas Correntes - Lançamentos
CREATE TABLE IF NOT EXISTS contas_correntes_lancamentos (
  id                      UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  codigo_lancamento       BIGINT UNIQUE,
  codigo_conta_corrente   BIGINT,
  data_lancamento         DATE,
  valor                   NUMERIC(15,2),
  descricao               TEXT,
  tipo_lancamento         TEXT,
  numero_documento        TEXT,
  dados_raw               JSONB DEFAULT '{}'::jsonb,
  created_at              TIMESTAMPTZ DEFAULT NOW(),
  updated_at              TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE contas_correntes_lancamentos ENABLE ROW LEVEL SECURITY;
CREATE INDEX IF NOT EXISTS idx_ccl_conta ON contas_correntes_lancamentos(codigo_conta_corrente);
CREATE INDEX IF NOT EXISTS idx_ccl_data  ON contas_correntes_lancamentos(data_lancamento);
CREATE TRIGGER set_updated_at BEFORE UPDATE ON contas_correntes_lancamentos
  FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();

-- 3.3 Contas a Pagar
CREATE TABLE IF NOT EXISTS contas_pagar (
  id                              UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  codigo_lancamento_omie          BIGINT UNIQUE,
  codigo_lancamento_integracao    TEXT,
  codigo_cliente_fornecedor       BIGINT,
  data_vencimento                 DATE,
  valor_documento                 NUMERIC(15,2),
  codigo_categoria                TEXT,
  numero_documento                TEXT,
  status_titulo                   TEXT,
  data_pagamento                  DATE,
  valor_pagamento                 NUMERIC(15,2),
  dados_raw                       JSONB DEFAULT '{}'::jsonb,
  created_at                      TIMESTAMPTZ DEFAULT NOW(),
  updated_at                      TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE contas_pagar ENABLE ROW LEVEL SECURITY;
CREATE INDEX IF NOT EXISTS idx_cp_vencimento ON contas_pagar(data_vencimento);
CREATE INDEX IF NOT EXISTS idx_cp_status     ON contas_pagar(status_titulo);
CREATE TRIGGER set_updated_at BEFORE UPDATE ON contas_pagar
  FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();

-- 3.4 Contas a Receber
CREATE TABLE IF NOT EXISTS contas_receber (
  id                              UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  codigo_lancamento_omie          BIGINT UNIQUE,
  codigo_lancamento_integracao    TEXT,
  codigo_cliente                  BIGINT,
  data_vencimento                 DATE,
  valor_documento                 NUMERIC(15,2),
  codigo_categoria                TEXT,
  numero_documento                TEXT,
  status_titulo                   TEXT,
  data_recebimento                DATE,
  valor_recebido                  NUMERIC(15,2),
  dados_raw                       JSONB DEFAULT '{}'::jsonb,
  created_at                      TIMESTAMPTZ DEFAULT NOW(),
  updated_at                      TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE contas_receber ENABLE ROW LEVEL SECURITY;
CREATE INDEX IF NOT EXISTS idx_cr_vencimento ON contas_receber(data_vencimento);
CREATE INDEX IF NOT EXISTS idx_cr_status     ON contas_receber(status_titulo);
CREATE INDEX IF NOT EXISTS idx_cr_cliente    ON contas_receber(codigo_cliente);
CREATE TRIGGER set_updated_at BEFORE UPDATE ON contas_receber
  FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();

-- 3.5 Contas a Receber - Boletos
CREATE TABLE IF NOT EXISTS contas_receber_boletos (
  id                      UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  codigo_lancamento_omie  BIGINT UNIQUE,
  nosso_numero            TEXT,
  linha_digitavel         TEXT,
  codigo_barras           TEXT,
  data_vencimento         DATE,
  valor                   NUMERIC(15,2),
  status                  TEXT,
  dados_raw               JSONB DEFAULT '{}'::jsonb,
  created_at              TIMESTAMPTZ DEFAULT NOW(),
  updated_at              TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE contas_receber_boletos ENABLE ROW LEVEL SECURITY;
CREATE TRIGGER set_updated_at BEFORE UPDATE ON contas_receber_boletos
  FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();

-- 3.6 PIX
CREATE TABLE IF NOT EXISTS pix (
  id                      UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  codigo_lancamento_omie  BIGINT,
  chave_pix               TEXT,
  valor                   NUMERIC(15,2),
  data_pagamento          DATE,
  status                  TEXT,
  txid                    TEXT UNIQUE,
  dados_raw               JSONB DEFAULT '{}'::jsonb,
  created_at              TIMESTAMPTZ DEFAULT NOW(),
  updated_at              TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE pix ENABLE ROW LEVEL SECURITY;
CREATE TRIGGER set_updated_at BEFORE UPDATE ON pix
  FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();

-- 3.7 Extrato de Conta Corrente
CREATE TABLE IF NOT EXISTS extrato (
  id                      UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  codigo_conta_corrente   BIGINT,
  data_movimento          DATE,
  valor                   NUMERIC(15,2),
  descricao               TEXT,
  tipo                    TEXT,
  dados_raw               JSONB DEFAULT '{}'::jsonb,
  created_at              TIMESTAMPTZ DEFAULT NOW(),
  updated_at              TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE extrato ENABLE ROW LEVEL SECURITY;
CREATE INDEX IF NOT EXISTS idx_extrato_conta ON extrato(codigo_conta_corrente);
CREATE INDEX IF NOT EXISTS idx_extrato_data  ON extrato(data_movimento);
CREATE TRIGGER set_updated_at BEFORE UPDATE ON extrato
  FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();

-- 3.8 Orçamento de Caixa
CREATE TABLE IF NOT EXISTS orcamento_caixa (
  id                UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  codigo_categoria  TEXT,
  descricao         TEXT,
  valor_previsto    NUMERIC(15,2),
  valor_realizado   NUMERIC(15,2),
  periodo           TEXT,
  dados_raw         JSONB DEFAULT '{}'::jsonb,
  created_at        TIMESTAMPTZ DEFAULT NOW(),
  updated_at        TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE orcamento_caixa ENABLE ROW LEVEL SECURITY;
CREATE TRIGGER set_updated_at BEFORE UPDATE ON orcamento_caixa
  FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();

-- 3.9 Pesquisa de Títulos
CREATE TABLE IF NOT EXISTS titulos_pesquisa (
  id                    UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  codigo_lancamento     BIGINT UNIQUE,
  tipo                  TEXT,
  status                TEXT,
  valor                 NUMERIC(15,2),
  data_vencimento       DATE,
  cliente_fornecedor    TEXT,
  dados_raw             JSONB DEFAULT '{}'::jsonb,
  created_at            TIMESTAMPTZ DEFAULT NOW(),
  updated_at            TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE titulos_pesquisa ENABLE ROW LEVEL SECURITY;
CREATE TRIGGER set_updated_at BEFORE UPDATE ON titulos_pesquisa
  FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();

-- 3.10 Movimentos Financeiros
CREATE TABLE IF NOT EXISTS movimentos_financeiros (
  id                UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  codigo_movimento  BIGINT UNIQUE,
  data_movimento    DATE,
  valor             NUMERIC(15,2),
  tipo              TEXT,
  descricao         TEXT,
  conta_corrente    BIGINT,
  dados_raw         JSONB DEFAULT '{}'::jsonb,
  created_at        TIMESTAMPTZ DEFAULT NOW(),
  updated_at        TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE movimentos_financeiros ENABLE ROW LEVEL SECURITY;
CREATE INDEX IF NOT EXISTS idx_mf_data ON movimentos_financeiros(data_movimento);
CREATE TRIGGER set_updated_at BEFORE UPDATE ON movimentos_financeiros
  FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();

-- 3.11 Resumo Financeiro
CREATE TABLE IF NOT EXISTS financas_resumo (
  id              UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  periodo         TEXT UNIQUE,
  total_pagar     NUMERIC(15,2),
  total_receber   NUMERIC(15,2),
  saldo           NUMERIC(15,2),
  dados_raw       JSONB DEFAULT '{}'::jsonb,
  created_at      TIMESTAMPTZ DEFAULT NOW(),
  updated_at      TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE financas_resumo ENABLE ROW LEVEL SECURITY;
CREATE TRIGGER set_updated_at BEFORE UPDATE ON financas_resumo
  FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();

-- 3.12 Bancos
CREATE TABLE IF NOT EXISTS bancos (
  id          UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  codigo      TEXT UNIQUE,
  descricao   TEXT,
  dados_raw   JSONB DEFAULT '{}'::jsonb,
  created_at  TIMESTAMPTZ DEFAULT NOW(),
  updated_at  TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE bancos ENABLE ROW LEVEL SECURITY;
CREATE TRIGGER set_updated_at BEFORE UPDATE ON bancos
  FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();

-- 3.13 Tipos de Documento
CREATE TABLE IF NOT EXISTS tipos_documento (
  id          UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  codigo      TEXT UNIQUE,
  descricao   TEXT,
  dados_raw   JSONB DEFAULT '{}'::jsonb,
  created_at  TIMESTAMPTZ DEFAULT NOW(),
  updated_at  TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE tipos_documento ENABLE ROW LEVEL SECURITY;
CREATE TRIGGER set_updated_at BEFORE UPDATE ON tipos_documento
  FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();

-- 3.14 Tipos de Contas Correntes
CREATE TABLE IF NOT EXISTS tipos_conta_corrente (
  id          UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  codigo      TEXT UNIQUE,
  descricao   TEXT,
  dados_raw   JSONB DEFAULT '{}'::jsonb,
  created_at  TIMESTAMPTZ DEFAULT NOW(),
  updated_at  TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE tipos_conta_corrente ENABLE ROW LEVEL SECURITY;
CREATE TRIGGER set_updated_at BEFORE UPDATE ON tipos_conta_corrente
  FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();

-- 3.15 Contas do DRE
CREATE TABLE IF NOT EXISTS contas_dre (
  id          UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  codigo      TEXT UNIQUE,
  descricao   TEXT,
  tipo        TEXT,
  estrutura   TEXT,
  dados_raw   JSONB DEFAULT '{}'::jsonb,
  created_at  TIMESTAMPTZ DEFAULT NOW(),
  updated_at  TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE contas_dre ENABLE ROW LEVEL SECURITY;
CREATE TRIGGER set_updated_at BEFORE UPDATE ON contas_dre
  FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();

-- 3.16 Finalidade de Transferência
CREATE TABLE IF NOT EXISTS finalidade_transferencia (
  id          UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  codigo      TEXT UNIQUE,
  descricao   TEXT,
  dados_raw   JSONB DEFAULT '{}'::jsonb,
  created_at  TIMESTAMPTZ DEFAULT NOW(),
  updated_at  TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE finalidade_transferencia ENABLE ROW LEVEL SECURITY;
CREATE TRIGGER set_updated_at BEFORE UPDATE ON finalidade_transferencia
  FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();

-- 3.17 Origem dos Lançamentos
CREATE TABLE IF NOT EXISTS origem_lancamento (
  id          UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  codigo      TEXT UNIQUE,
  descricao   TEXT,
  dados_raw   JSONB DEFAULT '{}'::jsonb,
  created_at  TIMESTAMPTZ DEFAULT NOW(),
  updated_at  TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE origem_lancamento ENABLE ROW LEVEL SECURITY;
CREATE TRIGGER set_updated_at BEFORE UPDATE ON origem_lancamento
  FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();

-- 3.18 Bandeiras de Cartão
CREATE TABLE IF NOT EXISTS bandeiras_cartao (
  id          UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  codigo      TEXT UNIQUE,
  descricao   TEXT,
  dados_raw   JSONB DEFAULT '{}'::jsonb,
  created_at  TIMESTAMPTZ DEFAULT NOW(),
  updated_at  TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE bandeiras_cartao ENABLE ROW LEVEL SECURITY;
CREATE TRIGGER set_updated_at BEFORE UPDATE ON bandeiras_cartao
  FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();
