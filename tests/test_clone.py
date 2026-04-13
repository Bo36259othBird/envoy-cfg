"""Tests for envoy_cfg.clone module."""

import pytest
from envoy_cfg.targets import DeploymentTarget, TargetRegistry
from envoy_cfg.clone import EnvCloner, CloneResult
from envoy_cfg.merge import MergeStrategy


@pytest.fixture
def registry():
    reg = TargetRegistry()
    reg.register(
        DeploymentTarget(
            name="staging",
            environment="staging",
            env={"APP_HOST": "staging.example.com", "DB_PASS": "s3cret", "DEBUG": "true"},
        )
    )
    reg.register(
        DeploymentTarget(
            name="production",
            environment="production",
            env={"APP_HOST": "prod.example.com", "LOG_LEVEL": "warn"},
        )
    )
    return reg


def test_clone_copies_keys_from_source(registry):
    cloner = EnvCloner(registry)
    result = cloner.clone("staging", "production", strategy=MergeStrategy.UNION)
    assert result.success is True
    assert result.keys_copied > 0
    prod = registry.get("production")
    assert "DB_PASS" in prod.env
    assert "DEBUG" in prod.env


def test_clone_union_keeps_dest_values_on_conflict(registry):
    cloner = EnvCloner(registry)
    cloner.clone("staging", "production", strategy=MergeStrategy.UNION)
    prod = registry.get("production")
    # production APP_HOST should win under UNION (ours) strategy
    assert prod.env["APP_HOST"] == "prod.example.com"


def test_clone_theirs_overwrites_dest(registry):
    cloner = EnvCloner(registry)
    cloner.clone("staging", "production", strategy=MergeStrategy.THEIRS)
    prod = registry.get("production")
    assert prod.env["APP_HOST"] == "staging.example.com"


def test_clone_dry_run_does_not_modify_dest(registry):
    cloner = EnvCloner(registry)
    cloner.set_dry_run(True)
    original_env = dict(registry.get("production").env)
    result = cloner.clone("staging", "production", strategy=MergeStrategy.THEIRS)
    assert result.dry_run is True
    assert registry.get("production").env == original_env


def test_clone_missing_source_returns_error(registry):
    cloner = EnvCloner(registry)
    result = cloner.clone("nonexistent", "production")
    assert result.success is False
    assert "nonexistent" in result.error


def test_clone_missing_dest_returns_error(registry):
    cloner = EnvCloner(registry)
    result = cloner.clone("staging", "nowhere")
    assert result.success is False
    assert "nowhere" in result.error


def test_clone_overwrite_replaces_dest_entirely(registry):
    cloner = EnvCloner(registry)
    cloner.clone("staging", "production", strategy=MergeStrategy.UNION, overwrite=True)
    prod = registry.get("production")
    # With overwrite=True base_env is empty, so source wins entirely
    assert prod.env["APP_HOST"] == "staging.example.com"
    # LOG_LEVEL was only in production and should be gone
    assert "LOG_LEVEL" not in prod.env


def test_clone_result_repr_dry_run(registry):
    cloner = EnvCloner(registry)
    cloner.set_dry_run(True)
    result = cloner.clone("staging", "production")
    assert "DRY RUN" in repr(result)


def test_clone_result_repr_success(registry):
    cloner = EnvCloner(registry)
    result = cloner.clone("staging", "production")
    assert "OK" in repr(result)
    assert "staging" in repr(result)
    assert "production" in repr(result)
