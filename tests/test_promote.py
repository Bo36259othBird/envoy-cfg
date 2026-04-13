"""Tests for env config promotion between targets."""

import pytest
from envoy_cfg.promote import EnvPromoter, PromoteResult
from envoy_cfg.merge import MergeStrategy
from envoy_cfg.targets import DeploymentTarget, TargetRegistry


@pytest.fixture
def registry() -> TargetRegistry:
    reg = TargetRegistry()
    reg.register(
        DeploymentTarget(
            name="staging",
            environment="staging",
            env_vars={"APP_NAME": "myapp", "DEBUG": "true", "DB_HOST": "staging-db"},
        )
    )
    reg.register(
        DeploymentTarget(
            name="production",
            environment="production",
            env_vars={"APP_NAME": "myapp", "DEBUG": "false"},
        )
    )
    return reg


def test_promote_adds_missing_keys(registry):
    promoter = EnvPromoter(registry)
    result = promoter.promote("staging", "production", MergeStrategy.UNION)
    assert result.success
    assert registry.get("production").env_vars.get("DB_HOST") == "staging-db"


def test_promote_union_keeps_dest_on_conflict(registry):
    promoter = EnvPromoter(registry)
    result = promoter.promote("staging", "production", MergeStrategy.UNION)
    assert result.success
    assert registry.get("production").env_vars["DEBUG"] == "false"


def test_promote_theirs_overwrites_dest(registry):
    promoter = EnvPromoter(registry)
    result = promoter.promote("staging", "production", MergeStrategy.THEIRS)
    assert result.success
    assert registry.get("production").env_vars["DEBUG"] == "true"


def test_promote_dry_run_does_not_apply(registry):
    promoter = EnvPromoter(registry, dry_run=True)
    result = promoter.promote("staging", "production", MergeStrategy.UNION)
    assert result.success
    assert result.dry_run
    assert "DB_HOST" not in registry.get("production").env_vars


def test_promote_missing_source_returns_failure(registry):
    promoter = EnvPromoter(registry)
    result = promoter.promote("nonexistent", "production")
    assert not result.success
    assert "not found" in result.message


def test_promote_missing_dest_returns_failure(registry):
    promoter = EnvPromoter(registry)
    result = promoter.promote("staging", "ghost")
    assert not result.success
    assert "not found" in result.message


def test_promote_result_repr_dry_run(registry):
    promoter = EnvPromoter(registry, dry_run=True)
    result = promoter.promote("staging", "production")
    assert "DRY-RUN" in repr(result)


def test_promote_result_repr_success(registry):
    promoter = EnvPromoter(registry)
    result = promoter.promote("staging", "production")
    assert "OK" in repr(result)


def test_promote_diff_reports_changes(registry):
    promoter = EnvPromoter(registry)
    result = promoter.promote("staging", "production", MergeStrategy.UNION)
    assert result.diff is not None
    keys_changed = {c.key for c in result.diff.changes}
    assert "DB_HOST" in keys_changed


def test_promote_no_changes_when_identical(registry):
    reg = TargetRegistry()
    env = {"APP": "x", "ENV": "prod"}
    reg.register(DeploymentTarget(name="a", environment="production", env_vars=dict(env)))
    reg.register(DeploymentTarget(name="b", environment="production", env_vars=dict(env)))
    promoter = EnvPromoter(reg)
    result = promoter.promote("a", "b", MergeStrategy.UNION)
    assert result.success
    assert len(result.diff.changes) == 0
