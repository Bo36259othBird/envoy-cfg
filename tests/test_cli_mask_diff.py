"""Tests for envoy_cfg.cli_mask_diff."""
import argparse
import json
import pytest
from pathlib import Path

from envoy_cfg.cli_mask_diff import cmd_mask_diff


@pytest.fixture
def base_file(tmp_path):
    f = tmp_path / "base.env"
    f.write_text(
        "APP_HOST=localhost\n"
        "DB_PASSWORD=secret123\n"
        "APP_PORT=8080\n"
    )
    return str(f)


@pytest.fixture
def updated_file(tmp_path):
    f = tmp_path / "updated.env"
    f.write_text(
        "APP_HOST=prod.example.com\n"
        "DB_PASSWORD=newsecret\n"
        "APP_DEBUG=false\n"
    )
    return str(f)


def make_args(**kwargs):
    defaults = {
        "base": None,
        "updated": None,
        "format": "text",
        "no_mask": False,
        "fail_on_diff": False,
    }
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_cmd_mask_diff_text_output(base_file, updated_file, capsys):
    args = make_args(base=base_file, updated=updated_file)
    cmd_mask_diff(args)
    out = capsys.readouterr().out
    assert "APP_HOST" in out


def test_cmd_mask_diff_json_output(base_file, updated_file, capsys):
    args = make_args(base=base_file, updated=updated_file, format="json")
    cmd_mask_diff(args)
    out = capsys.readouterr().out
    data = json.loads(out)
    assert "entries" in data
    assert "total" in data
    assert "masked_count" in data


def test_cmd_mask_diff_masks_password(base_file, updated_file, capsys):
    args = make_args(base=base_file, updated=updated_file, format="json")
    cmd_mask_diff(args)
    out = capsys.readouterr().out
    data = json.loads(out)
    pw_entries = [e for e in data["entries"] if e["key"] == "DB_PASSWORD"]
    if pw_entries:
        assert pw_entries[0]["masked"] is True
        assert pw_entries[0].get("new_value") != "newsecret"


def test_cmd_mask_diff_no_mask_exposes_secrets(base_file, updated_file, capsys):
    args = make_args(base=base_file, updated=updated_file, format="json", no_mask=True)
    cmd_mask_diff(args)
    out = capsys.readouterr().out
    data = json.loads(out)
    pw_entries = [e for e in data["entries"] if e["key"] == "DB_PASSWORD"]
    if pw_entries:
        assert pw_entries[0]["masked"] is False


def test_cmd_mask_diff_clean_envs_prints_no_diff(base_file, capsys):
    args = make_args(base=base_file, updated=base_file)
    cmd_mask_diff(args)
    out = capsys.readouterr().out
    assert "No differences" in out


def test_cmd_mask_diff_fail_on_diff_exits(base_file, updated_file):
    args = make_args(base=base_file, updated=updated_file, fail_on_diff=True)
    with pytest.raises(SystemExit) as exc:
        cmd_mask_diff(args)
    assert exc.value.code == 1
