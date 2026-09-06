# GPU full protocol (thesis numbers)

Primary thesis metrics require a CUDA machine with full IAM data (`n=2,915` test).

## Hardware note (GeForce MX130 / 2 GB)

Primary YAMLs are tuned for low VRAM:

- TrOCR train: `batch_size: 1`, `grad_accum: 8` (effective batch 8)
- TrOCR eval: `batch_size: 1`
- CRNN: `batch_size: 8`

Expect long wall-clock on MX130. If OOM persists, lower `max_target_length` or evaluate in smaller chunks.

## 1. Environment

```bash
# Option A: conda CUDA env
conda env create -f environment-gpu.yml
conda activate htr-gpu
pip install -e .

# Option B (Windows, existing Python): CUDA wheels
# Use cu126 for Maxwell GPUs (MX130 / sm_50). cu128+ drops Maxwell support.
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu126
pip install -e .


# Install Tesseract system package, e.g.:
# sudo apt install tesseract-ocr
# Windows: install from https://github.com/UB-Mannheim/tesseract/wiki and add to PATH
```

Verify:

```bash
python -c "import torch; print(torch.cuda.is_available(), torch.cuda.get_device_name(0))"
```

## 2. Data

```bash
python scripts/download_iam.py
python scripts/prepare_iam_lines.py
python scripts/prepare_iam_demo_examples.py
```

Confirm sizes: train 6482 / val 976 / test 2915 under `data/iam/processed/`.

## 3. Train + evaluate

PowerShell (Windows — preferred when `bash` is not on PATH):

```powershell
.\scripts\run_gpu_protocol.ps1
```

Git Bash / Linux / WSL:

```bash
bash scripts/run_gpu_protocol.sh
```

Or stepwise:

```bash
python scripts/run_train.py --config configs/iam_trocr_finetune.yaml
python scripts/run_train_crnn.py --config configs/iam_crnn.yaml
python scripts/run_all_experiments.py
python scripts/plot_results.py
python scripts/extract_error_examples.py
python scripts/fill_thesis_metrics.py
```

### TrOCR resume / progress

Training writes:

- `experiments/iam_trocr_finetuned/progress.json` — live % / step / ETA
- `experiments/iam_trocr_finetuned/checkpoints/latest.json` — resumable step/epoch meta
- `experiments/iam_trocr_finetuned/checkpoints/model/` — HF weights snapshot
- `experiments/iam_trocr_finetuned/checkpoints/optimizer.pt` — optional (skipped if disk &lt; ~4 GB free)
- `models/iam_trocr_finetuned/` — best-by-val-CER export

Keep several GB free on `C:` — a failed AdamW dump previously filled the disk.

```powershell
# Continue after interrupt (default)
python scripts/run_train.py --config configs/iam_trocr_finetune.yaml

# Discard checkpoints and start over
python scripts/run_train.py --config configs/iam_trocr_finetune.yaml --fresh

# Watch progress
Get-Content experiments\iam_trocr_finetuned\progress.json
```

Config knobs: `log_every_steps`, `save_every_steps`, `resume` in `configs/iam_trocr_finetune.yaml`.

## 4. Copy artifacts back

Bring to the thesis machine:

- `experiments/` (all run folders + `figures/`)
- `models/iam_trocr_finetuned/`
- `models/iam_crnn/`

## 5. Acceptance

- E1–E4 `metrics.json` have `"n_samples": 2915` (or documented deviation)
- `experiments/iam_trocr_finetuned/train_log.json` exists
- No thesis body number without a matching experiment field
- Do **not** publish smoke/synthetic CER as primary results

## CPU smoke (engineering only)

```bash
python scripts/prepare_smoke_data.py
python scripts/run_train_crnn.py --config configs/smoke/iam_crnn.yaml
python scripts/run_train.py --config configs/smoke/iam_trocr_finetune.yaml
python scripts/run_eval.py --config configs/smoke/iam_trocr_finetuned.yaml
```

Smoke configs may use a tiny local checkpoint when Hub weights are unavailable.
