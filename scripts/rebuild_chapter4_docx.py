#!/usr/bin/env python3
"""Rebuild Chapter_4_Implementation.docx aligned with the current HTR codebase."""

from __future__ import annotations

import shutil
import tempfile
import zipfile
from pathlib import Path
from xml.sax.saxutils import escape

REPO_ROOT = Path(__file__).resolve().parents[1]
DOCX_PATH = REPO_ROOT / "trocr-bullinger-htr-main" / "Chapter_4_Implementation.docx"

NS = (
    'xmlns:wpc="http://schemas.microsoft.com/office/word/2010/wordprocessingCanvas" '
    'xmlns:mo="http://schemas.microsoft.com/office/mac/office/2008/main" '
    'xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006" '
    'xmlns:mv="urn:schemas-microsoft-com:mac:vml" '
    'xmlns:o="urn:schemas-microsoft-com:office:office" '
    'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" '
    'xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math" '
    'xmlns:v="urn:schemas-microsoft-com:vml" '
    'xmlns:wp14="http://schemas.microsoft.com/office/word/2010/wordprocessingDrawing" '
    'xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing" '
    'xmlns:w10="urn:schemas-microsoft-com:office:word" '
    'xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" '
    'xmlns:w14="http://schemas.microsoft.com/office/word/2010/wordml" '
    'xmlns:wpg="http://schemas.microsoft.com/office/word/2010/wordprocessingGroup" '
    'xmlns:wpi="http://schemas.microsoft.com/office/word/2010/wordprocessingInk" '
    'xmlns:wne="http://schemas.microsoft.com/office/word/2006/wordml" '
    'xmlns:wps="http://schemas.microsoft.com/office/word/2010/wordprocessingShape" '
    'mc:Ignorable="w14 wp14"'
)


def _text(text: str) -> str:
    return escape(text)


def _para(text: str, style: str | None = None, center: bool = False) -> str:
    ppr = []
    if style:
        ppr.append(f'<w:pStyle w:val="{style}"/>')
    if center:
        ppr.append('<w:jc w:val="center"/>')
    ppr_xml = f"<w:pPr>{''.join(ppr)}</w:pPr>" if ppr else ""
    return f"<w:p>{ppr_xml}<w:r><w:t>{_text(text)}</w:t></w:r></w:p>"


def _code_block(lines: list[str]) -> str:
    runs = []
    for i, line in enumerate(lines):
        if i:
            runs.append("<w:br/>")
        space = ' xml:space="preserve"' if line.startswith(" ") or line == "" else ""
        runs.append(f"<w:t{space}>{_text(line)}</w:t>")
    return f"<w:p><w:r>{''.join(runs)}</w:r></w:p>"


def build_document_xml() -> str:
    parts: list[str] = []

    def add(text: str, style: str | None = None, center: bool = False) -> None:
        parts.append(_para(text, style=style, center=center))

    def add_code(lines: list[str]) -> None:
        parts.append(_code_block(lines))

    add("Chapter 4: Implementation", style="Title", center=True)

    add("4.1 System Overview", style="Heading1")
    add(
        "The implementation delivers an English handwritten text recognition (HTR) research "
        "and application pipeline. The system has two integrated layers: (1) a reproducible "
        "batch evaluation pipeline for measuring Character Error Rate (CER) and Word Error Rate "
        "(WER) on the IAM Handwriting Database, and (2) a Gradio web application for interactive "
        "line transcription. Both layers share the same core inference and metrics modules under "
        "src/htr/. The work is evaluation-only: no new model training is performed; the "
        "pretrained checkpoint microsoft/trocr-base-handwritten is used throughout."
    )

    add("4.2 Repository Structure", style="Heading1")
    add("The project is organized as follows:")
    for item in [
        "configs/: YAML experiment definitions (iam_trocr_handwritten, iam_demo, iam_tesseract)",
        "src/htr/: Shared library — models, inference, metrics, and batch evaluation",
        "scripts/: Data preparation, evaluation CLI, figure generation, and experiment runners",
        "app/gradio_app.py: Gradio web demo for English IAM line images",
        "data/iam/: IAM dataset exports (processed splits and demo examples)",
        "experiments/: Evaluation outputs (metrics.json, predictions.csv, figures)",
    ]:
        add(item, style="ListBullet")

    add("4.3 Technology Stack", style="Heading1")
    add("The implementation uses the following technologies (see pyproject.toml and environment.yml):")
    for item in [
        "Python 3.9+: Core language",
        "PyTorch (torch): Deep learning runtime; CUDA used when available, otherwise CPU",
        "Hugging Face Transformers: TrOCRProcessor and VisionEncoderDecoderModel loading",
        "Gradio 4.x: Web interface for the interactive demo",
        "Pillow (PIL): RGB image loading and conversion",
        "jiwer: Case-sensitive CER and WER computation",
        "Hugging Face datasets: IAM line dataset download (Teklia/IAM-line)",
        "PyYAML: Evaluation configuration files",
        "pytesseract: Optional Tesseract baseline backend",
        "matplotlib: CER comparison figure generation",
    ]:
        add(item, style="ListBullet")

    add("4.4 Dataset Pipeline", style="Heading1")
    add(
        "English IAM line-level data is sourced from the Hugging Face dataset Teklia/IAM-line, "
        "which provides official train, validation, and test splits (6,482 / 976 / 2,915 lines)."
    )
    add("4.4.1 Download", style="Heading2")
    add("scripts/download_iam.py downloads each split to Parquet files under data/iam/raw/.")
    add("4.4.2 Export", style="Heading2")
    add(
        "scripts/prepare_iam_lines.py exports images and labels.csv into "
        "data/iam/processed/{train,val,test}/."
    )
    add("4.4.3 Demo Examples", style="Heading2")
    add(
        "scripts/prepare_iam_demo_examples.py copies eight English test lines to data/iam/demo/ "
        "for the Gradio Examples gallery."
    )

    add("4.5 Model Architecture", style="Heading1")
    add(
        "The system uses TrOCR (Transformer-based Optical Character Recognition), consisting of:"
    )
    add(
        "Vision Encoder: A Vision Transformer (ViT) that encodes the input line image",
        style="ListNumber",
    )
    add(
        "Text Decoder: A BART-based autoregressive decoder that generates the transcription",
        style="ListNumber",
    )
    add(
        "The checkpoint microsoft/trocr-base-handwritten is pretrained on English IAM handwriting. "
        "Processor and model weights are loaded as a matched pair from the same checkpoint. "
        "This replaces the earlier Bullinger historical-document model; the current thesis scope "
        "is English IAM only."
    )

    add("4.6 Core Library Components (src/htr/)", style="Heading1")

    add("4.6.1 Model Loading (models.py)", style="Heading2")
    add("ModelBundle encapsulates the processor, model, and device:")
    add_code(
        [
            "processor = TrOCRProcessor.from_pretrained(checkpoint)",
            "model = VisionEncoderDecoderModel.from_pretrained(checkpoint)",
            "model.to(device)",
            "model.eval()",
        ]
    )
    add(
        "load_model_bundle() validates the checkpoint against KNOWN_CHECKPOINTS and returns a "
        "ModelBundle used by both inference and batch evaluation."
    )

    add("4.6.2 Inference (infer.py)", style="Heading2")
    add("Single-image recognition is exposed via recognize():")
    add_code(
        [
            "def recognize(image, checkpoint: str) -> str:",
            "    bundle = _cached_bundle(checkpoint)  # LRU-cached model load",
            "    pil_image = _load_image(image).convert('RGB')",
            "    return normalize_text(bundle.generate(pil_image))",
        ]
    )
    add(
        "Model weights are cached with functools.lru_cache so the Gradio app loads the model once "
        "per checkpoint and reuses it across requests."
    )

    add("4.6.3 Metrics (metrics.py)", style="Heading2")
    add(
        "CER and WER are computed with jiwer using case-sensitive, whitespace-normalized text:"
    )
    add_code(
        [
            "def normalize_text(text: str) -> str:",
            '    return re.sub(r"\\s+", " ", text.strip())',
            "",
            "def compute_cer(predictions, references) -> float:",
            "    return float(jiwer.cer(refs, preds))",
        ]
    )
    add(
        "summarize_errors() produces per-run substitution patterns for qualitative analysis, "
        "written to experiments/<run_id>/error_summary.json."
    )

    add("4.6.4 Batch Evaluation (evaluate.py)", style="Heading2")
    add(
        "run_evaluation() drives reproducible experiments from YAML configs. It supports two "
        "backends: trocr (batched TrOCR inference) and tesseract (classical OCR baseline). "
        "Each run writes:"
    )
    for item in [
        "metrics.json — corpus CER, WER, and sample count",
        "predictions.csv — per-line reference, prediction, and CER",
        "error_summary.json — top substitution patterns",
        "config.json — frozen run configuration for traceability",
    ]:
        add(item, style="ListBullet")
    add("Evaluation is invoked via:")
    add_code(["python3 scripts/run_eval.py --config configs/iam_trocr_handwritten.yaml"])

    add("4.7 Gradio Application (app/gradio_app.py)", style="Heading1")

    add("4.7.1 Interface Structure", style="Heading2")
    add("The web interface uses Gradio Blocks with these sections:")
    for item in [
        "Header: Title, architecture summary, and IAM benchmark CER (from experiments/ if available)",
        "Input panel: Image upload (PIL), optional ground-truth textbox, Recognize and Clear buttons",
        "Output panel: Recognized text and per-line CER when ground truth is supplied",
        "Examples gallery: Eight IAM English demo lines from data/iam/demo/",
        "Footer: Model and dataset attribution",
    ]:
        add(item, style="ListNumber")

    add("4.7.2 Recognition Handler", style="Heading2")
    add("The process_image callback delegates to the shared library:")
    add_code(
        [
            "def process_image(image, ground_truth: str):",
            "    text = recognize(image, TROCR_HANDWRITTEN)",
            "    if ground_truth and ground_truth.strip():",
            "        cer = compute_cer([text], [ground_truth])",
            "        return text, f'{cer:.4f}'",
            "    return text, 'Ground truth not provided'",
        ]
    )

    add("4.7.3 Example Data Loading", style="Heading2")
    add("Examples are loaded from a CSV manifest rather than paired .txt files:")
    add_code(
        [
            "def get_example_data(folder_path=EXAMPLES_DIR):",
            "    with open(labels_path, newline='', encoding='utf-8') as f:",
            "        for row in csv.DictReader(f):",
            "            examples.append([image_path, row['transcription']])",
            "    return examples",
        ]
    )

    add("4.8 Experiment Configuration", style="Heading1")
    add("Three YAML configs define the thesis experiment runs:")
    for item in [
        "configs/iam_trocr_handwritten.yaml — primary TrOCR result on IAM test (default 200 lines)",
        "configs/iam_demo.yaml — qualitative demo subset (8 lines)",
        "configs/iam_tesseract.yaml — Tesseract baseline on the same IAM test split",
    ]:
        add(item, style="ListBullet")
    add(
        "The default max_samples: 200 keeps CPU-only evaluation tractable. Removing max_samples "
        "evaluates the full 2,915-line IAM test split on a GPU machine. All experiment outputs "
        "are stored under experiments/<run_id>/ and referenced by the thesis results chapter."
    )

    add("4.9 Evaluation Metrics and Traceability", style="Heading1")
    add(
        "Every numeric result in the thesis must trace to experiments/<run_id>/metrics.json. "
        "Metrics follow the locked definitions in docs/RESEARCH_SCOPE.md:"
    )
    for item in [
        "Case-sensitive CER and WER",
        "Whitespace normalization (strip ends, collapse internal spaces)",
        "No lowercasing of transcriptions",
        "Corpus CER = total character edits / total reference characters",
    ]:
        add(item, style="ListBullet")
    add(
        "scripts/plot_results.py generates experiments/figures/cer_comparison.png comparing "
        "measured runs against cited literature baselines. scripts/fill_thesis_metrics.py "
        "injects measured values into the thesis rewrite guide."
    )

    add("4.10 Deployment Configuration", style="Heading1")
    add(
        "The Gradio app is launched with demo.launch() for local or server deployment. For VPS "
        "hosting (e.g. aaPanel), production settings bind to all interfaces and sit behind an "
        "Nginx reverse proxy with WebSocket support:"
    )
    add_code(
        [
            "demo.launch(server_name='0.0.0.0', server_port=7860)",
        ]
    )
    add(
        "A process manager (Supervisor) keeps the app running. The TrOCR model is downloaded "
        "from Hugging Face on first use and cached locally."
    )

    add("4.11 Performance Considerations", style="Heading1")
    for item in [
        "Model caching: LRU-cached ModelBundle avoids reloading weights on every request",
        "Batched evaluation: evaluate.py processes images in configurable batch sizes (default 8)",
        "Device selection: Automatic CUDA detection with CPU fallback",
        "Preprocessing: RGB conversion via TrOCRProcessor; no custom binarization",
        "Generation limit: max_new_tokens=128 caps decoder output length per line",
        "Graceful degradation: Missing demo data or Tesseract binary produces informative messages",
    ]:
        add(item, style="ListBullet")

    add("4.12 Integration with Research Framework", style="Heading1")
    add(
        "The implementation connects the thesis methodology to reproducible artifacts:"
    )
    for item in [
        "Research: YAML-driven batch evaluation with frozen outputs under experiments/",
        "Application: Shared recognize() and compute_cer() in the Gradio demo",
        "Traceability: Every claim maps to a file path (configs, scripts, metrics.json)",
        "Accessibility: Web UI for non-technical users to test English IAM line transcription",
    ]:
        add(item, style="ListBullet")
    add(
        "This design separates the research evaluation pipeline from the interactive demo while "
        "keeping a single source of truth for model loading, inference, and metrics — ensuring "
        "that application behaviour matches benchmark measurements."
    )

    body = "".join(parts)
    return (
        "<?xml version='1.0' encoding='UTF-8' standalone='yes'?>\n"
        f"<w:document {NS}>"
        f"<w:body>{body}<w:sectPr><w:pgSz w:w=\"12240\" w:h=\"15840\"/>"
        "<w:pgMar w:top=\"1440\" w:right=\"1440\" w:bottom=\"1440\" w:left=\"1440\" "
        "w:header=\"720\" w:footer=\"720\" w:gutter=\"0\"/></w:sectPr></w:body></w:document>"
    )


def rebuild_docx() -> None:
    if not DOCX_PATH.exists():
        raise FileNotFoundError(DOCX_PATH)

    new_xml = build_document_xml()

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        with zipfile.ZipFile(DOCX_PATH, "r") as zin:
            zin.extractall(tmp_path)
        (tmp_path / "word" / "document.xml").write_text(new_xml, encoding="utf-8")
        shutil.copy2(DOCX_PATH, DOCX_PATH.with_suffix(".docx.bak"))
        with zipfile.ZipFile(DOCX_PATH, "w", zipfile.ZIP_DEFLATED) as zout:
            for file_path in sorted(tmp_path.rglob("*")):
                if file_path.is_file():
                    zout.write(file_path, file_path.relative_to(tmp_path).as_posix())

    print(f"Updated {DOCX_PATH}")
    print(f"Backup: {DOCX_PATH.with_suffix('.docx.bak')}")


if __name__ == "__main__":
    rebuild_docx()
