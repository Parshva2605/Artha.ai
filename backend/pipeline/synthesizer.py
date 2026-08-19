from __future__ import annotations

import random
from typing import Any, Dict, List

"""
Simple synthesizer pipeline.
Given a list of existing labeled rows for a language, create synthetic rows
to top up to a target count. Synthetic rows are marked with source='synthetic'
and have a confidence score of 0.9. This implementation uses lightweight
heuristics (duplication + small suffix) rather than calling an external LLM,
keeping generation deterministic and safe.

Expected input row shape: dicts containing at least a `text` field and
optionally `label` and `confidence`.
"""


def synthesize_rows_for_language(
    language_config: Dict[str, Any],
    existing_rows: List[Dict[str, Any]],
    label_type: str,
    target_count: int,
    custom_labels: List[str] | None = None,
) -> List[Dict[str, Any]]:
    synthesized: List[Dict[str, Any]] = []
    if target_count <= 0:
        return synthesized

    # If there are no existing rows, create placeholder synthetic samples.
    if not existing_rows:
        base_text = language_config.get("example_prefix", "Synthetic sample")
        for i in range(target_count):
            synthesized.append({
                "text": f"{base_text} {i+1}",
                "label": (custom_labels or ["synthetic"])[i % max(1, len(custom_labels or ["synthetic"]))],
                "confidence": 0.9,
                "source": "synthetic",
            })
        return synthesized

    # Build a pool of source texts and labels to sample from
    pool = existing_rows
    for i in range(target_count):
        src = random.choice(pool)
        text = str(src.get("text") or src.get("content") or "").strip()
        if not text:
            text = language_config.get("example_prefix", "Synthetic sample")
        # Create a lightweight perturbation to keep things identifiable
        new_text = f"{text} (synthetic)"
        label = src.get("label") or (custom_labels or [None])[0]
        synthesized.append({
            "text": new_text,
            "label": label,
            "confidence": 0.9,
            "source": "synthetic",
        })
    return synthesized
