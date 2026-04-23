import argparse
import json
from pathlib import Path
import pytest
from envoy_cfg.cli_prefix import cmd_prefix_add, cmd_prefix_remove


@pytest.fixture
def dotenv_file(tmp_path):
    p = tmp_path / ".env"
    p.write_text(
        "APP_HOST=localhost\n"
        "APP_PORT=8080\n"
        "DB_URL=postgres://localhost/db\n"
    )
    return str(p)


def make_args(**kwargs) -> argparse.Namespace:
    defaults = {
        "file": "",
        "prefix": "",
        "keys": None,
        "no_skip": False,
        "format": "dotenv",
    }
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_cmd_prefix_add_dotenv_output(dotenv_file, capsys):
    args = make_args(file=dotenv_file, prefix="TEST_")
    cmd_prefix_add(args)
    out = capsys.readouterr().out
    assert "TEST_APP_HOST=localhost" in out
    assert "TEST_APP_PORT=8080" in out


def test_cmd_prefix_add_json_output(dotenv_file, capsys):
    args = make_args(file=dotenv_file, prefix="TEST_", format="json")
    cmd_prefix_add(args)
    out = capsys.readouterr().out
    data = json.loads(out)
    assert "TEST_APP_HOST" in data
    assert data["TEST_APP_HOST"] == "localhost"


def test_cmd_prefix_add_stderr_summary(dotenv_file, capsys):
    args = make_args(file=dotenv_file, prefix="P_")
    cmd_prefix_add(args)
    err = capsys.readouterr().err
    assert "affected=" in err
    assert "skipped=" in err


def test_cmd_prefix_add_subset_keys(dotenv_file, capsys):
    args = make_args(file=dotenv_file, prefix="X_", keys="APP_HOST")
    cmd_prefix_add(args)
    out = capsys.readouterr().out
    assert "X_APP_HOST=localhost" in out
    assert "APP_PORT=8080" in out  # untouched


def test_cmd_prefix_remove_dotenv_output(tmp_path, capsys):
    p = tmp_path / ".env"
    p.write_text("PRE_HOST=localhost\nPRE_PORT=8080\n")
    args = make_args(file=str(p), prefix="PRE_")
    cmd_prefix_remove(args)
    out = capsys.readouterr().out
    assert "HOST=localhost" in out
    assert "PORT=8080" in out


def test_cmd_prefix_remove_json_output(tmp_path, capsys):
    p = tmp_path / ".env"
    p.write_text("PRE_HOST=localhost\nOTHER=value\n")
    args = make_args(file=str(p), prefix="PRE_", format="json")
    cmd_prefix_remove(args)
    out = capsys.readouterr().out
    data = json.loads(out)
    assert "HOST" in data
    assert "OTHER" in data
