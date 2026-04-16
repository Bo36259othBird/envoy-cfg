"""Tests for envoy_cfg.crossref."""
import pytest
from envoy_cfg.crossref import crossref_envs, CrossRefResult


@pytest.fixture
def envs():
    return {
        "prod": {"DB_HOST": "prod-db", "DB_PASS": "secret", "APP_PORT": "443"},
        "staging": {"DB_HOST": "stg-db", "DB_PASS": "s3cr3t", "DEBUG": "true"},
        "dev": {"DB_HOST": "localhost", "DEBUG": "true", "APP_PORT": "8080"},
    }


def test_crossref_returns_result(envs):
    result = crossref_envs(envs)
    assert isinstance(result, CrossRefResult)


def test_crossref_common_keys(envs):
    result = crossref_envs(envs)
    assert result.common == {"DB_HOST"}


def test_crossref_only_in_prod(envs):
    result = crossref_envs(envs)
    assert "DB_PASS" in result.only_in["prod"]


def test_crossref_missing_in_dev(envs):
    result = crossref_envs(envs)
    assert "DB_PASS" in result.missing_in["dev"]


def test_crossref_is_not_consistent_with_differing_keys(envs):
    result = crossref_envs(envs)
    assert not result.is_consistent()


def test_crossref_is_consistent_when_all_keys_match():
    same = {
        "a": {"X": "1", "Y": "2"},
        "b": {"X": "3", "Y": "4"},
    }
    result = crossref_envs(same)
    assert result.is_consistent()


def test_crossref_empty_raises():
    with pytest.raises(ValueError):
        crossref_envs({})


def test_crossref_single_env_is_consistent():
    result = crossref_envs({"only": {"A": "1", "B": "2"}})
    assert result.is_consistent()
    assert result.common == {"A", "B"}


def test_crossref_only_in_all_empty_when_consistent():
    same = {"x": {"K": "v"}, "y": {"K": "v2"}}
    result = crossref_envs(same)
    assert all(len(v) == 0 for v in result.only_in.values())


def test_crossref_repr_contains_env_names(envs):
    result = crossref_envs(envs)
    r = repr(result)
    assert "CrossRefResult" in r
