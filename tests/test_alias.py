"""Tests for envoy_cfg.alias."""
import pytest

from envoy_cfg.alias import (
    AliasResult,
    apply_aliases,
    list_aliases,
    strip_aliases,
)


@pytest.fixture()
def base_env():
    return {
        "DATABASE_URL": "postgres://localhost/mydb",
        "API_KEY": "supersecret",
        "DEBUG": "true",
    }


@pytest.fixture()
def aliases():
    return {
        "DB": "DATABASE_URL",
        "KEY": "API_KEY",
    }


def test_apply_aliases_injects_alias_keys(base_env, aliases):
    result = apply_aliases(base_env, aliases)
    assert result.resolved["DB"] == base_env["DATABASE_URL"]
    assert result.resolved["KEY"] == base_env["API_KEY"]


def test_apply_aliases_applied_count(base_env, aliases):
    result = apply_aliases(base_env, aliases)
    assert result.applied_count == 2


def test_apply_aliases_preserves_original_keys(base_env, aliases):
    result = apply_aliases(base_env, aliases)
    for k in base_env:
        assert k in result.resolved


def test_apply_aliases_unresolved_when_source_missing(base_env):
    result = apply_aliases(base_env, {"GHOST": "MISSING_KEY"})
    assert "GHOST" in result.unresolved
    assert result.unresolved["GHOST"] == "MISSING_KEY"
    assert result.applied_count == 0


def test_apply_aliases_is_clean_when_all_resolved(base_env, aliases):
    result = apply_aliases(base_env, aliases)
    assert result.is_clean is True


def test_apply_aliases_not_clean_when_unresolved(base_env):
    result = apply_aliases(base_env, {"GHOST": "MISSING_KEY"})
    assert result.is_clean is False


def test_apply_aliases_no_overwrite_by_default(base_env, aliases):
    env_with_alias = {**base_env, "DB": "old_value"}
    result = apply_aliases(env_with_alias, aliases)
    assert result.resolved["DB"] == "old_value"


def test_apply_aliases_overwrite_flag_replaces_existing(base_env, aliases):
    env_with_alias = {**base_env, "DB": "old_value"}
    result = apply_aliases(env_with_alias, aliases, overwrite=True)
    assert result.resolved["DB"] == base_env["DATABASE_URL"]


def test_strip_aliases_removes_alias_keys(base_env, aliases):
    env_with = apply_aliases(base_env, aliases).resolved
    stripped = strip_aliases(env_with, aliases)
    assert "DB" not in stripped
    assert "KEY" not in stripped


def test_strip_aliases_keeps_non_alias_keys(base_env, aliases):
    env_with = apply_aliases(base_env, aliases).resolved
    stripped = strip_aliases(env_with, aliases)
    for k in base_env:
        assert k in stripped


def test_list_aliases_returns_values(base_env, aliases):
    listing = list_aliases(base_env, aliases)
    assert listing["DB"] == base_env["DATABASE_URL"]
    assert listing["KEY"] == base_env["API_KEY"]


def test_list_aliases_none_for_missing_source(base_env):
    listing = list_aliases(base_env, {"GHOST": "NO_SUCH_KEY"})
    assert listing["GHOST"] is None


def test_alias_result_repr_contains_count(base_env, aliases):
    result = apply_aliases(base_env, aliases)
    r = repr(result)
    assert "applied=2" in r
