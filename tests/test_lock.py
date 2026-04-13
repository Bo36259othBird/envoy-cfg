"""Tests for envoy_cfg.lock — LockEntry and LockStore."""

from __future__ import annotations

import json
import os
import pytest

from envoy_cfg.lock import LockEntry, LockStore


@pytest.fixture
def lock_file(tmp_path):
    return str(tmp_path / "test_locks.json")


@pytest.fixture
def store(lock_file):
    return LockStore(lock_file)


def test_lock_entry_to_dict():
    entry = LockEntry(target_name="api", environment="production", reason="freeze")
    d = entry.to_dict()
    assert d["target_name"] == "api"
    assert d["environment"] == "production"
    assert d["reason"] == "freeze"


def test_lock_entry_from_dict_roundtrip():
    data = {"target_name": "web", "environment": "staging", "reason": None}
    entry = LockEntry.from_dict(data)
    assert entry.target_name == "web"
    assert entry.environment == "staging"
    assert entry.reason is None


def test_lock_entry_repr_with_reason():
    entry = LockEntry("svc", "production", reason="deploy freeze")
    assert "deploy freeze" in repr(entry)
    assert "svc/production" in repr(entry)


def test_lock_entry_repr_without_reason():
    entry = LockEntry("svc", "staging")
    assert "svc/staging" in repr(entry)
    assert "(" not in repr(entry)


def test_is_locked_false_initially(store):
    assert store.is_locked("api", "production") is False


def test_lock_creates_entry(store):
    entry = store.lock("api", "production", reason="freeze")
    assert entry.target_name == "api"
    assert store.is_locked("api", "production") is True


def test_lock_persists_to_file(lock_file, store):
    store.lock("api", "production")
    store2 = LockStore(lock_file)
    assert store2.is_locked("api", "production") is True


def test_lock_duplicate_raises(store):
    store.lock("api", "production")
    with pytest.raises(ValueError, match="already locked"):
        store.lock("api", "production")


def test_unlock_removes_entry(store):
    store.lock("api", "production")
    result = store.unlock("api", "production")
    assert result is True
    assert store.is_locked("api", "production") is False


def test_unlock_nonexistent_returns_false(store):
    result = store.unlock("api", "production")
    assert result is False


def test_list_locks_empty(store):
    assert store.list_locks() == []


def test_list_locks_returns_all(store):
    store.lock("api", "production")
    store.lock("web", "staging")
    locks = store.list_locks()
    assert len(locks) == 2
    names = {(e.target_name, e.environment) for e in locks}
    assert ("api", "production") in names
    assert ("web", "staging") in names


def test_lock_does_not_affect_different_environment(store):
    store.lock("api", "production")
    assert store.is_locked("api", "staging") is False
