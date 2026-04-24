"""Generate and apply patch files derived from env diffs."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envoy_cfg.diff import DiffResult, ChangeType, compute_diff


@dataclass
class DiffPatchEntry:
    key: str
    change_type: str  # 'add', 'remove', 'modify'
    old_value: Optional[str]
    new_value: Optional[str]

    def to_dict(self) -> dict:
        return {
            "key": self.key,
            "change_type": self.change_type,
            "old_value": self.old_value,
            "new_value": self.new_value,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "DiffPatchEntry":
        return cls(
            key=data["key"],
            change_type=data["change_type"],
            old_value=data.get("old_value"),
            new_value=data.get("new_value"),
        )

    def __repr__(self) -> str:
        return f"DiffPatchEntry({self.change_type} {self.key!r})"


@dataclass
class DiffPatch:
    entries: List[DiffPatchEntry] = field(default_factory=list)

    @property
    def is_empty(self) -> bool:
        return len(self.entries) == 0

    def to_dict(self) -> dict:
        return {"entries": [e.to_dict() for e in self.entries]}

    @classmethod
    def from_dict(cls, data: dict) -> "DiffPatch":
        return cls(
            entries=[DiffPatchEntry.from_dict(e) for e in data.get("entries", [])]
        )


def build_patch(base: Dict[str, str], updated: Dict[str, str]) -> DiffPatch:
    """Build a DiffPatch from two env dicts."""
    diff: DiffResult = compute_diff(base, updated)
    entries: List[DiffPatchEntry] = []
    for change in diff.changes:
        if change.change_type == ChangeType.ADDED:
            entries.append(DiffPatchEntry(change.key, "add", None, change.new_value))
        elif change.change_type == ChangeType.REMOVED:
            entries.append(DiffPatchEntry(change.key, "remove", change.old_value, None))
        elif change.change_type == ChangeType.MODIFIED:
            entries.append(
                DiffPatchEntry(change.key, "modify", change.old_value, change.new_value)
            )
    return DiffPatch(entries=entries)


def apply_patch(
    env: Dict[str, str],
    patch: DiffPatch,
    *,
    strict: bool = False,
) -> Dict[str, str]:
    """Apply a DiffPatch to an env dict, returning the patched result.

    If *strict* is True, raises ValueError when a patch entry cannot be applied
    cleanly (e.g. key to remove is absent, or key to add already exists).
    """
    result = dict(env)
    for entry in patch.entries:
        if entry.change_type == "add":
            if strict and entry.key in result:
                raise ValueError(f"Patch conflict: key {entry.key!r} already exists.")
            result[entry.key] = entry.new_value or ""
        elif entry.change_type == "remove":
            if strict and entry.key not in result:
                raise ValueError(f"Patch conflict: key {entry.key!r} not found.")
            result.pop(entry.key, None)
        elif entry.change_type == "modify":
            if strict and entry.key not in result:
                raise ValueError(f"Patch conflict: key {entry.key!r} not found for modify.")
            result[entry.key] = entry.new_value or ""
    return result
