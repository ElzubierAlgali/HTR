# iam_trocr_finetuned

Fine-tuned weights are **not** stored in git (see `.gitignore`). After training they live under `models/iam_trocr_finetuned/`, produced by:

```bash
python scripts/run_train.py --config configs/iam_trocr_finetune.yaml
```

Evaluate (requires the local checkpoint above):

```bash
python scripts/run_eval.py --config configs/iam_trocr_finetuned.yaml
```

This directory keeps metrics, logs, and predictions only.
