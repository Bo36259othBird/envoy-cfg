"""CLI commands for mask_diff."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from envoy_cfg.mask_diff import mask_diff


def _load_dotenv(path: str) -> dict:
    env: dict = {}
    for line in Path(path).read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            k, _, v = line.partition("=")
            env[k.strip()] = v.strip()
    return env


def cmd_mask_diff(args: argparse.Namespace) -> None:
    base = _load_dotenv(args.base)
    updated = _load_dotenv(args.updated)
    result = mask_diff(base, updated, mask_secrets=not args.no_mask)

    if args.format == "json":
        data = {
            "total": result.total,
            "masked_count": result.masked_count,
            "is_clean": result.is_clean,
            "entries": [e.to_dict() for e in result.changed_entries],
        }
        print(json.dumps(data, indent=2))
        return

    if result.is_clean:
        print("No differences found.")
        return

    for entry in result.changed_entries:
        tag = " [masked]" if entry.masked else ""
        if entry.change_type == "added":
            print(f"+ {entry.key}={entry.new_value}{tag}")
        elif entry.change_type == "removed":
            print(f"- {entry.key}={entry.old_value}{tag}")
        elif entry.change_type == "modified":
            print(f"~ {entry.key}: {entry.old_value!r} -> {entry.new_value!r}{tag}")

    print(f"\nTotal keys: {result.total}, masked: {result.masked_count}")

    if args.fail_on_diff and not result.is_clean:
        sys.exit(1)


def register_mask_diff_commands(subparsers) -> None:
    p = subparsers.add_parser("mask-diff", help="Diff two env files with secret masking")
    p.add_argument("base", help="Base .env file")
    p.add_argument("updated", help="Updated .env file")
    p.add_argument(
        "--format", choices=["text", "json"], default="text", help="Output format"
    )
    p.add_argument(
        "--no-mask", action="store_true", help="Disable secret masking"
    )
    p.add_argument(
        "--fail-on-diff", action="store_true", help="Exit with code 1 if differences found"
    )
    p.set_defaults(func=cmd_mask_diff)
