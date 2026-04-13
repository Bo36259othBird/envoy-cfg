"""Tests for envoy_cfg.validate module."""

import pytest
from envoy_cfg.validate import (
    validate_key,
    validate_value,
    validate_env,
    ValidationResult,
    ValidationError,
    MAX_KEY_LENGTH,
    MAX_VALUE_LENGTH,
)


# --- validate_key ---

def test_valid_key_simple():
    assert validate_key("MY_VAR") is None


def test_valid_key_with_digits():
    assert validate_key("VAR_1") is None


def test_valid_key_starts_with_underscore():
    assert validate_key("_PRIVATE") is None


def test_valid_key_lowercase():
    assert validate_key("my_var") is None


def test_invalid_key_empty():
    error = validate_key("")
    assert error is not None
    assert "empty" in error.lower()


def test_invalid_key_starts_with_digit():
    error = validate_key("1BAD_KEY")
    assert error is not None


def test_invalid_key_contains_hyphen():
    error = validate_key("BAD-KEY")
    assert error is not None


def test_invalid_key_contains_space():
    error = validate_key("BAD KEY")
    assert error is not None


def test_invalid_key_too_long():
    long_key = "A" * (MAX_KEY_LENGTH + 1)
    error = validate_key(long_key)
    assert error is not None
    assert "length" in error.lower()


def test_valid_key_at_max_length():
    key = "A" * MAX_KEY_LENGTH
    assert validate_key(key) is None


# --- validate_value ---

def test_valid_value():
    assert validate_value("MY_VAR", "some value") is None


def test_valid_value_empty_string():
    assert validate_value("MY_VAR", "") is None


def test_invalid_value_too_long():
    long_value = "x" * (MAX_VALUE_LENGTH + 1)
    error = validate_value("MY_VAR", long_value)
    assert error is not None
    assert "length" in error.lower()


# --- validate_env ---

def test_validate_env_all_valid():
    env = {"APP_NAME": "myapp", "PORT": "8080", "DEBUG": "false"}
    result = validate_env(env)
    assert result.is_valid
    assert result.errors == []


def test_validate_env_empty():
    result = validate_env({})
    assert result.is_valid


def test_validate_env_with_invalid_key():
    env = {"VALID_KEY": "ok", "bad-key": "value"}
    result = validate_env(env)
    assert not result.is_valid
    assert any(e.key == "bad-key" for e in result.errors)


def test_validate_env_with_value_too_long():
    env = {"MY_KEY": "x" * (MAX_VALUE_LENGTH + 1)}
    result = validate_env(env)
    assert not result.is_valid
    assert result.errors[0].key == "MY_KEY"


def test_validate_env_multiple_errors():
    env = {"1BAD": "ok", "ALSO-BAD": "ok", "GOOD": "fine"}
    result = validate_env(env)
    assert len(result.errors) == 2


def test_validation_result_repr():
    result = ValidationResult()
    assert "valid=True" in repr(result)
    result.add_error("KEY", "some error")
    assert "valid=False" in repr(result)
    assert "errors=1" in repr(result)


def test_validation_error_repr():
    err = ValidationError(key="MY_KEY", message="bad value")
    assert "MY_KEY" in repr(err)
    assert "bad value" in repr(err)
