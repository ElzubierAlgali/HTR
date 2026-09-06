# Thesis Rewrite Guide (English IAM only)

Aligned text for `Enhancing Handwritten Text Recognition Using Transformer Models Derived from Large Language Models.docx`.

**Rule:** Replace `METRIC` placeholders (`run_id.field`) with values from `experiments/<run_id>/metrics.json` after running evaluations. Primary claims use full-test E1–E3 only.

---

## Abstract (replace empty abstract)

Handwritten text recognition (HTR) remains challenging due to variability in writing styles. This thesis evaluates **pretrained and fine-tuned TrOCR** models—combining a **Vision Transformer (ViT) encoder** with a **BART text decoder**—on the **English IAM Handwriting Database** benchmark (full test, n=2,915). We implement a reproducible pipeline measuring Character Error Rate (CER) and Word Error Rate (WER), fine-tune TrOCR on IAM, train a CRNN+CTC baseline, and contextualize results against published HTR literature. A Gradio web application demonstrates English line transcription. Primary pretrained IAM result: CER **4.72%** (n=2915); fine-tuned: CER **4.96%** (slightly higher; reported as a negative/neutral finding). This work contributes an aligned research-and-application pipeline rather than a novel architecture.

---

## Chapter 1 — Key replacements

### Remove entirely
- References to GPT-3, BERT, GPT-2, XLNet as implemented models
- Bullinger, Latin, German, historical documents
- Medical prescription as primary objective
- Custom attention / positional encoding objectives
- CTC as **TrOCR** training loss (CTC is used only for CRNN)
- Results/conclusions in methodology sections
- Claims that fine-tuning improved CER (it did not under the logged run)

### Replace problem statement (concise)

> This research addresses **English** handwritten text recognition for line images using transformer-based models, evaluated on the IAM Handwriting Database benchmark.

### Replace objectives

1. Review HTR methods with emphasis on transformer architectures (TrOCR).
2. Implement a reproducible IAM train/eval pipeline (CER/WER).
3. Evaluate pretrained and fine-tuned `microsoft/trocr-base-handwritten` on full IAM English test data (n=2,915).
4. Compare against a CRNN+CTC baseline and published IAM literature figures (protocol may differ).
5. Deploy a web application for English IAM line transcription.

### Replace scope

> English line-level HTR on IAM (6,482 train / 976 validation / 2,915 test lines from Teklia/IAM-line). Includes TrOCR fine-tuning and CRNN+CTC baseline training; primary measured results use the full test split (E1–E3). Tesseract is optional when installed. Demo metrics are qualitative only.

---

## Chapter 2 — Literature table fix (TrOCR row)

| Tools & Techniques |
|--------------------|
| ViT image encoder + BART text decoder; pretrained vision and language components |

---

## Chapter 3 — Methodology (design only)

See `docs/CHAPTER_3_METHODOLOGY.md`. Academic prose; no result numbers.

Structure:
- 3.1 Introduction
- 3.2 Dataset (Table 3.1; Figure 3.1)
- 3.3 Preprocessing
- 3.4 Model selection (TrOCR / CRNN+CTC / optional Tesseract; Figure 3.2)
- 3.5 Experiment design and evaluation metrics (Table 3.2)
- 3.6 Comparative framework
- 3.7 Scope of the chapter

---

## Chapter 4 — Implementation and Results

See `docs/CHAPTER_4_IMPLEMENTATION_RESULTS.md` (filled: `docs/CHAPTER_4_IMPLEMENTATION_RESULTS_FILLED.md`).

Structure:
- 4.1 Purpose and contribution of the chapter
- 4.2 Implementation overview (Table 4.1 — roles, not software docs)
- 4.3 Experimental procedure (fine-tune / CRNN / evaluation matrix)
- 4.4 Results (Table 4.2 primary; Table 4.3 literature context; Figure 4.1)
- 4.5 Discussion and analysis (pretrained success; fine-tune neutral/negative; CRNN gap; errors; limitations)
- 4.6 Application prototype
- 4.7 Reproducibility statement

### Measured runs (populate from experiments)

| Run | CER | WER | n | Role |
|-----|-----|-----|---|------|
| Pretrained TrOCR | 4.72% | 11.64% | 2915 | Primary |
| Fine-tuned TrOCR | 4.96% | 12.46% | 2915 | Primary (no gain vs Hub) |
| CRNN+CTC | 81.82% | 96.56% | 2915 | Weak neural baseline |
| Tesseract | [skipped: Tesseract binary not installed (sudo apt install tesseract-ocr)] | [skipped: Tesseract binary not installed (sudo apt install tesseract-ocr)] | [skipped: Tesseract binary not installed (sudo apt install tesseract-ocr)] | Optional / may be skipped |
| Demo | 100.00% [SMOKE—not primary] | 100.00% [SMOKE—not primary] | 4 | Application only — not primary |

### Literature comparison (cited, not estimated)

| Method | CER (IAM) | Source |
|--------|-----------|--------|
| TrOCR pretrained (this work) | 4.72% | experiments/ |
| TrOCR fine-tuned (this work) | 4.96% | experiments/ |
| AttentionHTR | 6.50% | Kass & Vats, 2022 |
| Light Transformer | 5.70% | Barrère et al., 2022 |
| GFCN | 7.99% | Coquenet et al., 2020 |

Figure: `experiments/figures/cer_comparison.png`

---

## Chapter 5 — Conclusion

See `docs/CHAPTER_5_CONCLUSION.md` (filled: `docs/CHAPTER_5_CONCLUSION_FILLED.md`).

Academic conclusion structure:
- 5.1 Revisiting the research aim
- 5.2 Principal findings (Table 5.1; pretrained CER **4.72%**; fine-tune **4.96%** as neutral/negative finding; CRNN **81.82%**)
- 5.3 Contributions of the study
- 5.4 Limitations of the study
- 5.5 Recommendations for future research
- 5.6 Concluding remarks

---

## Title suggestion (optional)

*Enhancing Handwritten Text Recognition Using Pretrained Transformer Models: An English IAM Benchmark and Web Application*
