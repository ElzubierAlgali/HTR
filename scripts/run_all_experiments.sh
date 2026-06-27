#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
python3 scripts/prepare_iam_demo_examples.py
python3 scripts/run_all_experiments.py
python3 scripts/plot_results.py
