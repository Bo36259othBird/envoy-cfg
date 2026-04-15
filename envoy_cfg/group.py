"""Group environment variables by prefix, suffix, or custom pattern."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
import re


@dataclass
class GroupResult:
    groups: Dict[str, Dict[str, str]]
    ungrouped: Dict[str, str]
    strategy: str

    def __repr__(self) -> str:
        total = sum(len(v) for v in self.groups.values())
        return (
            f"GroupResult(strategy={self.strategy!r}, groups={len(self.groups)}, "
            f"grouped_keys={total}, ungrouped={len(self.ungrouped)})"
        )

    def is_complete(self) -> bool:
        """Return True if every key was placed in a group."""
        return len(self.ungrouped) == 0

    def all_keys(self) -> List[str]:
        keys = list(self.ungrouped.keys())
        for group_keys in self.groups.values():
            keys.extend(group_keys.keys())
        return keys


def group_by_prefix(
    env: Dict[str, str],
    prefixes: List[str],
    separator: str = "_",
    strip_prefix: bool = False,
) -> GroupResult:
    """Partition env vars into groups based on known prefixes."""
    groups: Dict[str, Dict[str, str]] = {p: {} for p in prefixes}
    ungrouped: Dict[str, str] = {}

    for key, value in env.items():
        matched = False
        for prefix in prefixes:
            full_prefix = prefix + separator
            if key.startswith(full_prefix):
                group_key = key[len(full_prefix):] if strip_prefix else key
                groups[prefix][group_key] = value
                matched = True
                break
        if not matched:
            ungrouped[key] = value

    return GroupResult(groups=groups, ungrouped=ungrouped, strategy="prefix")


def group_by_suffix(
    env: Dict[str, str],
    suffixes: List[str],
    separator: str = "_",
    strip_suffix: bool = False,
) -> GroupResult:
    """Partition env vars into groups based on known suffixes."""
    groups: Dict[str, Dict[str, str]] = {s: {} for s in suffixes}
    ungrouped: Dict[str, str] = {}

    for key, value in env.items():
        matched = False
        for suffix in suffixes:
            full_suffix = separator + suffix
            if key.endswith(full_suffix):
                group_key = key[: -len(full_suffix)] if strip_suffix else key
                groups[suffix][group_key] = value
                matched = True
                break
        if not matched:
            ungrouped[key] = value

    return GroupResult(groups=groups, ungrouped=ungrouped, strategy="suffix")


def group_by_pattern(
    env: Dict[str, str],
    patterns: Dict[str, str],
) -> GroupResult:
    """Group env vars by named regex patterns. patterns maps label -> regex."""
    groups: Dict[str, Dict[str, str]] = {label: {} for label in patterns}
    compiled = {label: re.compile(pat) for label, pat in patterns.items()}
    ungrouped: Dict[str, str] = {}

    for key, value in env.items():
        matched = False
        for label, regex in compiled.items():
            if regex.search(key):
                groups[label][key] = value
                matched = True
                break
        if not matched:
            ungrouped[key] = value

    return GroupResult(groups=groups, ungrouped=ungrouped, strategy="pattern")
