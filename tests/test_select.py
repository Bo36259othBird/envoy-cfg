"""Tests for envoy_cfg.select."""
import pytest

from envoy_cfg.select import (
    SelectResult,
    select_by_glob,
    select_by_keys,
    select_by_regex,
)


@pytest.fixture()
def base_env() -> dict:
    return {
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "APP_NAME": "envoy",
        "APP_ENV": "production",
        "SECRET_KEY": "abc123",
    }


# --- select_by_keys ---

def test_select_by_keys_returns_only_listed(base_env):
    result = select_by_keys(base_env, ["DB_HOST", "APP_NAME"])
    assert set(result.selected.keys()) == {"DB_HOST", "APP_NAME"}


def test_select_by_keys_excluded_contains_rest(base_env):
    result = select_by_keys(base_env, ["DB_HOST"])
    assert "DB_PORT" in result.excluded
    assert "APP_NAME" in result.excluded


def test_select_by_keys_missing_key_not_in_selected(base_env):
    result = select_by_keys(base_env, ["NONEXISTENT"])
    assert result.selected == {}


def test_select_by_keys_strategy_label(base_env):
    result = select_by_keys(base_env, ["DB_HOST"])
    assert result.strategy == "keys"


def test_select_by_keys_empty_list_raises(base_env):
    with pytest.raises(ValueError, match="empty"):
        select_by_keys(base_env, [])


def test_select_by_keys_is_empty_when_no_match(base_env):
    result = select_by_keys(base_env, ["MISSING"])
    assert result.is_empty


# --- select_by_glob ---

def test_select_by_glob_matches_prefix(base_env):
    result = select_by_glob(base_env, "DB_*")
    assert set(result.selected.keys()) == {"DB_HOST", "DB_PORT"}


def test_select_by_glob_excluded_does_not_contain_matched(base_env):
    result = select_by_glob(base_env, "APP_*")
    assert "DB_HOST" in result.excluded
    assert "APP_NAME" not in result.excluded


def test_select_by_glob_strategy_label(base_env):
    result = select_by_glob(base_env, "DB_*")
    assert result.strategy == "glob"
    assert result.pattern == "DB_*"


def test_select_by_glob_empty_pattern_raises(base_env):
    with pytest.raises(ValueError, match="empty"):
        select_by_glob(base_env, "")


def test_select_by_glob_no_match_is_empty(base_env):
    result = select_by_glob(base_env, "NOPE_*")
    assert result.is_empty


# --- select_by_regex ---

def test_select_by_regex_matches_pattern(base_env):
    result = select_by_regex(base_env, r"^DB_")
    assert set(result.selected.keys()) == {"DB_HOST", "DB_PORT"}


def test_select_by_regex_partial_match(base_env):
    result = select_by_regex(base_env, r"HOST|NAME")
    assert "DB_HOST" in result.selected
    assert "APP_NAME" in result.selected


def test_select_by_regex_strategy_label(base_env):
    result = select_by_regex(base_env, r"SECRET")
    assert result.strategy == "regex"


def test_select_by_regex_empty_pattern_raises(base_env):
    with pytest.raises(ValueError, match="empty"):
        select_by_regex(base_env, "")


def test_select_by_regex_invalid_pattern_raises(base_env):
    with pytest.raises(ValueError, match="invalid regex"):
        select_by_regex(base_env, "[unclosed")


def test_select_result_repr_contains_strategy(base_env):
    result = select_by_keys(base_env, ["DB_HOST"])
    assert "keys" in repr(result)
