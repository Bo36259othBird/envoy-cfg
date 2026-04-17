from envoy_cfg.copy import copy_keys
from envoy_cfg.masking import mask_env
from envoy_cfg.diff import compute_diff


def test_copy_then_diff_shows_added_key():
    source = {"NEW_FEATURE": "enabled", "LOG_LEVEL": "debug"}
    dest = {"APP": "myapp"}
    result = copy_keys(source, dest, keys=["NEW_FEATURE"])
    merged = {**dest, **result.copied}
    diff = compute_diff(dest, merged)
    added_keys = [c.key for c in diff.added()]
    assert "NEW_FEATURE" in added_keys


def test_copy_then_mask_hides_secret():
    source = {"SECRET_KEY": "topsecret", "HOST": "localhost"}
    dest = {"APP": "myapp"}
    result = copy_keys(source, dest, keys=["SECRET_KEY", "HOST"])
    merged = {**dest, **result.copied}
    masked = mask_env(merged)
    assert masked["SECRET_KEY"] != "topsecret"
    assert masked["HOST"] == "localhost"


def test_copy_multiple_keys_all_present():
    source = {"A": "1", "B": "2", "C": "3"}
    dest = {}
    result = copy_keys(source, dest, keys=["A", "B", "C"])
    assert len(result.copied) == 3
    assert result.is_clean()


def test_copy_overwrite_then_diff_shows_modified():
    source = {"DB_HOST": "new-host"}
    dest = {"DB_HOST": "old-host"}
    result = copy_keys(source, dest, keys=["DB_HOST"], overwrite=True)
    merged = {**dest, **result.copied}
    diff = compute_diff(dest, merged)
    modified_keys = [c.key for c in diff.modified()]
    assert "DB_HOST" in modified_keys


def test_copy_prefix_does_not_affect_source():
    source = {"KEY": "value"}
    dest = {}
    result = copy_keys(source, dest, keys=["KEY"], prefix="APP_")
    assert "APP_KEY" in result.copied
    assert "KEY" not in result.copied
