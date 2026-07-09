# Módulo Alçadas — Tutorial de Engenharia (Níveis de Aprovação por Valor)

> **Isto é um tutorial, não um dump de código de produção.** Ensina o raciocínio e os passos para construir um sistema de "alçadas de aprovação" (quem pode aprovar até quanto) do zero, em qualquer projeto Supabase/Postgres novo. Onde for útil aprofundar, aponta para o arquivo real do projeto de origem — mas o objetivo aqui é o **padrão de engenharia**, não o código literal.
>
> Padrão extraído por análise (somente leitura) do módulo de Alçadas em [`verticalpartsIA/003_requisicoes`](https://github.com/verticalpartsIA/003_requisicoes).

## O problema que este padrão resolve
Uma requisição de compra de R$ 200 não deveria exigir a mesma autoridade de aprovação que uma de R$ 10.000. "Alçada" é o nome dado à **faixa de valor que define o nível hierárquico mínimo necessário para aprovar** uma transação. O desafio de engenharia é: onde guardar os limites, como atribuir nível a cada aprovador, quando calcular o nível exigido, e como impedir que alguém sem autoridade aprove mesmo burlando a interface.

## Passo a passo

### 1. Modele os limiares (thresholds) como dado configurável, não como constante no código
Não deixe os valores de corte (ex.: "até R$ 1.500", "R$ 1.500 a R$ 3.500") hardcoded espalhados pelo frontend e backend. Crie uma tabela simples de configuração:

```sql
create table public.settings (
  key   text primary key,
  value text not null,
  updated_at timestamptz not null default now()
);

insert into public.settings (key, value) values
  ('tier1_max', '1500.00'),
  ('tier2_max', '3500.00');
```

Isso permite ao Admin ajustar os limites sem deploy. O frontend deve sempre ler os limites daqui — nunca duplicar o número em dois lugares (essa foi exatamente a razão de existir essa tabela no projeto de origem).

### 2. Atribua um "nível de alçada" a cada aprovador
Adicione a coluna ao cadastro de papéis/usuários (não ao usuário genérico — só faz sentido para quem tem o papel de aprovador):

```sql
alter table public.user_roles
  add column if not exists approval_tier smallint check (approval_tier in (1, 2, 3));

comment on column public.user_roles.approval_tier is
  '1 = nível mais baixo | 2 = intermediário | 3 = mais alto — somente para role=aprovador';
```

Use `check` para restringir aos níveis válidos direto no banco — não confie só em validação de aplicação.

### 3. Calcule o nível exigido no momento certo do fluxo — não na criação do pedido
**Lição de arquitetura real do projeto de origem**: o nível de aprovação não é calculado quando a requisição é aberta, e sim **quando o valor final é conhecido** — no caso de compras, isso é o momento em que a cotação vencedora é escolhida (preço do fornecedor vencedor), não o valor estimado inicial. Calcule com uma função pura, testável, que recebe o valor e os thresholds:

```ts
function getApprovalLevelForValue(totalValue: number, thresholds: { tier1_max: number; tier2_max: number }): 1 | 2 | 3 {
  if (totalValue <= thresholds.tier1_max) return 1;
  if (totalValue <= thresholds.tier2_max) return 2;
  return 3;
}
```

Se o seu domínio tem um momento equivalente de "valor só fica definido depois" (ex.: orçamento fechado, proposta aceita, cotação vencedora), calcule a alçada **nesse momento**, não antes.

### 4. Modele a aprovação como uma entidade própria, não como um campo solto na entidade principal
Crie uma tabela dedicada de aprovação, 1:1 com a entidade que está sendo aprovada:

```sql
create table public.approvals (
  id uuid primary key default gen_random_uuid(),
  requisition_id uuid not null unique references public.requisitions(id) on delete cascade,
  approval_level integer not null check (approval_level between 1 and 3),
  total_value numeric(12,2),
  decision text not null default 'pending' check (decision in ('pending','approved','rejected')),
  justification text,
  approver_id uuid references auth.users(id) on delete set null,
  decided_at timestamptz,
  created_at timestamptz not null default now()
);
```

Isso separa claramente "o pedido" de "a decisão sobre o pedido" — permite auditar quem decidiu, quando e por quê, sem sujar a tabela principal.

### 5. Aplique a regra de autorização no banco (RLS), não só na tela
**Este é o passo mais importante e o mais fácil de esquecer.** Se a checagem de "este usuário pode aprovar este nível?" existir só no frontend, qualquer chamada direta à API/banco contorna a regra. Implemente como função `security definer` + policy de RLS:

```sql
create or replace function private.can_approve_level(target_level integer)
returns boolean
language sql stable security definer
set search_path = public, private
as $$
  select
    private.has_role('admin')  -- admin sempre pode aprovar qualquer nível
    or exists (
      select 1 from public.user_roles
      where user_id = auth.uid()
        and role = 'aprovador'
        and coalesce(approval_tier, 0) >= target_level
    );
$$;

create policy approvals_update_aprovador
on public.approvals for update to authenticated
using (decision = 'pending' and private.can_approve_level(approval_level))
with check (private.can_approve_level(approval_level));
```

A regra "nível do aprovador precisa ser >= nível exigido pela aprovação" fica garantida pelo Postgres, não pela UI.

### 6. Registre toda decisão em log de auditoria
Toda aprovação/reprovação deve gravar um evento (ação, status antes/depois, justificativa) numa tabela de log separada (`audit_logs` no projeto de origem) — não dependa do `updated_at` da própria tabela de aprovação para reconstruir histórico.

### 7. Gere os rótulos de exibição a partir dos mesmos thresholds
Não escreva "Nível 1 — até R$ 1.500" como string fixa em múltiplos componentes de tela. Gere o rótulo a partir da mesma configuração do passo 1:

```ts
function approvalLevelLabels(t: { tier1_max: number; tier2_max: number }) {
  return {
    1: `Nível 1 — até ${fmtBRL(t.tier1_max)}`,
    2: `Nível 2 — ${fmtBRL(t.tier1_max + 0.01)} a ${fmtBRL(t.tier2_max)}`,
    3: `Nível 3 — acima de ${fmtBRL(t.tier2_max)}`,
  };
}
```

## Desenho final (resumo do fluxo)
```
Requisição criada → Cotação (múltiplos fornecedores) → Fornecedor vencedor escolhido
                                                              │
                                                    valor final conhecido
                                                              │
                                              getApprovalLevelForValue(valor)
                                                              │
                                        cria/atualiza `approvals` com approval_level
                                                              │
                              aprovador com approval_tier >= approval_level decide
                                          (garantido por RLS, não só por UI)
                                                              │
                                       decisão + justificativa → log de auditoria
```

## Armadilha real encontrada na origem (vale generalizar)
No projeto de origem existem **duas migrations numeradas de forma colidente** (ambas com prefixo `004`) adicionando fragmentos relacionados de alçada em momentos diferentes — sinal de que a coluna/tabela foi evoluída em mais de uma etapa sem uma migration única consolidada. **Lição para replicar em outro projeto**: ao adicionar um sistema de alçadas, prefira consolidar tudo (coluna + tabela de thresholds + função + policy) numa única migration coesa, ou pelo menos numerá-las sem colisão — não é apenas estética, colisão de prefixo de migration pode confundir a ordem de aplicação.

## Onde aprofundar (arquivos reais do projeto de origem)
- `003_requisicoes/src/lib/approval.ts` — função de cálculo de nível + rótulos
- `003_requisicoes/database/004_approval_tiers_and_admin.sql` — função `can_approve_level` + policy de RLS
- `003_requisicoes/database/004_user_roles_tier_settings.sql` — coluna `approval_tier` + tabela `settings`
- `003_requisicoes/database/001_initial_schema.sql` — schema original da tabela `approvals`
- `003_requisicoes/src/features/approvals/api.ts` — fluxo de listar pendentes / aprovar / reprovar + log de auditoria
- `003_requisicoes/src/features/quotations/api.ts` — ponto exato onde `approval_level` é calculado (ao definir o fornecedor vencedor)

## Requisito de Banco de Dados (Supabase)
**Para que isso funcione você precisa criar no Supabase o seguinte:** as três peças de schema descritas nos passos 1, 2 e 4 acima (`settings`, coluna `approval_tier` em `user_roles`, tabela `approvals`) + a função `can_approve_level` e a policy de RLS do passo 5. Sem RLS aplicada no banco, a alçada é apenas decorativa (só UI).
