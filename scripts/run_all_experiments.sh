#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
python3 scripts/prepare_iam_demo_examples.py
python3 scripts/run_all_experiments.py
python3 scripts/plot_results.py
python3 scripts/extract_error_examples.py
python3 scripts/fill_thesis_metrics.py
# For full train+eval on GPU, use: bash scripts/run_gpu_protocol.sh
