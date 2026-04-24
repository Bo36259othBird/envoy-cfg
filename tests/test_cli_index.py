"""Tests for envoy_cfg.cli_index CLI commands."""
from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from envoy_cfg.cli_index import cmd_index_lookup, cmd_index_search


@pytest.fixture()
def dotenv_file(tmp_path: Path) -> Path:
    p = tmp_path / ".env"
    p.write_text(
        "APP_HOST=localhost\n"
        "APP_PORT=8080\n"
        "DB_URL=postgres://localhost/mydb\n"
        "SECRET_KEY=s3cr3t\n"
    )
    return p


def make_args(**kwargs):
    defaults = {"format": "text", "ignore_case": False, "by": "key"}
    defaults.update(kwargs)
    return SimpleNamespace(**defaults)


def test_cmd_lookup_prints_value(dotenv_file, capsys):
    args = make_args(file=str(dotenv_file), key="APP_HOST")
    cmd_index_lookup(args)
    out = capsys.readouterr().out.strip()
    assert out == "localhost"


def test_cmd_lookup_missing_key_exits(dotenv_file):
    args = make_args(file=str(dotenv_file), key="MISSING")
    with pytest.raises(SystemExit) as exc:
        cmd_index_lookup(args)
    assert exc.value.code == 1


def test_cmd_lookup_ignore_case(dotenv_file, capsys):
    args = make_args(file=str(dotenv_file), key="app_host", ignore_case=True)
    cmd_index_lookup(args)
    out = capsys.readouterr().out.strip()
    assert out == "localhost"


def test_cmd_search_keys_text(dotenv_file, capsys):
    args = make_args(file=str(dotenv_file), pattern="APP_*", by="key")
    cmd_index_search(args)
    out = capsys.readouterr().out
    assert "APP_HOST" in out
    assert "APP_PORT" in out
    assert "DB_URL" not in out


def test_cmd_search_keys_json(dotenv_file, capsys):
    args = make_args(file=str(dotenv_file), pattern="APP_*", by="key", format="json")
    cmd_index_search(args)
    data = json.loads(capsys.readouterr().out)
    assert isinstance(data, list)
    assert "APP_HOST" in data


def test_cmd_search_values_text(dotenv_file, capsys):
    args = make_args(file=str(dotenv_file), pattern="*localhost*", by="value")
    cmd_index_search(args)
    out = capsys.readouterr().out
    assert "APP_HOST" in out
    assert "DB_URL" in out


def test_cmd_search_values_json(dotenv_file, capsys):
    args = make_args(
        file=str(dotenv_file), pattern="*localhost*", by="value", format="json"
    )
    cmd_index_search(args)
    data = json.loads(capsys.readouterr().out)
    assert isinstance(data, dict)
    assert "APP_HOST" in data
