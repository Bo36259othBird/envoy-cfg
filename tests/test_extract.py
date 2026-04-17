import pytest
from envoy_cfg.extract import extract_by_prefix, extract_by_regex, ExtractResult


@pytest.fixture
def base_env():
    return {
        "APP_HOST": "localhost",
        "APP_PORT": "8080",
        "DB_HOST": "db.local",
        "DB_PORT": "5432",
        "SECRET_KEY": "abc123",
    }


def test_extract_by_prefix_returns_result(base_env):
    result = extract_by_prefix(base_env, "APP_")
    assert isinstance(result, ExtractResult)


def test_extract_by_prefix_gets_matching_keys(base_env):
    result = extract_by_prefix(base_env, "APP_")
    assert "APP_HOST" in result.extracted
    assert "APP_PORT" in result.extracted


def test_extract_by_prefix_remaining_excludes_matched(base_env):
    result = extract_by_prefix(base_env, "APP_")
    assert "APP_HOST" not in result.remaining
    assert "DB_HOST" in result.remaining


def test_extract_by_prefix_strip_removes_prefix(base_env):
    result = extract_by_prefix(base_env, "APP_", strip=True)
    assert "HOST" in result.extracted
    assert "PORT" in result.extracted
    assert "APP_HOST" not in result.extracted


def test_extract_by_prefix_strip_preserves_values(base_env):
    result = extract_by_prefix(base_env, "APP_", strip=True)
    assert result.extracted["HOST"] == "localhost"


def test_extract_by_prefix_strategy_label(base_env):
    result = extract_by_prefix(base_env, "DB_")
    assert result.strategy == "prefix"
    assert result.pattern == "DB_"


def test_extract_by_prefix_empty_prefix_raises(base_env):
    with pytest.raises(ValueError):
        extract_by_prefix(base_env, "")


def test_extract_by_prefix_no_matches(base_env):
    result = extract_by_prefix(base_env, "NOPE_")
    assert result.is_empty()
    assert len(result.remaining) == len(base_env)


def test_extract_by_regex_returns_result(base_env):
    result = extract_by_regex(base_env, r"^DB_")
    assert isinstance(result, ExtractResult)


def test_extract_by_regex_matches_pattern(base_env):
    result = extract_by_regex(base_env, r"^DB_")
    assert "DB_HOST" in result.extracted
    assert "DB_PORT" in result.extracted


def test_extract_by_regex_remaining_excludes_matched(base_env):
    result = extract_by_regex(base_env, r"^DB_")
    assert "DB_HOST" not in result.remaining
    assert "APP_HOST" in result.remaining


def test_extract_by_regex_invalid_pattern_raises(base_env):
    with pytest.raises(ValueError):
        extract_by_regex(base_env, r"[invalid")


def test_extract_by_regex_strategy_label(base_env):
    result = extract_by_regex(base_env, r"SECRET")
    assert result.strategy == "regex"


def test_extract_result_repr(base_env):
    result = extract_by_prefix(base_env, "APP_")
    r = repr(result)
    assert "prefix" in r
    assert "extracted" in r
