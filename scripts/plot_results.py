#!/usr/bin/env python3
"""Generate thesis figures from experiment metrics."""

from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
EXPERIMENTS = REPO_ROOT / "experiments"
FIGURES = EXPERIMENTS / "figures"
FIGURES.mkdir(parents=True, exist_ok=True)

MEASURED = [
    ("iam_trocr_handwritten", "TrOCR pretrained"),
    ("iam_trocr_finetuned", "TrOCR fine-tuned"),
    ("iam_crnn", "CRNN+CTC"),
    ("iam_tesseract", "Tesseract"),
]

LITERATURE = [
    ("AttentionHTR", 0.065),
    ("Light Transformer", 0.057),
    ("GFCN", 0.0799),
]


def load_cer(run_id: str) -> tuple[float | None, int | None]:
    path = EXPERIMENTS / run_id / "metrics.json"
    if not path.exists():
        return None, None
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if data.get("status") == "skipped":
        return None, None
    return float(data["cer"]) * 100, int(data.get("n_samples") or 0)


def _collect() -> tuple[list[str], list[float], list[str], list[int]]:
    labels: list[str] = []
    values: list[float] = []
    colors: list[str] = []
    ns: list[int] = []
    for run_id, label in MEASURED:
        cer, n = load_cer(run_id)
        if cer is not None:
            labels.append(label)
            values.append(cer)
            colors.append("#1a365d")
            ns.append(n or 0)
    for label, cer in LITERATURE:
        labels.append(f"{label}*")
        values.append(cer * 100)
        colors.append("#a0aec0")
        ns.append(-1)
    return labels, values, colors, ns


def plot_with_matplotlib(labels, values, colors, ns) -> Path:
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.bar(labels, values, color=colors)
    ax.set_ylabel("CER (%)")
    ax.set_title("IAM CER comparison (measured vs literature)")
    ax.tick_params(axis="x", rotation=25)
    measured_n = next((n for n in ns if n and n > 0), None)
    note = "* literature (cited; protocol may differ)"
    if measured_n:
        note = f"Measured bars use n={measured_n}. " + note
    ax.text(0.01, 0.98, note, transform=ax.transAxes, va="top", fontsize=8)
    for bar, val in zip(bars, values):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height(),
            f"{val:.2f}",
            ha="center",
            va="bottom",
            fontsize=8,
        )
    fig.tight_layout()
    out = FIGURES / "cer_comparison.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out


def plot_with_pil(labels, values, colors, ns) -> Path:
    """Fallback bar chart without matplotlib."""
    from PIL import Image, ImageDraw, ImageFont

    width, height = 1100, 520
    margin_l, margin_b, margin_t, margin_r = 80, 120, 60, 40
    img = Image.new("RGB", (width, height), (255, 255, 255))
    draw = ImageDraw.Draw(img)
    font = ImageFont.load_default()
    max_v = max(values) if values else 1.0
    plot_w = width - margin_l - margin_r
    plot_h = height - margin_t - margin_b
    n = max(1, len(values))
    bar_w = plot_w / (n * 1.5)
    for i, (label, val, color) in enumerate(zip(labels, values, colors)):
        x0 = margin_l + i * (bar_w * 1.5)
        bh = (val / max_v) * plot_h if max_v else 0
        y0 = margin_t + plot_h - bh
        draw.rectangle([x0, y0, x0 + bar_w, margin_t + plot_h], fill=color)
        draw.text((x0, y0 - 12), f"{val:.1f}", fill=(0, 0, 0), font=font)
        draw.text((x0, margin_t + plot_h + 8), label[:18], fill=(0, 0, 0), font=font)
    measured_n = next((n for n in ns if n and n > 0), None)
    title = "IAM CER comparison (measured vs literature)"
    draw.text((margin_l, 20), title, fill=(0, 0, 0), font=font)
    note = "* literature (cited; protocol may differ)"
    if measured_n:
        note = f"Measured n={measured_n}. " + note
    draw.text((margin_l, height - 24), note, fill=(80, 80, 80), font=font)
    out = FIGURES / "cer_comparison.png"
    img.save(out)
    return out


def plot_cer_comparison() -> Path:
    labels, values, colors, ns = _collect()
    if not values:
        # still write an empty placeholder figure
        from PIL import Image, ImageDraw

        img = Image.new("RGB", (800, 400), (255, 255, 255))
        ImageDraw.Draw(img).text((40, 180), "No measured metrics yet", fill=(0, 0, 0))
        out = FIGURES / "cer_comparison.png"
        img.save(out)
        print(f"Wrote {out} (placeholder)")
        return out
    try:
        out = plot_with_matplotlib(labels, values, colors, ns)
    except ImportError:
        out = plot_with_pil(labels, values, colors, ns)
    print(f"Wrote {out}")
    return out


def main() -> None:
    plot_cer_comparison()


if __name__ == "__main__":
    main()
