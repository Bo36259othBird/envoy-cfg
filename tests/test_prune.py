"""Tests for envoy_cfg.prune."""
import pytest
from envoy_cfg.prune import prune_empty, prune_keys, prune_pattern, PruneResult


@pytest.fixture
def base_env():
    return {
        "APP_NAME": "myapp",
        "DEBUG": "",
        "SECRET_KEY": "abc123",
        "EMPTY_VAR": "   ",
        "DB_HOST": "localhost",
        "TMP_TOKEN": "xyz",
        "TMP_SESSION": "sess",
        "LOG_SUFFIX_OLD": "ignored",
    }


def test_prune_empty_removes_empty_values(base_env):
    result = prune_empty(base_env)
    assert "DEBUG" not in result.pruned
    assert "EMPTY_VAR" not in result.pruned


def test_prune_empty_keeps_non_empty_values(base_env):
    result = prune_empty(base_env)
    assert "APP_NAME" in result.pruned
    assert "SECRET_KEY" in result.pruned


def test_prune_empty_removed_keys_sorted(base_env):
    result = prune_empty(base_env)
    assert result.removed_keys == sorted(result.removed_keys)


def test_prune_empty_no_strip_keeps_whitespace_only(base_env):
    result = prune_empty(base_env, strip_whitespace=False)
    # "EMPTY_VAR" has "   " which is non-empty without stripping
    assert "EMPTY_VAR" in result.pruned
    # "DEBUG" has "" which is still empty
    assert "DEBUG" not in result.pruned


def test_prune_empty_is_clean_when_nothing_removed():
    env = {"A": "1", "B": "2"}
    result = prune_empty(env)
    assert result.is_clean is True


def test_prune_empty_reason_label(base_env):
    result = prune_empty(base_env)
    assert result.reason == "empty_value"


def test_prune_keys_removes_specified_keys(base_env):
    result = prune_keys(base_env, ["APP_NAME", "DB_HOST"])
    assert "APP_NAME" not in result.pruned
    assert "DB_HOST" not in result.pruned


def test_prune_keys_keeps_unspecified_keys(base_env):
    result = prune_keys(base_env, ["APP_NAME"])
    assert "SECRET_KEY" in result.pruned
    assert "DEBUG" in result.pruned


def test_prune_keys_missing_key_is_ignored(base_env):
    result = prune_keys(base_env, ["NONEXISTENT_KEY"])
    assert result.removed_keys == []
    assert result.is_clean is True


def test_prune_keys_reason_label(base_env):
    result = prune_keys(base_env, ["APP_NAME"])
    assert result.reason == "explicit_keys"


def test_prune_pattern_prefix(base_env):
    result = prune_pattern(base_env, prefix="TMP_")
    assert "TMP_TOKEN" not in result.pruned
    assert "TMP_SESSION" not in result.pruned
    assert "APP_NAME" in result.pruned


def test_prune_pattern_suffix(base_env):
    result = prune_pattern(base_env, suffix="_OLD")
    assert "LOG_SUFFIX_OLD" not in result.pruned
    assert "APP_NAME" in result.pruned


def test_prune_pattern_prefix_and_suffix(base_env):
    result = prune_pattern(base_env, prefix="TMP_", suffix="_OLD")
    assert "TMP_TOKEN" not in result.pruned
    assert "LOG_SUFFIX_OLD" not in result.pruned


def test_prune_pattern_reason_label(base_env):
    result = prune_pattern(base_env, prefix="TMP_")
    assert result.reason == "pattern"


def test_prune_result_original_is_unchanged(base_env):
    result = prune_empty(base_env)
    assert result.original == base_env
