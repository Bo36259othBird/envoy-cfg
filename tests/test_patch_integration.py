"""Integration tests: patch combined with diff and masking."""

from envoy_cfg.patch import PatchOperation, apply_patch
from envoy_cfg.diff import compute_diff
from envoy_cfg.masking import mask_env


@pytest.fixture
def env():
    return {
        "APP_HOST": "localhost",
        "APP_PORT": "8080",
        "SECRET_KEY": "topsecret",
        "DB_URL": "postgres://localhost/db",
    }


import pytest


def test_patch_then_diff_shows_changes(env):
    ops = [
        PatchOperation(op="set", key="APP_PORT", value="443"),
        PatchOperation(op="delete", key="DB_URL"),
    ]
    result = apply_patch(env, ops)
    diff = compute_diff(env, result.patched)
    keys_changed = {c.key for c in diff.changes}
    assert "APP_PORT" in keys_changed
    assert "DB_URL" in keys_changed


def test_patch_then_mask_hides_secrets(env):
    ops = [PatchOperation(op="set", key="SECRET_KEY", value="newsecret")]
    result = apply_patch(env, ops)
    masked = mask_env(result.patched)
    assert masked["SECRET_KEY"] != "newsecret"
    assert "*" in masked["SECRET_KEY"]


def test_patch_rename_then_diff_reflects_add_remove(env):
    ops = [PatchOperation(op="rename", key="APP_HOST", new_key="SERVICE_HOST")]
    result = apply_patch(env, ops)
    diff = compute_diff(env, result.patched)
    keys_changed = {c.key for c in diff.changes}
    assert "APP_HOST" in keys_changed
    assert "SERVICE_HOST" in keys_changed


def test_empty_patch_produces_identical_env(env):
    result = apply_patch(env, [])
    assert result.patched == env
    assert result.is_clean


def test_patch_all_ops_combined(env):
    ops = [
        PatchOperation(op="set", key="NEW_VAR", value="hi"),
        PatchOperation(op="delete", key="DB_URL"),
        PatchOperation(op="rename", key="APP_HOST", new_key="HOST"),
    ]
    result = apply_patch(env, ops)
    assert "NEW_VAR" in result.patched
    assert "DB_URL" not in result.patched
    assert "HOST" in result.patched
    assert "APP_HOST" not in result.patched
    assert len(result.applied) == 3
    assert result.is_clean
