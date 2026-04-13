"""Rollback support: restore environment configs from snapshots."""

from dataclasses import dataclass, field
from typing import Optional

from envoy_cfg.snapshot import EnvSnapshot, SnapshotStore
from envoy_cfg.targets import TargetRegistry
from envoy_cfg.audit import AuditLog, AuditEntry


@dataclass
class RollbackResult:
    target_name: str
    snapshot_id: str
    applied: bool
    dry_run: bool
    keys_restored: list = field(default_factory=list)
    message: str = ""

    def __repr__(self) -> str:
        status = "DRY-RUN" if self.dry_run else ("OK" if self.applied else "FAILED")
        return (
            f"RollbackResult(target={self.target_name!r}, "
            f"snapshot={self.snapshot_id!r}, status={status}, "
            f"keys={len(self.keys_restored)})"
        )


class EnvRollback:
    def __init__(
        self,
        registry: TargetRegistry,
        store: SnapshotStore,
        audit_log: Optional[AuditLog] = None,
    ) -> None:
        self._registry = registry
        self._store = store
        self._audit_log = audit_log
        self._dry_run = False

    def set_dry_run(self, value: bool) -> None:
        self._dry_run = value

    def rollback(self, target_name: str, snapshot_id: str) -> RollbackResult:
        target = self._registry.get(target_name)
        if target is None:
            return RollbackResult(
                target_name=target_name,
                snapshot_id=snapshot_id,
                applied=False,
                dry_run=self._dry_run,
                message=f"Target '{target_name}' not found.",
            )

        snapshot = self._store.get(snapshot_id)
        if snapshot is None:
            return RollbackResult(
                target_name=target_name,
                snapshot_id=snapshot_id,
                applied=False,
                dry_run=self._dry_run,
                message=f"Snapshot '{snapshot_id}' not found.",
            )

        keys_restored = list(snapshot.env.keys())

        if not self._dry_run:
            target.env = dict(snapshot.env)
            if self._audit_log:
                for key in keys_restored:
                    entry = AuditEntry(
                        target_name=target_name,
                        action="rollback",
                        key=key,
                        new_value=snapshot.env.get(key),
                        actor="cli",
                        note=f"Restored from snapshot {snapshot_id}",
                    )
                    self._audit_log.record(entry)

        return RollbackResult(
            target_name=target_name,
            snapshot_id=snapshot_id,
            applied=not self._dry_run,
            dry_run=self._dry_run,
            keys_restored=keys_restored,
            message="Dry run — no changes applied." if self._dry_run else "Rollback applied.",
        )
