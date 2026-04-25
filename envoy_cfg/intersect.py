"""intersect.py – find keys common to multiple env dicts."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Set


@dataclass
class IntersectResult:
    """Result of intersecting two or more env dicts."""

    common: Dict[str, List[str]]  # key -> list of values (one per env)
    only_in: Dict[str, Set[str]]  # env_label -> keys exclusive to that env
    strategy: str = "intersect"

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"IntersectResult(common={len(self.common)} keys, "
            f"envs={list(self.only_in.keys())}, strategy={self.strategy!r})"
        )

    @property
    def is_consistent(self) -> bool:
        """True when all envs agree on the value for every common key."""
        return all(len(set(vals)) == 1 for vals in self.common.values())

    @property
    def conflicting_keys(self) -> List[str]:
        """Keys present in all envs but with differing values."""
        return sorted(k for k, vals in self.common.items() if len(set(vals)) > 1)


def intersect_envs(
    envs: Dict[str, Dict[str, str]],
) -> IntersectResult:
    """Return keys that appear in *every* labelled env dict.

    Parameters
    ----------
    envs:
        Mapping of label -> env dict, e.g. {"dev": {...}, "prod": {...}}.
        At least two envs must be provided.

    Returns
    -------
    IntersectResult
    """
    if len(envs) < 2:
        raise ValueError("intersect_envs requires at least two envs")

    labels = list(envs.keys())
    all_key_sets = [set(e.keys()) for e in envs.values()]

    common_keys: Set[str] = all_key_sets[0].intersection(*all_key_sets[1:])

    common: Dict[str, List[str]] = {
        k: [envs[lbl][k] for lbl in labels] for k in sorted(common_keys)
    }

    only_in: Dict[str, Set[str]] = {
        lbl: set(envs[lbl].keys()) - common_keys for lbl in labels
    }

    return IntersectResult(common=common, only_in=only_in)
