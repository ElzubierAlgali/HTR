# Chapter 4 — Implementation and Results

Metric tokens are filled by `scripts/fill_thesis_metrics.py` from `experiments/<run_id>/metrics.json`. Training details are taken from the corresponding `train_log.json` files.

## 4.1 Purpose and contribution of the chapter

Where Chapter 3 defined the research design, the present chapter reports how that design was realised and what was observed. The contribution is best understood as an aligned research-and-application study rather than as the invention of a new HTR architecture. In concrete terms, the chapter offers four interlocking outcomes: a reproducible English IAM training and evaluation workflow; a fully logged TrOCR fine-tuning experiment on the official training and validation partitions; a controlled comparison against a CRNN+CTC baseline on the identical full test set of 2,915 lines; and an interactive demonstration that places the recogniser in an applied setting. Comparative reference to published IAM CER figures is included for contextual scale, without any claim of protocol-identical superiority.

## 4.2 Implementation overview

The implementation follows the methodological commitments of Chapter 3. Dataset handling loads line images and transcriptions for training and evaluation. Model utilities load either the public TrOCR checkpoint or a locally fine-tuned directory and generate transcriptions. A dedicated training routine adapts TrOCR with cross-entropy, AdamW, and early stopping on validation CER. A separate CRNN+CTC module supplies the neural baseline. Shared metric code computes case-sensitive CER and WER after whitespace normalisation. Evaluation runners execute the experiment matrix, while a Gradio interface exposes recognition for interactive demonstration. Detailed module listings are placed in the appendix so that the chapter body may remain focused on scientific substance rather than software documentation.

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

Fine-tuning began from `microsoft/trocr-base-handwritten` and used the full IAM training and validation sets (6,482 and 976 lines). Optimisation employed AdamW with a learning rate of \(5 \times 10^{-6}\), a micro-batch size of 1, and gradient accumulation of 8, yielding an effective batch size of 8. A maximum of eight epochs was planned, with early-stopping patience of two validations. Training ran on CUDA and required approximately 88.7 hours of wall-clock time.

Under this schedule, validation CER reached its best value of 0.0137 after the first epoch and then deteriorated (0.0162 in epoch 2; 0.0187 in epoch 3). Early stopping therefore terminated training after three epochs, and the exported model corresponds to the best validation checkpoint rather than the final epoch weights. This behaviour is material to later interpretation: the adaptation run was completed and logged, yet it did not exhibit sustained validation improvement.

### 4.3.2 CRNN+CTC training

The CRNN baseline was trained from scratch on the same IAM partitions with learning rate \(1 \times 10^{-3}\), batch size 8, and fixed input geometry of \(32 \times 128\). Eight epochs were executed under early-stopping patience, with a character set of size 79. Best validation CER remained high (approximately 0.80), already signalling limited competitiveness relative to pretrained TrOCR before test evaluation.

### 4.3.3 Evaluation matrix

Evaluation followed the design of Chapter 3. Primary claims rest on pretrained TrOCR (E1), fine-tuned TrOCR (E2), and CRNN+CTC (E3), each assessed on the full IAM test split. Tesseract (E4) remains optional and is reported as skipped when the binary is unavailable. The demonstration run (E5) supports the application section and is excluded from primary CER evidence.

## 4.4 Results

Table 4.2 reports the primary measured outcomes.

**Table 4.2 — Measured results on the full IAM English test set**

| Method | CER | WER | n |
|--------|-----|-----|---|
| TrOCR pretrained | 4.72% | 11.64% | 2915 |
| TrOCR fine-tuned | 4.96% | 12.46% | 2915 |
| CRNN+CTC | 81.82% | 96.56% | 2915 |

The pretrained transformer attains a CER of 4.72% and a WER of 11.64%. After fine-tuning, CER and WER become 4.96% and 12.46%, respectively. The CRNN+CTC baseline yields a CER of 81.82% and a WER of 96.56% on the same population.

Tesseract status for this study is: [skipped: Tesseract binary not installed (sudo apt install tesseract-ocr)]. No classical OCR score is claimed when the run is skipped. Demonstration metrics, where present, are treated as qualitative application evidence only.

**Figure 4.1 — CER comparison.** Measured CER values for the systems evaluated in this thesis, with selected literature figures shown separately for contextual comparison.

**Table 4.3 — Literature CER figures cited for context**

| Method | CER (IAM) | Source |
|--------|-----------|--------|
| AttentionHTR | 6.50% | Kass & Vats, 2022 |
| Light Transformer | 5.70% | Barrère et al., 2022 |
| GFCN | 7.99% | Coquenet et al., 2020 |

These published values help the reader locate the present scores within the broader IAM literature. They are not re-implemented under the preprocessing and split conventions of this repository, and the thesis therefore does not assert a matched state-of-the-art ranking.

## 4.5 Discussion and analysis

### 4.5.1 Pretrained TrOCR as the principal empirical result

The pretrained TrOCR evaluation constitutes the central positive finding of the study. A CER of 4.72% on 2,915 previously unseen IAM lines indicates that a publicly released transformer HTR checkpoint can deliver strong line-level recognition when assessed under a complete and transparent local protocol. For a master’s investigation concerned with transfer learning rather than architectural invention, this result is scientifically meaningful: it shows what current pretrained models already achieve before any student-led adaptation is attempted.

### 4.5.2 Interpretation of the fine-tuning outcome

Fine-tuning did not improve test recognition. The adapted model’s CER of 4.96% is slightly higher than that of the Hub checkpoint. Several considerations make this outcome intelligible. First, the starting checkpoint is already specialised for English handwriting, so residual headroom on IAM is limited. Second, validation CER worsened after the first epoch, and early stopping rightly preferred the earlier checkpoint; continued training under the logged schedule was not justified by the validation signal. Third, the optimisation used a small micro-batch with gradient accumulation, which may be adequate for a feasibility study yet suboptimal for extracting further gains. The appropriate academic reading is therefore that fine-tuning was executed and measured, and that its effect under these conditions was neutral to slightly adverse—not that adaptation is universally unhelpful, nor that the experiment failed to run.

### 4.5.3 The CRNN+CTC baseline in perspective

The CRNN+CTC system’s CER of 81.82% confirms a substantial gap relative to TrOCR under matched data and metrics. A compact CNN–BiLSTM–CTC model trained from scratch with constrained geometry is not expected, in this setting, to rival a large pretrained encoder–decoder. The baseline nevertheless fulfils its methodological role: it anchors the transformer result against a familiar neural alternative and prevents the discussion from resting solely on a single model family.

### 4.5.4 Error behaviour and qualitative observations

Inspection of high-CER predictions reveals recurring difficulties with very short references, punctuation-dominated or dash-like strings, and rare or hyphenated tokens. Such lines can inflate per-example CER even when corpus-level error remains comparatively low. These observations caution against over-interpreting isolated failures and reinforce the primacy of aggregate CER/WER on the full test partition.

### 4.5.5 Limitations affecting interpretation

Interpretation remains bounded by the study’s design. The work addresses English line-level IAM only. Literature comparisons are contextual rather than protocol-matched. Tesseract may be unavailable in a given environment. The fine-tuning schedule was short and early-stopped, and should not be mistaken for an exhaustive hyperparameter search. Demonstration scores are illustrative and do not substitute for full-test evidence.

## 4.6 Application prototype

Beyond offline evaluation, the study includes a Gradio-based demonstration for interactive English line transcription, optionally with reference-based CER when ground truth is supplied. The prototype is an applied complement to the experimental programme: it shows that the recognition stack can be used by a non-specialist interface, while leaving scientific claims dependent on the full-test runs reported above.

## 4.7 Reproducibility statement

All quantitative statements in this chapter are intended to be recoverable from the logged experiment artefacts of the project. Training hyperparameters are taken from the fine-tuning and CRNN training logs; test metrics are taken from the corresponding evaluation records. Reproduction follows the project’s documented GPU protocol and evaluation commands. In this way, Chapter 4 remains answerable to the methodological design of Chapter 3 and prepares the reflective synthesis developed in Chapter 5.
