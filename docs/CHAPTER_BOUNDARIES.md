# Chapter Boundaries (locked)

| Chapter | Contains | Must not contain |
|---------|----------|------------------|
| **3 Methodology** | Research question, IAM description, preprocessing design, model selection, metrics definition, experiment matrix | Result numbers, CER/WER tables, conclusions from runs, long code listings |
| **4 Implementation & Results** | Contribution, brief tools table, actual hyperparameters from logs, measured results, figures, analysis, brief Gradio | Multi-page inline source code, long VPS/deployment manuals |
| **Appendices** | Key module descriptions and sample YAMLs (`docs/APPENDIX_CODE.md`) | Unrelated Bullinger / non-English material |

**Alignment rule:** Every step in Chapter 3 must appear in Chapter 4 as an experiment or implementation. Every number in Chapter 4 must trace to `experiments/<run_id>/metrics.json`.

**Honesty rule:** Chapter 3 describes the designed full protocol (n=2,915). Chapter 4 reports actual hyperparameters and confirms sample size (or documents deviation).
