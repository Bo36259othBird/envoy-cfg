"""Key/value transformation utilities for environment variable maps."""

from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional


@dataclass
class TransformResult:
    original: Dict[str, str]
    transformed: Dict[str, str]
    applied: List[str] = field(default_factory=list)

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"TransformResult(keys={len(self.transformed)}, "
            f"transforms={self.applied})"
        )

    @property
    def is_identity(self) -> bool:
        """True when no values changed."""
        return self.original == self.transformed


def transform_keys(
    env: Dict[str, str],
    fn: Callable[[str], str],
    label: str = "key_transform",
) -> TransformResult:
    """Apply *fn* to every key; values are preserved unchanged."""
    transformed = {fn(k): v for k, v in env.items()}
    return TransformResult(original=env, transformed=transformed, applied=[label])


def transform_values(
    env: Dict[str, str],
    fn: Callable[[str, str], str],
    label: str = "value_transform",
    keys: Optional[List[str]] = None,
) -> TransformResult:
    """Apply *fn(key, value)* to every value (or only to *keys* if given)."""
    target_keys = set(keys) if keys is not None else set(env.keys())
    transformed = {
        k: (fn(k, v) if k in target_keys else v)
        for k, v in env.items()
    }
    return TransformResult(original=env, transformed=transformed, applied=[label])


def apply_transforms(
    env: Dict[str, str],
    steps: List[Dict],
) -> TransformResult:
    """Run a sequence of named transform steps.

    Each step dict must have a ``"type"`` key with one of:
      - ``"keys_upper"``  – uppercase all keys
      - ``"keys_lower"``  – lowercase all keys
      - ``"values_upper"`` – uppercase all values
      - ``"values_strip"`` – strip whitespace from all values
      - ``"values_lower"`` – lowercase all values
    """
    current = dict(env)
    applied: List[str] = []

    _key_fns: Dict[str, Callable[[str], str]] = {
        "keys_upper": str.upper,
        "keys_lower": str.lower,
    }
    _val_fns: Dict[str, Callable[[str, str], str]] = {
        "values_upper": lambda k, v: v.upper(),
        "values_lower": lambda k, v: v.lower(),
        "values_strip": lambda k, v: v.strip(),
    }

    for step in steps:
        step_type = step.get("type", "")
        if step_type in _key_fns:
            result = transform_keys(current, _key_fns[step_type], label=step_type)
            current = result.transformed
            applied.append(step_type)
        elif step_type in _val_fns:
            result = transform_values(
                current,
                _val_fns[step_type],
                label=step_type,
                keys=step.get("keys"),
            )
            current = result.transformed
            applied.append(step_type)
        else:
            raise ValueError(f"Unknown transform type: {step_type!r}")

    return TransformResult(original=env, transformed=current, applied=applied)
