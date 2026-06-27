from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Union

import torch
from PIL import Image
from transformers import TrOCRProcessor, VisionEncoderDecoderModel

DEFAULT_DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

TROCR_HANDWRITTEN = "microsoft/trocr-base-handwritten"

KNOWN_CHECKPOINTS = {TROCR_HANDWRITTEN}

ImageInput = Union[Image.Image, list[Image.Image]]


@dataclass
class ModelBundle:
    checkpoint: str
    model: VisionEncoderDecoderModel
    device: torch.device
    image_processor: Any
    text_processor: TrOCRProcessor

    def preprocess(self, images: ImageInput) -> torch.Tensor:
        pixel_values = self.image_processor(images, return_tensors="pt").pixel_values
        return pixel_values.to(self.device)

    def generate_batch(self, images: list[Image.Image]) -> list[str]:
        self.model.eval()
        pixel_values = self.preprocess(images)
        with torch.no_grad():
            generated_ids = self.model.generate(pixel_values, max_new_tokens=128)
        return self.text_processor.batch_decode(generated_ids, skip_special_tokens=True)

    def generate(self, image: Image.Image) -> str:
        return self.generate_batch([image])[0]


def load_model_bundle(
    checkpoint: str,
    device: torch.device | None = None,
) -> ModelBundle:
    """Load English IAM TrOCR checkpoint with matched processor and weights."""
    if checkpoint not in KNOWN_CHECKPOINTS:
        raise ValueError(
            f"Unknown checkpoint {checkpoint!r}. Known: {sorted(KNOWN_CHECKPOINTS)}"
        )

    resolved_device = device or DEFAULT_DEVICE
    processor = TrOCRProcessor.from_pretrained(checkpoint)
    model = VisionEncoderDecoderModel.from_pretrained(checkpoint)
    model.to(resolved_device)
    model.eval()

    return ModelBundle(
        checkpoint=checkpoint,
        model=model,
        device=resolved_device,
        image_processor=processor.image_processor,
        text_processor=processor,
    )
