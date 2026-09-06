#!/usr/bin/env python3
"""Fine-tune TrOCR from a YAML config (supports resume)."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from htr.train import TrainConfig, run_training


def load_config(path: Path, *, resume: bool | None = None) -> TrainConfig:
    with open(path, encoding="utf-8") as f:
        raw = yaml.safe_load(f)

    resume_flag = bool(raw.get("resume", True)) if resume is None else resume

    return TrainConfig(
        run_id=raw["run_id"],
        base_checkpoint=raw.get("base_checkpoint", "microsoft/trocr-base-handwritten"),
        train_dir=REPO_ROOT / raw["train_dir"],
        val_dir=REPO_ROOT / raw["val_dir"],
        output_model_dir=REPO_ROOT / raw.get("output_model_dir", "models/iam_trocr_finetuned"),
        output_dir=REPO_ROOT / raw.get("output_dir", "experiments"),
        learning_rate=float(raw.get("learning_rate", 5e-6)),
        batch_size=int(raw.get("batch_size", 8)),
        grad_accum=int(raw.get("grad_accum", 1)),
        epochs=int(raw.get("epochs", 8)),
        early_stop_patience=int(raw.get("early_stop_patience", 2)),
        max_target_length=int(raw.get("max_target_length", 128)),
        max_train_samples=raw.get("max_train_samples"),
        max_val_samples=raw.get("max_val_samples"),
        seed=int(raw.get("seed", 42)),
        log_every_steps=int(raw.get("log_every_steps", 50)),
        save_every_steps=int(raw.get("save_every_steps", 100)),
        resume=resume_flag,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Fine-tune TrOCR on IAM")
    parser.add_argument("--config", required=True, help="Path to YAML config")
    parser.add_argument(
        "--no-resume",
        action="store_true",
        help="Ignore existing checkpoints and start from base_checkpoint",
    )
    parser.add_argument(
        "--fresh",
        action="store_true",
        help="Delete checkpoint dir for this run_id, then start fresh",
    )
    args = parser.parse_args()

    config_path = Path(args.config)
    if not config_path.is_absolute():
        config_path = REPO_ROOT / config_path

    # Peek run_id for --fresh before full load
    with open(config_path, encoding="utf-8") as f:
        raw = yaml.safe_load(f)
    run_id = raw["run_id"]
    ckpt_dir = REPO_ROOT / raw.get("output_dir", "experiments") / run_id / "checkpoints"
    if args.fresh and ckpt_dir.exists():
        shutil.rmtree(ckpt_dir)
        print(f"Removed {ckpt_dir}", flush=True)

    resume = False if (args.no_resume or args.fresh) else None
    log = run_training(load_config(config_path, resume=resume))
    print(json.dumps({k: v for k, v in log.items() if k != "history"}, indent=2, default=str))


if __name__ == "__main__":
    main()
