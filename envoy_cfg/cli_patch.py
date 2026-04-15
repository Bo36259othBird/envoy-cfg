"""CLI commands for the patch feature."""

import argparse
import json
from pathlib import Path

from envoy_cfg.patch import PatchOperation, apply_patch


def _load_dotenv(path: str) -> dict:
    env: dict = {}
    for line in Path(path).read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        env[k.strip()] = v.strip()
    return env


def cmd_patch(args: argparse.Namespace) -> None:
    env = _load_dotenv(args.file)

    ops: list = []
    for raw in args.set or []:
        if "=" not in raw:
            print(f"[warn] --set value must be KEY=VALUE, got: {raw!r}")
            continue
        k, _, v = raw.partition("=")
        ops.append(PatchOperation(op="set", key=k, value=v))

    for key in args.delete or []:
        ops.append(PatchOperation(op="delete", key=key))

    for raw in args.rename or []:
        if ":" not in raw:
            print(f"[warn] --rename value must be OLD:NEW, got: {raw!r}")
            continue
        old, _, new = raw.partition(":")
        ops.append(PatchOperation(op="rename", key=old, new_key=new))

    result = apply_patch(env, ops)

    if args.format == "json":
        print(json.dumps(result.patched, indent=2, sort_keys=True))
    else:
        for k, v in sorted(result.patched.items()):
            print(f"{k}={v}")

    print(
        f"\n# applied={len(result.applied)} skipped={len(result.skipped)}",
        flush=True,
    )
    if result.skipped:
        for op in result.skipped:
            print(f"#  skipped: {op}")


def register_patch_commands(subparsers) -> None:
    p = subparsers.add_parser("patch", help="Apply key-value patch operations to an env file")
    p.add_argument("file", help="Path to .env file")
    p.add_argument("--set", metavar="KEY=VALUE", action="append", help="Set a key")
    p.add_argument("--delete", metavar="KEY", action="append", help="Delete a key")
    p.add_argument("--rename", metavar="OLD:NEW", action="append", help="Rename a key")
    p.add_argument(
        "--format", choices=["dotenv", "json"], default="dotenv", help="Output format"
    )
    p.set_defaults(func=cmd_patch)
