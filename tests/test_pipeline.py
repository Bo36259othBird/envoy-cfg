"""Tests for envoy_cfg.pipeline."""

import pytest
from envoy_cfg.pipeline import EnvPipeline, PipelineStep, PipelineResult


@pytest.fixture
def base_env():
    return {"APP_HOST": "localhost", "DB_PASSWORD": "s3cr3t", "PORT": "8080"}


def upper_keys(env):
    return {k.upper(): v for k, v in env.items()}


def add_prefix(env):
    return {f"MY_{k}": v for k, v in env.items()}


def boom(_env):
    raise RuntimeError("intentional failure")


# --- PipelineStep ---

def test_pipeline_step_apply_when_enabled(base_env):
    step = PipelineStep(name="upper", transform=upper_keys, enabled=True)
    result = step.apply({"a": "1"})
    assert result == {"A": "1"}


def test_pipeline_step_skips_when_disabled(base_env):
    step = PipelineStep(name="upper", transform=upper_keys, enabled=False)
    result = step.apply({"a": "1"})
    assert result == {"a": "1"}


def test_pipeline_step_repr():
    step = PipelineStep(name="mask", transform=upper_keys, enabled=False)
    assert "mask" in repr(step)
    assert "off" in repr(step)


# --- EnvPipeline.run ---

def test_pipeline_runs_steps_in_order(base_env):
    pipeline = EnvPipeline()
    pipeline.add_step("upper", upper_keys)
    pipeline.add_step("prefix", add_prefix)
    result = pipeline.run({"x": "1"})
    assert result.success
    assert "MY_X" in result.final_env
    assert result.steps_applied == ["upper", "prefix"]


def test_pipeline_skips_disabled_step(base_env):
    pipeline = EnvPipeline()
    pipeline.add_step("upper", upper_keys, enabled=False)
    pipeline.add_step("prefix", add_prefix)
    result = pipeline.run({"x": "1"})
    assert result.steps_skipped == ["upper"]
    assert result.steps_applied == ["prefix"]
    assert "MY_x" in result.final_env


def test_pipeline_captures_error_on_failing_step():
    pipeline = EnvPipeline()
    pipeline.add_step("good", upper_keys)
    pipeline.add_step("bad", boom)
    result = pipeline.run({"k": "v"})
    assert not result.success
    assert "bad" in result.error
    assert result.steps_applied == ["good"]


def test_pipeline_empty_steps_returns_original(base_env):
    pipeline = EnvPipeline()
    result = pipeline.run(base_env)
    assert result.success
    assert result.final_env == base_env
    assert result.steps_applied == []


def test_pipeline_disable_step_by_name():
    pipeline = EnvPipeline()
    pipeline.add_step("upper", upper_keys)
    pipeline.disable_step("upper")
    result = pipeline.run({"a": "1"})
    assert result.steps_skipped == ["upper"]


def test_pipeline_enable_step_by_name():
    pipeline = EnvPipeline()
    pipeline.add_step("upper", upper_keys, enabled=False)
    pipeline.enable_step("upper")
    result = pipeline.run({"a": "1"})
    assert result.steps_applied == ["upper"]


def test_pipeline_disable_unknown_step_raises():
    pipeline = EnvPipeline()
    with pytest.raises(KeyError):
        pipeline.disable_step("nonexistent")


def test_pipeline_step_names():
    pipeline = EnvPipeline()
    pipeline.add_step("a", upper_keys)
    pipeline.add_step("b", add_prefix)
    assert pipeline.step_names() == ["a", "b"]


def test_pipeline_result_repr():
    r = PipelineResult(steps_applied=["a"], steps_skipped=["b"])
    assert "applied" in repr(r)
    assert "skipped" in repr(r)
