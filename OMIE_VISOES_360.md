# Omie MCP — Visões 360

Este documento descreve as visões compostas de negócio do MCP VerticalParts para o Omie.

## Princípio

Uma visão 360 não é uma tabela inventada. Ela é uma composição controlada de endpoints oficiais ligados por chaves reais do Omie.

O MCP deve sempre distinguir:

- dado direto da API;
- dado enriquecido por outro serviço oficial;
- dado agregado calculado pelo MCP;
- vínculo não disponível de forma seletiva na API.

Quando não existir filtro oficial seguro, a limitação deve aparecer no retorno em vez de ser escondida.

## Cliente 360

Ferramenta:

`omie_cliente_360`

Fontes atuais:

1. `geral/clientes` / `ConsultarCliente`
2. `financas/mf` / `ListarMovimentos` com natureza de Contas a Receber e `nCodCliente`
3. `produtos/pedido` / `ListarPedidos` com `filtrar_por_cliente`

Resumo financeiro calculado pelo MCP:

- quantidade de títulos;
- valor total dos títulos;
- valor recebido;
- valor a receber;
- contagem por status.

Chaves de correlação relevantes:

- `codigo_cliente_omie` ↔ `detalhes.nCodCliente`;
- `pedido.cabecalho.codigo_cliente`;
- `detalhes.nCodOS` / `cNumOS` para Pedido de Venda ou OS quando disponível;
- `detalhes.nCodCtr` / `cNumCtr` para contrato quando disponível.

Perguntas que a visão deve suportar:

- Quanto este cliente ainda nos deve?
- Quanto já recebemos deste cliente?
- Quantos títulos estão vencidos ou parciais?
- Quais pedidos de venda pertencem a este cliente?
- Qual pedido ou contrato originou determinado título quando o Omie publicar a chave no movimento?

## Fornecedor 360

Ferramenta:

`omie_fornecedor_360`

Fontes atuais:

1. `geral/clientes` / `ConsultarCliente`
2. `financas/mf` / `ListarMovimentos` com natureza de Contas a Pagar e `nCodCliente`

Resumo financeiro calculado pelo MCP:

- quantidade de títulos;
- valor total;
- valor pago;
- valor a pagar;
- contagem por status.

Chaves de correlação de compras documentadas pelo Omie:

- `pedido_compra.cabecalho_consulta.nCodFor`;
- `produto_fornecedor.cadastros[].nCodForn`;
- identificação do fornecedor nos recebimentos de NF-e.

### Limitação intencional

O método oficial `PesquisarPedCompra` não publica filtro por fornecedor. Portanto o Fornecedor 360 não percorre indiscriminadamente todas as páginas de pedidos para filtrar localmente. Isso evita custo excessivo, resultados parciais e falsa sensação de precisão.

Quando a Omie adicionar um filtro oficial, o radar de documentação deve detectar a mudança e essa visão poderá ser enriquecida.

## Regra para novas visões

Toda futura visão 360 deve documentar:

1. endpoints usados;
2. chaves de correlação;
3. campos agregados;
4. paginação e limites;
5. campos derivados;
6. limitações conhecidas;
7. testes que validem a correlação.
