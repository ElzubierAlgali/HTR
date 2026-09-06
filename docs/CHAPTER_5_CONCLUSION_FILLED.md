# Chapter 5 — Conclusion

Metric tokens are filled by `scripts/fill_thesis_metrics.py` from `experiments/<run_id>/metrics.json`. Voice and register follow `docs/WRITING_STYLE.md`.

## 5.1 Revisiting the research aim

This thesis set out to establish how well a transformer-based handwritten text recognition (HTR) model performs on a standard English benchmark when it is evaluated under a transparent and locally reproducible protocol. The central question was practical as much as scientific. Given a widely used pretrained TrOCR checkpoint, pairing a Vision Transformer (ViT) image encoder with a BART text decoder, what recognition quality is obtainable on the IAM Handwriting Database, and does further fine-tuning on the official IAM splits produce a measurable gain? Two subsidiary questions followed. How does such a model compare with a conventional neural sequence baseline (CRNN with CTC) and with a classical OCR engine (Tesseract) under identical test conditions? And how can the resulting system be presented as an interactive application?

The investigation was scoped narrowly. It covers English line-level recognition on IAM, with Character Error Rate (CER) and Word Error Rate (WER) as the primary metrics. No new network architecture was proposed. The goal was instead a single aligned workflow running from data preparation through training and evaluation to a working demonstration, with each stage logged and the outcomes reported with academic care.

## 5.2 Principal findings

The experiments were conducted on the full IAM English test partition of 2,915 line images. Table 5.1 summarises the main quantitative outcomes. Demo-subset and smoke metrics are excluded from it.

**Table 5.1 — Measured outcomes on the full IAM English test set**

| Method | CER | WER | n |
|--------|-----|-----|---|
| TrOCR pretrained | 4.72% | 11.64% | 2915 |
| TrOCR fine-tuned | 4.96% | 12.46% | 2915 |
| CRNN+CTC | 81.82% | 96.56% | 2915 |
| Tesseract | 56.33% | 91.35% | 2915 |

The strongest result came from the pretrained TrOCR model, which reached a CER of 4.72% and a WER of 11.64%. A publicly available transformer HTR checkpoint can therefore deliver competitive line-level recognition on IAM, provided it is assessed on the complete test split rather than a reduced sample.

Fine-tuning on the IAM training and validation sets completed successfully and the run was documented in full. Under the logged schedule, however, the adapted model did not surpass the Hub checkpoint on the held-out test set. Its CER rose slightly to 4.96%, with a WER of 12.46%. Early stopping halted training after three epochs once validation CER ceased to improve. The outcome is informative rather than disappointing. The base checkpoint is already specialised for English handwriting, so the remaining margin is narrow, and a short adaptation run with a small micro-batch may in any case be insufficient to unlock further gains. Fine-tuning is best read as a completed experimental intervention whose measured effect was neutral to slightly adverse, not as an automatic route to higher accuracy.

The CRNN+CTC baseline, trained from scratch on the same splits, produced a markedly higher CER of 81.82%. That figure reflects a lightweight CNN, BiLSTM and CTC reference with constrained input geometry. It is not a claim about the best achievable CTC system. The contrast does nevertheless underline the advantage of large-scale pretrained transformers under matched data and metrics.

Classical Tesseract, evaluated in line mode on the identical full test partition, yielded a CER of 56.33% and a WER of 91.35%. As a general-purpose OCR engine without handwriting-specific adaptation, it remained far behind TrOCR, completing the baseline triad set out in the methodology.

Published IAM figures from related studies were cited for contextual scale only. Those works may differ in preprocessing, decoding, or split definitions, so no matched state-of-the-art ranking is asserted here.

Inspection of the high-error lines showed that short references, punctuation-heavy strings, and rare or hyphenated tokens remain difficult even when corpus-level CER is low. The Gradio demonstration showed that the same recognition stack can be exposed for interactive use. Its demo-subset scores count as application evidence only and do not enter the primary result tables.

## 5.3 Contributions of the study

Within the limits of a master's project, the contributions are as follows.

The first is a coherent English IAM evaluation protocol, under which pretrained TrOCR, fine-tuned TrOCR, CRNN+CTC, and Tesseract are all assessed on the identical full test partition with shared metric definitions. The second is a fully documented end-to-end fine-tuning experiment, covering learning rate, batching strategy, early stopping, and wall-clock cost, so that the adaptation step is reproducible and open to scrutiny. The third is the reporting of a negative or near-neutral fine-tuning outcome with the same clarity as a positive result, which strengthens the credibility of the empirical account. The fourth is the positioning of transformer performance against both a lightweight neural baseline and a classical OCR baseline, without overstating either comparator. The fifth is a lightweight web demonstration that places the recognition model in an applied setting while keeping demo behaviour separate from full-test evidence. Taken together these amount to an aligned research-and-application contribution rather than a claim of architectural novelty.

## 5.4 Limitations of the study

Several constraints qualify the findings. The work addresses English line images only; page-level layout analysis and multilingual handwriting fall outside its remit. The fine-tuning regime was short and early-stopped, and cannot be presented as an exhaustive search over optimisation choices. The CRNN baseline was kept simple by design. More elaborate neural sequence models might narrow the gap to TrOCR, but pursuing them would have drawn the study away from its transformer-centred question. Tesseract was run as a classical line-mode reference rather than as a handwriting-tuned specialist. Literature comparisons remain secondary and protocol-sensitive. Application metrics gathered on the small demo subset, including any smoke or synthetic checks, are illustrative and were never intended to replace full-test evaluation.

## 5.5 Recommendations for future research

Further work could pursue longer or more carefully regularised fine-tuning schedules, testing alternative learning-rate policies and larger effective batch sizes to determine whether the observed plateau can be overcome. Stronger neural baselines trained under the same IAM splits would sharpen the comparative picture beyond the lightweight CRNN used here. Beyond the line level, the pipeline could be extended towards page-level HTR, and the interface towards batch processing and structured error review, increasing both scientific reach and practical utility.

## 5.6 Concluding remarks

This study has shown that pretrained transformer-based HTR can be evaluated rigorously on the full English IAM test set within a transparent student research pipeline, attaining a CER of 4.72%. Additional fine-tuning was executed successfully, yet under the logged conditions it did not improve test recognition, and that finding is reported as measured. Neural and classical baselines place the result in comparative context, while the demonstration interface completes the applied thread of the project. The lasting value of the work lies in that measured alignment of method, experiment, and application, not in a claim of architectural novelty.
