"""CLI commands for tag-based target filtering."""

import argparse
from envoy_cfg.targets import TargetRegistry
from envoy_cfg.tag_filter import filter_by_tags, tags_union, group_by_tag


def cmd_tags_list(args: argparse.Namespace, registry: TargetRegistry) -> None:
    """List all unique tags across registered targets."""
    all_targets = registry.list_targets()
    union = tags_union(all_targets)
    if not union:
        print("No tags found.")
        return
    for tag in union:
        print(tag)


def cmd_tags_filter(args: argparse.Namespace, registry: TargetRegistry) -> None:
    """List targets matching tag filters."""
    required = args.require or []
    excluded = args.exclude or []

    all_targets = registry.list_targets()
    matched = filter_by_tags(all_targets, required_tags=required, excluded_tags=excluded)

    if not matched:
        print("No targets matched the given tag filters.")
        return

    for target in matched:
        tag_str = ", ".join(sorted(target.tags or []))
        print(f"  {target.name} [{target.environment}] tags=[{tag_str}]")


def cmd_tags_group(args: argparse.Namespace, registry: TargetRegistry) -> None:
    """Show targets grouped by tag."""
    all_targets = registry.list_targets()
    groups = group_by_tag(all_targets)

    if not groups:
        print("No tagged targets found.")
        return

    for tag in sorted(groups):
        print(f"[{tag}]")
        for target in groups[tag]:
            print(f"  - {target.name} ({target.environment})")


def register_tag_filter_commands(subparsers) -> None:
    """Register tag filter subcommands onto a subparsers object."""
    tags_parser = subparsers.add_parser("tags", help="Tag-based target filtering")
    tags_sub = tags_parser.add_subparsers(dest="tags_cmd")

    tags_sub.add_parser("list", help="List all unique tags")

    filter_p = tags_sub.add_parser("filter", help="Filter targets by tags")
    filter_p.add_argument("--require", nargs="+", metavar="TAG", help="Tags targets must have")
    filter_p.add_argument("--exclude", nargs="+", metavar="TAG", help="Tags targets must not have")

    tags_sub.add_parser("group", help="Group targets by tag")
