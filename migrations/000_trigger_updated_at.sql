-- =============================================================================
-- 000 — Função de trigger para updated_at automático
-- Executar ANTES de qualquer módulo
-- =============================================================================

CREATE OR REPLACE FUNCTION trigger_set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;
