# VerticalParts Omie MCP

MCP vivo para Claude/Claude Code acessar o ERP Omie com cobertura ampla, fallback universal e radar de mudanças da documentação oficial.

## Objetivo

O servidor foi desenhado para não ficar preso a uma lista estática de ferramentas. Ele combina:

1. ferramentas tipadas para operações frequentes;
2. `omie_chamar_api`, fallback universal para qualquer endpoint/call oficial;
3. `omie_catalogo_servicos`, descoberta ao vivo dos serviços publicados pelo Omie;
4. `omie_inspecionar_servico`, inspeção de um serviço específico;
5. `omie_documentacao_diff`, radar de mudanças do portal oficial e das páginas/serviços individuais.

A intenção é detectar desde um serviço novo até alteração textual pequena na documentação. O radar guarda um snapshot local, compara hashes e produz prévias de diff.

## Segurança

Credenciais nunca devem ser gravadas no Git.

Copie `.env.example` para `.env` e preencha localmente:

```env
OMIE_APP_KEY=<sua-app-key>
OMIE_APP_SECRET=<seu-app-secret>
OMIE_ALLOW_WRITES=false
```

O `.gitignore` bloqueia `.env` e `.omie_mcp_state/`.

### Escrita no ERP

Por padrão o MCP trabalha em leitura. Uma operação não reconhecida como leitura só executa quando as duas condições forem verdadeiras:

```env
OMIE_ALLOW_WRITES=true
```

e a chamada informar:

```json
{"confirm_write": true}
```

Assim, habilitar escrita no ambiente não basta para uma mutação acidental.

## Instalação local

Requer Python 3.11+.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -U pip
pip install -e .
Copy-Item .env.example .env
```

Preencha o `.env` local e teste:

```powershell
omie-mcp
```

## Claude Code

Depois da instalação, registre o MCP no escopo do usuário:

```powershell
claude mcp add omie-verticalparts --scope user -- .\.venv\Scripts\omie-mcp.exe
```

Confirme com:

```powershell
claude mcp list
```

ou dentro do Claude Code:

```text
/mcp
```

## Ferramentas

### `omie_catalogo_servicos`

Busca o catálogo oficial atual. Não depende exclusivamente de uma enumeração codificada no projeto.

### `omie_inspecionar_servico`

Recebe um endpoint oficial e tenta identificar operações/calls documentadas.

### `omie_chamar_api`

Fallback universal. Exemplo conceitual:

```json
{
  "endpoint": "geral/clientes",
  "call": "ListarClientes",
  "param": {
    "pagina": 1,
    "registros_por_pagina": 50
  }
}
```

O endpoint também pode ser a URL oficial completa sob `https://app.omie.com.br/api/v1/`.

### `omie_documentacao_diff`

Na primeira execução cria a linha de base. Nas próximas compara:

- hash da lista oficial de serviços;
- serviços adicionados e removidos;
- metadados alterados;
- conteúdo das páginas/serviços descobertos;
- status HTTP;
- prévia do diff textual.

O estado fica apenas em `.omie_mcp_state/` e não é versionado.

### Atalhos tipados iniciais

- `omie_clientes_listar`
- `omie_produtos_listar`
- `omie_contas_pagar_listar`
- `omie_contas_receber_listar`
- `omie_pedidos_compra_listar`
- `omie_pedidos_venda_listar`

Novos atalhos podem ser adicionados sem reduzir a cobertura porque `omie_chamar_api` continua disponível.

## Estratégia de evolução

O repositório mantém duas fontes complementares:

- conhecimento curado: README, instructions e issues por módulo;
- conhecimento vivo: catálogo e snapshots obtidos da documentação oficial no momento da execução.

Quando `omie_documentacao_diff` apontar mudança, a manutenção ideal é:

1. verificar a diferença;
2. atualizar o mapa documental do módulo;
3. acrescentar uma ferramenta tipada se a operação for recorrente;
4. manter o fallback universal como cobertura imediata.

## Princípio

Nenhuma integração com Omie deve depender de o desenvolvedor ter previsto previamente todos os endpoints. O catálogo vivo encontra o que existe; o radar mostra o que mudou; o fallback universal acessa o que ainda não ganhou uma ferramenta dedicada.
