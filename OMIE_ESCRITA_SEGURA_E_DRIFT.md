# Escrita Segura e Radar Forever

## Objetivo

Permitir operações mutáveis no Omie sem transformar o MCP em um agente perigoso, e manter a integração consciente de mudanças futuras na documentação oficial.

## Barreiras de escrita

Toda escrita tipada exige simultaneamente:

1. `OMIE_ALLOW_WRITES=true` no ambiente;
2. `confirmar=true` na ferramenta semântica;
3. `motivo` auditável com pelo menos 5 caracteres;
4. validação mínima dos campos obrigatórios antes do envio;
5. `confirm_write=true` no cliente universal.

Sem qualquer uma dessas condições a operação é bloqueada.

## Escritas tipadas iniciais

- `omie_cliente_upsert_seguro` -> `geral/clientes` / `UpsertCliente`
- `omie_conta_pagar_upsert_seguro` -> `financas/contapagar` / `UpsertContaPagar`
- `omie_conta_receber_upsert_seguro` -> `financas/contareceber` / `UpsertContaReceber`
- `omie_pagamento_lancar_seguro` -> `financas/contapagar` / `LancarPagamento`
- `omie_recebimento_lancar_seguro` -> `financas/contareceber` / `LancarRecebimento`

Exclusões, cancelamentos e faturamentos destrutivos não foram expostos como tools semânticas nesta etapa. Continuam possíveis apenas via fallback universal quando writes estiverem explicitamente habilitadas e confirmadas.

## Radar diário de documentação

Workflow: `.github/workflows/omie-docs-drift.yml`

Execução:
- diária;
- também manual via `workflow_dispatch`;
- restaura o snapshot mais recente via GitHub Actions Cache;
- executa varredura profunda da lista de serviços e das páginas individuais;
- gera `omie-docs-diff.json`;
- publica o relatório como artifact por 30 dias;
- salva o novo snapshot para a próxima execução.

Primeira execução cria a baseline. As seguintes detectam:
- serviço adicionado/removido;
- mudanças de metadados do catálogo;
- mudança textual na lista oficial;
- mudança em qualquer página individual monitorada;
- alteração de hash mesmo quando a mudança for pequena, como pontuação ou novo campo.

## Princípio

O MCP deve ser conservador ao escrever e agressivo ao observar mudanças da documentação.
