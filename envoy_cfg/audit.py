"""Audit log for tracking config sync operations and changes."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Optional
import json
import os


@dataclass
class AuditEntry:
    action: str
    target_name: str
    environment: str
    keys_affected: List[str]
    performed_by: str
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    dry_run: bool = False
    note: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "action": self.action,
            "target_name": self.target_name,
            "environment": self.environment,
            "keys_affected": self.keys_affected,
            "performed_by": self.performed_by,
            "timestamp": self.timestamp,
            "dry_run": self.dry_run,
            "note": self.note,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "AuditEntry":
        return cls(
            action=data["action"],
            target_name=data["target_name"],
            environment=data["environment"],
            keys_affected=data["keys_affected"],
            performed_by=data["performed_by"],
            timestamp=data["timestamp"],
            dry_run=data.get("dry_run", False),
            note=data.get("note"),
        )

    def __repr__(self) -> str:
        dry = " [DRY RUN]" if self.dry_run else ""
        return (
            f"[{self.timestamp}]{dry} {self.action} on {self.target_name} "
            f"({self.environment}) by {self.performed_by} "
            f"— {len(self.keys_affected)} key(s) affected"
        )


class AuditLog:
    def __init__(self, log_path: str = "audit_log.json"):
        self.log_path = log_path
        self._entries: List[AuditEntry] = []
        self._load()

    def _load(self) -> None:
        if os.path.exists(self.log_path):
            with open(self.log_path, "r") as f:
                raw = json.load(f)
            self._entries = [AuditEntry.from_dict(e) for e in raw]

    def _save(self) -> None:
        with open(self.log_path, "w") as f:
            json.dump([e.to_dict() for e in self._entries], f, indent=2)

    def record(self, entry: AuditEntry) -> None:
        self._entries.append(entry)
        self._save()

    def all(self) -> List[AuditEntry]:
        return list(self._entries)

    def filter_by_target(self, target_name: str) -> List[AuditEntry]:
        return [e for e in self._entries if e.target_name == target_name]

    def filter_by_environment(self, environment: str) -> List[AuditEntry]:
        return [e for e in self._entries if e.environment == environment]

    def clear(self) -> None:
        self._entries = []
        self._save()
