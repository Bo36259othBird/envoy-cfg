"""Tests for envoy_cfg.schema."""

from __future__ import annotations

import pytest
from envoy_cfg.schema import EnvSchema, SchemaField


@pytest.fixture
def simple_schema() -> EnvSchema:
    schema = EnvSchema(name="test-schema")
    schema.add_field(SchemaField(key="DATABASE_URL", required=True))
    schema.add_field(SchemaField(key="SECRET_KEY", required=True))
    schema.add_field(SchemaField(key="DEBUG", required=False, default="false"))
    return schema


def test_schema_field_to_dict_roundtrip():
    f = SchemaField(key="API_KEY", required=True, default=None, description="API key")
    restored = SchemaField.from_dict(f.to_dict())
    assert restored.key == f.key
    assert restored.required == f.required
    assert restored.default == f.default
    assert restored.description == f.description


def test_schema_to_dict_roundtrip(simple_schema):
    restored = EnvSchema.from_dict(simple_schema.to_dict())
    assert restored.name == simple_schema.name
    assert len(restored.fields) == len(simple_schema.fields)
    assert restored.fields[0].key == "DATABASE_URL"


def test_validate_passes_with_all_required_keys(simple_schema):
    env = {"DATABASE_URL": "postgres://localhost/db", "SECRET_KEY": "abc123"}
    errors = simple_schema.validate(env)
    assert errors == []


def test_validate_fails_missing_required_key(simple_schema):
    env = {"DATABASE_URL": "postgres://localhost/db"}
    errors = simple_schema.validate(env)
    assert any("SECRET_KEY" in e for e in errors)


def test_validate_optional_key_not_required(simple_schema):
    env = {"DATABASE_URL": "postgres://localhost/db", "SECRET_KEY": "abc123"}
    errors = simple_schema.validate(env)
    assert not any("DEBUG" in e for e in errors)


def test_validate_reports_unexpected_keys(simple_schema):
    env = {
        "DATABASE_URL": "postgres://localhost/db",
        "SECRET_KEY": "abc123",
        "UNKNOWN_KEY": "oops",
    }
    errors = simple_schema.validate(env)
    assert any("UNKNOWN_KEY" in e for e in errors)


def test_apply_defaults_fills_missing_optional(simple_schema):
    env = {"DATABASE_URL": "postgres://localhost/db", "SECRET_KEY": "abc123"}
    result = simple_schema.apply_defaults(env)
    assert result["DEBUG"] == "false"


def test_apply_defaults_does_not_overwrite_existing(simple_schema):
    env = {"DATABASE_URL": "postgres://localhost/db", "SECRET_KEY": "abc123", "DEBUG": "true"}
    result = simple_schema.apply_defaults(env)
    assert result["DEBUG"] == "true"


def test_apply_defaults_returns_copy(simple_schema):
    env = {"DATABASE_URL": "x", "SECRET_KEY": "y"}
    result = simple_schema.apply_defaults(env)
    assert result is not env


def test_validate_with_default_does_not_error_when_missing(simple_schema):
    """A field with a default should not raise a missing-required error."""
    env = {"DATABASE_URL": "postgres://localhost/db", "SECRET_KEY": "abc123"}
    errors = simple_schema.validate(env)
    required_errors = [e for e in errors if "Missing required" in e]
    assert all("DEBUG" not in e for e in required_errors)
