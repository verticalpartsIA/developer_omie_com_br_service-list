
# Gaps atuais do estudo Omie

Data da revisão: 2026-10-05

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

### Issue #18 (2026-09-26) — sem gap acionável identificado

O radar (`omie-docs-drift.yml`) comparou a captura de `2026-09-26T16:35:30Z` com a de `2026-09-26T18:31:26Z` e reportou:

- Contagem de serviços: 138 → 138 (sem serviço novo, sem serviço removido).
- 138 páginas de serviço marcadas como "conteúdo alterado" — ou seja, praticamente o catálogo inteiro, no mesmo curto intervalo de ~2h.

Como a issue não trouxe diffs de campo por serviço (apenas a lista de URLs cujo hash de página mudou) e o total de serviços não se alterou, não há evidência de mudança substantiva de API para incorporar aos gaps por módulo — o padrão (toda a base mudando de uma vez, sem adição/remoção) é mais consistente com uma alteracão cosmética/estrutural das páginas (ex.: template, rodapé, timestamp) do que com uma mudança real de contrato de serviço. Nenhum item foi adicionado, removido ou alterado nas seções acima por causa desta issue.

Se o radar voltar a acusar drift, vale revisar se `omie-docs-drift.yml` pode passar a incluir um diff de conteúdo por página (não só a lista de URLs), para que mudanças reais de campo fiquem acionáveis por esta curadoria.

**Reconfirmação em 2026-09-28**: a Issue #18 permanecia aberta no GitHub nesta data (curadoria semanal seguinte). Não há informação nova além do que já está registrado acima — mesma issue, mesmo conteúdo, mesma conclusão de "sem gap acionável". O fechamento efetivo da issue depende de uma ação manual de um humano (a ferramenta de fechamento automático via API está bloqueada por padrão neste ambiente).

**Reconfirmação em 2026-10-05**: a Issue #18 permanecia aberta no GitHub nesta data (curadoria semanal seguinte). O corpo da issue continua idêntico (mesmas capturas `2026-09-26T16:35:30Z` → `2026-09-26T18:31:26Z`, mesma contagem 138 → 138, mesmo hash de drift registrado na issue). Nenhuma informação nova para incorporar; conclusão mantida: sem gap acionável. README.md e instructions.md foram conferidos novamente e já refletem os itens listados nas seções acima, então não foram alterados nesta revisão. O fechamento efetivo da issue continua dependendo de ação manual de um humano.

## Regra daqui em diante

Este arquivo não deve ser tratado como lista definitiva. A fonte definitiva continua sendo a documentação oficial no momento da execução.

O MCP deve usar `omie_documentacao_diff` para detectar mudanças posteriores a esta revisão e `omie_catalogo_servicos` para descobrir serviços atuais.

Quando surgir qualquer mudança oficial:

1. registrar a diferença;
2. classificar o módulo afetado;
3. atualizar README/instructions/issues quando necessário;
4. criar ferramenta tipada apenas quando houver valor de uso recorrente;
5. manter `omie_chamar_api` como cobertura imediata para a operação nova.
