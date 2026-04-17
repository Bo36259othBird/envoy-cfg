import argparse
import json
from pathlib import Path
from typing import Dict

from envoy_cfg.copy import copy_keys


def _load_dotenv(path: str) -> Dict[str, str]:
    env: Dict[str, str] = {}
    for line in Path(path).read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        env[k.strip()] = v.strip()
    return env


def cmd_copy(args: argparse.Namespace) -> None:
    source = _load_dotenv(args.source)
    dest = _load_dotenv(args.dest)
    keys = args.keys

    result = copy_keys(
        source=source,
        dest=dest,
        keys=keys,
        overwrite=args.overwrite,
        prefix=args.prefix or None,
    )

    if args.format == "json":
        print(json.dumps(result.copied indent=2))
    else:
        for k, v in result.copied.items():
            print(f"{k}={v}")

    if not args.quiet:
        print(f"# copied={len(result.copied)} skipped={len(result.skipped)} strategy={result.strategy}", flush=True)


def register_copy_commands(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("copy", help="Copy specific keys from one env file to another")
    p.add_argument("source", help="Source .env file")
    p.add_argument("dest", help="Destination .env file")
    p.add_argument("keys", nargs="+", help="Keys to copy")
    p.add_argument("--overwrite", action="store_true", help="Overwrite existing keys in dest")
    p.add_argument("--prefix", default="", help="Prefix to apply to copied keys in dest")
    p.add_argument("--format", choices=["dotenv", "json"], default="dotenv")
    p.add_argument("--quiet", action="store_true")
    p.set_defaults(func=cmd_copy)
