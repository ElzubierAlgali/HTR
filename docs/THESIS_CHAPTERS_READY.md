# Thesis chapters ready for integration

Generated: 2026-09-06 19:44 UTC

## Backups
- Main DOCX backup: `Enhancing Handwritten Text Recognition Using Transformer Models Derived from Large Language Models.docx.bak` (if main existed)

## Replace / insert these documents
- Abstract: `docs\ABSTRACT.docx`
- Chapter 1: `docs\CHAPTER_1_INTRODUCTION.docx`
- Chapter 2: `docs\CHAPTER_2_LITERATURE_REVIEW.docx`
- Chapter 3: `docs\CHAPTER_3_METHODOLOGY.docx`
- Chapter 4: `docs\CHAPTER_4_IMPLEMENTATION_RESULTS.docx`
- Chapter 5: `docs\CHAPTER_5_CONCLUSION.docx`
- Boundaries: `docs/CHAPTER_BOUNDARIES.md`
- Writing style: `docs/WRITING_STYLE.md`
- Filled rewrite: `docs/THESIS_REWRITE_FILLED.md`
- Appendix pointers: `docs/APPENDIX_CODE.md` / `docs/APPENDIX.docx`
- References: `docs/REFERENCES.md` / `docs/REFERENCES.docx`
- Combined appendix + references: `docs/APPENDIX_AND_REFERENCES.docx`

## Before final submission
- Primary claims: E1–E4 full test (n=2915); E5 demo qualitative only
- Re-run `scripts/fill_thesis_metrics.py` and rebuild every chapter DOCX
- Confirm every Ch4/Ch5 number matches `experiments/<run_id>/metrics.json`
- Confirm fine-tune narrative matches train_log.json (early stop; no CER gain vs Hub)
- Do not use smoke/synthetic CER as primary thesis numbers
- Confirm Ch1 objectives and Ch2 TrOCR row still match `docs/RESEARCH_SCOPE.md`
- Paste/replace the Abstract and Chapters 1–5 from the rebuilt DOCX into the main thesis
