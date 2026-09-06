# Chapter Boundaries (locked)

| Chapter | Contains | Must not contain |
|---------|----------|------------------|
| **3 Methodology** | Research question, IAM description, preprocessing design, model selection, metrics definition, experiment matrix (E1–E5) | Result numbers, CER/WER tables, conclusions from runs, long code listings |
| **4 Implementation & Results** | Contribution (pipeline framing), brief tools table, actual hyperparameters from logs, measured E1–E3 results, figures, honest analysis, brief Gradio | Multi-page inline source code, long VPS/deployment manuals, smoke CER as primary evidence, unmatched SOTA claims |
| **5 Conclusion** | Summary of measured findings, contributions, limitations, future work, closing remark | New experiments, long code, unmatched SOTA claims, smoke metrics as primary evidence |
| **Appendices** | Key module descriptions and sample YAMLs (`docs/APPENDIX_CODE.md`) | Unrelated Bullinger / non-English material |

**Alignment rule:** Every step in Chapter 3 must appear in Chapter 4 as an experiment or implementation note. Every number in Chapter 4 must trace to `experiments/<run_id>/metrics.json` (or `train_log.json` for training fields).

**Honesty rule:** Chapter 3 describes the designed full protocol (n=2,915). Chapter 4 reports actual hyperparameters and confirms sample size (or documents skips). Fine-tune vs pretrained must match logged metrics even if fine-tune does not improve CER.

**Primary vs optional:** E1–E3 are primary measured claims. E4 (Tesseract) is optional when installed. E5 (demo) is application/qualitative only.
