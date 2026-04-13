"""Track and retrieve the history of environment variable changes per target."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Optional


@dataclass
class HistoryEntry:
    target_name: str
    environment: str
    key: str
    old_value: Optional[str]
    new_value: Optional[str]
    changed_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    author: str = "unknown"

    def to_dict(self) -> dict:
        return {
            "target_name": self.target_name,
            "environment": self.environment,
            "key": self.key,
            "old_value": self.old_value,
            "new_value": self.new_value,
            "changed_at": self.changed_at,
            "author": self.author,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "HistoryEntry":
        return cls(
            target_name=data["target_name"],
            environment=data["environment"],
            key=data["key"],
            old_value=data.get("old_value"),
            new_value=data.get("new_value"),
            changed_at=data.get("changed_at", ""),
            author=data.get("author", "unknown"),
        )

    def __repr__(self) -> str:
        return (
            f"<HistoryEntry target={self.target_name!r} key={self.key!r} "
            f"at={self.changed_at}>"
        )


class HistoryStore:
    def __init__(self, path: str) -> None:
        self.path = path
        self._entries: List[HistoryEntry] = []
        self._load()

    def _load(self) -> None:
        if os.path.exists(self.path):
            with open(self.path, "r") as fh:
                raw = json.load(fh)
            self._entries = [HistoryEntry.from_dict(d) for d in raw]
        else:
            self._entries = []

    def _save(self) -> None:
        with open(self.path, "w") as fh:
            json.dump([e.to_dict() for e in self._entries], fh, indent=2)

    def record(self, entry: HistoryEntry) -> None:
        self._entries.append(entry)
        self._save()

    def record_changes(
        self,
        target_name: str,
        environment: str,
        before: Dict[str, str],
        after: Dict[str, str],
        author: str = "unknown",
    ) -> List[HistoryEntry]:
        recorded: List[HistoryEntry] = []
        all_keys = set(before) | set(after)
        for key in sorted(all_keys):
            old_val = before.get(key)
            new_val = after.get(key)
            if old_val != new_val:
                entry = HistoryEntry(
                    target_name=target_name,
                    environment=environment,
                    key=key,
                    old_value=old_val,
                    new_value=new_val,
                    author=author,
                )
                self._entries.append(entry)
                recorded.append(entry)
        if recorded:
            self._save()
        return recorded

    def for_target(self, target_name: str) -> List[HistoryEntry]:
        return [e for e in self._entries if e.target_name == target_name]

    def for_key(self, target_name: str, key: str) -> List[HistoryEntry]:
        return [
            e for e in self._entries
            if e.target_name == target_name and e.key == key
        ]

    def all_entries(self) -> List[HistoryEntry]:
        return list(self._entries)

    def clear(self) -> None:
        self._entries = []
        self._save()
