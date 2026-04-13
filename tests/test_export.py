"""Tests for envoy_cfg.export."""

from __future__ import annotations

import json
import pytest

from envoy_cfg.export import export_dotenv, export_env, export_json, export_shell


SAMPLE_ENV = {
    "APP_NAME": "envoy",
    "DATABASE_URL": "postgres://localhost/db",
    "SECRET_KEY": "supersecret",
    "DEBUG": "true",
}


# ---------------------------------------------------------------------------
# dotenv format
# ---------------------------------------------------------------------------

def test_export_dotenv_sorted_keys():
    output = export_dotenv(SAMPLE_ENV)
    lines = [l for l in output.splitlines() if l]
    keys = [l.split("=")[0] for l in lines]
    assert keys == sorted(keys)


def test_export_dotenv_quoted_values():
    output = export_dotenv({"FOO": "bar baz"})
    assert 'FOO="bar baz"' in output


def test_export_dotenv_escapes_double_quotes():
    output = export_dotenv({"MSG": 'say "hi"'})
    assert 'MSG="say \\"hi\\""' in output


def test_export_dotenv_masks_secrets():
    output = export_dotenv(SAMPLE_ENV, mask_secrets=True)
    assert "supersecret" not in output
    assert "SECRET_KEY" in output


def test_export_dotenv_empty_env():
    assert export_dotenv({}) == ""


# ---------------------------------------------------------------------------
# JSON format
# ---------------------------------------------------------------------------

def test_export_json_valid_json():
    output = export_json(SAMPLE_ENV)
    parsed = json.loads(output)
    assert parsed["APP_NAME"] == "envoy"
    assert parsed["DEBUG"] == "true"


def test_export_json_masks_secrets():
    output = export_json(SAMPLE_ENV, mask_secrets=True)
    parsed = json.loads(output)
    assert "supersecret" not in parsed["SECRET_KEY"]


# ---------------------------------------------------------------------------
# shell format
# ---------------------------------------------------------------------------

def test_export_shell_export_prefix():
    output = export_shell({"FOO": "bar"})
    assert output.strip() == "export FOO='bar'"


def test_export_shell_escapes_single_quotes():
    output = export_shell({"MSG": "it's alive"})
    assert "it'\\''s alive" in output


def test_export_shell_masks_secrets():
    output = export_shell(SAMPLE_ENV, mask_secrets=True)
    assert "supersecret" not in output


# ---------------------------------------------------------------------------
# export_env dispatcher
# ---------------------------------------------------------------------------

def test_export_env_dotenv():
    result = export_env(SAMPLE_ENV, fmt="dotenv")
    assert "APP_NAME=" in result


def test_export_env_json():
    result = export_env(SAMPLE_ENV, fmt="json")
    assert json.loads(result)["DEBUG"] == "true"


def test_export_env_shell():
    result = export_env(SAMPLE_ENV, fmt="shell")
    assert result.startswith("export ")


def test_export_env_invalid_format_raises():
    with pytest.raises(ValueError, match="Unsupported format"):
        export_env(SAMPLE_ENV, fmt="xml")


def test_export_env_writes_file(tmp_path):
    out_file = tmp_path / "config.env"
    export_env(SAMPLE_ENV, fmt="dotenv", output_path=str(out_file))
    assert out_file.exists()
    assert "APP_NAME" in out_file.read_text()
