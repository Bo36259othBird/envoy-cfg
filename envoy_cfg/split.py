"""Split an env dict into multiple named partitions based on key patterns."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class SplitResult:
    partitions: Dict[str, Dict[str, str]]
    unmatched: Dict[str, str]
    rules_applied: List[str] = field(default_factory=list)

    def __repr__(self) -> str:
        parts = len(self.partitions)
        unmatched = len(self.unmatched)
        return f"<SplitResult partitions={parts} unmatched_keys={unmatched}>"

    @property
    def is_complete(self) -> bool:
        """True when every key was matched by at least one rule."""
        return len(self.unmatched) == 0


def split_env(
    env: Dict[str, str],
    rules: Dict[str, str],
    *,
    allow_overlap: bool = False,
) -> SplitResult:
    """Split *env* into named partitions.

    Args:
        env: The source environment dict.
        rules: Mapping of partition name -> regex pattern.  Keys whose names
               match the pattern are placed in that partition.
        allow_overlap: When True a key may appear in multiple partitions.
                       When False (default) each key is claimed by the first
                       matching rule (rules are evaluated in insertion order).

    Returns:
        A :class:`SplitResult` with the populated partitions and any keys
        that were not matched by any rule.
    """
    if not rules:
        raise ValueError("At least one rule must be provided.")

    compiled = {name: re.compile(pattern) for name, pattern in rules.items()}
    partitions: Dict[str, Dict[str, str]] = {name: {} for name in rules}
    claimed: set = set()
    rules_applied: List[str] = []

    for name, regex in compiled.items():
        for key, value in env.items():
            if allow_overlap or key not in claimed:
                if regex.search(key):
                    partitions[name][key] = value
                    claimed.add(key)
                    if name not in rules_applied:
                        rules_applied.append(name)

    unmatched = {k: v for k, v in env.items() if k not in claimed}

    return SplitResult(
        partitions=partitions,
        unmatched=unmatched,
        rules_applied=rules_applied,
    )


def merge_partitions(result: SplitResult) -> Dict[str, str]:
    """Flatten all partitions (and unmatched keys) back into a single dict."""
    merged: Dict[str, str] = {}
    for partition in result.partitions.values():
        merged.update(partition)
    merged.update(result.unmatched)
    return merged
