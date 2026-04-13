"""Sync environment variable configs to deployment targets."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envoy_cfg.masking import mask_env
from envoy_cfg.targets import DeploymentTarget, TargetRegistry


@dataclass
class SyncResult:
    """Result of a sync operation for a single target."""

    target_name: str
    success: bool
    keys_synced: List[str] = field(default_factory=list)
    error: Optional[str] = None

    def __repr__(self) -> str:
        status = "OK" if self.success else f"FAILED: {self.error}"
        return f"SyncResult(target={self.target_name!r}, status={status!r}, keys={len(self.keys_synced)})"


class EnvSyncer:
    """Syncs environment variable configs to registered deployment targets."""

    def __init__(self, registry: TargetRegistry):
        self._registry = registry
        self._dry_run = False

    def set_dry_run(self, enabled: bool) -> None:
        """Enable or disable dry-run mode (no actual writes)."""
        self._dry_run = enabled

    def sync_to_target(
        self,
        target_name: str,
        env_vars: Dict[str, str],
        mask_secrets: bool = True,
    ) -> SyncResult:
        """Sync env vars to a single named target."""
        target = self._registry.get(target_name)
        if target is None:
            return SyncResult(
                target_name=target_name,
                success=False,
                error=f"Target '{target_name}' not found in registry.",
            )

        display_vars = mask_env(env_vars) if mask_secrets else env_vars

        if not self._dry_run:
            _write_env_to_target(target, env_vars)

        return SyncResult(
            target_name=target_name,
            success=True,
            keys_synced=list(display_vars.keys()),
        )

    def sync_to_all(
        self,
        env_vars: Dict[str, str],
        environment: Optional[str] = None,
        mask_secrets: bool = True,
    ) -> List[SyncResult]:
        """Sync env vars to all targets, optionally filtered by environment."""
        targets = self._registry.list_targets(environment=environment)
        return [
            self.sync_to_target(t.name, env_vars, mask_secrets=mask_secrets)
            for t in targets
        ]


def _write_env_to_target(target: DeploymentTarget, env_vars: Dict[str, str]) -> None:
    """Placeholder for actual write logic (e.g., HTTP push, file write, etc.)."""
    # In a real implementation this would push vars to the target's URL or system.
    pass
