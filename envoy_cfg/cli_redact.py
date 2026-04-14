"""CLI commands for the redact feature."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Dict

from envoy_cfg.redact import redact_env


def _load_dotenv(path: str) -> Dict[str, str]:
    env: Dict[str, str] = {}
    for line in Path(path).read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            key, _, value = line.partition("=")
            env[key.strip()] = value.strip().strip('"')
    return env


def cmd_redact(args: argparse.Namespace) -> None:
    """Read a .env file and print it with sensitive values redacted."""
    try:
        env = _load_dotenv(args.file)
    except FileNotFoundError:
        print(f"Error: file not found: {args.file}", file=sys.stderr)
        sys.exit(1)

    extra = args.extra.split(",") if args.extra else []
    result = redact_env(env, extra_keys=extra)

    if args.format == "json":
        print(json.dumps(result.env, indent=2))
    else:
        for key, value in sorted(result.env.items()):
            print(f"{key}={value}")

    if not args.quiet:
        if result.is_clean:
            print("# No keys redacted.", file=sys.stderr)
        else:
            print(
                f"# Redacted {len(result.redacted_keys)} key(s): "
                + ", ".join(result.redacted_keys),
                file=sys.stderr,
            )


def register_redact_commands(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser("redact", help="Redact sensitive values from a .env file")
    p.add_argument("file", help="Path to the .env file")
    p.add_argument(
        "--extra",
        default="",
        help="Comma-separated list of additional keys to redact",
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
        help="Suppress summary line on stderr",
    )
    p.set_defaults(func=cmd_redact)
