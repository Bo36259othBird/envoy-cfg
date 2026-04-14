"""Pin module: lock specific env keys to fixed values across targets."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional
import json
import os


@dataclass
class PinEntry:
    key: str
    value: str
    target: str
    reason: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "key": self.key,
            "value": self.value,
            "target": self.target,
            "reason": self.reason,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "PinEntry":
        return cls(
            key=data["key"],
            value=data["value"],
            target=data["target"],
            reason=data.get("reason"),
        )

    def __repr__(self) -> str:
        reason_part = f" ({self.reason})" if self.reason else ""
        return f"<PinEntry {self.target}:{self.key}={self.value!r}{reason_part}>"


@dataclass
class PinStore:
    _path: str
    _pins: Dict[str, PinEntry] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if os.path.exists(self._path):
            with open(self._path, "r") as fh:
                raw = json.load(fh)
            for record in raw:
                entry = PinEntry.from_dict(record)
                self._pins[self._pin_key(entry.target, entry.key)] = entry

    @staticmethod
    def _pin_key(target: str, key: str) -> str:
        return f"{target}::{key}"

    def _save(self) -> None:
        with open(self._path, "w") as fh:
            json.dump([e.to_dict() for e in self._pins.values()], fh, indent=2)

    def pin(self, target: str, key: str, value: str, reason: Optional[str] = None) -> PinEntry:
        entry = PinEntry(key=key, value=value, target=target, reason=reason)
        self._pins[self._pin_key(target, key)] = entry
        self._save()
        return entry

    def unpin(self, target: str, key: str) -> bool:
        pk = self._pin_key(target, key)
        if pk in self._pins:
            del self._pins[pk]
            self._save()
            return True
        return False

    def get(self, target: str, key: str) -> Optional[PinEntry]:
        return self._pins.get(self._pin_key(target, key))

    def list_for_target(self, target: str) -> List[PinEntry]:
        return [e for e in self._pins.values() if e.target == target]

    def apply(self, target: str, env: Dict[str, str]) -> Dict[str, str]:
        """Return a copy of env with pinned values enforced."""
        result = dict(env)
        for entry in self.list_for_target(target):
            result[entry.key] = entry.value
        return result

    def all(self) -> List[PinEntry]:
        return list(self._pins.values())
