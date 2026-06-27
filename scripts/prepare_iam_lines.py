#!/usr/bin/env python3
"""Export IAM line splits from Hugging Face parquet files to image folders."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = REPO_ROOT / "data" / "iam" / "raw"
PROCESSED_DIR = REPO_ROOT / "data" / "iam" / "processed"

HF_TO_LOCAL = {
    "train": "train",
    "validation": "val",
    "test": "test",
}


def export_split(hf_split: str, local_split: str, max_samples: int | None = None) -> int:
    from datasets import load_dataset

    parquet_path = RAW_DIR / f"iam_line_{hf_split}.parquet"
    if parquet_path.exists():
        dataset = load_dataset("parquet", data_files=str(parquet_path), split="train")
    else:
        dataset = load_dataset("Teklia/IAM-line", split=hf_split)

    if max_samples is not None:
        dataset = dataset.select(range(min(max_samples, len(dataset))))

    images_dir = PROCESSED_DIR / local_split / "images"
    images_dir.mkdir(parents=True, exist_ok=True)
    labels_path = PROCESSED_DIR / local_split / "labels.csv"

    rows: list[tuple[str, str]] = []
    for idx, sample in enumerate(dataset):
        image = sample["image"]
        text = str(sample["text"]).strip()
        if not text:
            continue
        filename = f"{local_split}_{idx:06d}.png"
        image_path = images_dir / filename
        image.convert("RGB").save(image_path)
        rows.append((filename, text))

    with open(labels_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["filename", "transcription"])
        writer.writerows(rows)

    print(f"{local_split}: exported {len(rows)} lines")
    return len(rows)


def prepare_splits(max_samples: int | None = None) -> dict:
    stats: dict[str, dict] = {}
    for hf_split, local_split in HF_TO_LOCAL.items():
        count = export_split(hf_split, local_split, max_samples)
        stats[local_split] = {"n_samples": count, "source_split": hf_split}

    stats_path = PROCESSED_DIR / "split_stats.json"
    stats_path.write_text(json.dumps(stats, indent=2), encoding="utf-8")
    return stats


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare IAM line splits")
    parser.add_argument("--max-samples", type=int, default=None)
    args = parser.parse_args()
    prepare_splits(args.max_samples)


if __name__ == "__main__":
    main()
