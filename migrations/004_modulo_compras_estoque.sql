-- =============================================================================
-- MÓDULO 4: COMPRAS, ESTOQUE E PRODUÇÃO
-- 35 tabelas
-- Endpoints: /geral/produtos/, /geral/prodcaract/, /geral/malha/,
--            /geral/produtoskit/, /produtos/variacao/, /produtos/produtoslote/,
--            /produtos/requisicaocompra/, /produtos/pedidocompra/, /produtos/op/,
--            /produtos/notaentrada/, /produtos/notaentradafat/,
--            /produtos/recebimentonfe/, /produtos/compras-resumo/,
--            /geral/familias/, /geral/unidade/, /estoque/comprador/,
--            /estoque/produtofornecedor/, /produtos/formaspagcompras/,
--            /produtos/ncm/, /geral/cenarios/, /produtos/cfop/, /produtos/cnae/,
--            /produtos/icmscst/, /produtos/icmscsosn/, /produtos/icmsorigem/,
--            /produtos/piscst/, /produtos/cofinscst/, /produtos/ipicst/,
--            /produtos/ipienq/, /produtos/tpcalc/, /produtos/cest/,
--            /estoque/ajuste/, /estoque/consulta/, /estoque/movestoque/,
--            /estoque/local/, /estoque/resumo/
-- =============================================================================

-- 4.1 Produtos
CREATE TABLE IF NOT EXISTS produtos (
  id                          UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  codigo_produto              BIGINT UNIQUE,
  codigo_produto_integracao   TEXT,
  descricao                   TEXT,
  codigo_familia              BIGINT,
  unidade                     TEXT,
  ncm                         TEXT,
  valor_unitario              NUMERIC(15,4),
  tipo_item                   TEXT,
  inativo                     TEXT,
  obs                         TEXT,
  ean                         TEXT,
  codigo_barras               TEXT,
  dados_raw                   JSONB DEFAULT '{}'::jsonb,
  created_at                  TIMESTAMPTZ DEFAULT NOW(),
  updated_at                  TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE produtos ENABLE ROW LEVEL SECURITY;
CREATE INDEX IF NOT EXISTS idx_produtos_codigo  ON produtos(codigo_produto);
CREATE INDEX IF NOT EXISTS idx_produtos_familia ON produtos(codigo_familia);
CREATE INDEX IF NOT EXISTS idx_produtos_ncm     ON produtos(ncm);
CREATE TRIGGER set_updated_at BEFORE UPDATE ON produtos
  FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();

-- 4.2 Produtos - Características
CREATE TABLE IF NOT EXISTS produtos_caract (
  id                UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  codigo_produto    BIGINT,
  cCaractItem       TEXT,
  cCaractDescricao  TEXT,
  cCaractValor      TEXT,
  dados_raw         JSONB DEFAULT '{}'::jsonb,
  created_at        TIMESTAMPTZ DEFAULT NOW(),
  updated_at        TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(codigo_produto, cCaractItem)
);
ALTER TABLE produtos_caract ENABLE ROW LEVEL SECURITY;
CREATE INDEX IF NOT EXISTS idx_prod_caract_codigo ON produtos_caract(codigo_produto);
CREATE TRIGGER set_updated_at BEFORE UPDATE ON produtos_caract
  FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();

-- 4.3 Produtos - Estrutura (Malha)
CREATE TABLE IF NOT EXISTS produtos_estrutura (
  id                  UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  codigo_produto      BIGINT,
  codigo_componente   BIGINT,
  quantidade          NUMERIC(15,4),
  unidade             TEXT,
  dados_raw           JSONB DEFAULT '{}'::jsonb,
  created_at          TIMESTAMPTZ DEFAULT NOW(),
  updated_at          TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(codigo_produto, codigo_componente)
);
ALTER TABLE produtos_estrutura ENABLE ROW LEVEL SECURITY;
CREATE TRIGGER set_updated_at BEFORE UPDATE ON produtos_estrutura
  FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();

-- 4.4 Produtos - Kit
CREATE TABLE IF NOT EXISTS produtos_kit (
  id              UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  codigo_produto  BIGINT,
  codigo_kit      BIGINT,
  quantidade      NUMERIC(15,4),
  dados_raw       JSONB DEFAULT '{}'::jsonb,
  created_at      TIMESTAMPTZ DEFAULT NOW(),
  updated_at      TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(codigo_produto, codigo_kit)
);
ALTER TABLE produtos_kit ENABLE ROW LEVEL SECURITY;
CREATE TRIGGER set_updated_at BEFORE UPDATE ON produtos_kit
  FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();

-- 4.5 Produtos - Variação
CREATE TABLE IF NOT EXISTS produtos_variacao (
  id              UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  codigo_produto  BIGINT,
  codigo_variacao BIGINT UNIQUE,
  descricao       TEXT,
  codigo_grade    TEXT,
  dados_raw       JSONB DEFAULT '{}'::jsonb,
  created_at      TIMESTAMPTZ DEFAULT NOW(),
  updated_at      TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE produtos_variacao ENABLE ROW LEVEL SECURITY;
CREATE TRIGGER set_updated_at BEFORE UPDATE ON produtos_variacao
  FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();

-- 4.6 Produtos - Lote
CREATE TABLE IF NOT EXISTS produtos_lote (
  id                UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  codigo_produto    BIGINT,
  numero_lote       TEXT,
  data_fabricacao   DATE,
  data_validade     DATE,
  quantidade        NUMERIC(15,4),
  dados_raw         JSONB DEFAULT '{}'::jsonb,
  created_at        TIMESTAMPTZ DEFAULT NOW(),
  updated_at        TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(codigo_produto, numero_lote)
);
ALTER TABLE produtos_lote ENABLE ROW LEVEL SECURITY;
CREATE TRIGGER set_updated_at BEFORE UPDATE ON produtos_lote
  FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();

-- 4.7 Requisições de Compra
CREATE TABLE IF NOT EXISTS requisicoes_compra (
  id                  UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  numero_requisicao   BIGINT UNIQUE,
  data_requisicao     DATE,
  status              TEXT,
  solicitante         TEXT,
  produtos_json       JSONB DEFAULT '[]'::jsonb,
  dados_raw           JSONB DEFAULT '{}'::jsonb,
  created_at          TIMESTAMPTZ DEFAULT NOW(),
  updated_at          TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE requisicoes_compra ENABLE ROW LEVEL SECURITY;
CREATE TRIGGER set_updated_at BEFORE UPDATE ON requisicoes_compra
  FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();

-- 4.8 Pedidos de Compra
CREATE TABLE IF NOT EXISTS pedidos_compra (
  id                  UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  numero_pedido       BIGINT UNIQUE,
  codigo_fornecedor   BIGINT,
  data_pedido         DATE,
  status              TEXT,
  valor_total         NUMERIC(15,2),
  produtos_json       JSONB DEFAULT '[]'::jsonb,
  dados_raw           JSONB DEFAULT '{}'::jsonb,
  created_at          TIMESTAMPTZ DEFAULT NOW(),
  updated_at          TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE pedidos_compra ENABLE ROW LEVEL SECURITY;
CREATE INDEX IF NOT EXISTS idx_pc_status ON pedidos_compra(status);
CREATE TRIGGER set_updated_at BEFORE UPDATE ON pedidos_compra
  FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();

-- 4.9 Ordens de Produção
CREATE TABLE IF NOT EXISTS ordens_producao (
  id              UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  numero_op       BIGINT UNIQUE,
  codigo_produto  BIGINT,
  quantidade      NUMERIC(15,4),
  data_inicio     DATE,
  data_fim        DATE,
  status          TEXT,
  dados_raw       JSONB DEFAULT '{}'::jsonb,
  created_at      TIMESTAMPTZ DEFAULT NOW(),
  updated_at      TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE ordens_producao ENABLE ROW LEVEL SECURITY;
CREATE TRIGGER set_updated_at BEFORE UPDATE ON ordens_producao
  FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();

-- 4.10 Notas de Entrada
CREATE TABLE IF NOT EXISTS notas_entrada (
  id                  UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  codigo_nfe          BIGINT UNIQUE,
  numero_nf           TEXT,
  serie               TEXT,
  codigo_fornecedor   BIGINT,
  data_emissao        DATE,
  valor_total         NUMERIC(15,2),
  status              TEXT,
  chave_nfe           TEXT,
  dados_raw           JSONB DEFAULT '{}'::jsonb,
  created_at          TIMESTAMPTZ DEFAULT NOW(),
  updated_at          TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE notas_entrada ENABLE ROW LEVEL SECURITY;
CREATE INDEX IF NOT EXISTS idx_ne_data ON notas_entrada(data_emissao);
CREATE TRIGGER set_updated_at BEFORE UPDATE ON notas_entrada
  FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();

-- 4.11 Notas de Entrada - Faturamento
CREATE TABLE IF NOT EXISTS notas_entrada_fat (
  id                UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  codigo_nfe        BIGINT UNIQUE,
  data_faturamento  DATE,
  status            TEXT,
  impostos_json     JSONB DEFAULT '{}'::jsonb,
  dados_raw         JSONB DEFAULT '{}'::jsonb,
  created_at        TIMESTAMPTZ DEFAULT NOW(),
  updated_at        TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE notas_entrada_fat ENABLE ROW LEVEL SECURITY;
CREATE TRIGGER set_updated_at BEFORE UPDATE ON notas_entrada_fat
  FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();

-- 4.12 Recebimento de Nota Fiscal
CREATE TABLE IF NOT EXISTS recebimento_nfe (
  id                UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  codigo_nfe        BIGINT UNIQUE,
  data_recebimento  DATE,
  status            TEXT,
  observacao        TEXT,
  dados_raw         JSONB DEFAULT '{}'::jsonb,
  created_at        TIMESTAMPTZ DEFAULT NOW(),
  updated_at        TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE recebimento_nfe ENABLE ROW LEVEL SECURITY;
CREATE TRIGGER set_updated_at BEFORE UPDATE ON recebimento_nfe
  FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();

-- 4.13 Resumo de Compras
CREATE TABLE IF NOT EXISTS compras_resumo (
  id              UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  periodo         TEXT UNIQUE,
  total_pedidos   INTEGER,
  valor_total     NUMERIC(15,2),
  status          TEXT,
  dados_raw       JSONB DEFAULT '{}'::jsonb,
  created_at      TIMESTAMPTZ DEFAULT NOW(),
  updated_at      TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE compras_resumo ENABLE ROW LEVEL SECURITY;
CREATE TRIGGER set_updated_at BEFORE UPDATE ON compras_resumo
  FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();

-- 4.14 Famílias de Produto
CREATE TABLE IF NOT EXISTS familias_produto (
  id          UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  codigo      BIGINT UNIQUE,
  descricao   TEXT,
  inativo     TEXT,
  dados_raw   JSONB DEFAULT '{}'::jsonb,
  created_at  TIMESTAMPTZ DEFAULT NOW(),
  updated_at  TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE familias_produto ENABLE ROW LEVEL SECURITY;
CREATE TRIGGER set_updated_at BEFORE UPDATE ON familias_produto
  FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();

-- 4.15 Unidades
CREATE TABLE IF NOT EXISTS unidades (
  id          UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  codigo      TEXT UNIQUE,
  descricao   TEXT,
  dados_raw   JSONB DEFAULT '{}'::jsonb,
  created_at  TIMESTAMPTZ DEFAULT NOW(),
  updated_at  TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE unidades ENABLE ROW LEVEL SECURITY;
CREATE TRIGGER set_updated_at BEFORE UPDATE ON unidades
  FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();

-- 4.16 Compradores
CREATE TABLE IF NOT EXISTS compradores (
  id          UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  codigo      BIGINT UNIQUE,
  nome        TEXT,
  email       TEXT,
  dados_raw   JSONB DEFAULT '{}'::jsonb,
  created_at  TIMESTAMPTZ DEFAULT NOW(),
  updated_at  TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE compradores ENABLE ROW LEVEL SECURITY;
CREATE TRIGGER set_updated_at BEFORE UPDATE ON compradores
  FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();

-- 4.17 Produto x Fornecedor
CREATE TABLE IF NOT EXISTS produto_fornecedor (
  id                          UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  codigo_produto              BIGINT,
  codigo_fornecedor           BIGINT,
  codigo_produto_fornecedor   TEXT,
  preco                       NUMERIC(15,4),
  prazo_entrega               INTEGER,
  dados_raw                   JSONB DEFAULT '{}'::jsonb,
  created_at                  TIMESTAMPTZ DEFAULT NOW(),
  updated_at                  TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(codigo_produto, codigo_fornecedor)
);
ALTER TABLE produto_fornecedor ENABLE ROW LEVEL SECURITY;
CREATE TRIGGER set_updated_at BEFORE UPDATE ON produto_fornecedor
  FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();

-- 4.18 Formas de Pagamento (Compras)
CREATE TABLE IF NOT EXISTS formas_pagamento_compras (
  id          UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  codigo      TEXT UNIQUE,
  descricao   TEXT,
  tipo        TEXT,
  dados_raw   JSONB DEFAULT '{}'::jsonb,
  created_at  TIMESTAMPTZ DEFAULT NOW(),
  updated_at  TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE formas_pagamento_compras ENABLE ROW LEVEL SECURITY;
CREATE TRIGGER set_updated_at BEFORE UPDATE ON formas_pagamento_compras
  FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();

-- 4.19 NCM
CREATE TABLE IF NOT EXISTS ncm (
  id            UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  codigo        TEXT UNIQUE,
  descricao     TEXT,
  aliquota_ii   NUMERIC(8,4),
  aliquota_ipi  NUMERIC(8,4),
  dados_raw     JSONB DEFAULT '{}'::jsonb,
  created_at    TIMESTAMPTZ DEFAULT NOW(),
  updated_at    TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE ncm ENABLE ROW LEVEL SECURITY;
CREATE TRIGGER set_updated_at BEFORE UPDATE ON ncm
  FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();

-- 4.20 Cenários de Impostos
CREATE TABLE IF NOT EXISTS cenarios_impostos (
  id          UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  codigo      BIGINT UNIQUE,
  descricao   TEXT,
  tipo        TEXT,
  dados_raw   JSONB DEFAULT '{}'::jsonb,
  created_at  TIMESTAMPTZ DEFAULT NOW(),
  updated_at  TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE cenarios_impostos ENABLE ROW LEVEL SECURITY;
CREATE TRIGGER set_updated_at BEFORE UPDATE ON cenarios_impostos
  FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();

-- 4.21 CFOP
CREATE TABLE IF NOT EXISTS cfop (
  id          UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  codigo      TEXT UNIQUE,
  descricao   TEXT,
  tipo        TEXT,
  dados_raw   JSONB DEFAULT '{}'::jsonb,
  created_at  TIMESTAMPTZ DEFAULT NOW(),
  updated_at  TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE cfop ENABLE ROW LEVEL SECURITY;
CREATE TRIGGER set_updated_at BEFORE UPDATE ON cfop
  FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();

-- 4.22 ICMS - CST
CREATE TABLE IF NOT EXISTS icms_cst (
  id          UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  codigo      TEXT UNIQUE,
  descricao   TEXT,
  dados_raw   JSONB DEFAULT '{}'::jsonb,
  created_at  TIMESTAMPTZ DEFAULT NOW(),
  updated_at  TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE icms_cst ENABLE ROW LEVEL SECURITY;
CREATE TRIGGER set_updated_at BEFORE UPDATE ON icms_cst
  FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();

-- 4.23 ICMS - CSOSN
CREATE TABLE IF NOT EXISTS icms_csosn (
  id          UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  codigo      TEXT UNIQUE,
  descricao   TEXT,
  dados_raw   JSONB DEFAULT '{}'::jsonb,
  created_at  TIMESTAMPTZ DEFAULT NOW(),
  updated_at  TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE icms_csosn ENABLE ROW LEVEL SECURITY;
CREATE TRIGGER set_updated_at BEFORE UPDATE ON icms_csosn
  FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();

-- 4.24 ICMS - Origem da Mercadoria
CREATE TABLE IF NOT EXISTS icms_origem (
  id          UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  codigo      TEXT UNIQUE,
  descricao   TEXT,
  dados_raw   JSONB DEFAULT '{}'::jsonb,
  created_at  TIMESTAMPTZ DEFAULT NOW(),
  updated_at  TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE icms_origem ENABLE ROW LEVEL SECURITY;
CREATE TRIGGER set_updated_at BEFORE UPDATE ON icms_origem
  FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();

-- 4.25 PIS - CST
CREATE TABLE IF NOT EXISTS pis_cst (
  id          UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  codigo      TEXT UNIQUE,
  descricao   TEXT,
  dados_raw   JSONB DEFAULT '{}'::jsonb,
  created_at  TIMESTAMPTZ DEFAULT NOW(),
  updated_at  TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE pis_cst ENABLE ROW LEVEL SECURITY;
CREATE TRIGGER set_updated_at BEFORE UPDATE ON pis_cst
  FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();

-- 4.26 COFINS - CST
CREATE TABLE IF NOT EXISTS cofins_cst (
  id          UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  codigo      TEXT UNIQUE,
  descricao   TEXT,
  dados_raw   JSONB DEFAULT '{}'::jsonb,
  created_at  TIMESTAMPTZ DEFAULT NOW(),
  updated_at  TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE cofins_cst ENABLE ROW LEVEL SECURITY;
CREATE TRIGGER set_updated_at BEFORE UPDATE ON cofins_cst
  FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();

-- 4.27 IPI - CST
CREATE TABLE IF NOT EXISTS ipi_cst (
  id          UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  codigo      TEXT UNIQUE,
  descricao   TEXT,
  dados_raw   JSONB DEFAULT '{}'::jsonb,
  created_at  TIMESTAMPTZ DEFAULT NOW(),
  updated_at  TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE ipi_cst ENABLE ROW LEVEL SECURITY;
CREATE TRIGGER set_updated_at BEFORE UPDATE ON ipi_cst
  FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();

-- 4.28 IPI - Enquadramento
CREATE TABLE IF NOT EXISTS ipi_enquadramento (
  id          UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  codigo      TEXT UNIQUE,
  descricao   TEXT,
  dados_raw   JSONB DEFAULT '{}'::jsonb,
  created_at  TIMESTAMPTZ DEFAULT NOW(),
  updated_at  TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE ipi_enquadramento ENABLE ROW LEVEL SECURITY;
CREATE TRIGGER set_updated_at BEFORE UPDATE ON ipi_enquadramento
  FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();

-- 4.29 Tipo de Cálculo
CREATE TABLE IF NOT EXISTS tipo_calculo (
  id          UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  codigo      TEXT UNIQUE,
  descricao   TEXT,
  dados_raw   JSONB DEFAULT '{}'::jsonb,
  created_at  TIMESTAMPTZ DEFAULT NOW(),
  updated_at  TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE tipo_calculo ENABLE ROW LEVEL SECURITY;
CREATE TRIGGER set_updated_at BEFORE UPDATE ON tipo_calculo
  FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();

-- 4.30 CEST
CREATE TABLE IF NOT EXISTS cest (
  id              UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  codigo          TEXT UNIQUE,
  descricao       TEXT,
  ncm_referencia  TEXT,
  dados_raw       JSONB DEFAULT '{}'::jsonb,
  created_at      TIMESTAMPTZ DEFAULT NOW(),
  updated_at      TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE cest ENABLE ROW LEVEL SECURITY;
CREATE TRIGGER set_updated_at BEFORE UPDATE ON cest
  FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();

-- 4.31 Ajustes de Estoque
CREATE TABLE IF NOT EXISTS ajustes_estoque (
  id              UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  codigo_ajuste   BIGINT UNIQUE,
  codigo_produto  BIGINT,
  data_ajuste     DATE,
  quantidade      NUMERIC(15,4),
  tipo_ajuste     TEXT,
  observacao      TEXT,
  dados_raw       JSONB DEFAULT '{}'::jsonb,
  created_at      TIMESTAMPTZ DEFAULT NOW(),
  updated_at      TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE ajustes_estoque ENABLE ROW LEVEL SECURITY;
CREATE TRIGGER set_updated_at BEFORE UPDATE ON ajustes_estoque
  FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();

-- 4.32 Consulta de Estoque
CREATE TABLE IF NOT EXISTS consulta_estoque (
  id              UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  codigo_produto  BIGINT UNIQUE,
  descricao       TEXT,
  saldo_atual     NUMERIC(15,4),
  local_estoque   TEXT,
  reservado       NUMERIC(15,4),
  disponivel      NUMERIC(15,4),
  dados_raw       JSONB DEFAULT '{}'::jsonb,
  created_at      TIMESTAMPTZ DEFAULT NOW(),
  updated_at      TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE consulta_estoque ENABLE ROW LEVEL SECURITY;
CREATE TRIGGER set_updated_at BEFORE UPDATE ON consulta_estoque
  FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();

-- 4.33 Movimento de Estoque
CREATE TABLE IF NOT EXISTS movimento_estoque (
  id                UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  codigo_movimento  BIGINT UNIQUE,
  codigo_produto    BIGINT,
  data_movimento    DATE,
  quantidade        NUMERIC(15,4),
  tipo_movimento    TEXT,
  origem            TEXT,
  numero_documento  TEXT,
  dados_raw         JSONB DEFAULT '{}'::jsonb,
  created_at        TIMESTAMPTZ DEFAULT NOW(),
  updated_at        TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE movimento_estoque ENABLE ROW LEVEL SECURITY;
CREATE INDEX IF NOT EXISTS idx_me_produto ON movimento_estoque(codigo_produto);
CREATE INDEX IF NOT EXISTS idx_me_data    ON movimento_estoque(data_movimento);
CREATE TRIGGER set_updated_at BEFORE UPDATE ON movimento_estoque
  FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();

-- 4.34 Locais de Estoque
CREATE TABLE IF NOT EXISTS locais_estoque (
  id          UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  codigo      BIGINT UNIQUE,
  descricao   TEXT,
  inativo     TEXT,
  dados_raw   JSONB DEFAULT '{}'::jsonb,
  created_at  TIMESTAMPTZ DEFAULT NOW(),
  updated_at  TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE locais_estoque ENABLE ROW LEVEL SECURITY;
CREATE TRIGGER set_updated_at BEFORE UPDATE ON locais_estoque
  FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();

-- 4.35 Resumo do Estoque
CREATE TABLE IF NOT EXISTS estoque_resumo (
  id              UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  codigo_produto  BIGINT UNIQUE,
  descricao       TEXT,
  saldo_total     NUMERIC(15,4),
  valor_total     NUMERIC(15,2),
  dados_raw       JSONB DEFAULT '{}'::jsonb,
  created_at      TIMESTAMPTZ DEFAULT NOW(),
  updated_at      TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE estoque_resumo ENABLE ROW LEVEL SECURITY;
CREATE TRIGGER set_updated_at BEFORE UPDATE ON estoque_resumo
  FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();
