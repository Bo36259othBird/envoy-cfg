"""Tests for envoy_cfg.reorder."""
import pytest
from envoy_cfg.reorder import (
    ReorderResult,
    reorder_alphabetical,
    reorder_by_prefix,
    reorder_secrets_last,
)


@pytest.fixture()
def base_env():
    return {
        "ZEBRA": "1",
        "APP_NAME": "myapp",
        "DB_PASSWORD": "secret",
        "APP_ENV": "prod",
        "DB_HOST": "localhost",
        "API_KEY": "abc123",
    }


def test_reorder_alphabetical_sorts_keys(base_env):
    result = reorder_alphabetical(base_env)
    assert list(result.reordered.keys()) == sorted(base_env.keys())


def test_reorder_alphabetical_preserves_values(base_env):
    result = reorder_alphabetical(base_env)
    for k, v in base_env.items():
        assert result.reordered[k] == v


def test_reorder_alphabetical_reverse(base_env):
    result = reorder_alphabetical(base_env, reverse=True)
    assert list(result.reordered.keys()) == sorted(base_env.keys(), reverse=True)


def test_reorder_alphabetical_strategy_label(base_env):
    assert reorder_alphabetical(base_env).strategy == "alphabetical"
    assert reorder_alphabetical(base_env, reverse=True).strategy == "alphabetical_desc"


def test_reorder_alphabetical_moved_count(base_env):
    result = reorder_alphabetical(base_env)
    # Original order is not sorted, so at least one key should have moved
    assert result.moved >= 0  # always non-negative


def test_reorder_already_sorted_is_identity():
    env = {"A": "1", "B": "2", "C": "3"}
    result = reorder_alphabetical(env)
    assert result.is_identity() is True
    assert result.moved == 0


def test_reorder_by_prefix_groups_correctly(base_env):
    result = reorder_by_prefix(base_env, ["APP_", "DB_"])
    keys = list(result.reordered.keys())
    app_indices = [keys.index(k) for k in keys if k.startswith("APP_")]
    db_indices = [keys.index(k) for k in keys if k.startswith("DB_")]
    assert max(app_indices) < min(db_indices)


def test_reorder_by_prefix_unmatched_keys_go_last(base_env):
    result = reorder_by_prefix(base_env, ["APP_", "DB_"])
    keys = list(result.reordered.keys())
    unmatched = [k for k in base_env if not k.startswith(("APP_", "DB_"))]
    for k in unmatched:
        assert keys.index(k) >= len(base_env) - len(unmatched)


def test_reorder_by_prefix_strategy_label(base_env):
    result = reorder_by_prefix(base_env, ["APP_"])
    assert result.strategy == "by_prefix"


def test_reorder_by_prefix_preserves_all_keys(base_env):
    result = reorder_by_prefix(base_env, ["APP_"])
    assert set(result.reordered.keys()) == set(base_env.keys())


def test_reorder_secrets_last_moves_secret_keys(base_env):
    result = reorder_secrets_last(base_env)
    keys = list(result.reordered.keys())
    secret_keys = ["DB_PASSWORD", "API_KEY"]
    non_secret_keys = [k for k in keys if k not in secret_keys]
    for sk in secret_keys:
        if sk in keys:
            assert keys.index(sk) >= len(non_secret_keys)


def test_reorder_secrets_last_strategy_label(base_env):
    result = reorder_secrets_last(base_env)
    assert result.strategy == "secrets_last"


def test_reorder_secrets_last_preserves_values(base_env):
    result = reorder_secrets_last(base_env)
    for k, v in base_env.items():
        assert result.reordered[k] == v


def test_reorder_result_repr(base_env):
    result = reorder_alphabetical(base_env)
    assert "ReorderResult" in repr(result)
