"""Tests for envoy_cfg.group module."""

import pytest
from envoy_cfg.group import (
    GroupResult,
    group_by_prefix,
    group_by_suffix,
    group_by_pattern,
)


@pytest.fixture
def base_env():
    return {
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "CACHE_HOST": "redis",
        "CACHE_TTL": "300",
        "APP_NAME": "myapp",
        "LOG_LEVEL": "INFO",
        "SECRET_KEY": "abc123",
    }


def test_group_by_prefix_creates_groups(base_env):
    result = group_by_prefix(base_env, prefixes=["DB", "CACHE"])
    assert "DB" in result.groups
    assert "CACHE" in result.groups
    assert "DB_HOST" in result.groups["DB"]
    assert "CACHE_HOST" in result.groups["CACHE"]


def test_group_by_prefix_ungrouped_keys(base_env):
    result = group_by_prefix(base_env, prefixes=["DB", "CACHE"])
    assert "APP_NAME" in result.ungrouped
    assert "LOG_LEVEL" in result.ungrouped


def test_group_by_prefix_strip_removes_prefix(base_env):
    result = group_by_prefix(base_env, prefixes=["DB"], strip_prefix=True)
    assert "HOST" in result.groups["DB"]
    assert "PORT" in result.groups["DB"]
    assert "DB_HOST" not in result.groups["DB"]


def test_group_by_prefix_custom_separator():
    env = {"DB.HOST": "localhost", "DB.PORT": "5432", "OTHER": "val"}
    result = group_by_prefix(env, prefixes=["DB"], separator=".")
    assert "DB.HOST" in result.groups["DB"]
    assert "OTHER" in result.ungrouped


def test_group_by_prefix_is_complete_when_all_grouped():
    env = {"DB_HOST": "localhost", "DB_PORT": "5432"}
    result = group_by_prefix(env, prefixes=["DB"])
    assert result.is_complete()


def test_group_by_prefix_not_complete_with_ungrouped(base_env):
    result = group_by_prefix(base_env, prefixes=["DB"])
    assert not result.is_complete()


def test_group_by_suffix_creates_groups():
    env = {"HOST_PROD": "prod.host", "HOST_STAGING": "staging.host", "LOG_LEVEL": "INFO"}
    result = group_by_suffix(env, suffixes=["PROD", "STAGING"])
    assert "HOST_PROD" in result.groups["PROD"]
    assert "HOST_STAGING" in result.groups["STAGING"]
    assert "LOG_LEVEL" in result.ungrouped


def test_group_by_suffix_strip_removes_suffix():
    env = {"HOST_PROD": "prod.host", "PORT_PROD": "443"}
    result = group_by_suffix(env, suffixes=["PROD"], strip_suffix=True)
    assert "HOST" in result.groups["PROD"]
    assert "PORT" in result.groups["PROD"]


def test_group_by_pattern_creates_groups():
    env = {"DB_HOST": "localhost", "CACHE_HOST": "redis", "APP_LOG": "info"}
    result = group_by_pattern(env, patterns={"database": r"^DB_", "cache": r"^CACHE_"})
    assert "DB_HOST" in result.groups["database"]
    assert "CACHE_HOST" in result.groups["cache"]
    assert "APP_LOG" in result.ungrouped


def test_group_by_pattern_strategy_label():
    env = {"KEY": "val"}
    result = group_by_pattern(env, patterns={"g": r"KEY"})
    assert result.strategy == "pattern"


def test_group_result_repr(base_env):
    result = group_by_prefix(base_env, prefixes=["DB", "CACHE"])
    r = repr(result)
    assert "GroupResult" in r
    assert "prefix" in r


def test_group_result_all_keys(base_env):
    result = group_by_prefix(base_env, prefixes=["DB", "CACHE"])
    all_k = result.all_keys()
    assert len(all_k) == len(base_env)


def test_group_empty_env():
    result = group_by_prefix({}, prefixes=["DB"])
    assert result.groups["DB"] == {}
    assert result.ungrouped == {}
    assert result.is_complete()
