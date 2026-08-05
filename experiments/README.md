# Experiment artifacts

Primary thesis numbers must come from the **GPU full protocol** (`docs/GPU_PROTOCOL.md`) with `"n_samples": 2915` for E1–E4.

If current `metrics.json` files show small `n_samples` (e.g. 4–16) or CER near 1.0 from a tiny random checkpoint, they are **CPU smoke only** and must be replaced before final thesis figures/tables.

Required after GPU runs:

| Path | Purpose |
|------|---------|
| `iam_trocr_handwritten/metrics.json` | E1 pretrained |
| `iam_trocr_finetuned/metrics.json` + `train_log.json` | E2 fine-tuned |
| `iam_crnn/metrics.json` + `train_log.json` | E3 CRNN |
| `iam_tesseract/metrics.json` | E4 (or skipped) |
| `iam_demo/metrics.json` | E5 |
| `figures/cer_comparison.png` | Chapter 4 figure |
| `figures/error_examples.md` | Qualitative analysis |
