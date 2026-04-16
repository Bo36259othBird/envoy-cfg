"""Tests for envoy_cfg.freeze."""
from __future__ import annotations

import pytest

from envoy_cfg.freeze import (
    FreezeResult,
    check_frozen,
    freeze_env,
    unfreeze_env,
)


@pytest.fixture
def base_env() -> dict:
    return {
        "APP_HOST": "localhost",
        "APP_PORT": "8080",
        "DB_PASSWORD": "secret",
        "DEBUG": "true",
    }


def test_freeze_all_keys(base_env):
    result = freeze_env(base_env)
    assert set(result.frozen_keys) == set(base_env.keys())


def test_freeze_all_strategy_label(base_env):
    result = freeze_env(base_env)
    assert result.strategy == "all"


def test_freeze_selective_keys(base_env):
    result = freeze_env(base_env, keys=["APP_HOST", "DB_PASSWORD"])
    assert result.frozen_keys == ["APP_HOST", "DB_PASSWORD"]


def test_freeze_selective_strategy_label(base_env):
    result = freeze_env(base_env, keys=["APP_PORT"])
    assert result.strategy == "selective"


def test_freeze_ignores_missing_keys(base_env):
    result = freeze_env(base_env, keys=["APP_HOST", "NONEXISTENT"])
    assert "NONEXISTENT" not in result.frozen_keys
    assert "APP_HOST" in result.frozen_keys


def test_freeze_empty_env_returns_clean():
    result = freeze_env({})
    assert result.is_clean()
    assert result.frozen_keys == []


def test_freeze_is_fully_frozen(base_env):
    result = freeze_env(base_env)
    assert result.is_fully_frozen()


def test_freeze_selective_is_not_fully_frozen(base_env):
    result = freeze_env(base_env, keys=["APP_HOST"])
    assert not result.is_fully_frozen()


def test_freeze_result_repr(base_env):
    result = freeze_env(base_env)
    r = repr(result)
    assert "FreezeResult" in r
    assert "all" in r


def test_freeze_preserves_env_contents(base_env):
    result = freeze_env(base_env)
    assert result.env == base_env


def test_unfreeze_all_removes_all(base_env):
    freeze_result = freeze_env(base_env)
    unfreeze_result = unfreeze_env(base_env, frozen_keys=freeze_result.frozen_keys)
    assert unfreeze_result.frozen_keys == []


def test_unfreeze_partial_leaves_remainder(base_env):
    freeze_result = freeze_env(base_env)
    unfreeze_result = unfreeze_env(
        base_env,
        frozen_keys=freeze_result.frozen_keys,
        keys=["APP_HOST", "APP_PORT"],
    )
    assert "APP_HOST" not in unfreeze_result.frozen_keys
    assert "DB_PASSWORD" in unfreeze_result.frozen_keys


def test_unfreeze_strategy_full(base_env):
    freeze_result = freeze_env(base_env)
    result = unfreeze_env(base_env, frozen_keys=freeze_result.frozen_keys)
    assert result.strategy == "full-unfreeze"


def test_unfreeze_strategy_partial(base_env):
    freeze_result = freeze_env(base_env)
    result = unfreeze_env(base_env, frozen_keys=freeze_result.frozen_keys, keys=["APP_HOST"])
    assert result.strategy == "partial-unfreeze"


def test_check_frozen_true(base_env):
    freeze_result = freeze_env(base_env)
    assert check_frozen("APP_HOST", freeze_result.frozen_keys) is True


def test_check_frozen_false_after_unfreeze(base_env):
    freeze_result = freeze_env(base_env)
    unfreeze_result = unfreeze_env(base_env, frozen_keys=freeze_result.frozen_keys, keys=["APP_HOST"])
    assert check_frozen("APP_HOST", unfreeze_result.frozen_keys) is False


def test_freeze_frozen_keys_sorted(base_env):
    result = freeze_env(base_env, keys=["DEBUG", "APP_HOST", "APP_PORT"])
    assert result.frozen_keys == sorted(result.frozen_keys)
