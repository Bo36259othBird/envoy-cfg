from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Tuple


@dataclass
class CoerceResult:
    env: Dict[str, str]
    coerced: List[Tuple[str, str, str]] = field(default_factory=list)  # (key, before, after)
    strategy: str = "coerce"

    def __repr__(self) -> str:
        return (
            f"CoerceResult(strategy={self.strategy!r}, "
            f"coerced={len(self.coerced)}, keys={len(self.env)})"
        )

    def is_clean(self) -> bool:
        return len(self.coerced) == 0


_BOOL_TRUE = {"true", "1", "yes", "on"}
_BOOL_FALSE = {"false", "0", "no", "off"}


def _coerce_value(value: str) -> str:
    """Normalise common boolean-like and whitespace-padded values."""
    stripped = value.strip()
    if stripped != value:
        return stripped
    lower = value.lower()
    if lower in _BOOL_TRUE:
        return "true"
    if lower in _BOOL_FALSE:
        return "false"
    return value


def coerce_env(
    env: Dict[str, str],
    *,
    booleans: bool = True,
    strip_whitespace: bool = True,
    keys: List[str] | None = None,
) -> CoerceResult:
    """Coerce env values: normalise booleans and strip surrounding whitespace."""
    result: Dict[str, str] = {}
    coerced: List[Tuple[str, str, str]] = []

    target_keys = set not None else None

    for k, v in env.items():
        if target_keys is not None and k not in target_keys:
            result[k] = v
            continue

        new_v = v
        if strip_whitespace:
            new_v = new_v.strip()
        if booleans:
            lower = new_v.lower()
            if lower in _BOOL_TRUE:
                new_v = "true"
            elif lower in _BOOL_FALSE:
                new_v = "false"

        if new_v != v:
            coerced.append((k, v, new_v))
        result[k] = new_v

    label = "coerce"
    if booleans and strip_whitespace:
        label = "coerce:bool+strip"
    elif booleans:
        label = "coerce:bool"
    elif strip_whitespace:
        label = "coerce:strip"

    return CoerceResult(env=result, coerced=coerced, strategy=label)
