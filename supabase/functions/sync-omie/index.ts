/**
 * sync-omie — Edge Function para sincronização incremental Omie → Supabase
 *
 * POST /functions/v1/sync-omie
 * Body: { "modulo": 1 }   → sincroniza só o módulo 1
 *       { "modulo": 0 }   → sincroniza todos os módulos (use com cuidado)
 *       {}                → igual modulo=0
 *
 * Estratégia incremental:
 *   1. Pede página 1 à Omie para obter total_de_registros
 *   2. Compara com contagem no Supabase
 *   3. Se Supabase ≥ Omie → skip (sem novas páginas)
 *   4. Se Omie > Supabase  → busca páginas novas e faz upsert
 *   5. Tabelas com HTTP 500 persistente → marcadas como "api_unavailable"
 */

import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

// ─── Credenciais ────────────────────────────────────────────────────────────
const OMIE_APP_KEY    = Deno.env.get("OMIE_APP_KEY")!;
const OMIE_APP_SECRET = Deno.env.get("OMIE_APP_SECRET")!;
const SUPABASE_URL    = Deno.env.get("SUPABASE_URL")!;
const SB_SERVICE_KEY  = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;

// ─── Constantes ─────────────────────────────────────────────────────────────
const PAGE_SIZE      = 500;
const SLEEP_MS       = 350;   // ~170 req/min  (limite: 240/min)
const MAX_RETRIES    = 3;
const TIMEOUT_BUDGET = 110_000; // 110s de budget (Edge Function timeout = 150s)

// ─── Tabelas LISTAR_SYNC ─────────────────────────────────────────────────────
// [table_name, endpoint, call_name, modulo]
const ALL_TABLES: [string, string, string, number][] = [
  // Módulo 1 – Geral
  ["1.1.7. ListarClientes",          "geral/clientes/",          "ListarClientes",          1],
  ["1.1.8. ListarClientesResumido",  "geral/clientes/",          "ListarClientesResumido",  1],
  ["1.3.4. ListarTags",              "geral/clientetag/",        "ListarTags",              1],
  ["1.4.5. ListarProjetos",          "geral/projetos/",          "ListarProjetos",          1],
  ["1.5.2. ListarEmpresas",          "geral/empresas/",          "ListarEmpresas",          1],
  ["1.6.5. ListarDepartamentos",     "geral/departamentos/",     "ListarDepartamentos",     1],
  ["1.6.6. ListarDepatartamentos",   "geral/departamentos/",     "ListarDepatartamentos",   1],
  ["1.7.6. ListarCategorias",        "geral/categorias/",        "ListarCategorias",        1],
  ["1.8.2. ListarParcelas",          "geral/parcelas/",          "ListarParcelas",          1],
  ["1.9.1. ListarTipoAtiv",          "geral/tpativ/",            "ListarTipoAtiv",          1],
  ["1.10.1. ListarCNAE",             "produtos/cnae/",           "ListarCNAE",              1],
  ["1.11.1. PesquisarCidades",       "geral/cidades/",           "PesquisarCidades",        1],
  ["1.12.1. ListarPaises",           "geral/paises/",            "ListarPaises",            1],
  ["1.13.1. ListarTiposAnexos",      "geral/tiposanexo/",        "ListarTiposAnexos",       1],
  ["1.14.4. ListarAnexo",            "geral/anexo/",             "ListarAnexo",             1],
  ["1.15.5. ListarTipoEntrega",      "geral/tiposentrega/",      "ListarTipoEntrega",       1],
  ["1.16.1. ListarTipoAssinante",    "geral/tipoassinante/",     "ListarTipoAssinante",     1],
  ["1.17.5. ListarTarefas",          "geral/tarefas/",           "ListarTarefas",           1],
  // Módulo 2 – CRM
  ["2.1.5. ListarContas",            "crm/contas/",              "ListarContas",            2],
  ["2.3.5. ListarContatos",          "crm/contatos/",            "ListarContatos",          2],
  ["2.4.5. ListarOportunidades",     "crm/oportunidades/",       "ListarOportunidades",     2],
  ["2.6.6. ListarEmailsTarefas",     "crm/tarefas/",             "ListarEmailsTarefas",     2],
  ["2.6.7. ListarTarefas",           "crm/tarefas/",             "ListarTarefas",           2],
  ["2.8.1. ListarSolucoes",          "crm/solucoes/",            "ListarSolucoes",          2],
  ["2.9.1. ListarFases",             "crm/fases/",               "ListarFases",             2],
  ["2.10.1. ListarUsuarios",         "crm/usuarios/",            "ListarUsuarios",          2],
  ["2.11.1. ListarStatus",           "crm/status/",              "ListarStatus",            2],
  ["2.12.1. ListarMotivos",          "crm/motivos/",             "ListarMotivos",           2],
  ["2.13.1. ListarTipos",            "crm/tipos/",               "ListarTipos",             2],
  ["2.14.1. ListarParceiros",        "crm/parceiros/",           "ListarParceiros",         2],
  ["2.15.1. ListarFinders",          "crm/finders/",             "ListarFinders",           2],
  ["2.16.1. ListarOrigens",          "crm/origens/",             "ListarOrigens",           2],
  ["2.17.1. ListarConcorrentes",     "crm/concorrentes/",        "ListarConcorrentes",      2],
  ["2.18.1. ListarVerticais",        "crm/verticais/",           "ListarVerticais",         2],
  ["2.19.1. ListarUsuarios",         "crm/usuarios/",            "ListarUsuarios",          2],
  ["2.20.1. ListarUsuarios",         "crm/usuarios/",            "ListarUsuarios",          2],
  ["2.21.1. ListarUsuarios",         "crm/usuarios/",            "ListarUsuarios",          2],
  ["2.22.5. ListarTiposTarefa",      "crm/tipostarefa/",         "ListarTiposTarefa",       2],
  // Módulo 3 – Financeiro
  ["3.1.5. ListarContasCorrentes",      "geral/contacorrente/",                 "ListarContasCorrentes",      3],
  ["3.1.6. ListarResumoContasCorrentes","geral/contacorrente/",                 "ListarResumoContasCorrentes",3],
  ["3.1.7. PesquisarContaCorrente",     "geral/contacorrente/",                 "PesquisarContaCorrente",     3],
  ["3.2.5. ListarLancCC",               "financas/contacorrentelancamentos/",   "ListarLancCC",               3],
  ["3.3.8. ListarContasPagar",          "financas/contapagar/",                 "ListarContasPagar",          3],
  ["3.4.14. ListarContasReceber",       "financas/contareceber/",               "ListarContasReceber",        3],
  ["3.6.4. ListarPix",                  "financas/pix/",                        "ListarPix",                  3],
  ["3.6.5. ListarStatusPix",            "financas/pix/",                        "ListarStatusPix",            3],
  ["3.7.1. ListarExtrato",              "financas/extrato/",                    "ListarExtrato",              3],
  ["3.8.1. ListarOrcamentos",           "financas/caixa/",                      "ListarOrcamentos",           3],
  ["3.9.2. PesquisarExcluidos",         "financas/pesquisartitulos/",           "PesquisarExcluidos",         3],
  ["3.9.3. PesquisarLancamentos",       "financas/pesquisartitulos/",           "PesquisarLancamentos",       3],
  ["3.10.1. ListarMovimentos",          "financas/mf/",                         "ListarMovimentos",           3],
  ["3.12.2. ListarBancos",              "geral/bancos/",                        "ListarBancos",               3],
  ["3.13.2. PesquisarTipoDocumento",    "geral/tiposdoc/",                      "PesquisarTipoDocumento",     3],
  ["3.14.1. ListarTiposCC",             "geral/tipocc/",                        "ListarTiposCC",              3],
  ["3.15.1. ListarCadastroDRE",         "geral/dre/",                           "ListarCadastroDRE",          3],
  ["3.16.2. ListarFinalTransf",         "geral/finaltransf/",                   "ListarFinalTransf",          3],
  ["3.17.1. ListarOrigem",              "geral/origemlancamento/",              "ListarOrigem",               3],
  ["3.18.1. ListarBandeiras",           "geral/bandeiracartao/",                "ListarBandeiras",            3],
  // Módulo 4 – Produtos & Estoque
  ["4.1.7. ListarProdutos",             "geral/produtos/",           "ListarProdutos",          4],
  ["4.1.8. ListarProdutosResumido",     "geral/produtos/",           "ListarProdutosResumido",  4],
  ["4.2.5. ListarCaractProduto",        "geral/prodcaract/",         "ListarCaractProduto",     4],
  ["4.3.5. ListarEstruturas",           "geral/malha/",              "ListarEstruturas",        4],
  ["4.5.3. ListarVariacoes",            "produtos/variacao/",        "ListarVariacoes",         4],
  ["4.6.2. ListarLotes",                "produtos/produtoslote/",    "ListarLotes",             4],
  ["4.7.5. PesquisarReq",               "produtos/requisicaocompra/","PesquisarReq",            4],
  ["4.8.5. PesquisarPedCompra",         "produtos/pedidocompra/",    "PesquisarPedCompra",      4],
  ["4.9.6. ListarOrdemProducao",        "produtos/op/",              "ListarOrdemProducao",     4],
  ["4.10.5. ListarNotaEnt",             "produtos/notaentrada/",     "ListarNotaEnt",           4],
  ["4.12.7. ListarRecebimentos",        "produtos/recebimentonfe/",  "ListarRecebimentos",      4],
  ["4.14.5. PesquisarFamilias",         "geral/familias/",           "PesquisarFamilias",       4],
  ["4.15.1. ListarUnidades",            "geral/unidade/",            "ListarUnidades",          4],
  ["4.16.1. ListarCompradores",         "estoque/comprador/",        "ListarCompradores",       4],
  ["4.17.1. ListarProdutoFornecedor",   "estoque/produtofornecedor/","ListarProdutoFornecedor",  4],
  ["4.18.1. ListarFormasPagCompras",    "produtos/formaspagcompras/","ListarFormasPagCompras",  4],
  ["4.19.2. ListarNCM",                 "produtos/ncm/",             "ListarNCM",               4],
  ["4.20.1. ListarCenarios",            "geral/cenarios/",           "ListarCenarios",          4],
  ["4.20.2. ListarImpostosCenario",     "geral/cenarios/",           "ListarImpostosCenario",   4],
  ["4.21.1. ListarCFOP",                "produtos/cfop/",            "ListarCFOP",              4],
  ["4.22.1. ListarCNAE",                "produtos/cnae/",            "ListarCNAE",              4],
  ["4.23.1. ListarCST",                 "produtos/icmscst/",         "ListarCST",               4],
  ["4.24.1. ListarCSOSN",               "produtos/icmscsosn/",       "ListarCSOSN",             4],
  ["4.25.1. ListarOrigMerc",            "produtos/icmsorigem/",      "ListarOrigMerc",          4],
  ["4.26.1. ListarCstPis",              "produtos/piscst/",          "ListarCstPis",            4],
  ["4.27.1. ListarCstCofins",           "produtos/cofinscst/",       "ListarCstCofins",         4],
  ["4.28.1. ListarCstIpi",              "produtos/ipicst/",          "ListarCstIpi",            4],
  ["4.29.1. ListarEnqIpi",              "produtos/ipienq/",          "ListarEnqIpi",            4],
  ["4.30.1. ListarTpCalc",              "produtos/tpcalc/",          "ListarTpCalc",            4],
  ["4.31.1. ListarCEST",                "produtos/cest/",            "ListarCEST",              4],
  ["4.32.4. ListarAjusteEstoque",       "estoque/ajuste/",           "ListarAjusteEstoque",     4],
  ["4.33.1. ListarMovimentoEstoque",    "estoque/consulta/",         "ListarMovimentoEstoque",  4],
  ["4.33.2. ListarPosEstoque",          "estoque/consulta/",         "ListarPosEstoque",        4],
  ["4.33.3. ListarSaldoPendente",       "estoque/consulta/",         "ListarSaldoPendente",     4],
  ["4.34.2. ListarMovimentos",          "estoque/movestoque/",       "ListarMovimentos",        4],
  ["4.35.3. ListarLocaisEstoque",       "estoque/local/",            "ListarLocaisEstoque",     4],
  // Módulo 5 – Vendas & NF-e
  ["5.2.7. ListarPedidos",           "produtos/pedido/",          "ListarPedidos",           5],
  ["5.4.1. ListarEtapasPedido",      "produtos/pedidoetapas/",    "ListarEtapasPedido",      5],
  ["5.5.9. ListarNFeTransp",         "produtos/cte/",             "ListarNFeTransp",         5],
  ["5.6.5. ListarRemessas",          "produtos/remessa/",         "ListarRemessas",          5],
  ["5.10.7. ListarProdutos",         "geral/produtos/",           "ListarProdutos",          5],
  ["5.10.8. ListarProdutosResumido", "geral/produtos/",           "ListarProdutosResumido",  5],
  ["5.11.5. ListarCaractProduto",    "geral/prodcaract/",         "ListarCaractProduto",     5],
  ["5.13.3. ListarVariacoes",        "produtos/variacao/",        "ListarVariacoes",         5],
  ["5.14.2. ListarLotes",            "produtos/produtoslote/",    "ListarLotes",             5],
  ["5.16.8. ListarCupons",           "produtos/cupomfiscal/",     "ListarCupons",            5],
  ["5.20.5. ListarVendedores",       "geral/vendedores/",         "ListarVendedores",        5],
  ["5.21.1. ListarFormasPagVendas",  "produtos/formaspagvendas/", "ListarFormasPagVendas",   5],
  ["5.22.8. ListarTabelaItens",      "produtos/tabelaprecos/",    "ListarTabelaItens",       5],
  ["5.22.9. ListarTabelasPreco",     "produtos/tabelaprecos/",    "ListarTabelasPreco",      5],
  ["5.23.5. ListarCaracteristicas",  "geral/caracteristicas/",    "ListarCaracteristicas",   5],
  ["5.24.2. ListarNCM",              "produtos/ncm/",             "ListarNCM",               5],
  ["5.25.1. ListarEtapasFaturamento","produtos/etapafat/",        "ListarEtapasFaturamento", 5],
  ["5.26.1. ListarCenarios",         "geral/cenarios/",           "ListarCenarios",          5],
  ["5.26.2. ListarImpostosCenario",  "geral/cenarios/",           "ListarImpostosCenario",   5],
  ["5.27.1. ListarMeiosPagamento",   "geral/meiospagamento/",     "ListarMeiosPagamento",    5],
  ["5.28.1. ListarOrigem",           "geral/origempedido/",       "ListarOrigem",            5],
  ["5.29.1. ListarMotivosDevol",     "geral/motivodevolucao/",    "ListarMotivosDevol",      5],
  ["5.30.2. ListarNF",               "produtos/nfconsultar/",     "ListarNF",                5],
  ["5.32.4. ListarNFe",              "produtos/nfe/",             "ListarNFe",               5],
  // Módulo 6 – Serviços & NFS-e
  ["6.1.6. ListarCadastroServico",      "servicos/servico/",              "ListarCadastroServico",      6],
  ["6.2.5. ListarOS",                   "servicos/os/",                   "ListarOS",                   6],
  ["6.4.2. ListarLoteNfse",             "servicos/oslote/",               "ListarLoteNfse",             6],
  ["6.4.3. ListarLotesOS",              "servicos/oslote/",               "ListarLotesOS",              6],
  ["6.5.5. ListarContratos",            "servicos/contrato/",             "ListarContratos",            6],
  ["6.7.2. ListarLotesContrato",        "servicos/contratolote/",         "ListarLotesContrato",        6],
  ["6.10.1. ListarNFSEs",               "servicos/nfse/",                 "ListarNFSEs",                6],
  ["6.11.5. ListarVendedores",          "geral/vendedores/",              "ListarVendedores",           6],
  ["6.12.1. ListarServMunic",           "servicos/listaservico/",         "ListarServMunic",            6],
  ["6.13.1. ListarTiposTrib",           "servicos/tipotrib/",             "ListarTiposTrib",            6],
  ["6.14.1. ListarLC116",               "servicos/lc116/",                "ListarLC116",                6],
  ["6.15.1. ListarNBS",                 "servicos/nbs/",                  "ListarNBS",                  6],
  ["6.16.1. ListarProdutosIBPT",        "servicos/ibpt/",                 "ListarProdutosIBPT",         6],
  ["6.16.2. ListarServicosIBPT",        "servicos/ibpt/",                 "ListarServicosIBPT",         6],
  ["6.17.1. ListarFormasPagVendas",     "produtos/formaspagvendas/",      "ListarFormasPagVendas",      6],
  ["6.18.1. ListarTipoFatContrato",     "servicos/contratotpfat/",        "ListarTipoFatContrato",      6],
  ["6.19.1. ListarEtapasFaturamento",   "produtos/etapafat/",             "ListarEtapasFaturamento",    6],
  ["6.20.1. ListarTipoUtilizacao",      "servicos/tipoutilizacao/",       "ListarTipoUtilizacao",       6],
  ["6.21.1. ListarClassificacaoServico","servicos/classificacaoservico/", "ListarClassificacaoServico", 6],
  // Módulo 7 – Painel do Contador
  ["7.1.1. ListarDocumentos",           "contador/xml/",                  "ListarDocumentos",           7],
];

// ─── Helpers ─────────────────────────────────────────────────────────────────
function sleep(ms: number) {
  return new Promise((r) => setTimeout(r, ms));
}

async function omiePost(
  endpoint: string,
  call: string,
  params: Record<string, unknown>,
  attempt = 0
): Promise<Record<string, unknown>> {
  const url = `https://app.omie.com.br/api/v1/${endpoint}`;
  const body = JSON.stringify({
    call,
    app_key: OMIE_APP_KEY,
    app_secret: OMIE_APP_SECRET,
    param: [params],
  });

  let res: Response;
  try {
    res = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body,
      signal: AbortSignal.timeout(15_000),
    });
  } catch (e) {
    if (attempt < MAX_RETRIES) {
      await sleep(2 ** attempt * 1000);
      return omiePost(endpoint, call, params, attempt + 1);
    }
    throw new Error(`network_error: ${e}`);
  }

  if (res.status === 429) {
    if (attempt < MAX_RETRIES) {
      await sleep(65_000);
      return omiePost(endpoint, call, params, attempt + 1);
    }
    throw new Error("rate_limit_exceeded");
  }

  if (res.status >= 500) {
    const text = await res.text();
    if (attempt < MAX_RETRIES) {
      await sleep(2 ** attempt * 1000);
      return omiePost(endpoint, call, params, attempt + 1);
    }
    throw new Error(`http_${res.status}: ${text.slice(0, 200)}`);
  }

  return res.json();
}

// ─── Handler principal ───────────────────────────────────────────────────────
Deno.serve(async (req: Request) => {
  const startTime = Date.now();

  // Autenticação via Bearer token (service role key ou CRON_SECRET)
  const authHeader = req.headers.get("Authorization") ?? "";
  const cronSecret = Deno.env.get("CRON_SECRET") ?? SB_SERVICE_KEY;
  if (!authHeader.includes(cronSecret) && !authHeader.includes(SB_SERVICE_KEY)) {
    return new Response(JSON.stringify({ error: "Unauthorized" }), {
      status: 401,
      headers: { "Content-Type": "application/json" },
    });
  }

  // Parâmetros
  let modulo = 0; // 0 = todos
  try {
    if (req.method === "POST") {
      const body = await req.json().catch(() => ({}));
      modulo = body.modulo ?? 0;
    } else {
      const url = new URL(req.url);
      modulo = parseInt(url.searchParams.get("modulo") ?? "0");
    }
  } catch {
    modulo = 0;
  }

  const tables = modulo > 0
    ? ALL_TABLES.filter(([, , , m]) => m === modulo)
    : ALL_TABLES;

  const supabase = createClient(SUPABASE_URL, SB_SERVICE_KEY);

  const results: Record<string, unknown>[] = [];
  let tablesSynced = 0;
  let tablesSkipped = 0;
  let totalInserted = 0;

  for (const [tableName, endpoint, callName] of tables) {
    // Verificar budget de tempo
    if (Date.now() - startTime > TIMEOUT_BUDGET) {
      results.push({ table: tableName, status: "timeout_budget" });
      continue;
    }

    // ── 1. Verificar contagem no Supabase ──────────────────────────────
    const { count: sbCount, error: countErr } = await supabase
      .from(tableName)
      .select("*", { count: "exact", head: true });

    if (countErr) {
      results.push({ table: tableName, status: "sb_error", error: countErr.message });
      continue;
    }

    // ── 2. Pedir página 1 à Omie para obter total de registros ─────────
    let omieTotal = 0;
    let firstPageData: unknown[] = [];
    try {
      const firstPage = await omiePost(endpoint, callName, {
        pagina: 1,
        registros_por_pagina: PAGE_SIZE,
      });
      omieTotal =
        (firstPage.total_de_registros as number) ??
        (firstPage.nTotRegistros as number) ??
        (firstPage.total as number) ??
        0;

      // Extrair registros da primeira página
      const dataKey = Object.keys(firstPage).find(
        (k) => Array.isArray(firstPage[k]) && k !== "param"
      );
      firstPageData = dataKey ? (firstPage[dataKey] as unknown[]) : [];

      await sleep(SLEEP_MS);
    } catch (e) {
      results.push({ table: tableName, status: "api_unavailable", error: String(e) });
      continue;
    }

    // ── 3. Skip se já está atualizado ─────────────────────────────────
    if ((sbCount ?? 0) >= omieTotal && omieTotal > 0) {
      tablesSkipped++;
      results.push({ table: tableName, status: "up_to_date", count: sbCount });
      continue;
    }

    // ── 4. Sincronizar (primeira página já em memória + páginas restantes)
    const totalPages = Math.ceil(omieTotal / PAGE_SIZE) || 1;
    let allRecords: unknown[] = [...firstPageData];

    for (let page = 2; page <= totalPages; page++) {
      if (Date.now() - startTime > TIMEOUT_BUDGET) break;
      try {
        const pageData = await omiePost(endpoint, callName, {
          pagina: page,
          registros_por_pagina: PAGE_SIZE,
        });
        const dataKey = Object.keys(pageData).find(
          (k) => Array.isArray(pageData[k]) && k !== "param"
        );
        if (dataKey) allRecords = allRecords.concat(pageData[dataKey] as unknown[]);
        await sleep(SLEEP_MS);
      } catch {
        break; // página falhou, insere o que já temos
      }
    }

    if (allRecords.length === 0) {
      results.push({ table: tableName, status: "sem_dados" });
      continue;
    }

    // ── 5. Upsert no Supabase ─────────────────────────────────────────
    const rows = allRecords.map((r) => ({ dados_raw: r }));
    const CHUNK = 500;
    let inserted = 0;

    for (let i = 0; i < rows.length; i += CHUNK) {
      const chunk = rows.slice(i, i + CHUNK);
      const { error: insErr } = await supabase
        .from(tableName)
        .insert(chunk);
      if (!insErr) inserted += chunk.length;
    }

    // ── 6. Atualizar _sync_status ─────────────────────────────────────
    await supabase.from("_sync_status").upsert(
      {
        table_name: tableName,
        last_sync_at: new Date().toISOString(),
        last_count: inserted,
        status: "ok",
      },
      { onConflict: "table_name" }
    );

    tablesSynced++;
    totalInserted += inserted;
    results.push({
      table: tableName,
      status: "synced",
      omie_total: omieTotal,
      inserted,
    });
  }

  const elapsed = ((Date.now() - startTime) / 1000).toFixed(1);

  return new Response(
    JSON.stringify({
      modulo: modulo || "all",
      tables_processed: tables.length,
      tables_synced: tablesSynced,
      tables_skipped: tablesSkipped,
      total_inserted: totalInserted,
      elapsed_s: elapsed,
      results,
    }),
    { headers: { "Content-Type": "application/json" } }
  );
});
