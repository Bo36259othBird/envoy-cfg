"""CLI commands for the reorder feature."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Dict

from envoy_cfg.reorder import reorder_alphabetical, reorder_by_prefix, reorder_secrets_last


def _load_dotenv(path: str) -> Dict[str, str]:
    env: Dict[str, str] = {}
    for line in Path(path).read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            k, _, v = line.partition("=")
            env[k.strip()] = v.strip()
    return env


def cmd_reorder(args: argparse.Namespace) -> None:
    env = _load_dotenv(args.file)

    if args.strategy == "alpha":
        result = reorder_alphabetical(env, reverse=getattr(args, "reverse", False))
    elif args.strategy == "prefix":
        prefixes = args.prefixes.split(",") if args.prefixes else []
        result = reorder_by_prefix(env, prefixes)
    elif args.strategy == "secrets-last":
        result = reorder_secrets_last(env)
    else:
        print(f"Unknown strategy: {args.strategy}", file=sys.stderr)
        sys.exit(1)

    fmt = getattr(args, "format", "dotenv")
    if fmt == "json":
        print(json.dumps(result.reordered, indent=2))
    else:
        for k, v in result.reordered.items():
            print(f"{k}={v}")

    if getattr(args, "summary", False):
        print(
            f"# strategy={result.strategy} moved={result.moved} "
            f"identity={result.is_identity()}",
            file=sys.stderr,
        )


def register_reorder_commands(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser("reorder", help="Reorder env keys by a given strategy")
    p.add_argument("file", help="Path to .env file")
    p.add_argument(
        "--strategy",
        choices=["alpha", "prefix", "secrets-last"],
        default="alpha",
        help="Ordering strategy (default: alpha)",
    )
    p.add_argument("--reverse", action="store_true", help="Reverse alphabetical order")
    p.add_argument(
        "--prefixes",
        default="",
        help="Comma-separated prefix order for 'prefix' strategy",
    )
    p.add_argument(
        "--format",
        choices=["dotenv", "json"],
        default="dotenv",
        help="Output format",
    )
    p.add_argument("--summary", action="store_true", help="Print summary to stderr")
    p.set_defaults(func=cmd_reorder)
