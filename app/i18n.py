"""English and Arabic UI strings for the Gradio demo."""

from __future__ import annotations

STRINGS: dict[str, dict[str, str]] = {
    "en": {
        "page_title": (
            "Enhancing Handwritten Text Recognition Using Pretrained Transformer Models: "
            "An English IAM Benchmark and Web Application"
        ),
        "university": "Sudan University of Science and Technology (SUST)",
        "research_title": (
            "Enhancing Handwritten Text Recognition Using Pretrained Transformer Models: "
            "An English IAM Benchmark and Web Application"
        ),
        "research_problem": (
            "English handwritten text recognition for line images using transformer-based models, "
            "evaluated on the IAM Handwriting Database benchmark."
        ),
        "research_scope": (
            "Evaluation-only study on IAM English line images "
            "(6,482 train / 976 validation / 2,915 test lines)."
        ),
        "lang_label": "Language / اللغة",
        "lang_en": "English",
        "lang_ar": "Arabic",
        "metric_cer": "CER",
        "metric_wer": "WER",
        "metric_samples": "Samples",
        "metric_model": "Model",
        "metric_model_value": "TrOCR IAM",
        "sidebar_overview": "Research overview",
        "sidebar_stack": "Technical stack",
        "sidebar_howto": "How to use",
        "howto_1": "Upload an English handwritten line image",
        "howto_2": "Optionally enter ground truth for CER",
        "howto_3": "Click <strong>Recognize</strong> or pick an example",
        "tag_vit": "ViT encoder",
        "tag_bart": "BART decoder",
        "tag_iam": "IAM dataset",
        "tag_gradio": "Gradio UI",
        "workspace": "Recognition workspace",
        "input_image": "Input image",
        "ground_truth": "Ground truth (optional)",
        "ground_truth_ph": "Enter reference transcription to compute CER…",
        "btn_recognize": "Recognize",
        "btn_clear": "Clear",
        "output_text": "Recognized text",
        "output_ph": "Transcription will appear here…",
        "cer_label": "Character Error Rate (CER)",
        "examples_section": "Example lines",
        "examples_label": "IAM English demo samples",
        "no_examples": (
            "No demo examples found. Run: `python3 scripts/prepare_iam_demo_examples.py`"
        ),
        "about_title": "About this thesis application",
        "about_body": (
            "This web demo supports the thesis **application objective**: interactive English IAM "
            "line transcription with optional ground-truth comparison.\n\n"
            "**Objectives demonstrated:**\n"
            "1. Pretrained TrOCR on English IAM line images\n"
            "2. Real-time transcription in the browser\n"
            "3. Per-line CER when ground truth is provided\n\n"
            "**Model:** `microsoft/trocr-base-handwritten` · "
            "**Dataset:** IAM Handwriting Database"
        ),
        "no_ground_truth": "Ground truth not provided",
    },
    "ar": {
        "page_title": (
            "تعزيز التعرف على النص المكتوب بخط اليد باستخدام نماذج المحولات المدربة مسبقاً: "
            "معيار IAM الإنجليزي وتطبيق ويب"
        ),
        "university": "جامعة السودان للعلوم والتكنولوجيا",
        "research_title": (
            "تعزيز التعرف على النص المكتوب بخط اليد باستخدام نماذج المحولات المدربة مسبقاً: "
            "معيار IAM الإنجليزي وتطبيق ويب"
        ),
        "research_problem": (
            "التعرف على النص الإنجليزي المكتوب بخط اليد على مستوى السطر باستخدام نماذج "
            "المحولات، مع التقييم على قاعدة بيانات IAM."
        ),
        "research_scope": (
            "دراسة تقييمية فقط على صور أسطر IAM الإنجليزية "
            "(6482 تدريب / 976 تحقق / 2915 اختبار)."
        ),
        "lang_label": "Language / اللغة",
        "lang_en": "English",
        "lang_ar": "Arabic",
        "metric_cer": "معدل خطأ الأحرف",
        "metric_wer": "معدل خطأ الكلمات",
        "metric_samples": "العينات",
        "metric_model": "النموذج",
        "metric_model_value": "TrOCR IAM",
        "sidebar_overview": "نظرة عامة على البحث",
        "sidebar_stack": "التقنيات المستخدمة",
        "sidebar_howto": "طريقة الاستخدام",
        "howto_1": "ارفع صورة سطر مكتوب بخط اليد بالإنجليزية",
        "howto_2": "أدخل النص المرجعي اختيارياً لحساب معدل خطأ الأحرف",
        "howto_3": "انقر <strong>تعرّف</strong> أو اختر مثالاً",
        "tag_vit": "مرمز ViT",
        "tag_bart": "فك BART",
        "tag_iam": "قاعدة IAM",
        "tag_gradio": "واجهة Gradio",
        "workspace": "مساحة التعرف",
        "input_image": "صورة الإدخال",
        "ground_truth": "النص المرجعي (اختياري)",
        "ground_truth_ph": "أدخل النص المرجعي لحساب معدل خطأ الأحرف…",
        "btn_recognize": "تعرّف",
        "btn_clear": "مسح",
        "output_text": "النص المتعرف عليه",
        "output_ph": "سيظهر النص هنا…",
        "cer_label": "معدل خطأ الأحرف (CER)",
        "examples_section": "أمثلة الأسطر",
        "examples_label": "عينات IAM الإنجليزية",
        "no_examples": (
            "لم يتم العثور على أمثلة. نفّذ: `python3 scripts/prepare_iam_demo_examples.py`"
        ),
        "about_title": "حول تطبيق الرسالة",
        "about_body": (
            "يدعم هذا العرض التوضيحي **هدف التطبيق** في الرسالة: نسخ أسطر IAM الإنجليزية "
            "بشكل تفاعلي مع مقارنة اختيارية بالنص المرجعي.\n\n"
            "**الأهداف المعروضة:**\n"
            "1. نموذج TrOCR المدرب مسبقاً على أسطر IAM الإنجليزية\n"
            "2. النسخ الفوري للنص في المتصفح\n"
            "3. حساب معدل خطأ الأحرف لكل سطر عند توفر النص المرجعي\n\n"
            "**النموذج:** `microsoft/trocr-base-handwritten` · **قاعدة البيانات:** IAM"
        ),
        "no_ground_truth": "لم يُقدَّم نص مرجعي",
    },
}


def t(lang: str, key: str) -> str:
    bundle = STRINGS.get(lang) or STRINGS["en"]
    return bundle.get(key, STRINGS["en"].get(key, key))


def is_rtl(lang: str) -> bool:
    return lang == "ar"
