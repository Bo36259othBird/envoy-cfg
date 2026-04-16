"""CLI commands for the pivot feature."""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

from envoy_cfg.pivot import pivot_env


def _load_dotenv(path: str) -> dict:
    env: dict = {}
    for line in Path(path).read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        env[k.strip()] = v.strip()
    return env


def cmd_pivot(args: argparse.Namespace) -> None:
    env = _load_dotenv(args.file)
    result = pivot_env(env, overwrite=args.overwrite, skip_empty=not args.keep_empty)

    if args.format == "json":
        print(json.dumps(result.pivoted, indent=2))
    else:
        for k, v in result.pivoted.items():
            print(f"{k}={v}")

    if result.skipped and not args.quiet:
        print(f"# skipped ({len(result.skipped)}): {', '.join(result.skipped)}",
              file=sys.stderr)


def register_pivot_commands(subparsers) -> None:
    p = subparsers.add_parser("pivot", help="Swap env keys and values")
    p.add_argument("file", help="Path to .env file")
    p.add_argument("--overwrite", action="store_true",
                   help="Overwrite on value collision (last key wins)")
    p.add_argument("--keep-empty", action="store_true",
                   help="Include keys with empty values in the pivot")
    p.add_argument("--format", choices=["dotenv", "json"], default="dotenv")
    p.add_argument("--quiet", action="store_true", help="Suppress skipped warnings")
    p.set_defaults(func=cmd_pivot)
