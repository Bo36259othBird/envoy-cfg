from __future__ import annotations

import argparse
import json
import sys
from typing import Dict

from envoy_cfg.classify import classify_env


def _load_dotenv(path: str) -> Dict[str, str]:
    env: Dict[str, str] = {}
    with open(path) as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                k, _, v = line.partition("=")
                env[k.strip()] = v.strip()
    return env


def cmd_classify(args: argparse.Namespace) -> None:
    env = _load_dotenv(args.file)
    result = classify_env(env)

    if args.format == "json":
        payload = {
            "strategy": result.strategy,
            "is_clean": result.is_clean,
            "by_type": result.by_type,
            "entries": [e.to_dict() for e in result.entries],
        }
        print(json.dumps(payload, indent=2))
        return

    # text output
    if not result.entries:
        print("No keys found.", file=sys.stderr)
        return

    by_type = result.by_type
    for vtype, keys in sorted(by_type.items()):
        print(f"[{vtype}]")
        for k in sorted(keys):
            secret_flag = "  *secret*" if k in result.secret_keys else ""
            print(f"  {k}{secret_flag}")

    print(
        f"\nTotal: {len(result.entries)} key(s), "
        f"{len(result.secret_keys)} secret(s).",
        file=sys.stderr,
    )


def register_classify_commands(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser("classify", help="Classify env keys by value type")
    p.add_argument("file", help="Path to .env file")
    p.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)",
    )
    p.set_defaults(func=cmd_classify)
