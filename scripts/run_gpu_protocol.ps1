# Full GPU protocol: train TrOCR + CRNN, then evaluate E1-E5.
# Usage (PowerShell from repo root):
#   .\scripts\run_gpu_protocol.ps1

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root
$env:PYTHONPATH = "src"

Write-Host "=== TrOCR fine-tune (full) ==="
python scripts/run_train.py --config configs/iam_trocr_finetune.yaml
if ($LASTEXITCODE -ne 0) { throw "TrOCR fine-tune failed ($LASTEXITCODE)" }

Write-Host "=== CRNN train (full) ==="
python scripts/run_train_crnn.py --config configs/iam_crnn.yaml
if ($LASTEXITCODE -ne 0) { throw "CRNN train failed ($LASTEXITCODE)" }

Write-Host "=== Evaluations E1-E5 ==="
python scripts/run_all_experiments.py
if ($LASTEXITCODE -ne 0) { throw "Evaluations failed ($LASTEXITCODE)" }

Write-Host "=== Figures + error examples + thesis fill ==="
python scripts/plot_results.py
python scripts/extract_error_examples.py
python scripts/fill_thesis_metrics.py

Write-Host "Done. Copy experiments/ and models/ back if this ran on a remote GPU host."
