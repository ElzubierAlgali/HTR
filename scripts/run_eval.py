#!/usr/bin/env python3
"""Run HTR evaluation from a YAML config."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from htr.evaluate import EvalConfig, run_evaluation


def load_config(path: Path) -> EvalConfig:
    with open(path, encoding="utf-8") as f:
        raw = yaml.safe_load(f)

    split_dir = REPO_ROOT / raw["split_dir"]
    output_dir = REPO_ROOT / raw.get("output_dir", "experiments")

    return EvalConfig(
        run_id=raw["run_id"],
        checkpoint=raw.get("checkpoint", ""),
        split_dir=split_dir,
        output_dir=output_dir,
        batch_size=int(raw.get("batch_size", 8)),
        max_samples=raw.get("max_samples"),
        backend=raw.get("backend", "trocr"),
        seed=int(raw.get("seed", 42)),
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Run HTR evaluation")
    parser.add_argument("--config", required=True, help="Path to YAML config")
    args = parser.parse_args()

    config_path = Path(args.config)
    if not config_path.is_absolute():
        config_path = REPO_ROOT / config_path

    config = load_config(config_path)
    metrics = run_evaluation(config)
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
