"""cli_mask_report.py — CLI commands for the mask-report feature."""

import argparse
import json
from envoy_cfg.mask_report import build_mask_report


def _load_dotenv(path: str) -> dict:
    env: dict = {}
    with open(path) as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, _, v = line.partition("=")
            env[k.strip()] = v.strip()
    return env


def cmd_mask_report(args: argparse.Namespace) -> None:
    env = _load_dotenv(args.file)
    report = build_mask_report(env)

    if args.format == "json":
        payload = {
            "total": report.total,
            "masked": report.masked_count,
            "plain": report.plain_count,
            "entries": [e.to_dict() for e in report.entries],
        }
        print(json.dumps(payload, indent=2))
        return

    # default: text
    print(f"Mask report — {args.file}")
    print(f"  Total keys : {report.total}")
    print(f"  Secret keys: {report.masked_count}")
    print(f"  Plain keys : {report.plain_count}")
    print()
    for entry in report.entries:
        tag = "[SECRET]" if entry.masked else "[plain] "
        display = entry.masked_value if entry.masked else entry.masked_value
        print(f"  {tag}  {entry.key} = {display}")

    if report.is_clean:
        print("\n  No secret keys detected.")


def register_mask_report_commands(
    subparsers: argparse._SubParsersAction,
) -> None:
    p = subparsers.add_parser(
        "mask-report",
        help="Show which keys in a .env file are treated as secrets",
    )
    p.add_argument("file", help="Path to .env file")
    p.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)",
    )
    p.set_defaults(func=cmd_mask_report)
