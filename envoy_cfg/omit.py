"""omit.py — Remove keys from an env dict by exact match, prefix, or glob pattern."""

from __future__ import annotations

import fnmatch
from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class OmitResult:
    env: Dict[str, str]
    omitted: List[str]
    strategy: str

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"OmitResult(strategy={self.strategy!r}, "
            f"omitted={len(self.omitted)}, remaining={len(self.env)})"
        )

    def is_clean(self) -> bool:
        """Return True when nothing was omitted."""
        return len(self.omitted) == 0


def omit_by_keys(
    env: Dict[str, str],
    keys: List[str],
) -> OmitResult:
    """Remove an explicit list of keys from *env*."""
    omitted = [k for k in keys if k in env]
    result = {k: v for k, v in env.items() if k not in keys}
    return OmitResult(env=result, omitted=sorted(omitted), strategy="keys")


def omit_by_prefix(
    env: Dict[str, str],
    prefix: str,
) -> OmitResult:
    """Remove all keys whose name starts with *prefix*."""
    omitted = [k for k in env if k.startswith(prefix)]
    result = {k: v for k, v in env.items() if not k.startswith(prefix)}
    return OmitResult(env=result, omitted=sorted(omitted), strategy="prefix")


def omit_by_glob(
    env: Dict[str, str],
    pattern: str,
) -> OmitResult:
    """Remove all keys matching a shell-style *pattern* (e.g. ``DB_*``)."""
    omitted = [k for k in env if fnmatch.fnmatchcase(k, pattern)]
    result = {k: v for k, v in env.items() if not fnmatch.fnmatchcase(k, pattern)}
    return OmitResult(env=result, omitted=sorted(omitted), strategy="glob")
