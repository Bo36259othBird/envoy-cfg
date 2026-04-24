import pytest
from envoy_cfg.diff import compute_diff
from envoy_cfg.diff_summary import summarize_diff, DiffSummary, DiffSummaryEntry


@pytest.fixture
def base_env():
    return {
        "APP_NAME": "myapp",
        "APP_ENV": "staging",
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
    }


@pytest.fixture
def updated_env():
    return {
        "APP_NAME": "myapp",
        "APP_ENV": "production",  # modified
        "DB_HOST": "db.prod.internal",  # modified
        "NEW_KEY": "new_value",  # added
        # DB_PORT removed
    }


def test_summarize_diff_returns_diff_summary(base_env, updated_env):
    result = compute_diff(base_env, updated_env)
    summary = summarize_diff(result)
    assert isinstance(summary, DiffSummary)


def test_summarize_diff_added_count(base_env, updated_env):
    result = compute_diff(base_env, updated_env)
    summary = summarize_diff(result)
    assert summary.added.count == 1
    assert "NEW_KEY" in summary.added.keys


def test_summarize_diff_removed_count(base_env, updated_env):
    result = compute_diff(base_env, updated_env)
    summary = summarize_diff(result)
    assert summary.removed.count == 1
    assert "DB_PORT" in summary.removed.keys


def test_summarize_diff_modified_count(base_env, updated_env):
    result = compute_diff(base_env, updated_env)
    summary = summarize_diff(result)
    assert summary.modified.count == 2
    assert "APP_ENV" in summary.modified.keys
    assert "DB_HOST" in summary.modified.keys


def test_summarize_diff_total_changes(base_env, updated_env):
    result = compute_diff(base_env, updated_env)
    summary = summarize_diff(result)
    assert summary.total_changes == 4


def test_summarize_diff_is_not_clean_when_changes_exist(base_env, updated_env):
    result = compute_diff(base_env, updated_env)
    summary = summarize_diff(result)
    assert not summary.is_clean


def test_summarize_diff_is_clean_for_identical_envs(base_env):
    result = compute_diff(base_env, base_env)
    summary = summarize_diff(result)
    assert summary.is_clean
    assert summary.total_changes == 0


def test_summarize_diff_to_dict_contains_expected_keys(base_env, updated_env):
    result = compute_diff(base_env, updated_env)
    summary = summarize_diff(result)
    d = summary.to_dict()
    assert "added" in d
    assert "removed" in d
    assert "modified" in d
    assert "total_changes" in d
    assert "is_clean" in d


def test_diff_summary_entry_to_dict():
    entry = DiffSummaryEntry(change_type="added", count=2, keys=["B_KEY", "A_KEY"])
    d = entry.to_dict()
    assert d["change_type"] == "added"
    assert d["count"] == 2
    assert d["keys"] == ["A_KEY", "B_KEY"]  # sorted


def test_summarize_diff_to_dict_added_keys_sorted(base_env, updated_env):
    result = compute_diff(base_env, updated_env)
    summary = summarize_diff(result)
    d = summary.to_dict()
    assert d["added"]["keys"] == sorted(d["added"]["keys"])
    assert d["removed"]["keys"] == sorted(d["removed"]["keys"])
    assert d["modified"]["keys"] == sorted(d["modified"]["keys"])


def test_summarize_diff_empty_envs():
    result = compute_diff({}, {})
    summary = summarize_diff(result)
    assert summary.is_clean
    assert summary.added.count == 0
    assert summary.removed.count == 0
    assert summary.modified.count == 0
