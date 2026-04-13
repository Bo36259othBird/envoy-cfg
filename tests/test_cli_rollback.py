"""Tests for CLI rollback commands."""

import argparse
import pytest
from io import StringIO
from unittest.mock import patch

from envoy_cfg.cli_rollback import cmd_rollback, register_rollback_commands
from envoy_cfg.snapshot import EnvSnapshot, SnapshotStore
from envoy_cfg.targets import DeploymentTarget, TargetRegistry


@pytest.fixture
def registry():
    reg = TargetRegistry()
    target = DeploymentTarget(
        name="api",
        environment="production",
        env={"HOST": "localhost"},
    )
    reg.register(target)
    return reg


@pytest.fixture
def store():
    s = SnapshotStore()
    snap = EnvSnapshot(
        snapshot_id="snap-abc",
        target_name="api",
        environment="production",
        env={"HOST": "prod-host", "PORT": "443"},
        timestamp="2024-06-01T12:00:00",
    )
    s._snapshots["snap-abc"] = snap
    return s


def make_args(target="api", snapshot_id="snap-abc", dry_run=False):
    args = argparse.Namespace()
    args.target = target
    args.snapshot_id = snapshot_id
    args.dry_run = dry_run
    return args


def test_cmd_rollback_success(registry, store, capsys):
    cmd_rollback(make_args(), registry, store)
    out = capsys.readouterr().out
    assert "api" in out
    assert "snap-abc" in out
    assert "Rollback applied" in out


def test_cmd_rollback_dry_run_label(registry, store, capsys):
    cmd_rollback(make_args(dry_run=True), registry, store)
    out = capsys.readouterr().out
    assert "[dry-run]" in out
    assert "No changes will be applied" in out


def test_cmd_rollback_missing_target(registry, store, capsys):
    cmd_rollback(make_args(target="ghost"), registry, store)
    out = capsys.readouterr().out
    assert "[error]" in out
    assert "not found" in out


def test_cmd_rollback_missing_snapshot(registry, store, capsys):
    cmd_rollback(make_args(snapshot_id="snap-zzz"), registry, store)
    out = capsys.readouterr().out
    assert "[error]" in out


def test_register_rollback_commands_adds_subparser():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()
    register_rollback_commands(subparsers)
    args = parser.parse_args(["rollback", "web", "snap-001"])
    assert args.target == "web"
    assert args.snapshot_id == "snap-001"
    assert args.dry_run is False
