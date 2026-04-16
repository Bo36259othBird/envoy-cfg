"""Tests for envoy_cfg.truncate."""

import pytest
from envoy_cfg.truncate import truncate_env, TruncateResult


@pytest.fixture
def base_env():
    return {
        "SHORT": "hi",
        "MEDIUM": "hello world",
        "LONG": "a" * 80,
        "SECRET_KEY": "supersecretvalue1234567890",
    }


def test_truncate_returns_truncate_result(base_env):
    result = truncate_env(base_env, max_length=20)
    assert isinstance(result, TruncateResult)


def test_truncate_short_values_unchanged(base_env):
    result = truncate_env(base_env, max_length=20)
    assert result.env["SHORT"] == "hi"
    assert result.env["MEDIUM"] == "hello world"


def test_truncate_long_value_is_cut(base_env):
    result = truncate_env(base_env, max_length=20)
    assert len(result.env["LONG"]) == 20


def test_truncate_long_value_ends_with_suffix(base_env):
    result = truncate_env(base_env, max_length=20, suffix="...")
    assert result.env["LONG"].endswith("...")


def test_truncate_records_truncated_keys(base_env):
    result = truncate_env(base_env, max_length=20)
    assert "LONG" in result.truncated_keys
    assert "SECRET_KEY" in result.truncated_keys


def test_truncate_short_keys_not_in_truncated(base_env):
    result = truncate_env(base_env, max_length=20)
    assert "SHORT" not in result.truncated_keys
    assert "MEDIUM" not in result.truncated_keys


def test_truncate_is_clean_when_nothing_truncated(base_env):
    result = truncate_env(base_env, max_length=200)
    assert result.is_clean is True


def test_truncate_is_not_clean_when_values_truncated(base_env):
    result = truncate_env(base_env, max_length=10)
    assert result.is_clean is False


def test_truncate_truncated_keys_sorted(base_env):
    result = truncate_env(base_env, max_length=10)
    assert result.truncated_keys == sorted(result.truncated_keys)


def test_truncate_custom_suffix(base_env):
    result = truncate_env(base_env, max_length=15, suffix="~~")
    assert result.env["LONG"].endswith("~~")
    assert len(result.env["LONG"]) == 15


def test_truncate_keys_allowlist(base_env):
    result = truncate_env(base_env, max_length=10, keys=["LONG"])
    assert "LONG" in result.truncated_keys
    # SECRET_KEY is longer than 10 but not in allowlist
    assert "SECRET_KEY" not in result.truncated_keys
    assert result.env["SECRET_KEY"] == base_env["SECRET_KEY"]


def test_truncate_invalid_max_length_raises(base_env):
    with pytest.raises(ValueError, match="max_length must be at least 1"):
        truncate_env(base_env, max_length=0)


def test_truncate_suffix_too_long_raises(base_env):
    with pytest.raises(ValueError, match="suffix length must be less than max_length"):
        truncate_env(base_env, max_length=3, suffix="...")


def test_truncate_repr_includes_counts(base_env):
    result = truncate_env(base_env, max_length=20)
    r = repr(result)
    assert "TruncateResult" in r
    assert "max_length=20" in r


def test_truncate_empty_env():
    result = truncate_env({}, max_length=10)
    assert result.env == {}
    assert result.is_clean is True
    assert result.truncated_keys == []
