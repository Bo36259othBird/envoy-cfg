"""CLI commands for unique-value analysis."""

from __future__ import annotations

import json
import sys
from argparse import ArgumentParser, Namespace
from pathlib import Path
from typing import Dict

from .unique import find_unique_values


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


def cmd_unique(args: Namespace) -> None:
    env = _load_dotenv(args.file)
    result = find_unique_values(
        env,
        case_sensitive=not args.ignore_case,
        ignore_empty=not args.include_empty,
    )

    if args.format == "json":
        print(
            json.dumps(
                {
                    "strategy": result.strategy,
                    "is_clean": result.is_clean(),
                    "shared_count": result.shared_count(),
                    "duplicate_values": result.duplicate_values,
                },
                indent=2,
            )
        )
        return

    if result.is_clean():
        print("All values are unique.")
        return

    print(f"Found {len(result.duplicate_values)} group(s) of shared values:\n")
    for value, keys in sorted(result.duplicate_values.items()):
        display = repr(value) if len(value) < 40 else repr(value[:37] + "...")
        print(f"  value {display} shared by: {', '.join(keys)}")

    sys.stderr.write(
        f"[unique] {result.shared_count()} key(s) share values with at least one other key.\n"
    )


def register_unique_commands(sub: ArgumentParser) -> None:
    p = sub.add_parser("unique", help="Detect keys that share identical values")
    p.add_argument("file", help="Path to .env file")
    p.add_argument("--ignore-case", action="store_true", help="Compare values case-insensitively")
    p.add_argument("--include-empty", action="store_true", help="Include empty values in analysis")
    p.add_argument("--format", choices=["text", "json"], default="text")
    p.set_defaults(func=cmd_unique)
