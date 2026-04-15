"""CLI commands for grouping environment variables."""

import json
from pathlib import Path
from typing import List

from envoy_cfg.group import group_by_prefix, group_by_suffix, group_by_pattern


def _load_dotenv(path: str) -> dict:
    env = {}
    for line in Path(path).read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        env[key.strip()] = value.strip()
    return env


def cmd_group(args) -> None:
    env = _load_dotenv(args.file)

    if args.strategy == "prefix":
        if not args.groups:
            print("[error] --groups required for prefix strategy")
            return
        result = group_by_prefix(
            env,
            prefixes=args.groups,
            separator=args.separator,
            strip_prefix=args.strip,
        )
    elif args.strategy == "suffix":
        if not args.groups:
            print("[error] --groups required for suffix strategy")
            return
        result = group_by_suffix(
            env,
            suffixes=args.groups,
            separator=args.separator,
            strip_suffix=args.strip,
        )
    elif args.strategy == "pattern":
        if not args.patterns:
            print("[error] --patterns required for pattern strategy (label=regex ...)")
            return
        patterns = {}
        for item in args.patterns:
            label, _, regex = item.partition("=")
            patterns[label.strip()] = regex.strip()
        result = group_by_pattern(env, patterns=patterns)
    else:
        print(f"[error] Unknown strategy: {args.strategy}")
        return

    if args.format == "json":
        output = {
            "strategy": result.strategy,
            "groups": result.groups,
            "ungrouped": result.ungrouped,
            "complete": result.is_complete(),
        }
        print(json.dumps(output, indent=2))
    else:
        for label, members in result.groups.items():
            print(f"[{label}]")
            for k, v in members.items():
                print(f"  {k}={v}")
        if result.ungrouped:
            print("[ungrouped]")
            for k, v in result.ungrouped.items():
                print(f"  {k}={v}")
        print(f"\ncomplete={result.is_complete()}  groups={len(result.groups)}")


def register_group_commands(subparsers) -> None:
    p = subparsers.add_parser("group", help="Group env vars by prefix, suffix, or pattern")
    p.add_argument("file", help="Path to .env file")
    p.add_argument(
        "--strategy",
        choices=["prefix", "suffix", "pattern"],
        default="prefix",
        help="Grouping strategy (default: prefix)",
    )
    p.add_argument("--groups", nargs="+", metavar="LABEL", help="Prefix/suffix labels")
    p.add_argument("--patterns", nargs="+", metavar="LABEL=REGEX", help="Pattern pairs")
    p.add_argument("--separator", default="_", help="Separator between prefix/suffix and key")
    p.add_argument("--strip", action="store_true", help="Strip prefix/suffix from output keys")
    p.add_argument("--format", choices=["text", "json"], default="text")
    p.set_defaults(func=cmd_group)
