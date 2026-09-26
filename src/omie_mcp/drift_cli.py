from __future__ import annotations

import asyncio
import json
from pathlib import Path

from .watcher import diff_official_docs


async def _run() -> int:
    result = await diff_official_docs(persist_new_snapshot=True, deep=True)
    out = Path("omie-docs-diff.json")
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({
        "status": result.get("status"),
        "services_before": result.get("services_before"),
        "services_after": result.get("services_after"),
        "added": len(result.get("added_services") or []),
        "removed": len(result.get("removed_services") or []),
        "changed_pages": len(result.get("changed_service_pages") or []),
        "artifact": str(out),
    }, ensure_ascii=False))
    return 0


def main() -> None:
    raise SystemExit(asyncio.run(_run()))


if __name__ == "__main__":
    main()
