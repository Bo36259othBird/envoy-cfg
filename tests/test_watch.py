"""Tests for envoy_cfg.watch module."""

import os
import time

import pytest

from envoy_cfg.watch import EnvWatcher, WatchEntry, _file_hash


@pytest.fixture
def tmp_env_file(tmp_path):
    f = tmp_path / ".env"
    f.write_text("KEY=value\n")
    return str(f)


def test_file_hash_returns_string_for_existing_file(tmp_env_file):
    result = _file_hash(tmp_env_file)
    assert isinstance(result, str)
    assert len(result) == 32  # MD5 hex digest


def test_file_hash_returns_none_for_missing_file():
    result = _file_hash("/nonexistent/path/.env")
    assert result is None


def test_file_hash_changes_on_content_update(tmp_env_file):
    h1 = _file_hash(tmp_env_file)
    with open(tmp_env_file, "a") as f:
        f.write("NEW=1\n")
    h2 = _file_hash(tmp_env_file)
    assert h1 != h2


def test_watch_entry_has_changed_detects_modification(tmp_env_file):
    entry = WatchEntry(path=tmp_env_file, last_hash=_file_hash(tmp_env_file))
    assert not entry.has_changed()
    with open(tmp_env_file, "a") as f:
        f.write("EXTRA=yes\n")
    assert entry.has_changed()


def test_watch_entry_updates_last_hash_after_check(tmp_env_file):
    entry = WatchEntry(path=tmp_env_file, last_hash=None)
    entry.has_changed()
    assert entry.last_hash == _file_hash(tmp_env_file)


def test_watcher_registers_path(tmp_env_file):
    watcher = EnvWatcher()
    watcher.watch(tmp_env_file, lambda p: None)
    assert os.path.abspath(tmp_env_file) in watcher.watched_paths


def test_watcher_unwatch_removes_path(tmp_env_file):
    watcher = EnvWatcher()
    watcher.watch(tmp_env_file, lambda p: None)
    removed = watcher.unwatch(tmp_env_file)
    assert removed is True
    assert tmp_env_file not in watcher.watched_paths


def test_watcher_unwatch_returns_false_for_unknown_path():
    watcher = EnvWatcher()
    assert watcher.unwatch("/some/unknown/path") is False


def test_watcher_check_once_triggers_callback_on_change(tmp_env_file):
    triggered = []
    watcher = EnvWatcher()
    watcher.watch(tmp_env_file, lambda p: triggered.append(p))

    with open(tmp_env_file, "a") as f:
        f.write("CHANGED=1\n")

    results = watcher.check_once()
    assert any(results.values())
    assert len(triggered) == 1


def test_watcher_check_once_no_change_no_callback(tmp_env_file):
    triggered = []
    watcher = EnvWatcher()
    watcher.watch(tmp_env_file, lambda p: triggered.append(p))
    watcher.check_once()  # baseline
    watcher.check_once()  # no change
    assert triggered == []


def test_watcher_run_limited_cycles(tmp_env_file):
    watcher = EnvWatcher(poll_interval=0.0)
    watcher.watch(tmp_env_file, lambda p: None)
    # Should complete without hanging
    watcher.run(max_cycles=3)
    assert True
