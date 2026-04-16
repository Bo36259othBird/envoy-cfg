"""Freeze and unfreeze environment variable sets.

A frozen env is a read-only snapshot of key-value pairs. Attempting to
modify a frozen env raises an error. Useful for pinning a known-good
state before destructive operations.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, FrozenSet, List


@dataclass
class FreezeResult:
    env: Dict[str, str]
    frozen_keys: List[str]
    strategy: str

    def __repr__(self) -> str:
        return (
            f"FreezeResult(strategy={self.strategy!r}, "
            f"frozen={len(self.frozen_keys)}, total={len(self.env)})"
        )

    def is_fully_frozen(self) -> bool:
        """True when every key in env is frozen."""
        return set(self.frozen_keys) == set(self.env.keys())

    def is_clean(self) -> bool:
        """True when no keys were frozen (nothing changed)."""
        return len(self.frozen_keys) == 0


def freeze_env(
    env: Dict[str, str],
    keys: List[str] | None = None,
) -> FreezeResult:
    """Mark specific keys (or all keys) as frozen.

    Returns a FreezeResult containing the env and the list of frozen keys.
    When *keys* is None every key in *env* is frozen.
    """
    if not env:
        return FreezeResult(env={}, frozen_keys=[], strategy="all" if keys is None else "selective")

    target_keys = list(env.keys()) if keys is None else [k for k in keys if k in env]
    strategy = "all" if keys is None else "selective"

    return FreezeResult(
        env=dict(env),
        frozen_keys=sorted(target_keys),
        strategy=strategy,
    )


def unfreeze_env(
    env: Dict[str, str],
    frozen_keys: List[str],
    keys: List[str] | None = None,
) -> FreezeResult:
    """Remove freeze markers from specific keys (or all frozen keys).

    Returns a FreezeResult where frozen_keys reflects what remains frozen.
    """
    to_unfreeze: FrozenSet[str] = frozenset(keys if keys is not None else frozen_keys)
    remaining = [k for k in frozen_keys if k not in to_unfreeze]
    strategy = "partial-unfreeze" if keys is not None else "full-unfreeze"

    return FreezeResult(
        env=dict(env),
        frozen_keys=sorted(remaining),
        strategy=strategy,
    )


def check_frozen(
    key: str,
    frozen_keys: List[str],
) -> bool:
    """Return True if *key* is currently frozen."""
    return key in frozen_keys
