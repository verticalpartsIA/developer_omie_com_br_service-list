# Omie — Contas a Pagar: mapeamento do relatório para API/MCP

Este documento registra como reconstruir, via API, a visão operacional do relatório de Contas a Pagar do Omie.

## Regra principal

Para perguntas sobre situação financeira realizada, **não usar apenas** `/api/v1/financas/contapagar/`.

O endpoint de Contas a Pagar contém o cadastro do título e expõe `valor_pag` como "Valor a pagar" em consulta/listagem, mas o endpoint mais completo para o realizado é:

- `/api/v1/financas/mf/`
- método `ListarMovimentos`
- `cTpLancamento = "CP"`
- `cNatureza = "P"`

No objeto `resumo` retornado por Movimentos Financeiros:

| Informação de negócio | Campo Omie |
|---|---|
| Valor Pago | `nValPago` |
| Valor a Pagar / Em Aberto | `nValAberto` |
| Valor Líquido | `nValLiquido` |
| Desconto | `nDesconto` |
| Juros | `nJuros` |
| Multa | `nMulta` |
| Liquidado | `cLiquidado` |

Esses campos devem ser tratados como fonte oficial para o MCP quando a pergunta for "quanto pagamos?" ou "quanto falta pagar?".

## Cabeçalho do relatório e origem provável

| # | Coluna do relatório | Fonte principal no MCP/API |
|---:|---|---|
| 1 | Situação | MF `detalhes.cStatus` / CP `status_titulo` |
| 2 | Número do Documento | MF `detalhes.cNumTitulo` / CP `numero_documento` |
| 3 | Parcela | MF `detalhes.cNumParcela` / CP `numero_parcela` |
| 4 | Nota Fiscal | MF `detalhes.cNumDocFiscal` / CP `numero_documento_fiscal` |
| 5 | Fornecedor (Nome Fantasia) | enriquecer com `/geral/clientes/` usando `nCodCliente` |
| 6 | Previsão de Pagamento | MF `detalhes.dDtPrevisao` / CP `data_previsao` |
| 7 | Último Pagamento | MF `detalhes.dDtPagamento` |
| 8 | Valor da Conta | MF `detalhes.nValorTitulo` / CP `valor_documento` |
| 9 | Valor Líquido | MF `resumo.nValLiquido` |
| 10 | Impostos Retidos | somatório de PIS/COFINS/CSLL/IR/ISS/INSS retidos |
| 11 | Desconto | MF `resumo.nDesconto` |
| 12 | Juros e Multa | MF `resumo.nJuros` + `resumo.nMulta` |
| 13 | Valor Pago | **MF `resumo.nValPago`** |
| 14 | Valor a Pagar | **MF `resumo.nValAberto`**; CP também expõe `valor_pag` |
| 15 | Categoria | MF `detalhes.cCodCateg`, enriquecer com `/geral/categorias/` |
| 16 | Operação | MF `detalhes.cOperacao` / CP `operacao` |
| 17 | Vendedor | MF `detalhes.cCodVendedor`, enriquecer com vendedores |
| 18 | Projeto | MF `detalhes.cCodProjeto`, enriquecer com projetos |
| 19 | Conta Corrente | MF `detalhes.nCodCC`, enriquecer com conta corrente |
| 20 | Tipo de Documento | MF `detalhes.cTipo`, enriquecer com `/geral/tiposdoc/` |
| 21 | Vencimento | MF `detalhes.dDtVenc` / CP `data_vencimento` |
| 22 | Data de Emissão | MF `detalhes.dDtEmissao` / CP `data_emissao` |
| 23 | Data de Registro | MF `detalhes.dDtRegistro` / CP `data_entrada` |
| 24 | Fornecedor (Razão Social) | `/geral/clientes/` |
| 25 | Fornecedor (CNPJ/CPF) | MF `detalhes.cCPFCNPJCliente` + `/geral/clientes/` |
| 26 | Tags do Fornecedor | `/geral/clientetag/` ou cadastro de clientes |
| 27 | Observação | MF `detalhes.observacao` / CP `observacao` |
| 28 | Inclusão | MF `detalhes.dDtInc` ou CP `info.dInc` |
| 29 | Última Alteração | MF `detalhes.dDtAlt` ou CP `info.dAlt` |
| 30 | Incluído por | MF `detalhes.cUsInc` ou CP `info.uInc` |
| 31 | Alterado por | MF `detalhes.cUsAlt` ou CP `info.uAlt` |
| 32 | Considera no fluxo e extrato? | validar no payload real/relatório; não presumir sem evidência do campo correspondente |

## Campos financeiros que não podem ser simplificados

Não derivar `valor_pago` apenas como `valor_documento - valor_a_pagar`, porque o título pode conter desconto, juros, multa, retenções e baixas parciais.

A visão financeira deve preservar os valores oficiais retornados em `resumo` pelo endpoint de Movimentos Financeiros.

## Ferramentas MCP implementadas

### `omie_contas_pagar_financeiro`

Lista contas a pagar usando `ListarMovimentos` e normaliza os principais campos do relatório, incluindo:

- `valor_conta`
- `valor_pago`
- `valor_a_pagar`
- `valor_liquido`
- `desconto`
- `juros`
- `multa`
- `situacao`
- `ultimo_pagamento`
- IDs de fornecedor, categoria, vendedor, projeto e conta corrente

### `omie_conta_pagar_situacao_financeira`

Recebe `codigo_lancamento_omie` e consulta diretamente a situação financeira do título.

Exemplos de perguntas que o Claude deve conseguir responder:

- Quanto já pagamos desta conta?
- Quanto ainda falta pagar?
- Quais títulos estão parcialmente pagos?
- Quanto temos em aberto para o fornecedor X?
- Quanto foi pago no mês e quanto ficou em aberto?
- Quais contas estão atrasadas e qual é o saldo em aberto?

## Próximo enriquecimento

A próxima camada deve resolver IDs para descrições e reconstruir as 32 colunas com nomes humanos, fazendo joins de API com:

- Clientes/Fornecedores
- Tags
- Categorias
- Projetos
- Contas Correntes
- Tipos de Documento
- Vendedores

A saída ideal será uma ferramenta `omie_contas_pagar_relatorio_completo`, equivalente à visão exportada do ERP, mas retornada de forma estruturada ao Claude.
