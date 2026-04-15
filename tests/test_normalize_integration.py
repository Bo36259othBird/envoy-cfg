"""Integration tests combining normalize with other modules."""

from envoy_cfg.normalize import normalize_keys, normalize_values
from envoy_cfg.lint import lint_env
from envoy_cfg.validate import validate_env
from envoy_cfg.masking import mask_env


def test_normalize_keys_then_lint_passes():
    env = {"app_host": "localhost", "db_port": "5432"}
    result = normalize_keys(env)
    lint_result = lint_env(result.normalized)
    # After uppercasing, lint should not complain about lowercase keys
    lowercase_issues = [
        i for i in lint_result.issues if "lowercase" in i.message.lower()
    ]
    assert len(lowercase_issues) == 0


def test_normalize_values_then_mask_hides_secrets():
    env = {"API_SECRET": "  my_token  ", "HOST": "  localhost  "}
    val_result = normalize_values(env)
    masked = mask_env(val_result.normalized)
    assert masked["API_SECRET"] != "my_token"
    assert masked["HOST"] == "localhost"


def test_normalize_keys_and_values_pipeline():
    env = {"  db_password  ": "  secret123  ", "  app_name  ": "  myapp  "}
    key_result = normalize_keys(env)
    val_result = normalize_values(key_result.normalized)
    assert "DB_PASSWORD" in val_result.normalized
    assert val_result.normalized["DB_PASSWORD"] == "secret123"
    assert val_result.normalized["APP_NAME"] == "myapp"


def test_normalize_then_validate_accepts_clean_keys():
    env = {"app_name": "myapp", "db_host": "localhost"}
    result = normalize_keys(env)
    v_result = validate_env(result.normalized)
    assert v_result.is_valid


def test_normalize_is_idempotent():
    env = {"APP_NAME": "myapp", "DB_HOST": "localhost"}
    first = normalize_keys(env)
    second = normalize_keys(first.normalized)
    assert first.normalized == second.normalized
    assert second.is_clean()
