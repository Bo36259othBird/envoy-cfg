"""Alias support: map short names to environment variable keys."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional


@dataclass
class AliasResult:
    """Result of applying an alias map to an env dict."""

    resolved: Dict[str, str]
    unresolved: Dict[str, str]  # alias -> target key that was missing
    applied_count: int

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"AliasResult(applied={self.applied_count}, "
            f"unresolved={list(self.unresolved.keys())})"
        )

    @property
    def is_clean(self) -> bool:
        """True when every alias resolved successfully."""
        return len(self.unresolved) == 0


def apply_aliases(
    env: Dict[str, str],
    aliases: Dict[str, str],
    *,
    overwrite: bool = False,
) -> AliasResult:
    """Inject alias keys into *env* whose values are copied from target keys.

    Parameters
    ----------
    env:
        The source environment mapping.
    aliases:
        Mapping of ``{alias_key: source_key}``.
    overwrite:
        When *True*, overwrite an existing alias key in *env*.

    Returns
    -------
    AliasResult
        Contains the updated env, any unresolved aliases, and a count of
        successfully applied aliases.
    """
    resolved = dict(env)
    unresolved: Dict[str, str] = {}
    applied = 0

    for alias, source_key in aliases.items():
        if source_key not in env:
            unresolved[alias] = source_key
            continue
        if alias in resolved and not overwrite:
            continue
        resolved[alias] = env[source_key]
        applied += 1

    return AliasResult(resolved=resolved, unresolved=unresolved, applied_count=applied)


def strip_aliases(
    env: Dict[str, str],
    aliases: Dict[str, str],
) -> Dict[str, str]:
    """Return a copy of *env* with all alias keys removed."""
    alias_keys = set(aliases.keys())
    return {k: v for k, v in env.items() if k not in alias_keys}


def list_aliases(
    env: Dict[str, str],
    aliases: Dict[str, str],
) -> Dict[str, Optional[str]]:
    """Return a mapping of alias -> resolved value (or None if missing)."""
    return {alias: env.get(src) for alias, src in aliases.items()}
