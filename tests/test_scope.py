"""Tests for envoy_cfg.scope."""

from __future__ import annotations

import pytest

from envoy_cfg.scope import ScopeResult, merge_scopes, scope_by_keys, scope_by_prefix


@pytest.fixture()
def base_env():
    return {
        "APP_HOST": "localhost",
        "APP_PORT": "8080",
        "DB_HOST": "db.local",
        "DB_PASSWORD": "secret",
        "LOG_LEVEL": "info",
    }


# --- scope_by_prefix ---

def test_scope_by_prefix_keeps_matching_keys(base_env):
    result = scope_by_prefix(base_env, prefix="APP_")
    assert set(result.scoped.keys()) == {"APP_HOST", "APP_PORT"}


def test_scope_by_prefix_excludes_non_matching(base_env):
    result = scope_by_prefix(base_env, prefix="APP_")
    assert "DB_HOST" in result.excluded_keys
    assert "LOG_LEVEL" in result.excluded_keys


def test_scope_by_prefix_strip_removes_prefix(base_env):
    result = scope_by_prefix(base_env, prefix="APP_", strip_prefix=True)
    assert "HOST" in result.scoped
    assert "PORT" in result.scoped
    assert "APP_HOST" not in result.scoped


def test_scope_by_prefix_preserves_values(base_env):
    result = scope_by_prefix(base_env, prefix="DB_")
    assert result.scoped["DB_PASSWORD"] == "secret"


def test_scope_by_prefix_custom_scope_name(base_env):
    result = scope_by_prefix(base_env, prefix="APP_", scope_name="application")
    assert result.scope_name == "application"


def test_scope_by_prefix_default_scope_name_strips_underscore(base_env):
    result = scope_by_prefix(base_env, prefix="APP_")
    assert result.scope_name == "APP"


def test_scope_by_prefix_empty_prefix_raises(base_env):
    with pytest.raises(ValueError, match="prefix"):
        scope_by_prefix(base_env, prefix="")


def test_scope_by_prefix_no_match_is_empty(base_env):
    result = scope_by_prefix(base_env, prefix="UNKNOWN_")
    assert result.is_empty


# --- scope_by_keys ---

def test_scope_by_keys_keeps_listed_keys(base_env):
    result = scope_by_keys(base_env, keys=["APP_HOST", "LOG_LEVEL"])
    assert set(result.scoped.keys()) == {"APP_HOST", "LOG_LEVEL"}


def test_scope_by_keys_excludes_unlisted(base_env):
    result = scope_by_keys(base_env, keys=["APP_HOST"])
    assert "DB_HOST" in result.excluded_keys


def test_scope_by_keys_missing_key_ignored(base_env):
    result = scope_by_keys(base_env, keys=["APP_HOST", "NONEXISTENT"])
    assert "NONEXISTENT" not in result.scoped
    assert "APP_HOST" in result.scoped


def test_scope_by_keys_empty_list_raises(base_env):
    with pytest.raises(ValueError, match="keys"):
        scope_by_keys(base_env, keys=[])


def test_scope_by_keys_custom_scope_name(base_env):
    result = scope_by_keys(base_env, keys=["LOG_LEVEL"], scope_name="logging")
    assert result.scope_name == "logging"


# --- ScopeResult ---

def test_scope_result_repr(base_env):
    result = scope_by_prefix(base_env, prefix="APP_")
    r = repr(result)
    assert "APP" in r
    assert "kept=" in r


def test_scope_result_original_unchanged(base_env):
    result = scope_by_prefix(base_env, prefix="APP_")
    assert result.original == base_env


# --- merge_scopes ---

def test_merge_scopes_combines_results(base_env):
    r1 = scope_by_prefix(base_env, prefix="APP_")
    r2 = scope_by_prefix(base_env, prefix="DB_")
    merged = merge_scopes(r1, r2)
    assert "APP_HOST" in merged
    assert "DB_HOST" in merged


def test_merge_scopes_later_wins_on_conflict():
    env = {"KEY": "first"}
    env2 = {"KEY": "second"}
    r1 = scope_by_keys(env, keys=["KEY"], scope_name="a")
    r2 = scope_by_keys(env2, keys=["KEY"], scope_name="b")
    merged = merge_scopes(r1, r2)
    assert merged["KEY"] == "second"
