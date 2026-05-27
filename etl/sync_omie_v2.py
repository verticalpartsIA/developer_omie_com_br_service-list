#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys, io
# Garante UTF-8 no stdout/stderr mesmo no Windows (cp1252)
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
"""
sync_omie_v2.py — ETL automático Omie ERP → Supabase
Schema hierárquico: tabelas nomeadas como "M.S.P. NomeDoMetodo"

╔══════════════════════════════════════════════════════════════════╗
║  CATEGORIAS DE OPERAÇÃO                                         ║
║                                                                  ║
║  LISTAR_SYNC  Listar*, Pesquisar*                               ║
║               → sync paginado completo (principal ETL)          ║
║                                                                  ║
║  OBTER_TRY    Obter*, Consultar*, Get*                          ║
║               → tenta sem ID; registra se retornar dados        ║
║                                                                  ║
║  WRITE_OP     Incluir*, Alterar*, Upsert*, Faturar*, etc.       ║
║               → populada pela aplicação ao executar operações   ║
║               → NÃO é chamada automaticamente                   ║
║                                                                  ║
║  SKIP         Excluir*, Cancelar*                               ║
║               → NUNCA chamadas (destrutivas)                    ║
╚══════════════════════════════════════════════════════════════════╝

Uso:
  python sync_omie_v2.py                      # sync completo
  python sync_omie_v2.py --fresh              # limpa tabelas antes de inserir
  python sync_omie_v2.py --categoria LISTAR_SYNC
  python sync_omie_v2.py --tabela clientes
  python sync_omie_v2.py --dry-run            # mostra plano sem chamar API

Boas práticas seguidas (instructions.md):
  ✓ POST para endpoint com call/app_key/app_secret/param
  ✓ Paginação: pagina + registros_por_pagina (máx 500)
  ✓ Limites: backoff exponencial em rate limit (429)
  ✓ Retry até 3x em erros 5xx com espera progressiva
  ✓ Credenciais nunca em logs
  ✓ Filtros de data em métodos financeiros
  ✓ Cadastros auxiliares preferem cache entre tabelas do mesmo endpoint
"""

import os
import re
import sys
import time
import json
import logging
import argparse
import urllib.parse
from datetime import date, datetime
from pathlib import Path

import requests

# ──────────────────────────────────────────────────────────────────
#  LOGGING
# ──────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%H:%M:%S',
    handlers=[
        logging.StreamHandler(sys.stdout),
    ]
)
log = logging.getLogger('sync_omie')

# ──────────────────────────────────────────────────────────────────
#  CREDENCIAIS  (mover para .env em produção)
# ──────────────────────────────────────────────────────────────────
OMIE_APP_KEY    = os.environ.get('OMIE_APP_KEY',    '8463170967')
OMIE_APP_SECRET = os.environ.get('OMIE_APP_SECRET', '69e22b773842044fdb218178521cac59')
OMIE_BASE_URL   = 'https://app.omie.com.br/api/v1/'

SUPABASE_URL = os.environ.get('SUPABASE_URL', 'https://hrhwplqlbuwfextznkea.supabase.co')
SUPABASE_KEY = os.environ.get('SUPABASE_KEY', (
    'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9'
    '.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhyaHdwbHFsYnV3ZmV4dHpua2VhIiwicm9sZSI6'
    'InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3OTgyNjgxMCwiZXhwIjoyMDk1NDAyODEwfQ'
    '.sFu6yrV6a2nKrGr8LiYk_i-pug6TkTa6S_ICXgojH10'
))

# ──────────────────────────────────────────────────────────────────
#  CONFIGURAÇÃO
# ──────────────────────────────────────────────────────────────────
PAGE_SIZE        = 500      # máximo recomendado pela Omie
MAX_RETRIES      = 3
SLEEP_BETWEEN    = 0.35     # ~170 req/min (bem abaixo dos 240/min por método)
SLEEP_RATE_LIMIT = 65       # segundos de espera ao receber 429
DATE_START       = '01/01/2020'
DATE_TODAY       = date.today().strftime('%d/%m/%Y')

MD_FILE = Path(__file__).parent.parent / 'Lita_Tables_Omie' / 'Lista_Tables_Omie.md'

# ──────────────────────────────────────────────────────────────────
#  CATEGORIZAÇÃO DOS MÉTODOS
# ──────────────────────────────────────────────────────────────────

# Nunca chamados (destrutivos)
SKIP_PREFIXES = (
    'Excluir', 'Cancelar',
)

# Sync paginado completo
LISTAR_PREFIXES = (
    'Listar', 'Pesquisar',
)

# Tenta sem ID; popula se retornar dados
OBTER_PREFIXES = (
    'Obter', 'Consultar', 'Get',
)

# Operações de escrita: populadas pela aplicação, não pelo ETL
WRITE_PREFIXES = (
    'Incluir', 'Alterar', 'Upsert', 'Adicionar', 'Faturar',
    'Associar', 'Trocar', 'Devolver', 'Duplicar', 'Concluir',
    'Conferir', 'Validar', 'Reenviar', 'Inutilizar', 'Importar',
    'Averbacao', 'CartaCorrecao', 'Ativar', 'Suspender',
    'Reativar', 'Totalizar', 'Simular', 'Status', 'Fechar',
    'Baixar', 'Emitir', 'Gerar', 'Processar', 'Sincronizar',
)

# Métodos que precisam de filtro de data
DATE_FILTER_KEYWORDS = (
    'lancamento', 'emissao', 'extrato', 'movimento',
    'historico', 'vencimento', 'receber', 'pagar',
    'pedido', 'nfe', 'nota', 'fatura',
)


def classify_method(method: str) -> str:
    """Retorna a categoria de um método Omie."""
    for p in SKIP_PREFIXES:
        if method.startswith(p):
            return 'SKIP'
    for p in LISTAR_PREFIXES:
        if method.startswith(p):
            return 'LISTAR_SYNC'
    for p in OBTER_PREFIXES:
        if method.startswith(p):
            return 'OBTER_TRY'
    for p in WRITE_PREFIXES:
        if method.startswith(p):
            return 'WRITE_OP'
    # Qualquer coisa não identificada vai para WRITE_OP por segurança
    return 'WRITE_OP'


# ──────────────────────────────────────────────────────────────────
#  PARSER DO MD
# ──────────────────────────────────────────────────────────────────

# Ex: "1.1.7. ListarClientes: https://app.omie.com.br/api/v1/geral/clientes/#ListarClientes"
MD_PATTERN = re.compile(
    r'^(\d+\.\d+\.\d+\.\s+\S+):\s+https://app\.omie\.com\.br/api/v1/(.+?)$'
)


def parse_md() -> list[dict]:
    """
    Lê Lista_Tables_Omie.md e retorna lista de entradas:
    { table, method, endpoint, call, category }
    """
    if not MD_FILE.exists():
        log.error(f'MD não encontrado: {MD_FILE}')
        sys.exit(1)

    entries = []
    with open(MD_FILE, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            m = MD_PATTERN.match(line)
            if not m:
                continue

            table    = m.group(1)    # "1.1.7. ListarClientes"
            url_tail = m.group(2)    # "geral/clientes/#ListarClientes"

            # Endpoint = path antes do '#'
            endpoint = url_tail.split('#')[0].rstrip('/') + '/'

            # Method = parte após "M.S.P. " no nome da tabela
            method = re.sub(r'^\d+\.\d+\.\d+\.\s+', '', table)

            entries.append({
                'table':    table,
                'method':   method,
                'endpoint': endpoint,
                'call':     method,            # call name == method name na API Omie
                'category': classify_method(method),
            })

    counts = {}
    for e in entries:
        counts[e['category']] = counts.get(e['category'], 0) + 1

    log.info(
        f'MD parseado: {len(entries)} entradas — '
        + ' | '.join(f'{k}={v}' for k, v in sorted(counts.items()))
    )
    return entries


# ──────────────────────────────────────────────────────────────────
#  OMIE API
# ──────────────────────────────────────────────────────────────────

def omie_post(endpoint: str, call: str, params: dict, attempt: int = 0) -> dict:
    """
    POST para a API Omie. Responde com dict (pode conter 'faultstring').
    Aplica retry com backoff exponencial em 5xx e rate limit.
    Nunca loga credenciais.
    """
    url     = OMIE_BASE_URL + endpoint
    payload = {
        'call':       call,
        'app_key':    OMIE_APP_KEY,
        'app_secret': OMIE_APP_SECRET,
        'param':      [params],
    }

    try:
        r = requests.post(url, json=payload, timeout=30)
    except requests.exceptions.RequestException as exc:
        if attempt < MAX_RETRIES:
            wait = 2 ** attempt
            log.warning(f'    Conexão falhou ({exc.__class__.__name__}). Retry {attempt+1} em {wait}s')
            time.sleep(wait)
            return omie_post(endpoint, call, params, attempt + 1)
        return {'faultstring': f'connection_error: {exc.__class__.__name__}'}

    # Rate limit
    if r.status_code == 429:
        if attempt < MAX_RETRIES:
            log.warning(f'    Rate limit (429). Aguardando {SLEEP_RATE_LIMIT}s...')
            time.sleep(SLEEP_RATE_LIMIT)
            return omie_post(endpoint, call, params, attempt + 1)
        return {'faultstring': 'rate_limit_exceeded'}

    # Erros de servidor
    if r.status_code >= 500:
        if attempt < MAX_RETRIES:
            wait = 2 ** attempt
            log.warning(f'    Erro {r.status_code}. Retry {attempt+1}/{MAX_RETRIES} em {wait}s')
            time.sleep(wait)
            return omie_post(endpoint, call, params, attempt + 1)
        return {'faultstring': f'http_{r.status_code}'}

    try:
        return r.json()
    except Exception:
        return {'faultstring': f'json_parse_error (status={r.status_code})'}


def find_list_key(response: dict) -> str | None:
    """Retorna a primeira chave cujo valor é uma lista não-vazia."""
    for k, v in response.items():
        if isinstance(v, list) and len(v) > 0:
            return k
    return None


def needs_date_filter(method: str) -> bool:
    """Heurística: método provavelmente precisa de filtro de data?"""
    m = method.lower()
    return any(kw in m for kw in DATE_FILTER_KEYWORDS)


def base_params_for(method: str) -> dict:
    """Retorna parâmetros base para chamadas que precisam de datas."""
    if needs_date_filter(method):
        return {
            'dDtInicio':       DATE_START,
            'dDtFim':          DATE_TODAY,
            'dDtEmissaoInicio': DATE_START,
            'dDtEmissaoFim':   DATE_TODAY,
            'dDtIni':          DATE_START,
            'dDtFim2':         DATE_TODAY,
        }
    return {}


def fetch_paginated(endpoint: str, call: str, extra_params: dict) -> list:
    """
    Busca TODOS os registros de um método Listar/Pesquisar com paginação.
    Respeita limite de 500 registros/página (recomendação Omie).
    """
    records   = []
    page      = 1
    total_pgs = 1
    list_key  = None

    while page <= total_pgs:
        params = {
            **extra_params,
            'pagina':               page,
            'registros_por_pagina': PAGE_SIZE,
        }
        result = omie_post(endpoint, call, params)

        # Erro na chamada paginada
        if 'faultstring' in result:
            fault = str(result['faultstring'])
            if page == 1:
                log.debug(f'    Paginação falhou: {fault[:120]}')
                # Tenta sem paginação (alguns endpoints não suportam)
                result2 = omie_post(endpoint, call, extra_params)
                if 'faultstring' not in result2:
                    lk = find_list_key(result2)
                    if lk:
                        recs = result2[lk]
                        log.info(f'    [sem-paginação] {len(recs)} registros')
                        return recs
                    # Resposta sem lista → trata como objeto único
                    clean = {k: v for k, v in result2.items()
                             if not k.startswith('fault') and k != 'call'}
                    return [clean] if clean else []
                log.warning(f'    Falha total: {fault[:140]}')
            break

        # Primeira página: descobre chave da lista e total de páginas
        if page == 1:
            list_key = find_list_key(result)
            if not list_key:
                # Resposta sem lista (ex: método retorna objeto único)
                clean = {k: v for k, v in result.items()
                         if not k.startswith('fault') and k != 'call'}
                return [clean] if clean else []

            total_pgs = (
                result.get('total_de_paginas') or
                result.get('nTotPaginas') or
                result.get('total_pages') or
                1
            )
            total_pgs = int(total_pgs)

        chunk = result.get(list_key, [])
        records.extend(chunk)
        log.info(f'    Pág {page:>3}/{total_pgs:<3}: +{len(chunk):<4} → {len(records)} total')

        if page >= total_pgs:
            break

        page += 1
        time.sleep(SLEEP_BETWEEN)   # respeita rate limit

    return records


def fetch_obter(endpoint: str, call: str) -> list:
    """
    Tenta Obter*/Consultar*/Get* sem parâmetros de ID.
    Retorna registros se a API responder sem exigir código.
    Retorna [] se precisar de ID obrigatório (esperado para maioria).
    """
    result = omie_post(endpoint, call, {})

    if 'faultstring' in result:
        fault = str(result['faultstring']).lower()
        # Erros esperados quando o método precisa de ID
        id_required = any(kw in fault for kw in (
            'obrigatorio', 'required', 'not found', 'não encontrado',
            'codigo', 'nao informado', 'invalid', 'nenhum',
            'parametro', 'campo', 'necessario',
        ))
        if id_required:
            log.debug(f'    {call}: exige ID → pulando (esperado)')
        else:
            log.warning(f'    {call}: erro inesperado: {str(result["faultstring"])[:100]}')
        return []

    lk = find_list_key(result)
    if lk:
        return result[lk]

    clean = {k: v for k, v in result.items()
             if not k.startswith('fault') and k not in ('call', 'app_key', 'app_secret')}
    return [clean] if clean else []


# ──────────────────────────────────────────────────────────────────
#  SUPABASE
# ──────────────────────────────────────────────────────────────────

SB_INSERT_HEADERS = {
    'apikey':        SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type':  'application/json',
    'Prefer':        'return=minimal',
}

SB_DELETE_HEADERS = {
    'apikey':        SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Prefer':        'return=minimal',
}

SB_COUNT_HEADERS = {
    'apikey':        SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Prefer':        'count=exact',
    'Range':         '0-0',
}


def sb_table_url(table_name: str) -> str:
    """
    Constrói a URL PostgREST para tabelas com caracteres especiais.
    Ex: '1.1.7. ListarClientes' → '.../rest/v1/1.1.7.%20ListarClientes'
    """
    encoded = urllib.parse.quote(table_name, safe='.')
    return f'{SUPABASE_URL}/rest/v1/{encoded}'


def sb_count(table_name: str) -> int:
    """Retorna a contagem de registros na tabela (-1 em caso de erro)."""
    url = sb_table_url(table_name)
    try:
        r = requests.get(url, headers=SB_COUNT_HEADERS, timeout=15)
        cr = r.headers.get('content-range', '')
        # content-range: 0-0/TOTAL
        if '/' in cr:
            total = cr.split('/')[-1]
            return int(total) if total != '*' else 0
        return 0
    except Exception:
        return -1


def sb_clear(table_name: str) -> bool:
    """
    Remove TODOS os registros da tabela (--fresh).
    Usa filtro `created_at=not.is.null` (coluna NOT NULL → seleciona tudo).
    """
    url = sb_table_url(table_name) + '?created_at=not.is.null'
    try:
        r = requests.delete(url, headers=SB_DELETE_HEADERS, timeout=30)
        return r.status_code in (200, 204)
    except Exception as exc:
        log.error(f'    Erro ao limpar {table_name}: {exc}')
        return False


def sb_insert(table_name: str, records: list) -> int:
    """
    Insere registros em lotes de 500 no Supabase.
    Retorna quantidade inserida.
    """
    if not records:
        return 0

    url      = sb_table_url(table_name)
    inserted = 0

    for i in range(0, len(records), 500):
        chunk = records[i:i + 500]
        try:
            r = requests.post(
                url,
                headers=SB_INSERT_HEADERS,
                json=chunk,
                timeout=60,
            )
            if r.status_code in (200, 201):
                inserted += len(chunk)
            else:
                log.error(f'    SB [{r.status_code}]: {r.text[:200]}')
        except Exception as exc:
            log.error(f'    SB exception: {exc}')

    return inserted


# ──────────────────────────────────────────────────────────────────
#  SYNC DE UMA TABELA
# ──────────────────────────────────────────────────────────────────

def sync_table(entry: dict, fresh: bool = False, dry_run: bool = False) -> dict:
    """
    Processa uma tabela. Retorna dict de resultado.
    """
    table    = entry['table']
    method   = entry['method']
    endpoint = entry['endpoint']
    call     = entry['call']
    cat      = entry['category']

    log.info(f'')
    log.info(f'{"─" * 62}')
    log.info(f'[{cat:12s}] {table}')

    # ── SKIP: nunca chamar ──────────────────────────────────────
    if cat == 'SKIP':
        log.info(f'    → IGNORADO (Excluir/Cancelar — destrutivo)')
        return _result(table, cat, 0, 0, 'skipped')

    # ── WRITE_OP: operação de escrita, não ETL ──────────────────
    if cat == 'WRITE_OP':
        log.info(f'    → WRITE_OP (populado pela aplicação ao executar a operação)')
        return _result(table, cat, 0, 0, 'write_op')

    # ── dry-run ────────────────────────────────────────────────
    if dry_run:
        log.info(f'    [DRY-RUN] Endpoint: {endpoint} | Call: {call}')
        return _result(table, cat, 0, 0, 'dry_run')

    # ── Verifica se tabela já tem dados ─────────────────────────
    if not fresh:
        existing = sb_count(table)
        if existing > 0:
            log.info(f'    Tabela já contém {existing} registros → pulando (use --fresh para re-sincronizar)')
            return _result(table, cat, existing, 0, f'already_populated({existing})')

    # ── Busca dados na API Omie ──────────────────────────────────
    log.info(f'    Endpoint : {endpoint}')
    log.info(f'    Call     : {call}')

    if cat == 'LISTAR_SYNC':
        extra   = base_params_for(method)
        records = fetch_paginated(endpoint, call, extra)

    elif cat == 'OBTER_TRY':
        records = fetch_obter(endpoint, call)

    else:
        records = []

    fetched = len(records)
    log.info(f'    Registros API: {fetched}')

    if fetched == 0:
        return _result(table, cat, 0, 0, 'sem_dados')

    # ── Limpa tabela se --fresh ──────────────────────────────────
    if fresh:
        ok = sb_clear(table)
        log.info(f'    Tabela limpa: {"✓" if ok else "✗"}')

    # ── Monta registros para o Supabase ─────────────────────────
    # Cada registro da API vai inteiro dentro de dados_raw (JSONB)
    sb_records = [{'dados_raw': rec} for rec in records]

    # ── Insere no Supabase ───────────────────────────────────────
    inserted = sb_insert(table, sb_records)
    status   = 'ok' if inserted == fetched else f'parcial_{inserted}/{fetched}'
    log.info(f'    Supabase: {inserted}/{fetched} inseridos [{status}]')

    return _result(table, cat, fetched, inserted, status)


def _result(table, category, fetched, inserted, status):
    return {
        'table':    table,
        'category': category,
        'fetched':  fetched,
        'inserted': inserted,
        'status':   status,
    }


# ──────────────────────────────────────────────────────────────────
#  RELATÓRIO FINAL
# ──────────────────────────────────────────────────────────────────

def print_summary(results: list, elapsed: float):
    ok          = [r for r in results if r['status'] == 'ok']
    parciais    = [r for r in results if r['status'].startswith('parcial_')]
    sem_dados   = [r for r in results if r['status'] == 'sem_dados']
    populated   = [r for r in results if r['status'].startswith('already_populated')]
    write_ops   = [r for r in results if r['status'] == 'write_op']
    skipped     = [r for r in results if r['status'] == 'skipped']
    dry_runs    = [r for r in results if r['status'] == 'dry_run']

    total_f = sum(r['fetched']  for r in results)
    total_i = sum(r['inserted'] for r in results)

    log.info('')
    log.info('=' * 62)
    log.info(f'RESUMO — {len(results)} tabelas em {elapsed:.0f}s')
    log.info('=' * 62)
    log.info(f'  ✅ Sync OK              : {len(ok):>3}')
    log.info(f'  ⚠️  Parcial              : {len(parciais):>3}')
    log.info(f'  ○  Sem dados            : {len(sem_dados):>3}')
    log.info(f'  📦 Já populadas (skip)  : {len(populated):>3}')
    log.info(f'  ✏️  Write ops (skip ETL) : {len(write_ops):>3}')
    log.info(f'  🚫 Excluir/Cancelar     : {len(skipped):>3}')
    if dry_runs:
        log.info(f'  🔍 Dry-run              : {len(dry_runs):>3}')
    log.info(f'  Registros : {total_f:>6} buscados → {total_i:>6} inseridos')

    if parciais:
        log.warning('\n  Parciais:')
        for r in parciais:
            log.warning(f'    {r["table"]:<55} {r["status"]}')

    if sem_dados:
        log.info('\n  Sem dados (Obter* sem ID ou endpoint sem registros):')
        for r in sem_dados:
            log.info(f'    {r["table"]:<55} [{r["category"]}]')

    # Tabelas WRITE_OP (para informação)
    log.info('\n  ✏️  WRITE_OPs (populadas pela app, não pelo ETL):')
    for r in write_ops[:10]:
        log.info(f'    {r["table"]}')
    if len(write_ops) > 10:
        log.info(f'    ... e mais {len(write_ops) - 10} tabelas')

    log.info('\n  🚫 SKIP (Excluir/Cancelar — nunca chamados):')
    for r in skipped[:10]:
        log.info(f'    {r["table"]}')
    if len(skipped) > 10:
        log.info(f'    ... e mais {len(skipped) - 10} tabelas')


def save_log(results: list, elapsed: float):
    """Salva log JSON com timestamp."""
    log_dir  = Path(__file__).parent / 'logs'
    log_dir.mkdir(exist_ok=True)
    log_path = log_dir / f'sync_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'

    payload = {
        'run_at':    datetime.now().isoformat(),
        'elapsed_s': round(elapsed, 1),
        'summary': {
            'total':      len(results),
            'ok':         sum(1 for r in results if r['status'] == 'ok'),
            'sem_dados':  sum(1 for r in results if r['status'] == 'sem_dados'),
            'write_ops':  sum(1 for r in results if r['status'] == 'write_op'),
            'skipped':    sum(1 for r in results if r['status'] == 'skipped'),
            'fetched':    sum(r['fetched']  for r in results),
            'inserted':   sum(r['inserted'] for r in results),
        },
        'results': results,
    }

    with open(log_path, 'w', encoding='utf-8') as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    log.info(f'\n  Log salvo: {log_path}')
    return log_path


# ──────────────────────────────────────────────────────────────────
#  MAIN
# ──────────────────────────────────────────────────────────────────

def parse_args():
    p = argparse.ArgumentParser(
        description='ETL Omie → Supabase (schema hierárquico)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    p.add_argument(
        '--fresh', action='store_true',
        help='Limpa cada tabela antes de inserir (re-sincronização completa)',
    )
    p.add_argument(
        '--dry-run', action='store_true', dest='dry_run',
        help='Mostra o plano sem chamar a API Omie',
    )
    p.add_argument(
        '--categoria', choices=['LISTAR_SYNC', 'OBTER_TRY', 'WRITE_OP', 'SKIP'],
        help='Processa somente esta categoria',
    )
    p.add_argument(
        '--tabela', type=str,
        help='Filtra tabelas cujo nome contenha este texto (case-insensitive)',
    )
    p.add_argument(
        '--modulo', type=str,
        help='Processa somente tabelas do módulo N (ex: --modulo 1)',
    )
    p.add_argument(
        '--listar-plano', action='store_true', dest='listar_plano',
        help='Mostra todas as tabelas e suas categorias sem executar nada',
    )
    return p.parse_args()


def main():
    args    = parse_args()
    entries = parse_md()

    # ── Filtros ──────────────────────────────────────────────────
    if args.categoria:
        entries = [e for e in entries if e['category'] == args.categoria]

    if args.tabela:
        entries = [e for e in entries
                   if args.tabela.lower() in e['table'].lower()]

    if args.modulo:
        entries = [e for e in entries
                   if e['table'].startswith(args.modulo + '.')]

    # ── Listar plano ─────────────────────────────────────────────
    if args.listar_plano:
        cats = {}
        for e in entries:
            cats.setdefault(e['category'], []).append(e['table'])

        for cat in ('LISTAR_SYNC', 'OBTER_TRY', 'WRITE_OP', 'SKIP'):
            tables = cats.get(cat, [])
            print(f'\n{"─"*60}')
            print(f'{cat} ({len(tables)} tabelas):')
            for t in tables:
                print(f'  {t}')
        return

    log.info(f'')
    log.info(f'{"="*62}')
    log.info(f'  sync_omie_v2 — {len(entries)} tabelas a processar')
    log.info(f'  fresh={args.fresh} | dry_run={args.dry_run}')
    log.info(f'  Data range: {DATE_START} → {DATE_TODAY}')
    log.info(f'{"="*62}')

    start   = time.time()
    results = []

    for entry in entries:
        result = sync_table(entry, fresh=args.fresh, dry_run=args.dry_run)
        results.append(result)

        # Pausa extra após chamadas reais para respeitar rate limit global
        if entry['category'] in ('LISTAR_SYNC', 'OBTER_TRY') and not args.dry_run:
            time.sleep(SLEEP_BETWEEN)

    elapsed = time.time() - start
    print_summary(results, elapsed)

    if not args.dry_run:
        save_log(results, elapsed)


if __name__ == '__main__':
    main()
