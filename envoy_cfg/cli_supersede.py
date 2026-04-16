"""CLI commands for the supersede feature."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from envoy_cfg.supersede import supersede_env


def _load_dotenv(path: str) -> dict:
    env: dict = {}
    for line in Path(path).read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        env[k.strip()] = v.strip()
    return env


def cmd_supersede(args: argparse.Namespace) -> None:
    base = _load_dotenv(args.base)
    overrides = _load_dotenv(args.overrides)
    result = supersede_env(base, overrides, inject_new=not args.no_inject)

    if args.format == "json":
        print(json.dumps(result.env, indent=2))
    else:
        for k, v in result.env.items():
            print(f"{k}={v}")

    if not args.quiet:
        import sys
        print(f"# overridden={len(result.overridden)} injected={len(result.injected)}",
              file=sys.stderr)


def register_supersede_commands(sub: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = sub.add_parser("supersede", help="Override env keys from a higher-priority source")
    p.add_argument("base", help="Base .env file")
    p.add_argument("overrides", help="Override .env file")
    p.add_argument("--no-inject", action="store_true",
                   help="Do not inject keys absent from base")
    p.add_argument("--format", choices=["dotenv", "json"], default="dotenv")
    p.add_argument("--quiet", action="store_true", help="Suppress summary line")
    p.set_defaults(func=cmd_supersede)
