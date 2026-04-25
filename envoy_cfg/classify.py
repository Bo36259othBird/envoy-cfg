from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from envoy_cfg.masking import is_secret_key

_BOOL_VALUES = {"true", "false", "yes", "no", "1", "0", "on", "off"}
_INT_PATTERN = None

import re

_INT_RE = re.compile(r"^-?\d+$")
_FLOAT_RE = re.compile(r"^-?\d+\.\d+$")
_URL_RE = re.compile(r"^https?://", re.IGNORECASE)
_PATH_RE = re.compile(r"^[/~]")


def _classify_value(value: str) -> str:
    if not value:
        return "empty"
    if value.lower() in _BOOL_VALUES:
        return "bool"
    if _INT_RE.match(value):
        return "int"
    if _FLOAT_RE.match(value):
        return "float"
    if _URL_RE.match(value):
        return "url"
    if _PATH_RE.match(value):
        return "path"
    return "string"


@dataclass
class ClassifyEntry:
    key: str
    value_type: str
    is_secret: bool

    def to_dict(self) -> Dict[str, object]:
        return {"key": self.key, "value_type": self.value_type, "is_secret": self.is_secret}

    def __repr__(self) -> str:  # pragma: no cover
        flag = " [secret]" if self.is_secret else ""
        return f"ClassifyEntry({self.key}: {self.value_type}{flag})"


@dataclass
class ClassifyResult:
    entries: List[ClassifyEntry] = field(default_factory=list)
    strategy: str = "default"

    @property
    def is_clean(self) -> bool:
        """True when every entry is a plain non-secret string."""
        return all(e.value_type == "string" and not e.is_secret for e in self.entries)

    @property
    def by_type(self) -> Dict[str, List[str]]:
        result: Dict[str, List[str]] = {}
        for e in self.entries:
            result.setdefault(e.value_type, []).append(e.key)
        return result

    @property
    def secret_keys(self) -> List[str]:
        return [e.key for e in self.entries if e.is_secret]

    def __repr__(self) -> str:  # pragma: no cover
        return f"ClassifyResult(entries={len(self.entries)}, strategy={self.strategy!r})"


def classify_env(env: Dict[str, str], strategy: str = "default") -> ClassifyResult:
    """Classify every key in *env* by inferred value type and secret status."""
    entries = [
        ClassifyEntry(
            key=k,
            value_type=_classify_value(v),
            is_secret=is_secret_key(k),
        )
        for k, v in sorted(env.items())
    ]
    return ClassifyResult(entries=entries, strategy=strategy)
