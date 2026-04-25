"""Tests for envoy_cfg.mask_audit."""

from __future__ import annotations

import pytest

from envoy_cfg.mask_audit import mask_and_audit, MaskAuditResult
from envoy_cfg.audit import AuditLog


@pytest.fixture()
def mixed_env() -> dict:
    return {
        "APP_NAME": "myapp",
        "DB_PASSWORD": "s3cr3t",
        "API_KEY": "abc123",
        "PORT": "8080",
        "SECRET_TOKEN": "tok",
    }


def test_mask_and_audit_returns_result(mixed_env):
    result = mask_and_audit(mixed_env, target="prod")
    assert isinstance(result, MaskAuditResult)


def test_mask_and_audit_total_equals_env_size(mixed_env):
    result = mask_and_audit(mixed_env, target="prod")
    assert result.total == len(mixed_env)


def test_mask_and_audit_masked_keys_are_secrets(mixed_env):
    result = mask_and_audit(mixed_env, target="prod")
    for key in result.masked_keys:
        assert key in ("DB_PASSWORD", "API_KEY", "SECRET_TOKEN")


def test_mask_and_audit_plain_keys_not_masked(mixed_env):
    result = mask_and_audit(mixed_env, target="prod")
    assert result.masked_env["APP_NAME"] == "myapp"
    assert result.masked_env["PORT"] == "8080"


def test_mask_and_audit_secret_values_are_masked(mixed_env):
    result = mask_and_audit(mixed_env, target="prod")
    for key in result.masked_keys:
        assert result.masked_env[key] != mixed_env[key]


def test_mask_and_audit_audit_entries_count_matches_masked_keys(mixed_env):
    result = mask_and_audit(mixed_env, target="prod")
    assert len(result.audit_entries) == len(result.masked_keys)


def test_mask_and_audit_entries_have_correct_target(mixed_env):
    result = mask_and_audit(mixed_env, target="staging")
    for entry in result.audit_entries:
        assert entry.target == "staging"


def test_mask_and_audit_entries_have_correct_operation(mixed_env):
    result = mask_and_audit(mixed_env, target="prod", operation="export")
    for entry in result.audit_entries:
        assert entry.operation == "export"


def test_mask_and_audit_entries_have_correct_actor(mixed_env):
    result = mask_and_audit(mixed_env, target="prod", actor="ci-bot")
    for entry in result.audit_entries:
        assert entry.actor == "ci-bot"


def test_mask_and_audit_is_clean_when_no_secrets():
    env = {"APP_NAME": "myapp", "PORT": "8080"}
    result = mask_and_audit(env, target="dev")
    assert result.is_clean
    assert result.masked_keys == []
    assert result.audit_entries == []


def test_mask_and_audit_is_not_clean_with_secrets(mixed_env):
    result = mask_and_audit(mixed_env, target="prod")
    assert not result.is_clean


def test_mask_and_audit_persists_to_log(mixed_env, tmp_path):
    log_file = tmp_path / "audit.json"
    log = AuditLog(path=log_file)
    result = mask_and_audit(mixed_env, target="prod", log=log)
    persisted = log.list_entries()
    assert len(persisted) == len(result.masked_keys)


def test_mask_and_audit_no_log_does_not_raise(mixed_env):
    result = mask_and_audit(mixed_env, target="prod", log=None)
    assert len(result.audit_entries) > 0


def test_mask_and_audit_masked_keys_sorted(mixed_env):
    result = mask_and_audit(mixed_env, target="prod")
    assert result.masked_keys == sorted(result.masked_keys)


def test_mask_and_audit_empty_env():
    result = mask_and_audit({}, target="prod")
    assert result.total == 0
    assert result.is_clean
    assert result.masked_env == {}
