"""CLI commands for bulk key renaming."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from envoy_cfg.rename import rename_keys


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


def _parse_pairs(pairs: list[str]) -> dict:
    mapping: dict = {}
    for pair in pairs:
        if ":" not in pair:
            print(f"[warn] skipping invalid pair (expected old:new): {pair!r}", file=sys.stderr)
            continue
        old, _, new = pair.partition(":")
        mapping[old.strip()] = new.strip()
    return mapping


def cmd_rename(args: argparse.Namespace) -> None:
    env = _load_dotenv(args.file)
    mapping = _parse_pairs(args.pair)

    if not mapping:
        print("[error] no valid old:new pairs provided.", file=sys.stderr)
        sys.exit(1)

    result = rename_keys(env, mapping, overwrite=not args.no_overwrite)

    for old, new in result.renamed:
        print(f"[renamed] {old} -> {new}")
    for key in result.skipped:
        print(f"[skipped] {key}")

    if args.format == "json":
        print(json.dumps(result.env, indent=2))
    else:
        for k, v in result.env.items():
            print(f"{k}={v}")


def register_rename_commands(subparsers) -> None:
    p = subparsers.add_parser("rename", help="Bulk-rename environment variable keys")
    p.add_argument("file", help="Path to .env file")
    p.add_argument(
        "pair",
        nargs="+",
        metavar="OLD:NEW",
        help="Key rename pairs in OLD:NEW format",
    )
    p.add_argument(
        "--no-overwrite",
        action="store_true",
        default=False,
        help="Skip rename if the new key already exists",
    )
    p.add_argument(
        "--format",
        choices=["dotenv", "json"],
        default="dotenv",
        help="Output format (default: dotenv)",
    )
    p.set_defaults(func=cmd_rename)
