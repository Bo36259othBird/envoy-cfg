"""Tests for envoy_cfg.tag_filter module."""

import pytest
from envoy_cfg.targets import DeploymentTarget, TargetRegistry
from envoy_cfg.tag_filter import filter_by_tags, tags_union, group_by_tag


@pytest.fixture
def targets():
    return [
        DeploymentTarget(name="web-prod", environment="production", tags=["web", "critical"]),
        DeploymentTarget(name="api-prod", environment="production", tags=["api", "critical"]),
        DeploymentTarget(name="web-staging", environment="staging", tags=["web"]),
        DeploymentTarget(name="worker", environment="production", tags=[]),
    ]


def test_filter_by_required_tag(targets):
    result = filter_by_tags(targets, required_tags=["web"])
    names = [t.name for t in result]
    assert "web-prod" in names
    assert "web-staging" in names
    assert "api-prod" not in names
    assert "worker" not in names


def test_filter_by_multiple_required_tags(targets):
    result = filter_by_tags(targets, required_tags=["web", "critical"])
    names = [t.name for t in result]
    assert names == ["web-prod"]


def test_filter_by_excluded_tag(targets):
    result = filter_by_tags(targets, excluded_tags=["critical"])
    names = [t.name for t in result]
    assert "web-prod" not in names
    assert "api-prod" not in names
    assert "web-staging" in names
    assert "worker" in names


def test_filter_combined_require_and_exclude(targets):
    result = filter_by_tags(targets, required_tags=["web"], excluded_tags=["critical"])
    names = [t.name for t in result]
    assert names == ["web-staging"]


def test_filter_no_criteria_returns_all(targets):
    result = filter_by_tags(targets)
    assert len(result) == len(targets)


def test_filter_returns_empty_when_no_match(targets):
    result = filter_by_tags(targets, required_tags=["nonexistent"])
    assert result == []


def test_tags_union_returns_sorted_unique(targets):
    union = tags_union(targets)
    assert union == ["api", "critical", "web"]


def test_tags_union_empty_targets():
    assert tags_union([]) == []


def test_group_by_tag_keys(targets):
    groups = group_by_tag(targets)
    assert set(groups.keys()) == {"web", "api", "critical"}


def test_group_by_tag_membership(targets):
    groups = group_by_tag(targets)
    web_names = [t.name for t in groups["web"]]
    assert "web-prod" in web_names
    assert "web-staging" in web_names


def test_group_by_tag_empty_targets():
    assert group_by_tag([]) == {}


def test_filter_target_with_no_tags_excluded_by_required(targets):
    result = filter_by_tags(targets, required_tags=["web"])
    names = [t.name for t in result]
    assert "worker" not in names


def test_group_by_tag_critical_members(targets):
    """Targets tagged 'critical' should include both web-prod and api-prod."""
    groups = group_by_tag(targets)
    critical_names = [t.name for t in groups["critical"]]
    assert "web-prod" in critical_names
    assert "api-prod" in critical_names
    assert "web-staging" not in critical_names
    assert "worker" not in critical_names


def test_filter_excluded_tag_not_present_returns_all(targets):
    """Excluding a tag that no target has should return all targets."""
    result = filter_by_tags(targets, excluded_tags=["nonexistent"])
    assert len(result) == len(targets)
