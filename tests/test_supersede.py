"""Tests for envoy_cfg.supersede."""
import pytest
from envoy_cfg.supersede import supersede_env, SupersedeResult


@pytest.fixture
def base_env():
    return {"HOST": "localhost", "PORT": "5432", "DEBUG": "false"}


@pytest.fixture
def overrides():
    return {"PORT": "9999", "SECRET_KEY": "abc123"}


def test_supersede_returns_result(base_env, overrides):
    result = supersede_env(base_env, overrides)
    assert isinstance(result, SupersedeResult)


def test_supersede_overrides_existing_key(base_env, overrides):
    result = supersede_env(base_env, overrides)
    assert result.env["PORT"] == "9999"


def test_supersede_keeps_unaffected_keys(base_env, overrides):
    result = supersede_env(base_env, overrides)
    assert result.env["HOST"] == "localhost"
    assert result.env["DEBUG"] == "false"


def test_supersede_injects_new_key_by_default(base_env, overrides):
    result = supersede_env(base_env, overrides)
    assert "SECRET_KEY" in result.env
    assert "SECRET_KEY" in result.injected


def test_supersede_no_inject_drops_new_key(base_env, overrides):
    result = supersede_env(base_env, overrides, inject_new=False)
    assert "SECRET_KEY" not in result.env
    assert result.injected == []


def test_supersede_overridden_list_sorted(base_env):
    ovr = {"PORT": "1", "DEBUG": "true"}
    result = supersede_env(base_env, ovr)
    assert result.overridden == sorted(result.overridden)


def test_supersede_injected_list_sorted():
    result = supersede_env({}, {"Z": "1", "A": "2", "M": "3"})
    assert result.injected == ["A", "M", "Z"]


def test_supersede_is_clean_when_no_changes(base_env):
    result = supersede_env(base_env, {"HOST": "localhost"})
    assert result.is_clean()


def test_supersede_not_clean_when_overridden(base_env, overrides):
    result = supersede_env(base_env, overrides)
    assert not result.is_clean()


def test_supersede_repr_contains_counts(base_env, overrides):
    result = supersede_env(base_env, overrides)
    r = repr(result)
    assert "overridden=" in r
    assert "injected=" in r


def test_supersede_empty_overrides_leaves_base_unchanged(base_env):
    result = supersede_env(base_env, {})
    assert result.env == base_env
    assert result.is_clean()


def test_supersede_empty_base_injects_all(overrides):
    result = supersede_env({}, overrides)
    assert set(result.injected) == set(overrides.keys())
