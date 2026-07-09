# Coleta de Assinatura Digital via Link Público — Guia de Integração para IA

> Documenta o padrão de **coleta e validação de assinatura digital** usado no Módulo Jurídico (Propostas e Contratos) da VerticalParts. Extraído por análise (somente leitura) do repositório [`verticalpartsIA/010_vpprd`](https://github.com/verticalpartsIA/010_vpprd).
>
> Este padrão é uma variação do [whatsapp-form-token-pattern.md](whatsapp-form-token-pattern.md) (mesma ideia de link público com token, sem login) — a diferença é o objetivo: aqui o cliente não preenche um formulário técnico, ele **lê um contrato/proposta e assina digitalmente** (desenho ou nome digitado), com trilha de auditoria e hash de integridade.

---

## Visão geral da arquitetura

```
Vendedor/Jurídico (painel autenticado)
   cria o contrato (rascunho) a partir de um formulário interno
        │
        ▼
Marca como "enviado" → gera token curto (16 hex) + expiração (7 dias)
   envio por WhatsApp (wa.me) ou e-mail (mailto) com o link /assinar/{token}
        │
        ▼
Cliente abre o link (sem login) — assinar.html + assinar-app.jsx
   - resolve o token em uma de duas tabelas (contratos_instalador OU
     contratos_venda_equipamentos) — cada uma tem sua própria "store" JS
   - ao abrir: status rascunho/enviado → "visualizado", grava IP + user-agent
     + rótulo de dispositivo no campo `audit` (JSONB)
   - exige rolar o documento até o fim + marcar concordância antes de habilitar
     o botão de assinar
   - assinatura: desenho num canvas (exportado como PNG base64) OU nome digitado
        │
        ▼
Ao confirmar: gera hash SHA-256 (form_state + nome do signatário), grava tudo
em `audit` (IP, user-agent, device, tipo de assinatura, dado da assinatura,
hash, timestamp) + status "assinado"
        │
        ▼
Notifica internamente (tabela `alertas` + log central `VPLog`)
Cliente pode baixar cópia em PDF (window.print())
```

## Componentes técnicos

### 1. Duas tabelas paralelas, mesmo formato
- **`contratos_instalador`** — contratos com montadores/instaladores.
- **`contratos_venda_equipamentos`** — contratos de venda de equipamento ao cliente final.

Ambas seguem o mesmo shape (mesma "store" pattern, arquivos `contrato-instalador-store.js` / `contrato-venda-store.js`), cada uma com seu conjunto de campos de negócio específicos, mas a espinha dorsal (token, status, audit, log) é idêntica.

### 2. Ciclo de vida do status
`rascunho` → `enviado` → `visualizado` → `assinado` (ou `recusado` / `expirado`)
- Nunca regride (ex.: visualizar de novo não volta o status).
- Expiração fixa de 7 dias a partir do envio; uma varredura (`sweepExpired`, chamada no load do dashboard) marca como `expirado` os que passaram do prazo sem assinatura.
- Cada transição é empilhada num array `log` (JSONB) com `status`, `at` (timestamp) e `meta` livre — histórico completo sem tabela de auditoria separada.

### 3. Assinatura e integridade
- **Dois modos de assinatura**: desenho à mão (canvas → `toDataURL('image/png')`) ou nome digitado (mínimo 3 caracteres).
- **Hash de integridade**: `SHA-256(JSON.stringify(form_state) + '|' + signerName)`, calculado no navegador do cliente (`crypto.subtle.digest`) e armazenado em `audit.hash`. **Isto não é uma assinatura digital criptográfica com certificado (ICP-Brasil)** — é um *fingerprint* de integridade do conteúdo assinado, exibido ao usuário como "protocolo" pós-assinatura.
- **Base legal citada na UI**: MP 2.200-2/2001 e Lei 14.063/2020 (validade de assinaturas eletrônicas no Brasil) — mencionar isso é responsabilidade do time jurídico da VerticalParts, não uma validação técnica automática.
- **Metadados de auditoria capturados**: IP público (via `api.ipify.org`, chamada client-side com timeout de 3s e fallback `null`), user-agent completo, rótulo de dispositivo/app inferido do user-agent (OS + navegador, detecta inclusive abertura via WhatsApp in-app browser).

### 4. Acesso público sem login
Diferente do padrão `whatsapp-form-token-pattern.md` (que usa server functions com service role), aqui o cliente **JavaScript acessa o Supabase diretamente** (`window.__VP_SB.sb`, mesma lib client-side) filtrando por `token`. Isso significa que a política de RLS precisa permitir `SELECT`/`UPDATE` por token para o role `anon` — **verificar/replicar essa policy com cuidado**, pois é diferente (e potencialmente mais permissiva) do padrão service-role-only do M7.

### 5. Notificação interna
- Toda mudança de status relevante grava um registro na tabela `alertas` (sino de notificações do painel) e espelha no log central `window.VPLog.registrar(...)` (auditoria cross-módulo, usada por outros módulos do mesmo app).

## ⚠️ Achado de governança de banco de dados
As tabelas `contratos_instalador` e `contratos_venda_equipamentos` **não têm migration versionada neste repositório** — só existe uma migration para uma tabela `contratos` (genérica, mais antiga, com `tipo_contrato`/`dados jsonb`) e outra para `propostas`. As duas tabelas realmente usadas pelo fluxo de assinatura atual foram, aparentemente, criadas diretamente no Supabase Studio, fora do controle de versão. O DDL abaixo foi **reconstruído a partir do código de aplicação** (`_packToRow` em `contrato-instalador-store.js`), não copiado de uma migration real — trate como ponto de partida e valide contra o schema real do projeto `vpprd` antes de aplicar em produção.

## Requisito de Banco de Dados (Supabase)

**Para que isso funcione você precisa criar no Supabase o seguinte** (schema reconstruído; sem migration de origem — ver achado de governança acima):

```sql
CREATE TABLE public.contratos_instalador (
  id                 UUID PRIMARY KEY,
  numero_documento   TEXT UNIQUE NOT NULL,
  seq_mes            INT,
  ano_mes            TEXT,
  token              TEXT UNIQUE NOT NULL,           -- 16 chars hex, link público /assinar/{token}
  titulo             TEXT,
  contratada_nome    TEXT,
  contratada_cnpj    TEXT,
  responsavel_nome   TEXT,
  responsavel_cpf    TEXT,
  valor_total        NUMERIC,
  objeto_resumo      TEXT,
  vendedor_id        UUID,
  status             TEXT NOT NULL DEFAULT 'rascunho', -- rascunho|enviado|visualizado|assinado|expirado|recusado
  channel            TEXT,                            -- whatsapp | email
  recipient          JSONB DEFAULT '{}'::jsonb,
  form_state         JSONB DEFAULT '{}'::jsonb,
  doc                JSONB DEFAULT '{}'::jsonb,        -- contrato renderizado (snapshot)
  log                JSONB DEFAULT '[]'::jsonb,        -- histórico de transições de status
  audit              JSONB DEFAULT '{}'::jsonb,        -- IP/UA/device/hash/dados da assinatura
  sent_at            TIMESTAMPTZ,
  viewed_at          TIMESTAMPTZ,
  signed_at          TIMESTAMPTZ,
  expires_at         TIMESTAMPTZ,
  criado_em          TIMESTAMPTZ NOT NULL DEFAULT now(),
  atualizado_em      TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX ON public.contratos_instalador (token);
CREATE INDEX ON public.contratos_instalador (status);

-- Estrutura idêntica para o outro fluxo de negócio (venda ao cliente final):
CREATE TABLE public.contratos_venda_equipamentos (LIKE public.contratos_instalador INCLUDING ALL);

ALTER TABLE public.contratos_instalador ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.contratos_venda_equipamentos ENABLE ROW LEVEL SECURITY;

-- Painel interno: acesso total para autenticados
CREATE POLICY "contratos_instalador_authenticated_all" ON public.contratos_instalador
  FOR ALL TO authenticated USING (true) WITH CHECK (true);

-- Página pública (sem login): precisa de policy para `anon` restrita por token.
-- Não confiar em "USING (true)" para anon — restrinja à validação de token/expiração
-- no nível de aplicação OU, preferencialmente, migre este fluxo para server functions
-- com service role (como no whatsapp-form-token-pattern.md) em vez de client anon direto.
CREATE POLICY "contratos_instalador_anon_by_token" ON public.contratos_instalador
  FOR SELECT TO anon USING (true); -- validar token na aplicação; endurecer antes de produção
CREATE POLICY "contratos_instalador_anon_update_by_token" ON public.contratos_instalador
  FOR UPDATE TO anon USING (true) WITH CHECK (true); -- idem — revisar antes de aplicar
```

> ⚠️ **Risco identificado**: permitir `UPDATE`/`SELECT` para `anon` "USING (true)" sem restrição por linha depende 100% da validação de token feita no JavaScript do cliente — um `anon key` exposto permite, em teoria, ler/alterar qualquer registro da tabela via API REST direta do Supabase, não só pelo token esperado. O padrão mais seguro (usado no `whatsapp-form-token-pattern.md`) é mover essa validação para uma server function com service role, sem policy de `anon` nenhuma. Recomenda-se avaliar essa migração antes de replicar este padrão em um novo projeto.

## Checklist para replicar em um novo domínio de assinatura
1. Definir a tabela de negócio (contrato, termo, aditivo etc.) com o esqueleto: `token`, `status`, `audit jsonb`, `log jsonb`, `expires_at`.
2. Implementar geração de token curto único e cálculo de expiração (7 dias é o padrão observado).
3. Implementar a página pública `/assinar/{token}` (ou equivalente) sem exigir login.
4. Implementar captura de assinatura (canvas de desenho + opção de nome digitado) e o hash de integridade (SHA-256 do conteúdo + nome).
5. Capturar IP público, user-agent e rótulo de dispositivo no momento da visualização e da assinatura.
6. Decidir a estratégia de acesso público: **preferir server function com service role** (mais seguro) em vez de client Supabase direto com `anon` + policy `USING (true)`.
7. Implementar rotina de expiração (`sweepExpired`) chamada periodicamente ou no load do painel.
8. Registrar toda transição relevante no log central de auditoria do projeto, se houver um (aqui: `window.VPLog`).

## Referência
Repositório de origem desta documentação (análise realizada em 2026-07-09): https://github.com/verticalpartsIA/010_vpprd — Módulo Jurídico (`assinar.html`, `assinar-app.jsx`, `contrato-instalador-store.js`, `contrato-venda-store.js`).
Ver também: [whatsapp-form-token-pattern.md](whatsapp-form-token-pattern.md) para o padrão irmão de formulário público via token (mais seguro, usa service role).
