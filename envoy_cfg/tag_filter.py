"""Tag-based filtering utilities for deployment targets."""

from typing import List, Optional
from envoy_cfg.targets import DeploymentTarget


def filter_by_tags(
    targets: List[DeploymentTarget],
    required_tags: Optional[List[str]] = None,
    excluded_tags: Optional[List[str]] = None,
) -> List[DeploymentTarget]:
    """Return targets matching required tags and not matching excluded tags.

    Args:
        targets: List of DeploymentTarget instances to filter.
        required_tags: If provided, targets must have ALL of these tags.
        excluded_tags: If provided, targets must have NONE of these tags.

    Returns:
        Filtered list of DeploymentTarget instances.
    """
    result = []
    for target in targets:
        target_tags = set(target.tags or [])

        if required_tags:
            if not all(tag in target_tags for tag in required_tags):
                continue

        if excluded_tags:
            if any(tag in target_tags for tag in excluded_tags):
                continue

        result.append(target)

    return result


def tags_union(targets: List[DeploymentTarget]) -> List[str]:
    """Return a sorted list of all unique tags across the given targets."""
    all_tags: set = set()
    for target in targets:
        all_tags.update(target.tags or [])
    return sorted(all_tags)


def group_by_tag(targets: List[DeploymentTarget]) -> dict:
    """Group targets by each of their tags.

    Returns:
        A dict mapping tag -> list of targets that have that tag.
    """
    groups: dict = {}
    for target in targets:
        for tag in target.tags or []:
            groups.setdefault(tag, []).append(target)
    return groups
