import pytest
from envoy_cfg.coerce import coerce_env, CoerceResult


@pytest.fixture
def base_env():
    return {
        "DEBUG": "True",
        "ENABLED": "YES",
        "VERBOSE": "  1  ",
        "RETRIES": "  3",
        "NAME": "alice",
        "ACTIVE": "OFF",
        "FLAG": "false",
    }


def test_coerce_returns_coerce_result(base_env):
    result = coerce_env(base_env)
    assert isinstance(result, CoerceResult)


def test_coerce_normalises_true_variants(base_env):
    result = coerce_env(base_env)
    assert result.env["DEBUG"] == "true"
    assert result.env["ENABLED"] == "true"


def test_coerce_normalises_false_variants(base_env):
    result = coerce_env(base_env)
    assert result.env["ACTIVE"] == "false"
    assert result.env["FLAG"] == "false"


def test_coerce_strips_whitespace(base_env):
    result = coerce_env(base_env)
    assert result.env["RETRIES"] == "3"
    assert result.env["VERBOSE"] == "true"  # stripped then bool-matched


def test_coerce_unchanged_plain_value(base_env):
    result = coerce_env(base_env)
    assert result.env["NAME"] == "alice"


def test_coerce_is_clean_when_no_changes():
    env = {"NAME": "alice", "HOST": "localhost"}
    result = coerce_env(env)
    assert result.is_clean()


def test_coerce_not_clean_when_changes(base_env):
    result = coerce_env(base_env)
    assert not result.is_clean()


def test_coerce_coerced_list_contains_changed_keys(base_env):
    result = coerce_env(base_env)
    changed_keys = {entry[0] for entry in result.coerced}
    assert "DEBUG" in changed_keys
    assert "NAME" not in changed_keys


def test_coerce_bool_disabled_leaves_true_variants():
    env = {"FLAG": "True", "OTHER": "YES"}
    result = coerce_env(env, booleans=False, strip_whitespace=False)
    assert result.env["FLAG"] == "True"
    assert result.env["OTHER"] == "YES"
    assert result.is_clean()


def test_coerce_strip_only_no_bool():
    env = {"KEY": "  hello  ", "FLAG": "True"}
    result = coerce_env(env, booleans=False, strip_whitespace=True)
    assert result.env["KEY"] == "hello"
    assert result.env["FLAG"] == "True"
    assert result.strategy == "coerce:strip"


def test_coerce_targeted_keys_only():
    env = {"A": "True", "B": "True"}
    result = coerce_env(env, keys=["A"])
    assert result.env["A"] == "true"
    assert result.env["B"] == "True"


def test_coerce_repr(base_env):
    result = coerce_env(base_env)
    r = repr(result)
    assert "CoerceResult" in r
    assert "coerced=" in r


def test_coerce_strategy_label_both():
    result = coerce_env({"X": "True"})
    assert result.strategy == "coerce:bool+strip"


def test_coerce_strategy_label_bool_only():
    result = coerce_env({"X": "True"}, strip_whitespace=False)
    assert result.strategy == "coerce:bool"
