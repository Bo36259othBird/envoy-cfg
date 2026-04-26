"""Tests for envoy_cfg.invert."""
import pytest

from envoy_cfg.invert import InvertResult, invert_booleans, invert_numerics


@pytest.fixture
def base_env():
    return {
        "FEATURE_FLAG": "true",
        "DEBUG": "false",
        "VERBOSE": "yes",
        "STRICT": "no",
        "ENABLED": "1",
        "DISABLED": "0",
        "TIMEOUT": "30",
        "RATIO": "0.5",
        "NEGATIVE": "-10",
        "NAME": "alice",
    }


# ---------------------------------------------------------------------------
# invert_booleans
# ---------------------------------------------------------------------------

def test_invert_booleans_returns_invert_result(base_env):
    result = invert_booleans(base_env)
    assert isinstance(result, InvertResult)


def test_invert_booleans_strategy_label(base_env):
    result = invert_booleans(base_env)
    assert result.strategy == "boolean"


def test_invert_booleans_true_becomes_false(base_env):
    result = invert_booleans(base_env, keys=["FEATURE_FLAG"])
    assert result.env["FEATURE_FLAG"] == "false"


def test_invert_booleans_false_becomes_true(base_env):
    result = invert_booleans(base_env, keys=["DEBUG"])
    assert result.env["DEBUG"] == "true"


def test_invert_booleans_yes_becomes_false(base_env):
    result = invert_booleans(base_env, keys=["VERBOSE"])
    assert result.env["VERBOSE"] == "false"


def test_invert_booleans_no_becomes_true(base_env):
    result = invert_booleans(base_env, keys=["STRICT"])
    assert result.env["STRICT"] == "true"


def test_invert_booleans_one_becomes_false(base_env):
    result = invert_booleans(base_env, keys=["ENABLED"])
    assert result.env["ENABLED"] == "false"


def test_invert_booleans_zero_becomes_true(base_env):
    result = invert_booleans(base_env, keys=["DISABLED"])
    assert result.env["DISABLED"] == "true"


def test_invert_booleans_non_boolean_skipped(base_env):
    result = invert_booleans(base_env, keys=["NAME"])
    assert "NAME" in result.skipped
    assert result.env["NAME"] == "alice"


def test_invert_booleans_missing_key_skipped(base_env):
    result = invert_booleans(base_env, keys=["MISSING_KEY"])
    assert "MISSING_KEY" in result.skipped


def test_invert_booleans_inverted_list_sorted(base_env):
    result = invert_booleans(base_env, keys=["DEBUG", "FEATURE_FLAG"])
    assert result.inverted == sorted(result.inverted)


def test_invert_booleans_is_clean_when_all_inverted(base_env):
    result = invert_booleans(base_env, keys=["FEATURE_FLAG", "DEBUG"])
    assert result.is_clean()


def test_invert_booleans_not_clean_when_skipped(base_env):
    result = invert_booleans(base_env, keys=["NAME"])
    assert not result.is_clean()


def test_invert_booleans_all_keys_when_none_specified(base_env):
    result = invert_booleans(base_env)
    # Non-boolean keys (TIMEOUT, RATIO, NEGATIVE, NAME) should be skipped
    assert len(result.skipped) > 0
    assert len(result.inverted) > 0


# ---------------------------------------------------------------------------
# invert_numerics
# ---------------------------------------------------------------------------

def test_invert_numerics_returns_invert_result(base_env):
    result = invert_numerics(base_env)
    assert isinstance(result, InvertResult)


def test_invert_numerics_strategy_label(base_env):
    result = invert_numerics(base_env)
    assert result.strategy == "numeric"


def test_invert_numerics_positive_int_becomes_negative(base_env):
    result = invert_numerics(base_env, keys=["TIMEOUT"])
    assert result.env["TIMEOUT"] == "-30"


def test_invert_numerics_negative_becomes_positive(base_env):
    result = invert_numerics(base_env, keys=["NEGATIVE"])
    assert result.env["NEGATIVE"] == "10"


def test_invert_numerics_float_value(base_env):
    result = invert_numerics(base_env, keys=["RATIO"])
    assert result.env["RATIO"] == "-0.5"


def test_invert_numerics_non_numeric_skipped(base_env):
    result = invert_numerics(base_env, keys=["NAME"])
    assert "NAME" in result.skipped
    assert result.env["NAME"] == "alice"


def test_invert_numerics_missing_key_skipped(base_env):
    result = invert_numerics(base_env, keys=["GHOST"])
    assert "GHOST" in result.skipped


def test_invert_numerics_is_clean_when_all_inverted(base_env):
    result = invert_numerics(base_env, keys=["TIMEOUT", "NEGATIVE"])
    assert result.is_clean()


def test_invert_numerics_zero_stays_zero():
    env = {"ZERO": "0"}
    result = invert_numerics(env, keys=["ZERO"])
    assert result.env["ZERO"] == "0"
