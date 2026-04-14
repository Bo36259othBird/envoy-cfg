"""Tests for envoy_cfg.namespace module."""

import pytest
from envoy_cfg.namespace import (
    apply_namespace,
    strip_namespace,
    extract_namespace,
    list_namespaces,
    NamespaceResult,
)


@pytest.fixture
def base_env():
    return {
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "APP_DEBUG": "true",
    }


def test_apply_namespace_prefixes_all_keys(base_env):
    result = apply_namespace(base_env, "prod")
    assert "PROD__DB_HOST" in result.transformed
    assert "PROD__DB_PORT" in result.transformed
    assert "PROD__APP_DEBUG" in result.transformed


def test_apply_namespace_preserves_values(base_env):
    result = apply_namespace(base_env, "staging")
    assert result.transformed["STAGING__DB_HOST"] == "localhost"


def test_apply_namespace_keys_affected_count(base_env):
    result = apply_namespace(base_env, "dev")
    assert result.keys_affected == len(base_env)


def test_apply_namespace_empty_raises():
    with pytest.raises(ValueError, match="Namespace must not be empty"):
        apply_namespace({"KEY": "val"}, "")


def test_apply_namespace_custom_separator(base_env):
    result = apply_namespace(base_env, "test", separator="_")
    assert "TEST_DB_HOST" in result.transformed


def test_strip_namespace_removes_prefix():
    env = {"PROD__DB_HOST": "localhost", "PROD__DB_PORT": "5432"}
    result = strip_namespace(env, "prod")
    assert "DB_HOST" in result.transformed
    assert "DB_PORT" in result.transformed
    assert result.keys_affected == 2


def test_strip_namespace_leaves_non_matching_keys():
    env = {"PROD__DB_HOST": "localhost", "OTHER_KEY": "value"}
    result = strip_namespace(env, "prod")
    assert "OTHER_KEY" in result.transformed
    assert result.keys_affected == 1


def test_strip_namespace_empty_raises():
    with pytest.raises(ValueError):
        strip_namespace({}, "")


def test_extract_namespace_returns_only_matching():
    env = {
        "PROD__DB_HOST": "localhost",
        "PROD__DB_PORT": "5432",
        "STAGING__DB_HOST": "staging-host",
    }
    extracted = extract_namespace(env, "prod")
    assert set(extracted.keys()) == {"DB_HOST", "DB_PORT"}
    assert "STAGING__DB_HOST" not in extracted


def test_extract_namespace_empty_when_no_match():
    env = {"STAGING__KEY": "val"}
    extracted = extract_namespace(env, "prod")
    assert extracted == {}


def test_list_namespaces_detects_multiple():
    env = {
        "PROD__DB_HOST": "a",
        "STAGING__DB_HOST": "b",
        "DEV__API_KEY": "c",
        "NO_NAMESPACE": "d",
    }
    namespaces = list_namespaces(env)
    assert "PROD" in namespaces
    assert "STAGING" in namespaces
    assert "DEV" in namespaces
    assert len(namespaces) == 3


def test_list_namespaces_sorted():
    env = {"ZEBRA__K": "v", "ALPHA__K": "v", "MANGO__K": "v"}
    namespaces = list_namespaces(env)
    assert namespaces == sorted(namespaces)


def test_list_namespaces_empty_env():
    assert list_namespaces({}) == []


def test_namespace_result_repr():
    result = apply_namespace({"A": "1"}, "ns")
    assert "ns" in repr(result)
    assert "keys_affected" in repr(result)
