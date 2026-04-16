"""CLI commands for cross-referencing multiple env files."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from envoy_cfg.crossref import crossref_envs


def _load_dotenv(path: str) -> dict:
    env = {}
    for line in Path(path).read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        env[k.strip()] = v.strip()
    return env


def cmd_crossref(args: argparse.Namespace) -> None:
    if len(args.files) < 2:
        print("ERROR: At least two files required for cross-reference.")
        return

    envs = {}
    for fpath in args.files:
        name = Path(fpath).stem
        envs[name] = _load_dotenv(fpath)

    result = crossref_envs(envs)

    if args.format == "json":
        out = {
            "common": sorted(result.common),
            "only_in": {k: sorted(v) for k, v in result.only_in.items()},
            "missing_in": {k: sorted(v) for k, v in result.missing_in.items()},
            "consistent": result.is_consistent(),
        }
        print(json.dumps(out, indent=2))
    else:
        print(f"Common keys ({len(result.common)}): {', '.join(sorted(result.common)) or 'none'}")
        for name, keys in result.only_in.items():
            if keys:
                print(f"  Only in '{name}': {', '.join(sorted(keys))}")
        for name, keys in result.missing_in.items():
            if keys:
                print(f"  Missing in '{name}': {', '.join(sorted(keys))}")
        status = "consistent" if result.is_consistent() else "inconsistent"
        print(f"Status: {status}")


def register_crossref_commands(subparsers) -> None:
    p = subparsers.add_parser("crossref", help="Cross-reference keys across env files")
    p.add_argument("files", nargs="+", help="Two or more .env files to compare")
    p.add_argument("--format", choices=["text", "json"], default="text")
    p.set_defaults(func=cmd_crossref)
