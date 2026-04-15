"""Tests for envoy_cfg.rename."""
import pytest
from envoy_cfg.rename import rename_keys, RenameResult


@pytest.fixture
def base_env():
    return {
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "APP_SECRET": "s3cr3t",
        "LOG_LEVEL": "info",
    }


def test_rename_single_key(base_env):
    result = rename_keys(base_env, {"DB_HOST": "DATABASE_HOST"})
    assert "DATABASE_HOST" in result.env
    assert "DB_HOST" not in result.env
    assert result.env["DATABASE_HOST"] == "localhost"


def test_rename_preserves_value(base_env):
    result = rename_keys(base_env, {"APP_SECRET": "APP_KEY"})
    assert result.env["APP_KEY"] == "s3cr3t"


def test_rename_multiple_keys(base_env):
    mapping = {"DB_HOST": "DATABASE_HOST", "DB_PORT": "DATABASE_PORT"}
    result = rename_keys(base_env, mapping)
    assert "DATABASE_HOST" in result.env
    assert "DATABASE_PORT" in result.env
    assert "DB_HOST" not in result.env
    assert "DB_PORT" not in result.env
    assert len(result.renamed) == 2


def test_rename_missing_key_is_skipped(base_env):
    result = rename_keys(base_env, {"MISSING_KEY": "NEW_KEY"})
    assert "MISSING_KEY" not in result.env
    assert "NEW_KEY" not in result.env
    assert "MISSING_KEY" in result.skipped
    assert len(result.renamed) == 0


def test_rename_is_clean_when_no_skips(base_env):
    result = rename_keys(base_env, {"DB_HOST": "DATABASE_HOST"})
    assert result.is_clean is True


def test_rename_is_not_clean_when_skipped(base_env):
    result = rename_keys(base_env, {"GHOST": "PHANTOM"})
    assert result.is_clean is False


def test_rename_no_overwrite_skips_existing_dest(base_env):
    env = dict(base_env)
    env["DATABASE_HOST"] = "existing"
    result = rename_keys(env, {"DB_HOST": "DATABASE_HOST"}, overwrite=False)
    assert result.env["DATABASE_HOST"] == "existing"
    assert "DB_HOST" in result.env  # not removed
    assert "DB_HOST" in result.skipped


def test_rename_overwrite_replaces_existing_dest(base_env):
    env = dict(base_env)
    env["DATABASE_HOST"] = "old_value"
    result = rename_keys(env, {"DB_HOST": "DATABASE_HOST"}, overwrite=True)
    assert result.env["DATABASE_HOST"] == "localhost"
    assert "DB_HOST" not in result.env


def test_rename_does_not_mutate_original(base_env):
    original_copy = dict(base_env)
    rename_keys(base_env, {"DB_HOST": "DATABASE_HOST"})
    assert base_env == original_copy


def test_rename_empty_mapping_returns_unchanged(base_env):
    result = rename_keys(base_env, {})
    assert result.env == base_env
    assert result.renamed == []
    assert result.skipped == []


def test_rename_result_repr(base_env):
    result = rename_keys(base_env, {"DB_HOST": "DATABASE_HOST"})
    r = repr(result)
    assert "RenameResult" in r
    assert "renamed=1" in r


def test_rename_result_is_rename_result_instance(base_env):
    result = rename_keys(base_env, {"LOG_LEVEL": "LOG"})
    assert isinstance(result, RenameResult)
