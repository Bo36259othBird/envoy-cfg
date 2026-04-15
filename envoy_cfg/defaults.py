"""Apply and strip default values for environment variable configs."""

from dataclasses import dataclass, field
from typing import Dict, Optional


@dataclass
class DefaultsResult:
    env: Dict[str, str]
    applied: Dict[str, str]  # keys that were filled in from defaults
    skipped: Dict[str, str]  # keys already present, defaults not applied

    def __repr__(self) -> str:
        return (
            f"DefaultsResult(applied={len(self.applied)}, "
            f"skipped={len(self.skipped)}, total={len(self.env)})"
        )

    @property
    def is_clean(self) -> bool:
        """True when no defaults were needed (all keys already present)."""
        return len(self.applied) == 0


def apply_defaults(
    env: Dict[str, str],
    defaults: Dict[str, str],
    overwrite: bool = False,
) -> DefaultsResult:
    """Merge *defaults* into *env*.

    Args:
        env: The base environment mapping.
        defaults: Key/value pairs to inject when missing from *env*.
        overwrite: When True, apply defaults even if the key already exists.

    Returns:
        A :class:`DefaultsResult` describing what changed.
    """
    if not defaults:
        return DefaultsResult(env=dict(env), applied={}, skipped={})

    result = dict(env)
    applied: Dict[str, str] = {}
    skipped: Dict[str, str] = {}

    for key, value in defaults.items():
        if key not in env or overwrite:
            if key in env and overwrite:
                skipped[key] = env[key]  # record what was overwritten
            result[key] = value
            applied[key] = value
        else:
            skipped[key] = env[key]

    return DefaultsResult(env=result, applied=applied, skipped=skipped)


def strip_defaults(
    env: Dict[str, str],
    defaults: Dict[str, str],
) -> Dict[str, str]:
    """Remove keys from *env* whose value exactly matches the default.

    Useful for producing a minimal diff against a known baseline.

    Args:
        env: Current environment mapping.
        defaults: Reference defaults to compare against.

    Returns:
        A new dict with default-valued keys removed.
    """
    return {k: v for k, v in env.items() if defaults.get(k) != v}
