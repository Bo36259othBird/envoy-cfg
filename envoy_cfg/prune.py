"""Prune unused or empty environment variable keys."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class PruneResult:
    original: Dict[str, str]
    pruned: Dict[str, str]
    removed_keys: List[str] = field(default_factory=list)
    reason: str = "unknown"

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"PruneResult(removed={len(self.removed_keys)}, "
            f"remaining={len(self.pruned)}, reason={self.reason!r})"
        )

    @property
    def is_clean(self) -> bool:
        """True when nothing was removed."""
        return len(self.removed_keys) == 0


def prune_empty(
    env: Dict[str, str],
    *,
    strip_whitespace: bool = True,
) -> PruneResult:
    """Remove keys whose values are empty (or whitespace-only)."""
    removed: List[str] = []
    pruned: Dict[str, str] = {}
    for key, value in env.items():
        effective = value.strip() if strip_whitespace else value
        if effective == "":
            removed.append(key)
        else:
            pruned[key] = value
    return PruneResult(
        original=dict(env),
        pruned=pruned,
        removed_keys=sorted(removed),
        reason="empty_value",
    )


def prune_keys(
    env: Dict[str, str],
    keys: List[str],
) -> PruneResult:
    """Remove a specific list of keys from the env."""
    key_set = set(keys)
    removed: List[str] = []
    pruned: Dict[str, str] = {}
    for key, value in env.items():
        if key in key_set:
            removed.append(key)
        else:
            pruned[key] = value
    return PruneResult(
        original=dict(env),
        pruned=pruned,
        removed_keys=sorted(removed),
        reason="explicit_keys",
    )


def prune_pattern(
    env: Dict[str, str],
    prefix: Optional[str] = None,
    suffix: Optional[str] = None,
) -> PruneResult:
    """Remove keys matching a prefix and/or suffix pattern."""
    removed: List[str] = []
    pruned: Dict[str, str] = {}
    for key, value in env.items():
        match = False
        if prefix and key.startswith(prefix):
            match = True
        if suffix and key.endswith(suffix):
            match = True
        if match:
            removed.append(key)
        else:
            pruned[key] = value
    return PruneResult(
        original=dict(env),
        pruned=pruned,
        removed_keys=sorted(removed),
        reason="pattern",
    )
