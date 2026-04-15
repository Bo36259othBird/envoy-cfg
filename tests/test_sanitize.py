"""Tests for envoy_cfg.sanitize."""

import pytest
from envoy_cfg.sanitize import sanitize_env, SanitizeResult, _sanitize_key, _sanitize_value


@pytest.fixture
def clean_env():
    return {
        "APP_NAME": "myapp",
        "PORT": "8080",
        "DEBUG": "false",
    }


def test_sanitize_clean_env_is_unchanged(clean_env):
    result = sanitize_env(clean_env)
    assert result.sanitized == clean_env
    assert result.is_clean


def test_sanitize_result_repr():
    result = sanitize_env({"KEY": "val"})
    assert "SanitizeResult" in repr(result)
    assert "keys_stripped=0" in repr(result)
    assert "values_modified=0" in repr(result)


def test_sanitize_strips_null_bytes_from_value():
    env = {"KEY": "hel\x00lo"}
    result = sanitize_env(env)
    assert result.sanitized["KEY"] == "hello"
    assert "KEY" in result.modified_values


def test_sanitize_strips_newline_from_value():
    env = {"MSG": "line1\nline2"}
    result = sanitize_env(env)
    assert result.sanitized["MSG"] == "line1line2"
    assert "MSG" in result.modified_values


def test_sanitize_strips_carriage_return_from_value():
    env = {"MSG": "val\r"}
    result = sanitize_env(env)
    assert result.sanitized["MSG"] == "val"


def test_sanitize_strips_tab_from_value():
    env = {"MSG": "col1\tcol2"}
    result = sanitize_env(env)
    assert result.sanitized["MSG"] == "col1col2"


def test_sanitize_strips_whitespace_from_value_by_default():
    env = {"KEY": "  spaced  "}
    result = sanitize_env(env)
    assert result.sanitized["KEY"] == "spaced"
    assert "KEY" in result.modified_values


def test_sanitize_preserves_whitespace_when_disabled():
    env = {"KEY": "  spaced  "}
    result = sanitize_env(env, strip_whitespace=False)
    assert result.sanitized["KEY"] == "  spaced  "
    assert result.is_clean


def test_sanitize_drops_key_with_null_byte():
    env = {"BAD\x00KEY": "value", "GOOD": "ok"}
    result = sanitize_env(env)
    assert "BAD\x00KEY" not in result.sanitized
    assert "BAD\x00KEY" in result.stripped_keys
    assert "GOOD" in result.sanitized


def test_sanitize_drops_empty_key():
    env = {"": "value", "OK": "yes"}
    result = sanitize_env(env)
    assert "" not in result.sanitized
    assert "" in result.stripped_keys


def test_sanitize_drops_unsafe_named_keys():
    for bad_key in ["__proto__", "constructor", "prototype"]:
        env = {bad_key: "evil", "SAFE": "ok"}
        result = sanitize_env(env)
        assert bad_key not in result.sanitized
        assert bad_key in result.stripped_keys
        assert "SAFE" in result.sanitized


def test_sanitize_original_preserved_in_result():
    env = {"KEY": "val\n"}
    result = sanitize_env(env)
    assert result.original == env
    assert result.sanitized["KEY"] == "val"


def test_sanitize_multiple_control_chars_in_value():
    env = {"KEY": "a\x00b\nc\rd"}
    result = sanitize_env(env)
    assert result.sanitized["KEY"] == "abcd"


def test_sanitize_key_whitespace_only_is_dropped():
    assert _sanitize_key("   ") is None


def test_sanitize_value_empty_string_unchanged():
    assert _sanitize_value("") == ""
