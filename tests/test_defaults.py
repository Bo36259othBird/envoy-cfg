"""Tests for envoy_cfg.defaults."""

import pytest
from envoy_cfg.defaults import apply_defaults, strip_defaults, DefaultsResult


@pytest.fixture
def base_env():
    return {"APP_HOST": "localhost", "APP_PORT": "8080", "APP_DEBUG": "true"}


@pytest.fixture
def defaults():
    return {"APP_PORT": "80", "APP_TIMEOUT": "30", "APP_LOG_LEVEL": "info"}


def test_apply_defaults_injects_missing_keys(base_env, defaults):
    result = apply_defaults(base_env, defaults)
    assert "APP_TIMEOUT" in result.env
    assert result.env["APP_TIMEOUT"] == "30"


def test_apply_defaults_does_not_overwrite_by_default(base_env, defaults):
    result = apply_defaults(base_env, defaults)
    assert result.env["APP_PORT"] == "8080"  # original preserved


def test_apply_defaults_overwrite_flag_replaces_existing(base_env, defaults):
    result = apply_defaults(base_env, defaults, overwrite=True)
    assert result.env["APP_PORT"] == "80"


def test_apply_defaults_applied_tracks_injected_keys(base_env, defaults):
    result = apply_defaults(base_env, defaults)
    assert "APP_TIMEOUT" in result.applied
    assert "APP_LOG_LEVEL" in result.applied
    assert "APP_PORT" not in result.applied


def test_apply_defaults_skipped_tracks_existing_keys(base_env, defaults):
    result = apply_defaults(base_env, defaults)
    assert "APP_PORT" in result.skipped
    assert result.skipped["APP_PORT"] == "8080"


def test_apply_defaults_is_clean_when_all_present():
    env = {"A": "1", "B": "2"}
    result = apply_defaults(env, {"A": "x", "B": "y"})
    assert result.is_clean


def test_apply_defaults_not_clean_when_keys_injected(base_env, defaults):
    result = apply_defaults(base_env, defaults)
    assert not result.is_clean


def test_apply_defaults_empty_defaults_returns_original(base_env):
    result = apply_defaults(base_env, {})
    assert result.env == base_env
    assert result.applied == {}
    assert result.skipped == {}


def test_apply_defaults_preserves_all_original_keys(base_env, defaults):
    result = apply_defaults(base_env, defaults)
    for k, v in base_env.items():
        assert result.env[k] == v


def test_defaults_result_repr(base_env, defaults):
    result = apply_defaults(base_env, defaults)
    r = repr(result)
    assert "applied=" in r
    assert "skipped=" in r
    assert "total=" in r


def test_strip_defaults_removes_matching_values():
    env = {"A": "1", "B": "2", "C": "3"}
    defs = {"A": "1", "C": "99"}  # A matches, C does not
    stripped = strip_defaults(env, defs)
    assert "A" not in stripped
    assert "B" in stripped
    assert "C" in stripped


def test_strip_defaults_keeps_overridden_values():
    env = {"PORT": "9000"}
    defs = {"PORT": "80"}
    stripped = strip_defaults(env, defs)
    assert "PORT" in stripped
    assert stripped["PORT"] == "9000"


def test_strip_defaults_empty_defaults_returns_full_env():
    env = {"X": "1", "Y": "2"}
    assert strip_defaults(env, {}) == env


def test_strip_defaults_all_match_returns_empty():
    env = {"A": "1", "B": "2"}
    assert strip_defaults(env, {"A": "1", "B": "2"}) == {}
