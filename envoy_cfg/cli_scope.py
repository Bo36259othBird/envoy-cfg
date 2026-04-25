"""CLI commands for scope-based env filtering."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Dict

from envoy_cfg.scope import scope_by_keys, scope_by_prefix


def _load_dotenv(path: str) -> Dict[str, str]:
    """Parse a .env file into a dict, skipping comments and blank lines.

    Raises:
        FileNotFoundError: If the given path does not exist.
        ValueError: If the file cannot be decoded as text.
    """
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"env file not found: {path}")
    env: Dict[str, str] = {}
    for line in p.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        env[k.strip()] = v.strip().strip('"').strip("'")
    return env


def cmd_scope_prefix(args: argparse.Namespace) -> None:
    env = _load_dotenv(args.file)
    result = scope_by_prefix(
        env,
        prefix=args.prefix,
        strip_prefix=args.strip,
        scope_name=args.name or None,
    )

    if args.format == "json":
        print(json.dumps(result.scoped, indent=2))
    else:
        for k, v in sorted(result.scoped.items()):
            print(f"{k}={v}")

    print(
        f"# scope '{result.scope_name}': {len(result.scoped)} kept, "
        f"{len(result.excluded_keys)} excluded",
        file=sys.stderr,
    )


def cmd_scope_keys(args: argparse.Namespace) -> None:
    env = _load_dotenv(args.file)
    keys = [k.strip() for k in args.keys.split(",") if k.strip()]
    result = scope_by_keys(env, keys=keys, scope_name=args.name or "custom")

    if args.format == "json":
        print(json.dumps(result.scoped, indent=2))
    else:
        for k, v in sorted(result.scoped.items()):
            print(f"{k}={v}")

    missing = [k for k in keys if k not in env]
    if missing:
        print(f"# warning: keys not found: {', '.join(missing)}", file=sys.stderr)
    print(
        f"# scope '{result.scope_name}': {len(result.scoped)} kept, "
        f"{len(result.excluded_keys)} excluded",
        file=sys.stderr,
    )


def register_scope_commands(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    # scope prefix
    p_prefix = subparsers.add_parser("scope-prefix", help="Filter env vars by key prefix")
    p_prefix.add_argument("file", help="Path to .env file")
    p_prefix.add_argument("prefix", help="Key prefix to match (e.g. APP_)")
    p_prefix.add_argument("--strip", action="store_true", help="Strip prefix from output keys")
    p_prefix.add_argument("--name", default="", help="Scope label for output")
    p_prefix.add_argument("--format", choices=["dotenv", "json"], default="dotenv")
    p_prefix.set_defaults(func=cmd_scope_prefix)

    # scope keys
    p_keys = subparsers.add_parser("scope-keys", help="Filter env vars to an explicit key list")
    p_keys.add_argument("file", help="Path to .env file")
    p_keys.add_argument("keys", help="Comma-separated list of keys to keep")
    p_keys.add_argument("--name", default="custom", help="Scope label for output")
    p_keys.add_argument("--format", choices=["dotenv", "json"], default="dotenv")
    p_keys.set_defaults(func=cmd_scope_keys)
