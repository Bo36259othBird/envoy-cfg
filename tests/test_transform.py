"""Tests for envoy_cfg.transform."""

import pytest
from envoy_cfg.transform import (
    TransformResult,
    apply_transforms,
    transform_keys,
    transform_values,
)


@pytest.fixture
def base_env():
    return {
        "app_host": "  localhost  ",
        "APP_PORT": "8080",
        "Debug": "True",
    }


# --- transform_keys ---

def test_transform_keys_upper(base_env):
    result = transform_keys(base_env, str.upper, label="keys_upper")
    assert "APP_HOST" in result.transformed
    assert "APP_PORT" in result.transformed
    assert "DEBUG" in result.transformed


def test_transform_keys_preserves_values(base_env):
    result = transform_keys(base_env, str.upper)
    assert result.transformed["APP_HOST"] == "  localhost  "


def test_transform_keys_lower(base_env):
    result = transform_keys(base_env, str.lower, label="keys_lower")
    assert "app_port" in result.transformed
    assert "debug" in result.transformed


def test_transform_keys_records_label(base_env):
    result = transform_keys(base_env, str.upper, label="my_step")
    assert "my_step" in result.applied


# --- transform_values ---

def test_transform_values_strip(base_env):
    result = transform_values(base_env, lambda k, v: v.strip(), label="values_strip")
    assert result.transformed["app_host"] == "localhost"


def test_transform_values_limited_to_keys(base_env):
    result = transform_values(
        base_env,
        lambda k, v: v.strip(),
        keys=["app_host"],
    )
    # Only app_host stripped; APP_PORT untouched
    assert result.transformed["app_host"] == "localhost"
    assert result.transformed["APP_PORT"] == "8080"


def test_transform_values_upper(base_env):
    result = transform_values(base_env, lambda k, v: v.upper())
    assert result.transformed["Debug"] == "TRUE"


def test_transform_values_records_label(base_env):
    result = transform_values(base_env, lambda k, v: v, label="noop")
    assert "noop" in result.applied


# --- is_identity ---

def test_is_identity_true_when_unchanged():
    env = {"A": "1"}
    result = transform_keys(env, lambda k: k)  # identity
    assert result.is_identity


def test_is_identity_false_when_changed(base_env):
    result = transform_keys(base_env, str.upper)
    assert not result.is_identity


# --- apply_transforms ---

def test_apply_transforms_keys_upper(base_env):
    result = apply_transforms(base_env, [{"type": "keys_upper"}])
    assert "APP_HOST" in result.transformed
    assert "DEBUG" in result.transformed


def test_apply_transforms_values_strip(base_env):
    result = apply_transforms(base_env, [{"type": "values_strip"}])
    assert result.transformed["app_host"] == "localhost"


def test_apply_transforms_chained(base_env):
    result = apply_transforms(
        base_env,
        [{"type": "keys_upper"}, {"type": "values_strip"}, {"type": "values_lower"}],
    )
    assert result.transformed["APP_HOST"] == "localhost"
    assert result.transformed["DEBUG"] == "true"
    assert set(result.applied) == {"keys_upper", "values_strip", "values_lower"}


def test_apply_transforms_unknown_type_raises(base_env):
    with pytest.raises(ValueError, match="Unknown transform type"):
        apply_transforms(base_env, [{"type": "explode"}])


def test_apply_transforms_original_unchanged(base_env):
    original_copy = dict(base_env)
    apply_transforms(base_env, [{"type": "keys_upper"}])
    assert base_env == original_copy
