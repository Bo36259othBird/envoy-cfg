"""mask_diff: Compute a diff between two envs with secrets masked in output."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from envoy_cfg.diff import DiffResult, compute_diff, ChangeType
from envoy_cfg.masking import is_secret_key, mask_value


@dataclass
class MaskDiffEntry:
    key: str
    change_type: str  # 'added' | 'removed' | 'modified' | 'unchanged'
    old_value: str | None
    new_value: str | None
    masked: bool

    def to_dict(self) -> dict:
        return {
            "key": self.key,
            "change_type": self.change_type,
            "old_value": self.old_value,
            "new_value": self.new_value,
            "masked": self.masked,
        }

    def __repr__(self) -> str:
        tag = "[MASKED]" if self.masked else ""
        return f"MaskDiffEntry({self.change_type} {self.key!r}{tag})"


@dataclass
class MaskDiffResult:
    entries: List[MaskDiffEntry] = field(default_factory=list)
    total: int = 0
    masked_count: int = 0

    @property
    def is_clean(self) -> bool:
        return all(e.change_type == "unchanged" for e in self.entries)

    @property
    def changed_entries(self) -> List[MaskDiffEntry]:
        return [e for e in self.entries if e.change_type != "unchanged"]

    def __repr__(self) -> str:
        return (
            f"MaskDiffResult(total={self.total}, "
            f"changed={len(self.changed_entries)}, masked={self.masked_count})"
        )


def mask_diff(
    base: Dict[str, str],
    updated: Dict[str, str],
    mask_secrets: bool = True,
) -> MaskDiffResult:
    """Compute a diff and mask secret values in the result."""
    diff: DiffResult = compute_diff(base, updated)
    entries: List[MaskDiffEntry] = []
    masked_count = 0

    all_keys = sorted(
        set(base.keys()) | set(updated.keys())
    )

    change_map = {c.key: c for c in diff.changes}

    for key in all_keys:
        secret = mask_secrets and is_secret_key(key)
        change = change_map.get(key)

        if change is None:
            old_v = base.get(key)
            new_v = updated.get(key)
            old_display = mask_value(old_v) if secret and old_v is not None else old_v
            new_display = mask_value(new_v) if secret and new_v is not None else new_v
            entries.append(MaskDiffEntry(key, "unchanged", old_display, new_display, secret))
        else:
            ct = change.change_type.value
            old_v = change.old_value
            new_v = change.new_value
            old_display = mask_value(old_v) if secret and old_v is not None else old_v
            new_display = mask_value(new_v) if secret and new_v is not None else new_v
            entries.append(MaskDiffEntry(key, ct, old_display, new_display, secret))
            if secret:
                masked_count += 1

    return MaskDiffResult(
        entries=entries,
        total=len(all_keys),
        masked_count=masked_count,
    )
