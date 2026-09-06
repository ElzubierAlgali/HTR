# Thesis Chapter Map (English IAM only)

Maps thesis sections to code artifacts for traceability.

## Abstract

| Content | Source |
|---------|--------|
| English + Arabic abstracts | `docs/ABSTRACT.md` / `docs/ABSTRACT_FILLED.md` / `docs/ABSTRACT.docx` |
| IAM CER/WER (pretrained) | `experiments/iam_trocr_handwritten/metrics.json` |
| Fine-tuned CER/WER | `experiments/iam_trocr_finetuned/metrics.json` |
| Method | `docs/RESEARCH_SCOPE.md` |
| Application | Gradio demo (qualitative only; not primary CER) |

## Chapter 1 — Introduction

Prose source: `docs/CHAPTER_1_INTRODUCTION.md` (filled + DOCX via `scripts/rebuild_chapter1_docx.py`).

| Section | Code / data reference |
|---------|------------------------|
| 1.3 Problem statement | English line-level HTR on IAM (`docs/RESEARCH_SCOPE.md`) |
| 1.4 Aim and objectives | Evaluate + fine-tune TrOCR; CRNN/Tesseract baselines; Gradio demo |
| 1.5 Methodology outline | `scripts/prepare_iam_lines.py`, `src/htr/train.py`, `src/htr/metrics.py` |
| 1.5 Training hyperparameters | `experiments/iam_trocr_finetuned/train_log.json` |
| 1.6 Scope | 6,482 / 976 / 2,915 lines from `Teklia/IAM-line` |
| Excluded | GPT-3 / BERT / XLNet, architecture modification, precision / recall / F1, medical prescriptions, page-count framing |

## Chapter 2 — Literature Review

Prose source: `docs/CHAPTER_2_LITERATURE_REVIEW.md` (filled + DOCX via `scripts/rebuild_chapter2_docx.py`).

| Section | Source |
|---------|--------|
| TrOCR row in summary table | ViT image encoder + BART text decoder |
| Literature CER anchors | AttentionHTR 6.50%, Light Transformer 5.70%, GFCN 7.99% |
| Light Transformer secondary figure | 4.76% labelled "with additional synthetic data" |
| Accuracy figures (Balci, Manchala) | Reported as cited-study accuracy, not comparable with thesis CER |

## Chapter 3 — Methodology (design only)

| Section | Code / data reference |
|---------|------------------------|
| Dataset | `scripts/prepare_iam_lines.py`, `data/iam/processed/` |
| Model design | `src/htr/models.py`, `src/htr/baselines/crnn.py` |
| Preprocessing | `TrOCRProcessor`; train aug in `src/htr/augment.py` |
| Training design | `src/htr/train.py`, CRNN train script |
| Metrics | `src/htr/metrics.py` |
| Experiment design | configs E1–E5 (no result numbers in Ch3) |
| Prose source | `docs/CHAPTER_3_METHODOLOGY.md` |

## Chapter 4 — Implementation and Results

| Section | Artifact |
|---------|----------|
| Contribution / impl | `docs/CHAPTER_4_IMPLEMENTATION_RESULTS.md` |
| 4.x Pretrained TrOCR | `experiments/iam_trocr_handwritten/` |
| 4.x Fine-tuned TrOCR | `experiments/iam_trocr_finetuned/` (+ `train_log.json`) |
| 4.x CRNN | `experiments/iam_crnn/` |
| 4.x Tesseract | `experiments/iam_tesseract/` |
| 4.x Literature table | Cited values only |
| 4.x Demo | `experiments/iam_demo/predictions.csv` |
| Figures | `experiments/figures/cer_comparison.png` |
| Error examples | `experiments/figures/error_examples.md` |
| Application | `app/gradio_app.py` |

## Chapter 5 — Conclusion

Source: `docs/CHAPTER_5_CONCLUSION.md` (filled + DOCX via rebuild script).

Summarize full-test IAM English findings (pretrained vs fine-tuned vs CRNN), Gradio deployment, limitations, future work. Do not introduce new numeric claims beyond Chapter 4 artifacts.

## Appendices

| Content | Source |
|---------|--------|
| Code listings | `docs/APPENDIX_CODE.md` |

## Aligned thesis text

See `docs/THESIS_REWRITE_FILLED.md` and chapter markdown sources above.
