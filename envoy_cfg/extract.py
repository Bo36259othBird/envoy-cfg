from dataclasses import dataclass, field
from typing import Dict, List, Optional
import re


@dataclass
class ExtractResult:
    extracted: Dict[str, str]
    remaining: Dict[str, str]
    pattern: str
    strategy: str

    def __repr__(self) -> str:
        return (
            f"ExtractResult(strategy={self.strategy!r}, "
            f"extracted={len(self.extracted)}, remaining={len(self.remaining)})"
        )

    def is_empty(self) -> bool:
        return len(self.extracted) == 0


def extract_by_prefix(env: Dict[str, str], prefix: str, strip: bool = False) -> ExtractResult:
    """Extract keys that start with the given prefix."""
    if not prefix:
        raise ValueError("prefix must not be empty")
    extracted: Dict[str, str] = {}
    remaining: Dict[str, str] = {}
    for k, v in env.items():
        if k.startswith(prefix):
            out_key = k[len(prefix):] if strip else k
            extracted[out_key] = v
        else:
            remaining[k] = v
    return ExtractResult(
        extracted=extracted,
        remaining=remaining,
        pattern=prefix,
        strategy="prefix",
    )


def extract_by_regex(env: Dict[str, str], pattern: str, strip: bool = False) -> ExtractResult:
    """Extract keys matching the given regex pattern."""
    try:
        compiled = re.compile(pattern)
    except re.error as exc:
        raise ValueError(f"invalid regex pattern: {exc}") from exc
    extracted: Dict[str, str] = {}
    remaining: Dict[str, str] = {}
    for k, v in env.items():
        m = compiled.search(k)
        if m:
            out_key = k.replace(m.group(), "", 1) if strip else k
            extracted[out_key] = v
        else:
            remaining[k] = v
    return ExtractResult(
        extracted=extracted,
        remaining=remaining,
        pattern=pattern,
        strategy="regex",
    )
