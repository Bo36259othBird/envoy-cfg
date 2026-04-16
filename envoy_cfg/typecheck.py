from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List


TYPE_VALIDATORS = {
    "int": lambda v: v.lstrip("-").isdigit(),
    "float": lambda v: _is_float(v),
    "bool": lambda v: v.lower() in ("true", "false", "1", "0", "yes", "no"),
    "url": lambda v: v.startswith(("http://", "https://")),
    "nonempty": lambda v: len(v.strip()) > 0,
}


def _is_float(v: str) -> bool:
    try:
        float(v)
        return True
    except ValueError:
        return False


@dataclass
class TypeCheckIssue:
    key: str
    value: str
    expected_type: str

    def __repr__(self) -> str:
        return f"TypeCheckIssue(key={self.key!r}, expected={self.expected_type!r}, value={self.value!r})"


@dataclass
class TypeCheckResult:
    issues: List[TypeCheckIssue] = field(default_factory=list)
    checked: int = 0

    @property
    def is_clean(self) -> bool:
        return len(self.issues) == 0

    def __repr__(self) -> str:
        return f"TypeCheckResult(checked={self.checked}, issues={len(self.issues)})"


def typecheck_env(
    env: Dict[str, str],
    schema: Dict[str, str],
) -> TypeCheckResult:
    """Validate env values against a type schema mapping key -> type name."""
    issues: List[TypeCheckIssue] = []
    checked = 0

    for key, expected_type in schema.items():
        if key not in env:
            continue
        value = env[key]
        validator = TYPE_VALIDATORS.get(expected_type)
        if validator is None:
            continue
        checked += 1
        if not validator(value):
            issues.append(TypeCheckIssue(key=key, value=value, expected_type=expected_type))

    return TypeCheckResult(issues=issues, checked=checked)
