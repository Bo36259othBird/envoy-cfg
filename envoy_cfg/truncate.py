"""Truncate environment variable values to a maximum length."""

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class TruncateResult:
    env: Dict[str, str]
    truncated_keys: List[str]
    max_length: int
    suffix: str = "..."

    def __repr__(self) -> str:
        return (
            f"TruncateResult(truncated={len(self.truncated_keys)}, "
            f"max_length={self.max_length}, total={len(self.env)})"
        )

    @property
    def is_clean(self) -> bool:
        """True if no values were truncated."""
        return len(self.truncated_keys) == 0


def truncate_env(
    env: Dict[str, str],
    max_length: int,
    suffix: str = "...",
    keys: List[str] = None,
) -> TruncateResult:
    """Truncate values in *env* that exceed *max_length* characters.

    Args:
        env: Source environment mapping.
        max_length: Maximum allowed value length (must be >= 1).
        suffix: String appended to truncated values (counts toward length).
        keys: Optional allowlist of keys to truncate; all keys if None.

    Returns:
        TruncateResult with the processed env and metadata.
    """
    if max_length < 1:
        raise ValueError("max_length must be at least 1")
    if len(suffix) >= max_length:
        raise ValueError("suffix length must be less than max_length")

    result: Dict[str, str] = {}
    truncated: List[str] = []
    target_keys = set(keys) if keys is not None else None

    for k, v in env.items():
        if target_keys is not None and k not in target_keys:
            result[k] = v
            continue
        if len(v) > max_length:
            cut = max_length - len(suffix)
            result[k] = v[:cut] + suffix
            truncated.append(k)
        else:
            result[k] = v

    return TruncateResult(
        env=result,
        truncated_keys=sorted(truncated),
        max_length=max_length,
        suffix=suffix,
    )
