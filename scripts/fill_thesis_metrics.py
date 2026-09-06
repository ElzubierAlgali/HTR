#!/usr/bin/env python3
"""Inject experiment metrics into thesis markdown placeholders."""

from __future__ import annotations

import json
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
EXPERIMENTS = REPO_ROOT / "experiments"
JOBS = [
    (REPO_ROOT / "docs" / "THESIS_REWRITE.md", REPO_ROOT / "docs" / "THESIS_REWRITE_FILLED.md"),
    (
        REPO_ROOT / "docs" / "CHAPTER_1_INTRODUCTION.md",
        REPO_ROOT / "docs" / "CHAPTER_1_INTRODUCTION_FILLED.md",
    ),
    (
        REPO_ROOT / "docs" / "CHAPTER_2_LITERATURE_REVIEW.md",
        REPO_ROOT / "docs" / "CHAPTER_2_LITERATURE_REVIEW_FILLED.md",
    ),
    (
        REPO_ROOT / "docs" / "CHAPTER_4_IMPLEMENTATION_RESULTS.md",
        REPO_ROOT / "docs" / "CHAPTER_4_IMPLEMENTATION_RESULTS_FILLED.md",
    ),
    (
        REPO_ROOT / "docs" / "CHAPTER_5_CONCLUSION.md",
        REPO_ROOT / "docs" / "CHAPTER_5_CONCLUSION_FILLED.md",
    ),
    (REPO_ROOT / "docs" / "ABSTRACT.md", REPO_ROOT / "docs" / "ABSTRACT_FILLED.md"),
]


def load_metric(run_id: str, field: str) -> str:
    path = EXPERIMENTS / run_id / "metrics.json"
    if not path.exists():
        return f"[pending:{run_id}.{field}]"
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if data.get("status") == "skipped":
        return f"[skipped: {data.get('reason', 'n/a')}]"
    value = data.get(field, "?")
    if field in ("cer", "wer") and isinstance(value, (int, float)):
        pct = f"{value * 100:.2f}%"
        if data.get("protocol") == "smoke_synthetic":
            return f"{pct} [SMOKE—not primary]"
        return pct
    return str(value)


def has_smoke_metrics() -> bool:
    for run_id in ("iam_trocr_handwritten", "iam_trocr_finetuned", "iam_crnn"):
        path = EXPERIMENTS / run_id / "metrics.json"
        if not path.exists():
            continue
        data = json.loads(path.read_text(encoding="utf-8-sig"))
        if data.get("protocol") == "smoke_synthetic":
            return True
    return False


def fill_text(text: str) -> str:
    def replacer(match: re.Match) -> str:
        return load_metric(match.group(1), match.group(2))

    filled = re.sub(r"\{\{METRIC:([^.]+)\.([^}]+)\}\}", replacer, text)
    if has_smoke_metrics():
        banner = (
            "> **WARNING:** Current experiment metrics are CPU smoke / synthetic. "
            "Run `docs/GPU_PROTOCOL.md` before submitting thesis numbers.\n\n"
        )
        filled = banner + filled
    return filled


def main() -> None:
    for template, output in JOBS:
        if not template.exists():
            print(f"Skip missing template: {template}")
            continue
        output.write_text(fill_text(template.read_text(encoding="utf-8")), encoding="utf-8")
        print(f"Wrote {output}")


if __name__ == "__main__":
    main()
