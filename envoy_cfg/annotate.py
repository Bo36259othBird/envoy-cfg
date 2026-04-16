"""Annotation support: attach metadata comments to env keys."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional


@dataclass
class AnnotateResult:
    env: Dict[str, str]
    annotations: Dict[str, str]
    annotated_keys: list = field(default_factory=list)
    strategy: str = "annotate"

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"AnnotateResult(annotated={len(self.annotated_keys)}, "
            f"total={len(self.env)})"
        )

    def is_clean(self) -> bool:
        return len(self.annotated_keys) == 0


def apply_annotations(
    env: Dict[str, str],
    annotations: Dict[str, str],
    overwrite: bool = False,
) -> AnnotateResult:
    """Attach annotation comments to matching env keys.

    Annotations are stored in a parallel dict keyed by env key.
    Existing annotations are preserved unless *overwrite* is True.
    """
    if not isinstance(annotations, dict):
        raise TypeError("annotations must be a dict")

    merged: Dict[str, str] = {}
    annotated: list = []

    for key in env:
        if key in annotations:
            if overwrite or key not in merged:
                merged[key] = annotations[key]
                annotated.append(key)
        # keys not in annotations get an empty annotation
        if key not in merged:
            merged[key] = annotations.get(key, "")
            if key in annotations:
                annotated.append(key)

    return AnnotateResult(
        env=dict(env),
        annotations=merged,
        annotated_keys=sorted(set(annotated)),
        strategy="annotate",
    )


def strip_annotations(
    annotations: Dict[str, str],
    keys: Optional[list] = None,
) -> Dict[str, str]:
    """Remove annotations for the given keys (or all if keys is None)."""
    if keys is None:
        return {}
    return {k: v for k, v in annotations.items() if k not in keys}


def get_annotation(annotations: Dict[str, str], key: str) -> Optional[str]:
    """Return the annotation for a key, or None if absent."""
    return annotations.get(key) or None
