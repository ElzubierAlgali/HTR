# Chapter 4 — Implementation and Results

Metric tokens are filled by `scripts/fill_thesis_metrics.py` from `experiments/<run_id>/metrics.json`. Training details are taken from the corresponding `train_log.json` files. Voice and register follow `docs/WRITING_STYLE.md`.

## 4.1 Purpose and contribution of the chapter

Chapter 3 defined the research design. This chapter reports how that design was realised and what it produced. The contribution is an aligned research-and-application study rather than the invention of a new HTR architecture. It consists of four parts. A reproducible English IAM training and evaluation workflow was implemented. TrOCR was fine-tuned on the official training and validation partitions, with the run logged in full. The transformer was then compared against a CRNN+CTC neural baseline and classical Tesseract on the identical full test set of 2,915 lines. Finally, an interactive demonstration places the recogniser in an applied setting. Published IAM CER figures are cited for contextual scale, without any claim of protocol-identical superiority.

## 4.2 Implementation overview

The implementation follows the methodological commitments of Chapter 3. Dataset handling loads line images and transcriptions for training and evaluation. Model utilities instantiate either the public TrOCR checkpoint or the locally fine-tuned directory for generation. A training routine adapts TrOCR with cross-entropy, AdamW, and early stopping on validation CER, while a separate module trains and evaluates the CRNN+CTC baseline. Shared metric code computes case-sensitive CER and WER. Evaluation runners execute the experiment matrix, and a Gradio interface exposes recognition for interactive demonstration. Detailed module listings sit in the appendix so that this chapter can stay focused on scientific substance rather than software documentation.

**Table 4.1 — Principal implementation components**

| Component | Role in the study |
|-----------|-------------------|
| Dataset I/O | Provides line images and transcriptions for train/eval |
| TrOCR loading and generation | Instantiates Hub or local checkpoints for inference |
| TrOCR fine-tuning | Adapts the pretrained model on IAM train/val |
| CRNN+CTC baseline | Trains and evaluates the neural reference system |
| Metrics | Computes CER and WER under a shared definition |
| Evaluation runners | Executes the designed experiment matrix |
| Demonstration interface | Supports interactive English line transcription |

## 4.3 Experimental procedure

### 4.3.1 TrOCR fine-tuning

Fine-tuning began from `microsoft/trocr-base-handwritten` on the full IAM training and validation sets of 6,482 and 976 lines. Optimisation used AdamW with a learning rate of \(5 \times 10^{-6}\), a micro-batch size of 1, and gradient accumulation of 8, giving an effective batch size of 8. A maximum of eight epochs was planned, with early-stopping patience of two validations. Training ran on CUDA, and the logged wall-clock time was approximately 88.7 hours.

Under this schedule, validation CER reached its best value of 0.0137 after the first epoch and then deteriorated, to 0.0162 in epoch 2 and 0.0187 in epoch 3. Early stopping therefore terminated training after three epochs, and the exported model corresponds to the best validation checkpoint rather than the final epoch weights. This behaviour matters for interpretation. The adaptation run completed and was logged in full, yet it showed no sustained validation improvement.

### 4.3.2 CRNN+CTC training

The CRNN baseline was trained from scratch on the same IAM partitions with a learning rate of \(1 \times 10^{-3}\), batch size 8, and fixed input geometry of \(32 \times 128\). Eight epochs ran under early-stopping patience, with a character set of size 79. Best validation CER remained high at approximately 0.80, which already signalled limited competitiveness relative to pretrained TrOCR before any test evaluation.

### 4.3.3 Evaluation matrix

Evaluation followed the design of Chapter 3. The measured full-test claims rest on pretrained TrOCR (E1), fine-tuned TrOCR (E2), CRNN+CTC (E3), and Tesseract (E4), each assessed on the identical IAM test split of 2,915 lines. The demonstration run (E5) supports the application section only. It is qualitative, may use a tiny demo subset, and never serves as a primary CER source.

## 4.4 Results

Table 4.2 reports the measured full-test outcomes. Demo and smoke scores are omitted from it by design.

**Table 4.2 — Measured results on the full IAM English test set**

| Method | CER | WER | n |
|--------|-----|-----|---|
| TrOCR pretrained | {{METRIC:iam_trocr_handwritten.cer}} | {{METRIC:iam_trocr_handwritten.wer}} | {{METRIC:iam_trocr_handwritten.n_samples}} |
| TrOCR fine-tuned | {{METRIC:iam_trocr_finetuned.cer}} | {{METRIC:iam_trocr_finetuned.wer}} | {{METRIC:iam_trocr_finetuned.n_samples}} |
| CRNN+CTC | {{METRIC:iam_crnn.cer}} | {{METRIC:iam_crnn.wer}} | {{METRIC:iam_crnn.n_samples}} |
| Tesseract | {{METRIC:iam_tesseract.cer}} | {{METRIC:iam_tesseract.wer}} | {{METRIC:iam_tesseract.n_samples}} |

The pretrained transformer attained a CER of {{METRIC:iam_trocr_handwritten.cer}} and a WER of {{METRIC:iam_trocr_handwritten.wer}}. After fine-tuning, the measured values were CER {{METRIC:iam_trocr_finetuned.cer}} and WER {{METRIC:iam_trocr_finetuned.wer}}, slightly worse than the Hub checkpoint under the logged early-stopped schedule. The lightweight CRNN+CTC baseline produced CER {{METRIC:iam_crnn.cer}} and WER {{METRIC:iam_crnn.wer}}. Classical Tesseract, run in line mode on the same split, produced CER {{METRIC:iam_tesseract.cer}} and WER {{METRIC:iam_tesseract.wer}}.

**Figure 4.1 — CER comparison.** Measured CER values for the systems evaluated in this thesis, with selected literature figures shown separately for contextual comparison.

**Table 4.3 — Literature CER figures cited for context**

| Method | CER (IAM) | Source |
|--------|-----------|--------|
| AttentionHTR | 6.50% | Kass & Vats, 2022 |
| Light Transformer | 5.70% | Barrère et al., 2022 |
| GFCN | 7.99% | Coquenet et al., 2020 |

These published values are cited only to locate the present scores within the broader IAM literature. Those systems were not re-implemented under the preprocessing and split conventions used here, so no matched state-of-the-art ranking is asserted.

## 4.5 Discussion and analysis

### 4.5.1 Pretrained TrOCR as the principal empirical result

The pretrained TrOCR evaluation is the central positive finding of the study. A CER of {{METRIC:iam_trocr_handwritten.cer}} on 2,915 previously unseen IAM lines shows that a publicly released transformer HTR checkpoint can deliver strong line-level recognition when assessed under a complete and transparent local protocol. For a master's investigation concerned with transfer learning rather than architectural invention, the result is scientifically meaningful. It establishes what current pretrained models already achieve before any student-led adaptation is attempted.

### 4.5.2 Interpretation of the fine-tuning outcome

Fine-tuning did not improve test recognition. The adapted model's CER of {{METRIC:iam_trocr_finetuned.cer}} is slightly higher than that of the Hub checkpoint. Three considerations make the outcome intelligible. First, the starting checkpoint is already specialised for English handwriting, so residual headroom on IAM is limited. Second, validation CER worsened after the first epoch, and early stopping rightly preferred the earlier checkpoint; continued training under the logged schedule was not justified by the validation signal. Third, the optimisation used a small micro-batch with gradient accumulation, which is adequate for a feasibility study but may be suboptimal for extracting further gains. Fine-tuning is therefore best read as an experiment that was executed and measured, whose effect under these conditions was neutral to slightly adverse. It is neither proof that adaptation is universally unhelpful nor evidence of a failed run.

### 4.5.3 The CRNN+CTC baseline in perspective

The CRNN+CTC system's CER of {{METRIC:iam_crnn.cer}} confirms a substantial gap relative to TrOCR under matched data and metrics. That gap needs careful reading. The baseline is a compact CNN, BiLSTM and CTC model trained from scratch with fixed \(32 \times 128\) geometry, designed to be lightweight rather than competitive, and it is not presented as an optimised neural HTR system. Its role is comparative anchoring. The large error rate illustrates the advantage of large-scale pretrained transformers in this setting; it does not imply that every CTC architecture would fail equally.

### 4.5.4 Classical Tesseract as a reference baseline

Tesseract served as a classical OCR point of comparison on the same full test partition, yielding CER {{METRIC:iam_tesseract.cer}} and WER {{METRIC:iam_tesseract.wer}}. The gap to pretrained TrOCR is large, as expected when a general-purpose OCR engine is applied to unconstrained handwriting line images without handwriting-specific adaptation. The result strengthens the case for transformer HTR while remaining modest in claim. Tesseract is a classical reference here, not a tuned handwriting specialist.

### 4.5.5 Error behaviour and qualitative observations

Inspection of high-CER predictions revealed recurring difficulties with very short references, punctuation-dominated or dash-like strings, and rare or hyphenated tokens. Such lines can inflate per-example CER even when corpus-level error remains comparatively low. These observations caution against over-interpreting isolated failures and reinforce the primacy of aggregate CER and WER on the full test partition.

### 4.5.6 Limitations affecting interpretation

Interpretation remains bounded by the design of the study. The work addresses English line-level IAM only. Literature comparisons are contextual rather than protocol-matched. The fine-tuning schedule was short and early-stopped, and is not an exhaustive hyperparameter search. The CRNN baseline was kept simple by design. Application and demo scores, especially any smoke or synthetic subset metrics, are illustrative only and are excluded from Table 4.2 and from the primary thesis claims.

## 4.6 Application prototype

Beyond offline evaluation, the study includes a Gradio-based demonstration for interactive English line transcription, optionally reporting reference-based CER when ground truth is supplied. The prototype is an applied complement to the experimental programme, showing that the recognition stack can be driven through a non-specialist interface. Scientific claims remain dependent on the full-test E1 to E4 runs reported above, not on demo-subset CER.

## 4.7 Reproducibility statement

Every quantitative statement in this chapter is recoverable from the logged experiment artefacts of the project. Training hyperparameters come from the fine-tuning and CRNN training logs, and test metrics from the corresponding evaluation records. Reproduction follows the project's documented GPU protocol and evaluation commands. Chapter 4 therefore remains answerable to the methodological design of Chapter 3, and prepares the synthesis developed in Chapter 5.
