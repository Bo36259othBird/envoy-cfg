"""Tests for envoy_cfg.mask_report."""

import pytest
from envoy_cfg.mask_report import build_mask_report, MaskReport, MaskReportEntry


@pytest.fixture
def mixed_env():
    return {
        "APP_NAME": "myapp",
        "DB_PASSWORD": "s3cr3t",
        "API_KEY": "abc123",
        "PORT": "8080",
        "SECRET_TOKEN": "topsecret",
    }


def test_build_mask_report_returns_mask_report(mixed_env):
    report = build_mask_report(mixed_env)
    assert isinstance(report, MaskReport)


def test_build_mask_report_total_equals_env_size(mixed_env):
    report = build_mask_report(mixed_env)
    assert report.total == len(mixed_env)


def test_build_mask_report_detects_secret_keys(mixed_env):
    report = build_mask_report(mixed_env)
    assert "DB_PASSWORD" in report.masked_keys()
    assert "API_KEY" in report.masked_keys()
    assert "SECRET_TOKEN" in report.masked_keys()


def test_build_mask_report_plain_keys_not_masked(mixed_env):
    report = build_mask_report(mixed_env)
    plain = {e.key for e in report.entries if not e.masked}
    assert "APP_NAME" in plain
    assert "PORT" in plain


def test_masked_count_matches_secret_keys(mixed_env):
    report = build_mask_report(mixed_env)
    assert report.masked_count == len(report.masked_keys())


def test_plain_count_plus_masked_equals_total(mixed_env):
    report = build_mask_report(mixed_env)
    assert report.plain_count + report.masked_count == report.total


def test_is_clean_for_env_with_no_secrets():
    env = {"APP_NAME": "myapp", "PORT": "8080"}
    report = build_mask_report(env)
    assert report.is_clean


def test_is_not_clean_for_env_with_secrets(mixed_env):
    report = build_mask_report(mixed_env)
    assert not report.is_clean


def test_masked_value_is_not_original_for_secret(mixed_env):
    report = build_mask_report(mixed_env)
    entry = next(e for e in report.entries if e.key == "DB_PASSWORD")
    assert entry.masked_value != "s3cr3t"


def test_original_length_recorded_correctly(mixed_env):
    report = build_mask_report(mixed_env)
    entry = next(e for e in report.entries if e.key == "DB_PASSWORD")
    assert entry.original_length == len("s3cr3t")


def test_entry_to_dict_has_expected_keys(mixed_env):
    report = build_mask_report(mixed_env)
    d = report.entries[0].to_dict()
    assert set(d.keys()) == {"key", "masked", "original_length", "masked_value"}


def test_entry_repr_contains_status():
    entry = MaskReportEntry(key="API_KEY", masked=True, original_length=6, masked_value="***")
    assert "SECRET" in repr(entry)


def test_plain_entry_repr_contains_plain():
    entry = MaskReportEntry(key="PORT", masked=False, original_length=4, masked_value="8080")
    assert "plain" in repr(entry)


def test_report_repr_contains_counts(mixed_env):
    report = build_mask_report(mixed_env)
    r = repr(report)
    assert "masked=" in r
    assert "total=" in r


def test_empty_env_produces_clean_report():
    report = build_mask_report({})
    assert report.total == 0
    assert report.is_clean
    assert report.masked_keys() == []
