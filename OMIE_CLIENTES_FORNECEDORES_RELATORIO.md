# Relatório Omie — Cadastro de Clientes e Fornecedores

Mapeamento do cabeçalho exportado pelo Omie para a API oficial `v1/geral/clientes` e endpoints auxiliares.

> O cabeçalho informado possui **36 colunas**.

## Regra de arquitetura para o MCP

O MCP deve distinguir três tipos de informação:

1. **Campo direto do cadastro**: vem de `ConsultarCliente`/`ListarClientes`.
2. **Campo enriquecido**: o cadastro traz um código e o MCP resolve a descrição em outro endpoint.
3. **Campo derivado/relatório**: não deve ser inventado. Deve ser calculado ou obtido cruzando outras APIs, principalmente Financeiro.

## Mapeamento das 36 colunas

| # | Cabeçalho Omie | Origem recomendada | Campo / estratégia | Situação |
|---|---|---|---|---|
| 1 | Situação | Clientes | `inativo` -> Ativo/Inativo | Direto |
| 2 | Tags | Clientes / Tags | `tags[].tag` | Direto |
| 3 | CNPJ / CPF | Clientes | `cnpj_cpf` | Direto |
| 4 | Razão Social / Nome Completo | Clientes | `razao_social` | Direto |
| 5 | Nome Fantasia / Nome Abreviado | Clientes | `nome_fantasia` | Direto |
| 6 | Telefone | Clientes | `telefone1_ddd` + `telefone1_numero` | Direto |
| 7 | Contato | Clientes | `contato` | Direto |
| 8 | E-mail | Clientes | `email` | Direto |
| 9 | Cidade | Clientes | `cidade` / `cidade_ibge`, podendo enriquecer via Cidades | Direto/enriquecido |
| 10 | Estado | Clientes | `estado` | Direto |
| 11 | Endereço | Clientes | `endereco`, `endereco_numero`, `complemento` | Direto |
| 12 | Bairro | Clientes | `bairro` | Direto |
| 13 | CEP | Clientes | `cep` | Direto |
| 14 | Banco | Clientes | `dadosBancarios.codigo_banco`, enriquecer via Bancos | Direto/enriquecido |
| 15 | Agência | Clientes | `dadosBancarios.agencia` | Direto |
| 16 | Conta Corrente | Clientes | `dadosBancarios.conta_corrente` | Direto |
| 17 | Inscrição Estadual | Clientes | `inscricao_estadual` | Direto |
| 18 | Contribuinte do ICMS | Clientes | `contribuinte` | Direto |
| 19 | Inscrição Municipal | Clientes | `inscricao_municipal` | Direto |
| 20 | Tipo de Atividade | Clientes / Tipos de Atividade | `tipo_atividade`, resolver descrição em `/geral/tpativ/` | Enriquecido |
| 21 | Número de Parcelas (padrão) | Clientes | `recomendacoes.numero_parcelas` | Direto |
| 22 | Vendedor (padrão) | Clientes / Vendedores | `recomendacoes.codigo_vendedor`, resolver nome do vendedor | Enriquecido |
| 23 | E-mail para NF-e e Boleto | Clientes | `recomendacoes.email_fatura` | Direto |
| 24 | Boleto ao Emitir NF-e | Clientes | `recomendacoes.gerar_boletos` | Direto |
| 25 | Faturamento Bloqueado | Clientes | `bloquear_faturamento` | Direto |
| 26 | Crédito Total | Clientes | `valor_limite_credito` | Direto |
| 27 | Total a Receber | Financeiro | somatório oficial de títulos/abertos em Contas a Receber / Movimentos Financeiros para `codigo_cliente_omie` | Derivado |
| 28 | Crédito Disponível | Clientes + Financeiro | não assumir fórmula sem validação do relatório Omie; candidato: limite de crédito menos exposição financeira elegível | Derivado a validar |
| 29 | Integração Automática | Clientes | verificar semântica exata do relatório. `info.cImpAPI`/`importado_api` indica origem via API, mas não deve ser rotulado automaticamente como “Integração Automática” sem confirmação | Gap semântico |
| 30 | Características | Clientes / Clientes-Características | `caracteristicas[]` e/ou `/geral/clientescaract/` | Direto/enriquecido |
| 31 | Transportadora | Clientes | `recomendacoes.codigo_transportadora`, resolver cadastro correspondente | Enriquecido |
| 32 | Inclusão | Clientes | `info.dInc` + `info.hInc` | Direto |
| 33 | Última Alteração | Clientes | `info.dAlt` + `info.hAlt` | Direto |
| 34 | Incluído por | Clientes | `info.uInc` | Direto |
| 35 | Alterado por | Clientes | `info.uAlt` | Direto |
| 36 | Monitoramento | — | campo não identificado com segurança no contrato público de `ClientesCadastro`; preservar como gap e investigar no relatório/interface Omie antes de implementar | Gap |

## Campos adicionais relevantes que a API entrega e o relatório não evidencia no cabeçalho

O MCP deve preservar também campos úteis como:

- `codigo_cliente_omie`
- `codigo_cliente_integracao`
- `telefone2_*`
- `homepage`
- `optante_simples_nacional`
- `cnae`
- `produtor_rural`
- `observacao`
- `obs_detalhadas`
- `pessoa_fisica`
- `exterior`
- `cidade_ibge`
- `dadosBancarios.cChavePix`
- `dadosBancarios.transf_padrao`
- `enderecoEntrega`
- `bloquear_exclusao`

## Ferramentas MCP desejadas

- `omie_clientes_fornecedores_listar_completo`
- `omie_cliente_fornecedor_consultar`
- `omie_cliente_fornecedor_visao_360`
- `omie_cliente_credito_exposicao`
- `omie_clientes_por_tag`
- `omie_clientes_bloqueados_faturamento`
- `omie_fornecedores_dados_bancarios`

### Visão 360

`omie_cliente_fornecedor_visao_360` deve combinar, conforme necessário:

- cadastro completo de Clientes;
- Tags;
- Características;
- vendedor padrão;
- transportadora padrão;
- banco/dados bancários;
- contas a receber em aberto;
- contas a pagar quando o cadastro também atuar como fornecedor;
- pedidos de venda/compra relacionados;
- documentos fiscais relacionados.

## Regras importantes

- `Total a Receber` não deve ser lido de `valor_limite_credito`.
- `Crédito Disponível` não deve ser calculado por uma fórmula presumida sem validação contra o relatório real do Omie.
- `Integração Automática` não deve ser confundida automaticamente com `importado_api`.
- `Monitoramento` permanece como campo a investigar.
- Na listagem completa, usar `exibir_caracteristicas="S"` quando o objetivo for reproduzir o relatório exportado.
