# VerticalParts Omie MCP

MCP vivo para Claude e Claude Code acessar o ERP Omie com cobertura ampla da API oficial, visões de negócio enriquecidas e detecção automática de mudanças na documentação.

Referência oficial: https://developer.omie.com.br/service-list/

## O que este repositório é agora

Este projeto reúne quatro camadas que se complementam:

1. **MCP Omie**: servidor Python/FastMCP para consultar o ERP e, quando explicitamente habilitado, executar operações de escrita.
2. **Catálogo vivo**: descoberta dos serviços publicados atualmente pelo Omie, sem depender apenas de uma lista fixa codificada.
3. **Base de conhecimento**: documentação por módulo, relatórios reais exportados do Omie, regras de negócio e mapeamentos usados por IA.
4. **Espelho analítico Omie → Supabase**: schema e conhecimento para persistir e cruzar entidades do ERP em PostgreSQL.

A meta não é criar centenas de funções cegas. A meta é permitir que Claude entenda o ERP, descubra o que existe hoje, perceba quando a Omie muda algo e responda usando a melhor fonte para cada pergunta.

## Princípio central

Um campo visto pelo usuário no Omie nem sempre vem de um único endpoint.

Exemplo: em Contas a Pagar, o relatório mostra **Valor Pago** e **Valor a Pagar**. A visão financeira correta usa Movimentos Financeiros:

- `resumo.nValPago` → Valor Pago
- `resumo.nValAberto` → Valor a Pagar

Em Contas a Receber:

- `resumo.nValPago` → Valor Recebido
- `resumo.nValAberto` → Valor a Receber

Por isso o MCP trabalha com dois níveis:

- **API bruta**: resposta fiel do endpoint oficial;
- **visão de negócio**: combinação e enriquecimento de várias APIs para reproduzir a informação que uma pessoa realmente usa no Omie.

## Arquitetura

```text
Claude / Claude Code
        │
        ▼
VerticalParts Omie MCP
        │
        ├── ferramentas tipadas
        │     ├── clientes/fornecedores
        │     ├── contas a pagar
        │     ├── contas a receber
        │     ├── produtos
        │     ├── pedidos de compra
        │     └── pedidos de venda
        │
        ├── omie_chamar_api
        │     └── fallback universal para qualquer endpoint oficial
        │
        ├── omie_catalogo_servicos
        │     └── catálogo atual do portal Omie
        │
        ├── omie_inspecionar_servico
        │     └── inspeção de serviço/calls
        │
        └── omie_documentacao_diff
              └── radar de mudanças

Omie REST API
        │
        ├── Geral
        ├── CRM
        ├── Finanças
        ├── Compras / Estoque / Produção
        ├── Vendas / NF-e
        ├── Serviços / NFS-e
        └── Painel do Contador
```

## Cobertura oficial observada em setembro de 2026

O catálogo oficial atual inclui, entre outros:

| Domínio | Serviços relevantes |
|---|---|
| Geral | Clientes/Fornecedores, características, tags, projetos, empresas, departamentos, categorias, parcelas, anexos, IBS/CBS CST e CSL |
| CRM | Contas, contatos, oportunidades, tarefas, finders, vendedores, telemarketing, pré-vendas e auxiliares |
| Finanças | Contas correntes, lançamentos, Contas a Pagar, Contas a Receber, boletos, PIX, extrato, caixa, pesquisa de títulos, movimentos e resumo |
| Compras | Produtos, requisições, pedidos de compra, ordens de produção, notas de entrada, recebimento de NF-e e resumo |
| Estoque | Ajustes, consulta, movimentos, locais e resumo de estoque |
| Vendas | Pedidos, faturamento, etapas, CT-e, remessas, devoluções, resumo e documentos fiscais |
| Cupom Fiscal | Adição, cancelamento/exclusão, consulta, importação NFC-e e CFe-SAT |
| NF-e | Consultas, utilitários e importação |
| Serviços | Serviços, OS, contratos, faturamentos, resumo e documentos |
| NFS-e | Consultas e cadastros auxiliares fiscais/municipais |
| Reforma Tributária | Indicador de Operação, IBS/CBS CST e CSL |
| Painel do Contador | Documentos fiscais e resumo de fechamento contábil |

O arquivo `OMIE_GAPS_ATUAIS.md` registra diferenças entre o estudo histórico do repositório e o catálogo oficial atual.

## Ferramentas fundamentais

### Descoberta e sobrevivência a mudanças

`omie_catalogo_servicos`

Descobre os serviços publicados no portal oficial no momento da execução.

`omie_inspecionar_servico`

Inspeciona um serviço específico e identifica operações/calls documentadas.

`omie_documentacao_diff`

Compara snapshots da documentação. Detecta serviços adicionados/removidos, alterações de páginas e mudanças textuais pequenas.

`omie_chamar_api`

Fallback universal. Se a Omie publicar uma operação nova antes de criarmos uma ferramenta tipada, Claude ainda pode acessá-la por este caminho.

## Ferramentas de negócio já tipadas

### Clientes e Fornecedores

- `omie_clientes_listar`
- `omie_clientes_fornecedores_listar_completo`
- `omie_cliente_fornecedor_consultar`

A visão normalizada cobre identidade, endereço, contato, tags, características, dados bancários, PIX, inscrições, recomendações comerciais, bloqueio de faturamento, limite de crédito e auditoria.

Ver `OMIE_CLIENTES_FORNECEDORES_RELATORIO.md`.

### Contas a Pagar

- `omie_contas_pagar_listar`
- `omie_contas_pagar_financeiro`
- `omie_conta_pagar_situacao_financeira`

Para perguntas sobre **quanto já foi pago** e **quanto ainda falta pagar**, usar a visão financeira baseada em `/financas/mf/`.

Ver `OMIE_CONTAS_PAGAR_RELATORIO.md`.

### Contas a Receber

- `omie_contas_receber_listar`
- `omie_contas_receber_financeiro`
- `omie_conta_receber_situacao_financeira`

Para perguntas sobre **quanto já foi recebido** e **quanto ainda falta receber**, usar a visão financeira baseada em Movimentos Financeiros.

Ver `OMIE_CONTAS_RECEBER_RELATORIO.md`.

### Produtos, Compras e Vendas

Atalhos iniciais:

- `omie_produtos_listar`
- `omie_pedidos_compra_listar`
- `omie_pedidos_venda_listar`

Enquanto as visões enriquecidas desses domínios são ampliadas, a cobertura completa permanece disponível via `omie_chamar_api`.

## Exemplos de perguntas que o MCP deve responder

```text
Quanto já pagamos ao fornecedor X neste ano?
Quanto ainda falta pagar por projeto?
Liste títulos a pagar com pagamento parcial.
Quanto temos a receber até o fim do mês?
Quais clientes têm títulos vencidos e saldo em aberto?
Qual o limite de crédito deste cliente?
Quais clientes estão com faturamento bloqueado?
Mostre os dados bancários e PIX deste fornecedor.
Qual foi o último preço de compra deste produto?
Quais pedidos de venda ainda não foram faturados?
Obtenha o XML/PDF da nota relacionada a este pedido.
```

## Visões 360 planejadas

O MCP deve evoluir para retornar objetos de negócio completos, por exemplo:

```text
CLIENTE
  ├── cadastro
  ├── tags e características
  ├── limite e disponibilidade de crédito
  ├── pedidos de venda
  ├── contas a receber
  ├── valor recebido
  ├── saldo em aberto
  ├── NF-e / NFS-e
  └── documentos

FORNECEDOR
  ├── cadastro
  ├── dados bancários
  ├── pedidos de compra
  ├── notas de entrada
  ├── contas a pagar
  ├── valor pago
  ├── saldo em aberto
  └── documentos
```

## Segurança

Credenciais nunca devem ser gravadas no Git.

Use `.env` local baseado em `.env.example`:

```env
OMIE_APP_KEY=
OMIE_APP_SECRET=
OMIE_ALLOW_WRITES=false
```

Operações de escrita são bloqueadas por padrão. Uma mutação exige simultaneamente:

```env
OMIE_ALLOW_WRITES=true
```

E confirmação explícita na chamada:

```json
{"confirm_write": true}
```

O cliente também restringe chamadas ao domínio oficial da API Omie.

## Instalação

Requer Python 3.11+.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -U pip
pip install -e .
Copy-Item .env.example .env
```

Preencha `.env` localmente.

Teste o servidor:

```powershell
omie-mcp
```

## Claude Code

Registro recomendado no escopo do usuário:

```powershell
claude mcp add omie-verticalparts --scope user -- .\.venv\Scripts\omie-mcp.exe
```

Valide:

```powershell
claude mcp list
```

Dentro do Claude Code:

```text
/mcp
```

## Qual arquivo consultar

| Arquivo | Uso |
|---|---|
| `README.md` | visão geral e arquitetura |
| `CLAUDE.md` | instruções operacionais para Claude |
| `instructions.md` | mapa histórico/funcional do conhecimento Omie |
| `MCP_OMIE.md` | instalação e funcionamento do servidor |
| `OMIE_GAPS_ATUAIS.md` | mudanças/gaps encontrados no catálogo oficial |
| `OMIE_CONTAS_PAGAR_RELATORIO.md` | mapeamento do relatório real de Contas a Pagar |
| `OMIE_CONTAS_RECEBER_RELATORIO.md` | mapeamento do relatório real de Contas a Receber |
| `OMIE_CLIENTES_FORNECEDORES_RELATORIO.md` | mapeamento do cadastro real de clientes/fornecedores |
| Issues #1–#9 | mapeamento histórico por módulo e regras de negócio |

## Estrutura do código

```text
src/omie_mcp/
├── server.py       # ferramentas MCP
├── client.py       # cliente universal e segurança
├── catalog.py      # catálogo vivo
├── watcher.py      # radar/diff da documentação
├── cadastros.py    # clientes e fornecedores
├── financeiro.py   # Contas a Pagar / movimentos
├── receber.py      # Contas a Receber / movimentos
└── config.py       # configuração por ambiente
```

## Estratégia de cobertura

A cobertura do MCP é composta por três níveis:

1. **Cobertura universal**: qualquer endpoint/call oficial pode ser acionado por `omie_chamar_api`.
2. **Cobertura viva**: catálogo e watcher detectam o que a Omie adicionou ou mudou.
3. **Cobertura semântica**: ferramentas tipadas e visões enriquecidas traduzem a API para perguntas reais do negócio.

Uma ferramenta nova não deve substituir o fallback universal; deve acrescentar entendimento, validação e ergonomia.

## Qualidade

O projeto possui workflow de CI para:

```text
python -m compileall -q src
pytest -q
```

Os testes devem cobrir não apenas normalizadores e cliente HTTP, mas também a importação integral de `omie_mcp.server`, evitando nomes quebrados entre módulos e servidor.

## Próximos domínios prioritários

1. Produtos + Estoque completo
2. Pedidos de Venda + faturamento + NF-e
3. Pedidos de Compra + notas de entrada + custo real
4. Cliente 360 / Fornecedor 360
5. CRM completo
6. Serviços / NFS-e
7. Documentos fiscais
8. Reforma tributária IBS/CBS

## Regra final

Quando houver conflito entre conhecimento antigo versionado e a documentação atual do Omie, a documentação oficial atual deve ser verificada. O conhecimento histórico continua útil para regras de negócio e relacionamentos, mas não deve congelar a integração em uma versão antiga da API.
