"""Reorder environment variable keys by various strategies."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class ReorderResult:
    original: Dict[str, str]
    reordered: Dict[str, str]
    strategy: str
    moved: int = 0

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"<ReorderResult strategy={self.strategy!r} "
            f"keys={len(self.reordered)} moved={self.moved}>"
        )

    def is_identity(self) -> bool:
        """Return True when the key order did not change."""
        return list(self.original.keys()) == list(self.reordered.keys())


def reorder_alphabetical(
    env: Dict[str, str], reverse: bool = False
) -> ReorderResult:
    """Sort keys alphabetically (A→Z by default, Z→A when reverse=True)."""
    original_keys = list(env.keys())
    sorted_keys = sorted(env.keys(), reverse=reverse)
    reordered = {k: env[k] for k in sorted_keys}
    moved = sum(1 for a, b in zip(original_keys, sorted_keys) if a != b)
    strategy = "alphabetical_desc" if reverse else "alphabetical"
    return ReorderResult(
        original=dict(env),
        reordered=reordered,
        strategy=strategy,
        moved=moved,
    )


def reorder_by_prefix(
    env: Dict[str, str], prefix_order: List[str]
) -> ReorderResult:
    """Group keys by prefix according to *prefix_order*; unmatched keys go last."""
    original_keys = list(env.keys())
    buckets: Dict[str, List[str]] = {p: [] for p in prefix_order}
    remainder: List[str] = []

    for key in env:
        matched = False
        for prefix in prefix_order:
            if key.startswith(prefix):
                buckets[prefix].append(key)
                matched = True
                break
        if not matched:
            remainder.append(key)

    ordered_keys: List[str] = []
    for prefix in prefix_order:
        ordered_keys.extend(sorted(buckets[prefix]))
    ordered_keys.extend(remainder)

    reordered = {k: env[k] for k in ordered_keys}
    moved = sum(1 for a, b in zip(original_keys, ordered_keys) if a != b)
    return ReorderResult(
        original=dict(env),
        reordered=reordered,
        strategy="by_prefix",
        moved=moved,
    )


def reorder_secrets_last(env: Dict[str, str]) -> ReorderResult:
    """Move secret keys (as detected by masking.is_secret_key) to the end."""
    from envoy_cfg.masking import is_secret_key

    original_keys = list(env.keys())
    non_secrets = [k for k in env if not is_secret_key(k)]
    secrets = [k for k in env if is_secret_key(k)]
    ordered_keys = non_secrets + secrets
    reordered = {k: env[k] for k in ordered_keys}
    moved = sum(1 for a, b in zip(original_keys, ordered_keys) if a != b)
    return ReorderResult(
        original=dict(env),
        reordered=reordered,
        strategy="secrets_last",
        moved=moved,
    )
