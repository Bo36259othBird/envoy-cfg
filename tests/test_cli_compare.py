"""Tests for CLI compare commands."""

import argparse
from io import StringIO
from unittest.mock import patch

import pytest

from envoy_cfg.cli_compare import cmd_compare, cmd_compare_all, register_compare_commands
from envoy_cfg.targets import DeploymentTarget, TargetRegistry


@pytest.fixture
def registry() -> TargetRegistry:
    reg = TargetRegistry()
    reg.register(
        DeploymentTarget(
            name="alpha",
            environment="staging",
            env={"HOST": "alpha.local", "SECRET_KEY": "s3cr3t", "EXTRA": "only-alpha"},
        )
    )
    reg.register(
        DeploymentTarget(
            name="beta",
            environment="staging",
            env={"HOST": "beta.local", "SECRET_KEY": "b3t4k3y"},
        )
    )
    return reg


def make_args(**kwargs) -> argparse.Namespace:
    defaults = {"no_mask": False, "masked_note": True, "environment": None}
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_cmd_compare_prints_differences(registry, capsys):
    args = make_args(source="alpha", dest="beta")
    cmd_compare(args, registry)
    captured = capsys.readouterr()
    assert "alpha" in captured.out
    assert "beta" in captured.out


def test_cmd_compare_no_differences(registry, capsys):
    args = make_args(source="alpha", dest="alpha")
    cmd_compare(args, registry)
    captured = capsys.readouterr()
    assert "No differences" in captured.out


def test_cmd_compare_missing_target(registry, capsys):
    args = make_args(source="ghost", dest="beta")
    cmd_compare(args, registry)
    captured = capsys.readouterr()
    assert "error" in captured.out.lower() or "not found" in captured.out.lower()


def test_cmd_compare_masked_note_shown(registry, capsys):
    args = make_args(source="alpha", dest="beta", no_mask=False, masked_note=True)
    cmd_compare(args, registry)
    captured = capsys.readouterr()
    assert "masked" in captured.out


def test_cmd_compare_all_lists_all_sources(registry, capsys):
    args = make_args(dest="beta")
    cmd_compare_all(args, registry)
    captured = capsys.readouterr()
    assert "alpha" in captured.out


def test_register_compare_commands_adds_subparsers():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()
    reg = TargetRegistry()
    register_compare_commands(subparsers, reg)
    args = parser.parse_args(["compare", "src", "dst"])
    assert args.source == "src"
    assert args.dest == "dst"
