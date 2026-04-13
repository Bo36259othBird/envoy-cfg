"""Merge utilities for combining environment variable configs."""

from enum import Enum
from typing import Dict, Optional


class MergeStrategy(str, Enum):
    """Strategy to use when merging two env configs."""
    OURS = "ours"       # Keep values from base on conflict
    THEIRS = "theirs"   # Keep values from incoming on conflict
    UNION = "union"     # Include all keys; incoming wins on conflict (default)


def merge_envs(
    base: Dict[str, str],
    incoming: Dict[str, str],
    strategy: MergeStrategy = MergeStrategy.UNION,
    prefix_filter: Optional[str] = None,
) -> Dict[str, str]:
    """Merge two environment variable dicts according to the given strategy.

    Args:
        base: The original/base environment dict.
        incoming: The new/incoming environment dict to merge in.
        strategy: How to resolve key conflicts.
        prefix_filter: If provided, only merge keys that start with this prefix.

    Returns:
        A new merged dict.
    """
    if prefix_filter:
        incoming = {
            k: v for k, v in incoming.items() if k.startswith(prefix_filter)
        }

    if strategy == MergeStrategy.OURS:
        # Start with incoming for non-conflicting keys, keep base on conflict
        merged = dict(incoming)
        merged.update(base)
        return merged

    if strategy == MergeStrategy.THEIRS:
        # Start with base for non-conflicting keys, incoming wins on conflict
        merged = dict(base)
        merged.update(incoming)
        return merged

    # UNION: same as THEIRS — all keys, incoming wins
    merged = dict(base)
    merged.update(incoming)
    return merged


def merge_summary(
    base: Dict[str, str],
    incoming: Dict[str, str],
    merged: Dict[str, str],
) -> Dict[str, int]:
    """Return a summary of what happened during the merge."""
    added = len(set(merged) - set(base))
    removed = len(set(base) - set(merged))
    overwritten = sum(
        1 for k in base
        if k in incoming and base[k] != incoming[k] and k in merged
    )
    unchanged = len(merged) - added - overwritten
    return {
        "added": added,
        "removed": removed,
        "overwritten": overwritten,
        "unchanged": max(unchanged, 0),
        "total": len(merged),
    }
