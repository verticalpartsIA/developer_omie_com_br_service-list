from omie_mcp.watcher import _normalize_text


def test_normalize_text_ignora_nonce_csp_volatil():
    a = '<style type="text/css" media="all" nonce="t0pWJM6eAG7zrOja/RKliQ==">body{}</style>'
    b = '<style type="text/css" media="all" nonce="Plc/s7cjMVxR8V9RplXN5g==">body{}</style>'
    assert _normalize_text(a) == _normalize_text(b)


def test_normalize_text_ainda_detecta_mudanca_real():
    a = '<style nonce="t0pWJM6eAG7zrOja/RKliQ==">body{color:red}</style>'
    b = '<style nonce="Plc/s7cjMVxR8V9RplXN5g==">body{color:blue}</style>'
    assert _normalize_text(a) != _normalize_text(b)


def test_normalize_text_colapsa_espacos_como_antes():
    assert _normalize_text("a   b\n\n  c  ") == "a b\nc"
