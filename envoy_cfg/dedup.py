"""Deduplication utilities for environment variable configs."""

from dataclasses import dataclass, field
from typing import Dict, List, Tuple


@dataclass
class DedupResult:
    env: Dict[str, str]
    duplicates: List[Tuple[str, List[str]]]  # (canonical_key, [duplicate_keys])
    removed_count: int

    def __repr__(self) -> str:
        return (
            f"DedupResult(keys={len(self.env)}, "
            f"duplicate_groups={len(self.duplicates)}, "
            f"removed={self.removed_count})"
        )

    @property
    def is_clean(self) -> bool:
        return self.removed_count == 0


def dedup_env(
    env: Dict[str, str],
    case_insensitive: bool = False,
    keep: str = "first",
) -> DedupResult:
    """Remove duplicate keys from an env dict.

    Args:
        env: The environment dict to deduplicate.
        case_insensitive: If True, treat keys differing only in case as duplicates.
            The canonical key is the first (or last) one encountered.
        keep: 'first' keeps the first occurrence; 'last' keeps the last.

    Returns:
        DedupResult with deduplicated env and metadata.
    """
    if not case_insensitive:
        # No real duplicates possible in a plain dict; return as-is.
        return DedupResult(env=dict(env), duplicates=[], removed_count=0)

    # Group keys by their lowercased form.
    groups: Dict[str, List[str]] = {}
    for k in env:
        groups.setdefault(k.lower(), []).append(k)

    result: Dict[str, str] = {}
    duplicates: List[Tuple[str, List[str]]] = []
    removed_count = 0

    for lower_key, keys in groups.items():
        if len(keys) == 1:
            canonical = keys[0]
            result[canonical] = env[canonical]
        else:
            chosen = keys[-1] if keep == "last" else keys[0]
            result[chosen] = env[chosen]
            dupes = [k for k in keys if k != chosen]
            duplicates.append((chosen, dupes))
            removed_count += len(dupes)

    return DedupResult(env=result, duplicates=duplicates, removed_count=removed_count)


def find_duplicate_keys(env: Dict[str, str]) -> Dict[str, List[str]]:
    """Return a mapping of lowercased key -> list of original keys that collide."""
    groups: Dict[str, List[str]] = {}
    for k in env:
        groups.setdefault(k.lower(), []).append(k)
    return {lower: keys for lower, keys in groups.items() if len(keys) > 1}
