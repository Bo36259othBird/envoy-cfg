"""Tests for envoy_cfg.history module."""

import json
import os
import pytest

from envoy_cfg.history import HistoryEntry, HistoryStore


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def history_file(tmp_path):
    return str(tmp_path / "history.json")


@pytest.fixture
def store(history_file):
    return HistoryStore(history_file)


@pytest.fixture
def sample_entry():
    return HistoryEntry(
        target_name="web",
        environment="production",
        key="DATABASE_URL",
        old_value="postgres://old",
        new_value="postgres://new",
        author="alice",
    )


# ---------------------------------------------------------------------------
# HistoryEntry tests
# ---------------------------------------------------------------------------

def test_history_entry_to_dict(sample_entry):
    d = sample_entry.to_dict()
    assert d["target_name"] == "web"
    assert d["key"] == "DATABASE_URL"
    assert d["old_value"] == "postgres://old"
    assert d["new_value"] == "postgres://new"
    assert d["author"] == "alice"
    assert "changed_at" in d


def test_history_entry_from_dict_roundtrip(sample_entry):
    restored = HistoryEntry.from_dict(sample_entry.to_dict())
    assert restored.target_name == sample_entry.target_name
    assert restored.key == sample_entry.key
    assert restored.old_value == sample_entry.old_value
    assert restored.new_value == sample_entry.new_value
    assert restored.author == sample_entry.author


def test_history_entry_repr_contains_key_info(sample_entry):
    r = repr(sample_entry)
    assert "web" in r
    assert "DATABASE_URL" in r


def test_history_entry_none_values_allowed():
    entry = HistoryEntry(
        target_name="api",
        environment="staging",
        key="NEW_KEY",
        old_value=None,
        new_value="hello",
    )
    d = entry.to_dict()
    assert d["old_value"] is None


# ---------------------------------------------------------------------------
# HistoryStore tests
# ---------------------------------------------------------------------------

def test_store_starts_empty(store):
    assert store.all_entries() == []


def test_store_record_persists(history_file, sample_entry):
    store = HistoryStore(history_file)
    store.record(sample_entry)
    reloaded = HistoryStore(history_file)
    assert len(reloaded.all_entries()) == 1
    assert reloaded.all_entries()[0].key == "DATABASE_URL"


def test_store_record_changes_detects_diff(store):
    before = {"A": "1", "B": "2", "C": "3"}
    after  = {"A": "1", "B": "99", "D": "4"}
    recorded = store.record_changes("svc", "staging", before, after, author="bob")
    keys = {e.key for e in recorded}
    assert "B" in keys   # modified
    assert "C" in keys   # removed (new_value=None)
    assert "D" in keys   # added   (old_value=None)
    assert "A" not in keys  # unchanged


def test_store_for_target_filters_correctly(store):
    store.record(HistoryEntry("web", "prod", "KEY1", "a", "b"))
    store.record(HistoryEntry("api", "prod", "KEY2", "x", "y"))
    web_entries = store.for_target("web")
    assert all(e.target_name == "web" for e in web_entries)
    assert len(web_entries) == 1


def test_store_for_key_filters_correctly(store):
    store.record(HistoryEntry("web", "prod", "SECRET_KEY", "old", "new"))
    store.record(HistoryEntry("web", "prod", "OTHER", "a", "b"))
    entries = store.for_key("web", "SECRET_KEY")
    assert len(entries) == 1
    assert entries[0].key == "SECRET_KEY"


def test_store_clear_removes_all_entries(store, sample_entry):
    store.record(sample_entry)
    store.clear()
    assert store.all_entries() == []


def test_store_loads_existing_file(history_file, sample_entry):
    # Pre-populate file manually
    with open(history_file, "w") as fh:
        json.dump([sample_entry.to_dict()], fh)
    store = HistoryStore(history_file)
    assert len(store.all_entries()) == 1
