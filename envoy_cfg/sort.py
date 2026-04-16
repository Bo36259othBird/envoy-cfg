from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class SortResult:
    env: Dict[str, str]
    strategy: str
    original_order: List[str]
    sorted_order: List[str]

    def __repr__(self) -> str:
        return (
            f"SortResult(strategy={self.strategy!r}, "
            f"keys={len(self.env)})"
        )

    def is_identity(self) -> bool:
        """Return True if sort did not change the key order."""
        return self.original_order == self.sorted_order


def sort_by_key(env: Dict[str, str], reverse: bool = False) -> SortResult:
    """Sort environment variables alphabetically by key."""
    original_order = list(env.keys())
    sorted_keys = sorted(env.keys(), reverse=reverse)
    sorted_env = {k: env[k] for k in sorted_keys}
    label = "alphabetical-desc" if reverse else "alphabetical-asc"
    return SortResult(
        env=sorted_env,
        strategy=label,
        original_order=original_order,
        sorted_order=sorted_keys,
    )


def sort_by_value(env: Dict[str, str], reverse: bool = False) -> SortResult:
    """Sort environment variables by value lexicographically."""
    original_order = list(env.keys())
    sorted_keys = sorted(env.keys(), key=lambda k: env[k], reverse=reverse)
    sorted_env = {k: env[k] for k in sorted_keys}
    label = "by-value-desc" if reverse else "by-value-asc"
    return SortResult(
        env=sorted_env,
        strategy=label,
        original_order=original_order,
        sorted_order=sorted_keys,
    )


def sort_by_length(env: Dict[str, str], reverse: bool = False) -> SortResult:
    """Sort environment variables by key length."""
    original_order = list(env.keys())
    sorted_keys = sorted(env.keys(), key=len, reverse=reverse)
    sorted_env = {k: env[k] for k in sorted_keys}
    label = "by-length-desc" if reverse else "by-length-asc"
    return SortResult(
        env=sorted_env,
        strategy=label,
        original_order=original_order,
        sorted_order=sorted_keys,
    )
