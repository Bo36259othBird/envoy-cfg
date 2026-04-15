"""Normalize environment variable keys and values to a canonical form."""

from dataclasses import dataclass, field
from typing import Dict, List, Tuple


@dataclass
class NormalizeResult:
    original: Dict[str, str]
    normalized: Dict[str, str]
    changes: List[Tuple[str, str, str]]  # (key, old_value, new_value)
    label: str = "normalize"

    def __repr__(self) -> str:
        return (
            f"NormalizeResult(keys={len(self.normalized)}, "
            f"changed={len(self.changes)}, label={self.label!r})"
        )

    def is_clean(self) -> bool:
        """Return True if no changes were made."""
        return len(self.changes) == 0


def normalize_keys(
    env: Dict[str, str],
    *,
    uppercase: bool = True,
    strip_whitespace: bool = True,
    label: str = "normalize_keys",
) -> NormalizeResult:
    """Normalize environment variable keys.

    Args:
        env: Source environment dict.
        uppercase: Convert keys to uppercase when True.
        strip_whitespace: Strip leading/trailing whitespace from keys.
        label: Label for the result.

    Returns:
        NormalizeResult with normalized env and list of changes.
    """
    normalized: Dict[str, str] = {}
    changes: List[Tuple[str, str, str]] = []

    for key, value in env.items():
        new_key = key
        if strip_whitespace:
            new_key = new_key.strip()
        if uppercase:
            new_key = new_key.upper()
        normalized[new_key] = value
        if new_key != key:
            changes.append((key, key, new_key))

    return NormalizeResult(
        original=dict(env),
        normalized=normalized,
        changes=changes,
        label=label,
    )


def normalize_values(
    env: Dict[str, str],
    *,
    strip_whitespace: bool = True,
    collapse_newlines: bool = True,
    label: str = "normalize_values",
) -> NormalizeResult:
    """Normalize environment variable values.

    Args:
        env: Source environment dict.
        strip_whitespace: Strip leading/trailing whitespace from values.
        collapse_newlines: Replace newline characters with a space.
        label: Label for the result.

    Returns:
        NormalizeResult with normalized env and list of changes.
    """
    normalized: Dict[str, str] = {}
    changes: List[Tuple[str, str, str]] = []

    for key, value in env.items():
        new_value = value
        if strip_whitespace:
            new_value = new_value.strip()
        if collapse_newlines:
            new_value = new_value.replace("\n", " ").replace("\r", "")
        normalized[key] = new_value
        if new_value != value:
            changes.append((key, value, new_value))

    return NormalizeResult(
        original=dict(env),
        normalized=normalized,
        changes=changes,
        label=label,
    )
