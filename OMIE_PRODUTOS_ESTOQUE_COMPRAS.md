# Omie MCP — Produtos, Estoque e Compras

Este documento consolida a visão de negócio do bloco operacional que liga cadastro de produto, estoque, pedidos de compra, nota de entrada e financeiro.

## Objetivo

Permitir que Claude responda perguntas reais como:

- Qual é o estoque atual deste produto?
- Em quais locais ele existe?
- Quais foram as últimas entradas e saídas?
- Há pedido de compra pendente?
- O pedido já foi faturado, recebido ou encerrado?
- Qual nota de entrada está ligada à compra?
- Qual fornecedor aparece no pedido?
- Qual preço unitário foi comprado?
- Qual foi o custo de entrada?
- Existe conta a pagar associada ao fluxo?

## APIs oficiais usadas

### Produtos

Endpoint: `/api/v1/geral/produtos/`

Métodos principais:

- `ListarProdutos`
- `ListarProdutosResumido`
- `ConsultarProduto`
- `IncluirProduto`
- `AlterarProduto`
- `UpsertProduto`
- `ExcluirProduto`

### Consulta de Estoque

Endpoint: `/api/v1/estoque/consulta/`

Métodos principais:

- `PosicaoEstoque`
- `ListarPosEstoque`
- `MovimentoEstoque`
- `ListarMovimentoEstoque`
- `ListarSaldoPendente`

### Pedidos de Compra

Endpoint: `/api/v1/produtos/pedidocompra/`

Métodos principais:

- `PesquisarPedCompra`
- `ConsultarPedCompra`
- `IncluirPedCompra`
- `AlteraPedCompra`
- `UpsertPedCompra`
- `ExcluirPedCompra`

Importante: para listagem/pesquisa o método documentado atualmente é `PesquisarPedCompra`. Não usar nomes presumidos como `ListarPedidosCompra` sem verificar a documentação atual.

### Nota de Entrada

Endpoint: `/api/v1/produtos/notaentrada/`

Métodos principais:

- `ListarNotaEnt`
- `ConsultarNotaEnt`
- `IncluirNotaEnt`
- `AlterarNotaEnt`
- `ExcluirNotaEnt`
- `StatusNotaEnt`

## Ferramentas MCP implementadas

- `omie_produtos_listar`
- `omie_produto_consultar`
- `omie_estoque_posicao`
- `omie_estoque_listar_posicao`
- `omie_estoque_movimentos`
- `omie_pedidos_compra_pesquisar`
- `omie_pedido_compra_consultar`
- `omie_notas_entrada_listar`
- `omie_nota_entrada_consultar`
- `omie_produto_ciclo_compra`

## Fluxo operacional esperado

```text
Produto
  ↓
Produto x Fornecedor
  ↓
Requisição de Compra
  ↓
Pedido de Compra
  ↓
Faturamento / Recebimento
  ↓
Nota de Entrada
  ↓
Movimento de Estoque
  ↓
Posição de Estoque
  ↓
Conta a Pagar
  ↓
Valor Pago / Valor a Pagar
```

## Regra de integridade

O MCP não deve inferir vínculos apenas por proximidade temporal ou descrição textual.

Para correlacionar entidades, priorizar códigos internos do Omie, especialmente:

- código do produto
- código do fornecedor
- código do pedido
- código da nota de entrada
- código do projeto
- código da conta corrente
- código do título financeiro

Quando a API não devolver uma chave inequívoca, retornar as fontes separadas e sinalizar que a correlação precisa ser validada.

## Próxima evolução deste domínio

1. Produto x Fornecedor
2. Requisições de Compra
3. Resumo de Compras
4. Recebimento de NF-e
5. Nota de Entrada - Faturamento
6. custo real por item
7. último preço de compra
8. preço médio de compra
9. lead time por fornecedor
10. ciclo completo Pedido → Entrada → Estoque → Financeiro
