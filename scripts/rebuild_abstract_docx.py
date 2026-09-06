#!/usr/bin/env python3
"""Build bilingual abstract DOCX (English + Arabic)."""

from __future__ import annotations

import json
import re
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.shared import Pt

REPO = Path(__file__).resolve().parents[1]
OUT = REPO / "docs" / "ABSTRACT.docx"
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

    # strip markdown bold markers for DOCX body
    text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
    return re.sub(r"\{\{METRIC:([^.]+)\.([^}]+)\}\}", repl, text)


def set_run_font(run, *, name: str = "Times New Roman", size: int = 12, rtl: bool = False) -> None:
    run.font.size = Pt(size)
    run.font.name = name
    r = run._element
    rPr = r.get_or_add_rPr()
    rFonts = rPr.get_or_add_rFonts()
    rFonts.set(qn("w:ascii"), name)
    rFonts.set(qn("w:hAnsi"), name)
    if rtl:
        rFonts.set(qn("w:cs"), "Traditional Arabic")
        run.font.name = "Traditional Arabic"


def add_ltr(doc: Document, text: str, *, bold: bool = False) -> None:
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    run = p.add_run(fill(text))
    set_run_font(run, name="Times New Roman", size=12)
    run.bold = bold


def add_rtl(doc: Document, text: str, *, bold: bool = False, size: int = 14) -> None:
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p.paragraph_format.right_to_left = True
    run = p.add_run(fill(text))
    set_run_font(run, name="Traditional Arabic", size=size, rtl=True)
    run.bold = bold


def main() -> None:
    doc = Document()

    doc.add_heading("Abstract", 0)
    add_ltr(
        doc,
        "Handwritten text recognition (HTR) remains challenging because writing styles vary "
        "so widely. This thesis evaluates pretrained and fine-tuned TrOCR models, which "
        "combine a Vision Transformer (ViT) encoder with a BART text decoder, on the English "
        "IAM Handwriting Database benchmark (full test, n=2,915). The study implements a "
        "reproducible pipeline measuring Character Error Rate (CER) and Word Error Rate "
        "(WER), fine-tunes TrOCR on IAM, trains a CRNN+CTC baseline, evaluates classical "
        "Tesseract on the same split, and sets the results against published HTR literature. "
        "A Gradio web application demonstrates English line transcription, qualitatively "
        "only. The primary pretrained IAM result is CER "
        "{{METRIC:iam_trocr_handwritten.cer}} "
        "(n={{METRIC:iam_trocr_handwritten.n_samples}}). After fine-tuning the CER is "
        "{{METRIC:iam_trocr_finetuned.cer}}, slightly higher, and is reported as a negative "
        "or neutral finding. The contribution is an aligned research-and-application "
        "pipeline rather than a novel architecture.",
    )
    add_ltr(doc, "Keywords: handwritten text recognition; TrOCR; transformers; IAM; CER; fine-tuning; CRNN; Tesseract")

    doc.add_heading("الملخص", 0)
    add_rtl(
        doc,
        "لا يزال التعرف على النص المكتوب بخط اليد (HTR) يمثل تحدياً بحثياً بسبب التباين الكبير "
        "في أساليب الكتابة. تقيّم هذه الرسالة نماذج TrOCR المدربة مسبقاً والمضبوطة دقيقاً، التي "
        "تجمع بين مُرمِّز Vision Transformer (ViT) ومُفكِّك نص BART، على معيار قاعدة بيانات "
        "IAM الإنجليزية لسطور الكتابة اليدوية (مجموعة الاختبار الكاملة، n=2,915). ويُنفَّذ خط "
        "أنابيب قابل لإعادة الإنتاج لقياس معدل خطأ الحروف (CER) ومعدل خطأ الكلمات (WER)، "
        "ويُضبَط نموذج TrOCR على بيانات IAM، ويُدرَّب خط أساس CRNN+CTC، ويُقيَّم محرك Tesseract "
        "الكلاسيكي على نفس التقسيم، وتُوضَع النتائج في سياق الأدبيات المنشورة في مجال HTR. كما "
        "يُقدَّم تطبيق ويب باستخدام Gradio لتوضيح نسخ السطور الإنجليزية (بصورة نوعية فقط). "
        "النتيجة الأساسية للنموذج المدرب مسبقاً هي CER {{METRIC:iam_trocr_handwritten.cer}} "
        "(n={{METRIC:iam_trocr_handwritten.n_samples}})؛ وبعد الضبط الدقيق يبلغ معدل خطأ "
        "الحروف {{METRIC:iam_trocr_finetuned.cer}} (أعلى قليلاً؛ ويُبلَّغ عنه بوصفه نتيجة "
        "سلبية/محايدة). وتسهم هذه الرسالة بخط أنابيب بحثي–تطبيقي متسق، لا بابتكار معمارية "
        "جديدة.",
    )
    add_rtl(
        doc,
        "الكلمات المفتاحية: التعرف على الكتابة اليدوية؛ TrOCR؛ المحوّلات؛ قاعدة بيانات IAM؛ "
        "معدل خطأ الحروف؛ الضبط الدقيق؛ CRNN؛ Tesseract",
        bold=True,
    )

    OUT.parent.mkdir(parents=True, exist_ok=True)
    doc.save(OUT)
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
