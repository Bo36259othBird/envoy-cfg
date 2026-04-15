"""Tests for envoy_cfg.normalize."""

import pytest
from envoy_cfg.normalize import (
    NormalizeResult,
    normalize_keys,
    normalize_values,
)


@pytest.fixture
def base_env():
    return {
        "app_name": "myapp",
        "  DB_HOST  ": "localhost",
        "api_key": "secret",
        "PORT": "8080",
    }


# --- normalize_keys ---

def test_normalize_keys_uppercases_all(base_env):
    result = normalize_keys(base_env)
    assert "APP_NAME" in result.normalized
    assert "API_KEY" in result.normalized


def test_normalize_keys_strips_whitespace(base_env):
    result = normalize_keys(base_env)
    assert "DB_HOST" in result.normalized
    assert "  DB_HOST  " not in result.normalized


def test_normalize_keys_preserves_values(base_env):
    result = normalize_keys(base_env)
    assert result.normalized["APP_NAME"] == "myapp"
    assert result.normalized["DB_HOST"] == "localhost"


def test_normalize_keys_records_changes(base_env):
    result = normalize_keys(base_env)
    changed_keys = {old for old, _, _ in result.changes}
    assert "app_name" in changed_keys
    assert "  DB_HOST  " in changed_keys


def test_normalize_keys_already_uppercase_not_in_changes():
    env = {"PORT": "8080", "HOST": "localhost"}
    result = normalize_keys(env)
    assert result.is_clean()


def test_normalize_keys_no_uppercase_option():
    env = {"app_name": "myapp"}
    result = normalize_keys(env, uppercase=False, strip_whitespace=False)
    assert "app_name" in result.normalized
    assert result.is_clean()


def test_normalize_keys_label_default():
    result = normalize_keys({})
    assert result.label == "normalize_keys"


def test_normalize_keys_custom_label():
    result = normalize_keys({}, label="my_step")
    assert result.label == "my_step"


def test_normalize_keys_repr_contains_info():
    env = {"a": "1", "b": "2"}
    result = normalize_keys(env)
    r = repr(result)
    assert "NormalizeResult" in r
    assert "keys=" in r


# --- normalize_values ---

def test_normalize_values_strips_whitespace():
    env = {"KEY": "  hello  "}
    result = normalize_values(env)
    assert result.normalized["KEY"] == "hello"


def test_normalize_values_collapses_newlines():
    env = {"MSG": "line1\nline2"}
    result = normalize_values(env)
    assert "\n" not in result.normalized["MSG"]
    assert result.normalized["MSG"] == "line1 line2"


def test_normalize_values_strips_carriage_return():
    env = {"MSG": "hello\r\nworld"}
    result = normalize_values(env)
    assert "\r" not in result.normalized["MSG"]


def test_normalize_values_clean_when_no_changes():
    env = {"KEY": "value", "PORT": "8080"}
    result = normalize_values(env)
    assert result.is_clean()


def test_normalize_values_records_changes():
    env = {"KEY": "  spaced  "}
    result = normalize_values(env)
    assert len(result.changes) == 1
    key, old, new = result.changes[0]
    assert key == "KEY"
    assert old == "  spaced  "
    assert new == "spaced"


def test_normalize_values_original_preserved():
    env = {"KEY": "  hello  "}
    result = normalize_values(env)
    assert result.original["KEY"] == "  hello  "


def test_normalize_values_no_strip_option():
    env = {"KEY": "  hello  "}
    result = normalize_values(env, strip_whitespace=False, collapse_newlines=False)
    assert result.normalized["KEY"] == "  hello  "
    assert result.is_clean()
