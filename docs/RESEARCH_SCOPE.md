# Research Scope (Source of Truth)

This document locks the research story for the thesis and codebase. Every claim in Chapter 4 must trace to an artifact under `experiments/<run_id>/`.

## Primary research question

How well do **pretrained transformer-based HTR models** (TrOCR) perform on the **English IAM Handwriting Database** benchmark compared to a classical OCR baseline and published literature?

## Locked definitions

| Item | Value |
|------|--------|
| Language | **English only** |
| Primary dataset | IAM Handwriting Database, line-level, English |
| Primary model | `microsoft/trocr-base-handwritten` |
| Architecture | Vision Transformer (ViT) image encoder + BART text decoder |
| Training in this work | **Evaluation-only** — no new fine-tuning |
| Loss (TrOCR original training) | Autoregressive cross-entropy — **not CTC** |
| Primary metrics | Character Error Rate (CER), Word Error Rate (WER) |
| Measured baseline | Tesseract 5.x on the same IAM test split |
| Literature baselines | Cited reported CER/WER only — no estimated numbers |
| Application | Gradio demo on IAM English sample lines |

## Out of scope

- Non-English handwriting (Latin, German, historical Bullinger corpus)
- GPT-3 / BERT / XLNet as implemented models
- Medical prescription recognition
- Custom transformer architecture modifications
- IAM fine-tuning (future work)

## Metric normalization

- **Case-sensitive** CER and WER (match common HTR literature)
- Strip leading/trailing whitespace on predictions and references
- Do not lowercase transcriptions
- Per-line CER via Levenshtein at character level; corpus CER = total edits / total reference characters

## IAM data source

- **Primary:** Hugging Face `Teklia/IAM-line` (official train / validation / test splits)
- **Columns:** `image`, `text`
- Processed exports: `data/iam/processed/{train,val,test}/`
- Demo samples: `data/iam/demo/` (English test subset for Gradio)
- Test set size: 2,915 line images (full benchmark split)

## IAM splits

Uses the dataset publisher splits directly:

- **Train:** 6,482 lines
- **Validation:** 976 lines
- **Test:** 2,915 lines

## Experiment runs

| Run ID | Model | Dataset | Role |
|--------|-------|---------|------|
| `iam_trocr_handwritten` | `microsoft/trocr-base-handwritten` | IAM test (200 lines default) | Primary result |
| `iam_demo` | `microsoft/trocr-base-handwritten` | IAM demo (8 English lines) | Application qualitative |
| `iam_tesseract` | Tesseract | IAM test | Measured classical baseline |

The default `max_samples` (200) keeps CPU-only evaluation tractable. Remove `max_samples` from the YAML configs to evaluate the full IAM test split (2,915 lines) on a GPU machine.

## Traceability rule

Every numeric result in the thesis must reference:

```
experiments/<run_id>/metrics.json
```

Reproduce with:

```bash
python scripts/run_eval.py --config configs/<config>.yaml
```
