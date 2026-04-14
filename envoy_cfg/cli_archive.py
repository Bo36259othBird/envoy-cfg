"""CLI commands for archive creation and extraction."""

from __future__ import annotations

import io
import sys
from argparse import ArgumentParser, Namespace
from pathlib import Path

from envoy_cfg.archive import create_archive, load_archive
from envoy_cfg.snapshot import SnapshotStore


def cmd_archive_create(args: Namespace) -> None:
    store = SnapshotStore(args.snapshot_dir)
    snapshots = store.list_snapshots()

    if args.target:
        snapshots = [s for s in snapshots if s.target_name == args.target]
    if args.environment:
        snapshots = [s for s in snapshots if s.environment == args.environment]

    if not snapshots:
        print("No snapshots matched the given filters.", file=sys.stderr)
        sys.exit(1)

    dest_path = Path(args.output)
    buf = io.BytesIO()
    manifest = create_archive(snapshots, buf)
    dest_path.write_bytes(buf.getvalue())

    print(f"Archive created: {dest_path}")
    print(f"  Snapshots : {manifest.snapshot_count}")
    print(f"  Targets   : {', '.join(manifest.targets)}")
    print(f"  Created at: {manifest.created_at}")


def cmd_archive_extract(args: Namespace) -> None:
    src_path = Path(args.input)
    if not src_path.exists():
        print(f"Archive not found: {src_path}", file=sys.stderr)
        sys.exit(1)

    buf = io.BytesIO(src_path.read_bytes())
    manifest, snapshots = load_archive(buf)

    store = SnapshotStore(args.snapshot_dir)
    for snapshot in snapshots:
        store.save_snapshot(snapshot)

    print(f"Extracted {len(snapshots)} snapshot(s) from {src_path}")
    print(f"  Targets: {', '.join(manifest.targets)}")


def register_archive_commands(subparsers) -> None:
    archive_parser: ArgumentParser = subparsers.add_parser(
        "archive", help="Archive and restore env snapshots"
    )
    archive_sub = archive_parser.add_subparsers(dest="archive_cmd")

    create_p = archive_sub.add_parser("create", help="Create archive from snapshots")
    create_p.add_argument("--snapshot-dir", default=".envoy_snapshots", help="Snapshot directory")
    create_p.add_argument("--output", required=True, help="Output .zip file path")
    create_p.add_argument("--target", default=None, help="Filter by target name")
    create_p.add_argument("--environment", default=None, help="Filter by environment")
    create_p.set_defaults(func=cmd_archive_create)

    extract_p = archive_sub.add_parser("extract", help="Extract snapshots from archive")
    extract_p.add_argument("--snapshot-dir", default=".envoy_snapshots", help="Snapshot directory")
    extract_p.add_argument("--input", required=True, help="Input .zip file path")
    extract_p.set_defaults(func=cmd_archive_extract)
