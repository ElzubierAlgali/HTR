from __future__ import annotations

if __name__ == "__main__" and __package__ is None:
    import subprocess
    import sys
    from pathlib import Path

    repo_root = Path(__file__).resolve().parents[2]
    script = repo_root / "scripts" / "run_eval.py"
    if len(sys.argv) == 1:
        print("Usage: python3 scripts/run_eval.py --config configs/<name>.yaml")
        print("Example: python3 scripts/run_eval.py --config configs/iam_trocr_handwritten.yaml")
        raise SystemExit(1)
    raise SystemExit(subprocess.call([sys.executable, str(script), *sys.argv[1:]]))

import csv
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import torch
from PIL import Image
from torch.utils.data import DataLoader

from .dataset import LineDataset
from .metrics import compute_cer, compute_wer, per_sample_cer, summarize_errors
from .models import ModelBundle, load_model_bundle


@dataclass
class EvalConfig:
    run_id: str
    checkpoint: str
    split_dir: Path
    output_dir: Path
    batch_size: int = 8
    max_samples: int | None = None
    backend: str = "trocr"  # trocr | tesseract | crnn
    seed: int = 42


def _collate(batch: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return batch


def _predict_tesseract(image_path: str) -> str:
    import shutil

    import pytesseract

    if shutil.which("tesseract") is None:
        raise RuntimeError(
            "Tesseract binary not found. Install with: sudo apt install tesseract-ocr"
        )

    image = Image.open(image_path).convert("RGB")
    return pytesseract.image_to_string(image, config="--psm 7").strip()


@torch.no_grad()
def _predict_trocr_batch(bundle: ModelBundle, image_paths: list[str]) -> list[str]:
    images = [Image.open(p).convert("RGB") for p in image_paths]
    return bundle.generate_batch(images)


def run_evaluation(config: EvalConfig) -> dict[str, Any]:
    torch.manual_seed(config.seed)
    output_dir = config.output_dir / config.run_id
    output_dir.mkdir(parents=True, exist_ok=True)

    if config.backend == "tesseract":
        import shutil

        if shutil.which("tesseract") is None:
            metrics = {
                "run_id": config.run_id,
                "status": "skipped",
                "reason": "Tesseract binary not installed (sudo apt install tesseract-ocr)",
                "backend": "tesseract",
            }
            with open(output_dir / "metrics.json", "w", encoding="utf-8") as f:
                json.dump(metrics, f, indent=2)
            (output_dir / "README.md").write_text(
                "# Skipped\n\nInstall Tesseract: `sudo apt install tesseract-ocr`\n",
                encoding="utf-8",
            )
            return metrics

    dataset = LineDataset(config.split_dir, config.max_samples)
    if len(dataset) == 0:
        raise ValueError(f"No samples found in {config.split_dir}")

    bundle = None
    crnn_bundle = None
    if config.backend == "trocr":
        bundle = load_model_bundle(config.checkpoint)
    elif config.backend == "crnn":
        from .baselines.crnn import load_crnn_bundle

        crnn_bundle = load_crnn_bundle(config.checkpoint)

    predictions: list[str] = []
    references: list[str] = []
    rows: list[dict[str, Any]] = []

    dataloader = DataLoader(
        dataset,
        batch_size=config.batch_size,
        shuffle=False,
        collate_fn=_collate,
    )

    for batch_idx, batch in enumerate(dataloader):
        paths = [item["path"] for item in batch]
        refs = [item["reference"] for item in batch]

        if config.backend == "trocr":
            assert bundle is not None
            preds = _predict_trocr_batch(bundle, paths)
        elif config.backend == "tesseract":
            preds = [_predict_tesseract(p) for p in paths]
        elif config.backend == "crnn":
            assert crnn_bundle is not None
            preds = crnn_bundle.predict_paths(paths)
        else:
            raise ValueError(f"Unknown backend: {config.backend}")

        for path, ref, pred in zip(paths, refs, preds):
            predictions.append(pred)
            references.append(ref)
            rows.append(
                {
                    "filename": Path(path).name,
                    "reference": ref,
                    "prediction": pred,
                    "cer": per_sample_cer(pred, ref),
                }
            )

        if (batch_idx + 1) % 10 == 0:
            print(f"  [{config.run_id}] {len(predictions)}/{len(dataset)} lines", flush=True)

    metrics = {
        "run_id": config.run_id,
        "checkpoint": config.checkpoint,
        "backend": config.backend,
        "n_samples": len(predictions),
        "cer": compute_cer(predictions, references),
        "wer": compute_wer(predictions, references),
        "split_dir": str(config.split_dir),
    }

    with open(output_dir / "config.json", "w", encoding="utf-8") as f:
        json.dump(asdict(config), f, indent=2, default=str)

    with open(output_dir / "metrics.json", "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)

    with open(output_dir / "predictions.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["filename", "reference", "prediction", "cer"])
        writer.writeheader()
        writer.writerows(rows)

    error_summary = summarize_errors(predictions, references)
    with open(output_dir / "error_summary.json", "w", encoding="utf-8") as f:
        json.dump(error_summary, f, indent=2)

    readme = (
        f"# {config.run_id}\n\n"
        f"Reproduce:\n\n"
        f"```bash\n"
        f"python scripts/run_eval.py --config configs/{config.run_id}.yaml\n"
        f"```\n"
    )
    (output_dir / "README.md").write_text(readme, encoding="utf-8")

    return metrics
