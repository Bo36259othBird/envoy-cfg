"""Tests for envoy_cfg.cast module."""
import pytest
from envoy_cfg.cast import cast_env, CastResult, _cast_value


@pytest.fixture
def base_env():
    return {
        "PORT": "8080",
        "DEBUG": "true",
        "RATIO": "3.14",
        "NAME": "myapp",
        "ENABLED": "yes",
        "VERBOSE": "0",
    }


def test_cast_env_returns_cast_result(base_env):
    result = cast_env(base_env, {})
    assert isinstance(result, CastResult)


def test_cast_int_converts_string(base_env):
    result = cast_env(base_env, {"PORT": "int"})
    assert result.env["PORT"] == 8080
    assert isinstance(result.env["PORT"], int)


def test_cast_float_converts_string(base_env):
    result = cast_env(base_env, {"RATIO": "float"})
    assert result.env["RATIO"] == pytest.approx(3.14)


def test_cast_bool_true_values(base_env):
    for val, key in [("true", "DEBUG"), ("yes", "ENABLED")]:
        base_env[key] = val
    result = cast_env(base_env, {"DEBUG": "bool", "ENABLED": "bool"})
    assert result.env["DEBUG"] is True
    assert result.env["ENABLED"] is True


def test_cast_bool_false_values(base_env):
    base_env["VERBOSE"] = "0"
    result = cast_env(base_env, {"VERBOSE": "bool"})
    assert result.env["VERBOSE"] is False


def test_cast_str_passthrough(base_env):
    result = cast_env(base_env, {"NAME": "str"})
    assert result.env["NAME"] == "myapp"
    assert isinstance(result.env["NAME"], str)


def test_cast_missing_key_is_skipped(base_env):
    result = cast_env(base_env, {"MISSING": "int"})
    assert "MISSING" not in result.env
    assert result.is_clean


def test_cast_invalid_int_records_error(base_env):
    base_env["PORT"] = "notanumber"
    result = cast_env(base_env, {"PORT": "int"})
    assert "PORT" in result.errors
    assert not result.is_clean


def test_cast_invalid_bool_records_error(base_env):
    base_env["DEBUG"] = "maybe"
    result = cast_env(base_env, {"DEBUG": "bool"})
    assert "DEBUG" in result.errors


def test_cast_unknown_type_records_error(base_env):
    result = cast_env(base_env, {"PORT": "uuid"})
    assert "PORT" in result.errors


def test_cast_casted_dict_tracks_successful_keys(base_env):
    result = cast_env(base_env, {"PORT": "int", "RATIO": "float"})
    assert "PORT" in result.casted
    assert "RATIO" in result.casted
    assert result.casted["PORT"] == "int"


def test_cast_uncasted_keys_remain_strings(base_env):
    result = cast_env(base_env, {"PORT": "int"})
    assert isinstance(result.env["NAME"], str)


def test_cast_value_bool_case_insensitive():
    assert _cast_value("TRUE", "bool") is True
    assert _cast_value("FALSE", "bool") is False
    assert _cast_value("ON", "bool") is True
    assert _cast_value("OFF", "bool") is False


def test_cast_is_clean_when_no_errors(base_env):
    result = cast_env(base_env, {"PORT": "int"})
    assert result.is_clean


def test_cast_empty_schema_passthrough(base_env):
    result = cast_env(base_env, {})
    assert result.env == base_env
    assert result.casted == {}
    assert result.is_clean
