#!/usr/bin/env python3
"""Gradio demo for English IAM handwritten text recognition."""

from __future__ import annotations

import base64
import csv
import json
import sys
from pathlib import Path

import gradio as gr

REPO_ROOT = Path(__file__).resolve().parents[1]
APP_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(APP_DIR))

from htr.infer import recognize
from htr.metrics import compute_cer
from htr.models import TROCR_HANDWRITTEN
from i18n import is_rtl, t

EXAMPLES_DIR = REPO_ROOT / "data" / "iam" / "demo"
IAM_METRICS = REPO_ROOT / "experiments" / "iam_trocr_handwritten" / "metrics.json"
SUST_LOGO = REPO_ROOT / "app" / "assets" / "sust_logo.png"

CUSTOM_CSS = """
.gradio-container {
    max-width: 1200px !important;
    margin: auto !important;
}
#htr-header {
    background: linear-gradient(135deg, #0f2744 0%, #1e3a5f 55%, #2d4a6f 100%);
    border-radius: 12px;
    padding: 1.25rem 1.5rem;
    margin-bottom: 1rem;
    color: #ffffff !important;
}
#htr-header .header-inner {
    display: flex;
    align-items: center;
    gap: 1.25rem;
    flex-wrap: wrap;
}
#htr-header img {
    height: 64px;
    background: #fff;
    border-radius: 8px;
    padding: 6px 10px;
}
#htr-header .header-text { flex: 1; min-width: 240px; color: #ffffff !important; }
#htr-header .uni {
    margin: 0;
    font-size: 0.82rem;
    opacity: 0.95;
    letter-spacing: 0.04em;
    text-transform: uppercase;
    color: #ffffff !important;
}
#htr-header .title {
    margin: 0.35rem 0 0;
    font-size: 1.15rem;
    line-height: 1.4;
    font-weight: 700;
    color: #ffffff !important;
}
#htr-header p, #htr-header h1, #htr-header span {
    color: #ffffff !important;
}
#htr-header.rtl .header-inner { flex-direction: row-reverse; }
#htr-header.rtl .header-text { text-align: right; }
#htr-metrics {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
    gap: 0.65rem;
    margin-bottom: 1rem;
}
.metric-card {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    padding: 0.75rem 0.9rem;
    text-align: center;
}
.metric-card .label { font-size: 0.72rem; color: #64748b; text-transform: uppercase; letter-spacing: 0.05em; }
.metric-card .value { font-size: 1.15rem; font-weight: 700; color: #0f2744; margin-top: 0.15rem; }
.sidebar-card {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    padding: 1rem 1.1rem;
    height: 100%;
}
.sidebar-card h3 { margin: 0 0 0.65rem; font-size: 0.95rem; color: #0f2744; }
.sidebar-card p, .sidebar-card li { font-size: 0.88rem; color: #475569; line-height: 1.55; }
.sidebar-card ul { margin: 0.4rem 0 0; padding-left: 1.1rem; }
.sidebar-card.rtl { direction: rtl; text-align: right; }
.sidebar-card.rtl ul { padding-right: 1.1rem; padding-left: 0; }
.tag {
    display: inline-block;
    margin: 0.2rem 0.25rem 0.2rem 0;
    padding: 0.2rem 0.55rem;
    border-radius: 999px;
    font-size: 0.75rem;
    background: #e0e7ff;
    color: #1e3a8a;
}
.section-label {
    font-size: 0.78rem;
    font-weight: 600;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    color: #64748b;
    margin-bottom: 0.5rem;
}
.section-label.rtl { direction: rtl; text-align: right; }
.lang-row { justify-content: flex-end; margin-bottom: 0.5rem; }
"""


def _logo_data_uri() -> str | None:
    if not SUST_LOGO.exists():
        return None
    encoded = base64.b64encode(SUST_LOGO.read_bytes()).decode("ascii")
    return f"data:image/png;base64,{encoded}"


def _load_metrics() -> dict:
    if not IAM_METRICS.exists():
        return {}
    return json.loads(IAM_METRICS.read_text(encoding="utf-8"))


def _header_html(lang: str) -> str:
    logo = _logo_data_uri()
    logo_html = f'<img src="{logo}" alt="SUST logo" />' if logo else ""
    rtl_class = " rtl" if is_rtl(lang) else ""
    return f"""
    <div id="htr-header" class="{rtl_class.strip()}" style="color:#ffffff;">
        <div class="header-inner">
            {logo_html}
            <div class="header-text" style="color:#ffffff;">
                <p class="uni" style="color:#ffffff;margin:0;">{t(lang, "university")}</p>
                <p class="title" style="color:#ffffff;margin:0.35rem 0 0;">{t(lang, "research_title")}</p>
            </div>
        </div>
    </div>
    """


def _metrics_html(lang: str) -> str:
    data = _load_metrics()
    if not data or data.get("status") == "skipped":
        cer = wer = "—"
        n = "—"
    else:
        cer = f"{data.get('cer', 0) * 100:.2f}%"
        wer = f"{data.get('wer', 0) * 100:.2f}%"
        n = str(data.get("n_samples", "—"))

    return f"""
    <div id="htr-metrics">
        <div class="metric-card"><div class="label">{t(lang, "metric_cer")}</div><div class="value">{cer}</div></div>
        <div class="metric-card"><div class="label">{t(lang, "metric_wer")}</div><div class="value">{wer}</div></div>
        <div class="metric-card"><div class="label">{t(lang, "metric_samples")}</div><div class="value">{n}</div></div>
        <div class="metric-card"><div class="label">{t(lang, "metric_model")}</div><div class="value" style="font-size:0.78rem;">{t(lang, "metric_model_value")}</div></div>
    </div>
    """


def _sidebar_html(lang: str) -> str:
    rtl_class = " rtl" if is_rtl(lang) else ""
    return f"""
    <div class="sidebar-card{rtl_class}">
        <h3>{t(lang, "sidebar_overview")}</h3>
        <p>{t(lang, "research_problem")}</p>
        <p style="margin-top:0.65rem;">{t(lang, "research_scope")}</p>
        <h3 style="margin-top:1rem;">{t(lang, "sidebar_stack")}</h3>
        <span class="tag">{t(lang, "tag_vit")}</span>
        <span class="tag">{t(lang, "tag_bart")}</span>
        <span class="tag">{t(lang, "tag_iam")}</span>
        <span class="tag">{t(lang, "tag_gradio")}</span>
        <h3 style="margin-top:1rem;">{t(lang, "sidebar_howto")}</h3>
        <ul>
            <li>{t(lang, "howto_1")}</li>
            <li>{t(lang, "howto_2")}</li>
            <li>{t(lang, "howto_3")}</li>
        </ul>
    </div>
    """


def _section_label(lang: str, key: str) -> str:
    rtl = " rtl" if is_rtl(lang) else ""
    return f'<div class="section-label{rtl}">{t(lang, key)}</div>'


def _examples_section_html(lang: str) -> str:
    rtl = " rtl" if is_rtl(lang) else ""
    rtl_style = "text-align:right;direction:rtl;" if is_rtl(lang) else ""
    return (
        f'<div class="section-label{rtl}" style="margin-top:0.75rem;">'
        f'{t(lang, "examples_section")}</div>'
        f'<p style="font-size:0.85rem;color:#64748b;margin:0 0 0.5rem;{rtl_style}">'
        f'{t(lang, "examples_label")}</p>'
    )


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


def process_image(image, ground_truth: str, lang: str):
    if image is None:
        return "", ""
    text = recognize(image, TROCR_HANDWRITTEN)
    if ground_truth and ground_truth.strip():
        cer = compute_cer([text], [ground_truth])
        return text, f"{cer:.4f}"
    return text, t(lang, "no_ground_truth")


def apply_language(lang: str):
    return (
        gr.update(value=_header_html(lang)),
        gr.update(value=_metrics_html(lang)),
        gr.update(value=_sidebar_html(lang)),
        gr.update(value=_section_label(lang, "workspace")),
        gr.update(label=t(lang, "input_image")),
        gr.update(label=t(lang, "ground_truth"), placeholder=t(lang, "ground_truth_ph")),
        gr.update(value=t(lang, "btn_recognize")),
        gr.update(value=t(lang, "btn_clear")),
        gr.update(label=t(lang, "output_text"), placeholder=t(lang, "output_ph")),
        gr.update(label=t(lang, "cer_label")),
        gr.update(value=_examples_section_html(lang)),
        gr.update(value=t(lang, "about_body")),
    )


with gr.Blocks(title=t("en", "page_title")) as demo:
    with gr.Row(elem_classes=["lang-row"]):
        language = gr.Radio(
            choices=[("English", "en"), ("العربية", "ar")],
            value="en",
            label=t("en", "lang_label"),
            interactive=True,
        )

    header = gr.HTML(_header_html("en"))
    metrics = gr.HTML(_metrics_html("en"))

    with gr.Row(equal_height=True):
        with gr.Column(scale=1, min_width=260):
            sidebar = gr.HTML(_sidebar_html("en"))

        with gr.Column(scale=3):
            workspace_label = gr.Markdown(_section_label("en", "workspace"))

            with gr.Row():
                with gr.Column():
                    input_image = gr.Image(type="pil", label=t("en", "input_image"), height=280)
                    ground_truth = gr.Textbox(
                        label=t("en", "ground_truth"),
                        placeholder=t("en", "ground_truth_ph"),
                        lines=2,
                    )
                    with gr.Row():
                        btn_submit = gr.Button(t("en", "btn_recognize"), variant="primary", scale=2)
                        btn_clear = gr.Button(t("en", "btn_clear"), scale=1)

                with gr.Column():
                    output_text = gr.Textbox(
                        label=t("en", "output_text"),
                        lines=6,
                        placeholder=t("en", "output_ph"),
                    )
                    cer_output = gr.Textbox(label=t("en", "cer_label"), lines=1, placeholder="—")

    examples_label_md = gr.Markdown(_examples_section_html("en"))

    examples = get_example_data()
    if examples:
        gr.Examples(examples=examples, inputs=[input_image, ground_truth], label="")
    else:
        gr.Markdown(t("en", "no_examples"))

    with gr.Accordion(f'{t("en", "about_title")} / {t("ar", "about_title")}', open=False):
        about_body = gr.Markdown(t("en", "about_body"))

    language.change(
        apply_language,
        inputs=[language],
        outputs=[
            header,
            metrics,
            sidebar,
            workspace_label,
            input_image,
            ground_truth,
            btn_submit,
            btn_clear,
            output_text,
            cer_output,
            examples_label_md,
            about_body,
        ],
    )

    btn_submit.click(
        process_image,
        inputs=[input_image, ground_truth, language],
        outputs=[output_text, cer_output],
    )
    btn_clear.click(
        lambda: (None, "", "", ""),
        outputs=[input_image, output_text, ground_truth, cer_output],
    )

if __name__ == "__main__":
    demo.launch(css=CUSTOM_CSS, theme=gr.themes.Soft())
