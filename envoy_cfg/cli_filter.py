"""CLI commands for filtering environment variables."""

import argparse
import json
import sys
from pathlib import Path

from envoy_cfg.filter import (
    filter_by_value_glob,
    filter_by_value_regex,
    filter_by_empty_values,
    filter_by_key_glob,
)


def _load_dotenv(path: str) -> dict:
    env = {}
    for line in Path(path).read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        env[k.strip()] = v.strip()
    return env


def cmd_filter(args: argparse.Namespace) -> None:
    env = _load_dotenv(args.file)

    if args.mode == "value-glob":
        result = filter_by_value_glob(env, args.pattern)
    elif args.mode == "value-regex":
        result = filter_by_value_regex(env, args.pattern)
    elif args.mode == "key-glob":
        result = filter_by_key_glob(env, args.pattern)
    elif args.mode == "empty":
        result = filter_by_empty_values(env, keep_empty=True)
    elif args.mode == "non-empty":
        result = filter_by_empty_values(env, keep_empty=False)
    else:
        print(f"Unknown filter mode: {args.mode}", file=sys.stderr)
        sys.exit(1)

    output = result.selected if not args.excluded else result.excluded

    if args.format == "json":
        print(json.dumps(output, indent=2))
    else:
        for k, v in output.items():
            print(f"{k}={v}")

    print(
        f"# strategy={result.strategy} selected={len(result.selected)} excluded={len(result.excluded)}",
        file=sys.stderr,
    )


def register_filter_commands(subparsers) -> None:
    p = subparsers.add_parser("filter", help="Filter env vars by key or value patterns")
    p.add_argument("file", help="Path to .env file")
    p.add_argument(
        "--mode",
        choices=["value-glob", "value-regex", "key-glob", "empty", "non-empty"],
        default="non-empty",
        help="Filter strategy",
    )
    p.add_argument("--pattern", default="*", help="Glob or regex pattern")
    p.add_argument("--excluded", action="store_true", help="Output excluded keys instead")
    p.add_argument("--format", choices=["dotenv", "json"], default="dotenv")
    p.set_defaults(func=cmd_filter)
