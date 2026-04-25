"""Tests for envoy_cfg.cli_unique."""

from __future__ import annotations

import json
from argparse import Namespace
from pathlib import Path

import pytest

from envoy_cfg.cli_unique import cmd_unique


@pytest.fixture
def dotenv_file(tmp_path: Path) -> Path:
    f = tmp_path / ".env"
    f.write_text(
        "DB_HOST=localhost\n"
        "CACHE_HOST=localhost\n"
        "APP_ENV=production\n"
        "PORT=8080\n"
    )
    return f


def make_args(file: str, **kwargs) -> Namespace:
    defaults = {"format": "text", "ignore_case": False, "include_empty": False}
    defaults.update(kwargs)
    return Namespace(file=file, **defaults)


def test_cmd_unique_text_clean(tmp_path: Path, capsys):
    f = tmp_path / ".env"
    f.write_text("A=1\nB=2\nC=3\n")
    cmd_unique(make_args(str(f)))
    out = capsys.readouterr().out
    assert "All values are unique" in out


def test_cmd_unique_text_shows_duplicates(dotenv_file: Path, capsys):
    cmd_unique(make_args(str(dotenv_file)))
    out = capsys.readouterr().out
    assert "localhost" in out
    assert "CACHE_HOST" in out
    assert "DB_HOST" in out


def test_cmd_unique_json_output(dotenv_file: Path, capsys):
    cmd_unique(make_args(str(dotenv_file), format="json"))
    out = capsys.readouterr().out
    data = json.loads(out)
    assert "duplicate_values" in data
    assert "is_clean" in data
    assert data["is_clean"] is False


def test_cmd_unique_json_clean(tmp_path: Path, capsys):
    f = tmp_path / ".env"
    f.write_text("X=alpha\nY=beta\n")
    cmd_unique(make_args(str(f), format="json"))
    data = json.loads(capsys.readouterr().out)
    assert data["is_clean"] is True
    assert data["shared_count"] == 0


def test_cmd_unique_stderr_summary(dotenv_file: Path, capsys):
    cmd_unique(make_args(str(dotenv_file)))
    err = capsys.readouterr().err
    assert "key(s) share values" in err


def test_cmd_unique_ignore_case(tmp_path: Path, capsys):
    f = tmp_path / ".env"
    f.write_text("A=Hello\nB=hello\n")
    cmd_unique(make_args(str(f), ignore_case=True, format="json"))
    data = json.loads(capsys.readouterr().out)
    assert data["is_clean"] is False
