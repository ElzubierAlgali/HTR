#!/usr/bin/env python3
"""Create tiny synthetic IAM-shaped splits for CPU smoke tests."""

from __future__ import annotations

import csv
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

REPO_ROOT = Path(__file__).resolve().parents[1]
ROOT = REPO_ROOT / "data" / "iam" / "processed"
TEXTS = [
    "The quick brown fox",
    "jumps over the lazy dog",
    "Handwritten text recognition",
    "IAM English line sample",
    "Transformer models for HTR",
    "Character error rate metric",
    "Vision encoder text decoder",
    "Sudan University research",
]


def _write_split(name: str, texts: list[str]) -> None:
    split = ROOT / name
    images = split / "images"
    images.mkdir(parents=True, exist_ok=True)
    rows = []
    for i, text in enumerate(texts):
        filename = f"{name}_{i:03d}.png"
        img = Image.new("RGB", (512, 64), color=(255, 255, 255))
        draw = ImageDraw.Draw(img)
        try:
            font = ImageFont.load_default()
        except Exception:
            font = None
        draw.text((10, 20), text, fill=(0, 0, 0), font=font)
        img.save(images / filename)
        rows.append({"filename": filename, "transcription": text})
    with open(split / "labels.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["filename", "transcription"])
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {split} ({len(rows)} lines)")


def main() -> None:
    _write_split("train", TEXTS)
    _write_split("val", TEXTS[:4])
    _write_split("test", TEXTS[:6])
    demo = REPO_ROOT / "data" / "iam" / "demo"
    demo_images = demo / "images"
    demo_images.mkdir(parents=True, exist_ok=True)
    rows = []
    for i, text in enumerate(TEXTS[:4]):
        filename = f"demo_{i:03d}.png"
        src = ROOT / "train" / "images" / f"train_{i:03d}.png"
        Image.open(src).save(demo_images / filename)
        rows.append({"filename": filename, "transcription": text})
    with open(demo / "labels.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["filename", "transcription"])
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {demo} ({len(rows)} lines)")


if __name__ == "__main__":
    main()
