"""Pivot: restructure env vars by swapping keys and values."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class PivotResult:
    pivoted: Dict[str, str]
    skipped: List[str]
    strategy: str

    def __repr__(self) -> str:
        return (
            f"PivotResult(strategy={self.strategy!r}, "
            f"pivoted={len(self.pivoted)}, skipped={len(self.skipped)})"
        )

    @property
    def is_clean(self) -> bool:
        return len(self.skipped) == 0


def pivot_env(
    env: Dict[str, str],
    *,
    overwrite: bool = False,
    skip_empty: bool = True,
) -> PivotResult:
    """Swap keys and values in *env*.

    When two keys share the same value, the last one wins unless
    *overwrite* is False, in which case the first mapping is kept and
    subsequent collisions are recorded in *skipped*.
    """
    pivoted: Dict[str, str] = {}
    skipped: List[str] = []

    for key, value in env.items():
        if skip_empty and not value:
            skipped.append(key)
            continue
        if value in pivoted and not overwrite:
            skipped.append(key)
            continue
        pivoted[value] = key

    strategy = "overwrite" if overwrite else "keep-first"
    return PivotResult(pivoted=pivoted, skipped=skipped, strategy=strategy)


def unpivot_env(
    env: Dict[str, str],
    original: Dict[str, str],
) -> Dict[str, str]:
    """Reverse a previous pivot using *original* as reference.

    Keys in *env* that are not found as values in *original* are
    passed through unchanged.
    """
    value_to_key = {v: k for k, v in original.items()}
    return {value_to_key.get(k, k): v for k, v in env.items()}
