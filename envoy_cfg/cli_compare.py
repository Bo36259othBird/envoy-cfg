"""CLI commands for comparing environment configs across targets."""

import argparse
from typing import Any

from envoy_cfg.compare import EnvComparer
from envoy_cfg.report import format_diff_report
from envoy_cfg.targets import TargetRegistry


def cmd_compare(args: argparse.Namespace, registry: TargetRegistry) -> None:
    comparer = EnvComparer(registry, mask_secrets=not args.no_mask)
    result = comparer.compare(args.source, args.dest)

    if result is None:
        print(f"[error] One or both targets not found: {args.source!r}, {args.dest!r}")
        return

    print(f"Comparing {args.source!r} -> {args.dest!r}")
    if args.masked_note and result.masked:
        print("  (secret values are masked)")

    if not result.has_differences:
        print("  No differences found.")
        return

    print(format_diff_report(result.diff))


def cmd_compare_all(args: argparse.Namespace, registry: TargetRegistry) -> None:
    comparer = EnvComparer(registry, mask_secrets=not args.no_mask)
    env_filter = getattr(args, "environment", None)
    results = comparer.compare_all_to(args.dest, environment=env_filter)

    if not results:
        print(f"No targets to compare against {args.dest!r}.")
        return

    for result in results:
        print(f"\n--- {result.source!r} -> {result.dest if hasattr(result, 'dest') else args.dest!r} ---")
        if not result.has_differences:
            print("  No differences.")
        else:
            print(format_diff_report(result.diff))


def register_compare_commands(
    subparsers: Any, registry: TargetRegistry
) -> None:
    p_compare = subparsers.add_parser("compare", help="Compare two targets")
    p_compare.add_argument("source", help="Source target name")
    p_compare.add_argument("dest", help="Destination target name")
    p_compare.add_argument(
        "--no-mask", action="store_true", help="Show raw secret values"
    )
    p_compare.add_argument(
        "--masked-note", action="store_true", default=True,
        help="Print note when secrets are masked"
    )
    p_compare.set_defaults(func=lambda a: cmd_compare(a, registry))

    p_compare_all = subparsers.add_parser(
        "compare-all", help="Compare all targets to a destination"
    )
    p_compare_all.add_argument("dest", help="Destination target name")
    p_compare_all.add_argument("--environment", help="Filter by environment")
    p_compare_all.add_argument(
        "--no-mask", action="store_true", help="Show raw secret values"
    )
    p_compare_all.set_defaults(func=lambda a: cmd_compare_all(a, registry))
