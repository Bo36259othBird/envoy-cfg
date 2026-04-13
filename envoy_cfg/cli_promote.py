"""CLI commands for promoting env configs between targets."""

import argparse
from typing import Optional

from envoy_cfg.promote import EnvPromoter
from envoy_cfg.merge import MergeStrategy
from envoy_cfg.targets import TargetRegistry
from envoy_cfg.audit import AuditLog
from envoy_cfg.report import format_diff_report


def cmd_promote(
    args: argparse.Namespace,
    registry: TargetRegistry,
    audit_log: Optional[AuditLog] = None,
) -> int:
    """Promote env config from one target to another."""
    try:
        strategy = MergeStrategy(args.strategy)
    except ValueError:
        valid = ", ".join(s.value for s in MergeStrategy)
        print(f"[error] Invalid strategy '{args.strategy}'. Valid options: {valid}")
        return 1

    promoter = EnvPromoter(registry, audit_log=audit_log, dry_run=args.dry_run)
    result = promoter.promote(args.source, args.destination, strategy)

    if not result.success:
        print(f"[error] {result.message}")
        return 1

    prefix = "[dry-run] " if result.dry_run else ""
    print(f"{prefix}Promoted '{args.source}' -> '{args.destination}' ({strategy.value})")
    print(f"{prefix}{result.message}")

    if result.diff and result.diff.changes:
        print()
        print(format_diff_report(result.diff, mask_secrets=not args.show_secrets))
    else:
        print("No changes detected.")

    return 0


def register_promote_commands(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser("promote", help="Promote env config between targets")
    parser.add_argument("source", help="Source target name")
    parser.add_argument("destination", help="Destination target name")
    parser.add_argument(
        "--strategy",
        default="union",
        help="Merge strategy: union, ours, theirs (default: union)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without applying them",
    )
    parser.add_argument(
        "--show-secrets",
        action="store_true",
        help="Show secret values in diff output",
    )
    parser.set_defaults(func=cmd_promote)
