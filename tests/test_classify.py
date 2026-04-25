from __future__ import annotations

import pytest

from envoy_cfg.classify import ClassifyEntry, ClassifyResult, classify_env, _classify_value


@pytest.fixture
def base_env():
    return {
        "PORT": "8080",
        "RATIO": "0.75",
        "DEBUG": "true",
        "API_SECRET": "s3cr3t",
        "BASE_URL": "https://example.com",
        "CONFIG_PATH": "/etc/app/config",
        "APP_NAME": "myapp",
        "EMPTY_VAR": "",
    }


# --- _classify_value ---

def test_classify_value_empty():
    assert _classify_value("") == "empty"


def test_classify_value_bool_true():
    assert _classify_value("true") == "bool"


def test_classify_value_bool_yes():
    assert _classify_value("yes") == "bool"


def test_classify_value_int():
    assert _classify_value("42") == "int"


def test_classify_value_negative_int():
    assert _classify_value("-7") == "int"


def test_classify_value_float():
    assert _classify_value("3.14") == "float"


def test_classify_value_url():
    assert _classify_value("https://example.com") == "url"


def test_classify_value_http_url():
    assert _classify_value("http://localhost:5432") == "url"


def test_classify_value_path():
    assert _classify_value("/etc/config") == "path"


def test_classify_value_tilde_path():
    assert _classify_value("~/projects") == "path"


def test_classify_value_string_fallback():
    assert _classify_value("hello-world") == "string"


# --- classify_env ---

def test_classify_env_returns_classify_result(base_env):
    result = classify_env(base_env)
    assert isinstance(result, ClassifyResult)


def test_classify_env_entry_count(base_env):
    result = classify_env(base_env)
    assert len(result.entries) == len(base_env)


def test_classify_env_detects_int(base_env):
    result = classify_env(base_env)
    entry = next(e for e in result.entries if e.key == "PORT")
    assert entry.value_type == "int"


def test_classify_env_detects_float(base_env):
    result = classify_env(base_env)
    entry = next(e for e in result.entries if e.key == "RATIO")
    assert entry.value_type == "float"


def test_classify_env_detects_bool(base_env):
    result = classify_env(base_env)
    entry = next(e for e in result.entries if e.key == "DEBUG")
    assert entry.value_type == "bool"


def test_classify_env_detects_url(base_env):
    result = classify_env(base_env)
    entry = next(e for e in result.entries if e.key == "BASE_URL")
    assert entry.value_type == "url"


def test_classify_env_detects_path(base_env):
    result = classify_env(base_env)
    entry = next(e for e in result.entries if e.key == "CONFIG_PATH")
    assert entry.value_type == "path"


def test_classify_env_detects_empty(base_env):
    result = classify_env(base_env)
    entry = next(e for e in result.entries if e.key == "EMPTY_VAR")
    assert entry.value_type == "empty"


def test_classify_env_marks_secret_key(base_env):
    result = classify_env(base_env)
    entry = next(e for e in result.entries if e.key == "API_SECRET")
    assert entry.is_secret is True


def test_classify_env_plain_key_not_secret(base_env):
    result = classify_env(base_env)
    entry = next(e for e in result.entries if e.key == "APP_NAME")
    assert entry.is_secret is False


def test_classify_env_secret_keys_list(base_env):
    result = classify_env(base_env)
    assert "API_SECRET" in result.secret_keys


def test_classify_env_by_type_groups_correctly(base_env):
    result = classify_env(base_env)
    assert "PORT" in result.by_type["int"]
    assert "DEBUG" in result.by_type["bool"]


def test_classify_env_is_not_clean_with_secrets(base_env):
    result = classify_env(base_env)
    assert result.is_clean is False


def test_classify_env_is_clean_for_plain_strings():
    env = {"APP_NAME": "myapp", "REGION": "us-east-1"}
    result = classify_env(env)
    assert result.is_clean is True


def test_classify_entry_to_dict():
    entry = ClassifyEntry(key="FOO", value_type="string", is_secret=False)
    d = entry.to_dict()
    assert d == {"key": "FOO", "value_type": "string", "is_secret": False}


def test_classify_result_strategy_default(base_env):
    result = classify_env(base_env)
    assert result.strategy == "default"


def test_classify_result_entries_sorted(base_env):
    result = classify_env(base_env)
    keys = [e.key for e in result.entries]
    assert keys == sorted(keys)
