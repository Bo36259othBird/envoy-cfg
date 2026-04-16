"""Tests for envoy_cfg.cli_crossref."""
import argparse
import json
from pathlib import Path
import pytest
from envoy_cfg.cli_crossref import cmd_crossref


@pytest.fixture
def env_files(tmp_path):
    a = tmp_path / "prod.env"
    b = tmp_path / "dev.env"
    a.write_text("DB_HOST=prod\nDB_PASS=secret\nAPP_PORT=443\n")
    b.write_text("DB_HOST=localhost\nDEBUG=true\nAPP_PORT=8080\n")
    return str(a), str(b)


def make_args(files, fmt="text"):
    ns = argparse.Namespace()
    ns.files = list(files)
    ns.format = fmt
    return ns


def test_cmd_crossref_text_output(env_files, capsys):
    cmd_crossref(make_args(env_files))
    out = capsys.readouterr().out
    assert "DB_HOST" in out
    assert "Common keys" in out


def test_cmd_crossref_json_output(env_files, capsys):
    cmd_crossref(make_args(env_files, fmt="json"))
    out = capsys.readouterr().out
    data = json.loads(out)
    assert "common" in data
    assert "DB_HOST" in data["common"]


def test_cmd_crossref_inconsistent_status(env_files, capsys):
    cmd_crossref(make_args(env_files))
    out = capsys.readouterr().out
    assert "inconsistent" in out


def test_cmd_crossref_consistent_status(tmp_path, capsys):
    a = tmp_path / "a.env"
    b = tmp_path / "b.env"
    a.write_text("X=1\nY=2\n")
    b.write_text("X=3\nY=4\n")
    cmd_crossref(make_args([str(a), str(b)]))
    out = capsys.readouterr().out
    assert "consistent" in out


def test_cmd_crossref_single_file_error(env_files, capsys):
    cmd_crossref(make_args([env_files[0]]))
    out = capsys.readouterr().out
    assert "ERROR" in out
