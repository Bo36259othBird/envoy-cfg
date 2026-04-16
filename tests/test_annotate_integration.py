"""Integration tests: annotate combined with other modules."""
import pytest
from envoy_cfg.annotate import apply_annotations, strip_annotations, get_annotation
from envoy_cfg.masking import mask_env
from envoy_cfg.diff import diff_envs


@pytest.fixture
def env():
    return {
        "APP_HOST": "prod.example.com",
        "APP_PORT": "443",
        "SECRET_TOKEN": "s3cr3t",
        "DB_PASSWORD": "hunter2",
    }


@pytest.fixture
def notes():
    return {
        "APP_HOST": "Primary hostname",
        "SECRET_TOKEN": "OAuth token — keep private",
        "DB_PASSWORD": "Database credential",
    }


def test_annotate_then_mask_secrets_hidden(env, notes):
    result = apply_annotations(env, notes)
    masked = mask_env(result.env)
    assert masked["SECRET_TOKEN"] != "s3cr3t"
    assert masked["DB_PASSWORD"] != "hunter2"
    assert masked["APP_HOST"] == "prod.example.com"


def test_annotate_annotations_preserved_after_mask(env, notes):
    result = apply_annotations(env, notes)
    # annotations dict is independent of masking
    assert get_annotation(result.annotations, "APP_HOST") == "Primary hostname"
    assert get_annotation(result.annotations, "SECRET_TOKEN") is not None


def test_annotate_unannotated_keys_have_no_note(env, notes):
    result = apply_annotations(env, notes)
    assert get_annotation(result.annotations, "APP_PORT") is None


def test_annotate_then_diff_reflects_env_changes(env, notes):
    result = apply_annotations(env, notes)
    updated = dict(result.env)
    updated["APP_PORT"] = "8443"
    diff = diff_envs(result.env, updated)
    modified_keys = [c.key for c in diff.modified]
    assert "APP_PORT" in modified_keys


def test_strip_then_reapply_is_consistent(env, notes):
    first = apply_annotations(env, notes)
    stripped = strip_annotations(first.annotations, keys=list(notes.keys()))
    # after stripping all annotated keys, no notes remain
    for key in notes:
        assert key not in stripped
    # re-apply produces same result
    second = apply_annotations(env, notes)
    assert second.annotated_keys == first.annotated_keys


def test_annotate_empty_env_is_clean():
    result = apply_annotations({}, {})
    assert result.is_clean()
    assert result.env == {}
    assert result.annotations == {}
