"""Integration tests combining index with other envoy_cfg modules."""
from __future__ import annotations

from envoy_cfg.index import build_index
from envoy_cfg.normalize import normalize_keys
from envoy_cfg.prefix import add_prefix
from envoy_cfg.prune import prune_empty
from envoy_cfg.masking import mask_env


def test_index_after_normalize_finds_uppercased_keys():
    env = {"app_host": "localhost", "app_port": "8080"}
    normalized = normalize_keys(env).env
    result = build_index(normalized)
    assert result.lookup("APP_HOST") == "localhost"
    assert result.lookup("app_host") is None


def test_index_after_prefix_searches_prefixed_keys():
    env = {"HOST": "localhost", "PORT": "8080"}
    prefixed = add_prefix(env, "APP_").env
    result = build_index(prefixed)
    keys = result.search_keys("APP_*")
    assert "APP_HOST" in keys
    assert "APP_PORT" in keys


def test_index_after_prune_excludes_empty_keys():
    env = {"HOST": "localhost", "EMPTY": "", "PORT": "8080"}
    pruned = prune_empty(env).env
    result = build_index(pruned)
    assert result.lookup("EMPTY") is None
    assert result.total == 2


def test_index_search_values_after_mask_returns_masked_values():
    env = {"SECRET_KEY": "s3cr3t", "APP_HOST": "localhost"}
    masked = mask_env(env)
    result = build_index(masked)
    hits = result.search_values("***")
    assert "SECRET_KEY" in hits
    assert "APP_HOST" not in hits


def test_index_case_insensitive_after_normalize_no_duplicates():
    env = {"app_host": "localhost", "APP_HOST": "other"}
    # last write wins in dict comprehension; just verify total is 1
    result = build_index(env, case_insensitive=True)
    assert result.total == 1
    assert result.lookup("APP_HOST") is not None
