from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Union

import torch
from PIL import Image
from transformers import TrOCRProcessor, VisionEncoderDecoderModel

DEFAULT_DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

TROCR_HANDWRITTEN = "microsoft/trocr-base-handwritten"
LOCAL_TROCR_FINETUNED = "models/iam_trocr_finetuned"

KNOWN_HUB_CHECKPOINTS = {TROCR_HANDWRITTEN}

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


def _resolve_checkpoint(checkpoint: str) -> tuple[str, Path | None]:
    """Return (load_id, local_path_or_none). Accepts Hub IDs or local dirs."""
    path = Path(checkpoint)
    if path.exists() and path.is_dir():
        return str(path), path
    # Also accept repo-relative models/... even if cwd differs
    repo_models = Path(__file__).resolve().parents[2] / checkpoint
    if repo_models.exists() and repo_models.is_dir():
        return str(repo_models), repo_models
    if checkpoint in KNOWN_HUB_CHECKPOINTS:
        return checkpoint, None
    # Allow any Hub-style id (org/name) for flexibility
    if "/" in checkpoint and not checkpoint.startswith(".") and not checkpoint.startswith("models"):
        return checkpoint, None
    raise ValueError(
        f"Unknown checkpoint {checkpoint!r}. "
        f"Use a Hub id (e.g. {TROCR_HANDWRITTEN!r}) or a local directory "
        f"(e.g. {LOCAL_TROCR_FINETUNED!r})."
    )


def load_model_bundle(
    checkpoint: str,
    device: torch.device | None = None,
) -> ModelBundle:
    """Load TrOCR checkpoint (Hub or local) with matched processor and weights."""
    load_id, local_path = _resolve_checkpoint(checkpoint)
    resolved_device = device or DEFAULT_DEVICE

    processor_source = load_id
    if local_path is not None:
        # Prefer processor saved with the checkpoint; fall back to Hub base
        has_processor = (local_path / "preprocessor_config.json").exists() or (
            local_path / "tokenizer_config.json"
        ).exists()
        if not has_processor:
            processor_source = TROCR_HANDWRITTEN

    processor = TrOCRProcessor.from_pretrained(processor_source)
    model = VisionEncoderDecoderModel.from_pretrained(load_id)
    model.to(resolved_device)
    model.eval()

    return ModelBundle(
        checkpoint=str(checkpoint),
        model=model,
        device=resolved_device,
        image_processor=processor.image_processor,
        text_processor=processor,
    )
