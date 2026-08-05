#!/usr/bin/env bash
# Full GPU protocol: train TrOCR + CRNN, then evaluate E1–E5.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "=== TrOCR fine-tune (full) ==="
python scripts/run_train.py --config configs/iam_trocr_finetune.yaml

echo "=== CRNN train (full) ==="
python scripts/run_train_crnn.py --config configs/iam_crnn.yaml

echo "=== Evaluations E1–E5 ==="
python scripts/run_all_experiments.py

echo "=== Figures + error examples + thesis fill ==="
python scripts/plot_results.py
python scripts/extract_error_examples.py
python scripts/fill_thesis_metrics.py

echo "Done. Copy experiments/ and models/ back if this ran on a remote GPU host."
