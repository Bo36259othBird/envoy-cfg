"""Tests for envoy_cfg.snapshot module."""

import json
import pytest
from pathlib import Path

from envoy_cfg.snapshot import EnvSnapshot, SnapshotStore, capture_snapshot


SAMPLE_VARS = {"APP_ENV": "production", "DB_HOST": "db.example.com", "PORT": "8080"}


# --- EnvSnapshot tests ---

def test_snapshot_creation():
    snap = EnvSnapshot(
        target_name="web-server",
        environment="production",
        captured_at="2024-01-15T10:00:00Z",
        variables=SAMPLE_VARS,
    )
    assert snap.target_name == "web-server"
    assert snap.environment == "production"
    assert snap.variables["PORT"] == "8080"
    assert snap.description is None


def test_snapshot_empty_target_name_raises():
    with pytest.raises(ValueError, match="target_name"):
        EnvSnapshot(target_name="", environment="staging", captured_at="2024-01-01T00:00:00Z")


def test_snapshot_empty_environment_raises():
    with pytest.raises(ValueError, match="environment"):
        EnvSnapshot(target_name="api", environment="", captured_at="2024-01-01T00:00:00Z")


def test_snapshot_to_dict_roundtrip():
    snap = EnvSnapshot(
        target_name="api",
        environment="staging",
        captured_at="2024-06-01T12:00:00Z",
        variables=SAMPLE_VARS,
        description="pre-deploy backup",
    )
    data = snap.to_dict()
    restored = EnvSnapshot.from_dict(data)
    assert restored.target_name == snap.target_name
    assert restored.environment == snap.environment
    assert restored.variables == snap.variables
    assert restored.description == snap.description


def test_capture_snapshot_sets_timestamp():
    snap = capture_snapshot("worker", "production", SAMPLE_VARS, description="test")
    assert snap.target_name == "worker"
    assert snap.environment == "production"
    assert snap.description == "test"
    assert "T" in snap.captured_at and snap.captured_at.endswith("Z")


# --- SnapshotStore tests ---

@pytest.fixture
def store(tmp_path):
    return SnapshotStore(store_dir=str(tmp_path / "snapshots"))


def test_store_save_and_load(store):
    snap = capture_snapshot("db", "production", SAMPLE_VARS)
    path = store.save(snap, label="v1")
    assert path.exists()
    loaded = store.load("db", "v1")
    assert loaded.target_name == "db"
    assert loaded.variables == SAMPLE_VARS


def test_store_load_missing_raises(store):
    with pytest.raises(FileNotFoundError):
        store.load("nonexistent", "v99")


def test_store_list_snapshots(store):
    snap1 = capture_snapshot("api", "staging", {"KEY": "val1"})
    snap2 = capture_snapshot("api", "staging", {"KEY": "val2"})
    store.save(snap1, label="snap-a")
    store.save(snap2, label="snap-b")
    listing = store.list_snapshots(target_name="api")
    assert any("snap-a" in s for s in listing)
    assert any("snap-b" in s for s in listing)


def test_store_list_all_snapshots(store):
    store.save(capture_snapshot("api", "prod", {}), label="x1")
    store.save(capture_snapshot("worker", "prod", {}), label="x2")
    all_snaps = store.list_snapshots()
    assert len(all_snaps) == 2


def test_store_delete_snapshot(store):
    snap = capture_snapshot("cache", "staging", {"REDIS_URL": "redis://localhost"})
    store.save(snap, label="del-me")
    assert store.delete("cache", "del-me") is True
    assert store.delete("cache", "del-me") is False


def test_store_save_uses_timestamp_as_default_label(store):
    snap = capture_snapshot("proxy", "prod", {})
    path = store.save(snap)
    assert path.exists()
    assert snap.captured_at.replace(":", "-") in path.stem
