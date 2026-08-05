# Chapter 4 — Implementation and Results

Every numeric claim below must match `experiments/<run_id>/metrics.json` after GPU full runs. Placeholders use `{{METRIC:run_id.field}}` until filled by `scripts/fill_thesis_metrics.py`.

## 4.1 Research Contribution

This chapter contributes:

1. A reproducible English IAM train/eval pipeline (configs, scripts, logged artifacts).
2. TrOCR fine-tuning on IAM with train-only augmentation and logged hyperparameters (`train_log.json`).
3. Measured CRNN+CTC and Tesseract baselines on the **same full test split** (n=2,915).
4. A Gradio demo for interactive English line transcription.
5. Comparative analysis against cited literature CER values at matched test-set scale (without claiming identical preprocess/splits).

## 4.2 Implementation overview

| Component | Role | Location |
|-----------|------|----------|
| Dataset I/O | Line images + labels | `src/htr/dataset.py` |
| TrOCR load/generate | Hub or local checkpoint | `src/htr/models.py` |
| TrOCR fine-tune | CE / AdamW / early stop | `src/htr/train.py` |
| CRNN+CTC | Neural baseline | `src/htr/baselines/crnn.py` |
| Metrics | CER/WER | `src/htr/metrics.py` |
| Evaluation | E1–E5 runners | `src/htr/evaluate.py`, `scripts/run_eval.py` |
| Demo UI | Interactive recognition | `app/gradio_app.py` |

Dataset preparation and split sizes are defined in Chapter 3. Processed paths: `data/iam/processed/{train,val,test}/`.

## 4.3 Experiments

### Fine-tune hyperparameters (actual)

Logged in `experiments/iam_trocr_finetuned/train_log.json` after training:

| Field | Source |
|-------|--------|
| learning rate | `train_log.json` → `lr` |
| batch size | `batch_size` |
| epochs run | `epochs_ran` |
| best val CER | `best_val_cer` |
| device | `device` |
| wall clock | `wall_clock_sec` |

Designed defaults: AdamW, lr ≈ 5e-6, epochs 5–8 with early stopping on val CER, batch 8–16 (VRAM-dependent).

### Evaluation matrix

| Run | Config | Backend |
|-----|--------|---------|
| E1 Pretrained TrOCR | `configs/iam_trocr_handwritten.yaml` | trocr |
| E2 Fine-tuned TrOCR | `configs/iam_trocr_finetuned.yaml` | trocr (local) |
| E3 CRNN+CTC | `configs/iam_crnn.yaml` | crnn |
| E4 Tesseract | `configs/iam_tesseract.yaml` | tesseract |
| E5 Demo | `configs/iam_demo.yaml` | trocr |

## 4.4 Results

**Table 4.1 — Measured results (full IAM test unless noted)**

| Method | CER | WER | n |
|--------|-----|-----|---|
| TrOCR pretrained | {{METRIC:iam_trocr_handwritten.cer}} | {{METRIC:iam_trocr_handwritten.wer}} | {{METRIC:iam_trocr_handwritten.n_samples}} |
| TrOCR fine-tuned | {{METRIC:iam_trocr_finetuned.cer}} | {{METRIC:iam_trocr_finetuned.wer}} | {{METRIC:iam_trocr_finetuned.n_samples}} |
| CRNN+CTC | {{METRIC:iam_crnn.cer}} | {{METRIC:iam_crnn.wer}} | {{METRIC:iam_crnn.n_samples}} |
| Tesseract | {{METRIC:iam_tesseract.cer}} | {{METRIC:iam_tesseract.wer}} | {{METRIC:iam_tesseract.n_samples}} |
| Demo (qualitative) | {{METRIC:iam_demo.cer}} | {{METRIC:iam_demo.wer}} | {{METRIC:iam_demo.n_samples}} |

**Figure 4.1 — CER comparison.** `experiments/figures/cer_comparison.png` (measured bars vs literature bars marked distinct).

**Table 4.2 — Literature CER (cited; protocol may differ)**

| Method | CER (IAM) | Source |
|--------|-----------|--------|
| AttentionHTR | 6.50% | Kass & Vats, 2022 |
| Light Transformer | 5.70% | Barrère et al., 2022 |
| GFCN | 7.99% | Coquenet et al., 2020 |

## 4.5 Analysis

- **Fine-tune vs pretrained.** The Hub checkpoint is already IAM-oriented; fine-tuning may yield small CER change. Report measured values honestly from `metrics.json`.
- **TrOCR vs CRNN vs Tesseract.** Compare under the same test split and metric normalization.
- **Error examples.** See `experiments/figures/error_examples.md` (high-CER lines from `predictions.csv`).
- **Limitations.** English line-level only; literature papers may use different splits/preprocess; compute environment affects wall-clock; do not claim SOTA without a matched protocol.
- **Tesseract.** If the binary is missing, `metrics.json` records `status: skipped` and is disclosed in the thesis.

## 4.6 Application

The Gradio application (`app/gradio_app.py`) demonstrates English IAM line transcription with optional ground-truth CER. Demo metrics: `experiments/iam_demo/`.

## 4.7 Traceability

Reproduce:

```bash
bash scripts/run_gpu_protocol.sh
# or stepwise train/eval as in README.md
```

All body numbers must resolve to experiment artifacts under `experiments/`.
