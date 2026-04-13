"""Validation utilities for environment variable configs."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional

# Valid env var key pattern: uppercase letters, digits, underscores, must not start with digit
_KEY_PATTERN = re.compile(r'^[A-Za-z_][A-Za-z0-9_]*$')

# Maximum allowed length for a key or value
MAX_KEY_LENGTH = 128
MAX_VALUE_LENGTH = 4096


@dataclass
class ValidationError:
    key: str
    message: str

    def __repr__(self) -> str:
        return f"ValidationError(key={self.key!r}, message={self.message!r})"


@dataclass
class ValidationResult:
    errors: List[ValidationError] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        return len(self.errors) == 0

    def add_error(self, key: str, message: str) -> None:
        self.errors.append(ValidationError(key=key, message=message))

    def __repr__(self) -> str:
        return f"ValidationResult(valid={self.is_valid}, errors={len(self.errors)})"


def validate_key(key: str) -> Optional[str]:
    """Validate a single environment variable key.
    Returns an error message string if invalid, None if valid.
    """
    if not key:
        return "Key must not be empty"
    if len(key) > MAX_KEY_LENGTH:
        return f"Key exceeds maximum length of {MAX_KEY_LENGTH}"
    if not _KEY_PATTERN.match(key):
        return "Key must start with a letter or underscore and contain only letters, digits, or underscores"
    return None


def validate_value(key: str, value: str) -> Optional[str]:
    """Validate a single environment variable value.
    Returns an error message string if invalid, None if valid.
    """
    if len(value) > MAX_VALUE_LENGTH:
        return f"Value for '{key}' exceeds maximum length of {MAX_VALUE_LENGTH}"
    return None


def validate_env(env: Dict[str, str]) -> ValidationResult:
    """Validate an entire environment variable mapping.
    Returns a ValidationResult with any errors found.
    """
    result = ValidationResult()
    for key, value in env.items():
        key_error = validate_key(key)
        if key_error:
            result.add_error(key, key_error)
        else:
            value_error = validate_value(key, value)
            if value_error:
                result.add_error(key, value_error)
    return result
