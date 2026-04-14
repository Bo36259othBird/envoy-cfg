"""Tests for envoy_cfg.pin module."""

import json
import pytest
from envoy_cfg.pin import PinEntry, PinStore


@pytest.fixture
def pin_file(tmp_path):
    return str(tmp_path / "pins.json")


@pytest.fixture
def store(pin_file):
    return PinStore(pin_file)


# --- PinEntry ---

def test_pin_entry_to_dict():
    entry = PinEntry(key="DB_HOST", value="localhost", target="prod", reason="stable")
    d = entry.to_dict()
    assert d["key"] == "DB_HOST"
    assert d["value"] == "localhost"
    assert d["target"] == "prod"
    assert d["reason"] == "stable"


def test_pin_entry_from_dict_roundtrip():
    original = PinEntry(key="API_URL", value="https://api.example.com", target="staging")
    restored = PinEntry.from_dict(original.to_dict())
    assert restored.key == original.key
    assert restored.value == original.value
    assert restored.target == original.target
    assert restored.reason is None


def test_pin_entry_repr_includes_info():
    entry = PinEntry(key="SECRET", value="abc", target="dev", reason="test")
    r = repr(entry)
    assert "dev:SECRET" in r
    assert "test" in r


def test_pin_entry_repr_without_reason():
    entry = PinEntry(key="FOO", value="bar", target="prod")
    r = repr(entry)
    assert "FOO" in r
    assert "(" not in r


# --- PinStore ---

def test_pin_adds_entry(store):
    entry = store.pin("prod", "DB_HOST", "db.prod.internal")
    assert entry.key == "DB_HOST"
    assert entry.target == "prod"


def test_pin_persists_to_file(pin_file):
    s = PinStore(pin_file)
    s.pin("prod", "REGION", "us-east-1", reason="fixed region")
    s2 = PinStore(pin_file)
    entry = s2.get("prod", "REGION")
    assert entry is not None
    assert entry.value == "us-east-1"
    assert entry.reason == "fixed region"


def test_unpin_removes_entry(store):
    store.pin("staging", "LOG_LEVEL", "debug")
    removed = store.unpin("staging", "LOG_LEVEL")
    assert removed is True
    assert store.get("staging", "LOG_LEVEL") is None


def test_unpin_nonexistent_returns_false(store):
    result = store.unpin("prod", "NONEXISTENT")
    assert result is False


def test_list_for_target_filters_correctly(store):
    store.pin("prod", "A", "1")
    store.pin("prod", "B", "2")
    store.pin("staging", "A", "3")
    prod_pins = store.list_for_target("prod")
    assert len(prod_pins) == 2
    assert all(e.target == "prod" for e in prod_pins)


def test_apply_enforces_pinned_values(store):
    store.pin("prod", "DB_HOST", "pinned-host")
    env = {"DB_HOST": "original-host", "APP_ENV": "production"}
    result = store.apply("prod", env)
    assert result["DB_HOST"] == "pinned-host"
    assert result["APP_ENV"] == "production"


def test_apply_adds_missing_pinned_key(store):
    store.pin("prod", "FORCED_KEY", "forced-value")
    env = {"OTHER": "x"}
    result = store.apply("prod", env)
    assert result["FORCED_KEY"] == "forced-value"


def test_apply_does_not_mutate_original(store):
    store.pin("prod", "X", "new")
    env = {"X": "old"}
    store.apply("prod", env)
    assert env["X"] == "old"


def test_all_returns_all_entries(store):
    store.pin("prod", "K1", "v1")
    store.pin("staging", "K2", "v2")
    assert len(store.all()) == 2
