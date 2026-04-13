"""Integration tests: pipeline wired with real masking and interpolation."""

import pytest
from envoy_cfg.pipeline import EnvPipeline
from envoy_cfg.masking import mask_env


@pytest.fixture
def rich_env():
    return {
        "APP_URL": "http://${APP_HOST}:${PORT}",
        "APP_HOST": "example.com",
        "PORT": "443",
        "API_SECRET": "topsecret",
        "DB_PASSWORD": "hunter2",
    }


def _interp_step(env):
    from envoy_cfg.interpolate import interpolate_env
    return interpolate_env(env).env


def test_interpolate_then_mask(rich_env):
    pipeline = EnvPipeline()
    pipeline.add_step("interpolate", _interp_step)
    pipeline.add_step("mask", mask_env)
    result = pipeline.run(rich_env)

    assert result.success
    assert result.steps_applied == ["interpolate", "mask"]
    # secrets masked
    assert result.final_env["API_SECRET"] != "topsecret"
    assert result.final_env["DB_PASSWORD"] != "hunter2"
    # non-secret interpolated value visible
    assert "example.com" in result.final_env["APP_URL"]


def test_mask_only_leaves_refs_unresolved(rich_env):
    pipeline = EnvPipeline()
    pipeline.add_step("mask", mask_env)
    result = pipeline.run(rich_env)

    assert result.success
    # APP_URL still contains raw reference (not interpolated)
    assert "${" in result.final_env["APP_URL"]
    assert result.final_env["API_SECRET"] != "topsecret"


def test_pipeline_chaining_preserves_non_secret_values(rich_env):
    pipeline = EnvPipeline()
    pipeline.add_step("interpolate", _interp_step)
    pipeline.add_step("mask", mask_env)
    result = pipeline.run(rich_env)

    assert result.final_env["APP_HOST"] == "example.com"
    assert result.final_env["PORT"] == "443"


def test_disabled_step_does_not_alter_env(rich_env):
    pipeline = EnvPipeline()
    pipeline.add_step("interpolate", _interp_step, enabled=False)
    pipeline.add_step("mask", mask_env)
    result = pipeline.run(rich_env)

    assert result.success
    assert result.steps_skipped == ["interpolate"]
    # APP_URL should still have raw refs since interpolation was skipped
    assert "${" in result.final_env["APP_URL"]
