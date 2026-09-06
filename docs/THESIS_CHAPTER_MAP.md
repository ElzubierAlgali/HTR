# Thesis Chapter Map (English IAM only)

Maps thesis sections to code artifacts for traceability.

## Abstract

| Content | Source |
|---------|--------|
| IAM CER/WER (pretrained) | `experiments/iam_trocr_handwritten/metrics.json` |
| Fine-tuned CER/WER | `experiments/iam_trocr_finetuned/metrics.json` |
| Method | `docs/RESEARCH_SCOPE.md` |
| Application | `experiments/iam_demo/metrics.json` |

## Chapter 1 — Introduction

| Section | Alignment action |
|---------|------------------|
| Problem statement | English HTR on IAM |
| Objectives | Evaluate + fine-tune TrOCR; CRNN/Tesseract baselines; Gradio demo |
| Remove | Bullinger, Latin/German, GPT-3, medical prescriptions |
| Scope | Match `docs/RESEARCH_SCOPE.md` |

## Chapter 2 — Literature Review

| Section | Source |
|---------|--------|
| TrOCR row in summary table | ViT encoder + BART decoder |
| Literature CER anchors | AttentionHTR 6.50%, Light Transformer 5.70%, GFCN 7.99% |

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
