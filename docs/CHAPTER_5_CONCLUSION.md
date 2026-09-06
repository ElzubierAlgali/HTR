# Chapter 5 — Conclusion

Metric tokens are filled by `scripts/fill_thesis_metrics.py` from `experiments/<run_id>/metrics.json`.

## 5.1 Revisiting the research aim

This thesis set out to examine how well a transformer-based handwritten text recognition (HTR) model performs on a standard English benchmark when evaluated under a transparent, locally reproducible protocol. The central question was practical as well as scientific: given a widely used pretrained TrOCR checkpoint with a Vision Transformer (ViT) image encoder and a BART text decoder, what recognition quality can be obtained on the IAM Handwriting Database, and does additional fine-tuning on the official IAM splits yield a measurable gain? The study also asked how such a model compares with a conventional neural sequence baseline (CRNN with CTC) under identical test conditions, and how the resulting system can be presented as an interactive application.

The investigation remained deliberately scoped. Attention was restricted to English line-level recognition on IAM, with Character Error Rate (CER) and Word Error Rate (WER) as primary metrics. The objective was not to propose a new network architecture, but to construct an aligned research workflow—data preparation, training, evaluation, logging, and demonstration—and to report its outcomes with academic care.

## 5.2 Principal findings

Experiments were conducted on the full IAM English test partition comprising 2,915 line images. The main quantitative outcomes are summarised in Table 5.1.

**Table 5.1 — Primary measured outcomes on the full IAM English test set**

| Method | CER | WER | n |
|--------|-----|-----|---|
| TrOCR pretrained | {{METRIC:iam_trocr_handwritten.cer}} | {{METRIC:iam_trocr_handwritten.wer}} | {{METRIC:iam_trocr_handwritten.n_samples}} |
| TrOCR fine-tuned | {{METRIC:iam_trocr_finetuned.cer}} | {{METRIC:iam_trocr_finetuned.wer}} | {{METRIC:iam_trocr_finetuned.n_samples}} |
| CRNN+CTC | {{METRIC:iam_crnn.cer}} | {{METRIC:iam_crnn.wer}} | {{METRIC:iam_crnn.n_samples}} |

The strongest and most consequential result is that of the pretrained TrOCR model, which achieved a CER of {{METRIC:iam_trocr_handwritten.cer}} and a WER of {{METRIC:iam_trocr_handwritten.wer}}. This confirms that a publicly available transformer HTR checkpoint can deliver competitive line-level recognition on IAM when evaluated carefully on the complete test split rather than on a reduced sample.

Fine-tuning on the IAM training and validation sets was completed successfully and is fully documented. Under the logged schedule, however, the adapted model did not surpass the Hub checkpoint on the held-out test set: the fine-tuned CER rose slightly to {{METRIC:iam_trocr_finetuned.cer}} (WER {{METRIC:iam_trocr_finetuned.wer}}). Early stopping interrupted training after three epochs once validation CER ceased to improve. In a master’s research setting this outcome is informative rather than disappointing. Because the base checkpoint is already specialised for English handwriting, the remaining margin for improvement is narrow; a short adaptation run with a small micro-batch may also be insufficient to unlock further gains. The thesis therefore treats fine-tuning as a completed experimental intervention whose measured effect was neutral to slightly adverse, not as an automatic route to superior accuracy.

The CRNN+CTC baseline, trained from scratch on the same splits, produced a markedly higher CER of {{METRIC:iam_crnn.cer}}. The contrast underscores the advantage of large-scale pretrained transformer models relative to a compact CNN–BiLSTM–CTC system with constrained input geometry. The baseline remains useful as a controlled reference; it should not be interpreted as an optimised competitor to TrOCR.

Classical OCR via Tesseract was retained in the experimental design where the runtime environment permitted it. When the binary was unavailable, the run was recorded as skipped rather than imputed. Published IAM figures from related studies were cited only for contextual scale. Because those works may differ in preprocessing, decoding, or split definitions, the present thesis refrains from asserting a matched state-of-the-art ranking.

Qualitative inspection of high-error lines suggested that short references, punctuation-heavy strings, and rare or hyphenated tokens remain difficult cases even when corpus-level CER is low. The Gradio demonstration illustrated that the same recognition stack can be exposed for interactive use, thereby linking the experimental pipeline to a tangible research application.

## 5.3 Contributions of the study

Within the limits of a master’s project, the contributions may be stated as follows.

First, the work provides a coherent English IAM evaluation protocol in which pretrained TrOCR, fine-tuned TrOCR, and a CRNN+CTC baseline are assessed on the identical full test partition with shared metric definitions. Second, it documents an end-to-end fine-tuning experiment—including learning rate, batching strategy, early stopping, and wall-clock cost—so that the adaptation step is reproducible and open to scrutiny. Third, it reports a negative or near-neutral fine-tuning outcome with equal clarity to positive results, which strengthens the credibility of the empirical narrative. Fourth, it delivers a lightweight web demonstration that situates the recognition model in an applied setting without confusing demo behaviour with full-test evidence. Collectively, these elements constitute an aligned research-and-application contribution rather than an architectural novelty claim.

## 5.4 Limitations of the study

Several constraints qualify the interpretation of the findings. The study addresses English line images only; page-level layout analysis and multilingual handwriting lie outside its remit. The fine-tuning regime was comparatively short and early-stopped, and therefore cannot be read as an exhaustive search over optimisation choices. The CRNN baseline was intentionally simple; more elaborate neural sequence models might narrow the gap to TrOCR, but exploring them would have diverted the project from its transformer-centred question. Literature comparisons remain secondary and protocol-sensitive. Finally, application metrics collected on a small demo subset are illustrative and were never intended to replace full-test evaluation.

## 5.5 Recommendations for future research

Future work could pursue longer or more carefully regularised fine-tuning schedules, including alternative learning-rate policies and larger effective batch sizes, to test whether the observed plateau can be overcome. Stronger neural baselines trained under the same IAM splits would sharpen the comparative picture. Where system dependencies allow, completing the classical Tesseract evaluation would restore the full baseline triad envisaged in the methodology. Beyond the line level, extending the pipeline toward page-level HTR and richer interactive tooling—such as batch processing and structured error review—would increase both scientific reach and practical utility.

## 5.6 Concluding remarks

In closing, the thesis demonstrates that pretrained transformer-based HTR can be evaluated rigorously on the full English IAM test set within a transparent student research pipeline, attaining a CER of {{METRIC:iam_trocr_handwritten.cer}}. Additional fine-tuning, although successfully executed, did not improve test recognition under the logged conditions and is reported accordingly. The accompanying baseline and demonstration complete a modest but consistent academic contribution: an evidence-based account of what a contemporary pretrained HTR model achieves on IAM, what adaptation did and did not change, and how such a system can be presented for use. The enduring value of the work lies in that measured alignment of method, experiment, and application.
