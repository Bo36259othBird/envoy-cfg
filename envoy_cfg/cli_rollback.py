"""CLI commands for rollback operations."""

import argparse
from typing import Optional

from envoy_cfg.rollback import EnvRollback
from envoy_cfg.snapshot import SnapshotStore
from envoy_cfg.targets import TargetRegistry
from envoy_cfg.audit import AuditLog


def cmd_rollback(
    args: argparse.Namespace,
    registry: TargetRegistry,
    store: SnapshotStore,
    audit_log: Optional[AuditLog] = None,
) -> None:
    rollback = EnvRollback(registry, store, audit_log=audit_log)

    if args.dry_run:
        rollback.set_dry_run(True)
        print("[dry-run] No changes will be applied.")

    result = rollback.rollback(args.target, args.snapshot_id)

    if not result.applied and not result.dry_run:
        print(f"[error] {result.message}")
        return

    label = "[dry-run]" if result.dry_run else "[rollback]"
    print(f"{label} Target: {result.target_name}")
    print(f"{label} Snapshot: {result.snapshot_id}")
    print(f"{label} Keys to restore: {len(result.keys_restored)}")
    for key in sorted(result.keys_restored):
        print(f"  - {key}")
    print(f"{label} {result.message}")


def register_rollback_commands(
    subparsers: argparse._SubParsersAction,
) -> None:
    parser = subparsers.add_parser(
        "rollback", help="Restore a target's env from a snapshot"
    )
    parser.add_argument("target", help="Target name to roll back")
    parser.add_argument("snapshot_id", help="Snapshot ID to restore from")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=False,
        help="Preview changes without applying",
    )
    parser.set_defaults(cmd="rollback")
