"""Promotion of environment configs between deployment targets."""

from dataclasses import dataclass, field
from typing import Optional

from envoy_cfg.targets import TargetRegistry
from envoy_cfg.merge import merge_envs, MergeStrategy
from envoy_cfg.diff import diff_envs, DiffResult
from envoy_cfg.audit import AuditLog, AuditEntry


@dataclass
class PromoteResult:
    source: str
    destination: str
    strategy: MergeStrategy
    diff: Optional[DiffResult] = None
    success: bool = False
    message: str = ""
    dry_run: bool = False

    def __repr__(self) -> str:
        status = "DRY-RUN" if self.dry_run else ("OK" if self.success else "FAILED")
        return f"<PromoteResult {self.source}->{self.destination} [{status}] {self.message}>"


class EnvPromoter:
    """Handles promotion of env configs from one target to another."""

    def __init__(
        self,
        registry: TargetRegistry,
        audit_log: Optional[AuditLog] = None,
        dry_run: bool = False,
    ) -> None:
        self._registry = registry
        self._audit_log = audit_log
        self._dry_run = dry_run

    def set_dry_run(self, value: bool) -> None:
        self._dry_run = value

    def promote(
        self,
        source_name: str,
        dest_name: str,
        strategy: MergeStrategy = MergeStrategy.UNION,
    ) -> PromoteResult:
        source = self._registry.get(source_name)
        if source is None:
            return PromoteResult(
                source=source_name,
                destination=dest_name,
                strategy=strategy,
                message=f"Source target '{source_name}' not found.",
            )

        dest = self._registry.get(dest_name)
        if dest is None:
            return PromoteResult(
                source=source_name,
                destination=dest_name,
                strategy=strategy,
                message=f"Destination target '{dest_name}' not found.",
            )

        merged = merge_envs(dest.env_vars, source.env_vars, strategy)
        diff = diff_envs(dest.env_vars, merged)

        if not self._dry_run:
            dest.env_vars.update(merged)
            if self._audit_log:
                for change in diff.changes:
                    self._audit_log.record(
                        AuditEntry(
                            target=dest_name,
                            key=change.key,
                            action=change.change_type.value,
                            old_value=change.old_value,
                            new_value=change.new_value,
                        )
                    )

        return PromoteResult(
            source=source_name,
            destination=dest_name,
            strategy=strategy,
            diff=diff,
            success=True,
            message=f"{len(diff.changes)} change(s) applied.",
            dry_run=self._dry_run,
        )
