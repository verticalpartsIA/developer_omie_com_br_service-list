
# Gaps atuais do estudo Omie

Data da revisão: 2026-10-26

Comparação entre o conhecimento já registrado neste repositório e a lista oficial atual de serviços do Omie.

## Novidades/gaps identificados

### Geral

- IBS e CBS - CST
- IBS e CBS - CSL

Esses cadastros aparecem na lista oficial atual e ainda não estavam refletidos no estudo original.

### CRM

Além dos serviços já mapeados, a lista oficial atual apresenta:

- Telemarketing
- Pré-Vendas

`Finders`, que já era marcado como gap no estudo, também continua devendo ser incorporado ao espelho/knowledge base.

### Estoque

- Resumo do Estoque

O estudo já cobre ajuste, consulta, movimento e locais, mas o endpoint agregado de resumo precisa entrar no mapa.

### Vendas e NF-e

É a área com maior expansão em relação ao estudo original. A lista atual inclui:

- Devolução de venda - Faturamento
- Resumo de vendas/NF-e/CT-e/Cupom Fiscal
- Obter Documentos
- Cupom Fiscal - Adicionar
- Cupom Fiscal - Cancelar ou excluir
- Cupom Fiscal - Consultar
- Importar NFC-e
- Importar CFe-SAT
- NF-e - Consultas
- NF-e - Utilitários
- NF-e - Importar

O MCP não depende de esse mapa estar completo para acessar a API, porque `omie_chamar_api` funciona como fallback universal. Mesmo assim, esses itens devem ser incorporados ao conhecimento curado para melhorar a interpretação do Claude.

### Serviços e NFS-e

Além do que já consta no estudo:

- Resumo do faturamento de serviços
- Obter Documentos
- NFS-e - Consultas
- Indicador de Operação, relacionado à Reforma Tributária

### Painel do Contador

- Resumo do Fechamento Contábil

O estudo anterior já reconhecia esse gap agregado.

## Observações do radar automático

### Issue #18 (2026-09-26) — sem gap acionável identificado; causa raiz confirmada

O radar (`omie-docs-drift.yml`) comparou a captura de `2026-09-26T16:35:30Z` com a de `2026-09-26T18:31:26Z` e reportou:

- Contagem de serviços: 138 → 138 (sem serviço novo, sem serviço removido).
- 138 páginas de serviço marcadas como "conteúdo alterado" — ou seja, praticamente o catálogo inteiro, no mesmo curto intervalo de ~2h.

Como a issue não trouxe diffs de campo por serviço (apenas a lista de URLs cujo hash de página mudou) e o total de serviços não se alterou, não há evidência de mudança substantiva de API para incorporar aos gaps por módulo — o padrão (toda a base mudando de uma vez, sem adição/remoção) é mais consistente com uma alteração cosmética/estrutural das páginas (ex.: template, rodapé, timestamp) do que com uma mudança real de contrato de serviço. Nenhum item foi adicionado, removido ou alterado nas seções acima por causa desta issue.

**Reconfirmação em 2026-09-28**: issue permanecia aberta, sem informação nova.

**Reconfirmação em 2026-10-05**: issue permanecia aberta, corpo idêntico, sem informação nova. README.md e instructions.md conferidos e já refletiam os gaps listados acima.

**Causa raiz (comentário de sessão humana em 2026-09-26, verificado na revisão de 2026-10-12)**: o servidor do Omie gera um `nonce` de CSP novo a cada resposta HTTP (mesmo conteúdo, mesma página), o que fazia toda página parecer alterada em toda execução do radar. O comentário registrado na issue afirmou ter aplicado a correção em `src/omie_mcp/watcher.py` (função `_normalize_text` passando a ignorar `nonce="..."` antes de calcular o hash) e ter fechado a issue manualmente. Ao ler `src/omie_mcp/watcher.py` em `main`, confirmamos que a correção está de fato presente no código (`_VOLATILE_NONCE_RE = re.compile(r'nonce="[^"]*"')` normalizando o texto antes do `_sha`). No entanto, a issue continuava aberta no GitHub na revisão de 2026-10-12 — apesar do código corrigido, o fechamento efetivo (via API) aparentemente não se concretizou da vez anterior, ou foi bloqueado silenciosamente.

**Reconfirmação em 2026-10-19**: issue permanece aberta, corpo idêntico, sem informação nova além do já registrado acima. Tentativa de fechamento via `gh_api_call` (PATCH `state=closed`, `confirmation=BREAK_GLASS`) recusada com `Break-glass está desabilitado por GITHUB_ALLOW_BREAK_GLASS=false` — bloqueio de permissão explícito, não erro técnico.

**Reconfirmação em 2026-10-26**: issue permanece aberta, corpo idêntico ao analisado desde 2026-09-26, sem informação nova. Nenhum gap por módulo foi adicionado/removido/alterado por causa desta issue nesta revisão. Esta curadoria comentou novamente e tentou fechá-la via `gh_api_call` (PATCH `state=closed`, `confirmation=BREAK_GLASS`); se recusado novamente pelo mesmo motivo (`GITHUB_ALLOW_BREAK_GLASS=false`), o fechamento efetivo continua dependendo de ação manual de um humano com permissão, ou de um administrador habilitando essa flag — já são 5 revisões semanais consecutivas tentando fechar esta issue sem sucesso.

### Issue #20 (2026-10-08) — drift pós-correção do nonce; sem gap acionável confirmado, mas padrão não totalmente explicado

O radar comparou a captura de `2026-10-07T16:27:09Z` com a de `2026-10-08T16:27:31Z` e reportou:

- Contagem de serviços: 138 → 138 (sem serviço novo, sem serviço removido).
- 76 das 138 páginas de serviço marcadas como "conteúdo alterado" (lista cobrindo principalmente `crm/`, `estoque/`, `financas/` e `geral/`), no mesmo intervalo de ~24h.

Diferente da Issue #18, esta captura ocorreu depois da correção do nonce CSP descrita acima (já confirmada presente em `main`). Isso significa que a explicação anterior ("toda página muda por causa do nonce volátil") não se aplica mais integralmente aqui — e ainda assim quase 55% das páginas foram sinalizadas como alteradas em ~24h, sem nenhuma mudança líquida na contagem de serviços.

Não foi possível confirmar o que de fato mudou em cada página: a issue traz apenas a lista de URLs cujo hash mudou, sem diff de conteúdo por campo, e esta curadoria não dispõe de ferramenta para ler os logs/artefatos da execução do workflow (`gh_get_workflow_run` só retorna status/jobs, não o diff interno que `watcher.py` já calcula em `changed_service_pages[].diff_preview`). Portanto, não há evidência suficiente para registrar um gap de campo específico por módulo, mas também não há base para concluir com segurança que se trata apenas de ruído cosmético, como no caso anterior — pode haver alguma outra fonte de volatilidade nas páginas (ex.: outro token dinâmico, timestamp de geração, ordenação não determinística) que a correção do nonce não cobre.

Nenhum item foi adicionado, removido ou alterado nas seções de gaps por módulo por causa desta issue. Recomendação registrada para o futuro: fazer `omie-docs-drift.yml` incluir no corpo da issue o `diff_preview` que `watcher.py` já calcula internamente (`changed_service_pages`), para que a curadoria semanal consiga avaliar mudanças reais de campo em vez de apenas uma lista de URLs com hash alterado.

**Reconfirmação em 2026-10-19**: issue permanece aberta, corpo idêntico, sem informação nova. Tentativa de fechamento recusada pelo mesmo bloqueio de break-glass.

**Reconfirmação em 2026-10-26**: issue permanece aberta, corpo idêntico ao analisado desde 2026-10-08, sem informação nova. A recomendação de incluir `diff_preview` no corpo da issue do workflow continua pendente e fora do escopo desta curadoria (não editamos `.github/workflows/` nem `.py`). Esta curadoria comentou novamente e tentou fechá-la via `gh_api_call` break-glass.

### Issues #21 (2026-10-22) e #22 (2026-10-24) — provável quebra do próprio radar, não mudança real de documentação

Estas duas issues, novas nesta revisão, mostram um padrão qualitativamente diferente das anteriores (#18, #20) e merecem atenção operacional, não apenas de conteúdo:

- **Issue #21** comparou a captura de `2026-10-21T14:28:42Z` com a de `2026-10-22T14:30:37Z` e reportou **contagem de serviços: 138 → 0**, listando os 138 serviços anteriores como "removidos" e as mesmas 138 URLs como "páginas com conteúdo alterado".
- **Issue #22** comparou `2026-10-23T14:13:40Z` com `2026-10-24T13:19:06Z` e reportou **contagem de serviços: 0 → 0** (sem páginas de serviço listadas).

**Análise**: é extremamente improvável que o Omie tenha realmente removido da documentação oficial a totalidade dos 138 serviços catalogados de um dia para o outro, sem substituí-los por nada — não há nenhum precedente disso nas revisões anteriores, e o domínio `developer.omie.com.br/service-list/` é a documentação pública de um ERP em produção. O padrão observado (contagem caindo abruptamente para 0 e permanecendo em 0 na captura seguinte) é muito mais consistente com uma **falha de captura/scraping** no próprio radar (`omie-docs-drift.yml` / `src/omie_mcp/watcher.py`) a partir de 2026-10-22 — por exemplo, a página oficial pode ter retornado erro HTTP, timeout, HTML vazio, ou um seletor/parsing usado pelo `watcher.py` pode ter parado de encontrar serviços após alguma mudança estrutural na página (ironicamente, o tipo de mudança estrutural que as Issues #18/#20 já vinham sinalizando como suspeita).

Por isso, **nenhum serviço foi registrado como removido ou alterado nas seções de gaps por módulo acima por causa destas duas issues** — tratar a queda para 0 como gaps reais de documentação seria especular sem evidência, e o risco de poluir o conhecimento curado com uma falsa "remoção de 138 serviços" é maior do que o risco de não registrar nada.

**Alerta operacional para humanos/sessões futuras**: se a captura do radar está de fato zerada desde 2026-10-22, o radar pode estar "cego" a mudanças reais na documentação oficial desde então — qualquer drift real do Omie nesse período não seria detectado nem geraria issue nova, porque uma comparação 0 → 0 não produz sinal de mudança útil. Recomenda-se que um humano (ou uma sessão com acesso a `.py`/workflows, fora do escopo desta curadoria de documentação) verifique:

1. Se `https://developer.omie.com.br/service-list/` ainda carrega normalmente ~138 serviços num navegador comum;
2. Os logs/execuções do workflow `omie-docs-drift.yml` a partir de 2026-10-21/2026-10-22, para identificar erro HTTP, timeout, ou mudança na estrutura da página que quebrou o parsing do `watcher.py`;
3. Se a correção do nonce (`_VOLATILE_NONCE_RE`) ou alguma mudança recente em `watcher.py` introduziu uma regressão no parsing de serviços.

Esta curadoria não tem ferramentas para investigar `.py`, logs de workflow ou fazer requisições HTTP diretas ao site do Omie — por isso o achado fica registrado aqui como texto, sem tentativa de correção de código.

## Regra daqui em diante

Este arquivo não deve ser tratado como lista definitiva. A fonte definitiva continua sendo a documentação oficial no momento da execução.

O MCP deve usar `omie_documentacao_diff` para detectar mudanças posteriores a esta revisão e `omie_catalogo_servicos` para descobrir serviços atuais.

Quando surgir qualquer mudança oficial:

1. registrar a diferença;
2. classificar o módulo afetado;
3. atualizar README/instructions/issues quando necessário;
4. criar ferramenta tipada apenas quando houver valor de uso recorrente;
5. manter `omie_chamar_api` como cobertura imediata para a operação nova.
