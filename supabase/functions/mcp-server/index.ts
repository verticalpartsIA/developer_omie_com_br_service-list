import "jsr:@supabase/functions-js/edge-runtime.d.ts";

// ─── Servidor MCP remoto: ponte Claude ↔ Omie ERP (API ao vivo) ────────────
// Diferente dos outros conectores MCP da VerticalParts, este NÃO consulta um
// espelho no Supabase — toda leitura e escrita chama a API real do Omie
// (https://app.omie.com.br/api/v1/<endpoint>/), em tempo real, usando o
// App Key / App Secret guardado na tabela `omie_credentials`.
//
// Autenticação do conector: chave compartilhada, aceita via header
// Authorization: Bearer <token> OU via query string ?key=<token> — mesmo
// padrão usado nos demais conectores MCP da VerticalParts, necessário porque
// o domínio compartilhado *.supabase.co aplica CSP sandbox em HTML servido
// por Edge Functions, o que impede qualquer tela de login OAuth de funcionar.
//
// Ferramentas genéricas (não uma por endpoint — a API do Omie tem mais de
// 300 operações): `omie_consultar` para leitura, `omie_executar` para
// escrita. Toda chamada de escrita é registrada em `omie_write_audit_log`
// (payload completo + resultado), porque aqui é documento fiscal e
// movimentação financeira reais.

const SUPABASE_URL = Deno.env.get("SUPABASE_URL")!;
const SERVICE_ROLE_KEY = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;
const OMIE_BASE_URL = "https://app.omie.com.br/api/v1";

const PROTOCOL_VERSION = "2025-06-18";
const SERVER_INFO = { name: "omie-erp-mcp", version: "1.0.0" };

const CORS_HEADERS = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "POST, OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type, Authorization, Mcp-Session-Id, Mcp-Protocol-Version",
};

function jsonResponse(body: unknown, status = 200) {
  const headers = new Headers();
  headers.set("Content-Type", "application/json; charset=utf-8");
  headers.set("Cache-Control", "no-store");
  for (const [key, value] of Object.entries(CORS_HEADERS)) headers.set(key, value);
  return new Response(new TextEncoder().encode(JSON.stringify(body)), { status, headers });
}

// ─── Acesso a dados (PostgREST via service_role) ───────────────────────────

async function supabaseRest<T>(
  path: string,
  options?: { method?: "GET" | "POST" | "PATCH" | "DELETE" | "HEAD"; body?: unknown; headers?: Record<string, string> },
): Promise<{ data: T; count: number }> {
  const method = options?.method || "GET";
  const response = await fetch(`${SUPABASE_URL}/rest/v1/${path}`, {
    method,
    headers: {
      apikey: SERVICE_ROLE_KEY,
      Authorization: `Bearer ${SERVICE_ROLE_KEY}`,
      "Content-Type": "application/json",
      Accept: "application/json",
      ...options?.headers,
    },
    body: options?.body === undefined ? undefined : JSON.stringify(options.body),
  });

  if (!response.ok) {
    const text = await response.text();
    let message = text || `Supabase respondeu com status ${response.status}.`;
    try {
      const parsed = JSON.parse(text) as { message?: string; error?: string };
      message = parsed.message || parsed.error || message;
    } catch {
      // texto simples, mantém message
    }
    throw new Error(message);
  }

  const contentRange = response.headers.get("content-range");
  const count = contentRange ? Number(contentRange.split("/")[1]) || 0 : 0;

  if (method === "HEAD" || response.status === 204) {
    return { data: null as T, count };
  }

  const text = await response.text();
  if (!text) return { data: null as T, count };
  return { data: JSON.parse(text) as T, count };
}

// ─── Autenticação por chave compartilhada (hash em mcp_api_keys) ──────────

async function sha256Hex(input: string) {
  const digest = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(input));
  return Array.from(new Uint8Array(digest))
    .map((b) => b.toString(16).padStart(2, "0"))
    .join("");
}

async function isAuthorized(req: Request, url: URL): Promise<boolean> {
  const header = req.headers.get("authorization") || "";
  const match = header.match(/^Bearer\s+(.+)$/i);
  const bearerToken = match ? match[1].trim() : "";
  const keyParam = (url.searchParams.get("key") || "").trim();

  for (const token of [bearerToken, keyParam]) {
    if (!token) continue;
    const tokenHash = await sha256Hex(token);
    const { data } = await supabaseRest<Array<{ id: string }>>(
      `mcp_api_keys?select=id&token_hash=eq.${tokenHash}&active=eq.true&limit=1`,
    );
    if (Array.isArray(data) && data.length > 0) return true;
  }
  return false;
}

// ─── Credenciais Omie ───────────────────────────────────────────────────────

let cachedOmieCreds: { appKey: string; appSecret: string } | null = null;

async function getOmieCredentials(): Promise<{ appKey: string; appSecret: string }> {
  if (cachedOmieCreds) return cachedOmieCreds;
  const { data } = await supabaseRest<Array<{ app_key: string; app_secret: string }>>(
    "omie_credentials?select=app_key,app_secret&active=eq.true&limit=1",
  );
  const row = data?.[0];
  if (!row) throw new Error("Nenhuma credencial ativa em omie_credentials.");
  cachedOmieCreds = { appKey: row.app_key, appSecret: row.app_secret };
  return cachedOmieCreds;
}

// Prefixos de chamada que representam ações de escrita real no Omie (criam,
// alteram ou excluem documentos/dados). Qualquer chamada que comece com um
// desses verbos é tratada como escrita e registrada em auditoria.
const WRITE_VERB_PREFIXES = [
  "Incluir", "Alterar", "Excluir", "Cancelar", "Duplicar", "Faturar", "Lancar",
  "Reverter", "Suspender", "Ativar", "Reativar", "Conciliar", "Desconciliar",
  "Upsert", "Associar", "Gerar", "Prorrogar", "Trocar", "Concluir", "Conferir",
  "Importar", "Devolver", "Fechar", "Validar", "Totalizar", "Reenviar",
];

function isWriteCall(chamada: string): boolean {
  return WRITE_VERB_PREFIXES.some((prefix) => chamada.startsWith(prefix));
}

// Faz a chamada real à API do Omie: POST https://app.omie.com.br/api/v1/<endpoint>/
// Body: { call, app_key, app_secret, param: [parametros] }
async function omieCall(endpoint: string, chamada: string, parametros: Record<string, unknown>) {
  const { appKey, appSecret } = await getOmieCredentials();
  const cleanEndpoint = endpoint.replace(/^\/+|\/+$/g, "");
  const response = await fetch(`${OMIE_BASE_URL}/${cleanEndpoint}/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      call: chamada,
      app_key: appKey,
      app_secret: appSecret,
      param: [parametros ?? {}],
    }),
  });
  const text = await response.text();
  let parsed: unknown;
  try {
    parsed = JSON.parse(text);
  } catch {
    parsed = { raw: text };
  }
  if (!response.ok) {
    const faultstring = (parsed as Record<string, unknown>)?.faultstring;
    throw new Error(typeof faultstring === "string" ? faultstring : `Omie respondeu com status ${response.status}.`);
  }
  return parsed;
}

async function logWriteAttempt(endpoint: string, chamada: string, parametros: unknown, sucesso: boolean, resultado: unknown) {
  try {
    await supabaseRest("omie_write_audit_log", {
      method: "POST",
      body: [{ endpoint, chamada, parametros, sucesso, resultado }],
    });
  } catch {
    // não deixa falha de auditoria quebrar a resposta ao usuário
  }
}

// ─── Ferramentas MCP ────────────────────────────────────────────────────────

interface ToolDef {
  name: string;
  description: string;
  inputSchema: Record<string, unknown>;
  handler: (args: Record<string, unknown>) => Promise<unknown>;
}

const ENDPOINT_PARAM_DESC =
  "Caminho do módulo/recurso na API do Omie (ex: 'geral/clientes', 'produtos/pedido', 'financas/contapagar'). Ver https://developer.omie.com.br/service-list/ para o endpoint correto de cada chamada.";
const CHAMADA_PARAM_DESC =
  "Nome exato da chamada Omie (ex: 'ListarClientes', 'IncluirPedido', 'LancarPagamento'), conforme a documentação oficial.";
const PARAMETROS_PARAM_DESC =
  "Objeto JSON com os parâmetros exigidos por essa chamada específica, no formato exato da documentação oficial do Omie (um único objeto — a Edge Function já envolve em param: [...]).";

const TOOLS: ToolDef[] = [
  {
    name: "omie_consultar",
    description:
      "Executa uma chamada de CONSULTA (leitura) na API ao vivo do Omie ERP — Listar*, Consultar*, Obter*, Pesquisar*, Status*, etc. Não deve ser usada para chamadas que criam/alteram/excluem dados (use omie_executar).",
    inputSchema: {
      type: "object",
      properties: {
        endpoint: { type: "string", description: ENDPOINT_PARAM_DESC },
        chamada: { type: "string", description: CHAMADA_PARAM_DESC },
        parametros: { type: "object", description: PARAMETROS_PARAM_DESC },
      },
      required: ["endpoint", "chamada"],
    },
    handler: async (args) => {
      const chamada = String(args.chamada);
      if (isWriteCall(chamada)) {
        throw new Error(`'${chamada}' parece ser uma chamada de escrita. Use a ferramenta omie_executar.`);
      }
      return await omieCall(String(args.endpoint), chamada, (args.parametros as Record<string, unknown>) ?? {});
    },
  },
  {
    name: "omie_executar",
    description:
      "Executa uma chamada de ESCRITA real na API ao vivo do Omie ERP — Incluir*, Alterar*, Excluir*, Cancelar*, Faturar*, Lancar*, Trocar*, etc. Cria/altera documentos e movimentações financeiras reais. Toda chamada é registrada em log de auditoria (endpoint, chamada, parâmetros e resultado).",
    inputSchema: {
      type: "object",
      properties: {
        endpoint: { type: "string", description: ENDPOINT_PARAM_DESC },
        chamada: { type: "string", description: CHAMADA_PARAM_DESC },
        parametros: { type: "object", description: PARAMETROS_PARAM_DESC },
      },
      required: ["endpoint", "chamada", "parametros"],
    },
    handler: async (args) => {
      const endpoint = String(args.endpoint);
      const chamada = String(args.chamada);
      const parametros = (args.parametros as Record<string, unknown>) ?? {};
      try {
        const resultado = await omieCall(endpoint, chamada, parametros);
        await logWriteAttempt(endpoint, chamada, parametros, true, resultado);
        return resultado;
      } catch (err) {
        const message = err instanceof Error ? err.message : String(err);
        await logWriteAttempt(endpoint, chamada, parametros, false, { erro: message });
        throw err;
      }
    },
  },
  {
    name: "omie_listar_auditoria_escrita",
    description: "Lista o histórico de chamadas de escrita já executadas no Omie via este conector MCP (para revisão/auditoria).",
    inputSchema: {
      type: "object",
      properties: {
        chamada: { type: "string" },
        sucesso: { type: "boolean" },
        limit: { type: "number", description: "Padrão 50, máx 200." },
      },
    },
    handler: async (args) => {
      const limit = Math.min(Number(args.limit) || 50, 200);
      const params = new URLSearchParams({ select: "*", order: "criado_em.desc", limit: String(limit) });
      if (args.chamada) params.set("chamada", `eq.${args.chamada}`);
      if (typeof args.sucesso === "boolean") params.set("sucesso", `eq.${args.sucesso}`);
      const { data } = await supabaseRest(`omie_write_audit_log?${params.toString()}`);
      return { registros: data };
    },
  },
];

const TOOLS_BY_NAME = new Map(TOOLS.map((t) => [t.name, t]));

// ─── JSON-RPC / MCP plumbing (Streamable HTTP, sem estado de sessão) ──────

function rpcResult(id: unknown, result: unknown) {
  return { jsonrpc: "2.0", id, result };
}

function rpcError(id: unknown, code: number, message: string) {
  return { jsonrpc: "2.0", id, error: { code, message } };
}

async function handleMessage(msg: Record<string, unknown>) {
  const { method, id, params } = msg as { method?: string; id?: unknown; params?: Record<string, unknown> };

  if (method === "initialize") {
    return rpcResult(id, {
      protocolVersion: PROTOCOL_VERSION,
      capabilities: { tools: {} },
      serverInfo: SERVER_INFO,
    });
  }

  if (method === "notifications/initialized" || method === "notifications/cancelled") {
    return null;
  }

  if (method === "ping") {
    return rpcResult(id, {});
  }

  if (method === "tools/list") {
    return rpcResult(id, {
      tools: TOOLS.map((t) => ({ name: t.name, description: t.description, inputSchema: t.inputSchema })),
    });
  }

  if (method === "tools/call") {
    const name = String(params?.name ?? "");
    const tool = TOOLS_BY_NAME.get(name);
    if (!tool) {
      return rpcResult(id, { content: [{ type: "text", text: `Ferramenta desconhecida: ${name}` }], isError: true });
    }
    try {
      const result = await tool.handler((params?.arguments as Record<string, unknown>) ?? {});
      return rpcResult(id, { content: [{ type: "text", text: JSON.stringify(result, null, 2) }] });
    } catch (err) {
      const message = err instanceof Error ? err.message : String(err);
      return rpcResult(id, { content: [{ type: "text", text: `Erro: ${message}` }], isError: true });
    }
  }

  if (id === undefined) return null; // notificação desconhecida: ignora
  return rpcError(id, -32601, `Método não suportado: ${method}`);
}

Deno.serve(async (req: Request) => {
  const url = new URL(req.url);

  if (req.method === "OPTIONS") {
    return new Response(null, { status: 204, headers: CORS_HEADERS });
  }

  if (req.method !== "POST") {
    return jsonResponse({ error: "not_found" }, 404);
  }

  try {
    if (!(await isAuthorized(req, url))) {
      return jsonResponse({ error: "unauthorized" }, 401);
    }

    let body: unknown;
    try {
      body = await req.json();
    } catch {
      return jsonResponse(rpcError(null, -32700, "Parse error"), 400);
    }

    if (Array.isArray(body)) {
      const results = (await Promise.all(body.map((m) => handleMessage(m as Record<string, unknown>)))).filter(
        (r) => r !== null,
      );
      if (results.length === 0) return new Response(null, { status: 202, headers: CORS_HEADERS });
      return jsonResponse(results);
    }

    const result = await handleMessage(body as Record<string, unknown>);
    if (result === null) return new Response(null, { status: 202, headers: CORS_HEADERS });
    return jsonResponse(result);
  } catch (err) {
    return jsonResponse(rpcError(null, -32603, err instanceof Error ? err.message : String(err)), 500);
  }
});
