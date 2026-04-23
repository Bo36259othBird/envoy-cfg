"""Integration tests: prefix operations compose with other envoy_cfg modules."""
import pytest
from envoy_cfg.prefix import add_prefix, remove_prefix
from envoy_cfg.diff import compute_diff
from envoy_cfg.masking import mask_env
from envoy_cfg.normalize import normalize_keys


@pytest.fixture
def base_env():
    return {
        "HOST": "localhost",
        "PORT": "5432",
        "SECRET_KEY": "topsecret",
        "API_TOKEN": "abc123",
    }


def test_add_then_remove_is_identity(base_env):
    added = add_prefix(base_env, "TMP_")
    restored = remove_prefix(added.env, "TMP_")
    assert restored.env == base_env


def test_add_prefix_then_diff_shows_renamed_keys(base_env):
    prefixed = add_prefix(base_env, "PROD_").env
    diff = compute_diff(base_env, prefixed)
    # original keys removed, prefixed keys added
    added_keys = {c.key for c in diff.added()}
    removed_keys = {c.key for c in diff.removed()}
    assert "PROD_HOST" in added_keys
    assert "HOST" in removed_keys


def test_add_prefix_then_mask_hides_secrets(base_env):
    prefixed = add_prefix(base_env, "APP_").env
    masked = mask_env(prefixed)
    # secret keys still detectable after prefix
    assert masked.get("APP_SECRET_KEY") != "topsecret"
    assert masked.get("APP_HOST") == "localhost"


def test_normalize_then_add_prefix(base_env):
    norm = normalize_keys(base_env)
    result = add_prefix(norm.env, "SVC_")
    assert all(k.startswith("SVC_") for k in result.env)


def test_add_prefix_subset_does_not_touch_others(base_env):
    result = add_prefix(base_env, "DB_", keys=["HOST", "PORT"])
    assert "DB_HOST" in result.env
    assert "DB_PORT" in result.env
    assert "SECRET_KEY" in result.env
    assert "API_TOKEN" in result.env
    assert "HOST" not in result.env
    assert "PORT" not in result.env
