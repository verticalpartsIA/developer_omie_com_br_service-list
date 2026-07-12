# Conector MCP: Claude ↔ Omie ERP (API ao vivo)

Este servidor MCP remoto (Streamable HTTP), hospedado como Supabase Edge
Function no projeto `hrhwplqlbuwfextznkea`, permite que o Claude (claude.ai,
Claude Desktop ou Claude Code) consulte e opere a API real do Omie ERP
diretamente em conversa.

## Diferença importante em relação aos outros conectores MCP da VerticalParts

Este conector **não** consulta nenhum espelho/mirror do Omie no Supabase
(nem `hrhwplqlbuwfextznkea` nas ~300 tabelas espelhadas, nem `bd_Omie`
`kgecbycsyrtdhmdziuul`). Toda leitura e escrita chama a API ao vivo do Omie
(`https://app.omie.com.br/api/v1/<endpoint>/`) em tempo real, usando o App
Key / App Secret configurado em `omie_credentials`. Isso foi uma decisão
explícita: os dois espelhos existentes divergem entre si e da documentação
deste repositório, então em vez de escolher um schema desatualizado, o
conector fala direto com a fonte oficial.

## Endpoint

```
https://hrhwplqlbuwfextznkea.supabase.co/functions/v1/mcp-server
```

Código-fonte: `supabase/functions/mcp-server/index.ts`.

## Autenticação: chave na URL (sem OAuth)

Mesmo padrão dos demais conectores MCP da VerticalParts: o domínio
compartilhado `*.supabase.co` aplica CSP sandbox em HTML servido por Edge
Functions, o que impede qualquer tela de login OAuth de funcionar. A
autenticação do conector é uma chave compartilhada, aceita via query string
`?key=` (ou header `Authorization: Bearer`), validada contra o hash SHA-256
guardado em `public.mcp_api_keys` (RLS habilitado sem policies — só
`service_role` acessa).

## Ferramentas disponíveis

A API do Omie tem mais de 300 operações (ver
https://developer.omie.com.br/service-list/), então este conector expõe
ferramentas **genéricas** em vez de uma por endpoint:

- **`omie_consultar`** — chamadas de leitura (`Listar*`, `Consultar*`,
  `Obter*`, `Pesquisar*`, `Status*`...). Parâmetros: `endpoint` (módulo/
  recurso, ex: `geral/clientes`), `chamada` (nome exato da API Omie, ex:
  `ListarClientes`), `parametros` (objeto com os campos exigidos por essa
  chamada específica).
- **`omie_executar`** — chamadas de escrita real (`Incluir*`, `Alterar*`,
  `Excluir*`, `Cancelar*`, `Faturar*`, `Lancar*`, `Trocar*`...). Mesmos
  parâmetros, porém `parametros` é obrigatório. Cria/altera documentos
  fiscais e movimentações financeiras reais em produção.
- **`omie_listar_auditoria_escrita`** — consulta o histórico de chamadas de
  escrita já feitas via este conector (payload e resultado).

Não há lista fixa de "ações permitidas" — qualquer chamada válida da API do
Omie pode ser executada. A classificação leitura/escrita é automática, por
prefixo do nome da chamada (`WRITE_VERB_PREFIXES` em `index.ts`); se um novo
verbo do Omie não estiver nessa lista e for na verdade uma escrita, o
`omie_consultar` deixaria passar sem bloquear — o `omie_executar` sempre
registra em auditoria independente da classificação, então prefira executar
ali quando houver dúvida.

## Auditoria

Toda chamada feita via `omie_executar` — sucesso ou erro — é registrada em
`public.omie_write_audit_log` (endpoint, chamada, parâmetros completos,
resultado, timestamp). `omie_consultar` não é registrado (alto volume,
sem efeito colateral real).

## Como conectar no claude.ai

1. Configurações → Conectores → Adicionar conector → Adicionar conector personalizado.
2. **Nome:** `Omie ERP`
3. **URL do servidor MCP remoto** (a URL inteira, incluindo `?key=`):
   ```
   https://hrhwplqlbuwfextznkea.supabase.co/functions/v1/mcp-server?key=<token-de-acesso>
   ```
4. Deixe os campos de OAuth Client ID/Secret em branco e clique em Adicionar.

## Riscos e responsabilidade

Este conector permite ao portador do token **qualquer** ação que a API do
Omie permita à conta configurada — incluir/alterar/excluir clientes,
produtos, pedidos de compra e venda, lançar contas a pagar/receber, emitir e
cancelar documentos fiscais. Não há aprovação humana no meio do caminho.
Trate o token com o mesmo cuidado que uma credencial de administrador do
ERP. Use `omie_listar_auditoria_escrita` para revisar o que foi feito.

Para revogar o token ou trocar a credencial Omie:

```sql
update public.mcp_api_keys set active = false where label = 'claude-web-connector';
insert into public.mcp_api_keys (label, token_hash) values ('novo-label', '<sha256-hex-do-novo-token>');

update public.omie_credentials set active = false where label = 'verticalparts-principal';
insert into public.omie_credentials (label, app_key, app_secret) values ('nova-conta', '<app_key>', '<app_secret>');
```
