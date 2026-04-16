from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List
from envoy_cfg.masking import is_secret_key


@dataclass
class SummaryResult:
    total: int
    secret_count: int
    plain_count: int
    empty_count: int
    prefixes: Dict[str, int]
    longest_key: str
    longest_value_key: str

    def __repr__(self) -> str:
        return (
            f"SummaryResult(total={self.total}, secrets={self.secret_count}, "
            f"plain={self.plain_count}, empty={self.empty_count})"
        )

    def is_clean(self) -> bool:
        """Returns True if no empty values and no secrets detected."""
        return self.empty_count == 0 and self.secret_count == 0


def summarize_env(
    env: Dict[str, str],
    prefix_separator: str = "_",
) -> SummaryResult:
    """Produce a statistical summary of an environment variable mapping."""
    if not env:
        return SummaryResult(
            total=0,
            secret_count=0,
            plain_count=0,
            empty_count=0,
            prefixes={},
            longest_key="",
            longest_value_key="",
        )

    secret_count = 0
    plain_count = 0
    empty_count = 0
    prefixes: Dict[str, int] = {}
    longest_key = ""
    longest_value_key = ""

    for key, value in env.items():
        if is_secret_key(key):
            secret_count += 1
        else:
            plain_count += 1

        if value == "":
            empty_count += 1

        if len(key) > len(longest_key):
            longest_key = key

        if len(value) > len(env.get(longest_value_key, "")):
            longest_value_key = key

        prefix = key.split(prefix_separator)[0] if prefix_separator in key else key
        prefixes[prefix] = prefixes.get(prefix, 0) + 1

    return SummaryResult(
        total=len(env),
        secret_count=secret_count,
        plain_count=plain_count,
        empty_count=empty_count,
        prefixes=prefixes,
        longest_key=longest_key,
        longest_value_key=longest_value_key,
    )
