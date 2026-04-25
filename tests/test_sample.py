"""Tests for envoy_cfg.sample."""
import pytest

from envoy_cfg.sample import (
    SampleResult,
    sample_by_count,
    sample_by_fraction,
    sample_by_keys,
)


@pytest.fixture
def base_env():
    return {
        "APP_HOST": "localhost",
        "APP_PORT": "8080",
        "DB_HOST": "db.local",
        "DB_PASSWORD": "secret",
        "API_KEY": "abc123",
        "LOG_LEVEL": "INFO",
    }


def test_sample_by_count_returns_sample_result(base_env):
    result = sample_by_count(base_env, 3, seed=42)
    assert isinstance(result, SampleResult)


def test_sample_by_count_correct_number_of_keys(base_env):
    result = sample_by_count(base_env, 3, seed=42)
    assert len(result.sampled) == 3


def test_sample_by_count_excluded_plus_sampled_equals_total(base_env):
    result = sample_by_count(base_env, 3, seed=42)
    assert len(result.sampled) + len(result.excluded) == len(base_env)


def test_sample_by_count_no_overlap(base_env):
    result = sample_by_count(base_env, 3, seed=7)
    assert set(result.sampled) & set(result.excluded) == set()


def test_sample_by_count_zero_returns_empty_sampled(base_env):
    result = sample_by_count(base_env, 0)
    assert result.sampled == {}
    assert len(result.excluded) == len(base_env)


def test_sample_by_count_exceeds_size_returns_all(base_env):
    result = sample_by_count(base_env, 100, seed=1)
    assert len(result.sampled) == len(base_env)
    assert result.excluded == {}


def test_sample_by_count_negative_raises(base_env):
    with pytest.raises(ValueError, match="count must be >= 0"):
        sample_by_count(base_env, -1)


def test_sample_by_count_strategy_label(base_env):
    result = sample_by_count(base_env, 2, seed=0)
    assert result.strategy == "count"


def test_sample_by_count_seed_is_recorded(base_env):
    result = sample_by_count(base_env, 2, seed=99)
    assert result.seed == 99


def test_sample_by_count_reproducible_with_same_seed(base_env):
    r1 = sample_by_count(base_env, 3, seed=42)
    r2 = sample_by_count(base_env, 3, seed=42)
    assert set(r1.sampled) == set(r2.sampled)


def test_sample_by_fraction_returns_correct_count(base_env):
    result = sample_by_fraction(base_env, 0.5, seed=1)
    assert len(result.sampled) == 3


def test_sample_by_fraction_strategy_label(base_env):
    result = sample_by_fraction(base_env, 0.5, seed=1)
    assert result.strategy == "fraction"


def test_sample_by_fraction_zero_returns_empty(base_env):
    result = sample_by_fraction(base_env, 0.0)
    assert result.sampled == {}


def test_sample_by_fraction_one_returns_all(base_env):
    result = sample_by_fraction(base_env, 1.0)
    assert len(result.sampled) == len(base_env)


def test_sample_by_fraction_invalid_raises(base_env):
    with pytest.raises(ValueError, match="fraction must be between"):
        sample_by_fraction(base_env, 1.5)


def test_sample_by_keys_returns_only_listed(base_env):
    result = sample_by_keys(base_env, ["APP_HOST", "LOG_LEVEL"])
    assert set(result.sampled) == {"APP_HOST", "LOG_LEVEL"}


def test_sample_by_keys_missing_key_not_in_sampled(base_env):
    result = sample_by_keys(base_env, ["APP_HOST", "DOES_NOT_EXIST"])
    assert "DOES_NOT_EXIST" not in result.sampled


def test_sample_by_keys_excluded_contains_rest(base_env):
    result = sample_by_keys(base_env, ["APP_HOST"])
    assert "DB_HOST" in result.excluded


def test_sample_by_keys_strategy_label(base_env):
    result = sample_by_keys(base_env, ["APP_PORT"])
    assert result.strategy == "keys"


def test_sample_by_keys_seed_is_none(base_env):
    result = sample_by_keys(base_env, ["APP_PORT"])
    assert result.seed is None


def test_sample_result_is_empty_when_no_sampled_keys(base_env):
    result = sample_by_count(base_env, 0)
    assert result.is_empty()


def test_sample_result_is_not_empty_when_keys_sampled(base_env):
    result = sample_by_count(base_env, 2, seed=1)
    assert not result.is_empty()
