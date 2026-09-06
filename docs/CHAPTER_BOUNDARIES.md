# Chapter Boundaries (locked)

| Chapter | Contains | Must not contain |
|---------|----------|------------------|
| **1 Introduction** | Problem statement, aim framed as evaluation, five objectives, methodology outline, line-level scope, thesis organisation | GPT-3 / BERT / GPT-2 / XLNet as implemented models, architecture or attention modification, accuracy / precision / recall / F1, medical prescriptions, IAM described as 1,539 pages, measured result numbers |
| **2 Literature Review** | HTR background, image processing and OCR context, related studies, summary table with cited figures | TrOCR described as CRNN or CNN encoder with RNN decoder, restatement of retired objectives, narrative or ornamental prose, uncited passages in another author's voice |
| **3 Methodology** | Research question, IAM description, preprocessing design, model selection, metrics definition, experiment matrix (E1–E5) | Result numbers, CER/WER tables, conclusions from runs, long code listings |
| **4 Implementation & Results** | Contribution (pipeline framing), brief tools table, actual hyperparameters from logs, measured E1–E3 results, figures, honest analysis, brief Gradio | Multi-page inline source code, long VPS/deployment manuals, smoke CER as primary evidence, unmatched SOTA claims |
| **5 Conclusion** | Summary of measured findings, contributions, limitations, future work, closing remark | New experiments, long code, unmatched SOTA claims, smoke metrics as primary evidence |
| **Appendices** | Key module descriptions and sample YAMLs (`docs/APPENDIX_CODE.md`) | Unrelated Bullinger / non-English material |

**Style rule:** Every chapter follows `docs/WRITING_STYLE.md`. Voice is impersonal third person throughout, including the Abstract. Chapter prose is duplicated between each markdown source and its `rebuild_*_docx.py` builder; edit both together.

**Objective rule:** Every objective in Chapter 1 must be delivered by a later chapter, and every deliverable reported in Chapters 4 and 5 must be announced as an objective in Chapter 1.

**Alignment rule:** Every step in Chapter 3 must appear in Chapter 4 as an experiment or implementation note. Every number in Chapter 4 must trace to `experiments/<run_id>/metrics.json` (or `train_log.json` for training fields).

**Honesty rule:** Chapter 3 describes the designed full protocol (n=2,915). Chapter 4 reports actual hyperparameters and confirms sample size (or documents skips). Fine-tune vs pretrained must match logged metrics even if fine-tune does not improve CER.

**Primary vs optional:** E1–E4 are measured full-test claims (TrOCR pretrained/fine-tuned, CRNN+CTC, Tesseract). E5 (demo) is application/qualitative only and must never supply primary CER/WER.
