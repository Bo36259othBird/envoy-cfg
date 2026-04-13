"""Tests for envoy_cfg.merge module."""

import pytest
from envoy_cfg.merge import merge_envs, merge_summary, MergeStrategy


@pytest.fixture
def base_env():
    return {"APP_ENV": "production", "DB_HOST": "db.prod", "LOG_LEVEL": "warn"}


@pytest.fixture
def incoming_env():
    return {"DB_HOST": "db.staging", "CACHE_URL": "redis://localhost", "LOG_LEVEL": "debug"}


def test_merge_union_incoming_wins_on_conflict(base_env, incoming_env):
    result = merge_envs(base_env, incoming_env, MergeStrategy.UNION)
    assert result["DB_HOST"] == "db.staging"
    assert result["LOG_LEVEL"] == "debug"


def test_merge_union_includes_all_keys(base_env, incoming_env):
    result = merge_envs(base_env, incoming_env, MergeStrategy.UNION)
    assert "APP_ENV" in result
    assert "CACHE_URL" in result
    assert "DB_HOST" in result


def test_merge_ours_keeps_base_on_conflict(base_env, incoming_env):
    result = merge_envs(base_env, incoming_env, MergeStrategy.OURS)
    assert result["DB_HOST"] == "db.prod"
    assert result["LOG_LEVEL"] == "warn"


def test_merge_ours_includes_non_conflicting_incoming(base_env, incoming_env):
    result = merge_envs(base_env, incoming_env, MergeStrategy.OURS)
    assert result["CACHE_URL"] == "redis://localhost"


def test_merge_theirs_incoming_wins(base_env, incoming_env):
    result = merge_envs(base_env, incoming_env, MergeStrategy.THEIRS)
    assert result["DB_HOST"] == "db.staging"
    assert result["LOG_LEVEL"] == "debug"


def test_merge_with_prefix_filter(base_env, incoming_env):
    result = merge_envs(base_env, incoming_env, prefix_filter="DB_")
    assert "DB_HOST" in result
    assert "CACHE_URL" not in result
    assert "LOG_LEVEL" not in result or result["LOG_LEVEL"] == "warn"


def test_merge_empty_incoming(base_env):
    result = merge_envs(base_env, {})
    assert result == base_env


def test_merge_empty_base(incoming_env):
    result = merge_envs({}, incoming_env)
    assert result == incoming_env


def test_merge_both_empty():
    result = merge_envs({}, {})
    assert result == {}


def test_merge_summary_counts(base_env, incoming_env):
    merged = merge_envs(base_env, incoming_env, MergeStrategy.UNION)
    summary = merge_summary(base_env, incoming_env, merged)
    assert summary["added"] == 1       # CACHE_URL
    assert summary["overwritten"] == 2  # DB_HOST, LOG_LEVEL
    assert summary["total"] == len(merged)


def test_merge_summary_no_changes(base_env):
    merged = merge_envs(base_env, {})
    summary = merge_summary(base_env, {}, merged)
    assert summary["added"] == 0
    assert summary["overwritten"] == 0
    assert summary["total"] == len(base_env)
