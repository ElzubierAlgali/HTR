#!/usr/bin/env python3
"""Run all planned HTR evaluation experiments (English IAM only)."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
CONFIGS = [
    "configs/iam_trocr_handwritten.yaml",
    "configs/iam_trocr_finetuned.yaml",
    "configs/iam_crnn.yaml",
    "configs/iam_tesseract.yaml",
    "configs/iam_demo.yaml",
]


def main() -> int:
    run_eval = REPO_ROOT / "scripts" / "run_eval.py"
    results = {}

    for config in CONFIGS:
        run_id = Path(config).stem
        metrics_path = REPO_ROOT / "experiments" / run_id / "metrics.json"
        if metrics_path.exists():
            data = json.loads(metrics_path.read_text(encoding="utf-8-sig"))
            # Re-run if cached metrics are smoke-sized while using primary configs
            n = data.get("n_samples")
            is_primary_full = run_id != "iam_demo" and data.get("status") != "skipped"
            if data.get("status") == "skipped" and run_id == "iam_tesseract":
                print(f"\n=== Skipping {config} (tesseract skipped) ===", flush=True)
                results[config] = "skipped"
                continue
            if is_primary_full and n is not None and int(n) >= 2915:
                print(f"\n=== Skipping {config} (full metrics exist, n={n}) ===", flush=True)
                results[config] = "ok (cached)"
                continue
            if run_id == "iam_demo" and data.get("status") != "skipped":
                print(f"\n=== Skipping {config} (metrics exist) ===", flush=True)
                results[config] = "ok (cached)"
                continue

        print(f"\n=== Running {config} ===", flush=True)
        try:
            proc = subprocess.run(
                [sys.executable, str(run_eval), "--config", config],
                cwd=REPO_ROOT,
                check=True,
                capture_output=True,
                text=True,
            )
            print(proc.stdout)
            results[config] = "ok"
        except subprocess.CalledProcessError as exc:
            print(exc.stderr or exc.stdout, file=sys.stderr)
            results[config] = f"failed: {exc.stderr or exc.stdout}"

    summary_path = REPO_ROOT / "experiments" / "run_summary.json"
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(json.dumps(results, indent=2))
    failed = [k for k, v in results.items() if v.startswith("failed")]
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
