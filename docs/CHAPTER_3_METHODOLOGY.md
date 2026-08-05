# Chapter 3 — Methodology

Design-only chapter. No measured CER/WER result numbers appear here. Implementation outcomes are reported in Chapter 4 and must trace to `experiments/<run_id>/metrics.json`.

## 3.1 Introduction

Handwritten text recognition (HTR) is difficult because writing styles, spacing, and stroke quality vary widely across writers. This chapter specifies the research design for English line-level HTR on the IAM Handwriting Database using transfer learning from a pretrained TrOCR transformer, with neural (CRNN+CTC) and classical (Tesseract) baselines. The chapter covers dataset choice, preprocessing, models, metrics, and the experiment matrix. Results and analysis are deferred to Chapter 4.

## 3.2 Dataset

Data are obtained from Hugging Face `Teklia/IAM-line` (official publisher splits) and prepared by `scripts/download_iam.py` and `scripts/prepare_iam_lines.py`. Processed exports live under `data/iam/processed/{train,val,test}/` with `images/` and `labels.csv` (`filename`, `transcription`). Demo samples for the Gradio application are stored in `data/iam/demo/`.

**Table 3.1 — IAM line dataset (Teklia/IAM-line)**

| Property | Value |
|----------|--------|
| Language | English |
| Unit | Line images |
| Train / Val / Test | 6,482 / 976 / 2,915 |
| Modalities | PNG line image + transcription text |
| Source | Hugging Face `Teklia/IAM-line` |

**Figure 3.1 — Example IAM line.** Representative English line image from `data/iam/demo/` (rendered in the chapter DOCX rebuild).

## 3.3 Preprocessing

Line images are converted to RGB and passed through Hugging Face `TrOCRProcessor` (image processor + tokenizer). This implementation does not apply custom binarization. Mild geometric and brightness augmentation (`src/htr/augment.py`) is applied **during fine-tuning only**; evaluation uses unaugmented images.

## 3.4 Model selection

### TrOCR (primary)

TrOCR combines a Vision Transformer (ViT) image encoder with a BART text decoder (`VisionEncoderDecoderModel`). The starting checkpoint is `microsoft/trocr-base-handwritten`, which is already pretrained for English handwritten lines. Fine-tuning on IAM train/val uses autoregressive cross-entropy (not CTC), AdamW, and early stopping on validation CER.

**Figure 3.2 — TrOCR architecture (conceptual).** Image patches → ViT encoder → cross-attention BART decoder → character/token sequence.

### CRNN+CTC (neural baseline)

A convolutional recurrent network with Connectionist Temporal Classification (CTC) is trained on the same IAM splits. CTC is used **only** for this baseline, not for TrOCR.

### Tesseract (classical baseline)

Tesseract OCR is run on the same test lines (line mode / PSM 7) as a classical reference.

## 3.5 Experiment design and metrics

Designed primary protocol (GPU):

| ID | Run | Role | Eval sample |
|----|-----|------|-------------|
| E1 | `iam_trocr_handwritten` | Pretrained TrOCR | Full test (n=2,915) |
| E2 | `iam_trocr_finetuned` | Fine-tuned TrOCR | Full test (n=2,915) |
| E3 | `iam_crnn` | CRNN+CTC | Full test (n=2,915) |
| E4 | `iam_tesseract` | Tesseract | Full test (n=2,915) |
| E5 | `iam_demo` | Application demo | 8 lines |

**Metrics.** Character Error Rate (CER) and Word Error Rate (WER) via `jiwer`, after case-sensitive whitespace normalization (`src/htr/metrics.py`). Corpus CER is total character edits divided by total reference characters. Transcriptions are not lowercased.

Smoke configs under `configs/smoke/` may use tiny `max_samples` / `max_train_samples` for engineering checks. Thesis numbers must come from the full GPU protocol.

## 3.6 Baselines (design summary)

Comparisons planned for Chapter 4:

1. Pretrained TrOCR vs fine-tuned TrOCR on the same full test set  
2. TrOCR vs CRNN+CTC vs Tesseract (measured)  
3. Literature CER values (AttentionHTR, Light Transformer, GFCN) cited separately — different papers/setups; not re-implemented

## 3.7 Chapter boundary

This chapter contains no numeric experimental outcomes. Chapter 4 reports measured results, hyperparameters actually used, and qualitative error analysis.
