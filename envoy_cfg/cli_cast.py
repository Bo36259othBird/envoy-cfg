"""CLI commands for envoy-cfg cast feature."""
from __future__ import annotations

import json
from pathlib import Path
from typing import List

from envoy_cfg.cast import cast_env


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


def _parse_schema(pairs: List[str]) -> dict:
    """Parse KEY=TYPE pairs into a dict."""
    schema: dict = {}
    for pair in pairs:
        if "=" not in pair:
            raise ValueError(f"Invalid schema pair: {pair!r}. Expected KEY=TYPE.")
        k, _, v = pair.partition("=")
        schema[k.strip()] = v.strip()
    return schema


def cmd_cast(args) -> None:
    env = _load_dotenv(args.file)
    schema = _parse_schema(args.type or [])

    result = cast_env(env, schema)

    if args.format == "json":
        print(json.dumps(result.env, indent=2, default=str))
    else:
        for k, v in result.env.items():
            print(f"{k}={v}")

    if result.errors and not getattr(args, "quiet", False):
        import sys
        for key, msg in result.errors.items():
            print(f"[cast error] {key}: {msg}", file=sys.stderr)


def register_cast_commands(subparsers) -> None:
    p = subparsers.add_parser("cast", help="Cast env variable values to typed representations")
    p.add_argument("file", help="Path to .env file")
    p.add_argument(
        "--type",
        metavar="KEY=TYPE",
        action="append",
        help="Type hint for a key, e.g. PORT=int. Repeatable.",
    )
    p.add_argument(
        "--format",
        choices=["dotenv", "json"],
        default="dotenv",
        help="Output format (default: dotenv)",
    )
    p.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress cast error messages on stderr",
    )
    p.set_defaults(func=cmd_cast)
