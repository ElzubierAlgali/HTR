#!/usr/bin/env python3
"""Build Chapter 2 literature review DOCX (impersonal academic voice).

Prose is kept in sync with docs/CHAPTER_2_LITERATURE_REVIEW.md; edit both together.
"""

from __future__ import annotations

from pathlib import Path

from docx import Document
from docx.shared import Pt

REPO = Path(__file__).resolve().parents[1]
OUT = REPO / "docs" / "CHAPTER_2_LITERATURE_REVIEW.docx"

BODY_FONT = "Times New Roman"
BODY_SIZE_PT = 11
TABLE_SIZE_PT = 9

SUMMARY_HEADER = (
    "#",
    "Study",
    "Objective",
    "Dataset",
    "Tools and techniques",
    "Reported results",
    "Limitation",
)

SUMMARY_ROWS = [
    (
        "1",
        "Fine-Tuning Vision Encoder-Decoder Transformers for HTR on Historical Documents "
        "(Parres and Paredes, 2023)",
        "Assess fine-tuned vision encoder-decoder transformers for historical manuscript "
        "transcription",
        "ICFHR 2014 Bentham; ICFHR 2016 Ratsprotokolle; Saint Gall",
        "Fine-tuning of pretrained vision encoder-decoder transformers",
        "WER 6.9% (Bentham), 14.5% (Ratsprotokolle), 17.3% (Saint Gall)",
        "No comparison against other fine-tuning strategies for vision transformers",
    ),
    (
        "2",
        "TrOCR: Transformer-Based Optical Character Recognition with Pre-trained Models "
        "(Li et al., 2023)",
        "Propose an end-to-end transformer OCR model built from pretrained vision and "
        "language components",
        "Synthetic handwritten text-line images generated with TRDG from 5,427 handwriting "
        "fonts; evaluated on IAM and further printed, handwritten, and scene-text benchmarks",
        "ViT image encoder + BART text decoder; pretrained vision and language components",
        "Pretrained components improve recognition; the transformer design outperforms CRNN "
        "systems and Tesseract",
        "Limited comparison against other transformer-based OCR models",
    ),
    (
        "3",
        "Handwriting Transformers (Bhunia et al., 2021)",
        "Generate styled handwritten text images capturing global and local style",
        "Not applicable (generation task)",
        "Transformer encoder-decoder with attention (HWT)",
        "Produces realistic styled handwritten text images",
        "Limited comparison with existing styled text generation methods",
    ),
    (
        "4",
        "AttentionHTR (Kass and Vats, 2022)",
        "Attention-based sequence-to-sequence handwritten word recognition using transfer "
        "learning from scene text",
        "IAM; Imgur5K",
        "ResNet feature extraction with bidirectional LSTM sequence modelling and "
        "content-based attention",
        "IAM CER 6.50%; IAM WER 15.40%",
        "Does not examine the effect of different pretrained models",
    ),
    (
        "5",
        "Handwritten Text Recognition using Deep Learning (Balci et al., 2017)",
        "Classify handwritten words using CNNs and LSTMs for document conversion",
        "IAM Handwriting Dataset, 1,500+ forms, 600+ writers",
        "VGG-19 and ResNet-18/34 with padding and rotation augmentation; Adam optimiser",
        "Word-level accuracy above 90.3%; character-level classification aids word "
        "recognition",
        "Does not explore transformer architectures",
    ),
    (
        "6",
        "Handwritten Text Recognition using Deep Learning with TensorFlow "
        "(Manchala et al., 2020)",
        "Build an HTR system for word classification in digital conversion",
        "IAM Handwriting Dataset, 1,500+ forms, 600+ writers",
        "VGG-19 and ResNet-18/34 for word classification; LSTMs for character segmentation; "
        "Tesseract for preprocessing",
        "Accuracy above 90.3%",
        "Limited comparison against other HTR systems",
    ),
    (
        "7",
        "A Light Transformer-Based Architecture for HTR (Barrere et al., 2022)",
        "Achieve competitive HTR on small datasets with a lightweight transformer",
        "IAM Handwriting Dataset, text-line images",
        "CNN and transformer hybrid; combined CTC and cross-entropy loss",
        "CER 5.70% on the IAM test set without additional data; CER 4.76% with additional "
        "synthetic data",
        "Provides no qualitative analysis of generated outputs",
    ),
    (
        "8",
        "HTR-Flor (de Sousa Neto et al., 2020)",
        "Optimise offline HTR with a gated CRNN using fewer parameters",
        "IAM Handwriting Database",
        "Gated CNN with bidirectional GRUs, implemented in PyTorch and TensorFlow",
        "Outperforms comparable CRNN systems with a reduced parameter count",
        "Limited explanation of the gated architecture design choices",
    ),
    (
        "9",
        "Recurrence-free unconstrained HTR using a gated fully convolutional network "
        "(Coquenet et al., 2020)",
        "Replace LSTM-based modelling with a gated fully convolutional network",
        "RIMES; IAM, images resized to 64 pixels in height",
        "GFCN with CTC loss, depthwise separable convolutions, Adam optimiser, CER and WER "
        "evaluation",
        "CER 4.35% on RIMES; CER 7.99% on IAM",
        "No detailed analysis of the learned features and filters",
    ),
]


def add_para(doc: Document, text: str) -> None:
    p = doc.add_paragraph(text)
    for run in p.runs:
        run.font.size = Pt(BODY_SIZE_PT)
        run.font.name = BODY_FONT


def add_summary_table(doc: Document) -> None:
    table = doc.add_table(rows=len(SUMMARY_ROWS) + 1, cols=len(SUMMARY_HEADER))
    table.style = "Table Grid"
    for j, label in enumerate(SUMMARY_HEADER):
        table.rows[0].cells[j].text = label
    for i, row in enumerate(SUMMARY_ROWS, start=1):
        for j, value in enumerate(row):
            table.rows[i].cells[j].text = value
    for row in table.rows:
        for cell in row.cells:
            for paragraph in cell.paragraphs:
                for run in paragraph.runs:
                    run.font.size = Pt(TABLE_SIZE_PT)
                    run.font.name = BODY_FONT


def main() -> None:
    doc = Document()
    doc.add_heading("Chapter 2 — Literature Review", 0)

    doc.add_heading("2.1 Introduction", 1)
    add_para(
        doc,
        "Handwritten text recognition has been reshaped by deep learning. Convolutional "
        "networks replaced hand-engineered features, recurrent networks trained with "
        "Connectionist Temporal Classification made line-level transcription practical, and "
        "transformer models have more recently been applied to both the visual and the "
        "linguistic side of the task.",
    )
    add_para(
        doc,
        "This chapter reviews that progression. It covers image processing and optical "
        "character recognition as the underlying disciplines, surveys the main handwriting "
        "recognition approaches, and examines the studies most relevant to this thesis. "
        "Particular attention is given to TrOCR, whose architecture and pretrained "
        "checkpoint the present work evaluates.",
    )

    doc.add_heading("2.2 Problem Background", 1)
    add_para(
        doc,
        "Recognising handwritten characters is difficult because the input is highly "
        "variable. Size, shape, slant, and spacing differ between writers and within the "
        "work of a single writer. Unlike printed text, handwriting offers no fixed glyph "
        "inventory to match against.",
    )
    add_para(
        doc,
        "Convolutional neural networks advanced image-based recognition and became the "
        "standard feature extractor for handwriting systems. Recognition then shifted "
        "towards recurrent networks combined with Connectionist Temporal Classification, "
        "which transcribe an entire line without needing explicit character segmentation. "
        "Multidimensional Long Short-Term Memory networks extended this by propagating "
        "recurrent connections along both spatial dimensions of the image.",
    )
    add_para(
        doc,
        "These approaches carry known costs. Recurrent models process sequences step by "
        "step, which limits training throughput, and they can require large parameter "
        "counts to model long-range dependencies. Transformer architectures address both "
        "points through parallel self-attention, and large pretrained language models offer "
        "a decoder that already encodes substantial linguistic structure. The question this "
        "raises for handwriting recognition, and the one this thesis takes up, is how much "
        "of that pretrained capability transfers to a specific benchmark.",
    )

    doc.add_heading("2.3 Image Processing", 1)
    add_para(
        doc,
        "Image processing covers the operations applied to a digital image to enhance it or "
        "to extract information from it. Inputs are images; outputs are either modified "
        "images or measurements derived from them (Covington, 2009). The field sits at the "
        "intersection of signal processing, engineering, and computer science, and supplies "
        "the preparatory operations on which recognition systems depend (Naveenkumar and "
        "Ayyasamy, 2016).",
    )
    add_para(
        doc,
        "For handwriting recognition, the relevant operations are normalisation of size and "
        "contrast, noise reduction, and geometric correction. The present study keeps this "
        "stage minimal. Line images are converted to RGB and normalised by the TrOCR "
        "processor, so that recognition quality reflects the model rather than the image "
        "pipeline.",
    )

    doc.add_heading("2.4 Optical Character Recognition", 1)
    add_para(
        doc,
        "Optical character recognition converts images of text into machine-encoded "
        "characters. An OCR system combines an optical scanner with software that segments "
        "and classifies the resulting image regions. Once converted, the text can be "
        "searched, edited, stored compactly, or passed to downstream processing such as "
        "translation or text mining.",
    )
    add_para(
        doc,
        "Early systems were calibrated to a single font and required a template for each "
        "character. Modern engines handle a wide range of fonts and can reproduce page "
        "structure including columns and embedded images. Recognition of printed text is "
        "largely a solved problem in well-conditioned settings.",
    )
    add_para(
        doc,
        "Handwriting remains the harder case. General-purpose OCR engines are trained "
        "predominantly on printed glyphs and degrade sharply on unconstrained handwriting, "
        "which is why handwriting recognition has developed as a distinct research area "
        "with its own architectures and benchmarks (Isheawy and Hasan, 2015). This thesis "
        "measures that gap directly by evaluating Tesseract on the same test partition as "
        "the neural systems.",
    )

    doc.add_heading("2.5 Handwritten Text Recognition", 1)
    add_para(
        doc,
        "Handwritten text recognition transcribes images of handwriting into "
        "machine-readable text. It is commonly divided by input granularity into character, "
        "word, and line recognition, and by acquisition mode into online recognition, which "
        "records pen trajectory, and offline recognition, which works from a static image. "
        "This thesis addresses offline line recognition.",
    )
    add_para(
        doc,
        "The dominant offline approach for much of the past decade combined convolutional "
        "feature extraction with recurrent sequence modelling and a CTC output layer "
        "(Sahare et al., 2018). CTC removes the need for character-level alignment, "
        "allowing a model to be trained on line images paired only with their "
        "transcriptions. Multidimensional LSTM variants extended this to capture context in "
        "two dimensions (Skala et al., 2022).",
    )
    add_para(
        doc,
        "Applications include the digitisation of archives and the preservation of "
        "historical documents, where manual transcription is prohibitively slow. "
        "Recognition quality is reported almost universally as Character Error Rate and "
        "Word Error Rate, computed as normalised edit distances. These are the metrics "
        "adopted in this thesis.",
    )

    doc.add_heading("2.6 Related Research", 1)
    for para in [
        "Historical document transcription. Parres and Paredes (2023) fine-tune vision "
        "encoder-decoder transformers for historical manuscript transcription, reporting "
        "Word Error Rates of 6.9% on ICFHR 2014 Bentham, 14.5% on ICFHR 2016 "
        "Ratsprotokolle, and 17.3% on Saint Gall. Their work shows that transformer "
        "fine-tuning transfers to degraded historical material, though the corpora and "
        "language differ from the English IAM benchmark used here.",
        "TrOCR. Li et al. (2023) propose TrOCR, an end-to-end transformer OCR model that "
        "pairs a pretrained Vision Transformer image encoder with a pretrained BART text "
        "decoder. Because the decoder is a language model, no separate post-processing "
        "language model is required. The authors report that pretrained vision and language "
        "components improve recognition, and that the pure transformer design outperforms "
        "both CRNN systems and Tesseract on their benchmarks. TrOCR is the architecture "
        "evaluated in this thesis, and the microsoft/trocr-base-handwritten checkpoint is "
        "its published English handwriting variant.",
        "Handwriting generation. Bhunia et al. (2021) introduce Handwriting Transformers, a "
        "transformer network for styled handwritten text image generation that models both "
        "global and local style patterns. The work addresses synthesis rather than "
        "recognition, but demonstrates that transformer attention captures handwriting "
        "style effectively.",
        "Attention-based recognition. Kass and Vats (2022) present AttentionHTR, an "
        "attention-based sequence-to-sequence model for handwritten word recognition that "
        "uses ResNet feature extraction with bidirectional LSTM sequence modelling. "
        "Transfer learning from scene text images mitigates the scarcity of handwriting "
        "training data. On IAM they report a CER of 6.50% and a WER of 15.40% at word level.",
        "Deep learning on IAM. Balci et al. (2017) and Manchala et al. (2020) both apply "
        "convolutional and recurrent architectures, including VGG-19 and ResNet-18/34, to "
        "word-level classification and character segmentation on IAM. Both report "
        "word-level classification accuracy above 90.3%. That figure is an accuracy measure "
        "under each study's own segmentation protocol and is not directly comparable with "
        "the corpus-level error rates reported in this thesis.",
        "Lightweight transformers. Barrere et al. (2022) propose a Light Transformer "
        "architecture that combines convolutional layers with transformer components while "
        "keeping the parameter count low enough for small datasets. A hybrid loss combining "
        "CTC and cross-entropy improves training efficiency. The model reaches a CER of "
        "5.70% on the IAM test set without additional training data, improving to 4.76% "
        "when synthetic data is added.",
        "Gated convolutional models. de Sousa Neto et al. (2020) introduce HTR-Flor, a gated "
        "CNN with bidirectional GRUs that outperforms comparable CRNN systems on IAM with "
        "fewer parameters. Coquenet et al. (2020) go further and remove recurrence "
        "entirely: their Gated Fully Convolutional Network uses depthwise separable "
        "convolutions and a gating mechanism, reaching a CER of 4.35% on RIMES and 7.99% on "
        "IAM with a low parameter count.",
        "Position of this thesis. These studies establish that both convolutional and "
        "transformer designs achieve single-digit CER on IAM, and that pretraining is the "
        "main lever available to a study without large-scale compute. What they do not "
        "settle is how a published transformer checkpoint performs on the full IAM test "
        "partition under a protocol that is documented end to end, or whether further "
        "fine-tuning on that same benchmark adds anything. That is the gap this thesis "
        "addresses.",
    ]:
        add_para(doc, para)

    doc.add_heading("2.7 Summary of Related Research", 1)
    doc.add_heading("Table 2.1 — Summary of reviewed HTR studies", 2)
    add_summary_table(doc)

    doc.add_heading("2.8 Summary", 1)
    add_para(
        doc,
        "This chapter traced handwritten text recognition from convolutional feature "
        "extraction, through recurrent models trained with CTC, to transformer "
        "architectures built on pretrained components. Image processing and optical "
        "character recognition were reviewed as the underlying disciplines, and the "
        "persistent difficulty of unconstrained handwriting for general-purpose OCR engines "
        "was noted.",
    )
    add_para(
        doc,
        "The reviewed studies establish two points that shape the present work. Single-digit "
        "CER on IAM is achievable by several architectural families, with reported figures "
        "including 5.70% for a light transformer, 6.50% for an attention-based model, and "
        "7.99% for a gated fully convolutional network. Pretraining is the principal lever "
        "available to a study without large-scale training resources, and TrOCR is the "
        "clearest instance of a model built entirely from pretrained vision and language "
        "components.",
    )
    add_para(
        doc,
        "What the literature leaves open is the performance of a published TrOCR checkpoint "
        "on the complete IAM English test partition under a fully documented local "
        "protocol, and whether fine-tuning on that benchmark improves it. Chapter 3 sets "
        "out the research design that addresses those questions.",
    )

    OUT.parent.mkdir(parents=True, exist_ok=True)
    doc.save(OUT)
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
