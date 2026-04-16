"""Type casting utilities for environment variable values."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Any

_BOOL_TRUE = {"1", "true", "yes", "on"}
_BOOL_FALSE = {"0", "false", "no", "off"}


@dataclass
class CastResult:
    env: Dict[str, Any]
    casted: Dict[str, str]  # key -> target type label
    errors: Dict[str, str]  # key -> error message

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"CastResult(casted={len(self.casted)}, errors={len(self.errors)})"
        )

    @property
    def is_clean(self) -> bool:
        return len(self.errors) == 0


def _cast_value(value: str, type_hint: str) -> Any:
    """Attempt to cast *value* to the type described by *type_hint*."""
    hint = type_hint.lower().strip()
    if hint == "int":
        return int(value)
    if hint == "float":
        return float(value)
    if hint == "bool":
        low = value.lower().strip()
        if low in _BOOL_TRUE:
            return True
        if low in _BOOL_FALSE:
            return False
        raise ValueError(f"Cannot cast {value!r} to bool")
    if hint == "str":
        return value
    raise ValueError(f"Unknown type hint: {type_hint!r}")


def cast_env(
    env: Dict[str, str],
    schema: Dict[str, str],
) -> CastResult:
    """Cast env values according to *schema* (key -> type hint).

    Keys not present in *schema* are passed through as plain strings.
    """
    result: Dict[str, Any] = dict(env)
    casted: Dict[str, str] = {}
    errors: Dict[str, str] = {}

    for key, type_hint in schema.items():
        if key not in env:
            continue
        try:
            result[key] = _cast_value(env[key], type_hint)
            casted[key] = type_hint
        except (ValueError, TypeError) as exc:
            errors[key] = str(exc)

    return CastResult(env=result, casted=casted, errors=errors)
