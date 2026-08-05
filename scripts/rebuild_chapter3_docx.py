#!/usr/bin/env python3
"""Build Chapter 3 methodology DOCX from CHAPTER_3_METHODOLOGY.md structure."""

from __future__ import annotations

from pathlib import Path

from docx import Document
from docx.shared import Inches, Pt

REPO = Path(__file__).resolve().parents[1]
OUT = REPO / "docs" / "CHAPTER_3_METHODOLOGY.docx"
DEMO_IMG = REPO / "data" / "iam" / "demo" / "images"


def add_heading(doc: Document, text: str, level: int = 1) -> None:
    doc.add_heading(text, level=level)


def add_para(doc: Document, text: str) -> None:
    p = doc.add_paragraph(text)
    for run in p.runs:
        run.font.size = Pt(11)


def main() -> None:
    doc = Document()
    add_heading(doc, "Chapter 3 — Methodology", 0)
    add_para(
        doc,
        "Design-only chapter. No measured CER/WER result numbers appear here. "
        "Implementation outcomes are reported in Chapter 4 and must trace to "
        "experiments/<run_id>/metrics.json.",
    )

    add_heading(doc, "3.1 Introduction", 1)
    add_para(
        doc,
        "Handwritten text recognition (HTR) is difficult because writing styles, spacing, "
        "and stroke quality vary widely across writers. This chapter specifies the research "
        "design for English line-level HTR on the IAM Handwriting Database using transfer "
        "learning from a pretrained TrOCR transformer, with neural (CRNN+CTC) and classical "
        "(Tesseract) baselines. Results and analysis are deferred to Chapter 4.",
    )

    add_heading(doc, "3.2 Dataset", 1)
    add_para(
        doc,
        "Data are obtained from Hugging Face Teklia/IAM-line (official publisher splits) "
        "and prepared by scripts/download_iam.py and scripts/prepare_iam_lines.py. "
        "Processed exports live under data/iam/processed/{train,val,test}/.",
    )
    add_heading(doc, "Table 3.1 — IAM line dataset", 2)
    table = doc.add_table(rows=6, cols=2)
    table.style = "Table Grid"
    rows = [
        ("Property", "Value"),
        ("Language", "English"),
        ("Unit", "Line images"),
        ("Train / Val / Test", "6,482 / 976 / 2,915"),
        ("Modalities", "PNG line image + transcription text"),
        ("Source", "Hugging Face Teklia/IAM-line"),
    ]
    for i, (a, b) in enumerate(rows):
        table.rows[i].cells[0].text = a
        table.rows[i].cells[1].text = b

    add_heading(doc, "Figure 3.1 — Example IAM line", 2)
    if DEMO_IMG.exists():
        images = sorted(DEMO_IMG.glob("*.png"))
        if images:
            doc.add_picture(str(images[0]), width=Inches(5.5))
            add_para(doc, f"Source: {images[0].relative_to(REPO)}")
        else:
            add_para(doc, "[Demo image not found — run prepare_iam_demo_examples.py]")
    else:
        add_para(doc, "[Demo directory missing — run prepare_smoke_data.py or prepare_iam_demo_examples.py]")

    add_heading(doc, "3.3 Preprocessing", 1)
    add_para(
        doc,
        "Line images are converted to RGB and passed through Hugging Face TrOCRProcessor. "
        "No custom binarization is applied. Mild augmentation is used during fine-tuning only.",
    )

    add_heading(doc, "3.4 Model selection", 1)
    add_para(
        doc,
        "TrOCR combines a Vision Transformer (ViT) image encoder with a BART text decoder. "
        "The starting checkpoint is microsoft/trocr-base-handwritten. Fine-tuning uses "
        "autoregressive cross-entropy (not CTC), AdamW, and early stopping on validation CER. "
        "A CRNN+CTC baseline is trained on the same splits; CTC is used only for CRNN. "
        "Tesseract provides a classical OCR baseline.",
    )
    add_heading(doc, "Figure 3.2 — TrOCR architecture (conceptual)", 2)
    add_para(
        doc,
        "Image patches → ViT encoder → cross-attention BART decoder → token sequence.",
    )

    add_heading(doc, "3.5 Experiment design and metrics", 1)
    add_para(
        doc,
        "Primary GPU protocol evaluates pretrained TrOCR, fine-tuned TrOCR, CRNN+CTC, and "
        "Tesseract on the full IAM test split (n=2,915), plus an 8-line demo run. "
        "Metrics are case-sensitive CER and WER via jiwer after whitespace normalization. "
        "Thesis numbers must come from full runs, not smoke subsets.",
    )

    add_heading(doc, "3.6 Baselines (design summary)", 1)
    add_para(
        doc,
        "Chapter 4 compares pretrained vs fine-tuned TrOCR, TrOCR vs CRNN vs Tesseract "
        "(measured), and cites literature CER values separately without claiming an identical protocol.",
    )

    add_heading(doc, "3.7 Chapter boundary", 1)
    add_para(
        doc,
        "This chapter contains no numeric experimental outcomes. Chapter 4 reports measured "
        "results, hyperparameters actually used, and qualitative error analysis.",
    )

    OUT.parent.mkdir(parents=True, exist_ok=True)
    doc.save(OUT)
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
