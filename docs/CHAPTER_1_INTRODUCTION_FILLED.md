# Chapter 1 — Introduction

Scope is locked by `docs/RESEARCH_SCOPE.md`. Voice and register follow `docs/WRITING_STYLE.md`. Metric tokens are filled by `scripts/fill_thesis_metrics.py`.

## 1.1 Introduction

Computer vision gives machines a way to interpret images, and character recognition is one of its oldest applications. Handwriting remains among the hardest cases. Letter shapes, slant, spacing, and stroke thickness vary from writer to writer, and the same writer is rarely consistent across a page.

Convolutional neural networks improved image-based recognition substantially and became the standard feature extractor for handwriting systems (Skala et al., 2022). Recognition of full text lines then moved towards recurrent networks trained with Connectionist Temporal Classification, which transcribe a line image without requiring character segmentation (Sahare et al., 2018). That combination defined the state of the art for much of the past decade.

Transformer architectures have since changed the picture. A transformer encoder can model an image as a sequence of patches, and a pretrained text decoder can generate the transcription under a language-model prior. TrOCR is the clearest example of this design: it pairs a Vision Transformer image encoder with a BART text decoder, both initialised from large-scale pretraining. This thesis examines what such a model achieves on a standard English handwriting benchmark, and whether adapting it further on that benchmark is worthwhile.

## 1.2 Motivation

Pretrained transformer checkpoints are now published openly and can be applied to handwriting recognition without training a model from scratch. That availability raises a practical question for any researcher with limited compute: how much recognition quality is already available off the shelf, and how much remains to be gained by fine-tuning?

The question matters because reported error rates are difficult to compare across studies. Preprocessing, decoding, and dataset splits differ, and many papers report figures obtained under conditions that are not fully documented. A transparent local protocol, applied to the full benchmark test set rather than a convenient subset, makes it possible to state what a given checkpoint actually delivers.

## 1.3 Problem Statement

This research addresses English handwritten text recognition for line images using transformer-based models, evaluated on the IAM Handwriting Database benchmark.

Existing approaches based on convolutional and recurrent networks handle diverse handwriting styles with mixed success, and published comparisons rarely share an identical evaluation protocol. The specific problem is therefore twofold. First, the recognition quality obtainable from a publicly released transformer checkpoint on the full IAM English test partition is not established under a reproducible local protocol. Second, it is unclear whether further fine-tuning on IAM improves that quality, given that the checkpoint is already specialised for English handwriting.

## 1.4 Aims and Objectives

### 1.4.1 Aim

The aim of this research is to evaluate transformer-based handwritten text recognition on the English IAM Handwriting Database under a transparent and reproducible protocol, and to determine whether fine-tuning the pretrained model on IAM yields a measurable improvement.

The aim is framed as evaluation rather than improvement. A fine-tuning run that fails to reduce the error rate is a valid answer to this question, and is reported as such in Chapters 4 and 5.

### 1.4.2 Objectives

1. Review handwritten text recognition methods, with emphasis on transformer architectures and on TrOCR in particular.
2. Implement a reproducible IAM training and evaluation pipeline that measures Character Error Rate and Word Error Rate.
3. Evaluate the pretrained `microsoft/trocr-base-handwritten` checkpoint and a fine-tuned variant on the full IAM English test partition of 2915 lines.
4. Compare both against a CRNN+CTC baseline trained on the same splits, a classical Tesseract reference evaluated on the same partition, and published IAM figures cited for context only.
5. Deploy a web application that performs English IAM line transcription interactively.

## 1.5 Research Methodology

The methodology is stated here in outline. Chapter 3 develops the research design in full, and Chapter 4 reports how it was implemented and what it produced.

**1. Collect the data.** The study uses the English IAM line corpus distributed as Hugging Face `Teklia/IAM-line`, which preserves the publisher's official training, validation, and test partitions. Using published splits keeps the results comparable with other work on IAM.

**2. Preprocess the images.** Line images are converted to RGB and passed to the Hugging Face TrOCR processor, which handles visual normalisation and tokenisation together. No custom binarisation stage is introduced. Mild geometric and photometric augmentation is applied during fine-tuning only, so that the evaluation distribution stays unchanged.

**3. Select the model.** TrOCR is adopted as the primary architecture, using the `microsoft/trocr-base-handwritten` checkpoint. Its Vision Transformer encoder reads image patches and its BART decoder generates the transcription. The architecture is used as published; no attention mechanisms, positional encodings, or layers are modified.

**4. Apply transfer learning.** Fine-tuning starts from the pretrained checkpoint and continues on the IAM training and validation partitions. The objective is teacher-forced cross-entropy. CTC is not used to train TrOCR; it belongs only to the convolutional recurrent baseline.

**5. Configure training.** Optimisation uses AdamW with a learning rate of 5x10⁻⁶, a micro-batch of 1, and gradient accumulation of 8 for an effective batch size of 8. Early stopping monitors validation CER. Hyperparameters and wall-clock cost are recorded to `experiments/iam_trocr_finetuned/train_log.json`.

**6. Train the baselines.** A CRNN+CTC network is trained from scratch on the same IAM splits as a lightweight neural reference. Tesseract is run in line mode as a classical OCR reference on the same test partition.

**7. Evaluate.** Character Error Rate is the primary metric and Word Error Rate the secondary one. Both are computed case-sensitively after whitespace trimming, on the complete test partition. Corpus CER is the ratio of total character edits to total reference characters. Accuracy at the word or character level is not used, because error rate is the established reporting convention in the handwriting recognition literature.

**8. Analyse and deploy.** Results are compared across the four measured systems, placed against published IAM figures for contextual scale, and examined qualitatively through the highest-error predictions. A Gradio application exposes the recogniser interactively. Demonstration output is qualitative and never contributes a primary error rate.

## 1.6 Research Scope

The study covers English handwritten text recognition at the line level, using the IAM Handwriting Database as distributed by `Teklia/IAM-line`. The corpus provides 6,482 training lines, 976 validation lines, and 2915 test lines. All primary results are measured on the complete test partition.

Four systems are evaluated: pretrained TrOCR, fine-tuned TrOCR, a CRNN+CTC baseline, and Tesseract. A Gradio demonstration accompanies them as an applied component.

The following lie outside the scope. Non-English handwriting is not addressed, nor are historical or degraded document collections. The transformer architecture is not modified. Page-level layout analysis and word segmentation are not performed, since the corpus supplies pre-segmented lines. Published results from other studies are cited for context and are not re-implemented under this protocol.

## 1.7 Research Planning

| Phase | Work |
|-------|------|
| 1 | Literature review and research design |
| 2 | Dataset acquisition, split preparation, and pipeline implementation |
| 3 | Baseline evaluation of the pretrained checkpoint |
| 4 | TrOCR fine-tuning on GPU, approximately 88.7 hours of training |
| 5 | CRNN+CTC training and Tesseract evaluation |
| 6 | Application development, analysis, and writing |

## 1.8 Thesis Organization

**Chapter 1** states the problem, the aim, and the objectives, and sets the scope of the study.

**Chapter 2** reviews handwritten text recognition research, covering convolutional and recurrent approaches and the transformer models that followed them.

**Chapter 3** presents the research design: the dataset, the preprocessing assumptions, the choice of models, the metric definitions, and the planned experiment matrix. It reports no measured results.

**Chapter 4** covers implementation and results. It records the logged hyperparameters, reports the measured error rates on the full test partition, presents the comparison figures, and analyses the outcomes.

**Chapter 5** concludes the study, summarising the findings, stating the contributions and limitations, and recommending directions for further work.

**Appendices** describe the principal source modules and provide sample configuration files.
