"""CLI commands for the annotate feature."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict

from envoy_cfg.annotate import apply_annotations, strip_annotations, get_annotation


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


def _parse_pairs(pairs: list) -> Dict[str, str]:
    result: Dict[str, str] = {}
    for item in pairs:
        if "=" in item:
            k, _, v = item.partition("=")
            result[k.strip()] = v.strip()
    return result


def cmd_annotate_apply(args: argparse.Namespace) -> None:
    env = _load_dotenv(args.file)
    annotations = _parse_pairs(args.annotation or [])
    result = apply_annotations(env, annotations, overwrite=args.overwrite)

    if args.format == "json":
        print(json.dumps({"env": result.env, "annotations": result.annotations}, indent=2))
    else:
        for key, val in result.env.items():
            note = result.annotations.get(key, "")
            suffix = f"  # {note}" if note else ""
            print(f"{key}={val}{suffix}")
    print(f"# annotated: {len(result.annotated_keys)} key(s)", flush=True)


def cmd_annotate_strip(args: argparse.Namespace) -> None:
    env = _load_dotenv(args.file)
    keys = args.keys or None
    # build a dummy full annotation map from env
    annotations = {k: f"annotation for {k}" for k in env}
    stripped = strip_annotations(annotations, keys=keys)
    remaining = len(stripped)
    removed = len(annotations) - remaining
    if args.format == "json":
        print(json.dumps(stripped, indent=2))
    else:
        for k, v in stripped.items():
            print(f"{k}: {v}")
    print(f"# removed: {removed} annotation(s)")


def cmd_annotate_get(args: argparse.Namespace) -> None:
    env = _load_dotenv(args.file)
    annotations = _parse_pairs(args.annotation or [])
    result = apply_annotations(env, annotations)
    note = get_annotation(result.annotations, args.key)
    if note:
        print(f"{args.key}: {note}")
    else:
        print(f"{args.key}: (no annotation)")


def register_annotate_commands(subparsers) -> None:
    p = subparsers.add_parser("annotate", help="Annotate env keys with metadata")
    sub = p.add_subparsers(dest="annotate_cmd")

    ap = sub.add_parser("apply", help="Apply annotations to env keys")
    ap.add_argument("file", help="Path to .env file")
    ap.add_argument("--annotation", nargs="*", metavar="KEY=NOTE", default=[])
    ap.add_argument("--overwrite", action="store_true")
    ap.add_argument("--format", choices=["dotenv", "json"], default="dotenv")
    ap.set_defaults(func=cmd_annotate_apply)

    sp = sub.add_parser("strip", help="Strip annotations from keys")
    sp.add_argument("file", help="Path to .env file")
    sp.add_argument("--keys", nargs="*", metavar="KEY")
    sp.add_argument("--format", choices=["text", "json"], default="text")
    sp.set_defaults(func=cmd_annotate_strip)

    gp = sub.add_parser("get", help="Get annotation for a single key")
    gp.add_argument("file", help="Path to .env file")
    gp.add_argument("key", help="Key to look up")
    gp.add_argument("--annotation", nargs="*", metavar="KEY=NOTE", default=[])
    gp.set_defaults(func=cmd_annotate_get)
