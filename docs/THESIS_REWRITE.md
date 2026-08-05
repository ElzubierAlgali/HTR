# Thesis Rewrite Guide (English IAM only)

Aligned text for `Enhancing Handwritten Text Recognition Using Transformer Models Derived from Large Language Models.docx`.

**Rule:** Replace `METRIC` placeholders (`run_id.field`) with values from `experiments/<run_id>/metrics.json` after running evaluations.

---

## Abstract (replace empty abstract)

Handwritten text recognition (HTR) remains challenging due to variability in writing styles. This thesis evaluates **pretrained and fine-tuned TrOCR** models—combining a **Vision Transformer (ViT) encoder** with a **BART text decoder**—on the **English IAM Handwriting Database** benchmark (full test, n=2,915). We implement a reproducible pipeline measuring Character Error Rate (CER) and Word Error Rate (WER), fine-tune TrOCR on IAM, train a CRNN+CTC baseline, compare against Tesseract where available, and contextualize results against published HTR literature. A Gradio web application demonstrates English line transcription. Primary pretrained IAM results: CER **{{METRIC:iam_trocr_handwritten.cer}}** (n={{METRIC:iam_trocr_handwritten.n_samples}}); fine-tuned: CER **{{METRIC:iam_trocr_finetuned.cer}}**. This work contributes an aligned research-and-application pipeline rather than a novel architecture.

---

## Chapter 1 — Key replacements

### Remove entirely
- References to GPT-3, BERT, GPT-2, XLNet as implemented models
- Bullinger, Latin, German, historical documents
- Medical prescription as primary objective
- Custom attention / positional encoding objectives
- CTC as **TrOCR** training loss (CTC is used only for CRNN)
- Results/conclusions in methodology sections

### Replace problem statement (concise)

> This research addresses **English** handwritten text recognition for line images using transformer-based models, evaluated on the IAM Handwriting Database benchmark.

### Replace objectives

1. Review HTR methods with emphasis on transformer architectures (TrOCR).
2. Implement a reproducible IAM train/eval pipeline (CER/WER).
3. Evaluate pretrained and fine-tuned `microsoft/trocr-base-handwritten` on full IAM English test data (n=2,915).
4. Compare against CRNN+CTC, Tesseract, and published IAM literature baselines.
5. Deploy a web application for English IAM line transcription.

### Replace scope

> English line-level HTR on IAM (6,482 train / 976 validation / 2,915 test lines from Teklia/IAM-line). Includes TrOCR fine-tuning and CRNN+CTC baseline training; primary measured results use the full test split.

---

## Chapter 2 — Literature table fix (TrOCR row)

| Tools & Techniques |
|--------------------|
| ViT image encoder + BART text decoder; pretrained vision and language components |

---

## Chapter 3 — Methodology (design only)

See `docs/CHAPTER_3_METHODOLOGY.md`. No result numbers.

### 3.1 Dataset
- IAM via `Teklia/IAM-line` (see `scripts/download_iam.py`, `scripts/prepare_iam_lines.py`)
- Demo examples: `data/iam/demo/` (English test subset)

### 3.2 Model
- `VisionEncoderDecoderModel` (TrOCR ViT+BART)
- CRNN+CTC baseline for comparison

### 3.3 Preprocessing
- RGB line images via `TrOCRProcessor`
- No custom binarization; augmentation during fine-tune only

### 3.4 Training
- TrOCR fine-tune: AdamW, cross-entropy, early stop on val CER
- CRNN: CTC loss on full train/val

### 3.5 Metrics
- CER, WER via `jiwer` (case-sensitive, whitespace-normalized)

### 3.6 Baselines (design)
- Pretrained TrOCR, fine-tuned TrOCR, CRNN+CTC, Tesseract
- Literature comparison deferred to Chapter 4

---

## Chapter 4 — Implementation and Results

See `docs/CHAPTER_4_IMPLEMENTATION_RESULTS.md`.

### Measured runs (populate from experiments)

| Run | CER | WER | n |
|-----|-----|-----|---|
| Pretrained TrOCR | {{METRIC:iam_trocr_handwritten.cer}} | {{METRIC:iam_trocr_handwritten.wer}} | {{METRIC:iam_trocr_handwritten.n_samples}} |
| Fine-tuned TrOCR | {{METRIC:iam_trocr_finetuned.cer}} | {{METRIC:iam_trocr_finetuned.wer}} | {{METRIC:iam_trocr_finetuned.n_samples}} |
| CRNN+CTC | {{METRIC:iam_crnn.cer}} | {{METRIC:iam_crnn.wer}} | {{METRIC:iam_crnn.n_samples}} |
| Tesseract | {{METRIC:iam_tesseract.cer}} | {{METRIC:iam_tesseract.wer}} | {{METRIC:iam_tesseract.n_samples}} |
| Demo | {{METRIC:iam_demo.cer}} | {{METRIC:iam_demo.wer}} | {{METRIC:iam_demo.n_samples}} |

### Literature comparison (cited, not estimated)

| Method | CER (IAM) | Source |
|--------|-----------|--------|
| TrOCR pretrained (this work) | {{METRIC:iam_trocr_handwritten.cer}} | experiments/ |
| TrOCR fine-tuned (this work) | {{METRIC:iam_trocr_finetuned.cer}} | experiments/ |
| AttentionHTR | 6.50% | Kass & Vats, 2022 |
| Light Transformer | 5.70% | Barrère et al., 2022 |
| GFCN | 7.99% | Coquenet et al., 2020 |

Figure: `experiments/figures/cer_comparison.png`

---

## Chapter 5 — Conclusion

- Summarize full-test IAM English CER/WER findings (pretrained vs fine-tuned vs CRNN vs Tesseract)
- Note GPU full-protocol scope and any honesty caveats (Hub checkpoint already IAM-pretrained)
- Gradio demo as deployment contribution
- Future work: longer fine-tunes, page-level HTR, additional neural baselines

---

## Title suggestion (optional)

*Enhancing Handwritten Text Recognition Using Pretrained Transformer Models: An English IAM Benchmark and Web Application*
