"""Integration tests for mask_audit — verifies interaction with audit and masking."""

from __future__ import annotations

from envoy_cfg.mask_audit import mask_and_audit
from envoy_cfg.audit import AuditLog
from envoy_cfg.masking import mask_env
from envoy_cfg.diff import compute_diff


def _make_env() -> dict:
    return {
        "SERVICE": "api",
        "DB_PASSWORD": "hunter2",
        "API_SECRET": "topsecret",
        "TIMEOUT": "30",
    }


def test_mask_and_audit_masked_env_matches_standalone_mask():
    env = _make_env()
    result = mask_and_audit(env, target="prod")
    expected = mask_env(env)
    assert result.masked_env == expected


def test_mask_and_audit_diff_shows_no_changes_on_plain_keys():
    env = _make_env()
    result = mask_and_audit(env, target="prod")
    # Plain keys should be identical in both original and masked envs
    plain_original = {k: v for k, v in env.items() if k not in result.masked_keys}
    plain_masked = {k: v for k, v in result.masked_env.items() if k not in result.masked_keys}
    assert plain_original == plain_masked


def test_audit_log_entries_reference_masked_keys_only(tmp_path):
    env = _make_env()
    log = AuditLog(path=tmp_path / "audit.json")
    result = mask_and_audit(env, target="staging", log=log)
    logged_keys = {e.key for e in log.list_entries()}
    assert logged_keys == set(result.masked_keys)


def test_repeated_calls_append_to_audit_log(tmp_path):
    env = _make_env()
    log = AuditLog(path=tmp_path / "audit.json")
    mask_and_audit(env, target="dev", log=log)
    mask_and_audit(env, target="prod", log=log)
    entries = log.list_entries()
    # Each call adds one entry per masked key
    assert len(entries) == 2 * len([k for k in env if k in ("DB_PASSWORD", "API_SECRET")])


def test_mask_and_audit_result_repr_contains_counts():
    env = _make_env()
    result = mask_and_audit(env, target="prod")
    r = repr(result)
    assert "total=" in r
    assert "masked=" in r
