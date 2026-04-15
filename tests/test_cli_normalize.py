"""Tests for envoy_cfg.cli_normalize."""

import argparse
import json
from io import StringIO
from pathlib import Path

import pytest

from envoy_cfg.cli_normalize import cmd_normalize, register_normalize_commands


@pytest.fixture
def dotenv_file(tmp_path):
    p = tmp_path / ".env"
    p.write_text("app_name=myapp\napi_key=secret\nPORT=8080\n")
    return str(p)


def make_args(**kwargs):
    defaults = dict(
        file=None,
        keys=False,
        values=False,
        no_uppercase=False,
        no_strip=False,
        no_collapse=False,
        format="dotenv",
        verbose=False,
    )
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_cmd_normalize_keys_dotenv_output(dotenv_file, capsys):
    args = make_args(file=dotenv_file, keys=True)
    cmd_normalize(args)
    out = capsys.readouterr().out
    assert "APP_NAME=myapp" in out
    assert "API_KEY=secret" in out


def test_cmd_normalize_keys_json_output(dotenv_file, capsys):
    args = make_args(file=dotenv_file, keys=True, format="json")
    cmd_normalize(args)
    out = capsys.readouterr().out
    data = json.loads(out)
    assert "APP_NAME" in data
    assert data["PORT"] == "8080"


def test_cmd_normalize_values_strips_spaces(tmp_path, capsys):
    p = tmp_path / ".env"
    p.write_text("KEY=  hello  \n")
    args = make_args(file=str(p), values=True)
    cmd_normalize(args)
    out = capsys.readouterr().out
    assert "KEY=hello" in out


def test_cmd_normalize_no_flags_passthrough(dotenv_file, capsys):
    args = make_args(file=dotenv_file)
    cmd_normalize(args)
    out = capsys.readouterr().out
    # Without --keys or --values, original keys passed through
    assert "app_name=myapp" in out


def test_cmd_normalize_verbose_logs_to_stderr(dotenv_file, capsys):
    args = make_args(file=dotenv_file, keys=True, verbose=True)
    cmd_normalize(args)
    err = capsys.readouterr().err
    assert "app_name" in err


def test_register_normalize_commands():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers()
    register_normalize_commands(sub)
    args = parser.parse_args(["normalize", "some.env", "--keys", "--format", "json"])
    assert args.keys is True
    assert args.format == "json"
