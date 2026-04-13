"""Environment config locking — prevent accidental overwrites on protected targets."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import List, Optional


DEFAULT_LOCK_FILE = ".envoy_locks.json"


@dataclass
class LockEntry:
    target_name: str
    environment: str
    reason: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "target_name": self.target_name,
            "environment": self.environment,
            "reason": self.reason,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "LockEntry":
        return cls(
            target_name=data["target_name"],
            environment=data["environment"],
            reason=data.get("reason"),
        )

    def __repr__(self) -> str:
        reason_part = f" ({self.reason})" if self.reason else ""
        return f"<LockEntry {self.target_name}/{self.environment}{reason_part}>"


class LockStore:
    def __init__(self, lock_file: str = DEFAULT_LOCK_FILE):
        self.lock_file = lock_file
        self._locks: List[LockEntry] = []
        self._load()

    def _load(self) -> None:
        if not os.path.exists(self.lock_file):
            self._locks = []
            return
        with open(self.lock_file, "r") as f:
            raw = json.load(f)
        self._locks = [LockEntry.from_dict(d) for d in raw]

    def _save(self) -> None:
        with open(self.lock_file, "w") as f:
            json.dump([e.to_dict() for e in self._locks], f, indent=2)

    def is_locked(self, target_name: str, environment: str) -> bool:
        return any(
            e.target_name == target_name and e.environment == environment
            for e in self._locks
        )

    def lock(self, target_name: str, environment: str, reason: Optional[str] = None) -> LockEntry:
        if self.is_locked(target_name, environment):
            raise ValueError(f"Target '{target_name}/{environment}' is already locked.")
        entry = LockEntry(target_name=target_name, environment=environment, reason=reason)
        self._locks.append(entry)
        self._save()
        return entry

    def unlock(self, target_name: str, environment: str) -> bool:
        before = len(self._locks)
        self._locks = [
            e for e in self._locks
            if not (e.target_name == target_name and e.environment == environment)
        ]
        if len(self._locks) < before:
            self._save()
            return True
        return False

    def list_locks(self) -> List[LockEntry]:
        return list(self._locks)
