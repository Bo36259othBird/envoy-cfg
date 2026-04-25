"""Integration tests combining mask_diff with other envoy_cfg modules."""
import pytest
from envoy_cfg.mask_diff import mask_diff
from envoy_cfg.masking import mask_env
from envoy_cfg.diff import compute_diff
from envoy_cfg.normalize import normalize_keys


@pytest.fixture
def env_a():
    return {
        "APP_HOST": "localhost",
        "DB_PASSWORD": "old_pass",
        "APP_PORT": "5000",
        "AUTH_TOKEN": "tok_old",
    }


@pytest.fixture
def env_b():
    return {
        "APP_HOST": "prod.host",
        "DB_PASSWORD": "new_pass",
        "APP_PORT": "5000",
        "AUTH_TOKEN": "tok_new",
        "APP_DEBUG": "false",
    }


def test_mask_diff_masked_values_match_standalone_mask(env_a, env_b):
    result = mask_diff(env_a, env_b, mask_secrets=True)
    masked_b = mask_env(env_b)
    for entry in result.entries:
        if entry.masked and entry.new_value is not None:
            assert entry.new_value == masked_b.get(entry.key)


def test_mask_diff_change_count_matches_raw_diff(env_a, env_b):
    result = mask_diff(env_a, env_b)
    raw_diff = compute_diff(env_a, env_b)
    assert len(result.changed_entries) == len(raw_diff.changes)


def test_mask_diff_after_normalize_detects_same_changes():
    raw_a = {"app_host": "localhost", "db_password": "pass"}
    raw_b = {"app_host": "prod", "db_password": "pass"}
    norm_a = normalize_keys(raw_a).env
    norm_b = normalize_keys(raw_b).env
    result = mask_diff(norm_a, norm_b)
    modified = [e for e in result.changed_entries if e.change_type == "modified"]
    assert any(e.key == "APP_HOST" for e in modified)


def test_mask_diff_plain_keys_always_visible(env_a, env_b):
    result = mask_diff(env_a, env_b)
    host_entry = next((e for e in result.entries if e.key == "APP_HOST"), None)
    assert host_entry is not None
    assert host_entry.masked is False
    assert host_entry.new_value == "prod.host"


def test_mask_diff_identical_envs_zero_changes(env_a):
    result = mask_diff(env_a, env_a)
    assert result.is_clean
    assert len(result.changed_entries) == 0
