"""Tests for envoy_cfg.lint."""
import pytest
from envoy_cfg.lint import lint_env, LintIssue, LintResult


@pytest.fixture
def clean_env():
    return {"APP_NAME": "myapp", "PORT": "8080", "DEBUG": "false"}


def test_lint_clean_env_returns_no_issues(clean_env):
    result = lint_env(clean_env)
    assert result.is_clean
    assert result.issues == []


def test_lint_result_repr():
    result = LintResult()
    assert "LintResult" in repr(result)


def test_lint_issue_repr():
    issue = LintIssue("my_key", "some message", "warning")
    assert "WARNING" in repr(issue)
    assert "my_key" in repr(issue)


def test_lint_detects_lowercase_key():
    result = lint_env({"app_name": "myapp"})
    assert not result.is_clean
    keys_flagged = [i.key for i in result.issues]
    assert "app_name" in keys_flagged


def test_lint_detects_mixed_case_key():
    result = lint_env({"AppName": "myapp"})
    warnings = result.warnings
    assert any(i.key == "AppName" for i in warnings)


def test_lint_detects_key_starting_with_digit():
    result = lint_env({"1_BAD_KEY": "value"})
    errors = result.errors
    assert any(i.key == "1_BAD_KEY" for i in errors)


def test_lint_detects_newline_in_value():
    result = lint_env({"GOOD_KEY": "line1\nline2"})
    errors = result.errors
    assert any(i.key == "GOOD_KEY" for i in errors)


def test_lint_empty_value_is_warning_by_default():
    result = lint_env({"EMPTY_KEY": ""})
    assert any(i.severity == "warning" and i.key == "EMPTY_KEY" for i in result.issues)


def test_lint_empty_value_is_error_in_strict_mode():
    result = lint_env({"EMPTY_KEY": ""}, strict=True)
    assert any(i.severity == "error" and i.key == "EMPTY_KEY" for i in result.issues)


def test_lint_case_insensitive_duplicate_keys():
    result = lint_env({"MY_KEY": "a", "my_key": "b"})
    errors = result.errors
    assert len(errors) >= 1
    assert any("conflicts with" in i.message for i in errors)


def test_lint_errors_property_filters_correctly():
    result = lint_env({"bad_lower": "ok", "1_DIGIT": "x"})
    assert all(i.severity == "error" for i in result.errors)
    assert all(i.severity == "warning" for i in result.warnings)


def test_lint_multiple_issues_same_key():
    # lowercase + digit start
    result = lint_env({"1lower": "value"})
    flagged = [i.key for i in result.issues]
    assert flagged.count("1lower") >= 1


def test_lint_is_clean_false_when_issues_exist():
    result = lint_env({"bad_key": ""})
    assert not result.is_clean
