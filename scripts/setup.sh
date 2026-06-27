#!/usr/bin/env bash
# End-to-end setup: English IAM data, experiments, figures
set -euo pipefail
cd "$(dirname "$0")/.."

echo "==> IAM English data"
python3 scripts/download_iam.py
python3 scripts/prepare_iam_lines.py
python3 scripts/prepare_iam_demo_examples.py

echo "==> Experiments"
python3 scripts/run_all_experiments.py

echo "==> Figures"
python3 scripts/plot_results.py

echo "==> Thesis metrics"
python3 scripts/fill_thesis_metrics.py

echo "Done. See experiments/ and docs/THESIS_REWRITE_FILLED.md"
