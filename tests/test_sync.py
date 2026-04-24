"""Tests for envoy_cfg.sync module."""

import pytest

from envoy_cfg.sync import EnvSyncer, SyncResult
from envoy_cfg.targets import DeploymentTarget, TargetRegistry


ENV_VARS = {
    "APP_NAME": "envoy",
    "DATABASE_PASSWORD": "s3cr3t",
    "PORT": "8080",
    "API_SECRET_KEY": "topsecret",
}


@pytest.fixture
def registry_with_targets():
    registry = TargetRegistry()
    registry.register(DeploymentTarget(name="prod-web", environment="production"))
    registry.register(DeploymentTarget(name="staging-web", environment="staging"))
    registry.register(DeploymentTarget(name="dev-web", environment="development"))
    return registry


def test_sync_to_existing_target(registry_with_targets):
    syncer = EnvSyncer(registry_with_targets)
    syncer.set_dry_run(True)
    result = syncer.sync_to_target("prod-web", ENV_VARS)
    assert result.success is True
    assert result.target_name == "prod-web"
    assert set(result.keys_synced) == set(ENV_VARS.keys())


def test_sync_to_nonexistent_target(registry_with_targets):
    syncer = EnvSyncer(registry_with_targets)
    result = syncer.sync_to_target("ghost-target", ENV_VARS)
    assert result.success is False
    assert "not found" in result.error
    assert result.keys_synced == []


def test_sync_to_all_targets(registry_with_targets):
    syncer = EnvSyncer(registry_with_targets)
    syncer.set_dry_run(True)
    results = syncer.sync_to_all(ENV_VARS)
    assert len(results) == 3
    assert all(r.success for r in results)


def test_sync_to_all_filtered_by_environment(registry_with_targets):
    syncer = EnvSyncer(registry_with_targets)
    syncer.set_dry_run(True)
    results = syncer.sync_to_all(ENV_VARS, environment="production")
    assert len(results) == 1
    assert results[0].target_name == "prod-web"


def test_sync_to_all_filtered_by_unknown_environment(registry_with_targets):
    """Filtering by an environment with no registered targets should return an empty list."""
    syncer = EnvSyncer(registry_with_targets)
    syncer.set_dry_run(True)
    results = syncer.sync_to_all(ENV_VARS, environment="canary")
    assert results == []


def test_sync_result_repr_success():
    result = SyncResult(target_name="web", success=True, keys_synced=["A", "B"])
    assert "OK" in repr(result)
    assert "web" in repr(result)


def test_sync_result_repr_failure():
    result = SyncResult(target_name="web", success=False, error="connection refused")
    assert "FAILED" in repr(result)
    assert "connection refused" in repr(result)


def test_dry_run_does_not_raise(registry_with_targets):
    syncer = EnvSyncer(registry_with_targets)
    syncer.set_dry_run(True)
    result = syncer.sync_to_target("prod-web", ENV_VARS)
    assert result.success is True


def test_sync_empty_env_vars(registry_with_targets):
    syncer = EnvSyncer(registry_with_targets)
    syncer.set_dry_run(True)
    result = syncer.sync_to_target("dev-web", {})
    assert result.success is True
    assert result.keys_synced == []


def test_sync_to_all_returns_result_per_target(registry_with_targets):
    """Each target in the registry should produce exactly one SyncResult."""
    syncer = EnvSyncer(registry_with_targets)
    syncer.set_dry_run(True)
    results = syncer.sync_to_all(ENV_VARS)
    target_names = {r.target_name for r in results}
    assert target_names == {"prod-web", "staging-web", "dev-web"}
