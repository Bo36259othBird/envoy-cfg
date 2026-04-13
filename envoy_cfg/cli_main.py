"""Main CLI entry point for envoy-cfg."""

import argparse
import sys

from envoy_cfg.targets import TargetRegistry
from envoy_cfg.audit import AuditLog
from envoy_cfg.cli_snapshot import (
    cmd_snapshot_capture,
    cmd_snapshot_list,
    cmd_snapshot_show,
    cmd_snapshot_delete,
)
from envoy_cfg.cli_audit import register_audit_commands
from envoy_cfg.cli_export import register_export_commands
from envoy_cfg.cli_validate import register_validate_commands
from envoy_cfg.cli_promote import register_promote_commands


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="envoy-cfg",
        description="Manage and sync environment variable configs across deployment targets.",
    )
    parser.add_argument(
        "--version", action="version", version="%(prog)s 0.1.0"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Snapshot commands
    snap = subparsers.add_parser("snapshot", help="Manage env snapshots")
    snap_sub = snap.add_subparsers(dest="snapshot_cmd")
    snap_sub.add_parser("capture", help="Capture a snapshot").set_defaults(
        func=cmd_snapshot_capture
    )
    snap_sub.add_parser("list", help="List snapshots").set_defaults(
        func=cmd_snapshot_list
    )
    snap_sub.add_parser("show", help="Show a snapshot").set_defaults(
        func=cmd_snapshot_show
    )
    snap_sub.add_parser("delete", help="Delete a snapshot").set_defaults(
        func=cmd_snapshot_delete
    )

    register_audit_commands(subparsers)
    register_export_commands(subparsers)
    register_validate_commands(subparsers)
    register_promote_commands(subparsers)

    return parser


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if not args.command:
        parser.print_help()
        return 0

    if not hasattr(args, "func"):
        parser.print_help()
        return 1

    registry = TargetRegistry()
    audit_log = AuditLog()

    return args.func(args, registry, audit_log)


if __name__ == "__main__":
    sys.exit(main())
