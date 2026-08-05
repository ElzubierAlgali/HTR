"""Train-only image augmentation; identity at eval."""

from __future__ import annotations

from PIL import Image
from torchvision import transforms


def train_augment() -> transforms.Compose:
    """Mild geometry/brightness transforms for fine-tuning only."""
    return transforms.Compose(
        [
            transforms.RandomAffine(
                degrees=2,
                translate=(0.02, 0.02),
                scale=(0.95, 1.05),
                fill=255,
            ),
            transforms.ColorJitter(brightness=0.15, contrast=0.15),
        ]
    )


def identity_augment(image: Image.Image) -> Image.Image:
    return image
