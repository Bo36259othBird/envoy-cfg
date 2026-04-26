"""Tests for envoy_cfg.interpolate module."""

import pytest
from envoy_cfg.interpolate import interpolate_env, InterpolateResult


# ---------------------------------------------------------------------------
# interpolate_env — basic resolution
# ---------------------------------------------------------------------------

def test_no_references_passthrough():
    env = {"HOST": "localhost", "PORT": "5432"}
    result = interpolate_env(env)
    assert result.resolved == env
    assert result.is_clean


def test_simple_reference_resolved():
    env = {"BASE": "https://example.com", "URL": "${BASE}/api"}
    result = interpolate_env(env)
    assert result.resolved["URL"] == "https://example.com/api"
    assert result.is_clean


def test_chained_reference_resolved():
    env = {
        "SCHEME": "https",
        "HOST": "${SCHEME}://example.com",
        "URL": "${HOST}/v1",
    }
    result = interpolate_env(env)
    assert result.resolved["URL"] == "https://example.com/v1"
    assert result.is_clean


def test_multiple_refs_in_single_value():
    env = {"USER": "admin", "PASS": "secret", "DSN": "${USER}:${PASS}@db"}
    result = interpolate_env(env)
    assert result.resolved["DSN"] == "admin:secret@db"
    assert result.is_clean


# ---------------------------------------------------------------------------
# interpolate_env — overlay support
# ---------------------------------------------------------------------------

def test_overlay_provides_reference_source():
    env = {"URL": "${BASE}/path"}
    overlay = {"BASE": "https://cdn.example.com"}
    result = interpolate_env(env, overlay=overlay)
    assert result.resolved["URL"] == "https://cdn.example.com/path"
    assert result.is_clean


def test_overlay_key_not_included_in_resolved():
    env = {"URL": "${BASE}/path"}
    overlay = {"BASE": "https://cdn.example.com"}
    result = interpolate_env(env, overlay=overlay)
    assert "BASE" not in result.resolved


def test_overlay_overrides_env_reference_source():
    """Overlay values should take precedence over env values when resolving refs."""
    env = {"BASE": "https://origin.example.com", "URL": "${BASE}/path"}
    overlay = {"BASE": "https://cdn.example.com"}
    result = interpolate_env(env, overlay=overlay)
    assert result.resolved["URL"] == "https://cdn.example.com/path"
    assert result.is_clean


# ---------------------------------------------------------------------------
# interpolate_env — error handling
# ---------------------------------------------------------------------------

def test_unresolved_reference_recorded():
    env = {"URL": "${MISSING}/api"}
    result = interpolate_env(env)
    assert "URL" in result.unresolved_keys
    assert any("MISSING" in e for e in result.errors)
    assert not result.is_clean


def test_unresolved_value_kept_as_raw():
    env = {"URL": "${MISSING}/api"}
    result = interpolate_env(env)
    assert result.resolved["URL"] == "${MISSING}/api"


def test_circular_reference_detected():
    """A key that references itself (directly or indirectly) should be flagged."""
    env = {"A": "${B}", "B": "${A}"}
    result = interpolate_env(env)
    assert not result.is_clean
    assert "A" in result.unresolved_keys or "B" in result.unresolved_keys
    assert any("circular" in e.lower() or "A" in e or "B" in e for e in result.errors)


def test_self_referencing_key_detected():
    """A key that directly references itself should be treated as a circular reference."""
    env = {"FOO": "prefix_${FOO}"}
    result = interpolate_env(env)
    assert not result.is_clean
    assert "FOO" in result.unresolved_keys
