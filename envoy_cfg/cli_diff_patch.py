"""CLI commands for diff-patch: build and apply env patches."""
from __future__ import annotations

import argparse
import json
import sys

from envoy_cfg.diff_patch import DiffPatch, build_patch, apply_patch


def _load_dotenv(path: str) -> dict:
    env: dict = {}
    with open(path) as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                k, _, v = line.partition("=")
                env[k.strip()] = v.strip()
    return env


def cmd_diff_patch_build(args: argparse.Namespace) -> None:
    base = _load_dotenv(args.base)
    updated = _load_dotenv(args.updated)
    patch = build_patch(base, updated)
    if patch.is_empty:
        print("No differences found.", file=sys.stderr)
    out = json.dumps(patch.to_dict(), indent=2)
    if args.output:
        with open(args.output, "w") as fh:
            fh.write(out)
        print(f"Patch written to {args.output}", file=sys.stderr)
    else:
        print(out)


def cmd_diff_patch_apply(args: argparse.Namespace) -> None:
    env = _load_dotenv(args.env)
    with open(args.patch) as fh:
        patch = DiffPatch.from_dict(json.load(fh))
    try:
        result = apply_patch(env, patch, strict=args.strict)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
    if args.format == "json":
        print(json.dumps(result, indent=2))
    else:
        for k, v in result.items():
            print(f"{k}={v}")
    print(
        f"Applied {len(patch.entries)} patch operation(s).",
        file=sys.stderr,
    )


def register_diff_patch_commands(subparsers: argparse._SubParsersAction) -> None:
    build_p = subparsers.add_parser("diff-patch-build", help="Build a patch from two env files")
    build_p.add_argument("base", help="Base .env file")
    build_p.add_argument("updated", help="Updated .env file")
    build_p.add_argument("-o", "--output", default=None, help="Write patch JSON to file")
    build_p.set_defaults(func=cmd_diff_patch_build)

    apply_p = subparsers.add_parser("diff-patch-apply", help="Apply a patch to an env file")
    apply_p.add_argument("env", help="Base .env file to patch")
    apply_p.add_argument("patch", help="Patch JSON file")
    apply_p.add_argument("--strict", action="store_true", help="Fail on patch conflicts")
    apply_p.add_argument(
        "--format", choices=["dotenv", "json"], default="dotenv", help="Output format"
    )
    apply_p.set_defaults(func=cmd_diff_patch_apply)
