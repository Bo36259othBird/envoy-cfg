"""Tests for envoy_cfg.cli_omit."""

from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from envoy_cfg.cli_omit import cmd_omit


@pytest.fixture
def dotenv_file(tmp_path: Path) -> Path:
    p = tmp_path / ".env"
    p.write_text(
        "APP_NAME=myapp\n"
        "APP_VERSION=1.0\n"
        "DB_HOST=localhost\n"
        "DB_PASSWORD=secret\n"
        "DEBUG=true\n"
    )
    return p


def make_args(file: str, mode: str, targets: list, fmt: str = "dotenv") -> SimpleNamespace:
    return SimpleNamespace(file=file, mode=mode, targets=targets, format=fmt)


def test_cmd_omit_keys_dotenv_output(dotenv_file, capsys):
    cmd_omit(make_args(str(dotenv_file), "keys", ["DEBUG"]))
    out = capsys.readouterr().out
    assert "DEBUG" not in out
    assert "APP_NAME=myapp" in out


def test_cmd_omit_keys_json_output(dotenv_file, capsys):
    cmd_omit(make_args(str(dotenv_file), "keys", ["DEBUG"], fmt="json"))
    out = capsys.readouterr().out
    data = json.loads(out)
    assert "DEBUG" not in data
    assert data["APP_NAME"] == "myapp"


def test_cmd_omit_prefix_removes_db_keys(dotenv_file, capsys):
    cmd_omit(make_args(str(dotenv_file), "prefix", ["DB_"]))
    out = capsys.readouterr().out
    assert "DB_HOST" not in out
    assert "DB_PASSWORD" not in out
    assert "APP_NAME" in out


def test_cmd_omit_glob_removes_app_keys(dotenv_file, capsys):
    cmd_omit(make_args(str(dotenv_file), "glob", ["APP_*"]))
    out = capsys.readouterr().out
    assert "APP_NAME" not in out
    assert "APP_VERSION" not in out
    assert "DEBUG=true" in out


def test_cmd_omit_reports_count_to_stderr(dotenv_file, capsys):
    cmd_omit(make_args(str(dotenv_file), "prefix", ["DB_"]))
    err = capsys.readouterr().err
    assert "2" in err
    assert "prefix" in err


def test_cmd_omit_unknown_mode_exits(dotenv_file):
    with pytest.raises(SystemExit):
        cmd_omit(make_args(str(dotenv_file), "invalid", ["X"]))


def test_cmd_omit_prefix_no_targets_exits(dotenv_file):
    with pytest.raises(SystemExit):
        cmd_omit(make_args(str(dotenv_file), "prefix", []))


def test_cmd_omit_glob_no_targets_exits(dotenv_file):
    with pytest.raises(SystemExit):
        cmd_omit(make_args(str(dotenv_file), "glob", []))
