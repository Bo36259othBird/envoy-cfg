"""Tests for envoy_cfg.mask_diff."""
import pytest
from envoy_cfg.mask_diff import mask_diff, MaskDiffResult, MaskDiffEntry


@pytest.fixture
def base_env():
    return {
        "APP_HOST": "localhost",
        "DB_PASSWORD": "secret123",
        "APP_PORT": "8080",
        "API_KEY": "key-abc",
    }


@pytest.fixture
def updated_env():
    return {
        "APP_HOST": "prod.example.com",
        "DB_PASSWORD": "newsecret",
        "APP_DEBUG": "false",
        "API_KEY": "key-abc",
    }


def test_mask_diff_returns_result(base_env, updated_env):
    result = mask_diff(base_env, updated_env)
    assert isinstance(result, MaskDiffResult)


def test_mask_diff_total_equals_union_of_keys(base_env, updated_env):
    result = mask_diff(base_env, updated_env)
    expected = len(set(base_env) | set(updated_env))
    assert result.total == expected


def test_mask_diff_detects_added_key(base_env, updated_env):
    result = mask_diff(base_env, updated_env)
    added = [e for e in result.entries if e.change_type == "added"]
    keys = [e.key for e in added]
    assert "APP_DEBUG" in keys


def test_mask_diff_detects_removed_key(base_env, updated_env):
    result = mask_diff(base_env, updated_env)
    removed = [e for e in result.entries if e.change_type == "removed"]
    keys = [e.key for e in removed]
    assert "APP_PORT" in keys


def test_mask_diff_detects_modified_key(base_env, updated_env):
    result = mask_diff(base_env, updated_env)
    modified = [e for e in result.entries if e.change_type == "modified"]
    keys = [e.key for e in modified]
    assert "APP_HOST" in keys


def test_mask_diff_masks_secret_key(base_env, updated_env):
    result = mask_diff(base_env, updated_env)
    password_entry = next(e for e in result.entries if e.key == "DB_PASSWORD")
    assert password_entry.masked is True
    assert password_entry.new_value != "newsecret"
    assert password_entry.old_value != "secret123"


def test_mask_diff_masks_api_key(base_env, updated_env):
    result = mask_diff(base_env, updated_env)
    api_entry = next(e for e in result.entries if e.key == "API_KEY")
    assert api_entry.masked is True


def test_mask_diff_does_not_mask_plain_key(base_env, updated_env):
    result = mask_diff(base_env, updated_env)
    host_entry = next(e for e in result.entries if e.key == "APP_HOST")
    assert host_entry.masked is False
    assert host_entry.new_value == "prod.example.com"


def test_mask_diff_no_mask_flag_exposes_secrets(base_env, updated_env):
    result = mask_diff(base_env, updated_env, mask_secrets=False)
    password_entry = next(e for e in result.entries if e.key == "DB_PASSWORD")
    assert password_entry.masked is False
    assert password_entry.new_value == "newsecret"


def test_mask_diff_is_clean_for_identical_envs(base_env):
    result = mask_diff(base_env, base_env)
    assert result.is_clean is True


def test_mask_diff_changed_entries_excludes_unchanged(base_env, updated_env):
    result = mask_diff(base_env, updated_env)
    for e in result.changed_entries:
        assert e.change_type != "unchanged"


def test_mask_diff_masked_count_reflects_secret_changes(base_env, updated_env):
    result = mask_diff(base_env, updated_env)
    assert result.masked_count >= 1


def test_mask_diff_repr(base_env, updated_env):
    result = mask_diff(base_env, updated_env)
    r = repr(result)
    assert "MaskDiffResult" in r
    assert "total=" in r


def test_mask_diff_entry_repr():
    e = MaskDiffEntry("MY_SECRET", "modified", "***", "***", True)
    r = repr(e)
    assert "MaskDiffEntry" in r
    assert "[MASKED]" in r


def test_mask_diff_entry_to_dict():
    e = MaskDiffEntry("HOST", "added", None, "localhost", False)
    d = e.to_dict()
    assert d["key"] == "HOST"
    assert d["change_type"] == "added"
    assert d["masked"] is False
