"""CLI commands for the split feature."""

from __future__ import annotations

import json
from argparse import ArgumentParser, Namespace
from pathlib import Path
from typing import Dict

from envoy_cfg.split import split_env


def _load_dotenv(path: str) -> Dict[str, str]:
    env: Dict[str, str] = {}
    for line in Path(path).read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            key, _, value = line.partition("=")
            env[key.strip()] = value.strip()
    return env


def cmd_split(args: Namespace) -> None:
    env = _load_dotenv(args.file)

    rules: Dict[str, str] = {}
    for rule_str in args.rule:
        if ":" not in rule_str:
            print(f"[error] Rule '{rule_str}' must be in NAME:PATTERN format.")
            return
        name, _, pattern = rule_str.partition(":")
        rules[name.strip()] = pattern.strip()

    if not rules:
        print("[error] Provide at least one --rule NAME:PATTERN.")
        return

    result = split_env(env, rules, allow_overlap=args.overlap)

    if args.format == "json":
        output = {
            "partitions": result.partitions,
            "unmatched": result.unmatched,
            "is_complete": result.is_complete,
        }
        print(json.dumps(output, indent=2))
    else:
        for name, partition in result.partitions.items():
            print(f"[{name}]")
            for k, v in sorted(partition.items()):
                print(f"  {k}={v}")
        if result.unmatched:
            print("[unmatched]")
            for k, v in sorted(result.unmatched.items()):
                print(f"  {k}={v}")
        status = "complete" if result.is_complete else f"{len(result.unmatched)} unmatched"
        print(f"\nStatus: {status}")


def register_split_commands(subparsers) -> None:
    p: ArgumentParser = subparsers.add_parser(
        "split", help="Split an env file into named partitions by key pattern"
    )
    p.add_argument("file", help="Path to .env file")
    p.add_argument(
        "--rule",
        action="append",
        default=[],
        metavar="NAME:PATTERN",
        help="Partition rule as NAME:REGEX (repeatable)",
    )
    p.add_argument(
        "--overlap",
        action="store_true",
        default=False,
        help="Allow a key to appear in multiple partitions",
    )
    p.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)",
    )
    p.set_defaults(func=cmd_split)
