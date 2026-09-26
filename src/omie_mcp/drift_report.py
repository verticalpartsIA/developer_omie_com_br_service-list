from __future__ import annotations

import argparse
import json
import os
import subprocess
from pathlib import Path
from typing import Any

MARKER_PREFIX = "<!-- omie-drift-hash: "
MARKER_SUFFIX = " -->"
ISSUE_TITLE_PREFIX = "🔭 Radar Omie: mudança na documentação oficial"


def _service_label(row: dict[str, Any]) -> str:
    return str(row.get("name") or row.get("endpoint") or row)


def build_issue_title(diff: dict[str, Any]) -> str:
    date = str(diff.get("current_captured_at") or "")[:10]
    return f"{ISSUE_TITLE_PREFIX} ({date})" if date else ISSUE_TITLE_PREFIX


def build_issue_body(diff: dict[str, Any]) -> str:
    added = diff.get("added_services") or []
    removed = diff.get("removed_services") or []
    changed_services = diff.get("changed_services") or []
    changed_pages = diff.get("changed_service_pages") or []

    lines = [
        "Radar automático (`omie-docs-drift.yml`) detectou mudança na documentação oficial do Omie.",
        "",
        f"- Captura anterior: `{diff.get('previous_captured_at')}`",
        f"- Captura atual: `{diff.get('current_captured_at')}`",
        f"- Serviços antes/depois: {diff.get('services_before')} → {diff.get('services_after')}",
        "",
    ]

    if added:
        lines.append(f"### Serviços adicionados ({len(added)})")
        lines.extend(f"- {_service_label(row)}" for row in added)
        lines.append("")

    if removed:
        lines.append(f"### Serviços removidos ({len(removed)})")
        lines.extend(f"- {_service_label(row)}" for row in removed)
        lines.append("")

    if changed_services:
        lines.append(f"### Metadados de serviço alterados ({len(changed_services)})")
        for row in changed_services:
            lines.append(f"- {_service_label(row.get('after') or row.get('before') or {})}")
        lines.append("")

    if changed_pages:
        lines.append(f"### Páginas de serviço com conteúdo alterado ({len(changed_pages)})")
        for row in changed_pages[:30]:
            lines.append(f"- `{row.get('endpoint')}`")
        if len(changed_pages) > 30:
            lines.append(f"- … e mais {len(changed_pages) - 30}")
        lines.append("")

    lines.append(
        "Próximo passo (ver `OMIE_GAPS_ATUAIS.md`): registrar a diferença, classificar o módulo "
        "afetado e atualizar README/instructions quando necessário. Feche esta issue quando a "
        "mudança tiver sido incorporada ao conhecimento curado."
    )
    lines.append("")
    lines.append(f"{MARKER_PREFIX}{diff.get('hash_after')}{MARKER_SUFFIX}")
    return "\n".join(lines)


def _run(*args: str) -> str:
    return subprocess.run(args, check=True, capture_output=True, text=True).stdout


def _already_reported(hash_after: str | None, repo: str) -> bool:
    if not hash_after:
        return False
    out = _run(
        "gh", "issue", "list", "--repo", repo, "--state", "open",
        "--search", f'"{ISSUE_TITLE_PREFIX}" in:title', "--json", "number",
    )
    for row in json.loads(out):
        body_json = _run(
            "gh", "issue", "view", str(row["number"]), "--repo", repo, "--json", "body",
        )
        if hash_after in json.loads(body_json)["body"]:
            return True
    return False


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Reporta drift da documentação Omie como Issue.")
    parser.add_argument(
        "--diff-path", default=os.environ.get("OMIE_DRIFT_DIFF_PATH", "omie-docs-diff.json"),
    )
    parser.add_argument("--repo", default=os.environ.get("GH_REPO"))
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Mostra título/corpo sem criar a Issue nem chamar a API do GitHub.",
    )
    args = parser.parse_args(argv)

    diff = json.loads(Path(args.diff_path).read_text(encoding="utf-8"))

    if diff.get("status") != "changed":
        print(f"status={diff.get('status')!r}: nada a reportar.")
        return

    title = build_issue_title(diff)
    body = build_issue_body(diff)

    if args.dry_run:
        print(f"[dry-run] título: {title}")
        print("[dry-run] corpo:")
        print(body)
        return

    if not args.repo:
        raise SystemExit("--repo (ou env GH_REPO) é obrigatório fora de --dry-run.")

    if _already_reported(diff.get("hash_after"), args.repo):
        print("Mudança já reportada em Issue aberta; não duplicando.")
        return

    _run("gh", "issue", "create", "--repo", args.repo, "--title", title, "--body", body)
    print(f"Issue criada: {title}")


if __name__ == "__main__":
    main()
