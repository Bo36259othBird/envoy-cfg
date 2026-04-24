"""CLI commands for the env index feature."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from .index import build_index


def _load_dotenv(path: str) -> dict:
    env: dict = {}
    for line in Path(path).read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        env[k.strip()] = v.strip()
    return env


def cmd_index_lookup(args: Any) -> None:
    env = _load_dotenv(args.file)
    result = build_index(env, case_insensitive=args.ignore_case)
    value = result.lookup(args.key if not args.ignore_case else args.key.upper())
    if value is None:
        print(f"Key not found: {args.key}", file=sys.stderr)
        sys.exit(1)
    print(value)


def cmd_index_search(args: Any) -> None:
    env = _load_dotenv(args.file)
    result = build_index(env, case_insensitive=args.ignore_case)
    if args.by == "key":
        hits = result.search_keys(args.pattern)
        if args.format == "json":
            print(json.dumps(hits, indent=2))
        else:
            for k in hits:
                print(k)
    else:
        hits = result.search_values(args.pattern)
        if args.format == "json":
            print(json.dumps(hits, indent=2))
        else:
            for k, v in hits.items():
                print(f"{k}={v}")


def register_index_commands(subparsers: Any) -> None:
    p_index = subparsers.add_parser("index", help="Build and query an env index")
    index_sub = p_index.add_subparsers(dest="index_cmd")

    p_lookup = index_sub.add_parser("lookup", help="Lookup a single key")
    p_lookup.add_argument("file")
    p_lookup.add_argument("key")
    p_lookup.add_argument("--ignore-case", action="store_true")
    p_lookup.set_defaults(func=cmd_index_lookup)

    p_search = index_sub.add_parser("search", help="Search keys or values by glob")
    p_search.add_argument("file")
    p_search.add_argument("pattern")
    p_search.add_argument("--by", choices=["key", "value"], default="key")
    p_search.add_argument("--ignore-case", action="store_true")
    p_search.add_argument("--format", choices=["text", "json"], default="text")
    p_search.set_defaults(func=cmd_index_search)
