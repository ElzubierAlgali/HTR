from __future__ import annotations

from functools import lru_cache
from typing import Union

import torch
from PIL import Image

from .metrics import compute_cer, normalize_text
from .models import ModelBundle, load_model_bundle

ImageInput = Union[str, Image.Image]


@lru_cache(maxsize=4)
def _cached_bundle(checkpoint: str) -> ModelBundle:
    return load_model_bundle(checkpoint)


def _load_image(image: ImageInput) -> Image.Image:
    if isinstance(image, str):
        return Image.open(image).convert("RGB")
    return image.convert("RGB")


def recognize(image: ImageInput, checkpoint: str) -> str:
    bundle = _cached_bundle(checkpoint)
    pil_image = _load_image(image)
    return normalize_text(bundle.generate(pil_image))


def recognize_with_cer(
    image: ImageInput,
    ground_truth: str,
    checkpoint: str,
) -> tuple[str, float]:
    prediction = recognize(image, checkpoint)
    cer = compute_cer([prediction], [ground_truth])
    return prediction, cer
