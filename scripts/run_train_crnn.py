#!/usr/bin/env python3
"""Train CRNN+CTC baseline from a YAML config."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from htr.baselines.crnn import CRNNTrainConfig, run_crnn_training


def load_config(path: Path) -> CRNNTrainConfig:
    with open(path, encoding="utf-8") as f:
        raw = yaml.safe_load(f)

    return CRNNTrainConfig(
        run_id=raw["run_id"],
        train_dir=REPO_ROOT / raw["train_dir"],
        val_dir=REPO_ROOT / raw["val_dir"],
        output_model_dir=REPO_ROOT / raw.get("output_model_dir", "models/iam_crnn"),
        output_dir=REPO_ROOT / raw.get("output_dir", "experiments"),
        learning_rate=float(raw.get("learning_rate", 1e-3)),
        batch_size=int(raw.get("batch_size", 32)),
        epochs=int(raw.get("epochs", 20)),
        early_stop_patience=int(raw.get("early_stop_patience", 3)),
        img_height=int(raw.get("img_height", 32)),
        img_width=int(raw.get("img_width", 128)),
        max_train_samples=raw.get("max_train_samples"),
        max_val_samples=raw.get("max_val_samples"),
        seed=int(raw.get("seed", 42)),
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Train CRNN+CTC on IAM")
    parser.add_argument("--config", required=True, help="Path to YAML config")
    args = parser.parse_args()

    config_path = Path(args.config)
    if not config_path.is_absolute():
        config_path = REPO_ROOT / config_path

    log = run_crnn_training(load_config(config_path))
    print(json.dumps({k: v for k, v in log.items() if k != "history"}, indent=2, default=str))


if __name__ == "__main__":
    main()
