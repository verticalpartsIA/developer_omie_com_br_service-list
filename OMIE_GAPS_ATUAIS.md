# Gaps atuais do estudo Omie

Data da revisão: 2026-09-10

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

## Regra daqui em diante

Este arquivo não deve ser tratado como lista definitiva. A fonte definitiva continua sendo a documentação oficial no momento da execução.

O MCP deve usar `omie_documentacao_diff` para detectar mudanças posteriores a esta revisão e `omie_catalogo_servicos` para descobrir serviços atuais.

Quando surgir qualquer mudança oficial:

1. registrar a diferença;
2. classificar o módulo afetado;
3. atualizar README/instructions/issues quando necessário;
4. criar ferramenta tipada apenas quando houver valor de uso recorrente;
5. manter `omie_chamar_api` como cobertura imediata para a operação nova.
