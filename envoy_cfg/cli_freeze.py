"""CLI commands for env freeze / unfreeze operations."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import List

from envoy_cfg.freeze import freeze_env, unfreeze_env


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


def cmd_freeze(args: argparse.Namespace) -> None:
    env = _load_dotenv(args.file)
    keys: List[str] | None = args.keys if args.keys else None
    result = freeze_env(env, keys=keys)

    if args.format == "json":
        print(json.dumps({"frozen_keys": result.frozen_keys, "strategy": result.strategy}))
    else:
        if result.is_clean():
            print("No keys frozen.")
        else:
            print(f"Frozen {len(result.frozen_keys)} key(s) [{result.strategy}]:")
            for k in result.frozen_keys:
                print(f"  {k}")


def cmd_unfreeze(args: argparse.Namespace) -> None:
    env = _load_dotenv(args.file)
    frozen_keys: List[str] = args.frozen_keys if args.frozen_keys else list(env.keys())
    keys: List[str] | None = args.keys if args.keys else None
    result = unfreeze_env(env, frozen_keys=frozen_keys, keys=keys)

    if args.format == "json":
        print(json.dumps({"remaining_frozen": result.frozen_keys, "strategy": result.strategy}))
    else:
        if not result.frozen_keys:
            print("All keys unfrozen.")
        else:
            print(f"Remaining frozen keys ({len(result.frozen_keys)}):")
            for k in result.frozen_keys:
                print(f"  {k}")


def register_freeze_commands(subparsers: argparse._SubParsersAction) -> None:
    p_freeze = subparsers.add_parser("freeze", help="Freeze env keys")
    p_freeze.add_argument("file", help="Path to .env file")
    p_freeze.add_argument("--keys", nargs="+", metavar="KEY", help="Keys to freeze (default: all)")
    p_freeze.add_argument("--format", choices=["text", "json"], default="text")
    p_freeze.set_defaults(func=cmd_freeze)

    p_unfreeze = subparsers.add_parser("unfreeze", help="Unfreeze env keys")
    p_unfreeze.add_argument("file", help="Path to .env file")
    p_unfreeze.add_argument("--frozen-keys", nargs="+", metavar="KEY", dest="frozen_keys")
    p_unfreeze.add_argument("--keys", nargs="+", metavar="KEY", help="Keys to unfreeze (default: all)")
    p_unfreeze.add_argument("--format", choices=["text", "json"], default="text")
    p_unfreeze.set_defaults(func=cmd_unfreeze)
