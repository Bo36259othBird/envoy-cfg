from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class CopyResult:
    copied: Dict[str, str]
    skipped: List[str]
    overwritten: List[str]
    strategy: str

    def __repr__(self) -> str:
        return (
            f"CopyResult(copied={len(self.copied)}, skipped={len(self.skipped)}, "
            f"overwritten={len(self.overwritten)}, strategy={self.strategy!r})"
        )

    def is_clean(self) -> bool:
        return len(self.skipped) == 0


def copy_keys(
    source: Dict[str, str],
    dest: Dict[str, str],
    keys: List[str],
    overwrite: bool = False,
    prefix: Optional[str] = None,
) -> CopyResult:
    """Copy specific keys from source into dest.

    Args:
        source: Source environment dict.
        dest: Destination environment dict (not mutated).
        keys: Keys to copy from source.
        overwrite: If True, overwrite existing keys in dest.
        prefix: Optional prefix to apply to keys in dest.
    """
    result_env = dict(dest)
    copied: Dict[str, str] = {}
    skipped: List[str] = []
    overwritten: List[str] = []

    for key in keys:
        if key not in source:
            skipped.append(key)
            continue
        dest_key = f"{prefix}{key}" if prefix else key
        if dest_key in result_env and not overwrite:
            skipped.append(key)
            continue
        if dest_key in result_env:
            overwritten.append(dest_key)
        result_env[dest_key] = source[key]
        copied[dest_key] = source[key]

    strategy = "overwrite" if overwrite else "keep-dest"
    return CopyResult(copied=copied, skipped=skipped, overwritten=overwritten, strategy=strategy)
