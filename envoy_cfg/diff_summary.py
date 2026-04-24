from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from envoy_cfg.diff import DiffResult, ChangeType


@dataclass
class DiffSummaryEntry:
    change_type: str
    count: int
    keys: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return {
            "change_type": self.change_type,
            "count": self.count,
            "keys": sorted(self.keys),
        }

    def __repr__(self) -> str:  # pragma: no cover
        return f"DiffSummaryEntry(type={self.change_type!r}, count={self.count})"


@dataclass
class DiffSummary:
    added: DiffSummaryEntry
    removed: DiffSummaryEntry
    modified: DiffSummaryEntry
    unchanged_count: int

    @property
    def total_changes(self) -> int:
        return self.added.count + self.removed.count + self.modified.count

    @property
    def is_clean(self) -> bool:
        return self.total_changes == 0

    def to_dict(self) -> Dict:
        return {
            "added": self.added.to_dict(),
            "removed": self.removed.to_dict(),
            "modified": self.modified.to_dict(),
            "unchanged_count": self.unchanged_count,
            "total_changes": self.total_changes,
            "is_clean": self.is_clean,
        }

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"DiffSummary(added={self.added.count}, removed={self.removed.count}, "
            f"modified={self.modified.count}, unchanged={self.unchanged_count})"
        )


def summarize_diff(result: DiffResult) -> DiffSummary:
    """Produce a structured summary from a DiffResult."""
    added_keys = [c.key for c in result.changes if c.change_type == ChangeType.ADDED]
    removed_keys = [c.key for c in result.changes if c.change_type == ChangeType.REMOVED]
    modified_keys = [c.key for c in result.changes if c.change_type == ChangeType.MODIFIED]

    unchanged = len(result.unchanged) if hasattr(result, "unchanged") else 0

    return DiffSummary(
        added=DiffSummaryEntry(change_type="added", count=len(added_keys), keys=added_keys),
        removed=DiffSummaryEntry(change_type="removed", count=len(removed_keys), keys=removed_keys),
        modified=DiffSummaryEntry(change_type="modified", count=len(modified_keys), keys=modified_keys),
        unchanged_count=unchanged,
    )
