-- =============================================================================
-- MÓDULO 5: VENDAS E NF-e
-- 23 tabelas
-- Endpoints: /produtos/pedidovenda/, /produtos/pedido/, /produtos/pedidovendafat/,
--            /produtos/pedidoetapas/, /produtos/cte/, /produtos/remessa/,
--            /produtos/remessafat/, /produtos/vendas-resumo/, /produtos/dfedocs/,
--            /geral/vendedores/, /produtos/formaspagvendas/, /produtos/tabelaprecos/,
--            /geral/caracteristicas/, /produtos/etapafat/, /geral/meiospagamento/,
--            /geral/origempedido/, /geral/motivodevolucao/, /produtos/nfconsultar/,
--            /produtos/notafiscalutil/, /produtos/nfe/,
--            /produtos/cupomfiscalincluir|cupomfiscal|cupomfiscalconsultar/,
--            /produtos/nfce/, /produtos/sat/
-- =============================================================================

-- 5.1 Pedidos de Venda - Resumido
CREATE TABLE IF NOT EXISTS pedidos_venda_resumo (
  id              UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  numero_pedido   BIGINT UNIQUE,
  codigo_cliente  BIGINT,
  data_pedido     DATE,
  status          TEXT,
  valor_total     NUMERIC(15,2),
  etapa           TEXT,
  dados_raw       JSONB DEFAULT '{}'::jsonb,
  created_at      TIMESTAMPTZ DEFAULT NOW(),
  updated_at      TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE pedidos_venda_resumo ENABLE ROW LEVEL SECURITY;
CREATE INDEX IF NOT EXISTS idx_pvr_status ON pedidos_venda_resumo(status);
CREATE INDEX IF NOT EXISTS idx_pvr_data   ON pedidos_venda_resumo(data_pedido);
CREATE TRIGGER set_updated_at BEFORE UPDATE ON pedidos_venda_resumo
  FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();

-- 5.2 Pedidos de Venda (completo)
CREATE TABLE IF NOT EXISTS pedidos_venda (
  id                          UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  numero_pedido               BIGINT UNIQUE,
  codigo_pedido_integracao    TEXT,
  codigo_cliente              BIGINT,
  data_pedido                 DATE,
  status                      TEXT,
  valor_total                 NUMERIC(15,2),
  etapa                       TEXT,
  produtos_json               JSONB DEFAULT '[]'::jsonb,
  parcelas_json               JSONB DEFAULT '[]'::jsonb,
  informacoes_adicionais      TEXT,
  dados_raw                   JSONB DEFAULT '{}'::jsonb,
  created_at                  TIMESTAMPTZ DEFAULT NOW(),
  updated_at                  TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE pedidos_venda ENABLE ROW LEVEL SECURITY;
CREATE INDEX IF NOT EXISTS idx_pv_cliente ON pedidos_venda(codigo_cliente);
CREATE INDEX IF NOT EXISTS idx_pv_status  ON pedidos_venda(status);
CREATE INDEX IF NOT EXISTS idx_pv_data    ON pedidos_venda(data_pedido);
CREATE TRIGGER set_updated_at BEFORE UPDATE ON pedidos_venda
  FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();

-- 5.3 Pedidos de Venda - Faturamento
CREATE TABLE IF NOT EXISTS pedidos_venda_fat (
  id                  UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  numero_pedido       BIGINT UNIQUE,
  status_faturamento  TEXT,
  numero_nfe          TEXT,
  data_faturamento    DATE,
  chave_nfe           TEXT,
  dados_raw           JSONB DEFAULT '{}'::jsonb,
  created_at          TIMESTAMPTZ DEFAULT NOW(),
  updated_at          TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE pedidos_venda_fat ENABLE ROW LEVEL SECURITY;
CREATE TRIGGER set_updated_at BEFORE UPDATE ON pedidos_venda_fat
  FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();

-- 5.4 Pedidos de Venda - Etapas
CREATE TABLE IF NOT EXISTS pedidos_venda_etapas (
  id            UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  codigo        TEXT UNIQUE,
  descricao     TEXT,
  ordem         INTEGER,
  status_padrao TEXT,
  dados_raw     JSONB DEFAULT '{}'::jsonb,
  created_at    TIMESTAMPTZ DEFAULT NOW(),
  updated_at    TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE pedidos_venda_etapas ENABLE ROW LEVEL SECURITY;
CREATE TRIGGER set_updated_at BEFORE UPDATE ON pedidos_venda_etapas
  FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();

-- 5.5 CT-e / CT-e OS
CREATE TABLE IF NOT EXISTS cte (
  id            UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  codigo_cte    BIGINT UNIQUE,
  numero_cte    TEXT,
  chave_cte     TEXT,
  emitente      TEXT,
  destinatario  TEXT,
  valor         NUMERIC(15,2),
  data_emissao  DATE,
  status        TEXT,
  dados_raw     JSONB DEFAULT '{}'::jsonb,
  created_at    TIMESTAMPTZ DEFAULT NOW(),
  updated_at    TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE cte ENABLE ROW LEVEL SECURITY;
CREATE TRIGGER set_updated_at BEFORE UPDATE ON cte
  FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();

-- 5.6 Remessa de Produtos
CREATE TABLE IF NOT EXISTS remessa_produtos (
  id              UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  codigo_remessa  BIGINT UNIQUE,
  codigo_cliente  BIGINT,
  data_remessa    DATE,
  status          TEXT,
  produtos_json   JSONB DEFAULT '[]'::jsonb,
  dados_raw       JSONB DEFAULT '{}'::jsonb,
  created_at      TIMESTAMPTZ DEFAULT NOW(),
  updated_at      TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE remessa_produtos ENABLE ROW LEVEL SECURITY;
CREATE TRIGGER set_updated_at BEFORE UPDATE ON remessa_produtos
  FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();

-- 5.7 Remessa de Produtos - Faturamento
CREATE TABLE IF NOT EXISTS remessa_fat (
  id                  UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  codigo_remessa      BIGINT UNIQUE,
  status_faturamento  TEXT,
  numero_nfe          TEXT,
  data_faturamento    DATE,
  dados_raw           JSONB DEFAULT '{}'::jsonb,
  created_at          TIMESTAMPTZ DEFAULT NOW(),
  updated_at          TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE remessa_fat ENABLE ROW LEVEL SECURITY;
CREATE TRIGGER set_updated_at BEFORE UPDATE ON remessa_fat
  FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();

-- 5.8 Resumo de Vendas
CREATE TABLE IF NOT EXISTS vendas_resumo (
  id              UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  periodo         TEXT UNIQUE,
  total_pedidos   INTEGER,
  valor_total     NUMERIC(15,2),
  status          TEXT,
  dados_raw       JSONB DEFAULT '{}'::jsonb,
  created_at      TIMESTAMPTZ DEFAULT NOW(),
  updated_at      TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE vendas_resumo ENABLE ROW LEVEL SECURITY;
CREATE TRIGGER set_updated_at BEFORE UPDATE ON vendas_resumo
  FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();

-- 5.9 DFe Documentos (Obter Documentos NF-e)
CREATE TABLE IF NOT EXISTS dfe_docs (
  id              UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  chave_nfe       TEXT UNIQUE,
  tipo_documento  TEXT,
  numero          TEXT,
  serie           TEXT,
  emitente        TEXT,
  destinatario    TEXT,
  valor           NUMERIC(15,2),
  data_emissao    DATE,
  status          TEXT,
  dados_raw       JSONB DEFAULT '{}'::jsonb,
  created_at      TIMESTAMPTZ DEFAULT NOW(),
  updated_at      TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE dfe_docs ENABLE ROW LEVEL SECURITY;
CREATE TRIGGER set_updated_at BEFORE UPDATE ON dfe_docs
  FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();

-- 5.10 Vendedores
CREATE TABLE IF NOT EXISTS vendedores (
  id          UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  codigo      BIGINT UNIQUE,
  nome        TEXT,
  email       TEXT,
  inativo     TEXT,
  dados_raw   JSONB DEFAULT '{}'::jsonb,
  created_at  TIMESTAMPTZ DEFAULT NOW(),
  updated_at  TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE vendedores ENABLE ROW LEVEL SECURITY;
CREATE TRIGGER set_updated_at BEFORE UPDATE ON vendedores
  FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();

-- 5.11 Formas de Pagamento (Vendas)
CREATE TABLE IF NOT EXISTS formas_pagamento_vendas (
  id          UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  codigo      TEXT UNIQUE,
  descricao   TEXT,
  tipo        TEXT,
  parcelas    INTEGER,
  dados_raw   JSONB DEFAULT '{}'::jsonb,
  created_at  TIMESTAMPTZ DEFAULT NOW(),
  updated_at  TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE formas_pagamento_vendas ENABLE ROW LEVEL SECURITY;
CREATE TRIGGER set_updated_at BEFORE UPDATE ON formas_pagamento_vendas
  FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();

-- 5.12 Tabela de Preços
CREATE TABLE IF NOT EXISTS tabela_precos (
  id                UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  codigo            BIGINT UNIQUE,
  descricao         TEXT,
  vigencia_inicio   DATE,
  vigencia_fim      DATE,
  inativo           TEXT,
  produtos_json     JSONB DEFAULT '[]'::jsonb,
  dados_raw         JSONB DEFAULT '{}'::jsonb,
  created_at        TIMESTAMPTZ DEFAULT NOW(),
  updated_at        TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE tabela_precos ENABLE ROW LEVEL SECURITY;
CREATE TRIGGER set_updated_at BEFORE UPDATE ON tabela_precos
  FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();

-- 5.13 Características de Produtos (cadastro de tipos de característica)
CREATE TABLE IF NOT EXISTS caracteristicas_produtos (
  id          UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  codigo      BIGINT UNIQUE,
  descricao   TEXT,
  tipo        TEXT,
  dados_raw   JSONB DEFAULT '{}'::jsonb,
  created_at  TIMESTAMPTZ DEFAULT NOW(),
  updated_at  TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE caracteristicas_produtos ENABLE ROW LEVEL SECURITY;
CREATE TRIGGER set_updated_at BEFORE UPDATE ON caracteristicas_produtos
  FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();

-- 5.14 Etapas de Faturamento
CREATE TABLE IF NOT EXISTS etapas_faturamento (
  id                UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  codigo            TEXT UNIQUE,
  descricao         TEXT,
  ordem             INTEGER,
  gera_financeiro   TEXT,
  gera_nfe          TEXT,
  dados_raw         JSONB DEFAULT '{}'::jsonb,
  created_at        TIMESTAMPTZ DEFAULT NOW(),
  updated_at        TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE etapas_faturamento ENABLE ROW LEVEL SECURITY;
CREATE TRIGGER set_updated_at BEFORE UPDATE ON etapas_faturamento
  FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();

-- 5.15 Meios de Pagamento
CREATE TABLE IF NOT EXISTS meios_pagamento (
  id          UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  codigo      TEXT UNIQUE,
  descricao   TEXT,
  dados_raw   JSONB DEFAULT '{}'::jsonb,
  created_at  TIMESTAMPTZ DEFAULT NOW(),
  updated_at  TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE meios_pagamento ENABLE ROW LEVEL SECURITY;
CREATE TRIGGER set_updated_at BEFORE UPDATE ON meios_pagamento
  FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();

-- 5.16 Origem do Pedido
CREATE TABLE IF NOT EXISTS origem_pedido (
  id          UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  codigo      TEXT UNIQUE,
  descricao   TEXT,
  dados_raw   JSONB DEFAULT '{}'::jsonb,
  created_at  TIMESTAMPTZ DEFAULT NOW(),
  updated_at  TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE origem_pedido ENABLE ROW LEVEL SECURITY;
CREATE TRIGGER set_updated_at BEFORE UPDATE ON origem_pedido
  FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();

-- 5.17 Motivos de Devolução
CREATE TABLE IF NOT EXISTS motivos_devolucao (
  id          UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  codigo      TEXT UNIQUE,
  descricao   TEXT,
  dados_raw   JSONB DEFAULT '{}'::jsonb,
  created_at  TIMESTAMPTZ DEFAULT NOW(),
  updated_at  TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE motivos_devolucao ENABLE ROW LEVEL SECURITY;
CREATE TRIGGER set_updated_at BEFORE UPDATE ON motivos_devolucao
  FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();

-- 5.18 NF-e Consultas
CREATE TABLE IF NOT EXISTS nfe_consultas (
  id            UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  chave_nfe     TEXT UNIQUE,
  numero        TEXT,
  serie         TEXT,
  status        TEXT,
  data_emissao  DATE,
  emitente      TEXT,
  destinatario  TEXT,
  valor         NUMERIC(15,2),
  dados_raw     JSONB DEFAULT '{}'::jsonb,
  created_at    TIMESTAMPTZ DEFAULT NOW(),
  updated_at    TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE nfe_consultas ENABLE ROW LEVEL SECURITY;
CREATE TRIGGER set_updated_at BEFORE UPDATE ON nfe_consultas
  FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();

-- 5.19 NF-e Utilitários (log de operações como cancelamento, inutilização)
CREATE TABLE IF NOT EXISTS nfe_utilitarios (
  id              UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  operacao        TEXT,
  chave_nfe       TEXT,
  data_operacao   TIMESTAMPTZ,
  resultado       TEXT,
  mensagem        TEXT,
  dados_raw       JSONB DEFAULT '{}'::jsonb,
  created_at      TIMESTAMPTZ DEFAULT NOW(),
  updated_at      TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE nfe_utilitarios ENABLE ROW LEVEL SECURITY;
CREATE TRIGGER set_updated_at BEFORE UPDATE ON nfe_utilitarios
  FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();

-- 5.20 NF-e Importadas
CREATE TABLE IF NOT EXISTS nfe_importadas (
  id              UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  chave_nfe       TEXT UNIQUE,
  xml_nfe         TEXT,
  data_importacao TIMESTAMPTZ,
  status          TEXT,
  dados_raw       JSONB DEFAULT '{}'::jsonb,
  created_at      TIMESTAMPTZ DEFAULT NOW(),
  updated_at      TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE nfe_importadas ENABLE ROW LEVEL SECURITY;
CREATE TRIGGER set_updated_at BEFORE UPDATE ON nfe_importadas
  FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();

-- 5.21 Cupom Fiscal (Incluir / Cancelar / Consultar — unificado)
CREATE TABLE IF NOT EXISTS cupom_fiscal (
  id                    UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  codigo_cupom          BIGINT UNIQUE,
  numero_cupom          TEXT,
  data_emissao          DATE,
  valor_total           NUMERIC(15,2),
  status                TEXT,
  cpf_cnpj_consumidor   TEXT,
  dados_raw             JSONB DEFAULT '{}'::jsonb,
  created_at            TIMESTAMPTZ DEFAULT NOW(),
  updated_at            TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE cupom_fiscal ENABLE ROW LEVEL SECURITY;
CREATE TRIGGER set_updated_at BEFORE UPDATE ON cupom_fiscal
  FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();

-- 5.22 NFC-e Importadas
CREATE TABLE IF NOT EXISTS nfce (
  id              UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  chave_nfce      TEXT UNIQUE,
  numero          TEXT,
  data_emissao    DATE,
  valor           NUMERIC(15,2),
  status          TEXT,
  cpf_consumidor  TEXT,
  dados_raw       JSONB DEFAULT '{}'::jsonb,
  created_at      TIMESTAMPTZ DEFAULT NOW(),
  updated_at      TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE nfce ENABLE ROW LEVEL SECURITY;
CREATE TRIGGER set_updated_at BEFORE UPDATE ON nfce
  FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();

-- 5.23 CFe-SAT Importadas
CREATE TABLE IF NOT EXISTS cfe_sat (
  id              UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  numero_sat      TEXT UNIQUE,
  cnpj_emitente   TEXT,
  data_emissao    DATE,
  valor           NUMERIC(15,2),
  status          TEXT,
  dados_raw       JSONB DEFAULT '{}'::jsonb,
  created_at      TIMESTAMPTZ DEFAULT NOW(),
  updated_at      TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE cfe_sat ENABLE ROW LEVEL SECURITY;
CREATE TRIGGER set_updated_at BEFORE UPDATE ON cfe_sat
  FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();
