"""Cross-reference: find keys used/missing across multiple envs."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Set


@dataclass
class CrossRefResult:
    envs: Dict[str, Set[str]]
    common: Set[str] = field(default_factory=set)
    only_in: Dict[str, Set[str]] = field(default_factory=dict)
    missing_in: Dict[str, Set[str]] = field(default_factory=dict)

    def __repr__(self) -> str:
        return (
            f"CrossRefResult(envs={list(self.envs)}, "
            f"common={len(self.common)}, "
            f"unique_sets={len(self.only_in)})"
        )

    def is_consistent(self) -> bool:
        return all(len(v) == 0 for v in self.missing_in.values())


def crossref_envs(envs: Dict[str, Dict[str, str]]) -> CrossRefResult:
    """Compare keys across multiple named envs."""
    if not envs:
        raise ValueError("At least one environment must be provided.")

    key_sets: Dict[str, Set[str]] = {name: set(e.keys()) for name, e in envs.items()}
    all_keys: Set[str] = set().union(*key_sets.values())
    common: Set[str] = set(all_keys)
    for ks in key_sets.values():
        common &= ks

    only_in: Dict[str, Set[str]] = {
        name: ks - common for name, ks in key_sets.items()
    }
    missing_in: Dict[str, Set[str]] = {
        name: all_keys - ks for name, ks in key_sets.items()
    }

    return CrossRefResult(
        envs=key_sets,
        common=common,
        only_in=only_in,
        missing_in=missing_in,
    )
