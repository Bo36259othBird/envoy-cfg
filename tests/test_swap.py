"""Tests for envoy_cfg.swap."""
import pytest

from envoy_cfg.swap import SwapResult, swap_keys, swap_pairs


@pytest.fixture()
def base_env() -> dict:
    return {
        "APP_HOST": "localhost",
        "APP_PORT": "8080",
        "DB_HOST": "db.internal",
        "DB_PORT": "5432",
        "DEBUG": "true",
    }


# ---------------------------------------------------------------------------
# swap_keys
# ---------------------------------------------------------------------------

def test_swap_keys_returns_swap_result(base_env):
    result = swap_keys(base_env, "APP_HOST", "DB_HOST")
    assert isinstance(result, SwapResult)


def test_swap_keys_exchanges_values(base_env):
    result = swap_keys(base_env, "APP_HOST", "DB_HOST")
    assert result.env["APP_HOST"] == "db.internal"
    assert result.env["DB_HOST"] == "localhost"


def test_swap_keys_other_keys_unchanged(base_env):
    result = swap_keys(base_env, "APP_HOST", "DB_HOST")
    assert result.env["APP_PORT"] == "8080"
    assert result.env["DEBUG"] == "true"


def test_swap_keys_strategy_label(base_env):
    result = swap_keys(base_env, "APP_HOST", "DB_HOST")
    assert result.strategy == "swap_keys"


def test_swap_keys_swapped_pairs_recorded(base_env):
    result = swap_keys(base_env, "APP_HOST", "DB_HOST")
    assert ("APP_HOST", "DB_HOST") in result.swapped_pairs


def test_swap_keys_is_clean_when_both_present(base_env):
    result = swap_keys(base_env, "APP_PORT", "DB_PORT")
    assert result.is_clean() is True


def test_swap_keys_missing_key_skipped(base_env):
    result = swap_keys(base_env, "APP_HOST", "NONEXISTENT")
    assert "NONEXISTENT" in result.skipped
    assert result.is_clean() is False


def test_swap_keys_missing_key_env_unchanged(base_env):
    result = swap_keys(base_env, "APP_HOST", "NONEXISTENT")
    assert result.env["APP_HOST"] == "localhost"


def test_swap_keys_both_missing_both_skipped(base_env):
    result = swap_keys(base_env, "FOO", "BAR")
    assert set(result.skipped) == {"FOO", "BAR"}
    assert result.swapped_pairs == []


def test_swap_keys_does_not_mutate_original(base_env):
    original = dict(base_env)
    swap_keys(base_env, "APP_HOST", "DB_HOST")
    assert base_env == original


# ---------------------------------------------------------------------------
# swap_pairs
# ---------------------------------------------------------------------------

def test_swap_pairs_returns_swap_result(base_env):
    result = swap_pairs(base_env, [("APP_HOST", "DB_HOST")])
    assert isinstance(result, SwapResult)


def test_swap_pairs_strategy_label(base_env):
    result = swap_pairs(base_env, [("APP_HOST", "DB_HOST")])
    assert result.strategy == "swap_pairs"


def test_swap_pairs_multiple_pairs(base_env):
    result = swap_pairs(
        base_env,
        [("APP_HOST", "DB_HOST"), ("APP_PORT", "DB_PORT")],
    )
    assert result.env["APP_HOST"] == "db.internal"
    assert result.env["DB_HOST"] == "localhost"
    assert result.env["APP_PORT"] == "5432"
    assert result.env["DB_PORT"] == "8080"


def test_swap_pairs_partial_skip_does_not_affect_valid_pairs(base_env):
    result = swap_pairs(
        base_env,
        [("APP_HOST", "MISSING"), ("APP_PORT", "DB_PORT")],
    )
    # valid pair swapped
    assert result.env["APP_PORT"] == "5432"
    assert result.env["DB_PORT"] == "8080"
    # invalid pair skipped
    assert "MISSING" in result.skipped


def test_swap_pairs_is_clean_all_present(base_env):
    result = swap_pairs(base_env, [("APP_HOST", "DB_HOST")])
    assert result.is_clean() is True


def test_swap_pairs_empty_pairs_list(base_env):
    result = swap_pairs(base_env, [])
    assert result.env == base_env
    assert result.swapped_pairs == []
    assert result.is_clean() is True
