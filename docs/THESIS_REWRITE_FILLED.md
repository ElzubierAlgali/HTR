# Thesis Rewrite Guide (English IAM only)

Aligned text for `Enhancing Handwritten Text Recognition Using Transformer Models Derived from Large Language Models.docx`.

**Rule:** Replace placeholder `[pending:run_id.field]` with values from `experiments/<run_id>/metrics.json` after running evaluations.

---

## Abstract (replace empty abstract)

Handwritten text recognition (HTR) remains challenging due to variability in writing styles. This thesis evaluates **pretrained TrOCR** transformer models—combining a **Vision Transformer (ViT) encoder** with a **BART text decoder**—on the **English IAM Handwriting Database** benchmark. We implement a reproducible evaluation pipeline measuring Character Error Rate (CER) and Word Error Rate (WER), compare against a classical Tesseract baseline where available, and contextualize results against published HTR literature. A Gradio web application demonstrates English line transcription on IAM sample images. Primary IAM results: CER **5.08%** (n=200). This work contributes an aligned research-and-application pipeline rather than a novel architecture.

---

## Chapter 1 — Key replacements

### Remove entirely
- References to GPT-3, BERT, GPT-2, XLNet as implemented models
- Bullinger, Latin, German, historical documents
- Medical prescription as primary objective
- Custom attention / positional encoding objectives
- CTC as **your** training loss
- Results/conclusions in methodology sections

### Replace problem statement (concise)

> This research addresses **English** handwritten text recognition for line images using transformer-based models, evaluated on the IAM Handwriting Database benchmark.

### Replace objectives

1. Review HTR methods with emphasis on transformer architectures (TrOCR).
2. Implement a reproducible IAM evaluation pipeline (CER/WER).
3. Evaluate pretrained `microsoft/trocr-base-handwritten` on IAM English test data.
4. Compare against Tesseract and published IAM literature baselines.
5. Deploy a web application for English IAM line transcription.

### Replace scope

> English line-level HTR on IAM (6,482 train / 976 validation / 2,915 test lines from Teklia/IAM-line). Evaluation-only: no new model training.

---

## Chapter 2 — Literature table fix (TrOCR row)

| Tools & Techniques |
|--------------------|
| ViT image encoder + BART text decoder; pretrained vision and language components |

---

## Chapter 3 — Methodology (mirror code)

### 3.1 Dataset
- IAM via `Teklia/IAM-line` (see `scripts/download_iam.py`, `scripts/prepare_iam_lines.py`)
- Demo examples: `data/iam/demo/` (English test subset)

### 3.2 Model
- `VisionEncoderDecoderModel` from Hugging Face Transformers
- `microsoft/trocr-base-handwritten` (English IAM pretrained)

### 3.3 Preprocessing
- RGB line images via `TrOCRProcessor`
- No custom binarization in this implementation

### 3.4 Training
- **Not performed in this thesis** — pretrained checkpoints only
- TrOCR original training uses autoregressive cross-entropy (Li et al., 2021)

### 3.5 Metrics
- CER, WER via `jiwer` (case-sensitive, whitespace-normalized)
- See `src/htr/metrics.py`

### 3.6 Baselines
- Measured: Tesseract on IAM test (`experiments/iam_tesseract/`)
- Literature only (not re-implemented): AttentionHTR 6.50% CER, Light Transformer 5.70%, GFCN 7.99%

---

## Chapter 4 — Results (populate from experiments)

### 4.1 IAM primary result (`iam_trocr_handwritten`)

| Metric | Value |
|--------|-------|
| CER | 5.08% |
| WER | 12.92% |
| n | 200 |

Artifact: `experiments/iam_trocr_handwritten/predictions.csv`

### 4.2 Tesseract baseline (`iam_tesseract`)

See `experiments/iam_tesseract/metrics.json` (or skipped status if Tesseract not installed).

### 4.3 Literature comparison (cited, not estimated)

| Method | CER (IAM) | Source |
|--------|-----------|--------|
| TrOCR (this work) | 5.08% | experiments/ |
| AttentionHTR | 6.50% | Kass & Vats, 2022 |
| Light Transformer | 5.70% | Barrère et al., 2022 |
| GFCN | 7.99% | Coquenet et al., 2020 |

### 4.4 IAM demo qualitative (`iam_demo`)

| Metric | Value |
|--------|-------|
| CER | 5.05% |
| WER | 14.97% |
| n | 8 |

See `experiments/iam_demo/predictions.csv`

### 4.5 Figure

`experiments/figures/cer_comparison.png` (from `scripts/plot_results.py`)

### 4.6 Application

Gradio app: `app/gradio_app.py` (English IAM sample lines)

---

## Chapter 5 — Conclusion

- Summarize IAM English CER/WER findings
- Note eval-only scope (no fine-tuning)
- Gradio demo as deployment contribution
- Future work: IAM fine-tuning, full 2,915-line test eval, CRNN baselines, Tesseract install

---

## Title suggestion (optional)

*Enhancing Handwritten Text Recognition Using Pretrained Transformer Models: An English IAM Benchmark and Web Application*
