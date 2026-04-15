"""Tests for envoy_cfg.cli_group CLI commands."""

import json
import pytest
from pathlib import Path
from unittest.mock import patch
from types import SimpleNamespace

from envoy_cfg.cli_group import cmd_group


@pytest.fixture
def dotenv_file(tmp_path):
    p = tmp_path / ".env"
    p.write_text(
        "DB_HOST=localhost\n"
        "DB_PORT=5432\n"
        "CACHE_HOST=redis\n"
        "CACHE_TTL=300\n"
        "APP_NAME=myapp\n"
    )
    return str(p)


def make_args(**kwargs):
    defaults = {
        "strategy": "prefix",
        "groups": None,
        "patterns": None,
        "separator": "_",
        "strip": False,
        "format": "text",
    }
    defaults.update(kwargs)
    return SimpleNamespace(**defaults)


def test_cmd_group_prefix_text_output(dotenv_file, capsys):
    args = make_args(file=dotenv_file, strategy="prefix", groups=["DB", "CACHE"])
    cmd_group(args)
    out = capsys.readouterr().out
    assert "[DB]" in out
    assert "[CACHE]" in out
    assert "DB_HOST=localhost" in out


def test_cmd_group_prefix_json_output(dotenv_file, capsys):
    args = make_args(file=dotenv_file, strategy="prefix", groups=["DB"], format="json")
    cmd_group(args)
    out = capsys.readouterr().out
    data = json.loads(out)
    assert "groups" in data
    assert "DB" in data["groups"]
    assert "strategy" in data
    assert data["strategy"] == "prefix"


def test_cmd_group_prefix_strip_flag(dotenv_file, capsys):
    args = make_args(file=dotenv_file, strategy="prefix", groups=["DB"], strip=True, format="json")
    cmd_group(args)
    out = capsys.readouterr().out
    data = json.loads(out)
    assert "HOST" in data["groups"]["DB"]
    assert "DB_HOST" not in data["groups"]["DB"]


def test_cmd_group_suffix_strategy(dotenv_file, capsys):
    args = make_args(file=dotenv_file, strategy="suffix", groups=["HOST", "TTL"], format="json")
    cmd_group(args)
    out = capsys.readouterr().out
    data = json.loads(out)
    assert "HOST" in data["groups"]
    assert data["strategy"] == "suffix"


def test_cmd_group_pattern_strategy(dotenv_file, capsys):
    args = make_args(
        file=dotenv_file,
        strategy="pattern",
        patterns=["database=^DB_", "cache=^CACHE_"],
        format="json",
    )
    cmd_group(args)
    out = capsys.readouterr().out
    data = json.loads(out)
    assert "database" in data["groups"]
    assert "cache" in data["groups"]


def test_cmd_group_missing_groups_prints_error(dotenv_file, capsys):
    args = make_args(file=dotenv_file, strategy="prefix", groups=None)
    cmd_group(args)
    out = capsys.readouterr().out
    assert "[error]" in out


def test_cmd_group_unknown_strategy_prints_error(dotenv_file, capsys):
    args = make_args(file=dotenv_file, strategy="unknown")
    cmd_group(args)
    out = capsys.readouterr().out
    assert "[error]" in out


def test_cmd_group_complete_flag_in_json(dotenv_file, capsys):
    args = make_args(
        file=dotenv_file, strategy="prefix", groups=["DB", "CACHE", "APP"], format="json"
    )
    cmd_group(args)
    out = capsys.readouterr().out
    data = json.loads(out)
    assert "complete" in data
