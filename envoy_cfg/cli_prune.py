"""CLI commands for pruning environment variable keys."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Dict

from envoy_cfg.prune import prune_empty, prune_keys, prune_pattern


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


def _emit(result_env: Dict[str, str], removed_keys, fmt: str, reason: str) -> None:
    if fmt == "json":
        print(json.dumps({"env": result_env, "removed": removed_keys, "reason": reason}, indent=2))
    else:
        for key, value in result_env.items():
            print(f"{key}={value}")
        if removed_keys:
            print(f"# pruned ({reason}): {', '.join(removed_keys)}", file=sys.stderr)


def cmd_prune(args: argparse.Namespace) -> None:
    env = _load_dotenv(args.file)

    if args.mode == "empty":
        result = prune_empty(env, strip_whitespace=not args.no_strip)
    elif args.mode == "keys":
        if not args.keys:
            print("error: --keys required for mode=keys", file=sys.stderr)
            sys.exit(1)
        result = prune_keys(env, args.keys)
    elif args.mode == "pattern":
        result = prune_pattern(env, prefix=args.prefix or None, suffix=args.suffix or None)
    else:
        print(f"error: unknown mode {args.mode!r}", file=sys.stderr)
        sys.exit(1)

    _emit(result.pruned, result.removed_keys, args.format, result.reason)


def register_prune_commands(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser("prune", help="Remove unwanted environment variable keys")
    p.add_argument("file", help="Path to .env file")
    p.add_argument(
        "--mode",
        choices=["empty", "keys", "pattern"],
        default="empty",
        help="Pruning strategy (default: empty)",
    )
    p.add_argument("--keys", nargs="+", metavar="KEY", help="Keys to remove (mode=keys)")
    p.add_argument("--prefix", help="Remove keys starting with this prefix (mode=pattern)")
    p.add_argument("--suffix", help="Remove keys ending with this suffix (mode=pattern)")
    p.add_argument("--no-strip", action="store_true", help="Do not strip whitespace before empty check")
    p.add_argument("--format", choices=["dotenv", "json"], default="dotenv", help="Output format")
    p.set_defaults(func=cmd_prune)
