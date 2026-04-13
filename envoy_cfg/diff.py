"""Diff utilities for comparing environment variable configs."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from enum import Enum


class ChangeType(str, Enum):
    ADDED = "added"
    REMOVED = "removed"
    MODIFIED = "modified"
    UNCHANGED = "unchanged"


@dataclass
class EnvChange:
    key: str
    change_type: ChangeType
    old_value: Optional[str] = None
    new_value: Optional[str] = None

    def __repr__(self) -> str:
        if self.change_type == ChangeType.ADDED:
            return f"+ {self.key}={self.new_value}"
        elif self.change_type == ChangeType.REMOVED:
            return f"- {self.key}={self.old_value}"
        elif self.change_type == ChangeType.MODIFIED:
            return f"~ {self.key}: {self.old_value!r} -> {self.new_value!r}"
        return f"  {self.key}={self.new_value}"


@dataclass
class DiffResult:
    changes: List[EnvChange] = field(default_factory=list)

    @property
    def added(self) -> List[EnvChange]:
        return [c for c in self.changes if c.change_type == ChangeType.ADDED]

    @property
    def removed(self) -> List[EnvChange]:
        return [c for c in self.changes if c.change_type == ChangeType.REMOVED]

    @property
    def modified(self) -> List[EnvChange]:
        return [c for c in self.changes if c.change_type == ChangeType.MODIFIED]

    @property
    def has_changes(self) -> bool:
        return any(
            c.change_type != ChangeType.UNCHANGED for c in self.changes
        )

    def summary(self) -> str:
        return (
            f"{len(self.added)} added, "
            f"{len(self.removed)} removed, "
            f"{len(self.modified)} modified"
        )


def diff_envs(
    current: Dict[str, str],
    incoming: Dict[str, str],
    include_unchanged: bool = False,
) -> DiffResult:
    """Compute the diff between two environment variable dictionaries."""
    changes: List[EnvChange] = []
    all_keys = set(current) | set(incoming)

    for key in sorted(all_keys):
        if key not in current:
            changes.append(EnvChange(key, ChangeType.ADDED, new_value=incoming[key]))
        elif key not in incoming:
            changes.append(EnvChange(key, ChangeType.REMOVED, old_value=current[key]))
        elif current[key] != incoming[key]:
            changes.append(
                EnvChange(key, ChangeType.MODIFIED, old_value=current[key], new_value=incoming[key])
            )
        elif include_unchanged:
            changes.append(EnvChange(key, ChangeType.UNCHANGED, new_value=current[key]))

    return DiffResult(changes=changes)
