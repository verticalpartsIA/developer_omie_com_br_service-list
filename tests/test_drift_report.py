from omie_mcp.drift_report import build_issue_body, build_issue_title, main


def _diff(**overrides):
    base = {
        "status": "changed",
        "previous_captured_at": "2026-09-25T09:17:00+00:00",
        "current_captured_at": "2026-09-26T09:17:00+00:00",
        "services_before": 10,
        "services_after": 11,
        "hash_after": "abc123",
        "added_services": [],
        "removed_services": [],
        "changed_services": [],
        "changed_service_pages": [],
    }
    base.update(overrides)
    return base


def test_title_usa_data_da_captura_atual():
    assert build_issue_title(_diff()) == (
        "🔭 Radar Omie: mudança na documentação oficial (2026-09-26)"
    )


def test_body_lista_servicos_adicionados_e_removidos():
    diff = _diff(
        added_services=[{"name": "Telemarketing", "endpoint": "/crm/telemarketing/"}],
        removed_services=[{"name": "Finders", "endpoint": "/crm/finders/"}],
    )
    body = build_issue_body(diff)
    assert "### Serviços adicionados (1)" in body
    assert "- Telemarketing" in body
    assert "### Serviços removidos (1)" in body
    assert "- Finders" in body


def test_body_trunca_paginas_alteradas_apos_30():
    changed_pages = [{"endpoint": f"/svc/{i}/"} for i in range(35)]
    body = build_issue_body(_diff(changed_service_pages=changed_pages))
    assert "### Páginas de serviço com conteúdo alterado (35)" in body
    assert "- … e mais 5" in body


def test_body_inclui_marcador_de_hash_para_deduplicacao():
    body = build_issue_body(_diff(hash_after="deadbeef"))
    assert "<!-- omie-drift-hash: deadbeef -->" in body


def test_main_nao_reporta_quando_status_unchanged(tmp_path, capsys):
    diff_path = tmp_path / "diff.json"
    diff_path.write_text('{"status": "unchanged"}', encoding="utf-8")
    main(["--diff-path", str(diff_path)])
    assert "nada a reportar" in capsys.readouterr().out


def test_main_dry_run_nao_chama_gh(tmp_path, capsys):
    import json

    diff_path = tmp_path / "diff.json"
    diff_path.write_text(json.dumps(_diff()), encoding="utf-8")
    main(["--diff-path", str(diff_path), "--dry-run"])
    out = capsys.readouterr().out
    assert "[dry-run] título:" in out
    assert "2026-09-26" in out
