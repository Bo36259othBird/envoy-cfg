"""Tests for EnvRollback rollback logic."""

import pytest
from unittest.mock import MagicMock

from envoy_cfg.rollback import EnvRollback, RollbackResult
from envoy_cfg.snapshot import EnvSnapshot, SnapshotStore
from envoy_cfg.targets import DeploymentTarget, TargetRegistry


@pytest.fixture
def registry():
    reg = TargetRegistry()
    target = DeploymentTarget(
        name="web",
        environment="staging",
        env={"DB_HOST": "old-host", "API_KEY": "old-key"},
    )
    reg.register(target)
    return reg


@pytest.fixture
def store():
    s = SnapshotStore()
    snap = EnvSnapshot(
        snapshot_id="snap-001",
        target_name="web",
        environment="staging",
        env={"DB_HOST": "new-host", "API_KEY": "new-key", "TIMEOUT": "30"},
        timestamp="2024-01-01T00:00:00",
    )
    s._snapshots["snap-001"] = snap
    return s


def test_rollback_applies_snapshot_env(registry, store):
    rollback = EnvRollback(registry, store)
    result = rollback.rollback("web", "snap-001")

    assert result.applied is True
    assert result.dry_run is False
    assert set(result.keys_restored) == {"DB_HOST", "API_KEY", "TIMEOUT"}
    target = registry.get("web")
    assert target.env["DB_HOST"] == "new-host"
    assert target.env["TIMEOUT"] == "30"


def test_rollback_dry_run_does_not_apply(registry, store):
    rollback = EnvRollback(registry, store)
    rollback.set_dry_run(True)
    result = rollback.rollback("web", "snap-001")

    assert result.dry_run is True
    assert result.applied is False
    target = registry.get("web")
    assert target.env["DB_HOST"] == "old-host"  # unchanged


def test_rollback_missing_target(registry, store):
    rollback = EnvRollback(registry, store)
    result = rollback.rollback("nonexistent", "snap-001")

    assert result.applied is False
    assert "not found" in result.message


def test_rollback_missing_snapshot(registry, store):
    rollback = EnvRollback(registry, store)
    result = rollback.rollback("web", "snap-999")

    assert result.applied is False
    assert "snap-999" in result.message


def test_rollback_records_audit_entries(registry, store):
    audit_log = MagicMock()
    rollback = EnvRollback(registry, store, audit_log=audit_log)
    rollback.rollback("web", "snap-001")

    assert audit_log.record.call_count == 3  # one per key
    call_args = [call.args[0] for call in audit_log.record.call_args_list]
    actions = {entry.action for entry in call_args}
    assert actions == {"rollback"}


def test_rollback_dry_run_skips_audit(registry, store):
    audit_log = MagicMock()
    rollback = EnvRollback(registry, store, audit_log=audit_log)
    rollback.set_dry_run(True)
    rollback.rollback("web", "snap-001")

    audit_log.record.assert_not_called()


def test_rollback_result_repr(registry, store):
    rollback = EnvRollback(registry, store)
    result = rollback.rollback("web", "snap-001")
    r = repr(result)
    assert "web" in r
    assert "snap-001" in r
    assert "OK" in r
