"""Filter environment variables by value patterns or conditions."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
import fnmatch
import re


@dataclass
class FilterResult:
    selected: Dict[str, str]
    excluded: Dict[str, str]
    strategy: str

    def __repr__(self) -> str:
        return (
            f"FilterResult(strategy={self.strategy!r}, "
            f"selected={len(self.selected)}, excluded={len(self.excluded)})"
        )

    def is_empty(self) -> bool:
        return len(self.selected) == 0


def filter_by_value_glob(env: Dict[str, str], pattern: str) -> FilterResult:
    """Keep keys whose values match a glob pattern."""
    selected = {k: v for k, v in env.items() if fnmatch.fnmatch(v, pattern)}
    excluded = {k: v for k, v in env.items() if k not in selected}
    return FilterResult(selected=selected, excluded=excluded, strategy=f"value_glob:{pattern}")


def filter_by_value_regex(env: Dict[str, str], pattern: str) -> FilterResult:
    """Keep keys whose values match a regular expression."""
    compiled = re.compile(pattern)
    selected = {k: v for k, v in env.items() if compiled.search(v)}
    excluded = {k: v for k, v in env.items() if k not in selected}
    return FilterResult(selected=selected, excluded=excluded, strategy=f"value_regex:{pattern}")


def filter_by_empty_values(env: Dict[str, str], *, keep_empty: bool = False) -> FilterResult:
    """Filter keys based on whether their values are empty."""
    if keep_empty:
        selected = {k: v for k, v in env.items() if not v.strip()}
    else:
        selected = {k: v for k, v in env.items() if v.strip()}
    excluded = {k: v for k, v in env.items() if k not in selected}
    strategy = "empty_values" if keep_empty else "non_empty_values"
    return FilterResult(selected=selected, excluded=excluded, strategy=strategy)


def filter_by_key_glob(env: Dict[str, str], pattern: str) -> FilterResult:
    """Keep keys whose names match a glob pattern."""
    selected = {k: v for k, v in env.items() if fnmatch.fnmatch(k, pattern)}
    excluded = {k: v for k, v in env.items() if k not in selected}
    return FilterResult(selected=selected, excluded=excluded, strategy=f"key_glob:{pattern}")
