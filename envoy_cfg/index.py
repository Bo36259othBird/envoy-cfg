"""Build a searchable index over an env dict for fast key/value lookups."""
from __future__ import annotations

from dataclasses import dataclass, field
from fnmatch import fnmatch
from typing import Dict, List, Optional


@dataclass
class IndexResult:
    index: Dict[str, str]
    strategy: str
    total: int

    def __repr__(self) -> str:  # pragma: no cover
        return f"<IndexResult strategy={self.strategy!r} total={self.total}>"

    def is_empty(self) -> bool:
        return self.total == 0

    def lookup(self, key: str) -> Optional[str]:
        """Return value for *key* or None if not present."""
        return self.index.get(key)

    def search_keys(self, pattern: str) -> List[str]:
        """Return all keys whose name matches *pattern* (glob)."""
        return sorted(k for k in self.index if fnmatch(k, pattern))

    def search_values(self, pattern: str) -> Dict[str, str]:
        """Return key/value pairs where the value matches *pattern* (glob)."""
        return {k: v for k, v in self.index.items() if fnmatch(v, pattern)}


def build_index(env: Dict[str, str], case_insensitive: bool = False) -> IndexResult:
    """Build an IndexResult from *env*.

    If *case_insensitive* is True all keys are normalised to upper-case in the
    stored index so that lookups are case-insensitive.
    """
    if not isinstance(env, dict):
        raise TypeError("env must be a dict")

    if case_insensitive:
        index = {k.upper(): v for k, v in env.items()}
        strategy = "case_insensitive"
    else:
        index = dict(env)
        strategy = "exact"

    return IndexResult(index=index, strategy=strategy, total=len(index))
