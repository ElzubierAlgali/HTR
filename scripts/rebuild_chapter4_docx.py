#!/usr/bin/env python3
"""Build Chapter 4 implementation/results DOCX (thesis style, not software docs)."""

from __future__ import annotations

import json
import re
from pathlib import Path

from docx import Document
from docx.shared import Inches, Pt

REPO = Path(__file__).resolve().parents[1]
OUT = REPO / "docs" / "CHAPTER_4_IMPLEMENTATION_RESULTS.docx"
MD = REPO / "docs" / "CHAPTER_4_IMPLEMENTATION_RESULTS.md"
FIGURE = REPO / "experiments" / "figures" / "cer_comparison.png"
EXPERIMENTS = REPO / "experiments"


def load_metric(run_id: str, field: str) -> str:
    path = EXPERIMENTS / run_id / "metrics.json"
    if not path.exists():
        return f"[pending:{run_id}.{field}]"
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if data.get("status") == "skipped":
        return f"[skipped: {data.get('reason', 'n/a')}]"
    value = data.get(field, "?")
    if field in ("cer", "wer") and isinstance(value, (int, float)):
        return f"{value * 100:.2f}%"
    return str(value)


def fill(text: str) -> str:
    def repl(m: re.Match) -> str:
        return load_metric(m.group(1), m.group(2))

    return re.sub(r"\{\{METRIC:([^.]+)\.([^}]+)\}\}", repl, text)


def add_para(doc: Document, text: str) -> None:
    p = doc.add_paragraph(fill(text))
    for run in p.runs:
        run.font.size = Pt(11)


def main() -> None:
    doc = Document()
    doc.add_heading("Chapter 4 — Implementation and Results", 0)
    add_para(
        doc,
        "Every numeric claim traces to experiments/<run_id>/metrics.json. "
        "Literature values are cited separately and may use different protocols.",
    )

    doc.add_heading("4.1 Research Contribution", 1)
    for item in [
        "Reproducible English IAM train/eval pipeline with logged artifacts.",
        "TrOCR fine-tuning on IAM with train-only augmentation and train_log.json.",
        "Measured CRNN+CTC and Tesseract baselines on the same full test split (n=2,915).",
        "Gradio demo for interactive English line transcription.",
        "Comparative analysis vs cited literature at matched test-set scale (no unmatched SOTA claim).",
    ]:
        doc.add_paragraph(item, style="List Bullet")

    doc.add_heading("4.2 Implementation overview", 1)
    add_para(
        doc,
        "Core components: dataset I/O (dataset.py), TrOCR load/generate (models.py), "
        "fine-tune (train.py), CRNN+CTC (baselines/crnn.py), metrics (metrics.py), "
        "evaluation (evaluate.py), and Gradio demo (app/gradio_app.py). "
        "Dataset splits and sizes are defined in Chapter 3.",
    )
    table = doc.add_table(rows=7, cols=3)
    table.style = "Table Grid"
    header = ("Component", "Role", "Location")
    rows = [
        header,
        ("Dataset I/O", "Line images + labels", "src/htr/dataset.py"),
        ("TrOCR", "Hub or local checkpoint", "src/htr/models.py"),
        ("Fine-tune", "CE / AdamW / early stop", "src/htr/train.py"),
        ("CRNN+CTC", "Neural baseline", "src/htr/baselines/crnn.py"),
        ("Evaluation", "E1–E5 runners", "src/htr/evaluate.py"),
        ("Demo UI", "Interactive recognition", "app/gradio_app.py"),
    ]
    for i, row in enumerate(rows):
        for j, val in enumerate(row):
            table.rows[i].cells[j].text = val

    doc.add_heading("4.3 Experiments", 1)
    train_log = EXPERIMENTS / "iam_trocr_finetuned" / "train_log.json"
    if train_log.exists():
        log = json.loads(train_log.read_text(encoding="utf-8-sig"))
        add_para(
            doc,
            f"Fine-tune log: lr={log.get('lr')}, batch_size={log.get('batch_size')}, "
            f"epochs_ran={log.get('epochs_ran')}, best_val_cer={log.get('best_val_cer')}, "
            f"device={log.get('device')}, wall_clock_sec={log.get('wall_clock_sec')}.",
        )
    else:
        add_para(doc, "Fine-tune hyperparameters will be read from train_log.json after training.")

    doc.add_heading("4.4 Results", 1)
    add_para(doc, "Table 4.1 — Measured results")
    mtable = doc.add_table(rows=6, cols=4)
    mtable.style = "Table Grid"
    mrows = [
        ("Method", "CER", "WER", "n"),
        (
            "TrOCR pretrained",
            "{{METRIC:iam_trocr_handwritten.cer}}",
            "{{METRIC:iam_trocr_handwritten.wer}}",
            "{{METRIC:iam_trocr_handwritten.n_samples}}",
        ),
        (
            "TrOCR fine-tuned",
            "{{METRIC:iam_trocr_finetuned.cer}}",
            "{{METRIC:iam_trocr_finetuned.wer}}",
            "{{METRIC:iam_trocr_finetuned.n_samples}}",
        ),
        (
            "CRNN+CTC",
            "{{METRIC:iam_crnn.cer}}",
            "{{METRIC:iam_crnn.wer}}",
            "{{METRIC:iam_crnn.n_samples}}",
        ),
        (
            "Tesseract",
            "{{METRIC:iam_tesseract.cer}}",
            "{{METRIC:iam_tesseract.wer}}",
            "{{METRIC:iam_tesseract.n_samples}}",
        ),
        (
            "Demo",
            "{{METRIC:iam_demo.cer}}",
            "{{METRIC:iam_demo.wer}}",
            "{{METRIC:iam_demo.n_samples}}",
        ),
    ]
    for i, row in enumerate(mrows):
        for j, val in enumerate(row):
            mtable.rows[i].cells[j].text = fill(val)

    doc.add_heading("Figure 4.1 — CER comparison", 2)
    if FIGURE.exists():
        doc.add_picture(str(FIGURE), width=Inches(5.8))
    else:
        add_para(doc, "[Run scripts/plot_results.py to generate cer_comparison.png]")

    doc.add_heading("Table 4.2 — Literature CER (cited)", 2)
    ltable = doc.add_table(rows=4, cols=3)
    ltable.style = "Table Grid"
    for i, row in enumerate(
        [
            ("Method", "CER (IAM)", "Source"),
            ("AttentionHTR", "6.50%", "Kass & Vats, 2022"),
            ("Light Transformer", "5.70%", "Barrère et al., 2022"),
            ("GFCN", "7.99%", "Coquenet et al., 2020"),
        ]
    ):
        for j, val in enumerate(row):
            ltable.rows[i].cells[j].text = val

    doc.add_heading("4.5 Analysis", 1)
    add_para(
        doc,
        "The Hub TrOCR checkpoint is already IAM-oriented; fine-tuning may yield only a small "
        "CER change and must be reported honestly. Comparisons among TrOCR, CRNN, and Tesseract "
        "use the same test split and metric normalization. High-CER examples are listed in "
        "experiments/figures/error_examples.md. Limitations include English line-level scope and "
        "possible protocol differences versus cited papers. Do not claim SOTA without a matched protocol.",
    )

    doc.add_heading("4.6 Application", 1)
    add_para(
        doc,
        "The Gradio application (app/gradio_app.py) demonstrates English IAM line transcription "
        "with optional ground-truth CER.",
    )

    doc.add_heading("4.7 Traceability", 1)
    add_para(
        doc,
        "Reproduce with bash scripts/run_gpu_protocol.sh (or stepwise commands in README.md). "
        "All body numbers must resolve to experiment artifacts under experiments/.",
    )

    OUT.parent.mkdir(parents=True, exist_ok=True)
    doc.save(OUT)
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
