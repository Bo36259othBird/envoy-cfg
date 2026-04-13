"""Tests for the promote CLI command."""

import argparse
import pytest
from envoy_cfg.cli_promote import cmd_promote, register_promote_commands
from envoy_cfg.targets import DeploymentTarget, TargetRegistry


@pytest.fixture
def registry() -> TargetRegistry:
    reg = TargetRegistry()
    reg.register(
        DeploymentTarget(
            name="staging",
            environment="staging",
            env_vars={"KEY1": "val1", "SECRET_TOKEN": "abc123"},
        )
    )
    reg.register(
        DeploymentTarget(
            name="production",
            environment="production",
            env_vars={"KEY1": "prod_val"},
        )
    )
    return reg


def make_args(**kwargs):
    defaults = {
        "source": "staging",
        "destination": "production",
        "strategy": "union",
        "dry_run": False,
        "show_secrets": False,
    }
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_cmd_promote_success(registry, capsys):
    args = make_args()
    code = cmd_promote(args, registry)
    assert code == 0
    out = capsys.readouterr().out
    assert "staging" in out
    assert "production" in out


def test_cmd_promote_dry_run_label(registry, capsys):
    args = make_args(dry_run=True)
    code = cmd_promote(args, registry)
    assert code == 0
    out = capsys.readouterr().out
    assert "dry-run" in out


def test_cmd_promote_invalid_strategy(registry, capsys):
    args = make_args(strategy="invalid")
    code = cmd_promote(args, registry)
    assert code == 1
    out = capsys.readouterr().out
    assert "Invalid strategy" in out


def test_cmd_promote_missing_source(registry, capsys):
    args = make_args(source="ghost")
    code = cmd_promote(args, registry)
    assert code == 1
    out = capsys.readouterr().out
    assert "error" in out


def test_register_promote_commands():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()
    register_promote_commands(subparsers)
    args = parser.parse_args(["promote", "staging", "production"])
    assert args.source == "staging"
    assert args.destination == "production"
    assert args.strategy == "union"
    assert args.dry_run is False
