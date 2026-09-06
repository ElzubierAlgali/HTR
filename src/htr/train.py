"""Fine-tune TrOCR on IAM line images (with progress logs, periodic checkpoints, resume)."""

from __future__ import annotations

import json
import shutil
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterator

import torch
from PIL import Image
from torch.utils.data import DataLoader
from transformers import TrOCRProcessor, VisionEncoderDecoderModel, get_linear_schedule_with_warmup

from .augment import train_augment
from .dataset import LineDataset
from .metrics import compute_cer
from .models import DEFAULT_DEVICE


def _save_bundle(model, processor, output_dir: Path) -> None:
    """Save model+processor with Windows/OneDrive-safe replace (no directory rename)."""
    output_dir = Path(output_dir)
    staging = output_dir.parent / f"{output_dir.name}_staging"
    if staging.exists():
        shutil.rmtree(staging, ignore_errors=True)
        if staging.exists():
            shutil.rmtree(staging)
    staging.mkdir(parents=True, exist_ok=True)
    model.save_pretrained(staging)
    processor.save_pretrained(staging)
    # Copy into place instead of rename: WinError 5 / OneDrive often blocks dir renames.
    if output_dir.exists():
        shutil.rmtree(output_dir, ignore_errors=True)
        if output_dir.exists():
            # Destination locked — write into a sibling then leave staging as fallback.
            alt = output_dir.parent / f"{output_dir.name}_new"
            if alt.exists():
                shutil.rmtree(alt, ignore_errors=True)
            staging.rename(alt)
            raise PermissionError(
                f"Could not replace locked {output_dir}; wrote {alt} instead"
            )
    output_dir.mkdir(parents=True, exist_ok=True)
    for item in staging.iterdir():
        dest = output_dir / item.name
        if item.is_dir():
            if dest.exists():
                shutil.rmtree(dest)
            shutil.copytree(item, dest)
        else:
            shutil.copy2(item, dest)
    shutil.rmtree(staging, ignore_errors=True)


def _disk_free_bytes(path: Path) -> int:
    return shutil.disk_usage(path.resolve().anchor).free


def _atomic_torch_save(obj: dict[str, Any], path: Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    try:
        torch.save(obj, tmp)
        if path.exists():
            path.unlink()
        tmp.rename(path)
    except Exception:
        if tmp.exists():
            tmp.unlink(missing_ok=True)
        raise


def _atomic_json_write(data: dict[str, Any], path: Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")
    if path.exists():
        path.unlink()
    tmp.rename(path)


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
    log_every_steps: int = 50
    save_every_steps: int = 100
    resume: bool = True


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


def _configure_special_tokens(model: VisionEncoderDecoderModel, processor: TrOCRProcessor) -> None:
    model.config.decoder_start_token_id = processor.tokenizer.cls_token_id
    model.config.pad_token_id = processor.tokenizer.pad_token_id
    model.config.eos_token_id = processor.tokenizer.sep_token_id
    model.generation_config.decoder_start_token_id = processor.tokenizer.cls_token_id
    model.generation_config.pad_token_id = processor.tokenizer.pad_token_id
    model.generation_config.eos_token_id = processor.tokenizer.sep_token_id


def _make_loader(
    dataset: LineDataset,
    batch_size: int,
    seed: int,
    epoch: int,
    processor: TrOCRProcessor,
    max_target_length: int,
) -> DataLoader:
    generator = torch.Generator()
    generator.manual_seed(seed + epoch * 1009)

    def _worker_init(worker_id: int) -> None:
        worker_seed = seed + epoch * 1009 + worker_id
        torch.manual_seed(worker_seed)

    return DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=True,
        generator=generator,
        worker_init_fn=_worker_init,
        collate_fn=lambda b: _collate_train(b, processor, max_target_length),
    )


def _iter_from_step(loader: DataLoader, start_step: int) -> Iterator[tuple[int, Any]]:
    """Yield (1-based step, batch), skipping completed steps within the epoch."""
    for step, batch in enumerate(loader, start=1):
        if step <= start_step:
            continue
        yield step, batch


def _eta_seconds(done: int, total: int, elapsed: float) -> float | None:
    if done <= 0 or elapsed <= 0:
        return None
    rate = done / elapsed
    remaining = max(0, total - done)
    return remaining / rate


def _fmt_hms(seconds: float | None) -> str:
    if seconds is None:
        return "?"
    seconds = int(max(0, seconds))
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    if h:
        return f"{h}h{m:02d}m"
    return f"{m}m{s:02d}s"


def run_training(config: TrainConfig) -> dict[str, Any]:
    torch.manual_seed(config.seed)
    device = DEFAULT_DEVICE
    start = time.time()
    session_start = start

    run_dir = config.output_dir / config.run_id
    ckpt_dir = run_dir / "checkpoints"
    run_dir.mkdir(parents=True, exist_ok=True)
    ckpt_dir.mkdir(parents=True, exist_ok=True)
    config.output_model_dir.mkdir(parents=True, exist_ok=True)

    latest_meta_path = ckpt_dir / "latest.json"
    optim_path = ckpt_dir / "optimizer.pt"
    progress_path = run_dir / "progress.json"
    train_log_path = run_dir / "train_log.json"
    model_ckpt = ckpt_dir / "model"

    resume_meta: dict[str, Any] | None = None
    if config.resume and latest_meta_path.exists() and (model_ckpt / "config.json").exists():
        print(f"Resuming from {latest_meta_path} + {model_ckpt}", flush=True)
        resume_meta = json.loads(latest_meta_path.read_text(encoding="utf-8-sig"))
    elif config.resume and (model_ckpt / "config.json").exists() and progress_path.exists():
        # Recover after a failed optimizer dump: model snapshot + progress.json
        print(f"Resuming from model snapshot + {progress_path}", flush=True)
        resume_meta = json.loads(progress_path.read_text(encoding="utf-8-sig"))
    elif config.resume:
        print("No resumable checkpoint found — starting fresh from base checkpoint.", flush=True)

    if resume_meta is not None and (model_ckpt / "config.json").exists():
        processor = TrOCRProcessor.from_pretrained(model_ckpt)
        model = VisionEncoderDecoderModel.from_pretrained(model_ckpt)
    else:
        processor = TrOCRProcessor.from_pretrained(config.base_checkpoint)
        model = VisionEncoderDecoderModel.from_pretrained(config.base_checkpoint)

    model.to(device)
    _configure_special_tokens(model, processor)
    model.train()

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

    steps_per_epoch = max(1, (len(train_ds) + config.batch_size - 1) // config.batch_size)
    optim_steps_per_epoch = max(1, steps_per_epoch // config.grad_accum)
    total_optim_steps = max(1, optim_steps_per_epoch * config.epochs)

    optimizer = torch.optim.AdamW(model.parameters(), lr=config.learning_rate)
    scheduler = get_linear_schedule_with_warmup(
        optimizer,
        num_warmup_steps=max(1, total_optim_steps // 10),
        num_training_steps=total_optim_steps,
    )

    start_epoch = 1
    start_step = 0  # last completed step in epoch (0 = start of epoch)
    global_step = 0
    best_val_cer = float("inf")
    patience_left = config.early_stop_patience
    history: list[dict[str, Any]] = []
    wall_offset = 0.0

    if resume_meta is not None:
        start_epoch = int(resume_meta["epoch"])
        start_step = int(resume_meta["step"])
        global_step = int(resume_meta.get("global_step", 0))
        bvc = resume_meta.get("best_val_cer")
        best_val_cer = float("inf") if bvc is None else float(bvc)
        patience_left = int(resume_meta.get("patience_left", config.early_stop_patience))
        history = list(resume_meta.get("history", []))
        wall_offset = float(resume_meta.get("wall_clock_sec", 0.0))
        if optim_path.exists():
            try:
                opt_blob = torch.load(optim_path, map_location=device, weights_only=False)
                optimizer.load_state_dict(opt_blob["optimizer_state_dict"])
                scheduler.load_state_dict(opt_blob["scheduler_state_dict"])
                print(f"Loaded optimizer state from {optim_path}", flush=True)
            except Exception as exc:
                print(f"WARNING: could not load optimizer ({exc}); continuing with fresh AdamW.", flush=True)
        else:
            print("No optimizer.pt — continuing with fresh AdamW (weights resumed).", flush=True)
        if start_step >= steps_per_epoch:
            print(
                f"Checkpoint at end of epoch {start_epoch}; advancing to epoch {start_epoch + 1}",
                flush=True,
            )
            start_epoch += 1
            start_step = 0
        print(
            f"Resume state: epoch={start_epoch} step={start_step}/{steps_per_epoch} "
            f"global_step={global_step} best_val_cer={best_val_cer}",
            flush=True,
        )

    epochs_ran = max(0, start_epoch - 1)
    stopped_early = False

    def save_training_checkpoint(epoch: int, step: int, *, reason: str) -> None:
        """Save HF weights + lightweight JSON. Optimizer saved only if disk has room."""
        free_before = _disk_free_bytes(ckpt_dir)
        # Need headroom to rewrite ~1.3GB model via staging
        if free_before < 2_000_000_000:
            print(
                f"[ckpt] WARNING: low disk ({free_before / 1e9:.2f} GB free); "
                "writing progress.json only (skip model rewrite).",
                flush=True,
            )
        else:
            _save_bundle(model, processor, model_ckpt)

        meta = {
            "epoch": epoch,
            "step": step,
            "global_step": global_step,
            "best_val_cer": None if best_val_cer == float("inf") else best_val_cer,
            "patience_left": patience_left,
            "history": history,
            "wall_clock_sec": wall_offset + (time.time() - session_start),
            "reason": reason,
            "saved_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "device": str(device),
            "steps_per_epoch": steps_per_epoch,
            "epochs_total": config.epochs,
            "pct_epoch": round(100.0 * step / steps_per_epoch, 2),
            "status": "running",
        }
        _atomic_json_write(meta, latest_meta_path)
        _atomic_json_write(meta, progress_path)

        # AdamW state is ~2x model size; only save when enough free space remains
        free_now = _disk_free_bytes(ckpt_dir)
        if free_now >= 4_000_000_000:
            try:
                _atomic_torch_save(
                    {
                        "optimizer_state_dict": optimizer.state_dict(),
                        "scheduler_state_dict": scheduler.state_dict(),
                    },
                    optim_path,
                )
                print(f"[ckpt] optimizer saved ({free_now / 1e9:.2f} GB free)", flush=True)
            except Exception as exc:
                print(f"[ckpt] WARNING: optimizer save failed ({exc})", flush=True)
        else:
            print(
                f"[ckpt] skip optimizer.pt (only {free_now / 1e9:.2f} GB free; need ~4 GB)",
                flush=True,
            )

        print(
            f"[ckpt] {reason} epoch={epoch} step={step}/{steps_per_epoch} "
            f"({meta['pct_epoch']}%) -> {latest_meta_path}",
            flush=True,
        )

    print(
        f"Train start: n_train={len(train_ds)} n_val={len(val_ds)} "
        f"steps/epoch={steps_per_epoch} device={device} "
        f"log_every={config.log_every_steps} save_every={config.save_every_steps}",
        flush=True,
    )

    for epoch in range(start_epoch, config.epochs + 1):
        model.train()
        running_loss = 0.0
        optimizer.zero_grad(set_to_none=True)
        loader = _make_loader(
            train_ds,
            config.batch_size,
            config.seed,
            epoch,
            processor,
            config.max_target_length,
        )
        epoch_start_step = start_step if epoch == start_epoch else 0
        epoch_t0 = time.time()
        steps_done_this_epoch = epoch_start_step

        for step, batch in _iter_from_step(loader, epoch_start_step):
            pixel_values = batch["pixel_values"].to(device)
            labels = batch["labels"].to(device)
            outputs = model(pixel_values=pixel_values, labels=labels)
            loss = outputs.loss / config.grad_accum
            loss.backward()
            running_loss += float(outputs.loss.item())
            if step % config.grad_accum == 0:
                optimizer.step()
                scheduler.step()
                optimizer.zero_grad(set_to_none=True)
                global_step += 1

            steps_done_this_epoch = step

            if step % config.log_every_steps == 0 or step == steps_per_epoch:
                elapsed = time.time() - epoch_t0
                # Progress within this epoch from resumed start
                done_delta = max(1, step - epoch_start_step)
                eta = _eta_seconds(done_delta, steps_per_epoch - epoch_start_step, elapsed)
                avg = running_loss / max(1, step - epoch_start_step)
                print(
                    f"[epoch {epoch}/{config.epochs}] step {step}/{steps_per_epoch} "
                    f"({100.0 * step / steps_per_epoch:.1f}%) "
                    f"loss={avg:.4f} global_step={global_step} "
                    f"eta_epoch~{_fmt_hms(eta)}",
                    flush=True,
                )
                _atomic_json_write(
                    {
                        "status": "running",
                        "epoch": epoch,
                        "step": step,
                        "steps_per_epoch": steps_per_epoch,
                        "epochs_total": config.epochs,
                        "global_step": global_step,
                        "pct_epoch": round(100.0 * step / steps_per_epoch, 2),
                        "loss_avg": avg,
                        "best_val_cer": None if best_val_cer == float("inf") else best_val_cer,
                        "device": str(device),
                        "eta_epoch_sec": eta,
                        "wall_clock_sec": wall_offset + (time.time() - session_start),
                    },
                    progress_path,
                )

            if step % config.save_every_steps == 0:
                save_training_checkpoint(epoch, step, reason=f"periodic_step_{step}")

        # End of epoch: flush leftover grads if needed
        if steps_done_this_epoch % config.grad_accum != 0:
            optimizer.step()
            scheduler.step()
            optimizer.zero_grad(set_to_none=True)
            global_step += 1

        print(f"[epoch {epoch}] running validation CER on {len(val_ds)} lines...", flush=True)
        val_cer = _eval_cer(model, processor, val_ds, device, batch_size=max(1, config.batch_size))
        # Approximate train loss over steps executed this epoch (from resume point)
        denom = max(1, steps_done_this_epoch - epoch_start_step)
        avg_loss = running_loss / denom
        epochs_ran = epoch
        history.append(
            {
                "epoch": epoch,
                "train_loss": avg_loss,
                "val_cer": val_cer,
                "steps": steps_done_this_epoch,
            }
        )
        print(f"[epoch {epoch}] loss={avg_loss:.4f} val_cer={val_cer:.4f}", flush=True)

        if val_cer < best_val_cer:
            best_val_cer = val_cer
            patience_left = config.early_stop_patience
            try:
                _save_bundle(model, processor, config.output_model_dir)
                print(f"[best] saved to {config.output_model_dir} (val_cer={val_cer:.4f})", flush=True)
            except Exception as exc:
                # Keep training; periodic ckpt still has weights. Retry via end-epoch save.
                print(f"[best] WARNING: save failed ({exc}); continuing.", flush=True)
        else:
            patience_left -= 1

        # Epoch boundary checkpoint (step = full epoch)
        save_training_checkpoint(epoch, steps_per_epoch, reason=f"end_epoch_{epoch}")
        # Next epoch starts at step 0
        start_step = 0

        if patience_left <= 0:
            print("Early stopping.", flush=True)
            stopped_early = True
            break

    if not (config.output_model_dir / "config.json").exists():
        _save_bundle(model, processor, config.output_model_dir)

    wall = wall_offset + (time.time() - session_start)
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
        "checkpoint_dir": str(ckpt_dir),
        "stopped_early": stopped_early,
        "history": history,
        "config": asdict(config),
    }
    _atomic_json_write(train_log, train_log_path)
    _atomic_json_write(
        {
            "status": "completed",
            "epochs_ran": epochs_ran,
            "best_val_cer": train_log["best_val_cer"],
            "wall_clock_sec": wall,
            "device": str(device),
            "output_model_dir": str(config.output_model_dir),
        },
        progress_path,
    )
    print(f"Training finished. Log: {train_log_path}", flush=True)
    return train_log
