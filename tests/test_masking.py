"""Tests for envoy_cfg.masking module."""

import pytest

from envoy_cfg.masking import is_secret_key, mask_env, mask_value, MASK_PLACEHOLDER


# ---------------------------------------------------------------------------
# is_secret_key
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("key", [
    "PASSWORD", "DB_PASSWORD", "db_passwd",
    "API_KEY", "api_key", "MY_API_KEY",
    "SECRET", "APP_SECRET", "secret_value",
    "AUTH_TOKEN", "ACCESS_TOKEN",
    "PRIVATE_KEY",
    "CREDENTIALS",
    "CONNECTION_STRING", "CONN_STR",
])
def test_is_secret_key_detects_sensitive_keys(key: str):
    assert is_secret_key(key) is True


@pytest.mark.parametrize("key", [
    "HOST", "PORT", "DEBUG", "LOG_LEVEL",
    "DATABASE_URL",  # URL itself is not a secret pattern
    "APP_NAME", "REGION",
])
def test_is_secret_key_ignores_non_sensitive_keys(key: str):
    assert is_secret_key(key) is False


# ---------------------------------------------------------------------------
# mask_value
# ---------------------------------------------------------------------------

def test_mask_value_short_string():
    assert mask_value("abc") == MASK_PLACEHOLDER


def test_mask_value_empty_string():
    assert mask_value("") == MASK_PLACEHOLDER


def test_mask_value_long_string():
    result = mask_value("supersecret")
    assert result.startswith("su")
    assert "*" in result
    assert "supersecret" not in result


def test_mask_value_non_string():
    assert mask_value(None) == MASK_PLACEHOLDER  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# mask_env
# ---------------------------------------------------------------------------

SAMPLE_ENV = {
    "HOST": "localhost",
    "PORT": "5432",
    "DB_PASSWORD": "hunter2",
    "API_KEY": "sk-abcdef123456",
    "APP_NAME": "myapp",
}


def test_mask_env_masks_secrets():
    result = mask_env(SAMPLE_ENV)
    assert result["HOST"] == "localhost"
    assert result["PORT"] == "5432"
    assert result["APP_NAME"] == "myapp"
    assert result["DB_PASSWORD"] != "hunter2"
    assert result["API_KEY"] != "sk-abcdef123456"


def test_mask_env_reveal_returns_original():
    result = mask_env(SAMPLE_ENV, reveal=True)
    assert result == SAMPLE_ENV


def test_mask_env_does_not_mutate_original():
    env = {"DB_PASSWORD": "secret123"}
    mask_env(env)
    assert env["DB_PASSWORD"] == "secret123"
