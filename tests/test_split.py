"""Tests for envoy_cfg.split."""

from __future__ import annotations

import pytest

from envoy_cfg.split import SplitResult, merge_partitions, split_env


@pytest.fixture
def base_env():
    return {
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "AWS_ACCESS_KEY": "AKIA123",
        "AWS_SECRET_KEY": "secret",
        "APP_DEBUG": "true",
        "APP_ENV": "production",
        "LOG_LEVEL": "info",
    }


def test_split_by_prefix_creates_partitions(base_env):
    result = split_env(base_env, {"db": r"^DB_", "aws": r"^AWS_"})
    assert set(result.partitions["db"]) == {"DB_HOST", "DB_PORT"}
    assert set(result.partitions["aws"]) == {"AWS_ACCESS_KEY", "AWS_SECRET_KEY"}


def test_split_unmatched_keys_captured(base_env):
    result = split_env(base_env, {"db": r"^DB_"})
    assert "APP_DEBUG" in result.unmatched
    assert "LOG_LEVEL" in result.unmatched
    assert "AWS_ACCESS_KEY" in result.unmatched


def test_split_is_complete_when_all_matched(base_env):
    result = split_env(
        base_env,
        {"db": r"^DB_", "aws": r"^AWS_", "app": r"^APP_", "log": r"^LOG_"},
    )
    assert result.is_complete is True
    assert result.unmatched == {}


def test_split_is_not_complete_with_unmatched(base_env):
    result = split_env(base_env, {"db": r"^DB_"})
    assert result.is_complete is False


def test_split_no_overlap_first_rule_wins(base_env):
    # DB_ matches both rules; first rule should claim it
    result = split_env(
        base_env,
        {"first": r"^DB_", "second": r"^DB_PORT"},
        allow_overlap=False,
    )
    assert "DB_PORT" in result.partitions["first"]
    assert "DB_PORT" not in result.partitions["second"]


def test_split_allow_overlap_key_in_multiple_partitions(base_env):
    result = split_env(
        base_env,
        {"all_db": r"^DB_", "port_keys": r"PORT"},
        allow_overlap=True,
    )
    assert "DB_PORT" in result.partitions["all_db"]
    assert "DB_PORT" in result.partitions["port_keys"]


def test_split_empty_rules_raises():
    with pytest.raises(ValueError, match="At least one rule"):
        split_env({"KEY": "val"}, {})


def test_split_empty_env_produces_empty_partitions():
    result = split_env({}, {"db": r"^DB_", "app": r"^APP_"})
    assert result.partitions["db"] == {}
    assert result.partitions["app"] == {}
    assert result.unmatched == {}
    assert result.is_complete is True


def test_split_result_repr(base_env):
    result = split_env(base_env, {"db": r"^DB_"})
    r = repr(result)
    assert "SplitResult" in r
    assert "partitions=" in r


def test_merge_partitions_reconstructs_full_env(base_env):
    result = split_env(
        base_env,
        {"db": r"^DB_", "aws": r"^AWS_", "app": r"^APP_", "log": r"^LOG_"},
    )
    merged = merge_partitions(result)
    assert merged == base_env


def test_merge_partitions_includes_unmatched(base_env):
    result = split_env(base_env, {"db": r"^DB_"})
    merged = merge_partitions(result)
    assert merged == base_env


def test_rules_applied_lists_matched_partition_names(base_env):
    result = split_env(
        base_env,
        {"db": r"^DB_", "noop": r"^ZZZNOMATCH_"},
    )
    assert "db" in result.rules_applied
    assert "noop" not in result.rules_applied
