"""Tests for envoy_cfg.archive."""

from __future__ import annotations

import io
import pytest
from datetime import datetime, timezone

from envoy_cfg.archive import ArchiveManifest, create_archive, load_archive
from envoy_cfg.snapshot import EnvSnapshot


def _make_snapshot(target: str, env: str, data: dict) -> EnvSnapshot:
    return EnvSnapshot(
        target_name=target,
        environment=env,
        env=data,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )


@pytest.fixture
def snapshots():
    return [
        _make_snapshot("api", "staging", {"HOST": "localhost", "PORT": "8080"}),
        _make_snapshot("api", "production", {"HOST": "prod.example.com", "PORT": "443"}),
        _make_snapshot("worker", "staging", {"QUEUE": "tasks"}),
    ]


def test_create_archive_returns_manifest(snapshots):
    buf = io.BytesIO()
    manifest = create_archive(snapshots, buf)
    assert manifest.snapshot_count == 3
    assert set(manifest.targets) == {"api", "worker"}
    assert manifest.created_at


def test_create_archive_produces_non_empty_bytes(snapshots):
    buf = io.BytesIO()
    create_archive(snapshots, buf)
    assert buf.tell() > 0


def test_create_archive_empty_raises():
    buf = io.BytesIO()
    with pytest.raises(ValueError, match="empty"):
        create_archive([], buf)


def test_roundtrip_preserves_snapshot_count(snapshots):
    buf = io.BytesIO()
    create_archive(snapshots, buf)
    buf.seek(0)
    manifest, loaded = load_archive(buf)
    assert len(loaded) == len(snapshots)


def test_roundtrip_preserves_env_data(snapshots):
    buf = io.BytesIO()
    create_archive(snapshots, buf)
    buf.seek(0)
    _, loaded = load_archive(buf)
    envs = {(s.target_name, s.environment): s.env for s in loaded}
    assert envs[("api", "staging")]["PORT"] == "8080"
    assert envs[("api", "production")]["HOST"] == "prod.example.com"


def test_roundtrip_manifest_targets(snapshots):
    buf = io.BytesIO()
    create_archive(snapshots, buf)
    buf.seek(0)
    manifest, _ = load_archive(buf)
    assert "api" in manifest.targets
    assert "worker" in manifest.targets


def test_manifest_to_dict_roundtrip():
    m = ArchiveManifest(created_at="2024-01-01T00:00:00+00:00", snapshot_count=2, targets=["a", "b"])
    restored = ArchiveManifest.from_dict(m.to_dict())
    assert restored.snapshot_count == 2
    assert restored.targets == ["a", "b"]
    assert restored.created_at == m.created_at


def test_load_archive_missing_manifest_raises():
    import zipfile
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, mode="w") as zf:
        zf.writestr("snapshots/0000_api_staging.json", '{"target_name":"api"}')
    buf.seek(0)
    with pytest.raises(ValueError, match="manifest"):
        load_archive(buf)
