# Copiloto Flutuante Consciente da Tela (DOM-Aware, não Visão Computacional) — Guia para IA

> Documenta o **"Copiloto VP"** — um widget de IA em bolinha flutuante, presente em todas as telas do sistema `vpprd`, que lê o formulário/documento renderizado na página atual e responde, preenche campos ou revisa erros. Extraído por análise (somente leitura) do repositório [`verticalpartsIA/010_vpprd`](https://github.com/verticalpartsIA/010_vpprd).

## ⚠️ Correção de premissa importante
O pedido de análise original presumia um "Agente de Visão Computacional (Screen-Aware)" com OCR ou API de multimodalidade (captura de imagem de tela). **Isso não existe no código analisado.** O que o componente realmente faz é:
- ler o **DOM** da página (`document.querySelector`, `innerText`, atributos dos `<input>/<select>/<textarea>`) — texto estruturado, não pixels;
- enviar esse texto (campos + rótulos + conteúdo do documento visível) como contexto para o Claude via uma Edge Function;
- **não há screenshot, não há OCR, não há chamada de API de visão/multimodal.**

Ou seja: é um agente **"consciente do conteúdo da tela via leitura de DOM/texto"**, não um agente de visão computacional. Documentando com precisão para não propagar uma premissa incorreta para outras IAs que consumirem este repositório.

---

## Visão geral da arquitetura

```
Usuário logado no VP Gestão (qualquer tela)
        │
        ▼
Bolinha flutuante "Copiloto VP" (montada uma vez em app.jsx, aparece em todas as rotas)
   3 ações possíveis:
     - chat            → pergunta livre sobre a tela/sistema
     - "✨ Preencher"   → pede pra IA preencher os campos da tela atual
     - "🔍 Revisar erros" → pede pra IA analisar o documento renderizado
        │
        ▼
No clique/envio, o componente varre o DOM:
   - vpcScanPage(): coleta todos os <input>/<select>/<textarea> visíveis e habilitados
     dentro de <main class="main">, com label resolvido (via <label for>, aria-label,
     label ancestral, ou placeholder), tipo, valor atual e se é obrigatório
   - vpcDocText(): pega o innerText do <main>, limitado a 12.000 caracteres
        │
        ▼
POST para Edge Function (Supabase, mas só como host da function — sem tabela)
   https://{projeto}.supabase.co/functions/v1/vp-copiloto
   body: { mode, message, history (últimas 12 msgs), page: { route, title, fields }, documentText? }
        │
        ▼
Edge Function (Deno) monta o prompt e chama a API Anthropic diretamente
   (system prompt fixo definindo o papel + as regras de cada modo)
   Responde SEMPRE em JSON estrito: { reply, fills?, questions?, issues? }
        │
        ▼
Componente aplica o resultado:
   - fills: preenche os campos do DOM via "native setter" (compatível com React
     controlado — despacha eventos input/change para o framework perceber a mudança)
   - questions: exibe perguntas de volta ao usuário quando falta dado que a IA
     não pode inventar (ex.: CNPJ, valor de contrato)
   - issues: lista de achados (severidade/onde/problema/sugestão) no modo "revisar"
```

## Componentes técnicos

### 1. Leitura de campos (`vpcScanPage`)
- Escopo: só dentro de `<main class="main">` (ou `document.body` como fallback) — não lê o menu/header.
- Filtra campos ocultos, desabilitados, somente-leitura e tipos não preenchíveis (`hidden`, `file`, `submit`, `button`, `checkbox`, `radio`, `range`).
- Resolve o rótulo (`label`) do campo em cascata: `<label for="id">` → `aria-label` → `<label>` de um ancestral (até 4 níveis acima) → `placeholder`/`name`.
- Cada campo carrega um índice estável (`idx`) — é esse índice, não o nome, que a IA usa para referenciar qual campo preencher, evitando ambiguidade.

### 2. Preenchimento compatível com React (`vpcSetValue`)
Componentes React controlados ignoram `el.value = x` direto — o componente usa o *native property setter* do protótipo (`HTMLInputElement.prototype`, etc.) e depois despacha `input`/`change` manualmente, técnica padrão para "enganar" o React e fazer o estado interno perceber a mudança feita via DOM puro.

### 3. Contrato de resposta da IA (rígido, JSON-only)
A Edge Function exige que o modelo devolva **apenas** um JSON, sem texto fora dele, com chaves `reply` (sempre), `fills`, `questions`, `issues` (conforme o modo). Regra explícita no prompt: **nunca inventar** CNPJ, valores, nomes ou datas — perguntar em vez de adivinhar.

### 4. Três modos de operação
| Modo | Gatilho | Comportamento |
|---|---|---|
| `chat` | usuário digita algo | responde dúvida sobre a tela/sistema; não navega sozinho |
| `fill` | botão "✨ Preencher página" | preenche campos com dados já fornecidos na conversa; pergunta o que falta |
| `analyze` | botão "🔍 Revisar erros" | analisa `documentText` + valores dos campos, lista até ~10 achados priorizados por severidade |

### 5. Estado e persistência
- Histórico de conversa vive **só em memória do componente React** (`useState`), truncado às últimas 12 mensagens ao montar o payload — **não é salvo em nenhuma tabela**. Recarregar a página perde o histórico.
- Único estado persistido no cliente é se o painel está aberto/fechado (`localStorage`, chave `vpc_open_v1`) — preferência de UI, não dado de negócio.
- A Edge Function é **stateless**: não grava log de conversas, não lê nem escreve em nenhuma tabela do Supabase — o Supabase aqui é usado só como plataforma de hospedagem da function (Edge Functions), não como banco de dados para este componente.

## Não precisa de Banco de Dados "Supabase"
Este componente **não requer nenhuma tabela, migration ou schema no Supabase**. Toda a "memória" é efêmera (estado React) ou de UI (`localStorage`). O único uso do Supabase aqui é como runtime de hospedagem da Edge Function (`supabase/functions/vp-copiloto/index.ts`), que por sua vez só depende da secret `ANTHROPIC_API_KEY` configurada no projeto.

> Se no futuro se quiser adicionar auditoria (quem pediu o quê, quantos campos foram preenchidos por IA, taxa de aceitação das sugestões), isso exigiria uma tabela nova — não existe hoje.

## Checklist para replicar em outro projeto
1. Montar o widget uma única vez no componente raiz da aplicação (ex.: `app.jsx`), fora do roteamento, para persistir entre navegações.
2. Implementar a varredura de DOM restrita a um contêiner previsível (ex.: `<main>`), nunca a página inteira (evita capturar menu/header como "campos").
3. Resolver rótulos com fallback em cascata (for/aria-label/label ancestral/placeholder) — não depender de apenas uma convenção.
4. Usar "native setter + dispatchEvent" para preencher inputs de forma compatível com frameworks reativos (React/Vue).
5. Implementar a Edge Function com contrato de saída **rígido em JSON** e regra explícita de "nunca inventar dado sensível — perguntar em vez disso".
6. Manter o histórico de conversa client-side (sem persistência) a menos que haja necessidade real de auditoria — nesse caso, criar uma tabela de log só então.
7. Separar claramente os "modos" de operação (chat/preencher/revisar) tanto no componente quanto no prompt do sistema, cada um com regras próprias.

## Referência
Repositório de origem desta documentação (análise realizada em 2026-07-09): https://github.com/verticalpartsIA/010_vpprd — `src/vp-copiloto.jsx` + `supabase/functions/vp-copiloto/index.ts`.
