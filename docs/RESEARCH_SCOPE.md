# Research Scope (Source of Truth)

This document locks the research story for the thesis and codebase. Every claim in Chapter 4 must trace to an artifact under `experiments/<run_id>/`.

## Primary research question

How well do **transformer-based HTR models** (pretrained and fine-tuned TrOCR) perform on the **English IAM Handwriting Database** benchmark compared to a CRNN+CTC baseline, classical OCR (Tesseract), and published literature?

## Locked definitions

| Item | Value |
|------|--------|
| Language | **English only** |
| Primary dataset | IAM Handwriting Database, line-level, English |
| Primary model | `microsoft/trocr-base-handwritten` (+ fine-tuned checkpoint) |
| Architecture | Vision Transformer (ViT) image encoder + BART text decoder |
| Training in this work | **TrOCR fine-tune on IAM** + **CRNN+CTC baseline train** (GPU primary) |
| Loss (TrOCR) | Autoregressive cross-entropy — **not CTC** |
| Loss (CRNN) | CTC |
| Primary metrics | Character Error Rate (CER), Word Error Rate (WER) |
| Measured baselines | CRNN+CTC and Tesseract 5.x on the same full IAM test split |
| Literature baselines | Cited reported CER/WER only — no estimated numbers |
| Application | Gradio demo on IAM English sample lines |
| Primary eval sample | **n = 2,915** (full IAM test) for measured runs |

## Out of scope

- Non-English handwriting (Latin, German, historical Bullinger corpus)
- GPT-3 / BERT / XLNet as implemented models
- Medical prescription recognition
- Custom transformer architecture modifications
- CTC as the TrOCR training loss
- Binarization as an implementation step
- Precision / recall / F1 as primary metrics

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
| `iam_trocr_handwritten` | `microsoft/trocr-base-handwritten` | IAM test (full, n=2,915) | Pretrained primary |
| `iam_trocr_finetuned` | Local `models/iam_trocr_finetuned/` | IAM test (full, n=2,915) | Fine-tuned TrOCR |
| `iam_crnn` | CRNN+CTC | IAM test (full, n=2,915) | Neural baseline |
| `iam_tesseract` | Tesseract | IAM test (full, n=2,915) | Classical baseline |
| `iam_demo` | `microsoft/trocr-base-handwritten` | IAM demo (8 English lines) | Application qualitative |

Primary YAMLs omit `max_samples` (full test). Smoke configs under `configs/smoke/` keep tiny limits for CPU checks. Thesis numbers must come from GPU full runs (`n=2,915`).

## Traceability rule

Every numeric result in the thesis must reference:

```
experiments/<run_id>/metrics.json
```

Reproduce with:

```bash
python scripts/run_eval.py --config configs/<config>.yaml
python scripts/run_train.py --config configs/iam_trocr_finetune.yaml
python scripts/run_train_crnn.py --config configs/iam_crnn.yaml
```

## Chapter boundaries

- **Chapter 3 (Methodology):** research design only — no result numbers
- **Chapter 4 (Implementation and Results):** contribution, brief implementation, experiments, results, analysis
- **Appendices:** full source code listings
