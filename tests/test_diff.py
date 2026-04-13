"""Tests for envoy_cfg.diff module."""

import pytest
from envoy_cfg.diff import diff_envs, ChangeType, EnvChange, DiffResult


@pytest.fixture
def base_env():
    return {"APP_ENV": "production", "DB_HOST": "localhost", "SECRET_KEY": "abc123"}


@pytest.fixture
def updated_env():
    return {"APP_ENV": "staging", "DB_HOST": "localhost", "NEW_VAR": "hello"}


def test_diff_detects_added_keys(base_env, updated_env):
    result = diff_envs(base_env, updated_env)
    keys = [c.key for c in result.added]
    assert "NEW_VAR" in keys


def test_diff_detects_removed_keys(base_env, updated_env):
    result = diff_envs(base_env, updated_env)
    keys = [c.key for c in result.removed]
    assert "SECRET_KEY" in keys


def test_diff_detects_modified_keys(base_env, updated_env):
    result = diff_envs(base_env, updated_env)
    keys = [c.key for c in result.modified]
    assert "APP_ENV" in keys


def test_diff_unchanged_key_not_in_changes_by_default(base_env, updated_env):
    result = diff_envs(base_env, updated_env)
    keys = [c.key for c in result.changes]
    assert "DB_HOST" not in keys


def test_diff_include_unchanged(base_env, updated_env):
    result = diff_envs(base_env, updated_env, include_unchanged=True)
    unchanged = [c for c in result.changes if c.change_type == ChangeType.UNCHANGED]
    assert any(c.key == "DB_HOST" for c in unchanged)


def test_diff_has_changes_true(base_env, updated_env):
    result = diff_envs(base_env, updated_env)
    assert result.has_changes is True


def test_diff_has_changes_false():
    env = {"A": "1", "B": "2"}
    result = diff_envs(env, env.copy())
    assert result.has_changes is False


def test_diff_empty_envs():
    result = diff_envs({}, {})
    assert result.changes == []
    assert result.has_changes is False


def test_diff_summary_string(base_env, updated_env):
    result = diff_envs(base_env, updated_env)
    summary = result.summary()
    assert "added" in summary
    assert "removed" in summary
    assert "modified" in summary


def test_env_change_repr_added():
    change = EnvChange("FOO", ChangeType.ADDED, new_value="bar")
    assert repr(change).startswith("+")


def test_env_change_repr_removed():
    change = EnvChange("FOO", ChangeType.REMOVED, old_value="bar")
    assert repr(change).startswith("-")


def test_env_change_repr_modified():
    change = EnvChange("FOO", ChangeType.MODIFIED, old_value="old", new_value="new")
    assert repr(change).startswith("~")


def test_diff_keys_sorted(base_env, updated_env):
    result = diff_envs(base_env, updated_env)
    keys = [c.key for c in result.changes]
    assert keys == sorted(keys)
