"""Tests for envoy_cfg.dedup."""

import pytest
from envoy_cfg.dedup import dedup_env, find_duplicate_keys, DedupResult


@pytest.fixture
def mixed_case_env():
    # Simulate an env dict that was built programmatically with case collisions.
    return {
        "DATABASE_URL": "postgres://prod",
        "database_url": "postgres://dev",
        "API_KEY": "abc123",
        "Api_Key": "xyz789",
        "PORT": "8080",
    }


def test_dedup_case_sensitive_returns_clean(mixed_case_env):
    result = dedup_env(mixed_case_env, case_insensitive=False)
    assert result.is_clean
    assert result.removed_count == 0
    assert result.env == mixed_case_env


def test_dedup_case_insensitive_removes_duplicates(mixed_case_env):
    result = dedup_env(mixed_case_env, case_insensitive=True)
    assert result.removed_count == 2  # one dupe per collision group
    assert len(result.env) == 3  # DATABASE_URL, API_KEY, PORT


def test_dedup_keep_first_retains_first_key(mixed_case_env):
    result = dedup_env(mixed_case_env, case_insensitive=True, keep="first")
    assert "DATABASE_URL" in result.env
    assert "database_url" not in result.env
    assert result.env["DATABASE_URL"] == "postgres://prod"


def test_dedup_keep_last_retains_last_key(mixed_case_env):
    result = dedup_env(mixed_case_env, case_insensitive=True, keep="last")
    assert "database_url" in result.env
    assert "DATABASE_URL" not in result.env
    assert result.env["database_url"] == "postgres://dev"


def test_dedup_duplicates_list_contains_canonical_and_removed(mixed_case_env):
    result = dedup_env(mixed_case_env, case_insensitive=True, keep="first")
    canonical_keys = {canonical for canonical, _ in result.duplicates}
    assert "DATABASE_URL" in canonical_keys
    assert "API_KEY" in canonical_keys


def test_dedup_no_collisions_is_clean():
    env = {"FOO": "1", "BAR": "2", "BAZ": "3"}
    result = dedup_env(env, case_insensitive=True)
    assert result.is_clean
    assert result.removed_count == 0
    assert result.env == env


def test_dedup_empty_env():
    result = dedup_env({}, case_insensitive=True)
    assert result.is_clean
    assert result.env == {}
    assert result.duplicates == []


def test_dedup_result_repr_contains_info(mixed_case_env):
    result = dedup_env(mixed_case_env, case_insensitive=True)
    r = repr(result)
    assert "DedupResult" in r
    assert "removed=" in r


def test_find_duplicate_keys_returns_collisions(mixed_case_env):
    dupes = find_duplicate_keys(mixed_case_env)
    assert "database_url" in dupes
    assert "api_key" in dupes
    assert len(dupes["database_url"]) == 2


def test_find_duplicate_keys_empty_when_no_collisions():
    env = {"FOO": "1", "BAR": "2"}
    assert find_duplicate_keys(env) == {}


def test_dedup_preserves_non_duplicate_values(mixed_case_env):
    result = dedup_env(mixed_case_env, case_insensitive=True)
    assert result.env["PORT"] == "8080"
