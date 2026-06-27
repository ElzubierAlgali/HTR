#!/usr/bin/env python3
"""Copy IAM English test samples for the Gradio demo."""

from __future__ import annotations

import csv
import shutil
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE = REPO_ROOT / "data" / "iam" / "processed" / "test"
TARGET = REPO_ROOT / "data" / "iam" / "demo"
NUM_SAMPLES = 8


def prepare_demo_examples(num_samples: int = NUM_SAMPLES) -> int:
    images_src = SOURCE / "images"
    labels_src = SOURCE / "labels.csv"
    if not labels_src.exists():
        raise FileNotFoundError(
            f"Missing {labels_src}. Run: python3 scripts/prepare_iam_lines.py"
        )

    images_dst = TARGET / "images"
    images_dst.mkdir(parents=True, exist_ok=True)

    rows: list[tuple[str, str]] = []
    with open(labels_src, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            filename = row["filename"]
            text = row["transcription"].strip()
            src = images_src / filename
            if not src.exists() or not text:
                continue
            shutil.copy2(src, images_dst / filename)
            rows.append((filename, text))
            if len(rows) >= num_samples:
                break

    labels_dst = TARGET / "labels.csv"
    with open(labels_dst, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["filename", "transcription"])
        writer.writerows(rows)

    print(f"Prepared {len(rows)} IAM English demo examples at {TARGET}")
    return len(rows)


if __name__ == "__main__":
    prepare_demo_examples()
