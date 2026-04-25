from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict

from envoy_cfg.masking import is_secret_key


@dataclass
class CountResult:
    total: int
    secret_count: int
    plain_count: int
    empty_count: int
    non_empty_count: int
    by_prefix: Dict[str, int] = field(default_factory=dict)
    separator: str = "_"

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"CountResult(total={self.total}, secret={self.secret_count}, "
            f"plain={self.plain_count}, empty={self.empty_count}, "
            f"non_empty={self.non_empty_count}, prefixes={len(self.by_prefix)})"
        )

    def is_empty(self) -> bool:
        return self.total == 0


def count_env(
    env: Dict[str, str],
    *,
    prefix_depth: int = 1,
    separator: str = "_",
) -> CountResult:
    """Count keys in *env* with breakdowns by type, emptiness, and prefix.

    Args:
        env: The environment mapping to analyse.
        prefix_depth: How many separator-delimited segments form a prefix
            bucket (default 1, e.g. ``DB`` from ``DB_HOST``).
        separator: Token separator used to derive prefixes (default ``_``).

    Returns:
        A :class:`CountResult` with aggregated counts.
    """
    total = len(env)
    secret_count = sum(1 for k in env if is_secret_key(k))
    plain_count = total - secret_count
    empty_count = sum(1 for v in env.values() if v == "")
    non_empty_count = total - empty_count

    by_prefix: Dict[str, int] = {}
    for key in env:
        parts = key.split(separator)
        prefix = separator.join(parts[:prefix_depth]) if len(parts) > prefix_depth else key
        by_prefix[prefix] = by_prefix.get(prefix, 0) + 1

    return CountResult(
        total=total,
        secret_count=secret_count,
        plain_count=plain_count,
        empty_count=empty_count,
        non_empty_count=non_empty_count,
        by_prefix=by_prefix,
        separator=separator,
    )
