from __future__ import annotations

import re
from collections import Counter

import jiwer


def normalize_text(text: str) -> str:
    """Case-sensitive normalization: collapse internal whitespace, strip ends."""
    return re.sub(r"\s+", " ", text.strip())


def compute_cer(predictions: list[str], references: list[str]) -> float:
    preds = [normalize_text(p) for p in predictions]
    refs = [normalize_text(r) for r in references]
    return float(jiwer.cer(refs, preds))


def compute_wer(predictions: list[str], references: list[str]) -> float:
    preds = [normalize_text(p) for p in predictions]
    refs = [normalize_text(r) for r in references]
    return float(jiwer.wer(refs, preds))


def per_sample_cer(prediction: str, reference: str) -> float:
    return compute_cer([prediction], [reference])


def summarize_errors(predictions: list[str], references: list[str], top_n: int = 20) -> dict:
    """Summarize character-level substitution patterns using jiwer alignment."""
    counter: Counter[str] = Counter()

    for pred, ref in zip(predictions, references):
        pred_n = normalize_text(pred)
        ref_n = normalize_text(ref)
        alignment = jiwer.process_words(ref_n, pred_n)
        for chunk in alignment.alignments[0]:
            if chunk.type == "equal":
                continue
            ref_slice = ref_n[chunk.ref_start_idx : chunk.ref_end_idx]
            pred_slice = pred_n[chunk.hyp_start_idx : chunk.hyp_end_idx]
            counter[f"{chunk.type}:{ref_slice!r}->{pred_slice!r}"] += 1

    return {
        "top_errors": [{"pattern": k, "count": v} for k, v in counter.most_common(top_n)],
        "total_mismatched_lines": sum(1 for p, r in zip(predictions, references) if p != r),
    }
