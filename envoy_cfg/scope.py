"""Scope filtering: restrict env vars to a named subset by prefix or explicit key list."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class ScopeResult:
    scope_name: str
    original: Dict[str, str]
    scoped: Dict[str, str]
    excluded_keys: List[str] = field(default_factory=list)

    def __repr__(self) -> str:
        return (
            f"<ScopeResult scope={self.scope_name!r} "
            f"kept={len(self.scoped)} excluded={len(self.excluded_keys)}>"
        )

    @property
    def is_empty(self) -> bool:
        return len(self.scoped) == 0


def scope_by_prefix(
    env: Dict[str, str],
    prefix: str,
    strip_prefix: bool = False,
    scope_name: Optional[str] = None,
) -> ScopeResult:
    """Return only keys that start with *prefix*.

    If *strip_prefix* is True the prefix is removed from the returned keys.
    """
    if not prefix:
        raise ValueError("prefix must not be empty")

    name = scope_name or prefix.rstrip("_")
    scoped: Dict[str, str] = {}
    excluded: List[str] = []

    for key, value in env.items():
        if key.startswith(prefix):
            out_key = key[len(prefix):] if strip_prefix else key
            scoped[out_key] = value
        else:
            excluded.append(key)

    return ScopeResult(
        scope_name=name,
        original=dict(env),
        scoped=scoped,
        excluded_keys=sorted(excluded),
    )


def scope_by_keys(
    env: Dict[str, str],
    keys: List[str],
    scope_name: str = "custom",
) -> ScopeResult:
    """Return only the explicitly listed *keys* from *env*."""
    if not keys:
        raise ValueError("keys list must not be empty")

    scoped = {k: env[k] for k in keys if k in env}
    excluded = [k for k in env if k not in keys]

    return ScopeResult(
        scope_name=scope_name,
        original=dict(env),
        scoped=scoped,
        excluded_keys=sorted(excluded),
    )


def merge_scopes(*results: ScopeResult) -> Dict[str, str]:
    """Merge multiple ScopeResult.scoped dicts; later results win on conflict."""
    merged: Dict[str, str] = {}
    for result in results:
        merged.update(result.scoped)
    return merged
