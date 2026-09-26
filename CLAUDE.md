# CLAUDE.md

Leia nesta ordem:

1. `instructions.md` — mapa funcional do conhecimento Omie/VerticalParts.
2. `README.md` — espelho Omie ↔ Supabase e módulos.
3. `MCP_OMIE.md` — servidor MCP vivo e regras de segurança.
4. `OMIE_GAPS_ATUAIS.md` — diferenças encontradas na revisão de 2026-09-10.
5. Issue do módulo específico quando a tarefa exigir regra de negócio detalhada.

## Regra principal para trabalhar com Omie

Não assuma que o conhecimento versionado é a versão mais nova da API.

Quando o MCP estiver disponível:

- use `omie_catalogo_servicos` para descobrir os serviços atualmente publicados;
- use `omie_documentacao_diff` para verificar mudanças desde o último snapshot;
- use `omie_inspecionar_servico` para investigar um endpoint;
- use ferramentas tipadas para operações frequentes;
- use `omie_chamar_api` como fallback quando uma operação oficial ainda não tiver ferramenta dedicada.

## Segurança

Nunca grave `OMIE_APP_KEY` ou `OMIE_APP_SECRET` em código, Markdown, issue, commit ou PR.

Operações de escrita devem permanecer desabilitadas por padrão. Só execute uma mutação quando `OMIE_ALLOW_WRITES=true` e a chamada tiver confirmação explícita (`confirm_write=true`).

## Princípio de cobertura

A cobertura do MCP não deve ser medida apenas pela quantidade de ferramentas tipadas. O servidor é considerado coberto quando consegue:

1. descobrir o serviço oficial atual;
2. identificar mudanças na documentação;
3. chamar o endpoint oficial por fallback universal;
4. oferecer atalhos tipados para os fluxos mais frequentes;
5. bloquear mutações acidentais.
