"""IAM line dataset shared by train and eval."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any, Callable

from PIL import Image
from torch.utils.data import Dataset


class LineDataset(Dataset):
    """Reads `split_dir/images/` + `split_dir/labels.csv` (filename, transcription)."""

    def __init__(
        self,
        split_dir: Path | str,
        max_samples: int | None = None,
        transform: Callable[[Image.Image], Image.Image] | None = None,
        return_pil: bool = False,
    ):
        self.split_dir = Path(split_dir)
        self.images_dir = self.split_dir / "images"
        self.transform = transform
        self.return_pil = return_pil
        labels_path = self.split_dir / "labels.csv"
        if not labels_path.exists():
            raise FileNotFoundError(f"Missing labels file: {labels_path}")

        self.samples: list[tuple[str, str]] = []
        with open(labels_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                filename = row["filename"]
                text = row["transcription"]
                image_path = self.images_dir / filename
                if image_path.exists():
                    self.samples.append((str(image_path), text))

        if max_samples is not None:
            self.samples = self.samples[:max_samples]

    def __len__(self) -> int:
        return len(self.samples)

    def __getitem__(self, idx: int) -> dict[str, Any]:
        path, text = self.samples[idx]
        if self.return_pil:
            image = Image.open(path).convert("RGB")
            if self.transform is not None:
                image = self.transform(image)
            return {"path": path, "image": image, "reference": text, "idx": idx}
        return {"path": path, "reference": text, "idx": idx}


def collect_charset(split_dirs: list[Path | str], max_samples: int | None = None) -> str:
    """Build sorted unique character vocabulary from transcriptions."""
    chars: set[str] = set()
    for split_dir in split_dirs:
        ds = LineDataset(split_dir, max_samples=max_samples)
        for _, text in ds.samples:
            chars.update(text)
    # CTC blank is index 0; printable charset starts at 1
    return "".join(sorted(chars))
