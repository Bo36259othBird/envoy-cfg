"""Unique value detection and deduplication across env keys."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class UniqueResult:
    env: Dict[str, str]
    duplicate_values: Dict[str, List[str]]  # value -> list of keys sharing it
    strategy: str

    def __repr__(self) -> str:
        n = len(self.duplicate_values)
        return f"<UniqueResult strategy={self.strategy!r} duplicate_value_groups={n}>"

    def is_clean(self) -> bool:
        """Return True when no two keys share the same value."""
        return len(self.duplicate_values) == 0

    def shared_count(self) -> int:
        """Total number of keys that share a value with at least one other key."""
        return sum(len(keys) for keys in self.duplicate_values.values())


def find_unique_values(
    env: Dict[str, str],
    *,
    case_sensitive: bool = True,
    ignore_empty: bool = True,
) -> UniqueResult:
    """Detect keys that share identical values.

    Args:
        env: The environment mapping to inspect.
        case_sensitive: When False, values are compared case-insensitively.
        ignore_empty: When True, empty-string values are excluded from analysis.

    Returns:
        A UniqueResult describing groups of keys that share the same value.
    """
    strategy = "case-sensitive" if case_sensitive else "case-insensitive"

    value_map: Dict[str, List[str]] = {}
    for key, value in env.items():
        if ignore_empty and value == "":
            continue
        normalised = value if case_sensitive else value.lower()
        value_map.setdefault(normalised, []).append(key)

    duplicates = {v: sorted(keys) for v, keys in value_map.items() if len(keys) > 1}

    return UniqueResult(env=dict(env), duplicate_values=duplicates, strategy=strategy)
