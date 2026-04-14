"""CLI commands for linting environment variable configs."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import List

from envoy_cfg.lint import lint_env


def _load_dotenv(path: str) -> dict:
    env: dict = {}
    for line in Path(path).read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            k, _, v = line.partition("=")
            env[k.strip()] = v.strip().strip('"').strip("'")
    return env


def cmd_lint(args: argparse.Namespace) -> None:
    try:
        env = _load_dotenv(args.file)
    except FileNotFoundError:
        print(f"[error] File not found: {args.file}", file=sys.stderr)
        sys.exit(1)

    result = lint_env(env, strict=getattr(args, "strict", False))

    if result.is_clean:
        print(f"[lint] {args.file}: no issues found.")
        return

    for issue in result.issues:
        tag = "ERROR  " if issue.severity == "error" else "WARNING"
        print(f"[{tag}] {issue.key}: {issue.message}")

    print(
        f"\n[lint] {len(result.errors)} error(s), {len(result.warnings)} warning(s)."
    )

    if result.errors:
        sys.exit(2)


def register_lint_commands(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser("lint", help="Lint an env file for style issues")
    p.add_argument("file", help="Path to .env file")
    p.add_argument(
        "--strict",
        action="store_true",
        help="Treat empty values as errors instead of warnings",
    )
    p.set_defaults(func=cmd_lint)
