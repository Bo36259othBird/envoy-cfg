"""Flatten and unflatten nested environment variable structures using delimiter-based keys."""

from dataclasses import dataclass, field
from typing import Dict, Optional


@dataclass
class FlattenResult:
    flattened: Dict[str, str]
    original_count: int
    flat_count: int
    delimiter: str

    def __repr__(self) -> str:
        return (
            f"<FlattenResult keys={self.flat_count} "
            f"original={self.original_count} delimiter={self.delimiter!r}>"
        )

    @property
    def is_expanded(self) -> bool:
        return self.flat_count > self.original_count


def flatten_env(
    env: Dict[str, str],
    delimiter: str = "__",
    prefix: Optional[str] = None,
) -> FlattenResult:
    """Flatten a dict by splitting keys on the delimiter into dotted paths.

    Keys that do not contain the delimiter are passed through unchanged.
    Optionally filter to only keys beginning with `prefix`.

    Args:
        env: The environment variable dictionary to flatten.
        delimiter: The string used to split keys into path segments. Defaults to "__".
        prefix: If provided, only keys starting with this prefix are included.

    Returns:
        A FlattenResult containing the flattened dict and metadata.

    Raises:
        ValueError: If delimiter is an empty string.
    """
    if not delimiter:
        raise ValueError("delimiter must be a non-empty string")

    original_count = len(env)
    flattened: Dict[str, str] = {}

    for key, value in env.items():
        if prefix and not key.startswith(prefix):
            continue
        parts = key.split(delimiter)
        flat_key = ".".join(p.lower() for p in parts if p)
        flattened[flat_key] = value

    return FlattenResult(
        flattened=flattened,
        original_count=original_count,
        flat_count=len(flattened),
        delimiter=delimiter,
    )


def unflatten_env(
    env: Dict[str, str],
    delimiter: str = "__",
) -> Dict[str, str]:
    """Reverse flatten_env: convert dotted flat keys back to delimiter-separated uppercase keys.

    Args:
        env: A dictionary with dotted flat keys (as produced by flatten_env).
        delimiter: The delimiter to use when joining key segments. Defaults to "__".

    Returns:
        A dictionary with restored delimiter-separated uppercase keys.

    Raises:
        ValueError: If delimiter is an empty string.
    """
    if not delimiter:
        raise ValueError("delimiter must be a non-empty string")

    result: Dict[str, str] = {}
    for key, value in env.items():
        parts = key.split(".")
        restored_key = delimiter.join(p.upper() for p in parts if p)
        result[restored_key] = value
    return result
