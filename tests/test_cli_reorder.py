"""Tests for envoy_cfg.cli_reorder."""
import argparse
import json
from pathlib import Path

import pytest

from envoy_cfg.cli_reorder import cmd_reorder, register_reorder_commands


@pytest.fixture()
def dotenv_file(tmp_path: Path) -> Path:
    p = tmp_path / ".env"
    p.write_text(
        "ZEBRA=1\n"
        "APP_NAME=myapp\n"
        "DB_PASSWORD=s3cr3t\n"
        "APP_ENV=prod\n"
        "API_KEY=abc\n"
    )
    return p


def make_args(**kwargs) -> argparse.Namespace:
    defaults = {
        "strategy": "alpha",
        "reverse": False,
        "prefixes": "",
        "format": "dotenv",
        "summary": False,
    }
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_cmd_reorder_alpha_dotenv_output(dotenv_file, capsys):
    args = make_args(file=str(dotenv_file))
    cmd_reorder(args)
    out = capsys.readouterr().out
    lines = [l for l in out.splitlines() if "=" in l]
    keys = [l.split("=")[0] for l in lines]
    assert keys == sorted(keys)


def test_cmd_reorder_alpha_json_output(dotenv_file, capsys):
    args = make_args(file=str(dotenv_file), format="json")
    cmd_reorder(args)
    out = capsys.readouterr().out
    data = json.loads(out)
    assert list(data.keys()) == sorted(data.keys())


def test_cmd_reorder_reverse_order(dotenv_file, capsys):
    args = make_args(file=str(dotenv_file), reverse=True)
    cmd_reorder(args)
    out = capsys.readouterr().out
    lines = [l for l in out.splitlines() if "=" in l]
    keys = [l.split("=")[0] for l in lines]
    assert keys == sorted(keys, reverse=True)


def test_cmd_reorder_prefix_strategy(dotenv_file, capsys):
    args = make_args(file=str(dotenv_file), strategy="prefix", prefixes="APP_,DB_")
    cmd_reorder(args)
    out = capsys.readouterr().out
    lines = [l for l in out.splitlines() if "=" in l]
    keys = [l.split("=")[0] for l in lines]
    app_pos = [i for i, k in enumerate(keys) if k.startswith("APP_")]
    db_pos = [i for i, k in enumerate(keys) if k.startswith("DB_")]
    assert max(app_pos) < min(db_pos)


def test_cmd_reorder_secrets_last(dotenv_file, capsys):
    args = make_args(file=str(dotenv_file), strategy="secrets-last")
    cmd_reorder(args)
    out = capsys.readouterr().out
    lines = [l for l in out.splitlines() if "=" in l]
    keys = [l.split("=")[0] for l in lines]
    # DB_PASSWORD and API_KEY should appear after non-secret keys
    non_secret = [k for k in keys if k not in ("DB_PASSWORD", "API_KEY")]
    for sk in ("DB_PASSWORD", "API_KEY"):
        if sk in keys:
            assert keys.index(sk) >= len(non_secret)


def test_cmd_reorder_unknown_strategy_exits(dotenv_file):
    args = make_args(file=str(dotenv_file), strategy="unknown")
    with pytest.raises(SystemExit):
        cmd_reorder(args)


def test_register_reorder_commands():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers()
    register_reorder_commands(sub)
    parsed = parser.parse_args(["reorder", "/fake.env", "--strategy", "alpha"])
    assert parsed.strategy == "alpha"
