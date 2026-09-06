#!/usr/bin/env python3
"""Backup main thesis DOCX and rebuild every chapter document as a sibling file.

Full OOXML merge into the original thesis is fragile; this script:
1. Copies the main DOCX to .docx.bak
2. Rebuilds the Abstract and CHAPTER_1..5 DOCX from their builders
3. Writes docs/THESIS_CHAPTERS_READY.md checklist for manual paste / supervisor review
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
MAIN = REPO / (
    "Enhancing Handwritten Text Recognition Using Transformer Models "
    "Derived from Large Language Models.docx"
)
SCRIPTS_DIR = REPO / "scripts"
DOCS_DIR = REPO / "docs"

# Ordered as the chapters appear in the thesis.
BUILD_TARGETS = [
    ("Abstract", SCRIPTS_DIR / "rebuild_abstract_docx.py", DOCS_DIR / "ABSTRACT.docx"),
    ("Chapter 1", SCRIPTS_DIR / "rebuild_chapter1_docx.py", DOCS_DIR / "CHAPTER_1_INTRODUCTION.docx"),
    (
        "Chapter 2",
        SCRIPTS_DIR / "rebuild_chapter2_docx.py",
        DOCS_DIR / "CHAPTER_2_LITERATURE_REVIEW.docx",
    ),
    ("Chapter 3", SCRIPTS_DIR / "rebuild_chapter3_docx.py", DOCS_DIR / "CHAPTER_3_METHODOLOGY.docx"),
    (
        "Chapter 4",
        SCRIPTS_DIR / "rebuild_chapter4_docx.py",
        DOCS_DIR / "CHAPTER_4_IMPLEMENTATION_RESULTS.docx",
    ),
    ("Chapter 5", SCRIPTS_DIR / "rebuild_chapter5_docx.py", DOCS_DIR / "CHAPTER_5_CONCLUSION.docx"),
]

READY = DOCS_DIR / "THESIS_CHAPTERS_READY.md"


def main() -> int:
    if MAIN.exists():
        bak = MAIN.with_suffix(MAIN.suffix + ".bak")
        shutil.copy2(MAIN, bak)
        print(f"Backup: {bak}")
    else:
        print(f"Main thesis DOCX not found at {MAIN} (skipping backup)")

    for _, script, _ in BUILD_TARGETS:
        subprocess.check_call([sys.executable, str(script)], cwd=REPO)

    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    document_lines = [
        f"- {label}: `{output.relative_to(REPO)}`" for label, _, output in BUILD_TARGETS
    ]
    READY.write_text(
        "\n".join(
            [
                "# Thesis chapters ready for integration",
                "",
                f"Generated: {stamp}",
                "",
                "## Backups",
                f"- Main DOCX backup: `{MAIN.name}.bak` (if main existed)",
                "",
                "## Replace / insert these documents",
                *document_lines,
                "- Boundaries: `docs/CHAPTER_BOUNDARIES.md`",
                "- Writing style: `docs/WRITING_STYLE.md`",
                "- Filled rewrite: `docs/THESIS_REWRITE_FILLED.md`",
                "- Appendix pointers: `docs/APPENDIX_CODE.md`",
                "",
                "## Before final submission",
                "- Primary claims: E1–E4 full test (n=2915); E5 demo qualitative only",
                "- Re-run `scripts/fill_thesis_metrics.py` and rebuild every chapter DOCX",
                "- Confirm every Ch4/Ch5 number matches `experiments/<run_id>/metrics.json`",
                "- Confirm fine-tune narrative matches train_log.json (early stop; no CER gain vs Hub)",
                "- Do not use smoke/synthetic CER as primary thesis numbers",
                "- Confirm Ch1 objectives and Ch2 TrOCR row still match `docs/RESEARCH_SCOPE.md`",
                "- Paste/replace the Abstract and Chapters 1–5 from the rebuilt DOCX into the main thesis",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(f"Wrote {READY}")
    for label, _, output in BUILD_TARGETS:
        print(f"{label} DOCX: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
