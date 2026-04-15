"""Sanitize environment variable values by stripping unsafe characters."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional

_UNSAFE_CHARS = ["\x00", "\r", "\n", "\t"]
_UNSAFE_NAMES = {"__proto__", "constructor", "prototype"}


@dataclass
class SanitizeResult:
    original: Dict[str, str]
    sanitized: Dict[str, str]
    stripped_keys: List[str] = field(default_factory=list)
    modified_values: List[str] = field(default_factory=list)

    def __repr__(self) -> str:
        return (
            f"SanitizeResult(keys_stripped={len(self.stripped_keys)}, "
            f"values_modified={len(self.modified_values)})"
        )

    @property
    def is_clean(self) -> bool:
        return not self.stripped_keys and not self.modified_values


def _sanitize_key(key: str) -> Optional[str]:
    """Return None if the key should be dropped, else a cleaned key."""
    cleaned = key.strip()
    if not cleaned:
        return None
    if cleaned in _UNSAFE_NAMES:
        return None
    for ch in _UNSAFE_CHARS:
        if ch in cleaned:
            return None
    return cleaned


def _sanitize_value(value: str) -> str:
    """Strip null bytes and control characters from a value."""
    result = value
    for ch in _UNSAFE_CHARS:
        result = result.replace(ch, "")
    return result


def sanitize_env(
    env: Dict[str, str],
    strip_whitespace: bool = True,
) -> SanitizeResult:
    """Sanitize all keys and values in an env dict.

    Args:
        env: The raw environment mapping.
        strip_whitespace: If True, strip leading/trailing whitespace from values.

    Returns:
        A SanitizeResult with the cleaned env and a record of changes.
    """
    sanitized: Dict[str, str] = {}
    stripped_keys: List[str] = []
    modified_values: List[str] = []

    for key, value in env.items():
        clean_key = _sanitize_key(key)
        if clean_key is None:
            stripped_keys.append(key)
            continue

        clean_value = _sanitize_value(value)
        if strip_whitespace:
            clean_value = clean_value.strip()

        if clean_value != value:
            modified_values.append(clean_key)

        sanitized[clean_key] = clean_value

    return SanitizeResult(
        original=dict(env),
        sanitized=sanitized,
        stripped_keys=stripped_keys,
        modified_values=modified_values,
    )
