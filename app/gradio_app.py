#!/usr/bin/env python3
"""Gradio demo for English IAM handwritten text recognition."""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

import gradio as gr

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from htr.infer import recognize
from htr.metrics import compute_cer
from htr.models import TROCR_HANDWRITTEN

EXAMPLES_DIR = REPO_ROOT / "data" / "iam" / "demo"
IAM_METRICS = REPO_ROOT / "experiments" / "iam_trocr_handwritten" / "metrics.json"


def _iam_cer_summary() -> str:
    if IAM_METRICS.exists():
        data = json.loads(IAM_METRICS.read_text(encoding="utf-8"))
        cer = data.get("cer", 0) * 100
        n = data.get("n_samples", "?")
        note = " (subset)" if n != 2915 else ""
        return f"IAM English benchmark: CER {cer:.2f}% (n={n}{note})"
    return "Run: python3 scripts/run_eval.py --config configs/iam_trocr_handwritten.yaml"


def get_example_data(folder_path: Path = EXAMPLES_DIR) -> list:
    labels_path = folder_path / "labels.csv"
    images_dir = folder_path / "images"
    if not labels_path.exists():
        return []

    examples = []
    with open(labels_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            image_path = images_dir / row["filename"]
            if image_path.exists():
                examples.append([str(image_path), row["transcription"]])
    return examples


def process_image(image, ground_truth: str):
    if image is None:
        return "", ""
    text = recognize(image, TROCR_HANDWRITTEN)
    if ground_truth and ground_truth.strip():
        cer = compute_cer([text], [ground_truth])
        return text, f"{cer:.4f}"
    return text, "Ground truth not provided"


with gr.Blocks(title="English Handwritten Text Recognition (IAM)") as demo:
    gr.HTML(
        f"""
        <div style="text-align:center;padding:1rem;">
            <h1>English Handwritten Text Recognition</h1>
            <p>TrOCR: Vision Transformer encoder + BART text decoder</p>
            <p><em>IAM Handwriting Database — English line images</em></p>
            <p style="font-size:0.9rem;color:#666;">{_iam_cer_summary()}</p>
        </div>
        """
    )

    with gr.Row():
        with gr.Column():
            input_image = gr.Image(type="pil", label="Upload English handwritten line")
            ground_truth = gr.Textbox(label="Ground truth (optional)", lines=2)
            btn_submit = gr.Button("Recognize", variant="primary")
            btn_clear = gr.Button("Clear")
        with gr.Column():
            output_text = gr.Textbox(label="Recognized text", lines=3)
            cer_output = gr.Textbox(label="Character Error Rate (CER)", lines=1)

    examples = get_example_data()
    if examples:
        gr.Examples(examples=examples, inputs=[input_image, ground_truth])
    else:
        gr.Markdown(
            "No demo examples found. Run: `python3 scripts/prepare_iam_demo_examples.py`"
        )

    gr.Markdown(
        """
        **Model:** `microsoft/trocr-base-handwritten` (English IAM pretrained TrOCR).
        **Dataset:** IAM Handwriting Database line images.
        """
    )

    btn_submit.click(process_image, inputs=[input_image, ground_truth], outputs=[output_text, cer_output])
    btn_clear.click(lambda: (None, "", "", ""), outputs=[input_image, output_text, ground_truth, cer_output])

if __name__ == "__main__":
    demo.launch()
