"""Tests for envoy_cfg.cli_pipeline."""

import argparse
import json
import pytest
from unittest.mock import patch, MagicMock
from envoy_cfg.cli_pipeline import cmd_pipeline_run, register_pipeline_commands


@pytest.fixture
def dotenv_file(tmp_path):
    p = tmp_path / ".env"
    p.write_text(
        'APP_HOST=localhost\n'
        'DB_PASSWORD=supersecret\n'
        'PORT=9000\n'
    )
    return str(p)


def make_args(**kwargs):
    defaults = {
        "file": "",
        "interpolate": False,
        "mask": False,
        "output_format": "dotenv",
    }
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_cmd_pipeline_run_dotenv_output(dotenv_file, capsys):
    args = make_args(file=dotenv_file)
    cmd_pipeline_run(args)
    out = capsys.readouterr().out
    assert "APP_HOST=localhost" in out


def test_cmd_pipeline_run_json_output(dotenv_file, capsys):
    args = make_args(file=dotenv_file, output_format="json")
    cmd_pipeline_run(args)
    out = capsys.readouterr().out
    data = json.loads(out.split("\n", 2)[-1])
    assert "APP_HOST" in data


def test_cmd_pipeline_run_with_mask(dotenv_file, capsys):
    args = make_args(file=dotenv_file, mask=True)
    cmd_pipeline_run(args)
    out = capsys.readouterr().out
    assert "supersecret" not in out
    assert "DB_PASSWORD" in out


def test_cmd_pipeline_run_steps_listed(dotenv_file, capsys):
    args = make_args(file=dotenv_file, mask=True)
    cmd_pipeline_run(args)
    out = capsys.readouterr().out
    assert "mask" in out


def test_cmd_pipeline_run_error_reported(dotenv_file, capsys):
    args = make_args(file=dotenv_file, mask=True)
    with patch("envoy_cfg.cli_pipeline.mask_env", side_effect=RuntimeError("oops")):
        cmd_pipeline_run(args)
    out = capsys.readouterr().out
    assert "error" in out.lower()


def test_register_pipeline_commands_adds_subparser():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()
    register_pipeline_commands(subparsers)
    args = parser.parse_args(["pipeline", "/dev/null"])
    assert hasattr(args, "func")
