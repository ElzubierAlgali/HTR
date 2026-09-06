# Thesis chapters ready for integration

Generated: 2026-08-14 08:48 UTC

## Backups
- Main DOCX backup: `Enhancing Handwritten Text Recognition Using Transformer Models Derived from Large Language Models.docx.bak` (if main existed)

## Replace / insert these chapter documents
- Chapter 3: `docs\CHAPTER_3_METHODOLOGY.docx`
- Chapter 4: `docs\CHAPTER_4_IMPLEMENTATION_RESULTS.docx`
- Chapter 5: `docs\CHAPTER_5_CONCLUSION.docx`
- Boundaries: `docs/CHAPTER_BOUNDARIES.md`
- Filled rewrite: `docs/THESIS_REWRITE_FILLED.md`
- Filled Ch5: `docs/CHAPTER_5_CONCLUSION_FILLED.md`
- Appendix pointers: `docs/APPENDIX_CODE.md`

## Before final submission
- Primary claims: E1–E3 full test (n=2915); E4 Tesseract optional; E5 demo qualitative only
- Re-run `scripts/fill_thesis_metrics.py` and rebuild Ch3/Ch4/Ch5 DOCX
- Confirm every Ch4/Ch5 number matches `experiments/<run_id>/metrics.json`
- Confirm fine-tune narrative matches train_log.json (early stop; no CER gain vs Hub)
- Do not use smoke/synthetic CER as primary thesis numbers
- Paste/replace Chapters 3–5 from the rebuilt DOCX into the main thesis
