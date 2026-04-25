"""Tests for envoy_cfg.intersect."""
import pytest

from envoy_cfg.intersect import IntersectResult, intersect_envs


@pytest.fixture()
def envs() -> dict:
    return {
        "dev": {
            "APP_NAME": "myapp",
            "DB_HOST": "localhost",
            "DEBUG": "true",
        },
        "prod": {
            "APP_NAME": "myapp",
            "DB_HOST": "prod.db.example.com",
            "SECRET_KEY": "s3cr3t",
        },
    }


# --- basic structure ---

def test_intersect_returns_intersect_result(envs):
    result = intersect_envs(envs)
    assert isinstance(result, IntersectResult)


def test_intersect_common_keys_present_in_all_envs(envs):
    result = intersect_envs(envs)
    assert set(result.common.keys()) == {"APP_NAME", "DB_HOST"}


def test_intersect_common_values_ordered_by_label(envs):
    result = intersect_envs(envs)
    # labels are iterated in insertion order: dev, prod
    assert result.common["APP_NAME"] == ["myapp", "myapp"]
    assert result.common["DB_HOST"] == ["localhost", "prod.db.example.com"]


def test_intersect_only_in_dev(envs):
    result = intersect_envs(envs)
    assert result.only_in["dev"] == {"DEBUG"}


def test_intersect_only_in_prod(envs):
    result = intersect_envs(envs)
    assert result.only_in["prod"] == {"SECRET_KEY"}


# --- consistency ---

def test_intersect_is_consistent_when_values_match():
    envs = {
        "a": {"HOST": "localhost"},
        "b": {"HOST": "localhost"},
    }
    result = intersect_envs(envs)
    assert result.is_consistent is True


def test_intersect_is_not_consistent_when_values_differ(envs):
    result = intersect_envs(envs)
    assert result.is_consistent is False


def test_intersect_conflicting_keys(envs):
    result = intersect_envs(envs)
    assert result.conflicting_keys == ["DB_HOST"]


def test_intersect_no_conflicting_keys_when_values_match():
    envs = {
        "x": {"PORT": "8080"},
        "y": {"PORT": "8080"},
    }
    result = intersect_envs(envs)
    assert result.conflicting_keys == []


# --- edge cases ---

def test_intersect_empty_common_when_no_shared_keys():
    envs = {
        "a": {"FOO": "1"},
        "b": {"BAR": "2"},
    }
    result = intersect_envs(envs)
    assert result.common == {}
    assert result.only_in["a"] == {"FOO"}
    assert result.only_in["b"] == {"BAR"}


def test_intersect_three_envs_requires_all_three():
    envs = {
        "a": {"X": "1", "Y": "2"},
        "b": {"X": "1", "Z": "3"},
        "c": {"X": "1", "Y": "9"},
    }
    result = intersect_envs(envs)
    # Only X is in all three
    assert set(result.common.keys()) == {"X"}


def test_intersect_raises_for_single_env():
    with pytest.raises(ValueError, match="at least two"):
        intersect_envs({"only": {"A": "1"}})


def test_intersect_common_keys_are_sorted():
    envs = {
        "p": {"ZEBRA": "z", "ALPHA": "a", "MANGO": "m"},
        "q": {"ZEBRA": "z", "ALPHA": "b", "MANGO": "m"},
    }
    result = intersect_envs(envs)
    assert list(result.common.keys()) == sorted(result.common.keys())


def test_intersect_strategy_label():
    envs = {"a": {"K": "v"}, "b": {"K": "v"}}
    result = intersect_envs(envs)
    assert result.strategy == "intersect"
