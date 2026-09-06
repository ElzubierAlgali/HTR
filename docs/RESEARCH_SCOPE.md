# Research Scope (Source of Truth)

This document locks the research story for the thesis and codebase. Every claim in Chapter 4 must trace to an artifact under `experiments/<run_id>/`.

## Primary research question

How well do **transformer-based HTR models** (pretrained and fine-tuned TrOCR) perform on the **English IAM Handwriting Database** benchmark compared to a CRNN+CTC baseline and published literature?

## Locked definitions

| Item | Value |
|------|--------|
| Language | **English only** |
| Primary dataset | IAM Handwriting Database, line-level, English |
| Primary model | `microsoft/trocr-base-handwritten` (+ fine-tuned checkpoint) |
| Architecture | Vision Transformer (ViT) image encoder + BART text decoder |
| Training in this work | **TrOCR fine-tune on IAM** + **CRNN+CTC baseline train** (GPU primary) |
| Loss (TrOCR) | Autoregressive cross-entropy — **not CTC** |
| Loss (CRNN) | CTC |
| Primary metrics | Character Error Rate (CER), Word Error Rate (WER) |
| Primary measured runs | E1 pretrained TrOCR, E2 fine-tuned TrOCR, E3 CRNN+CTC on full IAM test |
| Optional baseline | Tesseract 5.x when system binary is installed; otherwise recorded as skipped |
| Literature baselines | Cited reported CER/WER only — no estimated numbers; protocol may differ |
| Application | Gradio demo on IAM English sample lines (qualitative; not primary CER) |
| Primary eval sample | **n = 2,915** (full IAM test) for E1–E3 |
| Contribution framing | Aligned research-and-application pipeline — **not** a novel architecture or SOTA claim |

## Honesty locks (match logged runs)

- Fine-tuned TrOCR did **not** improve test CER vs Hub pretrained under the logged early-stopped run; report as negative/neutral.
- CRNN+CTC is a **weak** lightweight baseline in this setup, not a competitive neural system.
- Demo / smoke metrics must never appear as primary thesis numbers.
- Do not claim matched state-of-the-art against literature without identical preprocess/splits.

## Out of scope

- Non-English handwriting (Latin, German, historical Bullinger corpus)
- GPT-3 / BERT / XLNet as implemented models
- Medical prescription recognition
- Custom transformer architecture modifications
- CTC as the TrOCR training loss
- Binarization as an implementation step
- Precision / recall / F1 as primary metrics

## Metric normalization

- **Case-sensitive** CER and WER (match common HTR literature)
- Strip leading/trailing whitespace on predictions and references
- Do not lowercase transcriptions
- Per-line CER via Levenshtein at character level; corpus CER = total edits / total reference characters

## IAM data source

- **Primary:** Hugging Face `Teklia/IAM-line` (official train / validation / test splits)
- **Columns:** `image`, `text`
- Processed exports: `data/iam/processed/{train,val,test}/`
- Demo samples: `data/iam/demo/` (English test subset for Gradio)
- Test set size: 2,915 line images (full benchmark split)

## IAM splits

Uses the dataset publisher splits directly:

- **Train:** 6,482 lines
- **Validation:** 976 lines
- **Test:** 2,915 lines

## Experiment runs

| Run ID | Model | Dataset | Role |
|--------|-------|---------|------|
| `iam_trocr_handwritten` | `microsoft/trocr-base-handwritten` | IAM test (full, n=2,915) | **Primary** pretrained |
| `iam_trocr_finetuned` | Local `models/iam_trocr_finetuned/` | IAM test (full, n=2,915) | **Primary** fine-tuned |
| `iam_crnn` | CRNN+CTC | IAM test (full, n=2,915) | Neural baseline |
| `iam_tesseract` | Tesseract | IAM test (full, n=2,915) | Optional classical |
| `iam_demo` | TrOCR (local or Hub) | IAM demo subset | Application qualitative |

Primary YAMLs omit `max_samples` (full test). Smoke configs under `configs/smoke/` keep tiny limits for CPU checks. Thesis numbers must come from GPU full runs (`n=2,915`).

## Traceability rule

Every numeric result in the thesis must reference:

```
experiments/<run_id>/metrics.json
```

Training hyperparameters must reference:

```
experiments/<run_id>/train_log.json
```

Reproduce with:

```bash
python scripts/run_eval.py --config configs/<config>.yaml
python scripts/run_train.py --config configs/iam_trocr_finetune.yaml
python scripts/run_train_crnn.py --config configs/iam_crnn.yaml
```

## Chapter boundaries

- **Chapter 3 (Methodology):** research design only — no result numbers
- **Chapter 4 (Implementation and Results):** contribution, brief implementation, experiments, results, analysis
- **Chapter 5 (Conclusion):** summary of findings, contributions, limitations, future work
- **Appendices:** source module pointers (`docs/APPENDIX_CODE.md`)
