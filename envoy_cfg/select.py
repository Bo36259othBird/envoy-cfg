"""Select a subset of env keys by pattern or explicit list."""
from __future__ import annotations

import fnmatch
import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class SelectResult:
    selected: Dict[str, str]
    excluded: Dict[str, str]
    strategy: str
    pattern: Optional[str] = None

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"SelectResult(strategy={self.strategy!r}, "
            f"selected={len(self.selected)}, excluded={len(self.excluded)})"
        )

    @property
    def is_empty(self) -> bool:
        return len(self.selected) == 0


def select_by_keys(env: Dict[str, str], keys: List[str]) -> SelectResult:
    """Return only the explicitly listed keys from env."""
    if not keys:
        raise ValueError("keys list must not be empty")
    selected = {k: v for k, v in env.items() if k in keys}
    excluded = {k: v for k, v in env.items() if k not in keys}
    return SelectResult(selected=selected, excluded=excluded, strategy="keys")


def select_by_glob(env: Dict[str, str], pattern: str) -> SelectResult:
    """Return keys matching a glob pattern (e.g. 'DB_*')."""
    if not pattern:
        raise ValueError("pattern must not be empty")
    selected = {k: v for k, v in env.items() if fnmatch.fnmatch(k, pattern)}
    excluded = {k: v for k, v in env.items() if k not in selected}
    return SelectResult(
        selected=selected, excluded=excluded, strategy="glob", pattern=pattern
    )


def select_by_regex(env: Dict[str, str], pattern: str) -> SelectResult:
    """Return keys matching a regular expression."""
    if not pattern:
        raise ValueError("pattern must not be empty")
    try:
        rx = re.compile(pattern)
    except re.error as exc:
        raise ValueError(f"invalid regex pattern: {exc}") from exc
    selected = {k: v for k, v in env.items() if rx.search(k)}
    excluded = {k: v for k, v in env.items() if k not in selected}
    return SelectResult(
        selected=selected, excluded=excluded, strategy="regex", pattern=pattern
    )
