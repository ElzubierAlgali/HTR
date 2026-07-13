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


def _labeled(label: str, text: str) -> str:
    return (
        "<w:p>"
        f'<w:r><w:rPr><w:b/></w:rPr><w:t xml:space="preserve">{_text(label)} </w:t></w:r>'
        f"<w:r><w:t>{_text(text)}</w:t></w:r>"
        "</w:p>"
    )


def _code_block(lines: list[str]) -> str:
    runs = []
    for i, line in enumerate(lines):
        if i:
            runs.append("<w:br/>")
        space = ' xml:space="preserve"' if line.startswith(" ") or line == "" else ""
        runs.append(f"<w:t{space}>{_text(line)}</w:t>")
    return f"<w:p><w:r>{''.join(runs)}</w:r></w:p>"


def _tech(name: str, purpose: str, reason: str, usage: str, parts: list[str]) -> None:
    parts.append(_para(name, style="Heading2"))
    parts.append(_labeled("Purpose:", purpose))
    parts.append(_labeled("Reason for selection:", reason))
    parts.append(_labeled("Usage in this project:", usage))


def build_document_xml() -> str:
    parts: list[str] = []

    def add(text: str, style: str | None = None, center: bool = False) -> None:
        parts.append(_para(text, style=style, center=center))

    def add_code(lines: list[str]) -> None:
        parts.append(_code_block(lines))

    add("Chapter 4: Implementation", style="Title", center=True)

    # ------------------------------------------------------------------
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
    add(
        "Technology choices were guided by three principles: reproducibility (every result traces "
        "to a config file and an output artifact), interoperability (standard open-source ML "
        "libraries rather than custom frameworks), and separation of concerns (data preparation, "
        "model inference, metric computation, and user interface are implemented as distinct "
        "modules that can be tested and replaced independently)."
    )

    # ------------------------------------------------------------------
    add("4.2 Repository Structure", style="Heading1")
    add("The project is organized as follows:")
    for item in [
        "configs/: YAML experiment definitions (iam_trocr_handwritten, iam_demo, iam_tesseract)",
        "src/htr/: Shared library — models, inference, metrics, and batch evaluation",
        "scripts/: Data preparation, evaluation CLI, figure generation, and experiment runners",
        "app/gradio_app.py: Gradio web demo for English IAM line images",
        "data/iam/: IAM dataset exports (processed splits and demo examples)",
        "experiments/: Evaluation outputs (metrics.json, predictions.csv, figures)",
        "pyproject.toml / environment.yml: Dependency and environment specifications",
    ]:
        add(item, style="ListBullet")

    # ------------------------------------------------------------------
    add("4.3 Technology Stack — Detailed Overview", style="Heading1")
    add(
        "This section explains each technology used in the implementation, its purpose within "
        "the system, and the rationale for choosing it over alternatives. Dependencies are declared "
        "in pyproject.toml (pip install -e .) and environment.yml (conda alternative)."
    )

    _tech(
        "Python 3.9+ (recommended 3.10)",
        "Serves as the sole implementation language for data scripts, the shared HTR library, "
        "batch evaluation, and the Gradio web application.",
        "Python is the de facto standard for machine learning research and prototyping. Its "
        "ecosystem provides first-class support for PyTorch, Hugging Face Transformers, and "
        "Gradio — all required by this project. Version 3.9+ is mandated by pyproject.toml; "
        "Python 3.10 is specified in environment.yml for conda users because it balances stability "
        "with broad library compatibility.",
        "All modules under src/htr/, scripts/, and app/ are Python. The package is installed "
        "editable via pip install -e . so imports resolve consistently across scripts and the app.",
        parts,
    )

    _tech(
        "PyTorch (torch) and torchvision",
        "Provides the deep learning runtime: tensor operations, GPU acceleration, model loading, "
        "and autoregressive text generation during TrOCR inference.",
        "TrOCR and Hugging Face Transformers are built on PyTorch. PyTorch offers dynamic "
        "computation graphs, mature CUDA support, and direct integration with "
        "VisionEncoderDecoderModel. torchvision complements torch for image tensor handling. "
        "Alternatives such as TensorFlow or JAX were not chosen because the TrOCR checkpoint and "
        "processor are distributed through the Hugging Face PyTorch ecosystem.",
        "models.py loads weights with VisionEncoderDecoderModel.from_pretrained(), moves the model "
        "to cuda or cpu via model.to(device), and runs model.generate() inside torch.no_grad() "
        "during inference. evaluate.py uses torch.utils.data.DataLoader for batched evaluation.",
        parts,
    )

    _tech(
        "Hugging Face Transformers",
        "Supplies the TrOCR model architecture (VisionEncoderDecoderModel), the matched "
        "TrOCRProcessor (image preprocessing and text tokenization/decoding), and the standard "
        "from_pretrained() API for loading microsoft/trocr-base-handwritten.",
        "Implementing TrOCR from scratch would require replicating the ViT encoder, BART decoder, "
        "and tokenizer pipeline — hundreds of lines of error-prone code. Transformers provides "
        "battle-tested, paper-faithful implementations maintained by Microsoft and the open-source "
        "community. It also ensures that processor and model weights stay paired, which is critical "
        "for correct preprocessing and decoding.",
        "TrOCRProcessor.from_pretrained(checkpoint) loads both image_processor and text tokenizer. "
        "VisionEncoderDecoderModel.from_pretrained(checkpoint) loads encoder-decoder weights. Both "
        "are called in src/htr/models.py inside load_model_bundle().",
        parts,
    )

    _tech(
        "Hugging Face Hub (huggingface_hub)",
        "Handles automatic download, caching, and versioning of the TrOCR checkpoint and processor "
        "files from the Hugging Face model registry on first use.",
        "Storing large model weights (hundreds of megabytes) inside the Git repository is impractical. "
        "The Hub provides a reliable CDN-backed distribution channel with local disk caching, so "
        "the same checkpoint is fetched once and reused across evaluation runs and the Gradio app. "
        "sentencepiece (a Hub dependency for BART tokenization) is pulled transitively.",
        "When load_model_bundle() or from_pretrained() is first called, weights are downloaded to "
        "the local Hugging Face cache (~/.cache/huggingface/). Subsequent runs load from disk.",
        parts,
    )

    _tech(
        "TrOCR Architecture (ViT Encoder + BART Decoder)",
        "Performs the core handwritten text recognition task: encoding a line image into visual "
        "features and autoregressively decoding them into a text transcription.",
        "TrOCR (Li et al., 2021) is the state-of-the-art transformer approach for OCR/HTR and "
        "the focus of this thesis. The Vision Transformer (ViT) encoder captures spatial "
        "relationships in handwriting better than classical CNN feature extractors for this task. "
        "The BART decoder leverages pretrained language modelling to produce coherent word "
        "sequences. The checkpoint microsoft/trocr-base-handwritten is pretrained specifically on "
        "English IAM handwriting, making it the correct model for this benchmark without "
        "additional fine-tuning.",
        "The encoder processes RGB line images into pixel tensors. The decoder generates token IDs "
        "up to max_new_tokens=128, which are batch-decoded into strings in ModelBundle.generate_batch().",
        parts,
    )

    _tech(
        "Gradio (4.x)",
        "Provides the web-based user interface for the interactive HTR demo: image upload, "
        "transcription display, optional ground-truth CER feedback, and an examples gallery.",
        "Building a custom HTML/JavaScript frontend would add significant development overhead "
        "without improving research outcomes. Gradio is designed for ML demos: it handles file "
        "upload, image preview, event callbacks, and local/server deployment in a few lines of "
        "Python. It also supports Blocks API for structured layouts and integrates natively with "
        "PIL images returned by the inference pipeline.",
        "app/gradio_app.py defines a gr.Blocks interface with gr.Image, gr.Textbox, gr.Button, "
        "and gr.Examples components. The btn_submit.click handler calls process_image(), which "
        "delegates to recognize() and compute_cer() from src/htr/.",
        parts,
    )

    _tech(
        "Pillow (PIL)",
        "Loads, converts, and passes image data between the filesystem, Gradio upload widget, and "
        "the TrOCR image processor as RGB PIL Image objects.",
        "Pillow is the standard Python imaging library and the format expected by both Gradio "
        "(type='pil') and Hugging Face image processors. It handles PNG/JPEG decoding, colour space "
        "conversion (.convert('RGB')), and saving during the IAM data export pipeline. OpenCV was "
        "not used because TrOCR preprocessing is handled entirely by TrOCRProcessor and no custom "
        "computer-vision operations (binarization, deskewing) are applied in this implementation.",
        "infer.py converts all inputs to RGB via _load_image(). prepare_iam_lines.py saves IAM "
        "line images as PNG files. evaluate.py opens image paths with Image.open() before batching.",
        parts,
    )

    _tech(
        "jiwer",
        "Computes Character Error Rate (CER) and Word Error Rate (WER) using Levenshtein edit "
        "distance, aligned with standard HTR evaluation practice.",
        "CER and WER are the primary metrics defined in docs/RESEARCH_SCOPE.md. jiwer is a "
        "lightweight, well-tested library dedicated to speech and text recognition metrics. It was "
        "chosen over manual edit-distance implementations (error-prone) and over the Hugging Face "
        "evaluate library's CER metric because jiwer gives direct control over normalization and "
        "integrates cleanly with per-line and corpus-level aggregation. The evaluate package is "
        "listed in dependencies for compatibility but jiwer is the active metric backend.",
        "src/htr/metrics.py calls jiwer.cer() and jiwer.wer() after case-sensitive whitespace "
        "normalization. summarize_errors() uses jiwer.process_words() for alignment-based error "
        "pattern analysis. The Gradio app calls compute_cer() for live per-image feedback.",
        parts,
    )

    _tech(
        "Hugging Face datasets",
        "Downloads and loads the Teklia/IAM-line dataset with official train, validation, and test "
        "splits directly from the Hugging Face Hub.",
        "The IAM Handwriting Database is the thesis benchmark. The Teklia/IAM-line distribution "
        "on Hugging Face provides clean, pre-split line-level data with image and text columns, "
        "avoiding manual parsing of the original IAM XML/ASCII distribution. Using datasets ensures "
        "reproducible splits (6,482 / 976 / 2,915 lines) that match published benchmarks.",
        "scripts/download_iam.py calls load_dataset('Teklia/IAM-line') and exports each split to "
        "Parquet. scripts/prepare_iam_lines.py reloads Parquet (or streams from Hub) and writes "
        "per-split image folders and labels.csv files.",
        parts,
    )

    _tech(
        "Apache Parquet and PyArrow",
        "Stores raw IAM splits in a compact, columnar binary format between download and image export.",
        "Parquet is efficient for storing large image datasets with metadata columns: it compresses "
        "well, supports fast partial reads, and is the native serialization format of Hugging Face "
        "datasets. PyArrow provides the Python bindings required by datasets for Parquet I/O. "
        "Without this intermediate format, every data preparation run would re-download from the Hub.",
        "Downloaded splits are saved as data/iam/raw/iam_line_{split}.parquet. prepare_iam_lines.py "
        "reads these files with load_dataset('parquet', data_files=...) when available.",
        parts,
    )

    _tech(
        "pandas",
        "Supports tabular data handling in scripts that process dataset metadata and experiment "
        "outputs (alongside raw csv module usage in core evaluation).",
        "pandas is the standard Python tool for tabular data manipulation and is a transitive "
        "dependency of datasets and matplotlib workflows. It simplifies reading, filtering, and "
        "aggregating experiment tables when generating thesis figures and filled metric documents.",
        "Used in supporting scripts (plot_results.py, fill_thesis_metrics.py) and available "
        "throughout the environment for ad hoc analysis of predictions.csv files.",
        parts,
    )

    _tech(
        "PyYAML",
        "Defines experiment configurations in human-readable YAML files that specify run ID, model "
        "checkpoint, dataset split, batch size, sample limits, and backend type.",
        "Hard-coding experiment parameters in Python scripts makes reproduction difficult and "
        "error-prone. YAML configs separate what to run from how to run it: the same "
        "run_evaluation() function executes any experiment by reading a config file. This supports "
        "thesis traceability — each experiments/<run_id>/config.json is a frozen copy of the YAML "
        "used at run time.",
        "configs/iam_trocr_handwritten.yaml, iam_demo.yaml, and iam_tesseract.yaml are loaded by "
        "scripts/run_eval.py via yaml.safe_load() and mapped to an EvalConfig dataclass.",
        parts,
    )

    _tech(
        "Tesseract OCR and pytesseract",
        "Provides a classical, non-neural OCR baseline for comparison against TrOCR on the same "
        "IAM test split.",
        "A transformer-based result is only meaningful when compared against a traditional baseline "
        "on identical data. Tesseract 5.x is the most widely available open-source OCR engine. "
        "pytesseract is its Python wrapper, called from evaluate.py when backend: tesseract is set. "
        "If the Tesseract binary is not installed, the run is gracefully skipped and recorded in "
        "metrics.json with status: skipped — preserving pipeline reproducibility without blocking "
        "TrOCR experiments.",
        "evaluate.py calls pytesseract.image_to_string(image, config='--psm 7') for single-line "
        "mode on each IAM test image. configs/iam_tesseract.yaml sets backend: tesseract.",
        parts,
    )

    _tech(
        "matplotlib",
        "Generates publication-quality bar charts comparing measured CER results against literature "
        "baselines for the thesis results chapter.",
        "Visual comparison of TrOCR, Tesseract, and cited literature CER values is required for "
        "Chapter 4 (Results). matplotlib is the standard Python plotting library, produces "
        "high-DPI PNG output, and requires no external GUI — suitable for headless server execution "
        "during automated experiment pipelines.",
        "scripts/plot_results.py reads experiments/*/metrics.json, builds a CER bar chart including "
        "literature anchors (AttentionHTR, Light Transformer, GFCN), and saves "
        "experiments/figures/cer_comparison.png.",
        parts,
    )

    _tech(
        "setuptools and pyproject.toml (PEP 621)",
        "Packages the src/htr/ library as an installable Python project with declared dependencies "
        "and version metadata.",
        "Editable installation (pip install -e .) ensures that scripts, the Gradio app, and "
        "evaluation CLI all import from the same htr package without manual PYTHONPATH "
        "manipulation. pyproject.toml is the modern standard for Python project metadata, making "
        "dependency versions explicit and reproducible for thesis examiners and future contributors.",
        "pyproject.toml lists all runtime dependencies. setuptools discovers packages under src/ "
        "via [tool.setuptools.packages.find]. The project is installed once during setup.",
        parts,
    )

    _tech(
        "JSON and CSV (standard library + flat files)",
        "Persists experiment metrics, per-line predictions, error summaries, and dataset labels in "
        "human-readable, tool-agnostic formats.",
        "JSON is ideal for structured metric summaries (CER, WER, n_samples) that the thesis "
        "references by file path. CSV is ideal for per-line predictions that researchers can open "
        "in Excel or pandas for qualitative review. Both formats require no database server, align "
        "with the traceability rule in docs/RESEARCH_SCOPE.md, and remain readable years later.",
        "evaluate.py writes metrics.json, predictions.csv, error_summary.json, and config.json per "
        "run. prepare_iam_lines.py and prepare_iam_demo_examples.py write labels.csv. The Gradio "
        "header reads metrics.json for the benchmark CER summary.",
        parts,
    )

    _tech(
        "functools.lru_cache",
        "Caches loaded ModelBundle instances in memory so the TrOCR model is loaded once per "
        "checkpoint and reused across Gradio requests and repeated inference calls.",
        "Loading a transformer model from disk takes several seconds and hundreds of megabytes of "
        "RAM. Without caching, every Gradio button click would reload weights, making the demo "
        "unusable. lru_cache is a zero-dependency Python standard-library solution applied to "
        "_cached_bundle() in infer.py.",
        "recognize() calls _cached_bundle(checkpoint) which wraps load_model_bundle(). The first "
        "call loads weights; subsequent calls return the cached bundle immediately.",
        parts,
    )

    _tech(
        "Nginx and Supervisor (deployment stack)",
        "Nginx acts as a reverse proxy terminating HTTPS and forwarding traffic to the Gradio "
        "server; Supervisor keeps the Python process running across restarts.",
        "Gradio's built-in server is suitable for development but not for production exposure. "
        "Nginx provides SSL termination, domain routing, and WebSocket proxying (required by "
        "Gradio's live interface). Supervisor (or an equivalent process manager available in "
        "hosting panels such as aaPanel) ensures the app restarts after crashes or server reboots. "
        "These are deployment-layer technologies, not Python dependencies.",
        "Production deployment binds Gradio to 0.0.0.0:7860, proxies port 443 to 7860 via Nginx "
        "with Upgrade/Connection headers for WebSockets, and registers a Supervisor daemon for "
        "python3 app/gradio_app.py.",
        parts,
    )

    add(
        "Table 4.1 summarizes the technology stack. Each entry maps to a declared dependency in "
        "pyproject.toml or an architectural component described above.",
        style=None,
    )

    # ------------------------------------------------------------------
    add("4.4 Dataset Pipeline", style="Heading1")
    add(
        "English IAM line-level data is sourced from the Hugging Face dataset Teklia/IAM-line, "
        "which provides official train, validation, and test splits (6,482 / 976 / 2,915 lines)."
    )
    add("4.4.1 Download (scripts/download_iam.py)", style="Heading2")
    add(
        "Purpose: Fetch authoritative IAM splits from Hugging Face and cache them locally. "
        "Reason: Ensures the same benchmark splits used in published literature. "
        "Output: Parquet files under data/iam/raw/ and download_meta.json with split statistics."
    )
    add("4.4.2 Export (scripts/prepare_iam_lines.py)", style="Heading2")
    add(
        "Purpose: Convert Hub/Parquet records into per-line PNG images and labels.csv manifests. "
        "Reason: The evaluation pipeline (LineDataset) expects a folder of images plus a CSV, "
        "decoupling inference from Hugging Face APIs during experiments. "
        "Output: data/iam/processed/{train,val,test}/images/ and labels.csv."
    )
    add("4.4.3 Demo Examples (scripts/prepare_iam_demo_examples.py)", style="Heading2")
    add(
        "Purpose: Copy eight representative English test lines into data/iam/demo/ for the Gradio "
        "Examples gallery. Reason: Gives demo users immediate sample images without downloading "
        "the full IAM dataset. Output: data/iam/demo/images/ and labels.csv."
    )

    # ------------------------------------------------------------------
    add("4.5 Model Architecture and Checkpoint", style="Heading1")
    add(
        "The system uses TrOCR (Transformer-based Optical Character Recognition), consisting of:"
    )
    add(
        "Vision Encoder (ViT): Splits the line image into patches, applies self-attention, and "
        "produces a sequence of visual feature vectors.",
        style="ListNumber",
    )
    add(
        "Text Decoder (BART): Autoregressively predicts the next character/token given visual "
        "features and previously generated tokens, using cross-attention to the encoder output.",
        style="ListNumber",
    )
    add(
        "The checkpoint microsoft/trocr-base-handwritten is pretrained on English IAM handwriting. "
        "Processor and model weights are loaded as a matched pair from the same checkpoint. "
        "Evaluation-only scope: no fine-tuning is performed in this thesis; the pretrained weights "
        "are used directly, consistent with docs/RESEARCH_SCOPE.md."
    )

    # ------------------------------------------------------------------
    add("4.6 Core Library Components (src/htr/)", style="Heading1")

    add("4.6.1 Model Loading — models.py", style="Heading2")
    add(
        "Purpose: Centralize checkpoint validation, processor/model loading, device placement, and "
        "batched generation. Reason: Prevents the Gradio app and evaluation pipeline from "
        "duplicating Hugging Face boilerplate."
    )
    add_code(
        [
            "processor = TrOCRProcessor.from_pretrained(checkpoint)",
            "model = VisionEncoderDecoderModel.from_pretrained(checkpoint)",
            "model.to(device)",
            "model.eval()",
        ]
    )
    add(
        "ModelBundle dataclass exposes preprocess(), generate(), and generate_batch() methods. "
        "KNOWN_CHECKPOINTS restricts loading to vetted checkpoints only."
    )

    add("4.6.2 Inference — infer.py", style="Heading2")
    add(
        "Purpose: Provide a single-call recognize(image, checkpoint) API for scripts and the Gradio "
        "app. Reason: Decouples UI event handlers from model internals."
    )
    add_code(
        [
            "def recognize(image, checkpoint: str) -> str:",
            "    bundle = _cached_bundle(checkpoint)  # LRU-cached model load",
            "    pil_image = _load_image(image).convert('RGB')",
            "    return normalize_text(bundle.generate(pil_image))",
        ]
    )

    add("4.6.3 Metrics — metrics.py", style="Heading2")
    add(
        "Purpose: Implement thesis-aligned CER/WER and error summarization. Reason: One metrics "
        "module guarantees that benchmark numbers and live Gradio CER use identical normalization."
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

    add("4.6.4 Batch Evaluation — evaluate.py", style="Heading2")
    add(
        "Purpose: Run reproducible corpus-level experiments from YAML configs with trocr or "
        "tesseract backends. Reason: Separates one-off demo inference from systematic benchmark "
        "evaluation with frozen artifacts."
    )
    add("Invocation:")
    add_code(["python3 scripts/run_eval.py --config configs/iam_trocr_handwritten.yaml"])
    add("Each run produces metrics.json, predictions.csv, error_summary.json, and config.json.")

    # ------------------------------------------------------------------
    add("4.7 Gradio Application (app/gradio_app.py)", style="Heading1")
    add(
        "Purpose: Demonstrate the research model to non-technical users via a browser. "
        "Reason: Satisfies thesis objective 5 (deploy a web application) while reusing src/htr/ "
        "for identical inference behaviour."
    )
    add("4.7.1 Interface Structure", style="Heading2")
    for item in [
        "Header: Title, architecture summary, and IAM benchmark CER (from experiments/ if available)",
        "Input panel: Image upload (PIL), optional ground-truth textbox, Recognize and Clear buttons",
        "Output panel: Recognized text and per-line CER when ground truth is supplied",
        "Examples gallery: Eight IAM English demo lines from data/iam/demo/",
        "Footer: Model and dataset attribution",
    ]:
        add(item, style="ListNumber")

    add("4.7.2 Recognition Handler", style="Heading2")
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
    add(
        "Purpose: Populate gr.Examples from a CSV manifest. Reason: Scales to any number of demo "
        "lines without maintaining paired .txt files per image."
    )
    add_code(
        [
            "def get_example_data(folder_path=EXAMPLES_DIR):",
            "    with open(labels_path, newline='', encoding='utf-8') as f:",
            "        for row in csv.DictReader(f):",
            "            examples.append([image_path, row['transcription']])",
            "    return examples",
        ]
    )

    # ------------------------------------------------------------------
    add("4.8 Experiment Configuration", style="Heading1")
    for item in [
        "configs/iam_trocr_handwritten.yaml — primary TrOCR result on IAM test (default 200 lines)",
        "configs/iam_demo.yaml — qualitative demo subset (8 lines)",
        "configs/iam_tesseract.yaml — Tesseract baseline on the same IAM test split",
    ]:
        add(item, style="ListBullet")
    add(
        "max_samples: 200 keeps CPU-only evaluation tractable. Removing it evaluates all 2,915 "
        "test lines on a GPU machine. All outputs land in experiments/<run_id>/."
    )

    # ------------------------------------------------------------------
    add("4.9 Evaluation Metrics and Traceability", style="Heading1")
    for item in [
        "Case-sensitive CER and WER (jiwer, after whitespace normalization)",
        "No lowercasing of transcriptions",
        "Corpus CER = total character edits / total reference characters",
        "Every thesis number references experiments/<run_id>/metrics.json",
    ]:
        add(item, style="ListBullet")
    add(
        "scripts/plot_results.py and scripts/fill_thesis_metrics.py connect measured numbers to "
        "thesis prose and figures."
    )

    # ------------------------------------------------------------------
    add("4.10 Deployment Configuration", style="Heading1")
    add(
        "Purpose: Expose the Gradio demo on a VPS with HTTPS and process supervision. "
        "Reason: A locally running demo.launch() is insufficient for public thesis demonstration."
    )
    add_code(["demo.launch(server_name='0.0.0.0', server_port=7860)"])
    add(
        "Nginx reverse-proxies port 443 to 7860 with WebSocket headers. Supervisor restarts the "
        "Python process on failure. The TrOCR checkpoint is cached by Hugging Face Hub after first download."
    )

    # ------------------------------------------------------------------
    add("4.11 Performance Considerations", style="Heading1")
    for item in [
        "LRU-cached ModelBundle: avoids per-request model reload in the Gradio app",
        "Batched evaluation (default batch_size=8): amortizes GPU kernel launch overhead",
        "Automatic CUDA/CPU device selection: runs on laptops and servers alike",
        "RGB preprocessing via TrOCRProcessor: no extra binarization latency",
        "max_new_tokens=128: bounds decoder runtime per line",
        "Graceful degradation: missing Tesseract or demo data yields informative messages, not crashes",
    ]:
        add(item, style="ListBullet")

    # ------------------------------------------------------------------
    add("4.12 Integration with Research Framework", style="Heading1")
    add(
        "The technology stack is unified by a shared src/htr/ library: the same PyTorch model, "
        "jiwer metrics, and Pillow preprocessing drive both batch experiments and the live Gradio "
        "demo. YAML configs and JSON/CSV artifacts ensure every implementation claim in this "
        "chapter maps to a reproducible file path, satisfying the traceability requirements of "
        "the thesis methodology."
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
        backup = DOCX_PATH.with_suffix(".docx.bak")
        if not backup.exists():
            shutil.copy2(DOCX_PATH, backup)
        with zipfile.ZipFile(DOCX_PATH, "w", zipfile.ZIP_DEFLATED) as zout:
            for file_path in sorted(tmp_path.rglob("*")):
                if file_path.is_file():
                    zout.write(file_path, file_path.relative_to(tmp_path).as_posix())

    print(f"Updated {DOCX_PATH}")


if __name__ == "__main__":
    rebuild_docx()
