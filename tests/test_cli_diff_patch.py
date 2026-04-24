"""Tests for envoy_cfg.cli_diff_patch CLI commands."""
import argparse
import json
import sys
from pathlib import Path

import pytest

from envoy_cfg.cli_diff_patch import cmd_diff_patch_build, cmd_diff_patch_apply
from envoy_cfg.diff_patch import DiffPatch, DiffPatchEntry


@pytest.fixture
def base_file(tmp_path):
    p = tmp_path / "base.env"
    p.write_text("APP_HOST=localhost\nAPP_PORT=8080\nDB_PASS=secret\n")
    return str(p)


@pytest.fixture
def updated_file(tmp_path):
    p = tmp_path / "updated.env"
    p.write_text("APP_HOST=prod.example.com\nAPP_PORT=8080\nNEW_KEY=value\n")
    return str(p)


@pytest.fixture
def patch_file(tmp_path, base_file, updated_file):
    from envoy_cfg.diff_patch import build_patch

    def _load(path):
        env = {}
        with open(path) as fh:
            for line in fh:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    k, _, v = line.partition("=")
                    env[k.strip()] = v.strip()
        return env

    patch = build_patch(_load(base_file), _load(updated_file))
    p = tmp_path / "patch.json"
    p.write_text(json.dumps(patch.to_dict()))
    return str(p)


def make_args(**kwargs):
    ns = argparse.Namespace(
        base=None,
        updated=None,
        output=None,
        env=None,
        patch=None,
        strict=False,
        format="dotenv",
    )
    for k, v in kwargs.items():
        setattr(ns, k, v)
    return ns


def test_cmd_diff_patch_build_prints_json(base_file, updated_file, capsys):
    args = make_args(base=base_file, updated=updated_file)
    cmd_diff_patch_build(args)
    out = capsys.readouterr().out
    data = json.loads(out)
    assert "entries" in data
    assert len(data["entries"]) > 0


def test_cmd_diff_patch_build_writes_to_file(base_file, updated_file, tmp_path):
    out_path = str(tmp_path / "out.json")
    args = make_args(base=base_file, updated=updated_file, output=out_path)
    cmd_diff_patch_build(args)
    data = json.loads(Path(out_path).read_text())
    assert "entries" in data


def test_cmd_diff_patch_apply_dotenv_output(base_file, patch_file, capsys):
    args = make_args(env=base_file, patch=patch_file, format="dotenv")
    cmd_diff_patch_apply(args)
    out = capsys.readouterr().out
    assert "APP_HOST=prod.example.com" in out


def test_cmd_diff_patch_apply_json_output(base_file, patch_file, capsys):
    args = make_args(env=base_file, patch=patch_file, format="json")
    cmd_diff_patch_apply(args)
    out = capsys.readouterr().out
    data = json.loads(out)
    assert data["APP_HOST"] == "prod.example.com"


def test_cmd_diff_patch_apply_strict_conflict_exits(base_file, tmp_path, capsys):
    conflict_patch = DiffPatch(
        entries=[DiffPatchEntry("APP_HOST", "add", None, "conflict")]
    )
    p = tmp_path / "conflict.json"
    p.write_text(json.dumps(conflict_patch.to_dict()))
    args = make_args(env=base_file, patch=str(p), strict=True)
    with pytest.raises(SystemExit) as exc_info:
        cmd_diff_patch_apply(args)
    assert exc_info.value.code == 1
