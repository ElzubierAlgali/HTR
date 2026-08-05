#!/usr/bin/env python3
"""Extract high-CER prediction examples for Chapter 4 analysis."""

from __future__ import annotations

import csv
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
EXPERIMENTS = REPO_ROOT / "experiments"
OUT = EXPERIMENTS / "figures" / "error_examples.md"

RUNS = ["iam_trocr_handwritten", "iam_trocr_finetuned"]


def top_errors(run_id: str, k: int = 3) -> list[dict[str, str]]:
    path = EXPERIMENTS / run_id / "predictions.csv"
    if not path.exists():
        return []
    rows: list[dict[str, str]] = []
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            try:
                row["_cer"] = float(row["cer"])
            except (KeyError, ValueError):
                continue
            rows.append(row)
    rows.sort(key=lambda r: r["_cer"], reverse=True)
    return rows[:k]


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# High-CER error examples",
        "",
        "Extracted from `predictions.csv` for qualitative Chapter 4 analysis.",
        "",
    ]
    found = False
    for run_id in RUNS:
        examples = top_errors(run_id)
        if not examples:
            continue
        found = True
        lines.append(f"## `{run_id}`")
        lines.append("")
        for i, row in enumerate(examples, start=1):
            lines.append(f"### Example {i}")
            lines.append(f"- **filename:** `{row['filename']}`")
            lines.append(f"- **reference:** {row['reference']}")
            lines.append(f"- **prediction:** {row['prediction']}")
            lines.append(f"- **cer:** {float(row['cer']):.4f}")
            lines.append("")
    if not found:
        lines.append("_No predictions.csv found yet. Run evaluations first._")
        lines.append("")
    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
