from __future__ import annotations

import argparse
import json
import sys

from envoy_cfg.diff import compute_diff
from envoy_cfg.diff_summary import summarize_diff


def _load_dotenv(path: str) -> dict:
    env: dict = {}
    try:
        with open(path) as fh:
            for line in fh:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, _, value = line.partition("=")
                env[key.strip()] = value.strip()
    except FileNotFoundError:
        print(f"error: file not found: {path}", file=sys.stderr)
        sys.exit(1)
    return env


def cmd_diff_summary(args: argparse.Namespace) -> None:
    base = _load_dotenv(args.base)
    updated = _load_dotenv(args.updated)

    diff_result = compute_diff(base, updated)
    summary = summarize_diff(diff_result)

    if args.format == "json":
        print(json.dumps(summary.to_dict(), indent=2))
        return

    if summary.is_clean:
        print("No differences found.")
        return

    print(f"Diff summary: {summary.total_changes} change(s)")
    if summary.added.count:
        print(f"  Added    ({summary.added.count}): {', '.join(sorted(summary.added.keys))}")
    if summary.removed.count:
        print(f"  Removed  ({summary.removed.count}): {', '.join(sorted(summary.removed.keys))}")
    if summary.modified.count:
        print(f"  Modified ({summary.modified.count}): {', '.join(sorted(summary.modified.keys))}")
    if summary.unchanged_count:
        print(f"  Unchanged: {summary.unchanged_count}")

    if args.strict and not summary.is_clean:
        sys.exit(1)


def register_diff_summary_commands(subparsers) -> None:
    p = subparsers.add_parser("diff-summary", help="Show a structured summary of env differences")
    p.add_argument("base", help="Base .env file")
    p.add_argument("updated", help="Updated .env file")
    p.add_argument(
        "--format", choices=["text", "json"], default="text", help="Output format"
    )
    p.add_argument(
        "--strict", action="store_true", help="Exit with code 1 if differences exist"
    )
    p.set_defaults(func=cmd_diff_summary)
