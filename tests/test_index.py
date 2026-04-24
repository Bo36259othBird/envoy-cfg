"""Tests for envoy_cfg.index."""
from __future__ import annotations

import pytest

from envoy_cfg.index import IndexResult, build_index


@pytest.fixture()
def base_env() -> dict:
    return {
        "APP_HOST": "localhost",
        "APP_PORT": "8080",
        "DB_URL": "postgres://localhost/mydb",
        "SECRET_KEY": "s3cr3t",
        "debug": "true",
    }


def test_build_index_returns_index_result(base_env):
    result = build_index(base_env)
    assert isinstance(result, IndexResult)


def test_build_index_total_matches_env_size(base_env):
    result = build_index(base_env)
    assert result.total == len(base_env)


def test_build_index_strategy_exact(base_env):
    result = build_index(base_env)
    assert result.strategy == "exact"


def test_build_index_strategy_case_insensitive(base_env):
    result = build_index(base_env, case_insensitive=True)
    assert result.strategy == "case_insensitive"


def test_build_index_case_insensitive_uppercases_keys(base_env):
    result = build_index(base_env, case_insensitive=True)
    assert "DEBUG" in result.index
    assert "debug" not in result.index


def test_lookup_existing_key(base_env):
    result = build_index(base_env)
    assert result.lookup("APP_HOST") == "localhost"


def test_lookup_missing_key_returns_none(base_env):
    result = build_index(base_env)
    assert result.lookup("MISSING") is None


def test_lookup_case_insensitive(base_env):
    result = build_index(base_env, case_insensitive=True)
    assert result.lookup("DEBUG") == "true"


def test_search_keys_glob_prefix(base_env):
    result = build_index(base_env)
    keys = result.search_keys("APP_*")
    assert "APP_HOST" in keys
    assert "APP_PORT" in keys
    assert "DB_URL" not in keys


def test_search_keys_returns_sorted(base_env):
    result = build_index(base_env)
    keys = result.search_keys("APP_*")
    assert keys == sorted(keys)


def test_search_keys_no_match_returns_empty(base_env):
    result = build_index(base_env)
    assert result.search_keys("NOPE_*") == []


def test_search_values_glob(base_env):
    result = build_index(base_env)
    hits = result.search_values("*localhost*")
    assert "APP_HOST" in hits
    assert "DB_URL" in hits
    assert "APP_PORT" not in hits


def test_search_values_returns_dict(base_env):
    result = build_index(base_env)
    hits = result.search_values("8080")
    assert isinstance(hits, dict)
    assert hits["APP_PORT"] == "8080"


def test_is_empty_false_for_populated(base_env):
    result = build_index(base_env)
    assert not result.is_empty()


def test_is_empty_true_for_empty_env():
    result = build_index({})
    assert result.is_empty()


def test_build_index_raises_on_non_dict():
    with pytest.raises(TypeError):
        build_index(["not", "a", "dict"])  # type: ignore[arg-type]


def test_build_index_does_not_mutate_original(base_env):
    original_keys = set(base_env.keys())
    build_index(base_env, case_insensitive=True)
    assert set(base_env.keys()) == original_keys
