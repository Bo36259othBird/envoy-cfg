from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path
from typing import Dict

from envoy_cfg.prefix import add_prefix, remove_prefix


def _load_dotenv(path: str) -> Dict[str, str]:
    env: Dict[str, str] = {}
    for line in Path(path).read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        env[k.strip()] = v.strip()
    return env


def cmd_prefix_add(args: argparse.Namespace) -> None:
    env = _load_dotenv(args.file)
    keys = args.keys.split(",") if args.keys else None
    result = add_prefix(
        env,
        args.prefix,
        skip_existing=not args.no_skip,
        keys=keys,
    )
    if args.format == "json":
        print(json.dumps(result.env, indent=2))
    else:
        for k, v in result.env.items():
            print(f"{k}={v}")
    print(
        f"# prefix_add: affected={len(result.affected)} skipped={len(result.skipped)}",
        file=sys.stderr,
    )


def cmd_prefix_remove(args: argparse.Namespace) -> None:
    env = _load_dotenv(args.file)
    keys = args.keys.split(",") if args.keys else None
    result = remove_prefix(env, args.prefix, keys=keys)
    if args.format == "json":
        print(json.dumps(result.env, indent=2))
    else:
        for k, v in result.env.items():
            print(f"{k}={v}")
    print(
        f"# prefix_remove: affected={len(result.affected)} skipped={len(result.skipped)}",
        file=sys.stderr,
    )


def register_prefix_commands(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p_add = subparsers.add_parser("prefix-add", help="Add a prefix to env keys")
    p_add.add_argument("file", help="Path to .env file")
    p_add.add_argument("prefix", help="Prefix string to add")
    p_add.add_argument("--keys", default=None, help="Comma-separated subset of keys")
    p_add.add_argument("--no-skip", action="store_true", help="Overwrite if prefixed key already exists")
    p_add.add_argument("--format", choices=["dotenv", "json"], default="dotenv")
    p_add.set_defaults(func=cmd_prefix_add)

    p_rm = subparsers.add_parser("prefix-remove", help="Remove a prefix from env keys")
    p_rm.add_argument("file", help="Path to .env file")
    p_rm.add_argument("prefix", help="Prefix string to remove")
    p_rm.add_argument("--keys", default=None, help="Comma-separated subset of keys")
    p_rm.add_argument("--format", choices=["dotenv", "json"], default="dotenv")
    p_rm.set_defaults(func=cmd_prefix_remove)
