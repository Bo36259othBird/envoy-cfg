"""CLI commands for the defaults feature."""

import argparse
import json
from pathlib import Path
from typing import Dict

from envoy_cfg.defaults import apply_defaults, strip_defaults


def _load_dotenv(path: str) -> Dict[str, str]:
    env: Dict[str, str] = {}
    for line in Path(path).read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        env[key.strip()] = value.strip()
    return env


def _parse_pairs(pairs) -> Dict[str, str]:
    """Parse KEY=VALUE strings into a dict."""
    result: Dict[str, str] = {}
    for pair in pairs or []:
        if "=" not in pair:
            raise argparse.ArgumentTypeError(f"Invalid KEY=VALUE pair: {pair!r}")
        k, _, v = pair.partition("=")
        result[k.strip()] = v.strip()
    return result


def cmd_defaults_apply(args: argparse.Namespace) -> None:
    env = _load_dotenv(args.file)
    defaults = _parse_pairs(args.default)
    result = apply_defaults(env, defaults, overwrite=args.overwrite)

    if args.format == "json":
        print(json.dumps(result.env, indent=2))
    else:
        for k, v in result.env.items():
            print(f"{k}={v}")

    if not args.quiet:
        print(f"# applied={len(result.applied)} skipped={len(result.skipped)}",
              flush=True)


def cmd_defaults_strip(args: argparse.Namespace) -> None:
    env = _load_dotenv(args.file)
    defaults = _parse_pairs(args.default)
    stripped = strip_defaults(env, defaults)

    if args.format == "json":
        print(json.dumps(stripped, indent=2))
    else:
        for k, v in stripped.items():
            print(f"{k}={v}")


def register_defaults_commands(subparsers) -> None:
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("file", help="Path to .env file")
    common.add_argument(
        "--default", metavar="KEY=VALUE", action="append",
        help="Default pair (repeatable)"
    )
    common.add_argument(
        "--format", choices=["dotenv", "json"], default="dotenv"
    )
    common.add_argument("--quiet", action="store_true")

    p_apply = subparsers.add_parser(
        "defaults-apply", parents=[common], help="Apply defaults to an env file"
    )
    p_apply.add_argument(
        "--overwrite", action="store_true",
        help="Apply defaults even when key already exists"
    )
    p_apply.set_defaults(func=cmd_defaults_apply)

    p_strip = subparsers.add_parser(
        "defaults-strip", parents=[common],
        help="Strip keys whose value matches the default"
    )
    p_strip.set_defaults(func=cmd_defaults_strip)
