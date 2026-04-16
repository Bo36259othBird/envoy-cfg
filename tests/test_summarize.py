import pytest
from envoy_cfg.summarize import summarize_env, SummaryResult


@pytest.fixture
def base_env():
    return {
        "APP_HOST": "localhost",
        "APP_PORT": "8080",
        "DB_PASSWORD": "s3cr3t",
        "DB_HOST": "db.internal",
        "EMPTY_VAR": "",
        "API_SECRET_KEY": "topsecret",
    }


def test_summarize_returns_summary_result(base_env):
    result = summarize_env(base_env)
    assert isinstance(result, SummaryResult)


def test_summarize_total_count(base_env):
    result = summarize_env(base_env)
    assert result.total == 6


def test_summarize_detects_secret_keys(base_env):
    result = summarize_env(base_env)
    assert result.secret_count >= 2  # DB_PASSWORD and API_SECRET_KEY


def test_summarize_plain_count(base_env):
    result = summarize_env(base_env)
    assert result.plain_count == result.total - result.secret_count


def test_summarize_empty_count(base_env):
    result = summarize_env(base_env)
    assert result.empty_count == 1


def test_summarize_prefixes_grouped(base_env):
    result = summarize_env(base_env)
    assert "APP" in result.prefixes
    assert "DB" in result.prefixes
    assert result.prefixes["APP"] == 2
    assert result.prefixes["DB"] == 2


def test_summarize_longest_key(base_env):
    result = summarize_env(base_env)
    assert result.longest_key == "API_SECRET_KEY"


def test_summarize_longest_value_key(base_env):
    result = summarize_env(base_env)
    assert result.longest_value_key in base_env
    assert len(base_env[result.longest_value_key]) == max(len(v) for v in base_env.values())


def test_summarize_empty_env():
    result = summarize_env({})
    assert result.total == 0
    assert result.secret_count == 0
    assert result.plain_count == 0
    assert result.empty_count == 0
    assert result.prefixes == {}
    assert result.longest_key == ""
    assert result.longest_value_key == ""


def test_summarize_is_clean_no_secrets_no_empty():
    env = {"APP_HOST": "localhost", "APP_PORT": "8080"}
    result = summarize_env(env)
    assert result.is_clean()


def test_summarize_is_not_clean_with_secrets(base_env):
    result = summarize_env(base_env)
    assert not result.is_clean()


def test_summarize_repr(base_env):
    result = summarize_env(base_env)
    r = repr(result)
    assert "SummaryResult" in r
    assert "total=6" in r


def test_summarize_no_separator_keys():
    env = {"HOST": "localhost", "PORT": "8080"}
    result = summarize_env(env)
    assert "HOST" in result.prefixes
    assert "PORT" in result.prefixes
