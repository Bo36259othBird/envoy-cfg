"""Tests for envoy_cfg.cli_patch."""

import argparse
import json
from pathlib import Path

import pytest

from envoy_cfg.cli_patch import cmd_patch, register_patch_commands


@pytest.fixture
def dotenv_file(tmp_path):
    p = tmp_path / ".env"
    p.write_text("APP_HOST=localhost\nAPP_PORT=8080\nDB_PASS=secret\n")
    return str(p)


def make_args(file, set_ops=None, delete_ops=None, rename_ops=None, fmt="dotenv"):
    ns = argparse.Namespace(
        file=file,
        set=set_ops,
        delete=delete_ops,
        rename=rename_ops,
        format=fmt,
    )
    return ns


def test_cmd_patch_set_key_dotenv_output(dotenv_file, capsys):
    args = make_args(dotenv_file, set_ops=["NEW_KEY=hello"])
    cmd_patch(args)
    out = capsys.readouterr().out
    assert "NEW_KEY=hello" in out


def test_cmd_patch_delete_key_dotenv_output(dotenv_file, capsys):
    args = make_args(dotenv_file, delete_ops=["DB_PASS"])
    cmd_patch(args)
    out = capsys.readouterr().out
    assert "DB_PASS" not in out


def test_cmd_patch_rename_key_dotenv_output(dotenv_file, capsys):
    args = make_args(dotenv_file, rename_ops=["APP_HOST:SERVICE_HOST"])
    cmd_patch(args)
    out = capsys.readouterr().out
    assert "SERVICE_HOST=localhost" in out
    assert "APP_HOST=" not in out.split("#")[0]


def test_cmd_patch_json_output(dotenv_file, capsys):
    args = make_args(dotenv_file, set_ops=["APP_PORT=9090"], fmt="json")
    cmd_patch(args)
    out = capsys.readouterr().out
    data = json.loads(out.split("\n# ")[0])
    assert data["APP_PORT"] == "9090"


def test_cmd_patch_bad_set_warns(dotenv_file, capsys):
    args = make_args(dotenv_file, set_ops=["NOEQUALS"])
    cmd_patch(args)
    out = capsys.readouterr().out
    assert "warn" in out


def test_cmd_patch_bad_rename_warns(dotenv_file, capsys):
    args = make_args(dotenv_file, rename_ops=["NOCOLON"])
    cmd_patch(args)
    out = capsys.readouterr().out
    assert "warn" in out


def test_cmd_patch_skipped_shown_in_output(dotenv_file, capsys):
    args = make_args(dotenv_file, delete_ops=["DOES_NOT_EXIST"])
    cmd_patch(args)
    out = capsys.readouterr().out
    assert "skipped" in out


def test_register_patch_commands():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()
    register_patch_commands(subparsers)
    args = parser.parse_args(["patch", "/dev/null"])
    assert hasattr(args, "func")
