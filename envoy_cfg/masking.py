"""Secret masking utilities for envoy-cfg.

Provides functions to detect and mask sensitive environment variable
values before display or logging.
"""

import re
from typing import Any

# Patterns that indicate a key likely holds a secret value
SECRET_KEY_PATTERNS: list[re.Pattern] = [
    re.compile(r"(?i)(password|passwd|pwd)"),
    re.compile(r"(?i)(secret)"),
    re.compile(r"(?i)(api[_-]?key)"),
    re.compile(r"(?i)(auth[_-]?token|access[_-]?token)"),
    re.compile(r"(?i)(private[_-]?key)"),
    re.compile(r"(?i)(credentials?)"),
    re.compile(r"(?i)(connection[_-]?string|conn[_-]?str)"),
]

MASK_PLACEHOLDER = "********"


def is_secret_key(key: str) -> bool:
    """Return True if the key name suggests it holds a sensitive value."""
    return any(pattern.search(key) for pattern in SECRET_KEY_PATTERNS)


def mask_value(value: Any) -> str:
    """Return a masked representation of a secret value."""
    if not isinstance(value, str) or len(value) == 0:
        return MASK_PLACEHOLDER
    # Numeric-only secrets do not have a safe prefix to reveal: even the first
    # digits can expose ports, account IDs, PINs, or generated numeric tokens.
    if value.isdigit():
        return MASK_PLACEHOLDER
    # Reveal only the first 2 characters for non-trivial values
    if len(value) <= 4:
        return MASK_PLACEHOLDER
    return value[:2] + "*" * (len(value) - 2)


def mask_env(env: dict[str, str], *, reveal: bool = False) -> dict[str, str]:
    """Return a copy of *env* with secret values masked.

    Args:
        env: Mapping of environment variable names to their values.
        reveal: When True, values are returned unmasked (e.g. for export).

    Returns:
        A new dict safe for display or logging.
    """
    if reveal:
        return dict(env)
    return {
        key: (mask_value(value) if is_secret_key(key) else value)
        for key, value in env.items()
    }
