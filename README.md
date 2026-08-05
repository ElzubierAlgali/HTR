# Handwritten Text Recognition — English IAM Research & Application

Aligned implementation for thesis: **English IAM train/eval protocol** (pretrained + fine-tuned TrOCR, CRNN+CTC, Tesseract) + **Gradio demo**.

## Research story

- **Primary:** Evaluate `microsoft/trocr-base-handwritten` on **full** IAM English test (n=2,915)
- **Fine-tune:** TrOCR on IAM train/val → `models/iam_trocr_finetuned/`
- **Baselines:** CRNN+CTC and Tesseract on the same full test split
- **Demo eval:** Same pretrained model on IAM demo subset (`iam_demo`)
- **Application:** Gradio demo with English IAM sample lines

See [docs/RESEARCH_SCOPE.md](docs/RESEARCH_SCOPE.md) for locked definitions.

## Setup (CPU smoke)

```bash
python3 -m pip install --user --break-system-packages -e .

# Or use conda
conda env create -f environment.yml
conda activate htr
pip install -e .
```

## Setup (GPU primary — thesis numbers)

```bash
conda env create -f environment-gpu.yml
conda activate htr-gpu
pip install -e .
# System: install tesseract-ocr (e.g. sudo apt install tesseract-ocr)
```

## Data pipeline

```bash
python3 scripts/download_iam.py
python3 scripts/prepare_iam_lines.py
python3 scripts/prepare_iam_demo_examples.py
```

## Train (GPU)

```bash
python3 scripts/run_train.py --config configs/iam_trocr_finetune.yaml
python3 scripts/run_train_crnn.py --config configs/iam_crnn.yaml
```

Windows PowerShell (no bash required):

```powershell
.\scripts\run_gpu_protocol.ps1
```

Smoke (CPU, tiny subsets):

```bash
python3 scripts/run_train.py --config configs/smoke/iam_trocr_finetune.yaml
python3 scripts/run_train_crnn.py --config configs/smoke/iam_crnn.yaml
```

## Run evaluations

```bash
bash scripts/run_all_experiments.sh

# Or individually (primary = full test)
python3 scripts/run_eval.py --config configs/iam_trocr_handwritten.yaml
python3 scripts/run_eval.py --config configs/iam_trocr_finetuned.yaml
python3 scripts/run_eval.py --config configs/iam_crnn.yaml
python3 scripts/run_eval.py --config configs/iam_tesseract.yaml
python3 scripts/run_eval.py --config configs/iam_demo.yaml
```

Results land in `experiments/<run_id>/metrics.json`.

## Figures and thesis fill

```bash
python3 scripts/plot_results.py
python3 scripts/extract_error_examples.py
python3 scripts/fill_thesis_metrics.py
```

## Application

```bash
python3 app/gradio_app.py
```

## Results

| Run | Artifact |
|-----|----------|
| IAM TrOCR pretrained | `experiments/iam_trocr_handwritten/metrics.json` |
| IAM TrOCR fine-tuned | `experiments/iam_trocr_finetuned/metrics.json` |
| CRNN+CTC | `experiments/iam_crnn/metrics.json` |
| Tesseract | `experiments/iam_tesseract/metrics.json` |
| IAM demo (8 lines) | `experiments/iam_demo/metrics.json` |

Figure: `experiments/figures/cer_comparison.png`  
Thesis text: `docs/THESIS_REWRITE_FILLED.md`

## Repository layout

```
configs/           # Primary + smoke YAML configs
src/htr/           # Models, train, evaluate, metrics, CRNN baseline
scripts/           # Data prep, train, eval, thesis rebuild
data/iam/          # IAM English data (processed + demo)
experiments/       # Metrics and predictions (gitignored)
models/            # Fine-tuned checkpoints (gitignored)
app/               # Gradio demo (English IAM)
docs/              # Research scope, chapter markdown, appendices
```

## Thesis alignment

- Scope: [docs/RESEARCH_SCOPE.md](docs/RESEARCH_SCOPE.md)
- Chapter map: [docs/THESIS_CHAPTER_MAP.md](docs/THESIS_CHAPTER_MAP.md)
- Ch3 methodology: [docs/CHAPTER_3_METHODOLOGY.md](docs/CHAPTER_3_METHODOLOGY.md)
- Ch4 results: [docs/CHAPTER_4_IMPLEMENTATION_RESULTS.md](docs/CHAPTER_4_IMPLEMENTATION_RESULTS.md)
- Rewrite guide: [docs/THESIS_REWRITE.md](docs/THESIS_REWRITE.md)

## Traceability

Every number in Chapter 4 must match `experiments/<run_id>/metrics.json`.
Primary thesis numbers use the full IAM test split (n=2,915), not smoke subsets.
