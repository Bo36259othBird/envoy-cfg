"""Archive module: compress and export env snapshots to portable archive files."""

from __future__ import annotations

import json
import zipfile
import io
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, List, Optional

from envoy_cfg.snapshot import EnvSnapshot


@dataclass
class ArchiveManifest:
    created_at: str
    snapshot_count: int
    targets: List[str]

    def to_dict(self) -> dict:
        return {
            "created_at": self.created_at,
            "snapshot_count": self.snapshot_count,
            "targets": self.targets,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ArchiveManifest":
        return cls(
            created_at=data["created_at"],
            snapshot_count=data["snapshot_count"],
            targets=data["targets"],
        )


def create_archive(snapshots: List[EnvSnapshot], dest: io.BytesIO) -> ArchiveManifest:
    """Write snapshots into a zip archive and return the manifest."""
    if not snapshots:
        raise ValueError("Cannot create archive from empty snapshot list.")

    targets = sorted({s.target_name for s in snapshots})
    manifest = ArchiveManifest(
        created_at=datetime.now(timezone.utc).isoformat(),
        snapshot_count=len(snapshots),
        targets=targets,
    )

    with zipfile.ZipFile(dest, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("manifest.json", json.dumps(manifest.to_dict(), indent=2))
        for idx, snapshot in enumerate(snapshots):
            filename = f"snapshots/{idx:04d}_{snapshot.target_name}_{snapshot.environment}.json"
            zf.writestr(filename, json.dumps(snapshot.to_dict(), indent=2))

    return manifest


def load_archive(src: io.BytesIO) -> tuple[ArchiveManifest, List[EnvSnapshot]]:
    """Read snapshots from a zip archive."""
    snapshots: List[EnvSnapshot] = []
    manifest: Optional[ArchiveManifest] = None

    with zipfile.ZipFile(src, mode="r") as zf:
        for name in zf.namelist():
            data = json.loads(zf.read(name).decode("utf-8"))
            if name == "manifest.json":
                manifest = ArchiveManifest.from_dict(data)
            elif name.startswith("snapshots/"):
                snapshots.append(EnvSnapshot.from_dict(data))

    if manifest is None:
        raise ValueError("Archive is missing manifest.json")

    return manifest, snapshots
