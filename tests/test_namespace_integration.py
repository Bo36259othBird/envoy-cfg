"""Integration tests: apply then strip/extract namespace round-trips."""

import pytest
from envoy_cfg.namespace import apply_namespace, strip_namespace, extract_namespace, list_namespaces


@pytest.fixture
def multi_env():
    return {
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "API_KEY": "secret",
        "DEBUG": "false",
    }


def test_apply_then_strip_is_identity(multi_env):
    applied = apply_namespace(multi_env, "prod")
    stripped = strip_namespace(applied.transformed, "prod")
    assert stripped.transformed == multi_env


def test_apply_then_extract_recovers_original(multi_env):
    applied = apply_namespace(multi_env, "staging")
    extracted = extract_namespace(applied.transformed, "staging")
    assert extracted == multi_env


def test_two_namespaces_do_not_interfere():
    env_a = {"HOST": "host-a", "PORT": "8080"}
    env_b = {"HOST": "host-b", "PORT": "9090"}

    ns_a = apply_namespace(env_a, "alpha")
    ns_b = apply_namespace(env_b, "beta")

    merged = {**ns_a.transformed, **ns_b.transformed}

    recovered_a = extract_namespace(merged, "alpha")
    recovered_b = extract_namespace(merged, "beta")

    assert recovered_a == env_a
    assert recovered_b == env_b


def test_list_namespaces_after_apply(multi_env):
    applied = apply_namespace(multi_env, "gamma")
    namespaces = list_namespaces(applied.transformed)
    assert "GAMMA" in namespaces


def test_strip_only_affects_matching_namespace():
    env = {
        "PROD__DB_HOST": "prod-host",
        "STAGING__DB_HOST": "staging-host",
        "PLAIN_KEY": "value",
    }
    result = strip_namespace(env, "prod")
    assert "DB_HOST" in result.transformed
    assert "STAGING__DB_HOST" in result.transformed
    assert "PLAIN_KEY" in result.transformed
    assert result.keys_affected == 1


def test_custom_separator_roundtrip():
    env = {"ALPHA": "1", "BETA": "2"}
    applied = apply_namespace(env, "ns", separator=".")
    extracted = extract_namespace(applied.transformed, "ns", separator=".")
    assert extracted == env
