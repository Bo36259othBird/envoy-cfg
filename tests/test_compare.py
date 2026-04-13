"""Tests for EnvComparer and CompareResult."""

import pytest

from envoy_cfg.compare import CompareResult, EnvComparer
from envoy_cfg.targets import DeploymentTarget, TargetRegistry


@pytest.fixture
def registry() -> TargetRegistry:
    reg = TargetRegistry()
    reg.register(
        DeploymentTarget(
            name="staging",
            environment="staging",
            env={"APP_HOST": "staging.example.com", "SECRET_KEY": "abc123", "DEBUG": "true"},
        )
    )
    reg.register(
        DeploymentTarget(
            name="production",
            environment="production",
            env={"APP_HOST": "prod.example.com", "SECRET_KEY": "xyz789"},
        )
    )
    reg.register(
        DeploymentTarget(
            name="dev",
            environment="development",
            env={"APP_HOST": "localhost", "SECRET_KEY": "devkey", "DEBUG": "true"},
        )
    )
    return reg


def test_compare_detects_added_keys(registry):
    comparer = EnvComparer(registry, mask_secrets=False)
    result = comparer.compare("production", "staging")
    assert result is not None
    assert "DEBUG" in [c.key for c in result.diff.added]


def test_compare_detects_removed_keys(registry):
    comparer = EnvComparer(registry, mask_secrets=False)
    result = comparer.compare("staging", "production")
    assert result is not None
    assert "DEBUG" in [c.key for c in result.diff.removed]


def test_compare_detects_modified_keys(registry):
    comparer = EnvComparer(registry, mask_secrets=False)
    result = comparer.compare("staging", "production")
    assert result is not None
    modified_keys = [c.key for c in result.diff.modified]
    assert "APP_HOST" in modified_keys


def test_compare_masks_secrets_by_default(registry):
    comparer = EnvComparer(registry, mask_secrets=True)
    result = comparer.compare("staging", "production")
    assert result is not None
    assert result.masked is True
    for change in result.diff.modified:
        if change.key == "SECRET_KEY":
            assert "abc123" not in str(change.old_value)
            assert "xyz789" not in str(change.new_value)


def test_compare_no_differences_when_identical(registry):
    comparer = EnvComparer(registry, mask_secrets=False)
    result = comparer.compare("staging", "staging")
    assert result is not None
    assert not result.has_differences


def test_compare_returns_none_for_missing_source(registry):
    comparer = EnvComparer(registry)
    result = comparer.compare("nonexistent", "production")
    assert result is None


def test_compare_returns_none_for_missing_dest(registry):
    comparer = EnvComparer(registry)
    result = comparer.compare("staging", "nonexistent")
    assert result is None


def test_compare_all_to_excludes_dest(registry):
    comparer = EnvComparer(registry, mask_secrets=False)
    results = comparer.compare_all_to("production")
    dest_names = [r.destination for r in results]
    assert "production" not in dest_names
    assert all(r.destination == "production" for r in results)


def test_compare_all_to_filters_by_environment(registry):
    comparer = EnvComparer(registry, mask_secrets=False)
    results = comparer.compare_all_to("production", environment="development")
    assert len(results) == 1
    assert results[0].source == "dev"


def test_compare_result_repr(registry):
    comparer = EnvComparer(registry, mask_secrets=False)
    result = comparer.compare("staging", "production")
    assert result is not None
    r = repr(result)
    assert "staging" in r
    assert "production" in r
