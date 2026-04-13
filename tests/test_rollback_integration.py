"""Integration tests: rollback interacts with snapshot store and audit log."""

import pytest
from envoy_cfg.rollback import EnvRollback
from envoy_cfg.snapshot import EnvSnapshot, SnapshotStore
from envoy_cfg.targets import DeploymentTarget, TargetRegistry
from envoy_cfg.audit import AuditLog


@pytest.fixture
def full_setup(tmp_path):
    reg = TargetRegistry()
    target = DeploymentTarget(
        name="svc",
        environment="staging",
        env={"FOO": "bar", "SECRET_KEY": "old-secret"},
    )
    reg.register(target)

    store = SnapshotStore()
    snap = EnvSnapshot(
        snapshot_id="snap-int-01",
        target_name="svc",
        environment="staging",
        env={"FOO": "baz", "SECRET_KEY": "new-secret", "ADDED": "yes"},
        timestamp="2024-03-15T08:00:00",
    )
    store._snapshots["snap-int-01"] = snap

    log_file = tmp_path / "audit.json"
    audit = AuditLog(str(log_file))

    return reg, store, audit


def test_rollback_updates_env_and_logs(full_setup):
    reg, store, audit = full_setup
    rollback = EnvRollback(reg, store, audit_log=audit)
    result = rollback.rollback("svc", "snap-int-01")

    assert result.applied is True
    target = reg.get("svc")
    assert target.env["FOO"] == "baz"
    assert target.env["ADDED"] == "yes"
    assert target.env["SECRET_KEY"] == "new-secret"

    entries = audit.entries()
    assert len(entries) == 3
    assert all(e.action == "rollback" for e in entries)
    assert all(e.target_name == "svc" for e in entries)
    keys_logged = {e.key for e in entries}
    assert keys_logged == {"FOO", "SECRET_KEY", "ADDED"}


def test_rollback_dry_run_leaves_env_unchanged(full_setup):
    reg, store, audit = full_setup
    rollback = EnvRollback(reg, store, audit_log=audit)
    rollback.set_dry_run(True)
    result = rollback.rollback("svc", "snap-int-01")

    assert result.dry_run is True
    target = reg.get("svc")
    assert target.env["FOO"] == "bar"  # original value preserved
    assert "ADDED" not in target.env
    assert len(audit.entries()) == 0
