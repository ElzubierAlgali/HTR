#!/usr/bin/env python3
"""Backup main thesis DOCX and append rebuilt Chapter 3/4 documents as siblings.

Full OOXML merge into the original thesis is fragile; this script:
1. Copies the main DOCX to .docx.bak
2. Ensures CHAPTER_3/4 DOCX exist (rebuilds if missing)
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
CH3_SCRIPT = REPO / "scripts" / "rebuild_chapter3_docx.py"
CH4_SCRIPT = REPO / "scripts" / "rebuild_chapter4_docx.py"
CH3 = REPO / "docs" / "CHAPTER_3_METHODOLOGY.docx"
CH4 = REPO / "docs" / "CHAPTER_4_IMPLEMENTATION_RESULTS.docx"
READY = REPO / "docs" / "THESIS_CHAPTERS_READY.md"


def main() -> int:
    if MAIN.exists():
        bak = MAIN.with_suffix(MAIN.suffix + ".bak")
        shutil.copy2(MAIN, bak)
        print(f"Backup: {bak}")
    else:
        print(f"Main thesis DOCX not found at {MAIN} (skipping backup)")

    for script in (CH3_SCRIPT, CH4_SCRIPT):
        subprocess.check_call([sys.executable, str(script)], cwd=REPO)

    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
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
                "## Replace / insert these chapter documents",
                f"- Chapter 3: `{CH3.relative_to(REPO)}`",
                f"- Chapter 4: `{CH4.relative_to(REPO)}`",
                "- Boundaries: `docs/CHAPTER_BOUNDARIES.md`",
                "- Filled rewrite: `docs/THESIS_REWRITE_FILLED.md`",
                "- Appendix pointers: `docs/APPENDIX_CODE.md`",
                "",
                "## Before final submission",
                "- Run GPU protocol (`docs/GPU_PROTOCOL.md`) so E1–E4 have n=2915",
                "- Re-run `scripts/fill_thesis_metrics.py` and rebuild Ch4 DOCX",
                "- Confirm every Ch4 number matches `experiments/<run_id>/metrics.json`",
                "- Do not use smoke/synthetic CER as primary thesis numbers",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(f"Wrote {READY}")
    print(f"Chapter 3 DOCX: {CH3}")
    print(f"Chapter 4 DOCX: {CH4}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
