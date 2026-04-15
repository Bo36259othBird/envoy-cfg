"""Tests for envoy_cfg.patch."""

import pytest
from envoy_cfg.patch import PatchOperation, PatchResult, apply_patch


@pytest.fixture
def base_env():
    return {"APP_HOST": "localhost", "APP_PORT": "8080", "DB_PASSWORD": "secret"}


def test_patch_set_new_key(base_env):
    ops = [PatchOperation(op="set", key="APP_DEBUG", value="true")]
    result = apply_patch(base_env, ops)
    assert result.patched["APP_DEBUG"] == "true"
    assert len(result.applied) == 1
    assert result.is_clean


def test_patch_set_overwrites_existing_key(base_env):
    ops = [PatchOperation(op="set", key="APP_PORT", value="9090")]
    result = apply_patch(base_env, ops)
    assert result.patched["APP_PORT"] == "9090"


def test_patch_delete_existing_key(base_env):
    ops = [PatchOperation(op="delete", key="DB_PASSWORD")]
    result = apply_patch(base_env, ops)
    assert "DB_PASSWORD" not in result.patched
    assert len(result.applied) == 1


def test_patch_delete_missing_key_is_skipped(base_env):
    ops = [PatchOperation(op="delete", key="NONEXISTENT")]
    result = apply_patch(base_env, ops)
    assert len(result.skipped) == 1
    assert not result.is_clean


def test_patch_rename_key(base_env):
    ops = [PatchOperation(op="rename", key="APP_HOST", new_key="SERVICE_HOST")]
    result = apply_patch(base_env, ops)
    assert "APP_HOST" not in result.patched
    assert result.patched["SERVICE_HOST"] == "localhost"


def test_patch_rename_missing_key_is_skipped(base_env):
    ops = [PatchOperation(op="rename", key="MISSING", new_key="OTHER")]
    result = apply_patch(base_env, ops)
    assert len(result.skipped) == 1


def test_patch_rename_without_new_key_is_skipped(base_env):
    ops = [PatchOperation(op="rename", key="APP_HOST", new_key=None)]
    result = apply_patch(base_env, ops)
    assert len(result.skipped) == 1


def test_patch_set_without_value_is_skipped(base_env):
    ops = [PatchOperation(op="set", key="APP_HOST", value=None)]
    result = apply_patch(base_env, ops)
    assert len(result.skipped) == 1


def test_patch_invalid_op_is_skipped(base_env):
    ops = [PatchOperation(op="upsert", key="APP_HOST", value="x")]
    result = apply_patch(base_env, ops)
    assert len(result.skipped) == 1


def test_patch_does_not_mutate_original(base_env):
    original_copy = dict(base_env)
    ops = [PatchOperation(op="delete", key="APP_PORT")]
    result = apply_patch(base_env, ops)
    assert base_env == original_copy
    assert result.original == original_copy


def test_patch_multiple_ops_applied_in_order(base_env):
    ops = [
        PatchOperation(op="set", key="APP_PORT", value="443"),
        PatchOperation(op="rename", key="APP_PORT", new_key="HTTPS_PORT"),
    ]
    result = apply_patch(base_env, ops)
    assert "APP_PORT" not in result.patched
    assert result.patched["HTTPS_PORT"] == "443"
    assert len(result.applied) == 2


def test_patch_result_repr(base_env):
    result = apply_patch(base_env, [])
    assert "PatchResult" in repr(result)
    assert "applied=0" in repr(result)


def test_patch_operation_repr_set():
    op = PatchOperation(op="set", key="FOO", value="bar")
    assert "set" in repr(op)
    assert "FOO" in repr(op)


def test_patch_operation_repr_delete():
    op = PatchOperation(op="delete", key="FOO")
    assert "delete" in repr(op)


def test_patch_operation_repr_rename():
    op = PatchOperation(op="rename", key="FOO", new_key="BAR")
    assert "rename" in repr(op)
    assert "BAR" in repr(op)
