#!/usr/bin/env python3
"""Download IAM line-level dataset from Hugging Face."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = REPO_ROOT / "data" / "iam" / "raw"
META_PATH = RAW_DIR / "download_meta.json"
HF_DATASET = "Teklia/IAM-line"


def download_hf_iam() -> dict:
    from datasets import load_dataset

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Loading {HF_DATASET} from Hugging Face...")
    dataset = load_dataset(HF_DATASET)

    paths = {}
    for split_name in dataset:
        hf_split = dataset[split_name]
        split_key = str(split_name)
        out_path = RAW_DIR / f"iam_line_{split_key}.parquet"
        hf_split.to_parquet(out_path)
        paths[split_key] = str(out_path)
        print(f"  {split_key}: {len(hf_split)} samples -> {out_path}")

    meta = {
        "source": f"huggingface:{HF_DATASET}",
        "splits": {k: {"path": v, "n_samples": len(dataset[k])} for k, v in paths.items()},
        "columns": dataset["train"].column_names,
    }
    META_PATH.write_text(json.dumps(meta, indent=2), encoding="utf-8")
    return meta


def main() -> None:
    parser = argparse.ArgumentParser(description="Download IAM line dataset")
    parser.parse_args()
    meta = download_hf_iam()
    print(json.dumps(meta["splits"], indent=2))


if __name__ == "__main__":
    main()
