-- =============================================================================
-- MÓDULO 7: PAINEL DO CONTADOR
-- 2 tabelas
-- Endpoints: /contador/xml/, /contador/resumo/
-- =============================================================================

-- 7.1 Documentos Fiscais (XML)
CREATE TABLE IF NOT EXISTS documentos_fiscais_xml (
  id                  UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  chave_acesso        TEXT UNIQUE,
  tipo_documento      TEXT,
  numero              TEXT,
  serie               TEXT,
  emitente            TEXT,
  destinatario        TEXT,
  data_emissao        DATE,
  valor               NUMERIC(15,2),
  xml_content         TEXT,
  periodo_referencia  TEXT,
  dados_raw           JSONB DEFAULT '{}'::jsonb,
  created_at          TIMESTAMPTZ DEFAULT NOW(),
  updated_at          TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE documentos_fiscais_xml ENABLE ROW LEVEL SECURITY;
CREATE INDEX IF NOT EXISTS idx_dfxml_periodo ON documentos_fiscais_xml(periodo_referencia);
CREATE INDEX IF NOT EXISTS idx_dfxml_tipo    ON documentos_fiscais_xml(tipo_documento);
CREATE INDEX IF NOT EXISTS idx_dfxml_data    ON documentos_fiscais_xml(data_emissao);
CREATE TRIGGER set_updated_at BEFORE UPDATE ON documentos_fiscais_xml
  FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();

-- 7.2 Resumo Contador
CREATE TABLE IF NOT EXISTS contador_resumo (
  id            UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  periodo       TEXT UNIQUE,
  total_nfe     INTEGER,
  total_nfse    INTEGER,
  total_cte     INTEGER,
  valor_total   NUMERIC(15,2),
  dados_raw     JSONB DEFAULT '{}'::jsonb,
  created_at    TIMESTAMPTZ DEFAULT NOW(),
  updated_at    TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE contador_resumo ENABLE ROW LEVEL SECURITY;
CREATE TRIGGER set_updated_at BEFORE UPDATE ON contador_resumo
  FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();
