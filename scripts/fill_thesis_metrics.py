#!/usr/bin/env python3
"""Inject experiment metrics into THESIS_REWRITE placeholders."""

from __future__ import annotations

import json
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = REPO_ROOT / "docs" / "THESIS_REWRITE.md"
OUTPUT = REPO_ROOT / "docs" / "THESIS_REWRITE_FILLED.md"
EXPERIMENTS = REPO_ROOT / "experiments"


def load_metric(run_id: str, field: str) -> str:
    path = EXPERIMENTS / run_id / "metrics.json"
    if not path.exists():
        return f"[pending:{run_id}.{field}]"
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if data.get("status") == "skipped":
        return f"[skipped: {data.get('reason', 'n/a')}]"
    value = data.get(field, "?")
    if field in ("cer", "wer") and isinstance(value, (int, float)):
        return f"{value * 100:.2f}%"
    return str(value)


def main() -> None:
    text = TEMPLATE.read_text(encoding="utf-8")

    def replacer(match: re.Match) -> str:
        run_id, field = match.group(1), match.group(2)
        return load_metric(run_id, field)

    filled = re.sub(r"\{\{METRIC:([^.]+)\.([^}]+)\}\}", replacer, text)
    OUTPUT.write_text(filled, encoding="utf-8")
    print(f"Wrote {OUTPUT}")


if __name__ == "__main__":
    main()
