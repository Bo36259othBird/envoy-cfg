"""Swap keys and values or swap two specific keys within an env dict."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


@dataclass
class SwapResult:
    env: Dict[str, str]
    swapped_pairs: List[Tuple[str, str]]
    strategy: str
    skipped: List[str] = field(default_factory=list)

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"SwapResult(strategy={self.strategy!r}, "
            f"swapped={len(self.swapped_pairs)}, skipped={len(self.skipped)})"
        )

    def is_clean(self) -> bool:
        """Return True when no keys were skipped during the swap."""
        return len(self.skipped) == 0


def swap_keys(
    env: Dict[str, str],
    key_a: str,
    key_b: str,
) -> SwapResult:
    """Swap the values of two keys inside *env*.

    If either key is absent the operation is skipped and recorded in
    ``SwapResult.skipped``.
    """
    result = dict(env)
    skipped: List[str] = []
    swapped: List[Tuple[str, str]] = []

    missing = [k for k in (key_a, key_b) if k not in env]
    if missing:
        skipped.extend(missing)
    else:
        result[key_a], result[key_b] = result[key_b], result[key_a]
        swapped.append((key_a, key_b))

    return SwapResult(
        env=result,
        swapped_pairs=swapped,
        strategy="swap_keys",
        skipped=skipped,
    )


def swap_pairs(
    env: Dict[str, str],
    pairs: List[Tuple[str, str]],
) -> SwapResult:
    """Swap the values for each ``(key_a, key_b)`` pair in *pairs*.

    Pairs where either key is missing are skipped.
    """
    result = dict(env)
    skipped: List[str] = []
    swapped: List[Tuple[str, str]] = []

    for key_a, key_b in pairs:
        missing = [k for k in (key_a, key_b) if k not in result]
        if missing:
            skipped.extend(m for m in missing if m not in skipped)
        else:
            result[key_a], result[key_b] = result[key_b], result[key_a]
            swapped.append((key_a, key_b))

    return SwapResult(
        env=result,
        swapped_pairs=swapped,
        strategy="swap_pairs",
        skipped=skipped,
    )
