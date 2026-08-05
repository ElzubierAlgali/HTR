# Thesis chapters ready for integration

Generated: 2026-08-03 18:59 UTC

## Backups
- Main DOCX backup: `Enhancing Handwritten Text Recognition Using Transformer Models Derived from Large Language Models.docx.bak` (if main existed)

## Replace / insert these chapter documents
- Chapter 3: `docs\CHAPTER_3_METHODOLOGY.docx`
- Chapter 4: `docs\CHAPTER_4_IMPLEMENTATION_RESULTS.docx`
- Boundaries: `docs/CHAPTER_BOUNDARIES.md`
- Filled rewrite: `docs/THESIS_REWRITE_FILLED.md`
- Appendix pointers: `docs/APPENDIX_CODE.md`

## Before final submission
- Run GPU protocol (`docs/GPU_PROTOCOL.md`) so E1–E4 have n=2915
- Re-run `scripts/fill_thesis_metrics.py` and rebuild Ch4 DOCX
- Confirm every Ch4 number matches `experiments/<run_id>/metrics.json`
- Do not use smoke/synthetic CER as primary thesis numbers
