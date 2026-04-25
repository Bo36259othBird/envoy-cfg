"""Tests for envoy_cfg.unique."""

from __future__ import annotations

import pytest

from envoy_cfg.unique import UniqueResult, find_unique_values


@pytest.fixture
def base_env():
    return {
        "DB_HOST": "localhost",
        "CACHE_HOST": "localhost",   # duplicate of DB_HOST
        "APP_ENV": "production",
        "STAGE": "production",       # duplicate of APP_ENV
        "PORT": "8080",
        "EMPTY_A": "",
        "EMPTY_B": "",
    }


def test_find_unique_values_returns_unique_result(base_env):
    result = find_unique_values(base_env)
    assert isinstance(result, UniqueResult)


def test_find_unique_values_detects_shared_values(base_env):
    result = find_unique_values(base_env)
    assert "localhost" in result.duplicate_values
    assert "production" in result.duplicate_values


def test_find_unique_values_keys_sorted(base_env):
    result = find_unique_values(base_env)
    assert result.duplicate_values["localhost"] == ["CACHE_HOST", "DB_HOST"]


def test_find_unique_values_ignores_empty_by_default(base_env):
    result = find_unique_values(base_env)
    assert "" not in result.duplicate_values


def test_find_unique_values_includes_empty_when_flag_set(base_env):
    result = find_unique_values(base_env, ignore_empty=False)
    assert "" in result.duplicate_values
    assert sorted(result.duplicate_values[""]) == ["EMPTY_A", "EMPTY_B"]


def test_find_unique_values_unique_key_not_in_duplicates(base_env):
    result = find_unique_values(base_env)
    assert "8080" not in result.duplicate_values


def test_is_clean_false_when_duplicates_exist(base_env):
    result = find_unique_values(base_env)
    assert result.is_clean() is False


def test_is_clean_true_for_all_unique_env():
    env = {"A": "1", "B": "2", "C": "3"}
    result = find_unique_values(env)
    assert result.is_clean() is True


def test_shared_count(base_env):
    result = find_unique_values(base_env)
    # localhost: 2 keys, production: 2 keys
    assert result.shared_count() == 4


def test_case_insensitive_groups_differently():
    env = {"A": "Hello", "B": "hello", "C": "HELLO"}
    result = find_unique_values(env, case_sensitive=False)
    assert "hello" in result.duplicate_values
    assert len(result.duplicate_values["hello"]) == 3


def test_case_sensitive_does_not_group_mixed_case():
    env = {"A": "Hello", "B": "hello"}
    result = find_unique_values(env, case_sensitive=True)
    assert result.is_clean() is True


def test_strategy_label_case_sensitive():
    result = find_unique_values({"A": "x"}, case_sensitive=True)
    assert result.strategy == "case-sensitive"


def test_strategy_label_case_insensitive():
    result = find_unique_values({"A": "x"}, case_sensitive=False)
    assert result.strategy == "case-insensitive"


def test_repr_includes_strategy_and_count(base_env):
    result = find_unique_values(base_env)
    r = repr(result)
    assert "case-sensitive" in r
    assert "duplicate_value_groups" in r


def test_empty_env_is_clean():
    result = find_unique_values({})
    assert result.is_clean() is True
    assert result.shared_count() == 0
