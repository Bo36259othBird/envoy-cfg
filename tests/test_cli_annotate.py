"""Tests for envoy_cfg.cli_annotate CLI commands."""
import argparse
import json
from pathlib import Path
from io import StringIO
import pytest

from envoy_cfg.cli_annotate import cmd_annotate_apply, cmd_annotate_strip, cmd_annotate_get


@pytest.fixture
def dotenv_file(tmp_path):
    p = tmp_path / ".env"
    p.write_text("APP_HOST=localhost\nAPP_PORT=8080\nSECRET_KEY=abc123\n")
    return str(p)


def make_args(**kwargs):
    defaults = {
        "file": None,
        "annotation": [],
        "overwrite": False,
        "format": "dotenv",
        "keys": None,
        "key": None,
    }
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_cmd_annotate_apply_dotenv_output(dotenv_file, capsys):
    args = make_args(file=dotenv_file, annotation=["APP_HOST=The hostname"])
    cmd_annotate_apply(args)
    out = capsys.readouterr().out
    assert "APP_HOST=localhost" in out
    assert "The hostname" in out


def test_cmd_annotate_apply_json_output(dotenv_file, capsys):
    args = make_args(
        file=dotenv_file,
        annotation=["APP_PORT=Port number"],
        format="json",
    )
    cmd_annotate_apply(args)
    out = capsys.readouterr().out
    # strip trailing summary line before parsing json
    json_part = "\n".join(
        line for line in out.splitlines() if not line.startswith("#")
    )
    data = json.loads(json_part)
    assert "env" in data
    assert "annotations" in data
    assert data["annotations"]["APP_PORT"] == "Port number"


def test_cmd_annotate_apply_reports_count(dotenv_file, capsys):
    args = make_args(
        file=dotenv_file,
        annotation=["APP_HOST=h", "APP_PORT=p"],
    )
    cmd_annotate_apply(args)
    out = capsys.readouterr().out
    assert "annotated: 2" in out


def test_cmd_annotate_apply_no_annotations_reports_zero(dotenv_file, capsys):
    args = make_args(file=dotenv_file, annotation=[])
    cmd_annotate_apply(args)
    out = capsys.readouterr().out
    assert "annotated: 0" in out


def test_cmd_annotate_strip_removes_all(dotenv_file, capsys):
    args = make_args(file=dotenv_file, keys=None, format="text")
    cmd_annotate_strip(args)
    out = capsys.readouterr().out
    assert "removed: 3" in out


def test_cmd_annotate_strip_json_output(dotenv_file, capsys):
    args = make_args(file=dotenv_file, keys=["APP_HOST"], format="json")
    cmd_annotate_strip(args)
    out = capsys.readouterr().out
    json_part = "\n".join(
        line for line in out.splitlines() if not line.startswith("#")
    )
    data = json.loads(json_part)
    assert "APP_HOST" not in data


def test_cmd_annotate_get_existing_key(dotenv_file, capsys):
    args = make_args(
        file=dotenv_file,
        key="APP_HOST",
        annotation=["APP_HOST=The main host"],
    )
    cmd_annotate_get(args)
    out = capsys.readouterr().out
    assert "The main host" in out


def test_cmd_annotate_get_missing_annotation(dotenv_file, capsys):
    args = make_args(file=dotenv_file, key="APP_PORT", annotation=[])
    cmd_annotate_get(args)
    out = capsys.readouterr().out
    assert "no annotation" in out
