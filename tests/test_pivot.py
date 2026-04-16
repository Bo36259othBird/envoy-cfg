"""Tests for envoy_cfg.pivot."""
import pytest
from envoy_cfg.pivot import pivot_env, unpivot_env, PivotResult


@pytest.fixture
def base_env():
    return {
        "APP_HOST": "localhost",
        "DB_HOST": "db.internal",
        "CACHE_HOST": "redis.internal",
        "EMPTY_KEY": "",
    }


def test_pivot_returns_pivot_result(base_env):
    result = pivot_env(base_env)
    assert isinstance(result, PivotResult)


def test_pivot_swaps_keys_and_values(base_env):
    result = pivot_env(base_env)
    assert result.pivoted["localhost"] == "APP_HOST"
    assert result.pivoted["db.internal"] == "DB_HOST"


def test_pivot_skips_empty_values_by_default(base_env):
    result = pivot_env(base_env)
    assert "EMPTY_KEY" in result.skipped
    assert "" not in result.pivoted


def test_pivot_keep_empty_includes_empty_values(base_env):
    result = pivot_env(base_env, skip_empty=False)
    assert "" in result.pivoted
    assert result.pivoted[""] == "EMPTY_KEY"


def test_pivot_is_clean_when_no_skipped():
    env = {"A": "alpha", "B": "beta"}
    result = pivot_env(env)
    assert result.is_clean


def test_pivot_not_clean_when_skipped(base_env):
    result = pivot_env(base_env)
    assert not result.is_clean


def test_pivot_collision_keep_first():
    env = {"A": "same", "B": "same"}
    result = pivot_env(env, overwrite=False)
    assert result.pivoted["same"] == "A"
    assert "B" in result.skipped


def test_pivot_collision_overwrite():
    env = {"A": "same", "B": "same"}
    result = pivot_env(env, overwrite=True)
    assert result.pivoted["same"] == "B"
    assert len(result.skipped) == 0


def test_pivot_strategy_label_keep_first():
    result = pivot_env({"X": "y"}, overwrite=False)
    assert result.strategy == "keep-first"


def test_pivot_strategy_label_overwrite():
    result = pivot_env({"X": "y"}, overwrite=True)
    assert result.strategy == "overwrite"


def test_pivot_repr():
    result = pivot_env({"A": "alpha"})
    r = repr(result)
    assert "PivotResult" in r
    assert "pivoted=" in r


def test_unpivot_reverses_pivot():
    original = {"APP_HOST": "localhost", "DB_HOST": "db.internal"}
    pivoted = {"localhost": "APP_HOST", "db.internal": "DB_HOST"}
    restored = unpivot_env(pivoted, original)
    assert restored["APP_HOST"] == "APP_HOST"
    assert restored["DB_HOST"] == "DB_HOST"


def test_unpivot_passthrough_unknown_keys():
    original = {"A": "alpha"}
    modified = {"alpha": "A", "unknown_val": "X"}
    restored = unpivot_env(modified, original)
    assert "unknown_val" in restored
