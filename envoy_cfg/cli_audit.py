"""CLI commands for viewing and managing the audit log."""

import argparse
import os
from envoy_cfg.audit import AuditLog

DEFAULT_LOG_PATH = os.environ.get("ENVOY_AUDIT_LOG", "audit_log.json")


def cmd_audit_list(args: argparse.Namespace) -> None:
    """List audit log entries with optional filters."""
    log = AuditLog(log_path=DEFAULT_LOG_PATH)
    entries = log.all()

    if args.target:
        entries = [e for e in entries if e.target_name == args.target]
    if args.environment:
        entries = [e for e in entries if e.environment == args.environment]
    if args.action:
        entries = [e for e in entries if e.action == args.action]

    if not entries:
        print("No audit entries found.")
        return

    for entry in entries:
        print(repr(entry))
        if args.verbose and entry.note:
            print(f"  Note: {entry.note}")


def cmd_audit_clear(args: argparse.Namespace) -> None:
    """Clear all audit log entries."""
    if not args.yes:
        confirm = input("Are you sure you want to clear the audit log? [y/N]: ")
        if confirm.strip().lower() != "y":
            print("Aborted.")
            return
    log = AuditLog(log_path=DEFAULT_LOG_PATH)
    log.clear()
    print("Audit log cleared.")


def register_audit_commands(subparsers: argparse._SubParsersAction) -> None:
    """Register audit subcommands onto the given subparser."""
    audit_parser = subparsers.add_parser("audit", help="Manage audit log")
    audit_sub = audit_parser.add_subparsers(dest="audit_cmd")

    list_parser = audit_sub.add_parser("list", help="List audit log entries")
    list_parser.add_argument("--target", help="Filter by target name")
    list_parser.add_argument("--environment", help="Filter by environment")
    list_parser.add_argument("--action", help="Filter by action type")
    list_parser.add_argument("-v", "--verbose", action="store_true", help="Show notes")
    list_parser.set_defaults(func=cmd_audit_list)

    clear_parser = audit_sub.add_parser("clear", help="Clear the audit log")
    clear_parser.add_argument("-y", "--yes", action="store_true", help="Skip confirmation")
    clear_parser.set_defaults(func=cmd_audit_clear)
