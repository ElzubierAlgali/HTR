# Appendix — Key Source Modules

Full listings are maintained in the repository. This appendix points to the modules that implement the Chapter 3 design and Chapter 4 experiments.

## A.1 Model loading — `src/htr/models.py`

Loads `TrOCRProcessor` + `VisionEncoderDecoderModel` from a Hub ID (e.g. `microsoft/trocr-base-handwritten`) or a local directory (`models/iam_trocr_finetuned/`). Exposes `ModelBundle.generate` / `generate_batch`.

## A.2 Dataset — `src/htr/dataset.py`

`LineDataset` reads `split_dir/images/` and `labels.csv` (`filename`, `transcription`). Shared by training and evaluation. `collect_charset` builds the CRNN vocabulary.

## A.3 Augmentation — `src/htr/augment.py`

Train-only torchvision transforms (mild affine + color jitter). Evaluation uses unaugmented RGB images.

## A.4 TrOCR fine-tune — `src/htr/train.py`

AdamW + cross-entropy fine-tuning with early stopping on validation CER. Saves model+processor to `models/iam_trocr_finetuned/` and writes `experiments/iam_trocr_finetuned/train_log.json`.

CLI: `python scripts/run_train.py --config configs/iam_trocr_finetune.yaml`

## A.5 Evaluation — `src/htr/evaluate.py`

Backends: `trocr` | `tesseract` | `crnn`. Writes `metrics.json`, `predictions.csv`, `error_summary.json`, `config.json` under `experiments/<run_id>/`.

CLI: `python scripts/run_eval.py --config configs/<name>.yaml`

## A.6 CRNN+CTC — `src/htr/baselines/crnn.py`

CNN + BiLSTM + CTC baseline. Checkpoint: `models/iam_crnn/{crnn.pt,meta.json}`.

CLI: `python scripts/run_train_crnn.py --config configs/iam_crnn.yaml`

## A.7 Metrics — `src/htr/metrics.py`

Case-sensitive whitespace normalization; corpus CER/WER via `jiwer`.

## A.8 Gradio application — `app/gradio_app.py`

Interactive recognition with optional ground-truth CER; IAM demo examples.

## A.9 Sample YAML configs

**Eval (pretrained, full test):** `configs/iam_trocr_handwritten.yaml`

```yaml
run_id: iam_trocr_handwritten
checkpoint: microsoft/trocr-base-handwritten
split_dir: data/iam/processed/test
output_dir: experiments
batch_size: 8
backend: trocr
seed: 42
```

**Fine-tune:** `configs/iam_trocr_finetune.yaml`

```yaml
run_id: iam_trocr_finetuned
base_checkpoint: microsoft/trocr-base-handwritten
train_dir: data/iam/processed/train
val_dir: data/iam/processed/val
output_model_dir: models/iam_trocr_finetuned
learning_rate: 5.0e-6
batch_size: 8
epochs: 8
early_stop_patience: 2
```

**CRNN:** `configs/iam_crnn.yaml` (train fields + `backend: crnn` for eval)

Smoke variants with tiny `max_samples` / `max_train_samples` live under `configs/smoke/`.
