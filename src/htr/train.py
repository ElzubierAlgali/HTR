"""Fine-tune TrOCR on IAM line images."""

from __future__ import annotations

import json
import shutil
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import torch
from PIL import Image
from torch.utils.data import DataLoader
from transformers import TrOCRProcessor, VisionEncoderDecoderModel, get_linear_schedule_with_warmup

from .augment import train_augment
from .dataset import LineDataset
from .metrics import compute_cer
from .models import DEFAULT_DEVICE


def _save_bundle(model, processor, output_dir: Path) -> None:
    """Save model+processor, avoiding Windows overwrite locks on open files."""
    output_dir = Path(output_dir)
    staging = output_dir.parent / f".{output_dir.name}.staging"
    if staging.exists():
        shutil.rmtree(staging)
    staging.mkdir(parents=True, exist_ok=True)
    model.save_pretrained(staging)
    processor.save_pretrained(staging)
    if output_dir.exists():
        shutil.rmtree(output_dir)
    staging.rename(output_dir)


@dataclass
class TrainConfig:
    run_id: str
    base_checkpoint: str
    train_dir: Path
    val_dir: Path
    output_model_dir: Path
    output_dir: Path
    learning_rate: float = 5e-6
    batch_size: int = 8
    grad_accum: int = 1
    epochs: int = 8
    early_stop_patience: int = 2
    max_target_length: int = 128
    max_train_samples: int | None = None
    max_val_samples: int | None = None
    seed: int = 42


def _collate_train(batch: list[dict[str, Any]], processor: TrOCRProcessor, max_target_length: int):
    images = [item["image"] for item in batch]
    texts = [item["reference"] for item in batch]
    pixel_values = processor(images, return_tensors="pt").pixel_values
    labels = processor.tokenizer(
        texts,
        padding=True,
        truncation=True,
        max_length=max_target_length,
        return_tensors="pt",
    ).input_ids
    labels[labels == processor.tokenizer.pad_token_id] = -100
    return {"pixel_values": pixel_values, "labels": labels}


@torch.no_grad()
def _eval_cer(
    model: VisionEncoderDecoderModel,
    processor: TrOCRProcessor,
    dataset: LineDataset,
    device: torch.device,
    batch_size: int,
) -> float:
    model.eval()
    preds: list[str] = []
    refs: list[str] = []
    loader = DataLoader(dataset, batch_size=batch_size, shuffle=False, collate_fn=lambda b: b)
    for batch in loader:
        images = [Image.open(item["path"]).convert("RGB") for item in batch]
        refs.extend(item["reference"] for item in batch)
        pixel_values = processor(images, return_tensors="pt").pixel_values.to(device)
        generated = model.generate(pixel_values, max_new_tokens=128)
        preds.extend(processor.batch_decode(generated, skip_special_tokens=True))
    return compute_cer(preds, refs)


def run_training(config: TrainConfig) -> dict[str, Any]:
    torch.manual_seed(config.seed)
    device = DEFAULT_DEVICE
    start = time.time()

    run_dir = config.output_dir / config.run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    config.output_model_dir.mkdir(parents=True, exist_ok=True)

    processor = TrOCRProcessor.from_pretrained(config.base_checkpoint)
    model = VisionEncoderDecoderModel.from_pretrained(config.base_checkpoint)
    model.to(device)
    model.train()

    # Decoder start / pad tokens required for VisionEncoderDecoder training.
    # Set unconditionally — VisionEncoderDecoderConfig may not expose these attrs for getattr.
    model.config.decoder_start_token_id = processor.tokenizer.cls_token_id
    model.config.pad_token_id = processor.tokenizer.pad_token_id
    model.config.eos_token_id = processor.tokenizer.sep_token_id
    model.generation_config.decoder_start_token_id = processor.tokenizer.cls_token_id
    model.generation_config.pad_token_id = processor.tokenizer.pad_token_id
    model.generation_config.eos_token_id = processor.tokenizer.sep_token_id

    augment = train_augment()
    train_ds = LineDataset(
        config.train_dir,
        max_samples=config.max_train_samples,
        transform=augment,
        return_pil=True,
    )
    val_ds = LineDataset(config.val_dir, max_samples=config.max_val_samples)

    if len(train_ds) == 0:
        raise ValueError(f"No training samples in {config.train_dir}")

    train_loader = DataLoader(
        train_ds,
        batch_size=config.batch_size,
        shuffle=True,
        collate_fn=lambda b: _collate_train(b, processor, config.max_target_length),
    )

    optimizer = torch.optim.AdamW(model.parameters(), lr=config.learning_rate)
    total_steps = max(1, (len(train_loader) // config.grad_accum) * config.epochs)
    scheduler = get_linear_schedule_with_warmup(
        optimizer, num_warmup_steps=max(1, total_steps // 10), num_training_steps=total_steps
    )

    best_val_cer = float("inf")
    epochs_ran = 0
    patience_left = config.early_stop_patience
    history: list[dict[str, Any]] = []

    for epoch in range(1, config.epochs + 1):
        model.train()
        running_loss = 0.0
        optimizer.zero_grad(set_to_none=True)
        for step, batch in enumerate(train_loader, start=1):
            pixel_values = batch["pixel_values"].to(device)
            labels = batch["labels"].to(device)
            outputs = model(pixel_values=pixel_values, labels=labels)
            loss = outputs.loss / config.grad_accum
            loss.backward()
            running_loss += outputs.loss.item()
            if step % config.grad_accum == 0:
                optimizer.step()
                scheduler.step()
                optimizer.zero_grad(set_to_none=True)

        val_cer = _eval_cer(model, processor, val_ds, device, batch_size=max(1, config.batch_size))
        avg_loss = running_loss / max(1, len(train_loader))
        epochs_ran = epoch
        history.append({"epoch": epoch, "train_loss": avg_loss, "val_cer": val_cer})
        print(f"[epoch {epoch}] loss={avg_loss:.4f} val_cer={val_cer:.4f}", flush=True)

        if val_cer < best_val_cer:
            best_val_cer = val_cer
            patience_left = config.early_stop_patience
            _save_bundle(model, processor, config.output_model_dir)
        else:
            patience_left -= 1
            if patience_left <= 0:
                print("Early stopping.", flush=True)
                break

    # Ensure a checkpoint exists even if val never improved (save last)
    if not (config.output_model_dir / "config.json").exists():
        _save_bundle(model, processor, config.output_model_dir)

    wall = time.time() - start
    train_log = {
        "run_id": config.run_id,
        "base_checkpoint": config.base_checkpoint,
        "lr": config.learning_rate,
        "batch_size": config.batch_size,
        "grad_accum": config.grad_accum,
        "epochs_ran": epochs_ran,
        "best_val_cer": best_val_cer if best_val_cer < float("inf") else None,
        "device": str(device),
        "wall_clock_sec": wall,
        "seed": config.seed,
        "max_train_samples": config.max_train_samples,
        "max_val_samples": config.max_val_samples,
        "n_train": len(train_ds),
        "n_val": len(val_ds),
        "output_model_dir": str(config.output_model_dir),
        "history": history,
        "config": asdict(config),
    }
    with open(run_dir / "train_log.json", "w", encoding="utf-8") as f:
        json.dump(train_log, f, indent=2, default=str)

    return train_log
