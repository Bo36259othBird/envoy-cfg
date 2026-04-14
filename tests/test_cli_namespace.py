"""Tests for envoy_cfg.cli_namespace CLI commands."""

import argparse
import json
import pytest
from io import StringIO
from unittest.mock import patch

from envoy_cfg.cli_namespace import (
    cmd_namespace_apply,
    cmd_namespace_strip,
    cmd_namespace_extract,
    cmd_namespace_list,
)


@pytest.fixture
def dotenv_file(tmp_path):
    p = tmp_path / ".env"
    p.write_text("DB_HOST=localhost\nDB_PORT=5432\nAPP_DEBUG=true\n")
    return str(p)


def make_args(**kwargs):
    defaults = {"namespace": "prod", "separator": "__", "format": "dotenv"}
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_cmd_namespace_apply_dotenv_output(dotenv_file, capsys):
    args = make_args(file=dotenv_file)
    cmd_namespace_apply(args)
    out = capsys.readouterr().out
    assert "PROD__DB_HOST=localhost" in out
    assert "PROD__DB_PORT=5432" in out


def test_cmd_namespace_apply_json_output(dotenv_file, capsys):
    args = make_args(file=dotenv_file, format="json")
    cmd_namespace_apply(args)
    out = capsys.readouterr().out
    # strip the summary comment line
    json_part = "\n".join(l for l in out.splitlines() if not l.startswith("#"))
    data = json.loads(json_part)
    assert "PROD__DB_HOST" in data


def test_cmd_namespace_apply_reports_count(dotenv_file, capsys):
    args = make_args(file=dotenv_file)
    cmd_namespace_apply(args)
    out = capsys.readouterr().out
    assert "3 key(s)" in out


def test_cmd_namespace_strip_removes_prefix(tmp_path, capsys):
    p = tmp_path / ".env"
    p.write_text("PROD__DB_HOST=localhost\nPROD__DB_PORT=5432\n")
    args = make_args(file=str(p))
    cmd_namespace_strip(args)
    out = capsys.readouterr().out
    assert "DB_HOST=localhost" in out
    assert "2 key(s)" in out


def test_cmd_namespace_extract_filters_keys(tmp_path, capsys):
    p = tmp_path / ".env"
    p.write_text("PROD__DB_HOST=localhost\nSTAGING__DB_HOST=staging\n")
    args = make_args(file=str(p), namespace="prod")
    cmd_namespace_extract(args)
    out = capsys.readouterr().out
    assert "DB_HOST=localhost" in out
    assert "STAGING" not in out


def test_cmd_namespace_list_shows_namespaces(tmp_path, capsys):
    p = tmp_path / ".env"
    p.write_text("PROD__KEY=a\nSTAGING__KEY=b\nNO_NS=c\n")
    args = argparse.Namespace(file=str(p), separator="__")
    cmd_namespace_list(args)
    out = capsys.readouterr().out
    assert "PROD" in out
    assert "STAGING" in out


def test_cmd_namespace_list_no_namespaces(tmp_path, capsys):
    p = tmp_path / ".env"
    p.write_text("KEY=value\n")
    args = argparse.Namespace(file=str(p), separator="__")
    cmd_namespace_list(args)
    out = capsys.readouterr().out
    assert "No namespaces detected" in out
