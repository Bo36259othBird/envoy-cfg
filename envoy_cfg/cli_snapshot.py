"""CLI commands for snapshot management in envoy-cfg."""

from __future__ import annotations

import sys
from typing import Optional

from envoy_cfg.masking import mask_env
from envoy_cfg.snapshot import SnapshotStore, capture_snapshot


DEFAULT_STORE_DIR = ".envoy_snapshots"


def cmd_snapshot_capture(
    target_name: str,
    environment: str,
    variables: dict,
    label: Optional[str] = None,
    description: Optional[str] = None,
    store_dir: str = DEFAULT_STORE_DIR,
    mask_secrets: bool = True,
) -> int:
    """Capture a snapshot of the given variables and persist it.

    Returns 0 on success, 1 on failure.
    """
    try:
        store = SnapshotStore(store_dir=store_dir)
        snap = capture_snapshot(target_name, environment, variables, description=description)
        path = store.save(snap, label=label)
        print(f"[snapshot] Captured snapshot for '{target_name}' ({environment}) -> {path}")
        return 0
    except Exception as exc:  # pragma: no cover
        print(f"[snapshot] ERROR: {exc}", file=sys.stderr)
        return 1


def cmd_snapshot_list(
    target_name: Optional[str] = None,
    store_dir: str = DEFAULT_STORE_DIR,
) -> int:
    """List available snapshots, optionally filtered by target name."""
    try:
        store = SnapshotStore(store_dir=store_dir)
        snapshots = store.list_snapshots(target_name=target_name)
        if not snapshots:
            print("[snapshot] No snapshots found.")
        else:
            print(f"[snapshot] Found {len(snapshots)} snapshot(s):")
            for name in snapshots:
                print(f"  - {name}")
        return 0
    except Exception as exc:  # pragma: no cover
        print(f"[snapshot] ERROR: {exc}", file=sys.stderr)
        return 1


def cmd_snapshot_show(
    target_name: str,
    label: str,
    store_dir: str = DEFAULT_STORE_DIR,
    mask_secrets: bool = True,
) -> int:
    """Display the contents of a stored snapshot."""
    try:
        store = SnapshotStore(store_dir=store_dir)
        snap = store.load(target_name, label)
        display_vars = mask_env(snap.variables) if mask_secrets else snap.variables
        print(f"[snapshot] Target   : {snap.target_name}")
        print(f"[snapshot] Env      : {snap.environment}")
        print(f"[snapshot] Captured : {snap.captured_at}")
        if snap.description:
            print(f"[snapshot] Note     : {snap.description}")
        print(f"[snapshot] Variables ({len(display_vars)}):")
        for k, v in sorted(display_vars.items()):
            print(f"  {k}={v}")
        return 0
    except FileNotFoundError as exc:
        print(f"[snapshot] ERROR: {exc}", file=sys.stderr)
        return 1


def cmd_snapshot_delete(
    target_name: str,
    label: str,
    store_dir: str = DEFAULT_STORE_DIR,
) -> int:
    """Delete a stored snapshot by target name and label."""
    store = SnapshotStore(store_dir=store_dir)
    removed = store.delete(target_name, label)
    if removed:
        print(f"[snapshot] Deleted snapshot '{label}' for target '{target_name}'.")
        return 0
    print(f"[snapshot] Snapshot '{label}' for '{target_name}' not found.", file=sys.stderr)
    return 1
