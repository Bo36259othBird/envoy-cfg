"""Tests for envoy_cfg.filter module."""

import pytest
from envoy_cfg.filter import (
    filter_by_value_glob,
    filter_by_value_regex,
    filter_by_empty_values,
    filter_by_key_glob,
    FilterResult,
)


@pytest.fixture
def base_env():
    return {
        "APP_NAME": "myapp",
        "APP_VERSION": "1.2.3",
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "SECRET_KEY": "abc123",
        "EMPTY_VAR": "",
        "WHITESPACE_VAR": "   ",
    }


def test_filter_by_value_glob_matches_pattern(base_env):
    result = filter_by_value_glob(base_env, "local*")
    assert "DB_HOST" in result.selected
    assert "APP_NAME" not in result.selected


def test_filter_by_value_glob_excluded_contains_rest(base_env):
    result = filter_by_value_glob(base_env, "local*")
    assert "APP_NAME" in result.excluded
    assert "DB_HOST" not in result.excluded


def test_filter_by_value_glob_strategy_label(base_env):
    result = filter_by_value_glob(base_env, "1.*")
    assert result.strategy == "value_glob:1.*"


def test_filter_by_value_regex_matches(base_env):
    result = filter_by_value_regex(base_env, r"^\d+$")
    assert "DB_PORT" in result.selected
    assert "APP_NAME" not in result.selected


def test_filter_by_value_regex_strategy_label(base_env):
    result = filter_by_value_regex(base_env, r"^\d+$")
    assert "value_regex" in result.strategy


def test_filter_by_value_regex_no_match_returns_empty(base_env):
    result = filter_by_value_regex(base_env, r"^ZZZNOMATCH$")
    assert result.selected == {}
    assert result.is_empty()


def test_filter_by_empty_values_keeps_empty(base_env):
    result = filter_by_empty_values(base_env, keep_empty=True)
    assert "EMPTY_VAR" in result.selected
    assert "WHITESPACE_VAR" in result.selected
    assert "APP_NAME" not in result.selected


def test_filter_by_empty_values_removes_empty(base_env):
    result = filter_by_empty_values(base_env, keep_empty=False)
    assert "EMPTY_VAR" not in result.selected
    assert "WHITESPACE_VAR" not in result.selected
    assert "APP_NAME" in result.selected


def test_filter_by_empty_values_strategy_non_empty(base_env):
    result = filter_by_empty_values(base_env, keep_empty=False)
    assert result.strategy == "non_empty_values"


def test_filter_by_empty_values_strategy_empty(base_env):
    result = filter_by_empty_values(base_env, keep_empty=True)
    assert result.strategy == "empty_values"


def test_filter_by_key_glob_matches_prefix(base_env):
    result = filter_by_key_glob(base_env, "DB_*")
    assert "DB_HOST" in result.selected
    assert "DB_PORT" in result.selected
    assert "APP_NAME" not in result.selected


def test_filter_by_key_glob_strategy_label(base_env):
    result = filter_by_key_glob(base_env, "APP_*")
    assert result.strategy == "key_glob:APP_*"


def test_filter_result_repr():
    r = FilterResult(selected={"A": "1"}, excluded={"B": "2"}, strategy="test")
    assert "FilterResult" in repr(r)
    assert "test" in repr(r)


def test_filter_selected_plus_excluded_equals_total(base_env):
    result = filter_by_key_glob(base_env, "APP_*")
    assert len(result.selected) + len(result.excluded) == len(base_env)
