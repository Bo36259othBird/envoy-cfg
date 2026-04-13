"""CLI commands for environment variable interpolation."""

import argparse
import json
from typing import Dict

from envoy_cfg.interpolate import interpolate_env


def _load_dotenv(path: str) -> Dict[str, str]:
    env: Dict[str, str] = {}
    with open(path) as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, _, value = line.partition("=")
                env[key.strip()] = value.strip().strip('"').strip("'")
    return env


def cmd_interpolate(args: argparse.Namespace) -> None:
    """Resolve ${VAR} references in a .env file and print the result."""
    env = _load_dotenv(args.env_file)

    overlay: Dict[str, str] = {}
    if args.overlay:
        for path in args.overlay:
            overlay.update(_load_dotenv(path))

    result = interpolate_env(env, overlay=overlay or None)

    if args.format == "json":
        print(json.dumps(result.resolved, indent=2, sort_keys=True))
    else:
        for key, value in sorted(result.resolved.items()):
            print(f"{key}={value}")

    if result.errors:
        print("\n[interpolation warnings]")
        for err in result.errors:
            print(f"  ! {err}")

    if not result.is_clean and args.strict:
        raise SystemExit(1)


def register_interpolate_commands(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser(
        "interpolate",
        help="Resolve ${VAR} references in an env file",
    )
    p.add_argument("env_file", help="Path to the .env file to interpolate")
    p.add_argument(
        "--overlay",
        nargs="+",
        metavar="FILE",
        help="Additional .env files whose keys can be used as reference sources",
    )
    p.add_argument(
        "--format",
        choices=["dotenv", "json"],
        default="dotenv",
        help="Output format (default: dotenv)",
    )
    p.add_argument(
        "--strict",
        action="store_true",
        help="Exit with code 1 if any references remain unresolved",
    )
    p.set_defaults(func=cmd_interpolate)
