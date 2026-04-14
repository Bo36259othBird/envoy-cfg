"""Tests for envoy_cfg.flatten."""

import pytest
from envoy_cfg.flatten import flatten_env, unflatten_env, FlattenResult


@pytest.fixture
def base_env():
    return {
        "APP__DB__HOST": "localhost",
        "APP__DB__PORT": "5432",
        "APP__SECRET_KEY": "abc123",
        "LOG_LEVEL": "debug",
    }


def test_flatten_returns_flatten_result(base_env):
    result = flatten_env(base_env)
    assert isinstance(result, FlattenResult)


def test_flatten_splits_on_double_underscore(base_env):
    result = flatten_env(base_env)
    assert "app.db.host" in result.flattened
    assert "app.db.port" in result.flattened


def test_flatten_passthrough_for_no_delimiter(base_env):
    result = flatten_env(base_env)
    assert "log_level" in result.flattened


def test_flatten_preserves_values(base_env):
    result = flatten_env(base_env)
    assert result.flattened["app.db.host"] == "localhost"
    assert result.flattened["app.db.port"] == "5432"


def test_flatten_original_count(base_env):
    result = flatten_env(base_env)
    assert result.original_count == 4


def test_flatten_flat_count(base_env):
    result = flatten_env(base_env)
    assert result.flat_count == 4


def test_flatten_is_expanded_when_same_count(base_env):
    result = flatten_env(base_env)
    assert not result.is_expanded


def test_flatten_custom_delimiter():
    env = {"APP_DB_HOST": "localhost", "APP_DB_PORT": "5432"}
    result = flatten_env(env, delimiter="_")
    assert "app.db.host" in result.flattened
    assert result.delimiter == "_"


def test_flatten_empty_delimiter_raises():
    with pytest.raises(ValueError, match="delimiter"):
        flatten_env({"KEY": "val"}, delimiter="")


def test_flatten_with_prefix_filters_keys(base_env):
    result = flatten_env(base_env, prefix="APP__DB")
    assert all(k.startswith("app.db") for k in result.flattened)
    assert "log_level" not in result.flattened


def test_flatten_repr_contains_info(base_env):
    result = flatten_env(base_env)
    r = repr(result)
    assert "FlattenResult" in r
    assert "delimiter" in r


def test_unflatten_restores_uppercase_keys():
    flat = {"app.db.host": "localhost", "app.db.port": "5432"}
    result = unflatten_env(flat)
    assert "APP__DB__HOST" in result
    assert "APP__DB__PORT" in result


def test_unflatten_preserves_values():
    flat = {"app.secret_key": "abc123"}
    result = unflatten_env(flat)
    assert result["APP__SECRET_KEY"] == "abc123"


def test_unflatten_empty_delimiter_raises():
    with pytest.raises(ValueError, match="delimiter"):
        unflatten_env({"key": "val"}, delimiter="")


def test_flatten_unflatten_roundtrip():
    env = {"APP__DB__HOST": "localhost", "LOG__LEVEL": "info"}
    flat = flatten_env(env).flattened
    restored = unflatten_env(flat)
    assert restored == env
