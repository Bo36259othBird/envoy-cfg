"""Tests for envoy_cfg.annotate."""
import pytest
from envoy_cfg.annotate import (
    apply_annotations,
    strip_annotations,
    get_annotation,
    AnnotateResult,
)


@pytest.fixture
def base_env():
    return {"APP_HOST": "localhost", "APP_PORT": "8080", "SECRET_KEY": "abc123"}


@pytest.fixture
def annotations():
    return {"APP_HOST": "The application hostname", "SECRET_KEY": "Do not expose"}


def test_apply_annotations_returns_annotate_result(base_env, annotations):
    result = apply_annotations(base_env, annotations)
    assert isinstance(result, AnnotateResult)


def test_apply_annotations_annotated_keys_sorted(base_env, annotations):
    result = apply_annotations(base_env, annotations)
    assert result.annotated_keys == sorted(["APP_HOST", "SECRET_KEY"])


def test_apply_annotations_env_unchanged(base_env, annotations):
    result = apply_annotations(base_env, annotations)
    assert result.env == base_env


def test_apply_annotations_annotations_stored(base_env, annotations):
    result = apply_annotations(base_env, annotations)
    assert result.annotations["APP_HOST"] == "The application hostname"
    assert result.annotations["SECRET_KEY"] == "Do not expose"


def test_apply_annotations_unannotated_key_has_empty_string(base_env, annotations):
    result = apply_annotations(base_env, annotations)
    assert result.annotations.get("APP_PORT") == ""


def test_apply_annotations_is_clean_when_no_annotations(base_env):
    result = apply_annotations(base_env, {})
    assert result.is_clean()


def test_apply_annotations_not_clean_when_annotated(base_env, annotations):
    result = apply_annotations(base_env, annotations)
    assert not result.is_clean()


def test_apply_annotations_strategy_label(base_env, annotations):
    result = apply_annotations(base_env, annotations)
    assert result.strategy == "annotate"


def test_apply_annotations_invalid_type_raises(base_env):
    with pytest.raises(TypeError):
        apply_annotations(base_env, "not-a-dict")


def test_strip_annotations_removes_all_when_keys_none():
    annotations = {"A": "note A", "B": "note B"}
    result = strip_annotations(annotations, keys=None)
    assert result == {}


def test_strip_annotations_removes_specified_keys():
    annotations = {"A": "note A", "B": "note B", "C": "note C"}
    result = strip_annotations(annotations, keys=["A", "C"])
    assert "A" not in result
    assert "C" not in result
    assert result["B"] == "note B"


def test_strip_annotations_missing_key_is_ignored():
    annotations = {"A": "note A"}
    result = strip_annotations(annotations, keys=["Z"])
    assert result == {"A": "note A"}


def test_get_annotation_returns_note(base_env, annotations):
    result = apply_annotations(base_env, annotations)
    note = get_annotation(result.annotations, "APP_HOST")
    assert note == "The application hostname"


def test_get_annotation_returns_none_for_missing_key(base_env):
    result = apply_annotations(base_env, {})
    note = get_annotation(result.annotations, "NONEXISTENT")
    assert note is None


def test_get_annotation_returns_none_for_empty_annotation(base_env):
    result = apply_annotations(base_env, {})
    note = get_annotation(result.annotations, "APP_PORT")
    assert note is None
