"""Bulk key renaming for environment variable maps."""
from dataclasses import dataclass, field
from typing import Dict, List, Tuple


@dataclass
class RenameResult:
    env: Dict[str, str]
    renamed: List[Tuple[str, str]] = field(default_factory=list)  # (old, new)
    skipped: List[str] = field(default_factory=list)  # old keys not found

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"RenameResult(renamed={len(self.renamed)}, "
            f"skipped={len(self.skipped)}, keys={len(self.env)})"
        )

    @property
    def is_clean(self) -> bool:
        """True when every requested rename was applied (nothing skipped)."""
        return len(self.skipped) == 0


def rename_keys(
    env: Dict[str, str],
    mapping: Dict[str, str],
    overwrite: bool = True,
) -> RenameResult:
    """Rename keys in *env* according to *mapping* {old_key: new_key}.

    Parameters
    ----------
    env:
        Source environment dict (not mutated).
    mapping:
        Dict of ``{old_name: new_name}`` pairs.
    overwrite:
        When *True* (default) the new key overwrites any existing value.
        When *False* the rename is skipped if the new key already exists.
    """
    result: Dict[str, str] = dict(env)
    renamed: List[Tuple[str, str]] = []
    skipped: List[str] = []

    for old_key, new_key in mapping.items():
        if old_key not in result:
            skipped.append(old_key)
            continue
        if new_key in result and not overwrite:
            skipped.append(old_key)
            continue
        value = result.pop(old_key)
        result[new_key] = value
        renamed.append((old_key, new_key))

    return RenameResult(env=result, renamed=renamed, skipped=skipped)
