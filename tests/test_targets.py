"""Tests for envoy_cfg.targets module."""

import pytest

from envoy_cfg.targets import DeploymentTarget, TargetRegistry


# --- DeploymentTarget tests ---

def test_create_valid_target():
    t = DeploymentTarget(name="web-prod", environment="production", url="https://example.com")
    assert t.name == "web-prod"
    assert t.environment == "production"
    assert t.url == "https://example.com"
    assert t.tags == []


def test_create_target_with_tags():
    t = DeploymentTarget(name="api", environment="staging", tags=["backend", "api"])
    assert t.tags == ["backend", "api"]


def test_invalid_environment_raises():
    with pytest.raises(ValueError, match="Invalid environment"):
        DeploymentTarget(name="test", environment="qa")


def test_empty_name_raises():
    with pytest.raises(ValueError, match="name must not be empty"):
        DeploymentTarget(name="  ", environment="development")


def test_to_dict_roundtrip():
    t = DeploymentTarget(name="svc", environment="staging", url="http://svc", tags=["x"])
    d = t.to_dict()
    restored = DeploymentTarget.from_dict(d)
    assert restored.name == t.name
    assert restored.environment == t.environment
    assert restored.url == t.url
    assert restored.tags == t.tags


# --- TargetRegistry tests ---

def test_register_and_get_target():
    registry = TargetRegistry()
    t = DeploymentTarget(name="db", environment="production")
    registry.register(t)
    assert registry.get("db") is t


def test_duplicate_registration_raises():
    registry = TargetRegistry()
    t = DeploymentTarget(name="db", environment="production")
    registry.register(t)
    with pytest.raises(ValueError, match="already registered"):
        registry.register(DeploymentTarget(name="db", environment="staging"))


def test_get_nonexistent_returns_none():
    registry = TargetRegistry()
    assert registry.get("ghost") is None


def test_remove_target():
    registry = TargetRegistry()
    registry.register(DeploymentTarget(name="tmp", environment="development"))
    assert registry.remove("tmp") is True
    assert registry.get("tmp") is None


def test_remove_nonexistent_returns_false():
    registry = TargetRegistry()
    assert registry.remove("nobody") is False


def test_list_targets_all():
    registry = TargetRegistry()
    registry.register(DeploymentTarget(name="a", environment="production"))
    registry.register(DeploymentTarget(name="b", environment="staging"))
    assert len(registry.list_targets()) == 2


def test_list_targets_filtered_by_environment():
    registry = TargetRegistry()
    registry.register(DeploymentTarget(name="a", environment="production"))
    registry.register(DeploymentTarget(name="b", environment="staging"))
    registry.register(DeploymentTarget(name="c", environment="production"))
    prod = registry.list_targets(environment="production")
    assert len(prod) == 2
    assert all(t.environment == "production" for t in prod)


def test_registry_len():
    registry = TargetRegistry()
    assert len(registry) == 0
    registry.register(DeploymentTarget(name="x", environment="development"))
    assert len(registry) == 1
