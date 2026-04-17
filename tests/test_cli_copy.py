import argparse
import json
from pathlib import Path
import pytest
from envoy_cfg.cli_copy import cmd_copy


@pytest.fixture
def source_file(tmp_path):
    f = tmp_path / "source.env"
    f.write_text("DB_HOST=localhost\nDB_PORT=5432\nDEBUG=true\n")
    return str(f)


@pytest.fixture
def dest_file(tmp_path):
    f = tmp_path / "dest.env"
    f.write_text("APP_NAME=myapp\nDB_HOST=prod-host\n")
    return str(f)


def make_args(**kwargs):
    defaults = dict(overwrite=False, prefix="", format="dotenv", quiet=True)
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_cmd_copy_dotenv_output(source_file, dest_file, capsys):
    args = make_args(source=source_file, dest=dest_file, keys=["DEBUG"])
    cmd_copy(args)
    out = capsys.readouterr().out
    assert "DEBUG=true" in out


def test_cmd_copy_json_output(source_file, dest_file, capsys):
    args = make_args(source=source_file, dest=dest_file, keys=["DEBUG", "DB_PORT"], format="json")
    cmd_copy(args)
    out = capsys.readouterr().out
    data = json.loads(out)
    assert "DEBUG" in data
    assert "DB_PORT" in data


def test_cmd_copy_skip_existing(source_file, dest_file, capsys):
    args = make_args(source=source_file, dest=dest_file, keys=["DB_HOST"])
    cmd_copy(args)
    out = capsys.readouterr().out
    assert "DB_HOST" not in out


def test_cmd_copy_overwrite_flag(source_file, dest_file, capsys):
    args = make_args(source=source_file, dest=dest_file, keys=["DB_HOST"], overwrite=True)
    cmd_copy(args)
    out = capsys.readouterr().out
    assert "DB_HOST=localhost" in out


def test_cmd_copy_with_prefix(source_file, dest_file, capsys):
    args = make_args(source=source_file, dest=dest_file, keys=["DEBUG"], prefix="NEW_")
    cmd_copy(args)
    out = capsys.readouterr().out
    assert "NEW_DEBUG=true" in out
