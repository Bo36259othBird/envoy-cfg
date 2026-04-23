"""cli_omit.py — CLI commands for the omit feature."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from envoy_cfg.omit import omit_by_glob, omit_by_keys, omit_by_prefix


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


def cmd_omit(args: argparse.Namespace) -> None:
    env = _load_dotenv(args.file)

    if args.mode == "keys":
        result = omit_by_keys(env, args.targets)
    elif args.mode == "prefix":
        if not args.targets:
            print("error: --prefix requires exactly one target", file=sys.stderr)
            sys.exit(1)
        result = omit_by_prefix(env, args.targets[0])
    elif args.mode == "glob":
        if not args.targets:
            print("error: --glob requires exactly one pattern", file=sys.stderr)
            sys.exit(1)
        result = omit_by_glob(env, args.targets[0])
    else:
        print(f"error: unknown mode {args.mode!r}", file=sys.stderr)
        sys.exit(1)

    print(
        f"Omitted {len(result.omitted)} key(s) via strategy '{result.strategy}'.",
        file=sys.stderr,
    )

    if args.format == "json":
        print(json.dumps(result.env, indent=2))
    else:
        for k, v in result.env.items():
            print(f"{k}={v}")


def register_omit_commands(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser("omit", help="Remove keys from an env file")
    p.add_argument("file", help="Path to .env file")
    mode = p.add_mutually_exclusive_group(required=True)
    mode.add_argument("--keys", dest="mode", action="store_const", const="keys")
    mode.add_argument("--prefix", dest="mode", action="store_const", const="prefix")
    mode.add_argument("--glob", dest="mode", action="store_const", const="glob")
    p.add_argument("targets", nargs="+", help="Keys / prefix / glob pattern to omit")
    p.add_argument("--format", choices=["dotenv", "json"], default="dotenv")
    p.set_defaults(func=cmd_omit)
