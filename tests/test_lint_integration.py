"""Integration tests for lint + validate interaction."""
from envoy_cfg.lint import lint_env
from envoy_cfg.validate import validate_env


def test_lint_and_validate_both_pass_on_clean_env():
    env = {"APP_HOST": "localhost", "APP_PORT": "3000", "SECRET_KEY": "abc123"}
    lint_result = lint_env(env)
    validate_result = validate_env(env)
    assert lint_result.is_clean
    assert validate_result.is_valid


def test_lint_catches_style_issues_validate_misses():
    # validate only checks key format (alphanumeric/underscore), lint checks case
    env = {"app_host": "localhost"}  # valid key format but not UPPER_CASE
    lint_result = lint_env(env)
    assert not lint_result.is_clean
    assert any("UPPER_CASE" in i.message for i in lint_result.warnings)


def test_lint_empty_values_strict_and_validate_together():
    env = {"GOOD_KEY": "", "ANOTHER": "value"}
    lint_result = lint_env(env, strict=True)
    validate_result = validate_env(env)
    # lint strict: empty value → error
    assert any(i.severity == "error" and i.key == "GOOD_KEY" for i in lint_result.issues)
    # validate doesn't care about empty values
    assert validate_result.is_valid


def test_lint_newline_in_value_is_always_error():
    env = {"MULTILINE": "line1\nline2"}
    result = lint_env(env)
    errors = result.errors
    assert any(i.key == "MULTILINE" for i in errors)


def test_lint_full_bad_env_accumulates_all_issues():
    env = {
        "lower_key": "",
        "1DIGIT": "x",
        "NEWLINE_VAL": "a\nb",
    }
    result = lint_env(env, strict=True)
    keys = [i.key for i in result.issues]
    assert "lower_key" in keys
    assert "1DIGIT" in keys
    assert "NEWLINE_VAL" in keys
    assert not result.is_clean
