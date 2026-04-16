"""Integration tests: crossref combined with other modules."""
from envoy_cfg.crossref import crossref_envs
from envoy_cfg.normalize import normalize_keys
from envoy_cfg.prune import prune_empty


def test_crossref_after_normalize_finds_common_keys():
    raw_a = {"db_host": "prod", "app_port": "443"}
    raw_b = {"DB_HOST": "dev", "APP_PORT": "8080"}
    norm_a = normalize_keys(raw_a).env
    norm_b = normalize_keys(raw_b).env
    result = crossref_envs({"a": norm_a, "b": norm_b})
    assert "DB_HOST" in result.common
    assert "APP_PORT" in result.common


def test_crossref_after_prune_removes_noise():
    a = {"HOST": "prod", "EMPTY": ""}
    b = {"HOST": "dev", "EMPTY": ""}
    pruned_a = prune_empty(a).env
    pruned_b = prune_empty(b).env
    result = crossref_envs({"a": pruned_a, "b": pruned_b})
    assert "EMPTY" not in result.common
    assert result.is_consistent()


def test_crossref_three_envs_missing_in_reports_correctly():
    envs = {
        "prod": {"A": "1", "B": "2", "C": "3"},
        "staging": {"A": "1", "B": "2"},
        "dev": {"A": "1"},
    }
    result = crossref_envs(envs)
    assert "B" in result.missing_in["dev"]
    assert "C" in result.missing_in["dev"]
    assert "C" in result.missing_in["staging"]
    assert result.common == {"A"}


def test_crossref_identical_envs_is_consistent():
    env = {"HOST": "x", "PORT": "80"}
    result = crossref_envs({"a": dict(env), "b": dict(env), "c": dict(env)})
    assert result.is_consistent()
    assert len(result.common) == 2
