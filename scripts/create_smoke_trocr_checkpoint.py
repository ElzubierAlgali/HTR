#!/usr/bin/env python3
"""Create a tiny random TrOCR-compatible checkpoint for CPU smoke tests.

Used when Hub model weights cannot be downloaded. Not for thesis numbers.
"""

from __future__ import annotations

from pathlib import Path

from transformers import TrOCRProcessor, VisionEncoderDecoderConfig, VisionEncoderDecoderModel

REPO = Path(__file__).resolve().parents[1]
OUT = REPO / "models" / "iam_trocr_finetuned"


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    cfg = VisionEncoderDecoderConfig.from_pretrained("microsoft/trocr-base-handwritten")
    cfg.encoder.num_hidden_layers = 1
    cfg.encoder.num_attention_heads = 3
    cfg.encoder.hidden_size = 192
    cfg.encoder.intermediate_size = 768
    cfg.decoder.num_hidden_layers = 1
    cfg.decoder.num_attention_heads = 4
    cfg.decoder.hidden_size = 256
    cfg.decoder.intermediate_size = 1024
    cfg.decoder.cross_attention_hidden_size = 192
    model = VisionEncoderDecoderModel(cfg)
    proc = TrOCRProcessor.from_pretrained("microsoft/trocr-base-handwritten")
    model.config.decoder_start_token_id = proc.tokenizer.cls_token_id
    model.config.pad_token_id = proc.tokenizer.pad_token_id
    model.config.eos_token_id = proc.tokenizer.sep_token_id
    model.save_pretrained(OUT)
    proc.save_pretrained(OUT)
    print(f"Wrote smoke checkpoint to {OUT}")


if __name__ == "__main__":
    main()
