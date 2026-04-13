"""Tests for envoy_cfg.cli_lock CLI commands."""

from __future__ import annotations

import argparse
import pytest

from envoy_cfg.lock import LockStore
from envoy_cfg.cli_lock import cmd_lock, cmd_unlock, cmd_lock_list


@pytest.fixture
def lock_file(tmp_path):
    return str(tmp_path / "cli_test_locks.json")


@pytest.fixture
def store(lock_file):
    return LockStore(lock_file)


def make_args(**kwargs) -> argparse.Namespace:
    defaults = {"target": "api", "environment": "production", "reason": None, "lock_file": None}
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_cmd_lock_success(lock_file, store, capsys):
    args = make_args(lock_file=lock_file)
    cmd_lock(args)
    out = capsys.readouterr().out
    assert "Locked" in out
    assert store.is_locked("api", "production") is True


def test_cmd_lock_with_reason(lock_file, capsys):
    args = make_args(lock_file=lock_file, reason="release freeze")
    cmd_lock(args)
    out = capsys.readouterr().out
    assert "Locked" in out


def test_cmd_lock_duplicate_prints_error(lock_file, capsys):
    args = make_args(lock_file=lock_file)
    cmd_lock(args)
    capsys.readouterr()
    cmd_lock(args)
    out = capsys.readouterr().out
    assert "Error" in out


def test_cmd_unlock_success(lock_file, store, capsys):
    store.lock("api", "production")
    args = make_args(lock_file=lock_file)
    cmd_unlock(args)
    out = capsys.readouterr().out
    assert "Unlocked" in out
    assert store.is_locked("api", "production") is False


def test_cmd_unlock_nonexistent_prints_message(lock_file, capsys):
    args = make_args(lock_file=lock_file)
    cmd_unlock(args)
    out = capsys.readouterr().out
    assert "No lock found" in out


def test_cmd_lock_list_empty(lock_file, capsys):
    args = make_args(lock_file=lock_file)
    cmd_lock_list(args)
    out = capsys.readouterr().out
    assert "No locks" in out


def test_cmd_lock_list_shows_entries(lock_file, store, capsys):
    store.lock("api", "production", reason="freeze")
    store.lock("web", "staging")
    args = make_args(lock_file=lock_file)
    cmd_lock_list(args)
    out = capsys.readouterr().out
    assert "api/production" in out
    assert "web/staging" in out
    assert "freeze" in out
