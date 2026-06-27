# Thesis Chapter Map (English IAM only)

Maps thesis sections to code artifacts for traceability.

## Abstract

| Content | Source |
|---------|--------|
| IAM CER/WER | `experiments/iam_trocr_handwritten/metrics.json` |
| Method | `docs/RESEARCH_SCOPE.md` |
| Application | `experiments/iam_demo/metrics.json` |

## Chapter 1 — Introduction

| Section | Alignment action |
|---------|------------------|
| Problem statement | English HTR on IAM |
| Objectives | Evaluate TrOCR; deploy English IAM demo |
| Remove | Bullinger, Latin/German, GPT-3, medical prescriptions |
| Scope | Match `docs/RESEARCH_SCOPE.md` |

## Chapter 2 — Literature Review

| Section | Source |
|---------|--------|
| TrOCR row in summary table | ViT encoder + BART decoder (not CRNN) |
| Literature CER anchors | AttentionHTR 6.50%, Light Transformer 5.70%, GFCN 7.99% |

## Chapter 3 — Methodology

| Section | Code reference |
|---------|----------------|
| Dataset | `scripts/prepare_iam_lines.py`, `data/iam/processed/split_stats.json` |
| Model loading | `src/htr/models.py` |
| Preprocessing | Hugging Face `TrOCRProcessor` |
| Metrics | `src/htr/metrics.py` |
| Evaluation | `src/htr/evaluate.py`, `scripts/run_eval.py` |
| Application | `app/gradio_app.py`, `scripts/prepare_iam_demo_examples.py` |

## Chapter 4 — Results

| Section | Artifact |
|---------|----------|
| 4.1 IAM quantitative | `experiments/iam_trocr_handwritten/` |
| 4.2 Tesseract baseline | `experiments/iam_tesseract/` |
| 4.3 Literature table | Cited values only (see `docs/THESIS_REWRITE.md`) |
| 4.4 IAM demo qualitative | `experiments/iam_demo/predictions.csv` |
| Figures | `experiments/figures/cer_comparison.png` |
| Application | `app/gradio_app.py` |

## Chapter 5 — Conclusion

Summarize IAM English findings, eval-only limitation, Gradio deployment, future work.

## Aligned thesis text

See `docs/THESIS_REWRITE_FILLED.md` for chapter-by-chapter replacement text.
