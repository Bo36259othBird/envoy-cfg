"""Tests for envoy_cfg.audit module."""

import json
import os
import pytest
from envoy_cfg.audit import AuditEntry, AuditLog


@pytest.fixture
def tmp_log(tmp_path):
    return str(tmp_path / "test_audit.json")


@pytest.fixture
def sample_entry():
    return AuditEntry(
        action="sync",
        target_name="web-prod",
        environment="production",
        keys_affected=["DATABASE_URL", "API_KEY"],
        performed_by="alice",
    )


def test_audit_entry_to_dict(sample_entry):
    d = sample_entry.to_dict()
    assert d["action"] == "sync"
    assert d["target_name"] == "web-prod"
    assert d["environment"] == "production"
    assert d["keys_affected"] == ["DATABASE_URL", "API_KEY"]
    assert d["performed_by"] == "alice"
    assert d["dry_run"] is False


def test_audit_entry_from_dict_roundtrip(sample_entry):
    restored = AuditEntry.from_dict(sample_entry.to_dict())
    assert restored.action == sample_entry.action
    assert restored.target_name == sample_entry.target_name
    assert restored.keys_affected == sample_entry.keys_affected
    assert restored.timestamp == sample_entry.timestamp


def test_audit_entry_repr_includes_key_info(sample_entry):
    r = repr(sample_entry)
    assert "sync" in r
    assert "web-prod" in r
    assert "alice" in r
    assert "2 key(s)" in r


def test_audit_entry_repr_marks_dry_run():
    entry = AuditEntry(
        action="sync",
        target_name="api-staging",
        environment="staging",
        keys_affected=["SECRET"],
        performed_by="bob",
        dry_run=True,
    )
    assert "[DRY RUN]" in repr(entry)


def test_audit_log_record_and_retrieve(tmp_log, sample_entry):
    log = AuditLog(log_path=tmp_log)
    log.record(sample_entry)
    entries = log.all()
    assert len(entries) == 1
    assert entries[0].action == "sync"


def test_audit_log_persists_to_disk(tmp_log, sample_entry):
    log = AuditLog(log_path=tmp_log)
    log.record(sample_entry)
    log2 = AuditLog(log_path=tmp_log)
    assert len(log2.all()) == 1


def test_audit_log_filter_by_target(tmp_log):
    log = AuditLog(log_path=tmp_log)
    log.record(AuditEntry("sync", "web-prod", "production", ["A"], "alice"))
    log.record(AuditEntry("sync", "api-prod", "production", ["B"], "alice"))
    results = log.filter_by_target("web-prod")
    assert len(results) == 1
    assert results[0].target_name == "web-prod"


def test_audit_log_filter_by_environment(tmp_log):
    log = AuditLog(log_path=tmp_log)
    log.record(AuditEntry("sync", "web-prod", "production", ["A"], "alice"))
    log.record(AuditEntry("sync", "web-staging", "staging", ["A"], "alice"))
    results = log.filter_by_environment("staging")
    assert len(results) == 1
    assert results[0].environment == "staging"


def test_audit_log_clear(tmp_log, sample_entry):
    log = AuditLog(log_path=tmp_log)
    log.record(sample_entry)
    log.clear()
    assert log.all() == []
    log2 = AuditLog(log_path=tmp_log)
    assert log2.all() == []
