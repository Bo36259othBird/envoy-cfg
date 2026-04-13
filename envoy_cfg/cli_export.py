"""CLI commands for exporting environment configs."""

from __future__ import annotations

import argparse
import sys

from envoy_cfg.export import SUPPORTED_FORMATS, export_env
from envoy_cfg.snapshot import SnapshotStore


def cmd_export(args: argparse.Namespace) -> int:
    """Export a snapshot's env vars to the requested format."""
    store = SnapshotStore(args.store_dir)
    snapshots = store.list_snapshots(target=args.target, environment=args.environment)

    if not snapshots:
        print(
            f"No snapshots found for target='{args.target}' env='{args.environment}'.",
            file=sys.stderr,
        )
        return 1

    # Use the most recent snapshot.
    latest = sorted(snapshots, key=lambda s: s.timestamp, reverse=True)[0]

    try:
        output = export_env(
            latest.env,
            fmt=args.format,
            mask_secrets=args.mask,
            output_path=args.output,
        )
    except ValueError as exc:
        print(f"Export error: {exc}", file=sys.stderr)
        return 1

    if not args.output:
        print(output, end="")
    else:
        print(f"Exported to '{args.output}'.")

    return 0


def register_export_commands(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    """Attach export sub-commands to the CLI parser."""
    parser = subparsers.add_parser(
        "export",
        help="Export env config from the latest snapshot for a target.",
    )
    parser.add_argument("target", help="Deployment target name.")
    parser.add_argument("environment", help="Environment (e.g. production, staging).")
    parser.add_argument(
        "--format",
        choices=SUPPORTED_FORMATS,
        default="dotenv",
        help="Output format (default: dotenv).",
    )
    parser.add_argument(
        "--mask",
        action="store_true",
        default=False,
        help="Mask secret values in the output.",
    )
    parser.add_argument(
        "--output",
        metavar="FILE",
        default=None,
        help="Write output to FILE instead of stdout.",
    )
    parser.add_argument(
        "--store-dir",
        default=".envoy_snapshots",
        help="Directory where snapshots are stored.",
    )
    parser.set_defaults(func=cmd_export)
