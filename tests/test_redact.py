"""Tests for envoy_cfg.redact."""

import pytest

from envoy_cfg.redact import (
    REDACTED_PLACEHOLDER,
    RedactResult,
    redact_env,
    redact_value,
)


# ---------------------------------------------------------------------------
# redact_env
# ---------------------------------------------------------------------------

def test_redact_env_masks_secret_keys():
    env = {"API_KEY": "abc123", "HOST": "localhost"}
    result = redact_env(env)
    assert result.env["API_KEY"] == REDACTED_PLACEHOLDER
    assert result.env["HOST"] == "localhost"


def test_redact_env_redacted_keys_sorted():
    env = {"SECRET_TOKEN": "x", "PASSWORD": "y", "PORT": "8080"}
    result = redact_env(env)
    assert result.redacted_keys == sorted(result.redacted_keys)


def test_redact_env_original_count():
    env = {"A": "1", "B": "2", "C": "3"}
    result = redact_env(env)
    assert result.original_count == 3


def test_redact_env_is_clean_when_no_secrets():
    env = {"HOST": "localhost", "PORT": "5432"}
    result = redact_env(env)
    assert result.is_clean is True
    assert result.redacted_keys == []


def test_redact_env_extra_keys_are_redacted():
    env = {"MY_CUSTOM": "sensitive", "NORMAL": "ok"}
    result = redact_env(env, extra_keys=["MY_CUSTOM"])
    assert result.env["MY_CUSTOM"] == REDACTED_PLACEHOLDER
    assert result.env["NORMAL"] == "ok"


def test_redact_env_extra_keys_case_insensitive():
    env = {"my_custom": "sensitive"}
    result = redact_env(env, extra_keys=["MY_CUSTOM"])
    assert result.env["my_custom"] == REDACTED_PLACEHOLDER


def test_redact_env_custom_placeholder():
    env = {"API_SECRET": "topsecret"}
    result = redact_env(env, placeholder="***")
    assert result.env["API_SECRET"] == "***"


def test_redact_env_empty_env():
    result = redact_env({})
    assert result.env == {}
    assert result.original_count == 0
    assert result.is_clean is True


def test_redact_result_repr():
    env = {"TOKEN": "abc"}
    result = redact_env(env)
    r = repr(result)
    assert "RedactResult" in r
    assert "TOKEN" in r


# ---------------------------------------------------------------------------
# redact_value
# ---------------------------------------------------------------------------

def test_redact_value_secret_key():
    assert redact_value("DB_PASSWORD", "hunter2") == REDACTED_PLACEHOLDER


def test_redact_value_non_secret_key():
    assert redact_value("APP_HOST", "example.com") == "example.com"


def test_redact_value_extra_key():
    assert redact_value("CUSTOM", "val", extra_keys=["CUSTOM"]) == REDACTED_PLACEHOLDER


def test_redact_value_custom_placeholder():
    assert redact_value("SECRET_KEY", "xyz", placeholder="<hidden>") == "<hidden>"
