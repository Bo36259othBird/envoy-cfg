import pytest
from envoy_cfg.prefix import add_prefix, remove_prefix, PrefixResult


@pytest.fixture
def base_env():
    return {
        "APP_HOST": "localhost",
        "APP_PORT": "8080",
        "DB_URL": "postgres://localhost/db",
        "SECRET_KEY": "s3cr3t",
    }


def test_add_prefix_returns_prefix_result(base_env):
    result = add_prefix(base_env, "TEST_")
    assert isinstance(result, PrefixResult)


def test_add_prefix_all_keys(base_env):
    result = add_prefix(base_env, "TEST_")
    assert "TEST_APP_HOST" in result.env
    assert "TEST_APP_PORT" in result.env
    assert "TEST_DB_URL" in result.env
    assert "TEST_SECRET_KEY" in result.env


def test_add_prefix_removes_original_keys(base_env):
    result = add_prefix(base_env, "TEST_")
    assert "APP_HOST" not in result.env
    assert "DB_URL" not in result.env


def test_add_prefix_preserves_values(base_env):
    result = add_prefix(base_env, "TEST_")
    assert result.env["TEST_APP_HOST"] == "localhost"
    assert result.env["TEST_DB_URL"] == "postgres://localhost/db"


def test_add_prefix_affected_count(base_env):
    result = add_prefix(base_env, "TEST_")
    assert len(result.affected) == len(base_env)


def test_add_prefix_strategy_label(base_env):
    result = add_prefix(base_env, "X_")
    assert result.strategy == "add_prefix"
    assert result.prefix == "X_"


def test_add_prefix_subset_of_keys(base_env):
    result = add_prefix(base_env, "NEW_", keys=["APP_HOST", "APP_PORT"])
    assert "NEW_APP_HOST" in result.env
    assert "NEW_APP_PORT" in result.env
    assert "DB_URL" in result.env  # untouched
    assert "APP_HOST" not in result.env


def test_add_prefix_skip_existing(base_env):
    env = dict(base_env)
    env["PRE_APP_HOST"] = "already_here"
    result = add_prefix(env, "PRE_", skip_existing=True, keys=["APP_HOST"])
    assert "APP_HOST" in result.env  # skipped, original kept
    assert result.skipped == ["APP_HOST"]


def test_add_prefix_no_skip_overwrites(base_env):
    env = dict(base_env)
    env["PRE_APP_HOST"] = "already_here"
    result = add_prefix(env, "PRE_", skip_existing=False, keys=["APP_HOST"])
    assert result.env["PRE_APP_HOST"] == "localhost"


def test_add_prefix_empty_prefix_raises(base_env):
    with pytest.raises(ValueError, match="prefix must not be empty"):
        add_prefix(base_env, "")


def test_add_prefix_is_clean_when_no_skips(base_env):
    result = add_prefix(base_env, "Z_")
    assert result.is_clean()


def test_remove_prefix_returns_prefix_result(base_env):
    prefixed = {f"APP_{k}": v for k, v in base_env.items()}
    result = remove_prefix(prefixed, "APP_")
    assert isinstance(result, PrefixResult)


def test_remove_prefix_strips_prefix(base_env):
    prefixed = {f"PRE_{k}": v for k, v in base_env.items()}
    result = remove_prefix(prefixed, "PRE_")
    for orig_key in base_env:
        assert orig_key in result.env


def test_remove_prefix_non_matching_keys_unchanged(base_env):
    env = dict(base_env)
    env["OTHER"] = "value"
    result = remove_prefix(env, "APP_")
    assert "OTHER" in result.env


def test_remove_prefix_affected_sorted(base_env):
    prefixed = {f"P_{k}": v for k, v in base_env.items()}
    result = remove_prefix(prefixed, "P_")
    assert result.affected == sorted(result.affected)


def test_remove_prefix_empty_prefix_raises(base_env):
    with pytest.raises(ValueError, match="prefix must not be empty"):
        remove_prefix(base_env, "")


def test_prefix_repr(base_env):
    result = add_prefix(base_env, "T_")
    r = repr(result)
    assert "add_prefix" in r
    assert "T_" in r
