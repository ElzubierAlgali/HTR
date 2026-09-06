# Chapter 3 — Methodology

This chapter presents the research design only. Measured CER and WER values are reserved for Chapter 4.

## 3.1 Introduction

A sound empirical study of handwritten text recognition (HTR) requires more than the selection of a fashionable model: it requires an explicit account of the data, the preprocessing assumptions, the learning objectives, the evaluation criteria, and the comparisons against which claims will be judged. This chapter therefore sets out the methodological framework adopted for the present thesis. The research focuses on English line-level recognition using the IAM Handwriting Database and investigates transfer learning from a pretrained TrOCR transformer, whose Vision Transformer (ViT) encoder is paired with a BART text decoder. A convolutional recurrent network trained with Connectionist Temporal Classification (CRNN+CTC) provides a neural baseline of classical design, while Tesseract is retained as an optional classical optical character recognition reference when the runtime environment permits its use.

The chapter proceeds from dataset characterisation to preprocessing, model choice, metric definitions, and the planned experiment matrix. In keeping with conventional thesis organisation, no experimental scores are reported here; Chapter 4 is responsible for implementation detail, measured outcomes, and interpretive analysis.

## 3.2 Dataset

Reliable benchmarking in HTR depends on a corpus whose splits are stable and publicly documented. The study therefore employs the English IAM line corpus distributed as Hugging Face `Teklia/IAM-line`, which preserves the publisher’s official training, validation, and test partitions. Each sample consists of a line image together with its corresponding transcription. Local preparation yields organised image directories and label tables suitable for both training and evaluation, while a small demonstration subset is reserved for the interactive application described later in the thesis.

**Table 3.1 — IAM line dataset (Teklia/IAM-line)**

| Property | Value |
|----------|--------|
| Language | English |
| Unit | Line images |
| Train / Val / Test | 6,482 / 976 / 2,915 |
| Modalities | PNG line image + transcription text |
| Source | Hugging Face `Teklia/IAM-line` |

The test partition contains 2,915 lines. This full split constitutes the primary evaluation population of the thesis and is preferred over reduced samples that would weaken comparability with published IAM practice.

**Figure 3.1 — Example IAM line.** A representative English line image illustrating the visual domain addressed by the study.

## 3.3 Preprocessing

Preprocessing is kept intentionally conservative so that recognition performance can be attributed primarily to the model rather than to aggressive image engineering. Line images are converted to RGB and presented to the Hugging Face TrOCR processor, which jointly handles visual normalisation and tokenisation for the encoder–decoder model. No custom binarisation pipeline is introduced. Mild geometric and photometric augmentation is applied exclusively during fine-tuning, on the premise that stochastic variation may aid adaptation while leaving the evaluation distribution unaltered. All reported test scores are therefore computed on unaugmented images.

## 3.4 Model selection

### 3.4.1 TrOCR as the primary model

TrOCR is adopted as the principal recognition architecture because it exemplifies the contemporary transfer-learning paradigm in HTR: an image transformer encodes local visual structure, while an autoregressive text transformer decodes character sequences under a language-model prior. The study begins from the publicly available checkpoint `microsoft/trocr-base-handwritten`, which has already been pretrained for English handwritten lines. Fine-tuning on the IAM training and validation partitions uses teacher-forced cross-entropy rather than CTC, with AdamW optimisation and early stopping guided by validation CER. This design choice is consequential: CTC remains associated only with the neural baseline, and is never treated as the training objective of TrOCR.

**Figure 3.2 — TrOCR architecture (conceptual).** Image patches are encoded by a ViT encoder and decoded by a cross-attentive BART decoder into a token sequence.

### 3.4.2 CRNN+CTC as a neural baseline

To situate transformer performance against a familiar neural alternative, a CRNN with CTC is trained from scratch on the same IAM splits. The baseline is deliberately lightweight: convolutional feature extraction is followed by bidirectional recurrent modelling and CTC alignment. Its purpose is comparative clarity rather than architectural rivalry. A large performance gap, should it appear, would illuminate the benefit of large-scale pretrained transformers under matched data conditions.

### 3.4.3 Tesseract as an optional classical baseline

Tesseract, operated in line-oriented recognition mode, is included as a classical OCR reference. Because availability of the system binary can vary across machines, the methodology treats Tesseract as optional: when execution is impossible, Chapter 4 records a skipped status instead of fabricating scores. This rule preserves methodological honesty without forcing an incomplete software dependency to dictate the scientific narrative.

## 3.5 Experiment design and evaluation metrics

The empirical programme is organised as a small matrix of complementary runs. Primary scientific claims rest on full-test evaluation of pretrained TrOCR, fine-tuned TrOCR, and the CRNN+CTC baseline. The optional Tesseract run and the demonstration subset support completeness and application discussion, respectively, but do not redefine the primary evidence base.

**Table 3.2 — Designed experiment matrix**

| ID | Run | Role | Evaluation sample |
|----|-----|------|-------------------|
| E1 | Pretrained TrOCR | Primary transformer baseline | Full test (n=2,915) |
| E2 | Fine-tuned TrOCR | Adaptation experiment | Full test (n=2,915) |
| E3 | CRNN+CTC | Neural baseline | Full test (n=2,915) |
| E4 | Tesseract | Optional classical baseline | Full test (n=2,915) |
| E5 | Demonstration subset | Application support | Demo lines only |

Two metrics dominate the evaluation. Character Error Rate (CER) quantifies the normalised edit distance at character level and remains the principal indicator of transcription fidelity in HTR. Word Error Rate (WER) provides a complementary word-level view of recognition difficulty. Both are computed after case-sensitive whitespace normalisation; transcriptions are not lowercased, so that the metric reflects orthographic detail rather than an artificially simplified string space. Corpus CER is defined as the ratio of total character edits to total reference characters across the evaluated set.

Engineering smoke tests with severely reduced sample limits may be used during development, but they are excluded from thesis claims. All numbers advanced as research evidence must originate from the full GPU protocol on the complete test partition.

## 3.6 Comparative framework

Chapter 4 is designed to answer three comparative questions that follow directly from this methodology. First, does fine-tuning improve upon the pretrained TrOCR checkpoint when both are evaluated on the same full IAM test set? Second, how does TrOCR compare with the CRNN+CTC baseline under identical data and metric definitions? Third, how do the measured scores relate, at a contextual level only, to CER figures reported in selected IAM literature? The third comparison is deliberately cautious: published studies may differ in preprocessing, decoding, or split conventions, and are therefore cited for scale rather than treated as protocol-identical replications.

## 3.7 Scope of the chapter

In summary, Chapter 3 fixes the scientific design of the thesis: English IAM line data, conservative preprocessing, TrOCR as the primary transfer-learning model, CRNN+CTC as a controlled neural baseline, optional classical OCR, and full-test CER/WER evaluation. The chapter contains no numeric experimental outcomes. Implementation choices actually used, measured results, and interpretive discussion are developed in Chapter 4.
