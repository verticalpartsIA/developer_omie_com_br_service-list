# Relatório Omie — Contas a Receber

Mapeamento do cabeçalho exportado pelo Omie para a API oficial e para a visão financeira do MCP.

> O cabeçalho informado possui **37 colunas**.

## Regra principal

Para perguntas de saldo realizado, não usar apenas o cadastro do título.

- **Valor Recebido**: `resumo.nValPago` em `/financas/mf/` → `ListarMovimentos`
- **Valor a Receber**: `resumo.nValAberto` em `/financas/mf/` → `ListarMovimentos`

O cadastro de Contas a Receber continua sendo importante para dados do título, boleto, integrações e campos específicos. A visão final deve combinar título + movimentos + cadastros auxiliares.

## Cabeçalho do relatório

| # | Cabeçalho | Fonte/estratégia no MCP |
|---|---|---|
| 1 | Situação | Movimento financeiro / status do título |
| 2 | Número do Documento | Movimento financeiro / título |
| 3 | Parcela | Movimento financeiro / título |
| 4 | Nota Fiscal / Cupom Fiscal | Movimento financeiro / origem fiscal |
| 5 | Cliente (Nome Fantasia) | Enriquecer via Clientes |
| 6 | Previsão de Recebimento | Movimento financeiro / título |
| 7 | Último Recebimento | Movimento financeiro |
| 8 | Valor da Conta | `nValorTitulo` |
| 9 | Valor Líquido | `resumo.nValLiquido` |
| 10 | Impostos Retidos | Título + detalhamento fiscal quando disponível |
| 11 | Desconto | `resumo.nDesconto` |
| 12 | Juros e Multa | `resumo.nJuros + resumo.nMulta` |
| 13 | Valor Recebido | `resumo.nValPago` |
| 14 | Valor a Receber | `resumo.nValAberto` |
| 15 | Categoria | Código no movimento; enriquecer via Categorias |
| 16 | Operação | Movimento financeiro |
| 17 | Vendedor | Código; enriquecer via Vendedores |
| 18 | Projeto | Código; enriquecer via Projetos |
| 19 | Conta Corrente | Código; enriquecer via Contas Correntes |
| 20 | Número do Boleto | Contas a Receber / Boletos |
| 21 | Tipo de Documento | Código; enriquecer via Tipos de Documento |
| 22 | Duplicata Descontada | Contas a Receber / movimento, validar semântica por operação |
| 23 | Número NSU (Cupom Fiscal) | Movimento financeiro/origem de cartão/cupom |
| 24 | Vencimento | Movimento financeiro / título |
| 25 | Data de Emissão | Movimento financeiro / título |
| 26 | Data de Registro | Movimento financeiro / título |
| 27 | Cliente (Razão Social) | Enriquecer via Clientes |
| 28 | Cliente (CNPJ/CPF) | Movimento/Clientes |
| 29 | Nº do Pedido do Cliente | Título/origem de pedido; enriquecer via Vendas quando necessário |
| 30 | Nº do Contrato de Venda | Título/origem contratual; enriquecer quando necessário |
| 31 | Tags do Cliente | Clientes/Tags |
| 32 | Observação | Título/movimento |
| 33 | Inclusão | Auditoria do título/movimento |
| 34 | Última Alteração | Auditoria do título/movimento |
| 35 | Incluído por | Auditoria do título/movimento |
| 36 | Alterado por | Auditoria do título/movimento |
| 37 | Considera no fluxo e extrato? | Validar campo exato do contrato atual; nunca inferir por nome aproximado |

## Ferramentas do MCP

### `omie_contas_receber_listar`
Visão cadastral direta de `/financas/contareceber/`.

### `omie_contas_receber_financeiro`
Visão recomendada para perguntas como:

- quanto já recebemos;
- quanto ainda falta receber;
- títulos em aberto/vencidos/parciais;
- exposição por cliente ou projeto.

### `omie_conta_receber_situacao_financeira`
Consulta de um título específico pelo `codigo_lancamento_omie`.

## Princípio de fidelidade

Se uma coluna do relatório depender de outra API, o MCP deve enriquecer o dado. Se a semântica não estiver confirmada na documentação atual, retornar `null`/pendente de enriquecimento é preferível a inventar uma equivalência.
