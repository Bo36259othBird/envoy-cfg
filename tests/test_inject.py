"""tests/test_inject.py — Tests for envoy_cfg.inject."""
from __future__ import annotations

import pytest

from envoy_cfg.inject import inject_env, InjectResult


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def env():
    return {
        "APP_HOST": "localhost",
        "APP_PORT": "8080",
        "DB_PASSWORD": "s3cr3t",
    }


# ---------------------------------------------------------------------------
# inject_env
# ---------------------------------------------------------------------------

def test_inject_no_placeholders(env):
    result = inject_env("Hello, world!", env)
    assert result.output == "Hello, world!"
    assert result.resolved == []
    assert result.missing == []
    assert result.is_clean is True


def test_inject_single_placeholder(env):
    result = inject_env("Host: ${APP_HOST}", env)
    assert result.output == "Host: localhost"
    assert "APP_HOST" in result.resolved
    assert result.is_clean is True


def test_inject_multiple_placeholders(env):
    result = inject_env("${APP_HOST}:${APP_PORT}", env)
    assert result.output == "localhost:8080"
    assert set(result.resolved) == {"APP_HOST", "APP_PORT"}


def test_inject_missing_placeholder_kept_by_default(env):
    result = inject_env("url=${MISSING_KEY}", env)
    assert result.output == "url=${MISSING_KEY}"
    assert "MISSING_KEY" in result.missing
    assert result.is_clean is False


def test_inject_missing_placeholder_with_default(env):
    result = inject_env("url=${MISSING_KEY}", env, default="")
    assert result.output == "url="
    assert "MISSING_KEY" in result.missing


def test_inject_strict_raises_on_missing(env):
    with pytest.raises(KeyError, match="MISSING_KEY"):
        inject_env("${MISSING_KEY}", env, strict=True)


def test_inject_strict_succeeds_when_all_resolved(env):
    result = inject_env("${APP_HOST}:${APP_PORT}", env, strict=True)
    assert result.is_clean is True
    assert result.output == "localhost:8080"


def test_inject_multiline_template(env):
    template = "HOST=${APP_HOST}\nPORT=${APP_PORT}\n"
    result = inject_env(template, env)
    assert result.output == "HOST=localhost\nPORT=8080\n"
    assert result.is_clean is True


def test_inject_repeated_placeholder(env):
    result = inject_env("${APP_HOST} and ${APP_HOST}", env)
    assert result.output == "localhost and localhost"
    # Both occurrences register as resolved
    assert result.resolved.count("APP_HOST") == 2


def test_inject_empty_env():
    result = inject_env("${KEY}", {})
    assert result.output == "${KEY}"
    assert result.missing == ["KEY"]


def test_inject_empty_template(env):
    result = inject_env("", env)
    assert result.output == ""
    assert result.resolved == []
    assert result.missing == []


def test_inject_result_repr(env):
    result = inject_env("${APP_HOST}:${MISSING}", env)
    r = repr(result)
    assert "resolved=1" in r
    assert "missing=1" in r
