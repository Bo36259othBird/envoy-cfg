"""Tests for envoy_cfg.omit."""

from __future__ import annotations

import pytest

from envoy_cfg.omit import OmitResult, omit_by_glob, omit_by_keys, omit_by_prefix


@pytest.fixture
def base_env() -> dict:
    return {
        "APP_NAME": "myapp",
        "APP_VERSION": "1.0",
        "DB_HOST": "localhost",
        "DB_PASSWORD": "secret",
        "DEBUG": "true",
    }


# --- omit_by_keys ---

def test_omit_by_keys_returns_result(base_env):
    result = omit_by_keys(base_env, ["DEBUG"])
    assert isinstance(result, OmitResult)


def test_omit_by_keys_removes_listed_key(base_env):
    result = omit_by_keys(base_env, ["DEBUG"])
    assert "DEBUG" not in result.env


def test_omit_by_keys_preserves_other_keys(base_env):
    result = omit_by_keys(base_env, ["DEBUG"])
    assert "APP_NAME" in result.env
    assert "DB_HOST" in result.env


def test_omit_by_keys_omitted_sorted(base_env):
    result = omit_by_keys(base_env, ["DB_PASSWORD", "APP_NAME"])
    assert result.omitted == ["APP_NAME", "DB_PASSWORD"]


def test_omit_by_keys_missing_key_not_in_omitted(base_env):
    result = omit_by_keys(base_env, ["NONEXISTENT"])
    assert "NONEXISTENT" not in result.omitted
    assert result.is_clean()


def test_omit_by_keys_strategy_label(base_env):
    result = omit_by_keys(base_env, ["DEBUG"])
    assert result.strategy == "keys"


def test_omit_by_keys_empty_list_is_clean(base_env):
    result = omit_by_keys(base_env, [])
    assert result.is_clean()
    assert result.env == base_env


# --- omit_by_prefix ---

def test_omit_by_prefix_removes_matching_keys(base_env):
    result = omit_by_prefix(base_env, "DB_")
    assert "DB_HOST" not in result.env
    assert "DB_PASSWORD" not in result.env


def test_omit_by_prefix_keeps_non_matching_keys(base_env):
    result = omit_by_prefix(base_env, "DB_")
    assert "APP_NAME" in result.env
    assert "DEBUG" in result.env


def test_omit_by_prefix_omitted_count(base_env):
    result = omit_by_prefix(base_env, "APP_")
    assert len(result.omitted) == 2


def test_omit_by_prefix_strategy_label(base_env):
    result = omit_by_prefix(base_env, "DB_")
    assert result.strategy == "prefix"


def test_omit_by_prefix_no_match_is_clean(base_env):
    result = omit_by_prefix(base_env, "XYZ_")
    assert result.is_clean()


# --- omit_by_glob ---

def test_omit_by_glob_removes_matching_keys(base_env):
    result = omit_by_glob(base_env, "DB_*")
    assert "DB_HOST" not in result.env
    assert "DB_PASSWORD" not in result.env


def test_omit_by_glob_keeps_non_matching_keys(base_env):
    result = omit_by_glob(base_env, "DB_*")
    assert "APP_NAME" in result.env


def test_omit_by_glob_strategy_label(base_env):
    result = omit_by_glob(base_env, "APP_*")
    assert result.strategy == "glob"


def test_omit_by_glob_exact_pattern(base_env):
    result = omit_by_glob(base_env, "DEBUG")
    assert "DEBUG" not in result.env
    assert len(result.omitted) == 1


def test_omit_by_glob_no_match_is_clean(base_env):
    result = omit_by_glob(base_env, "NOPE_*")
    assert result.is_clean()
