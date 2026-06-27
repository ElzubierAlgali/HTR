# Handwritten Text Recognition — English IAM Research & Application

Aligned implementation for thesis: **English IAM benchmark evaluation** + **English IAM Gradio demo**.

## Research story

- **Primary:** Evaluate `microsoft/trocr-base-handwritten` on IAM English test lines (CER/WER)
- **Demo eval:** Same model on IAM demo subset (`iam_demo`)
- **Baseline:** Tesseract on IAM (if installed)
- **Application:** Gradio demo with English IAM sample lines

See [docs/RESEARCH_SCOPE.md](docs/RESEARCH_SCOPE.md) for locked definitions.

## Setup

```bash
python3 -m pip install --user --break-system-packages -e .

# Or use conda
conda env create -f environment.yml
conda activate htr
pip install -e .
```

## Data pipeline

```bash
python3 scripts/download_iam.py
python3 scripts/prepare_iam_lines.py
python3 scripts/prepare_iam_demo_examples.py
```

## Run evaluations

```bash
bash scripts/run_all_experiments.sh

# Or individually
python3 scripts/run_eval.py --config configs/iam_trocr_handwritten.yaml
python3 scripts/run_eval.py --config configs/iam_demo.yaml
python3 scripts/run_eval.py --config configs/iam_tesseract.yaml
```

Results land in `experiments/<run_id>/metrics.json`.

## Figures

```bash
python3 scripts/plot_results.py
python3 scripts/fill_thesis_metrics.py
```

## Application

```bash
python3 app/gradio_app.py
```

## Results

| Run | Artifact |
|-----|----------|
| IAM TrOCR (primary) | `experiments/iam_trocr_handwritten/metrics.json` |
| IAM demo (8 lines) | `experiments/iam_demo/metrics.json` |
| Tesseract | `experiments/iam_tesseract/metrics.json` |

Figure: `experiments/figures/cer_comparison.png`  
Thesis text: `docs/THESIS_REWRITE_FILLED.md`

## Repository layout

```
configs/           # Eval YAML configs (English IAM only)
src/htr/           # Shared models, metrics, evaluate, infer
scripts/           # Data prep and eval CLI
data/iam/          # IAM English data (processed + demo)
experiments/       # Metrics and predictions (gitignored)
app/               # Gradio demo (English IAM)
docs/              # Research scope, thesis rewrite guide
trocr-main/        # Legacy training wrapper (future fine-tuning)
```

## Thesis alignment

- Chapter map: [docs/THESIS_CHAPTER_MAP.md](docs/THESIS_CHAPTER_MAP.md)
- Rewrite guide: [docs/THESIS_REWRITE.md](docs/THESIS_REWRITE.md)

## Traceability

Every number in Chapter 4 must match `experiments/<run_id>/metrics.json`.
