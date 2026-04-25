"""Integration tests combining unique with other envoy_cfg modules."""

from __future__ import annotations

from envoy_cfg.normalize import normalize_keys
from envoy_cfg.prune import prune_empty
from envoy_cfg.unique import find_unique_values
from envoy_cfg.mask_report import build_mask_report


def test_unique_after_normalize_detects_shared_values():
    raw = {"db_host": "localhost", "cache_host": "localhost", "port": "8080"}
    normalised = normalize_keys(raw).env
    result = find_unique_values(normalised)
    assert not result.is_clean()
    assert "localhost" in result.duplicate_values


def test_unique_after_prune_excludes_empty_keys():
    env = {"A": "x", "B": "x", "C": "", "D": ""}
    pruned = prune_empty(env).env
    result = find_unique_values(pruned, ignore_empty=False)
    # empty values were removed by prune so no empty duplicates
    assert "" not in result.duplicate_values
    assert "x" in result.duplicate_values


def test_unique_clean_env_is_consistent():
    env = {"KEY_A": "alpha", "KEY_B": "beta", "KEY_C": "gamma"}
    result = find_unique_values(env)
    assert result.is_clean()
    assert result.shared_count() == 0


def test_unique_shared_count_matches_duplicate_groups():
    env = {"A": "same", "B": "same", "C": "same", "D": "other", "E": "other"}
    result = find_unique_values(env)
    # 3 keys share "same", 2 keys share "other"
    assert result.shared_count() == 5
    assert len(result.duplicate_values) == 2


def test_unique_does_not_mutate_original_env():
    env = {"X": "val", "Y": "val"}
    original = dict(env)
    find_unique_values(env)
    assert env == original
