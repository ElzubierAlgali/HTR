"""CRNN + CTC baseline for IAM line recognition."""

from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import torch
import torch.nn as nn
from PIL import Image
from torch.utils.data import DataLoader
from torchvision import transforms

from ..augment import train_augment
from ..dataset import LineDataset, collect_charset
from ..metrics import compute_cer
from ..models import DEFAULT_DEVICE


def _cnn_feat_dim(cnn: nn.Module, img_height: int, img_width: int) -> int:
    with torch.no_grad():
        y = cnn(torch.zeros(1, 1, img_height, img_width))
    _, c, h, _ = y.shape
    return c * h


class CRNN(nn.Module):
    """CNN + BiLSTM + linear head for CTC."""

    def __init__(self, n_classes: int, img_height: int = 32, img_width: int = 128):
        super().__init__()
        self.img_height = img_height
        self.img_width = img_width
        self.cnn = nn.Sequential(
            nn.Conv2d(1, 64, 3, 1, 1),
            nn.ReLU(True),
            nn.MaxPool2d(2, 2),
            nn.Conv2d(64, 128, 3, 1, 1),
            nn.ReLU(True),
            nn.MaxPool2d(2, 2),
            nn.Conv2d(128, 256, 3, 1, 1),
            nn.BatchNorm2d(256),
            nn.ReLU(True),
            nn.Conv2d(256, 256, 3, 1, 1),
            nn.ReLU(True),
            nn.MaxPool2d((2, 1), (2, 1)),
            nn.Conv2d(256, 512, 3, 1, 1),
            nn.BatchNorm2d(512),
            nn.ReLU(True),
            nn.Conv2d(512, 512, 3, 1, 1),
            nn.ReLU(True),
            nn.MaxPool2d((2, 1), (2, 1)),
            nn.Conv2d(512, 512, kernel_size=(2, 2), stride=1, padding=0),
            nn.BatchNorm2d(512),
            nn.ReLU(True),
        )
        feat_dim = _cnn_feat_dim(self.cnn, img_height, img_width)
        self.rnn = nn.LSTM(feat_dim, 256, num_layers=2, bidirectional=True, batch_first=True)
        self.fc = nn.Linear(512, n_classes)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        feats = self.cnn(x)
        b, c, h, w = feats.size()
        feats = feats.permute(0, 3, 1, 2).contiguous().view(b, w, c * h)
        out, _ = self.rnn(feats)
        return self.fc(out)


@dataclass
class CRNNTrainConfig:
    run_id: str
    train_dir: Path
    val_dir: Path
    output_model_dir: Path
    output_dir: Path
    learning_rate: float = 1e-3
    batch_size: int = 32
    epochs: int = 20
    early_stop_patience: int = 3
    img_height: int = 32
    img_width: int = 128
    max_train_samples: int | None = None
    max_val_samples: int | None = None
    seed: int = 42


class CharsetCodec:
    """CTC blank = 0; characters start at 1."""

    def __init__(self, charset: str):
        self.charset = charset
        self.char_to_idx = {c: i + 1 for i, c in enumerate(charset)}
        self.idx_to_char = {i + 1: c for i, c in enumerate(charset)}
        self.blank = 0
        self.n_classes = len(charset) + 1

    def encode(self, text: str) -> list[int]:
        return [self.char_to_idx[c] for c in text if c in self.char_to_idx]

    def decode_greedy(self, indices: list[int]) -> str:
        chars: list[str] = []
        prev = self.blank
        for i in indices:
            if i != self.blank and i != prev:
                chars.append(self.idx_to_char.get(i, ""))
            prev = i
        return "".join(chars)


def _image_transform(img_height: int, img_width: int, augment: bool):
    ops: list[Any] = []
    if augment:
        ops.append(train_augment())
    ops.extend(
        [
            transforms.Grayscale(num_output_channels=1),
            transforms.Resize((img_height, img_width)),
            transforms.ToTensor(),
            transforms.Normalize((0.5,), (0.5,)),
        ]
    )
    return transforms.Compose(ops)


def _collate_crnn(batch: list[dict[str, Any]], codec: CharsetCodec, tfm):
    images = []
    targets: list[int] = []
    target_lengths: list[int] = []
    refs: list[str] = []
    for item in batch:
        img = Image.open(item["path"]).convert("RGB")
        images.append(tfm(img))
        encoded = codec.encode(item["reference"])
        if not encoded:
            encoded = [1]
        targets.extend(encoded)
        target_lengths.append(len(encoded))
        refs.append(item["reference"])
    return {
        "images": torch.stack(images, dim=0),
        "targets": torch.tensor(targets, dtype=torch.long),
        "target_lengths": torch.tensor(target_lengths, dtype=torch.long),
        "refs": refs,
        "paths": [item["path"] for item in batch],
    }


@torch.no_grad()
def _eval_cer_crnn(
    model: CRNN,
    codec: CharsetCodec,
    dataset: LineDataset,
    device: torch.device,
    tfm,
    batch_size: int,
) -> float:
    model.eval()
    preds: list[str] = []
    refs: list[str] = []
    loader = DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=False,
        collate_fn=lambda b: _collate_crnn(b, codec, tfm),
    )
    for batch in loader:
        logits = model(batch["images"].to(device))
        pred_idx = logits.argmax(dim=-1).cpu().tolist()
        for seq, ref in zip(pred_idx, batch["refs"]):
            preds.append(codec.decode_greedy(seq))
            refs.append(ref)
    return compute_cer(preds, refs)


@dataclass
class CRNNBundle:
    model: CRNN
    codec: CharsetCodec
    device: torch.device
    img_height: int
    img_width: int

    def predict_paths(self, paths: list[str]) -> list[str]:
        self.model.eval()
        tfm = _image_transform(self.img_height, self.img_width, augment=False)
        images = torch.stack([tfm(Image.open(p).convert("RGB")) for p in paths], dim=0).to(
            self.device
        )
        with torch.no_grad():
            logits = self.model(images)
            pred_idx = logits.argmax(dim=-1).cpu().tolist()
        return [self.codec.decode_greedy(seq) for seq in pred_idx]


def load_crnn_bundle(checkpoint: str | Path, device: torch.device | None = None) -> CRNNBundle:
    path = Path(checkpoint)
    if not path.is_absolute():
        repo = Path(__file__).resolve().parents[3]
        candidate = repo / checkpoint
        if candidate.exists():
            path = candidate
    if not path.exists():
        raise FileNotFoundError(f"CRNN checkpoint not found: {checkpoint}")

    meta = json.loads((path / "meta.json").read_text(encoding="utf-8"))
    codec = CharsetCodec(meta["charset"])
    resolved = device or DEFAULT_DEVICE
    model = CRNN(
        n_classes=codec.n_classes,
        img_height=int(meta["img_height"]),
        img_width=int(meta["img_width"]),
    )
    state = torch.load(path / "crnn.pt", map_location=resolved, weights_only=True)
    model.load_state_dict(state)
    model.to(resolved)
    model.eval()
    return CRNNBundle(
        model=model,
        codec=codec,
        device=resolved,
        img_height=int(meta["img_height"]),
        img_width=int(meta["img_width"]),
    )


def run_crnn_training(config: CRNNTrainConfig) -> dict[str, Any]:
    torch.manual_seed(config.seed)
    device = DEFAULT_DEVICE
    start = time.time()

    run_dir = config.output_dir / config.run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    config.output_model_dir.mkdir(parents=True, exist_ok=True)

    charset = collect_charset(
        [config.train_dir, config.val_dir],
        max_samples=config.max_train_samples,
    )
    if not charset:
        raise ValueError("Empty charset — check train labels")
    codec = CharsetCodec(charset)

    train_tfm = _image_transform(config.img_height, config.img_width, augment=True)
    eval_tfm = _image_transform(config.img_height, config.img_width, augment=False)

    train_ds = LineDataset(config.train_dir, max_samples=config.max_train_samples)
    val_ds = LineDataset(config.val_dir, max_samples=config.max_val_samples)
    if len(train_ds) == 0:
        raise ValueError(f"No training samples in {config.train_dir}")

    model = CRNN(codec.n_classes, config.img_height, config.img_width).to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=config.learning_rate)
    ctc = nn.CTCLoss(blank=codec.blank, zero_infinity=True)

    train_loader = DataLoader(
        train_ds,
        batch_size=config.batch_size,
        shuffle=True,
        collate_fn=lambda b: _collate_crnn(b, codec, train_tfm),
    )

    best_val_cer = float("inf")
    epochs_ran = 0
    patience_left = config.early_stop_patience
    history: list[dict[str, Any]] = []

    for epoch in range(1, config.epochs + 1):
        model.train()
        running = 0.0
        for batch in train_loader:
            images = batch["images"].to(device)
            logits = model(images)
            log_probs = logits.log_softmax(2).permute(1, 0, 2)
            input_lengths = torch.full(
                (images.size(0),), log_probs.size(0), dtype=torch.long, device=device
            )
            loss = ctc(
                log_probs,
                batch["targets"].to(device),
                input_lengths,
                batch["target_lengths"].to(device),
            )
            optimizer.zero_grad(set_to_none=True)
            loss.backward()
            nn.utils.clip_grad_norm_(model.parameters(), 5.0)
            optimizer.step()
            running += loss.item()

        val_cer = _eval_cer_crnn(
            model, codec, val_ds, device, eval_tfm, batch_size=config.batch_size
        )
        avg_loss = running / max(1, len(train_loader))
        epochs_ran = epoch
        history.append({"epoch": epoch, "train_loss": avg_loss, "val_cer": val_cer})
        print(f"[crnn epoch {epoch}] loss={avg_loss:.4f} val_cer={val_cer:.4f}", flush=True)

        if val_cer < best_val_cer:
            best_val_cer = val_cer
            patience_left = config.early_stop_patience
            torch.save(model.state_dict(), config.output_model_dir / "crnn.pt")
            meta = {
                "charset": charset,
                "img_height": config.img_height,
                "img_width": config.img_width,
                "n_classes": codec.n_classes,
            }
            (config.output_model_dir / "meta.json").write_text(
                json.dumps(meta, indent=2), encoding="utf-8"
            )
        else:
            patience_left -= 1
            if patience_left <= 0:
                print("Early stopping.", flush=True)
                break

    if not (config.output_model_dir / "crnn.pt").exists():
        torch.save(model.state_dict(), config.output_model_dir / "crnn.pt")
        meta = {
            "charset": charset,
            "img_height": config.img_height,
            "img_width": config.img_width,
            "n_classes": codec.n_classes,
        }
        (config.output_model_dir / "meta.json").write_text(
            json.dumps(meta, indent=2), encoding="utf-8"
        )

    wall = time.time() - start
    train_log = {
        "run_id": config.run_id,
        "lr": config.learning_rate,
        "batch_size": config.batch_size,
        "epochs_ran": epochs_ran,
        "best_val_cer": best_val_cer if best_val_cer < float("inf") else None,
        "device": str(device),
        "wall_clock_sec": wall,
        "seed": config.seed,
        "max_train_samples": config.max_train_samples,
        "n_train": len(train_ds),
        "n_val": len(val_ds),
        "charset_size": len(charset),
        "output_model_dir": str(config.output_model_dir),
        "history": history,
        "config": asdict(config),
    }
    with open(run_dir / "train_log.json", "w", encoding="utf-8") as f:
        json.dump(train_log, f, indent=2, default=str)
    return train_log
