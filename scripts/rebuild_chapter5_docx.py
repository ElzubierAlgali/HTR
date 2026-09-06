#!/usr/bin/env python3
"""Build Chapter 5 DOCX (impersonal academic voice).

Prose is kept in sync with docs/CHAPTER_5_CONCLUSION.md; edit both together.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from docx import Document
from docx.shared import Pt

REPO = Path(__file__).resolve().parents[1]
OUT = REPO / "docs" / "CHAPTER_5_CONCLUSION.docx"
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
        pct = f"{value * 100:.2f}%"
        if data.get("protocol") == "smoke_synthetic":
            return f"{pct} [SMOKE—not primary]"
        return pct
    return str(value)


def fill(text: str) -> str:
    def repl(m: re.Match) -> str:
        return load_metric(m.group(1), m.group(2))

    return re.sub(r"\{\{METRIC:([^.]+)\.([^}]+)\}\}", repl, text)


def add_para(doc: Document, text: str) -> None:
    p = doc.add_paragraph(fill(text))
    for run in p.runs:
        run.font.size = Pt(11)
        run.font.name = "Times New Roman"


def main() -> None:
    doc = Document()
    doc.add_heading("Chapter 5 — Conclusion", 0)

    doc.add_heading("5.1 Revisiting the research aim", 1)
    add_para(
        doc,
        "This thesis set out to establish how well a transformer-based handwritten text "
        "recognition (HTR) model performs on a standard English benchmark when it is "
        "evaluated under a transparent and locally reproducible protocol. The central "
        "question was practical as much as scientific. Given a widely used pretrained TrOCR "
        "checkpoint, pairing a Vision Transformer (ViT) image encoder with a BART text "
        "decoder, what recognition quality is obtainable on the IAM Handwriting Database, "
        "and does further fine-tuning on the official IAM splits produce a measurable gain? "
        "Two subsidiary questions followed. How does such a model compare with a "
        "conventional neural sequence baseline (CRNN with CTC) and with a classical OCR "
        "engine (Tesseract) under identical test conditions? And how can the resulting "
        "system be presented as an interactive application?",
    )
    add_para(
        doc,
        "The investigation was scoped narrowly. It covers English line-level recognition on "
        "IAM, with Character Error Rate (CER) and Word Error Rate (WER) as the primary "
        "metrics. No new network architecture was proposed. The goal was instead a single "
        "aligned workflow running from data preparation through training and evaluation to "
        "a working demonstration, with each stage logged and the outcomes reported with "
        "academic care.",
    )

    doc.add_heading("5.2 Principal findings", 1)
    add_para(
        doc,
        "The experiments were conducted on the full IAM English test partition of 2,915 "
        "line images. Table 5.1 summarises the main quantitative outcomes. Demo-subset and "
        "smoke metrics are excluded from it.",
    )
    add_para(doc, "Table 5.1 — Measured outcomes on the full IAM English test set")
    table = doc.add_table(rows=5, cols=4)
    table.style = "Table Grid"
    for i, row in enumerate(
        [
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
        ]
    ):
        for j, val in enumerate(row):
            table.rows[i].cells[j].text = fill(val)

    add_para(
        doc,
        "The strongest result came from the pretrained TrOCR model, which reached a CER of "
        "{{METRIC:iam_trocr_handwritten.cer}} and a WER of "
        "{{METRIC:iam_trocr_handwritten.wer}}. A publicly available transformer HTR "
        "checkpoint can therefore deliver competitive line-level recognition on IAM, "
        "provided it is assessed on the complete test split rather than a reduced sample.",
    )
    add_para(
        doc,
        "Fine-tuning on the IAM training and validation sets completed successfully and the "
        "run was documented in full. Under the logged schedule, however, the adapted model "
        "did not surpass the Hub checkpoint on the held-out test set. Its CER rose slightly "
        "to {{METRIC:iam_trocr_finetuned.cer}}, with a WER of "
        "{{METRIC:iam_trocr_finetuned.wer}}. Early stopping halted training after three "
        "epochs once validation CER ceased to improve. The outcome is informative rather "
        "than disappointing. The base checkpoint is already specialised for English "
        "handwriting, so the remaining margin is narrow, and a short adaptation run with a "
        "small micro-batch may in any case be insufficient to unlock further gains. "
        "Fine-tuning is best read as a completed experimental intervention whose measured "
        "effect was neutral to slightly adverse, not as an automatic route to higher "
        "accuracy.",
    )
    add_para(
        doc,
        "The CRNN+CTC baseline, trained from scratch on the same splits, produced a markedly "
        "higher CER of {{METRIC:iam_crnn.cer}}. That figure reflects a lightweight CNN, "
        "BiLSTM and CTC reference with constrained input geometry. It is not a claim about "
        "the best achievable CTC system. The contrast does nevertheless underline the "
        "advantage of large-scale pretrained transformers under matched data and metrics.",
    )
    add_para(
        doc,
        "Classical Tesseract, evaluated in line mode on the identical full test partition, "
        "yielded a CER of {{METRIC:iam_tesseract.cer}} and a WER of "
        "{{METRIC:iam_tesseract.wer}}. As a general-purpose OCR engine without "
        "handwriting-specific adaptation, it remained far behind TrOCR, completing the "
        "baseline triad set out in the methodology.",
    )
    add_para(
        doc,
        "Published IAM figures from related studies were cited for contextual scale only. "
        "Those works may differ in preprocessing, decoding, or split definitions, so no "
        "matched state-of-the-art ranking is asserted here. Inspection of the high-error "
        "lines showed that short references, punctuation-heavy strings, and rare or "
        "hyphenated tokens remain difficult even when corpus-level CER is low. The Gradio "
        "demonstration showed that the same recognition stack can be exposed for "
        "interactive use. Its demo-subset scores count as application evidence only and do "
        "not enter the primary result tables.",
    )

    doc.add_heading("5.3 Contributions of the study", 1)
    add_para(
        doc,
        "Within the limits of a master's project, the contributions are as follows. The "
        "first is a coherent English IAM evaluation protocol, under which pretrained TrOCR, "
        "fine-tuned TrOCR, CRNN+CTC, and Tesseract are all assessed on the identical full "
        "test partition with shared metric definitions. The second is a fully documented "
        "end-to-end fine-tuning experiment, covering learning rate, batching strategy, "
        "early stopping, and wall-clock cost, so that the adaptation step is reproducible "
        "and open to scrutiny. The third is the reporting of a negative or near-neutral "
        "fine-tuning outcome with the same clarity as a positive result, which strengthens "
        "the credibility of the empirical account. The fourth is the positioning of "
        "transformer performance against both a lightweight neural baseline and a classical "
        "OCR baseline, without overstating either comparator. The fifth is a lightweight web "
        "demonstration that places the recognition model in an applied setting while keeping "
        "demo behaviour separate from full-test evidence. Taken together these amount to an "
        "aligned research-and-application contribution rather than a claim of architectural "
        "novelty.",
    )

    doc.add_heading("5.4 Limitations of the study", 1)
    add_para(
        doc,
        "Several constraints qualify the findings. The work addresses English line images "
        "only; page-level layout analysis and multilingual handwriting fall outside its "
        "remit. The fine-tuning regime was short and early-stopped, and cannot be presented "
        "as an exhaustive search over optimisation choices. The CRNN baseline was kept "
        "simple by design. More elaborate neural sequence models might narrow the gap to "
        "TrOCR, but pursuing them would have drawn the study away from its "
        "transformer-centred question. Tesseract was run as a classical line-mode reference "
        "rather than as a handwriting-tuned specialist. Literature comparisons remain "
        "secondary and protocol-sensitive. Application metrics gathered on the small demo "
        "subset, including any smoke or synthetic checks, are illustrative and were never "
        "intended to replace full-test evaluation.",
    )

    doc.add_heading("5.5 Recommendations for future research", 1)
    add_para(
        doc,
        "Further work could pursue longer or more carefully regularised fine-tuning "
        "schedules, testing alternative learning-rate policies and larger effective batch "
        "sizes to determine whether the observed plateau can be overcome. Stronger neural "
        "baselines trained under the same IAM splits would sharpen the comparative picture "
        "beyond the lightweight CRNN used here. Beyond the line level, the pipeline could be "
        "extended towards page-level HTR, and the interface towards batch processing and "
        "structured error review, increasing both scientific reach and practical utility.",
    )

    doc.add_heading("5.6 Concluding remarks", 1)
    add_para(
        doc,
        "This study has shown that pretrained transformer-based HTR can be evaluated "
        "rigorously on the full English IAM test set within a transparent student research "
        "pipeline, attaining a CER of {{METRIC:iam_trocr_handwritten.cer}}. Additional "
        "fine-tuning was executed successfully, yet under the logged conditions it did not "
        "improve test recognition, and that finding is reported as measured. Neural and "
        "classical baselines place the result in comparative context, while the "
        "demonstration interface completes the applied thread of the project. The lasting "
        "value of the work lies in that measured alignment of method, experiment, and "
        "application, not in a claim of architectural novelty.",
    )

    OUT.parent.mkdir(parents=True, exist_ok=True)
    doc.save(OUT)
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
