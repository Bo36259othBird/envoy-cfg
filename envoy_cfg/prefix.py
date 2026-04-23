from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class PrefixResult:
    env: Dict[str, str]
    strategy: str
    prefix: str
    affected: List[str] = field(default_factory=list)
    skipped: List[str] = field(default_factory=list)

    def __repr__(self) -> str:
        return (
            f"PrefixResult(strategy={self.strategy!r}, prefix={self.prefix!r}, "
            f"affected={len(self.affected)}, skipped={len(self.skipped)})"
        )

    def is_clean(self) -> bool:
        return len(self.skipped) == 0


def add_prefix(
    env: Dict[str, str],
    prefix: str,
    *,
    skip_existing: bool = True,
    keys: Optional[List[str]] = None,
) -> PrefixResult:
    """Add a prefix to all keys (or a subset of keys) in env."""
    if not prefix:
        raise ValueError("prefix must not be empty")

    result: Dict[str, str] = {}
    affected: List[str] = []
    skipped: List[str] = []
    target_keys = set(keys) if keys is not None else set(env.keys())

    for k, v in env.items():
        if k not in target_keys:
            result[k] = v
            continue
        new_key = f"{prefix}{k}"
        if skip_existing and new_key in env:
            result[k] = v
            skipped.append(k)
        else:
            result[new_key] = v
            affected.append(k)

    return PrefixResult(
        env=result,
        strategy="add_prefix",
        prefix=prefix,
        affected=sorted(affected),
        skipped=sorted(skipped),
    )


def remove_prefix(
    env: Dict[str, str],
    prefix: str,
    *,
    keys: Optional[List[str]] = None,
) -> PrefixResult:
    """Remove a prefix from matching keys in env."""
    if not prefix:
        raise ValueError("prefix must not be empty")

    result: Dict[str, str] = {}
    affected: List[str] = []
    skipped: List[str] = []
    target_keys = set(keys) if keys is not None else set(env.keys())

    for k, v in env.items():
        if k not in target_keys or not k.startswith(prefix):
            result[k] = v
            if k in target_keys and not k.startswith(prefix):
                skipped.append(k)
            continue
        new_key = k[len(prefix):]
        result[new_key] = v
        affected.append(k)

    return PrefixResult(
        env=result,
        strategy="remove_prefix",
        prefix=prefix,
        affected=sorted(affected),
        skipped=sorted(skipped),
    )
