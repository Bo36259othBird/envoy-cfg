"""Sample a subset of environment variable keys from an env dict."""
from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class SampleResult:
    sampled: Dict[str, str]
    excluded: Dict[str, str]
    strategy: str
    seed: Optional[int] = None

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"SampleResult(strategy={self.strategy!r}, "
            f"sampled={len(self.sampled)}, excluded={len(self.excluded)})"
        )

    def is_empty(self) -> bool:
        return len(self.sampled) == 0


def sample_by_count(
    env: Dict[str, str],
    count: int,
    seed: Optional[int] = None,
) -> SampleResult:
    """Return a random sample of *count* keys from *env*."""
    if count < 0:
        raise ValueError("count must be >= 0")
    rng = random.Random(seed)
    keys = list(env.keys())
    count = min(count, len(keys))
    chosen = set(rng.sample(keys, count))
    sampled = {k: env[k] for k in keys if k in chosen}
    excluded = {k: env[k] for k in keys if k not in chosen}
    return SampleResult(
        sampled=sampled,
        excluded=excluded,
        strategy="count",
        seed=seed,
    )


def sample_by_fraction(
    env: Dict[str, str],
    fraction: float,
    seed: Optional[int] = None,
) -> SampleResult:
    """Return a random sample covering *fraction* (0.0–1.0) of *env* keys."""
    if not (0.0 <= fraction <= 1.0):
        raise ValueError("fraction must be between 0.0 and 1.0")
    count = round(len(env) * fraction)
    result = sample_by_count(env, count, seed=seed)
    result.strategy = "fraction"
    return result


def sample_by_keys(
    env: Dict[str, str],
    keys: List[str],
) -> SampleResult:
    """Return a deterministic sample containing only the specified *keys*."""
    sampled = {k: env[k] for k in keys if k in env}
    excluded = {k: v for k, v in env.items() if k not in sampled}
    return SampleResult(
        sampled=sampled,
        excluded=excluded,
        strategy="keys",
        seed=None,
    )
