"""cli_inject.py — CLI commands for injecting env vars into templates."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from envoy_cfg.inject import inject_env


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


def cmd_inject(args: argparse.Namespace) -> None:
    env = _load_dotenv(args.env_file)

    template_path = Path(args.template)
    if not template_path.exists():
        print(f"[error] Template file not found: {args.template}", file=sys.stderr)
        sys.exit(1)

    template = template_path.read_text()

    try:
        result = inject_env(
            template,
            env,
            strict=args.strict,
            default=args.default,
        )
    except KeyError as exc:
        print(f"[error] {exc}", file=sys.stderr)
        sys.exit(1)

    if args.output == "json":
        print(
            json.dumps(
                {
                    "output": result.output,
                    "resolved": result.resolved,
                    "missing": result.missing,
                    "is_clean": result.is_clean,
                },
                indent=2,
            )
        )
    else:
        print(result.output, end="")
        if result.missing:
            print(
                f"\n[warn] Unresolved placeholders: {', '.join(result.missing)}",
                file=sys.stderr,
            )


def register_inject_commands(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser("inject", help="Inject env vars into a template file")
    p.add_argument("template", help="Path to the template file")
    p.add_argument("--env-file", required=True, help="Path to .env file")
    p.add_argument(
        "--strict",
        action="store_true",
        default=False,
        help="Fail on unresolved placeholders",
    )
    p.add_argument(
        "--default",
        default=None,
        metavar="VALUE",
        help="Fallback value for missing keys (default: keep placeholder)",
    )
    p.add_argument(
        "--output",
        choices=["text", "json"],
        default="text",
        help="Output format",
    )
    p.set_defaults(func=cmd_inject)
