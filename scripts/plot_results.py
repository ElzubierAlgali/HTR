#!/usr/bin/env python3
"""Generate thesis figures from experiment metrics."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt

REPO_ROOT = Path(__file__).resolve().parents[1]
EXPERIMENTS = REPO_ROOT / "experiments"
FIGURES = EXPERIMENTS / "figures"
FIGURES.mkdir(parents=True, exist_ok=True)

RUNS = [
    ("iam_trocr_handwritten", "TrOCR (IAM pretrained)"),
    ("iam_demo", "TrOCR (IAM demo subset)"),
    ("iam_tesseract", "Tesseract"),
]

LITERATURE = [
    ("AttentionHTR", 0.065),
    ("Light Transformer", 0.057),
    ("GFCN", 0.0799),
]


def load_cer(run_id: str) -> float | None:
    path = EXPERIMENTS / run_id / "metrics.json"
    if not path.exists():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("status") == "skipped":
        return None
    return float(data["cer"]) * 100


def plot_cer_comparison() -> Path:
    labels: list[str] = []
    values: list[float] = []
    colors: list[str] = []

    for run_id, label in RUNS:
        cer = load_cer(run_id)
        if cer is not None:
            labels.append(label)
            values.append(cer)
            colors.append("#1a365d")

    for label, cer in LITERATURE:
        labels.append(f"{label} (lit.)")
        values.append(cer * 100)
        colors.append("#94a3b8")

    if not values:
        print("No experiment metrics found; skipping figure generation.")
        return FIGURES / "cer_comparison.png"

    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.bar(labels, values, color=colors)
    ax.set_ylabel("CER (%)")
    ax.set_title("English IAM Handwritten Text Recognition — Character Error Rate")
    ax.tick_params(axis="x", rotation=25)
    plt.tight_layout()

    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), f"{val:.2f}%",
                ha="center", va="bottom", fontsize=9)

    out = FIGURES / "cer_comparison.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    print(f"Saved {out}")
    return out


if __name__ == "__main__":
    plot_cer_comparison()
