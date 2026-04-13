"""CLI commands for validating environment variable configs."""

from __future__ import annotations

import json
import sys
from typing import Optional

from envoy_cfg.validate import validate_env


def _load_env_from_dotenv(path: str) -> dict:
    """Parse a simple .env file into a dict (no external dependencies)."""
    env = {}
    with open(path, "r") as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            key, _, value = line.partition("=")
            # Strip optional surrounding quotes from value
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            env[key] = value
    return env


def cmd_validate(args) -> int:
    """Validate env vars from a .env or JSON file.

    Returns exit code: 0 if valid, 1 if validation errors found, 2 on IO error.
    """
    path: str = args.file
    fmt: Optional[str] = getattr(args, "format", None)

    try:
        if fmt == "json" or path.endswith(".json"):
            with open(path, "r") as fh:
                env = json.load(fh)
        else:
            env = _load_env_from_dotenv(path)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"[error] Could not load file '{path}': {exc}", file=sys.stderr)
        return 2

    result = validate_env(env)

    if result.is_valid:
        print(f"[ok] All {len(env)} variable(s) in '{path}' are valid.")
        return 0

    print(f"[fail] Found {len(result.errors)} validation error(s) in '{path}':")
    for err in result.errors:
        print(f"  - {err.key}: {err.message}")
    return 1


def register_validate_commands(subparsers) -> None:
    """Register the 'validate' subcommand onto an argparse subparsers object."""
    parser = subparsers.add_parser(
        "validate",
        help="Validate environment variable keys and values from a file",
    )
    parser.add_argument(
        "file",
        help="Path to a .env or JSON file containing environment variables",
    )
    parser.add_argument(
        "--format",
        choices=["dotenv", "json"],
        default=None,
        help="Force file format (default: auto-detect from extension)",
    )
    parser.set_defaults(func=cmd_validate)
