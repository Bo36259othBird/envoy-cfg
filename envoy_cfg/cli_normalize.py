"""CLI commands for the normalize feature."""

import argparse
import json
import sys
from pathlib import Path

from envoy_cfg.normalize import normalize_keys, normalize_values


def _load_dotenv(path: str) -> dict:
    env = {}
    for line in Path(path).read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            k, _, v = line.partition("=")
            env[k] = v
    return env


def cmd_normalize(args: argparse.Namespace) -> None:
    """Normalize keys and/or values in a .env file."""
    env = _load_dotenv(args.file)

    result_env = dict(env)

    if args.keys:
        key_result = normalize_keys(
            result_env,
            uppercase=not args.no_uppercase,
            strip_whitespace=not args.no_strip,
        )
        result_env = key_result.normalized
        if args.verbose:
            for old_key, _, new_key in key_result.changes:
                print(f"  key: {old_key!r} -> {new_key!r}", file=sys.stderr)

    if args.values:
        val_result = normalize_values(
            result_env,
            strip_whitespace=not args.no_strip,
            collapse_newlines=not args.no_collapse,
        )
        result_env = val_result.normalized
        if args.verbose:
            for key, old_val, new_val in val_result.changes:
                print(f"  value [{key}]: {old_val!r} -> {new_val!r}", file=sys.stderr)

    if args.format == "json":
        print(json.dumps(result_env, indent=2))
    else:
        for k, v in sorted(result_env.items()):
            print(f"{k}={v}")


def register_normalize_commands(subparsers) -> None:
    p = subparsers.add_parser("normalize", help="Normalize env keys and/or values")
    p.add_argument("file", help="Path to .env file")
    p.add_argument("--keys", action="store_true", help="Normalize keys")
    p.add_argument("--values", action="store_true", help="Normalize values")
    p.add_argument("--no-uppercase", action="store_true", help="Skip uppercasing keys")
    p.add_argument("--no-strip", action="store_true", help="Skip whitespace stripping")
    p.add_argument("--no-collapse", action="store_true", help="Skip newline collapsing")
    p.add_argument("--format", choices=["dotenv", "json"], default="dotenv")
    p.add_argument("--verbose", action="store_true", help="Show changes on stderr")
    p.set_defaults(func=cmd_normalize)
