import pytest
from envoy_cfg.sort import sort_by_key, sort_by_value, sort_by_length, SortResult


@pytest.fixture
def base_env():
    return {
        "ZEBRA": "last",
        "ALPHA": "first",
        "MONKEY": "middle",
        "BB": "short_key",
    }


def test_sort_by_key_returns_sort_result(base_env):
    result = sort_by_key(base_env)
    assert isinstance(result, SortResult)


def test_sort_by_key_ascending(base_env):
    result = sort_by_key(base_env)
    assert list(result.env.keys()) == ["ALPHA", "BB", "MONKEY", "ZEBRA"]


def test_sort_by_key_descending(base_env):
    result = sort_by_key(base_env, reverse=True)
    assert list(result.env.keys()) == ["ZEBRA", "MONKEY", "BB", "ALPHA"]


def test_sort_by_key_preserves_values(base_env):
    result = sort_by_key(base_env)
    assert result.env["ALPHA"] == "first"
    assert result.env["ZEBRA"] == "last"


def test_sort_by_key_strategy_label(base_env):
    asc = sort_by_key(base_env)
    desc = sort_by_key(base_env, reverse=True)
    assert asc.strategy == "alphabetical-asc"
    assert desc.strategy == "alphabetical-desc"


def test_sort_by_key_original_order_preserved(base_env):
    result = sort_by_key(base_env)
    assert result.original_order == list(base_env.keys())


def test_sort_by_key_is_identity_when_already_sorted():
    env = {"ALPHA": "a", "BETA": "b", "GAMMA": "c"}
    result = sort_by_key(env)
    assert result.is_identity() is True


def test_sort_by_key_not_identity_when_unsorted(base_env):
    result = sort_by_key(base_env)
    assert result.is_identity() is False


def test_sort_by_value_ascending(base_env):
    result = sort_by_value(base_env)
    assert list(result.env.keys()) == ["ALPHA", "ZEBRA", "MONKEY", "BB"]


def test_sort_by_value_strategy_label(base_env):
    result = sort_by_value(base_env)
    assert result.strategy == "by-value-asc"


def test_sort_by_value_descending_strategy_label(base_env):
    result = sort_by_value(base_env, reverse=True)
    assert result.strategy == "by-value-desc"


def test_sort_by_length_ascending(base_env):
    result = sort_by_length(base_env)
    keys = list(result.env.keys())
    key_lengths = [len(k) for k in keys]
    assert key_lengths == sorted(key_lengths)


def test_sort_by_length_descending(base_env):
    result = sort_by_length(base_env, reverse=True)
    keys = list(result.env.keys())
    key_lengths = [len(k) for k in keys]
    assert key_lengths == sorted(key_lengths, reverse=True)


def test_sort_by_length_strategy_label(base_env):
    asc = sort_by_length(base_env)
    desc = sort_by_length(base_env, reverse=True)
    assert asc.strategy == "by-length-asc"
    assert desc.strategy == "by-length-desc"


def test_sort_repr(base_env):
    result = sort_by_key(base_env)
    r = repr(result)
    assert "alphabetical-asc" in r
    assert "4" in r
