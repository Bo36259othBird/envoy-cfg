import pytest

from envoy_cfg.count import CountResult, count_env


@pytest.fixture()
def base_env() -> dict:
    return {
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "DB_PASSWORD": "secret",
        "APP_NAME": "envoy",
        "APP_SECRET_KEY": "topsecret",
        "EMPTY_VAR": "",
        "DEBUG": "true",
    }


def test_count_returns_count_result(base_env):
    result = count_env(base_env)
    assert isinstance(result, CountResult)


def test_count_total(base_env):
    result = count_env(base_env)
    assert result.total == len(base_env)


def test_count_detects_secret_keys(base_env):
    result = count_env(base_env)
    # DB_PASSWORD and APP_SECRET_KEY are secrets
    assert result.secret_count >= 2


def test_count_plain_plus_secret_equals_total(base_env):
    result = count_env(base_env)
    assert result.plain_count + result.secret_count == result.total


def test_count_empty_count(base_env):
    result = count_env(base_env)
    assert result.empty_count == 1


def test_count_non_empty_count(base_env):
    result = count_env(base_env)
    assert result.non_empty_count == result.total - result.empty_count


def test_count_empty_plus_non_empty_equals_total(base_env):
    result = count_env(base_env)
    assert result.empty_count + result.non_empty_count == result.total


def test_count_by_prefix_groups_db_keys(base_env):
    result = count_env(base_env)
    assert result.by_prefix.get("DB") == 3


def test_count_by_prefix_groups_app_keys(base_env):
    result = count_env(base_env)
    assert result.by_prefix.get("APP") == 2


def test_count_by_prefix_depth_two(base_env):
    env = {"APP_DB_HOST": "h", "APP_DB_PORT": "5432", "APP_WEB_PORT": "80"}
    result = count_env(env, prefix_depth=2)
    assert result.by_prefix.get("APP_DB") == 2
    assert result.by_prefix.get("APP_WEB") == 1


def test_count_empty_env():
    result = count_env({})
    assert result.total == 0
    assert result.is_empty()
    assert result.by_prefix == {}


def test_count_is_empty_false_for_non_empty_env(base_env):
    result = count_env(base_env)
    assert not result.is_empty()


def test_count_custom_separator():
    env = {"DB.HOST": "h", "DB.PORT": "5432", "APP.NAME": "x"}
    result = count_env(env, separator=".")
    assert result.by_prefix.get("DB") == 2
    assert result.by_prefix.get("APP") == 1


def test_count_key_with_no_separator_uses_full_key_as_prefix():
    env = {"DEBUG": "1", "VERBOSE": "0"}
    result = count_env(env)
    assert "DEBUG" in result.by_prefix
    assert "VERBOSE" in result.by_prefix
