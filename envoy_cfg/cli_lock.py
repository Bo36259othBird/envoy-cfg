"""CLI commands for locking and unlocking deployment targets."""

from __future__ import annotations

import argparse

from envoy_cfg.lock import LockStore


def cmd_lock(args: argparse.Namespace) -> None:
    store = LockStore(args.lock_file)
    try:
        entry = store.lock(args.target, args.environment, reason=args.reason)
        print(f"Locked: {entry}")
    except ValueError as exc:
        print(f"Error: {exc}")


def cmd_unlock(args: argparse.Namespace) -> None:
    store = LockStore(args.lock_file)
    removed = store.unlock(args.target, args.environment)
    if removed:
        print(f"Unlocked: {args.target}/{args.environment}")
    else:
        print(f"No lock found for {args.target}/{args.environment}")


def cmd_lock_list(args: argparse.Namespace) -> None:
    store = LockStore(args.lock_file)
    locks = store.list_locks()
    if not locks:
        print("No locks active.")
        return
    for entry in locks:
        reason_str = f"  reason: {entry.reason}" if entry.reason else ""
        print(f"  {entry.target_name}/{entry.environment}{reason_str}")


def register_lock_commands(subparsers: argparse._SubParsersAction, lock_file: str) -> None:
    lock_parser = subparsers.add_parser("lock", help="Lock a deployment target")
    lock_parser.add_argument("target", help="Target name")
    lock_parser.add_argument("environment", help="Environment (e.g. production)")
    lock_parser.add_argument("--reason", default=None, help="Optional reason for locking")
    lock_parser.add_argument("--lock-file", default=lock_file)
    lock_parser.set_defaults(func=cmd_lock)

    unlock_parser = subparsers.add_parser("unlock", help="Unlock a deployment target")
    unlock_parser.add_argument("target", help="Target name")
    unlock_parser.add_argument("environment", help="Environment")
    unlock_parser.add_argument("--lock-file", default=lock_file)
    unlock_parser.set_defaults(func=cmd_unlock)

    list_parser = subparsers.add_parser("lock-list", help="List active locks")
    list_parser.add_argument("--lock-file", default=lock_file)
    list_parser.set_defaults(func=cmd_lock_list)
