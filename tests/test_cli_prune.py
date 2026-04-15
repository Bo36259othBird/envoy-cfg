"""Tests for envoy_cfg.cli_prune."""
import argparse
import json
from pathlib import Path

import pytest

from envoy_cfg.cli_prune import cmd_prune, register_prune_commands


@pytest.fixture
def dotenv_file(tmp_path: Path) -> Path:
    p = tmp_path / ".env"
    p.write_text(
        "APP_NAME=myapp\n"
        "DEBUG=\n"
        "SECRET_KEY=abc123\n"
        "TMP_TOKEN=xyz\n"
        "DB_HOST=localhost\n"
    )
    return p


def make_args(**kwargs) -> argparse.Namespace:
    defaults = {
        "mode": "empty",
        "keys": None,
        "prefix": None,
        "suffix": None,
        "no_strip": False,
        "format": "dotenv",
    }
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_cmd_prune_empty_dotenv_output(dotenv_file, capsys):
    args = make_args(file=str(dotenv_file), mode="empty", format="dotenv")
    cmd_prune(args)
    out = capsys.readouterr().out
    assert "APP_NAME=myapp" in out
    assert "DEBUG=" not in out


def test_cmd_prune_empty_json_output(dotenv_file, capsys):
    args = make_args(file=str(dotenv_file), mode="empty", format="json")
    cmd_prune(args)
    out = capsys.readouterr().out
    data = json.loads(out)
    assert "DEBUG" in data["removed"]
    assert data["reason"] == "empty_value"


def test_cmd_prune_keys_mode(dotenv_file, capsys):
    args = make_args(file=str(dotenv_file), mode="keys", keys=["APP_NAME", "DB_HOST"], format="json")
    cmd_prune(args)
    data = json.loads(capsys.readouterr().out)
    assert "APP_NAME" in data["removed"]
    assert "DB_HOST" in data["removed"]
    assert "SECRET_KEY" in data["env"]


def test_cmd_prune_keys_mode_no_keys_exits(dotenv_file, capsys):
    args = make_args(file=str(dotenv_file), mode="keys", keys=None)
    with pytest.raises(SystemExit) as exc_info:
        cmd_prune(args)
    assert exc_info.value.code == 1


def test_cmd_prune_pattern_prefix(dotenv_file, capsys):
    args = make_args(file=str(dotenv_file), mode="pattern", prefix="TMP_", format="json")
    cmd_prune(args)
    data = json.loads(capsys.readouterr().out)
    assert "TMP_TOKEN" in data["removed"]
    assert data["reason"] == "pattern"


def test_cmd_prune_unknown_mode_exits(dotenv_file, capsys):
    args = make_args(file=str(dotenv_file), mode="bogus")
    with pytest.raises(SystemExit) as exc_info:
        cmd_prune(args)
    assert exc_info.value.code == 1


def test_register_prune_commands_adds_subparser():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()
    register_prune_commands(subparsers)
    args = parser.parse_args(["prune", "/tmp/fake.env", "--mode", "empty"])
    assert args.mode == "empty"
