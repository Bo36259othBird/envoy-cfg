"""Clone environment configs from one deployment target to another."""

from dataclasses import dataclass, field
from typing import Optional

from envoy_cfg.targets import TargetRegistry
from envoy_cfg.merge import MergeStrategy, merge_envs


@dataclass
class CloneResult:
    source: str
    destination: str
    keys_copied: int
    dry_run: bool
    strategy: str
    success: bool
    error: Optional[str] = None

    def __repr__(self) -> str:
        status = "DRY RUN" if self.dry_run else ("OK" if self.success else "FAILED")
        return (
            f"<CloneResult [{status}] {self.source} -> {self.destination} "
            f"keys={self.keys_copied} strategy={self.strategy}>"
        )


class EnvCloner:
    def __init__(self, registry: TargetRegistry) -> None:
        self._registry = registry
        self._dry_run = False

    def set_dry_run(self, dry_run: bool) -> None:
        self._dry_run = dry_run

    def clone(
        self,
        source_name: str,
        dest_name: str,
        strategy: MergeStrategy = MergeStrategy.UNION,
        overwrite: bool = False,
    ) -> CloneResult:
        source = self._registry.get(source_name)
        if source is None:
            return CloneResult(
                source=source_name,
                destination=dest_name,
                keys_copied=0,
                dry_run=self._dry_run,
                strategy=strategy.value,
                success=False,
                error=f"Source target '{source_name}' not found.",
            )

        dest = self._registry.get(dest_name)
        if dest is None:
            return CloneResult(
                source=source_name,
                destination=dest_name,
                keys_copied=0,
                dry_run=self._dry_run,
                strategy=strategy.value,
                success=False,
                error=f"Destination target '{dest_name}' not found.",
            )

        base_env = dest.env if not overwrite else {}
        merged = merge_envs(base_env, source.env, strategy=strategy)
        keys_copied = len(merged)

        if not self._dry_run:
            dest.env.clear()
            dest.env.update(merged)

        return CloneResult(
            source=source_name,
            destination=dest_name,
            keys_copied=keys_copied,
            dry_run=self._dry_run,
            strategy=strategy.value,
            success=True,
        )
