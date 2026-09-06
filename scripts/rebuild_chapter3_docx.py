#!/usr/bin/env python3
"""Build Chapter 3 methodology DOCX (master's thesis academic prose)."""

from __future__ import annotations

from pathlib import Path

from docx import Document
from docx.shared import Inches, Pt

REPO = Path(__file__).resolve().parents[1]
OUT = REPO / "docs" / "CHAPTER_3_METHODOLOGY.docx"
DEMO_IMG = REPO / "data" / "iam" / "demo" / "images"


def add_para(doc: Document, text: str) -> None:
    p = doc.add_paragraph(text)
    for run in p.runs:
        run.font.size = Pt(11)
        run.font.name = "Times New Roman"


def main() -> None:
    doc = Document()
    doc.add_heading("Chapter 3 — Methodology", 0)
    add_para(
        doc,
        "This chapter presents the research design only. Measured CER and WER values "
        "are reserved for Chapter 4.",
    )

    doc.add_heading("3.1 Introduction", 1)
    add_para(
        doc,
        "A sound empirical study of handwritten text recognition (HTR) requires more "
        "than the selection of a fashionable model: it requires an explicit account of "
        "the data, the preprocessing assumptions, the learning objectives, the evaluation "
        "criteria, and the comparisons against which claims will be judged. This chapter "
        "therefore sets out the methodological framework adopted for the present thesis. "
        "The research focuses on English line-level recognition using the IAM Handwriting "
        "Database and investigates transfer learning from a pretrained TrOCR transformer, "
        "whose Vision Transformer (ViT) encoder is paired with a BART text decoder. A "
        "convolutional recurrent network trained with Connectionist Temporal Classification "
        "(CRNN+CTC) provides a neural baseline of classical design, while Tesseract is "
        "retained as an optional classical optical character recognition reference when "
        "the runtime environment permits its use.",
    )
    add_para(
        doc,
        "The chapter proceeds from dataset characterisation to preprocessing, model "
        "choice, metric definitions, and the planned experiment matrix. In keeping with "
        "conventional thesis organisation, no experimental scores are reported here; "
        "Chapter 4 is responsible for implementation detail, measured outcomes, and "
        "interpretive analysis.",
    )

    doc.add_heading("3.2 Dataset", 1)
    add_para(
        doc,
        "Reliable benchmarking in HTR depends on a corpus whose splits are stable and "
        "publicly documented. The study therefore employs the English IAM line corpus "
        "distributed as Hugging Face Teklia/IAM-line, which preserves the publisher’s "
        "official training, validation, and test partitions. Each sample consists of a "
        "line image together with its corresponding transcription. Local preparation "
        "yields organised image directories and label tables suitable for both training "
        "and evaluation, while a small demonstration subset is reserved for the interactive "
        "application described later in the thesis.",
    )
    doc.add_heading("Table 3.1 — IAM line dataset (Teklia/IAM-line)", 2)
    table = doc.add_table(rows=6, cols=2)
    table.style = "Table Grid"
    for i, (a, b) in enumerate(
        [
            ("Property", "Value"),
            ("Language", "English"),
            ("Unit", "Line images"),
            ("Train / Val / Test", "6,482 / 976 / 2,915"),
            ("Modalities", "PNG line image + transcription text"),
            ("Source", "Hugging Face Teklia/IAM-line"),
        ]
    ):
        table.rows[i].cells[0].text = a
        table.rows[i].cells[1].text = b
    add_para(
        doc,
        "The test partition contains 2,915 lines. This full split constitutes the primary "
        "evaluation population of the thesis and is preferred over reduced samples that "
        "would weaken comparability with published IAM practice.",
    )

    doc.add_heading("Figure 3.1 — Example IAM line", 2)
    if DEMO_IMG.exists():
        images = sorted(DEMO_IMG.glob("*.png"))
        if images:
            doc.add_picture(str(images[0]), width=Inches(5.5))
            add_para(doc, "A representative English line image illustrating the visual domain addressed by the study.")
        else:
            add_para(doc, "[Demo image not found — run prepare_iam_demo_examples.py]")
    else:
        add_para(doc, "[Demo directory missing — run prepare_iam_demo_examples.py]")

    doc.add_heading("3.3 Preprocessing", 1)
    add_para(
        doc,
        "Preprocessing is kept intentionally conservative so that recognition performance "
        "can be attributed primarily to the model rather than to aggressive image "
        "engineering. Line images are converted to RGB and presented to the Hugging Face "
        "TrOCR processor, which jointly handles visual normalisation and tokenisation for "
        "the encoder–decoder model. No custom binarisation pipeline is introduced. Mild "
        "geometric and photometric augmentation is applied exclusively during fine-tuning, "
        "on the premise that stochastic variation may aid adaptation while leaving the "
        "evaluation distribution unaltered. All reported test scores are therefore computed "
        "on unaugmented images.",
    )

    doc.add_heading("3.4 Model selection", 1)
    doc.add_heading("3.4.1 TrOCR as the primary model", 2)
    add_para(
        doc,
        "TrOCR is adopted as the principal recognition architecture because it exemplifies "
        "the contemporary transfer-learning paradigm in HTR: an image transformer encodes "
        "local visual structure, while an autoregressive text transformer decodes character "
        "sequences under a language-model prior. The study begins from the publicly available "
        "checkpoint microsoft/trocr-base-handwritten, which has already been pretrained for "
        "English handwritten lines. Fine-tuning on the IAM training and validation partitions "
        "uses teacher-forced cross-entropy rather than CTC, with AdamW optimisation and early "
        "stopping guided by validation CER. This design choice is consequential: CTC remains "
        "associated only with the neural baseline, and is never treated as the training "
        "objective of TrOCR.",
    )
    doc.add_heading("Figure 3.2 — TrOCR architecture (conceptual)", 2)
    add_para(
        doc,
        "Image patches are encoded by a ViT encoder and decoded by a cross-attentive BART "
        "decoder into a token sequence.",
    )

    doc.add_heading("3.4.2 CRNN+CTC as a neural baseline", 2)
    add_para(
        doc,
        "To situate transformer performance against a familiar neural alternative, a CRNN "
        "with CTC is trained from scratch on the same IAM splits. The baseline is deliberately "
        "lightweight: convolutional feature extraction is followed by bidirectional recurrent "
        "modelling and CTC alignment. Its purpose is comparative clarity rather than "
        "architectural rivalry. A large performance gap, should it appear, would illuminate "
        "the benefit of large-scale pretrained transformers under matched data conditions.",
    )

    doc.add_heading("3.4.3 Tesseract as an optional classical baseline", 2)
    add_para(
        doc,
        "Tesseract, operated in line-oriented recognition mode, is included as a classical "
        "OCR reference. Because availability of the system binary can vary across machines, "
        "the methodology treats Tesseract as optional: when execution is impossible, Chapter 4 "
        "records a skipped status instead of fabricating scores. This rule preserves "
        "methodological honesty without forcing an incomplete software dependency to dictate "
        "the scientific narrative.",
    )

    doc.add_heading("3.5 Experiment design and evaluation metrics", 1)
    add_para(
        doc,
        "The empirical programme is organised as a small matrix of complementary runs. "
        "Primary scientific claims rest on full-test evaluation of pretrained TrOCR, "
        "fine-tuned TrOCR, and the CRNN+CTC baseline. The optional Tesseract run and the "
        "demonstration subset support completeness and application discussion, respectively, "
        "but do not redefine the primary evidence base.",
    )
    doc.add_heading("Table 3.2 — Designed experiment matrix", 2)
    mtable = doc.add_table(rows=6, cols=4)
    mtable.style = "Table Grid"
    for i, row in enumerate(
        [
            ("ID", "Run", "Role", "Evaluation sample"),
            ("E1", "Pretrained TrOCR", "Primary transformer baseline", "Full test (n=2,915)"),
            ("E2", "Fine-tuned TrOCR", "Adaptation experiment", "Full test (n=2,915)"),
            ("E3", "CRNN+CTC", "Neural baseline", "Full test (n=2,915)"),
            ("E4", "Tesseract", "Optional classical baseline", "Full test (n=2,915)"),
            ("E5", "Demonstration subset", "Application support", "Demo lines only"),
        ]
    ):
        for j, val in enumerate(row):
            mtable.rows[i].cells[j].text = val
    add_para(
        doc,
        "Two metrics dominate the evaluation. Character Error Rate (CER) quantifies the "
        "normalised edit distance at character level and remains the principal indicator of "
        "transcription fidelity in HTR. Word Error Rate (WER) provides a complementary "
        "word-level view of recognition difficulty. Both are computed after case-sensitive "
        "whitespace normalisation; transcriptions are not lowercased, so that the metric "
        "reflects orthographic detail rather than an artificially simplified string space. "
        "Corpus CER is defined as the ratio of total character edits to total reference "
        "characters across the evaluated set.",
    )
    add_para(
        doc,
        "Engineering smoke tests with severely reduced sample limits may be used during "
        "development, but they are excluded from thesis claims. All numbers advanced as "
        "research evidence must originate from the full GPU protocol on the complete test "
        "partition.",
    )

    doc.add_heading("3.6 Comparative framework", 1)
    add_para(
        doc,
        "Chapter 4 is designed to answer three comparative questions that follow directly "
        "from this methodology. First, does fine-tuning improve upon the pretrained TrOCR "
        "checkpoint when both are evaluated on the same full IAM test set? Second, how does "
        "TrOCR compare with the CRNN+CTC baseline under identical data and metric definitions? "
        "Third, how do the measured scores relate, at a contextual level only, to CER figures "
        "reported in selected IAM literature? The third comparison is deliberately cautious: "
        "published studies may differ in preprocessing, decoding, or split conventions, and "
        "are therefore cited for scale rather than treated as protocol-identical replications.",
    )

    doc.add_heading("3.7 Scope of the chapter", 1)
    add_para(
        doc,
        "In summary, Chapter 3 fixes the scientific design of the thesis: English IAM line "
        "data, conservative preprocessing, TrOCR as the primary transfer-learning model, "
        "CRNN+CTC as a controlled neural baseline, optional classical OCR, and full-test "
        "CER/WER evaluation. The chapter contains no numeric experimental outcomes. "
        "Implementation choices actually used, measured results, and interpretive discussion "
        "are developed in Chapter 4.",
    )

    OUT.parent.mkdir(parents=True, exist_ok=True)
    doc.save(OUT)
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
