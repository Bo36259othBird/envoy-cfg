import pytest
from envoy_cfg.typecheck import typecheck_env, TypeCheckResult, TypeCheckIssue


@pytest.fixture
def env():
    return {
        "PORT": "8080",
        "RATIO": "0.75",
        "DEBUG": "true",
        "API_URL": "https://example.com",
        "NAME": "myapp",
        "EMPTY": "",
    }


def test_typecheck_returns_result(env):
    result = typecheck_env(env, {"PORT": "int"})
    assert isinstance(result, TypeCheckResult)


def test_typecheck_valid_int(env):
    result = typecheck_env(env, {"PORT": "int"})
    assert result.is_clean
    assert result.checked == 1


def test_typecheck_invalid_int(env):
    result = typecheck_env({"PORT": "abc"}, {"PORT": "int"})
    assert not result.is_clean
    assert len(result.issues) == 1
    assert result.issues[0].key == "PORT"


def test_typecheck_valid_float(env):
    result = typecheck_env(env, {"RATIO": "float"})
    assert result.is_clean


def test_typecheck_invalid_float(env):
    result = typecheck_env({"RATIO": "not-a-float"}, {"RATIO": "float"})
    assert not result.is_clean


def test_typecheck_valid_bool(env):
    for val in ("true", "false", "1", "0", "yes", "no"):
        result = typecheck_env({"DEBUG": val}, {"DEBUG": "bool"})
        assert result.is_clean, f"Expected {val!r} to be valid bool"


def test_typecheck_invalid_bool(env):
    result = typecheck_env({"DEBUG": "maybe"}, {"DEBUG": "bool"})
    assert not result.is_clean


def test_typecheck_valid_url(env):
    result = typecheck_env(env, {"API_URL": "url"})
    assert result.is_clean


def test_typecheck_invalid_url(env):
    result = typecheck_env({"API_URL": "ftp://bad"}, {"API_URL": "url"})
    assert not result.is_clean


def test_typecheck_nonempty_passes(env):
    result = typecheck_env(env, {"NAME": "nonempty"})
    assert result.is_clean


def test_typecheck_nonempty_fails(env):
    result = typecheck_env(env, {"EMPTY": "nonempty"})
    assert not result.is_clean


def test_typecheck_missing_key_skipped(env):
    result = typecheck_env(env, {"MISSING_KEY": "int"})
    assert result.is_clean
    assert result.checked == 0


def test_typecheck_unknown_type_skipped(env):
    result = typecheck_env(env, {"PORT": "uuid"})
    assert result.is_clean
    assert result.checked == 0


def test_typecheck_multiple_issues(env):
    bad_env = {"PORT": "xyz", "RATIO": "oops", "DEBUG": "maybe"}
    schema = {"PORT": "int", "RATIO": "float", "DEBUG": "bool"}
    result = typecheck_env(bad_env, schema)
    assert len(result.issues) == 3


def test_issue_repr():
    issue = TypeCheckIssue(key="PORT", value="abc", expected_type="int")
    r = repr(issue)
    assert "PORT" in r
    assert "int" in r


def test_result_repr(env):
    result = typecheck_env(env, {"PORT": "int"})
    r = repr(result)
    assert "checked" in r
