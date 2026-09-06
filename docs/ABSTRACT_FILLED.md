# Abstracts — English & Arabic

Filled numbers come from `experiments/<run_id>/metrics.json` via `scripts/fill_thesis_metrics.py`. Voice and register follow `docs/WRITING_STYLE.md`.

## Abstract (English)

Handwritten text recognition (HTR) remains challenging because writing styles vary so widely. This thesis evaluates **pretrained and fine-tuned TrOCR** models, which combine a **Vision Transformer (ViT) encoder** with a **BART text decoder**, on the **English IAM Handwriting Database** benchmark (full test, n=2,915). The study implements a reproducible pipeline measuring Character Error Rate (CER) and Word Error Rate (WER), fine-tunes TrOCR on IAM, trains a CRNN+CTC baseline, evaluates classical Tesseract on the same split, and sets the results against published HTR literature. A Gradio web application demonstrates English line transcription, qualitatively only. The primary pretrained IAM result is CER **4.72%** (n=2915). After fine-tuning the CER is **4.96%**, slightly higher, and is reported as a negative or neutral finding. The contribution is an aligned research-and-application pipeline rather than a novel architecture.

**Keywords:** handwritten text recognition; TrOCR; transformers; IAM; CER; fine-tuning; CRNN; Tesseract

## الملخص

لا يزال التعرف على النص المكتوب بخط اليد (HTR) يمثل تحدياً بحثياً بسبب التباين الكبير في أساليب الكتابة. تقيّم هذه الرسالة نماذج **TrOCR** المدربة مسبقاً والمضبوطة دقيقاً، التي تجمع بين مُرمِّز **Vision Transformer (ViT)** ومُفكِّك نص **BART**، على معيار قاعدة بيانات **IAM** الإنجليزية لسطور الكتابة اليدوية (مجموعة الاختبار الكاملة، n=2,915). ويُنفَّذ خط أنابيب قابل لإعادة الإنتاج لقياس معدل خطأ الحروف (CER) ومعدل خطأ الكلمات (WER)، ويُضبَط نموذج TrOCR على بيانات IAM، ويُدرَّب خط أساس CRNN+CTC، ويُقيَّم محرك Tesseract الكلاسيكي على نفس التقسيم، وتُوضَع النتائج في سياق الأدبيات المنشورة في مجال HTR. كما يُقدَّم تطبيق ويب باستخدام Gradio لتوضيح نسخ السطور الإنجليزية (بصورة نوعية فقط). النتيجة الأساسية للنموذج المدرب مسبقاً هي CER **4.72%** (n=2915)؛ وبعد الضبط الدقيق يبلغ معدل خطأ الحروف **4.96%** (أعلى قليلاً؛ ويُبلَّغ عنه بوصفه نتيجة سلبية/محايدة). وتسهم هذه الرسالة بخط أنابيب بحثي–تطبيقي متسق، لا بابتكار معمارية جديدة.

### كلمات مفتاحية
التعرف على الكتابة اليدوية؛ TrOCR؛ المحوّلات؛ قاعدة بيانات IAM؛ معدل خطأ الحروف؛ الضبط الدقيق؛ CRNN؛ Tesseract
