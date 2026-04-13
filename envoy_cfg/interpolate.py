"""Environment variable interpolation with cross-target reference support."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
import re

_REF_PATTERN = re.compile(r"\$\{([^}]+)\}")


@dataclass
class InterpolateResult:
    resolved: Dict[str, str] = field(default_factory=dict)
    unresolved_keys: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

    @property
    def is_clean(self) -> bool:
        return not self.unresolved_keys and not self.errors

    def __repr__(self) -> str:
        return (
            f"InterpolateResult(resolved={len(self.resolved)}, "
            f"unresolved={self.unresolved_keys}, errors={self.errors})"
        )


def _resolve_refs(
    value: str,
    env: Dict[str, str],
    visited: Optional[List[str]] = None,
) -> Optional[str]:
    """Recursively resolve ${VAR} references in a value string."""
    if visited is None:
        visited = []

    def replacer(match: re.Match) -> str:
        ref_key = match.group(1)
        if ref_key in visited:
            raise ValueError(f"Circular reference detected: {ref_key}")
        if ref_key not in env:
            raise KeyError(ref_key)
        nested = env[ref_key]
        if _REF_PATTERN.search(nested):
            return _resolve_refs(nested, env, visited + [ref_key])
        return nested

    return _REF_PATTERN.sub(replacer, value)


def interpolate_env(
    env: Dict[str, str],
    overlay: Optional[Dict[str, str]] = None,
) -> InterpolateResult:
    """Interpolate all ${VAR} references in env values.

    Args:
        env: The environment dict to interpolate.
        overlay: Optional extra variables usable as reference sources only.

    Returns:
        InterpolateResult with resolved values and any issues.
    """
    lookup = {**env}
    if overlay:
        lookup.update(overlay)

    result = InterpolateResult()

    for key, raw_value in env.items():
        if not _REF_PATTERN.search(raw_value):
            result.resolved[key] = raw_value
            continue
        try:
            resolved = _resolve_refs(raw_value, lookup)
            result.resolved[key] = resolved
        except KeyError as exc:
            missing = str(exc).strip("'")
            result.unresolved_keys.append(key)
            result.errors.append(f"{key}: unresolved reference '${{{missing}}}'")
            result.resolved[key] = raw_value
        except ValueError as exc:
            result.unresolved_keys.append(key)
            result.errors.append(f"{key}: {exc}")
            result.resolved[key] = raw_value

    return result
