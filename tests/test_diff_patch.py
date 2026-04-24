"""Tests for envoy_cfg.diff_patch."""
import pytest

from envoy_cfg.diff_patch import (
    DiffPatch,
    DiffPatchEntry,
    build_patch,
    apply_patch,
)


@pytest.fixture
def base_env():
    return {"APP_HOST": "localhost", "APP_PORT": "8080", "DB_PASS": "secret"}


@pytest.fixture
def updated_env():
    return {"APP_HOST": "prod.example.com", "APP_PORT": "8080", "NEW_KEY": "value"}


def test_build_patch_returns_diff_patch(base_env, updated_env):
    patch = build_patch(base_env, updated_env)
    assert isinstance(patch, DiffPatch)


def test_build_patch_detects_added_key(base_env, updated_env):
    patch = build_patch(base_env, updated_env)
    keys = {e.key for e in patch.entries}
    assert "NEW_KEY" in keys


def test_build_patch_detects_removed_key(base_env, updated_env):
    patch = build_patch(base_env, updated_env)
    removed = [e for e in patch.entries if e.change_type == "remove"]
    assert any(e.key == "DB_PASS" for e in removed)


def test_build_patch_detects_modified_key(base_env, updated_env):
    patch = build_patch(base_env, updated_env)
    modified = [e for e in patch.entries if e.change_type == "modify"]
    assert any(e.key == "APP_HOST" for e in modified)


def test_build_patch_unchanged_key_not_in_patch(base_env, updated_env):
    patch = build_patch(base_env, updated_env)
    keys = {e.key for e in patch.entries}
    assert "APP_PORT" not in keys


def test_build_patch_empty_when_identical():
    env = {"A": "1", "B": "2"}
    patch = build_patch(env, env)
    assert patch.is_empty


def test_patch_entry_to_dict_roundtrip():
    entry = DiffPatchEntry("MY_KEY", "modify", "old", "new")
    assert DiffPatchEntry.from_dict(entry.to_dict()) == entry


def test_diff_patch_to_dict_roundtrip(base_env, updated_env):
    patch = build_patch(base_env, updated_env)
    restored = DiffPatch.from_dict(patch.to_dict())
    assert len(restored.entries) == len(patch.entries)


def test_apply_patch_adds_key(base_env):
    patch = DiffPatch(entries=[DiffPatchEntry("NEW", "add", None, "hello")])
    result = apply_patch(base_env, patch)
    assert result["NEW"] == "hello"


def test_apply_patch_removes_key(base_env):
    patch = DiffPatch(entries=[DiffPatchEntry("APP_PORT", "remove", "8080", None)])
    result = apply_patch(base_env, patch)
    assert "APP_PORT" not in result


def test_apply_patch_modifies_key(base_env):
    patch = DiffPatch(
        entries=[DiffPatchEntry("APP_HOST", "modify", "localhost", "prod.example.com")]
    )
    result = apply_patch(base_env, patch)
    assert result["APP_HOST"] == "prod.example.com"


def test_apply_patch_preserves_untouched_keys(base_env):
    patch = DiffPatch(entries=[DiffPatchEntry("NEW", "add", None, "x")])
    result = apply_patch(base_env, patch)
    assert result["DB_PASS"] == "secret"


def test_apply_patch_strict_raises_on_duplicate_add(base_env):
    patch = DiffPatch(entries=[DiffPatchEntry("APP_HOST", "add", None, "x")])
    with pytest.raises(ValueError, match="already exists"):
        apply_patch(base_env, patch, strict=True)


def test_apply_patch_strict_raises_on_missing_remove():
    patch = DiffPatch(entries=[DiffPatchEntry("GHOST", "remove", "v", None)])
    with pytest.raises(ValueError, match="not found"):
        apply_patch({}, patch, strict=True)


def test_apply_patch_non_strict_missing_remove_is_noop():
    patch = DiffPatch(entries=[DiffPatchEntry("GHOST", "remove", "v", None)])
    result = apply_patch({"A": "1"}, patch, strict=False)
    assert result == {"A": "1"}


def test_diff_patch_entry_repr():
    entry = DiffPatchEntry("KEY", "add", None, "val")
    assert "add" in repr(entry)
    assert "KEY" in repr(entry)
