"""Snapshot support for capturing and restoring environment variable states."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class EnvSnapshot:
    """Represents a point-in-time capture of environment variables for a target."""

    target_name: str
    environment: str
    captured_at: str
    variables: Dict[str, str] = field(default_factory=dict)
    description: Optional[str] = None

    def __post_init__(self) -> None:
        if not self.target_name:
            raise ValueError("target_name must not be empty")
        if not self.environment:
            raise ValueError("environment must not be empty")

    def to_dict(self) -> dict:
        return {
            "target_name": self.target_name,
            "environment": self.environment,
            "captured_at": self.captured_at,
            "variables": self.variables,
            "description": self.description,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "EnvSnapshot":
        return cls(
            target_name=data["target_name"],
            environment=data["environment"],
            captured_at=data["captured_at"],
            variables=data.get("variables", {}),
            description=data.get("description"),
        )


class SnapshotStore:
    """Manages persistence of environment snapshots to disk."""

    def __init__(self, store_dir: str = ".envoy_snapshots") -> None:
        self.store_dir = Path(store_dir)
        self.store_dir.mkdir(parents=True, exist_ok=True)

    def _snapshot_path(self, target_name: str, label: str) -> Path:
        safe_name = target_name.replace("/", "_").replace(" ", "_")
        return self.store_dir / f"{safe_name}__{label}.json"

    def save(self, snapshot: EnvSnapshot, label: Optional[str] = None) -> Path:
        if label is None:
            label = snapshot.captured_at.replace(":", "-").replace(" ", "T")
        path = self._snapshot_path(snapshot.target_name, label)
        path.write_text(json.dumps(snapshot.to_dict(), indent=2))
        return path

    def load(self, target_name: str, label: str) -> EnvSnapshot:
        path = self._snapshot_path(target_name, label)
        if not path.exists():
            raise FileNotFoundError(f"Snapshot not found: {path}")
        data = json.loads(path.read_text())
        return EnvSnapshot.from_dict(data)

    def list_snapshots(self, target_name: Optional[str] = None) -> List[str]:
        snapshots = []
        for f in sorted(self.store_dir.glob("*.json")):
            if target_name is None or f.name.startswith(target_name.replace("/", "_")):
                snapshots.append(f.stem)
        return snapshots

    def delete(self, target_name: str, label: str) -> bool:
        path = self._snapshot_path(target_name, label)
        if path.exists():
            path.unlink()
            return True
        return False


def capture_snapshot(
    target_name: str,
    environment: str,
    variables: Dict[str, str],
    description: Optional[str] = None,
) -> EnvSnapshot:
    """Create a new snapshot with the current UTC timestamp."""
    captured_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    return EnvSnapshot(
        target_name=target_name,
        environment=environment,
        captured_at=captured_at,
        variables=variables,
        description=description,
    )
