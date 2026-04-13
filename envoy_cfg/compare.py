"""Compare environment configs across two deployment targets."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envoy_cfg.diff import DiffResult, compute_diff
from envoy_cfg.masking import mask_env
from envoy_cfg.targets import TargetRegistry


@dataclass
class CompareResult:
    source: str
    destination: str
    diff: DiffResult
    masked: bool = False

    def __repr__(self) -> str:
        counts = (
            f"+{len(self.diff.added)} "
            f"-{len(self.diff.removed)} "
            f"~{len(self.diff.modified)}"
        )
        return f"<CompareResult {self.source!r} -> {self.destination!r} [{counts}]>"

    @property
    def has_differences(self) -> bool:
        return not self.diff.is_empty


class EnvComparer:
    def __init__(self, registry: TargetRegistry, mask_secrets: bool = True) -> None:
        self._registry = registry
        self._mask_secrets = mask_secrets

    def compare(self, source_name: str, dest_name: str) -> Optional[CompareResult]:
        source = self._registry.get(source_name)
        dest = self._registry.get(dest_name)

        if source is None or dest is None:
            return None

        src_env = source.env.copy()
        dst_env = dest.env.copy()

        if self._mask_secrets:
            src_env = mask_env(src_env)
            dst_env = mask_env(dst_env)

        diff = compute_diff(src_env, dst_env)
        return CompareResult(
            source=source_name,
            destination=dest_name,
            diff=diff,
            masked=self._mask_secrets,
        )

    def compare_all_to(
        self, dest_name: str, environment: Optional[str] = None
    ) -> List[CompareResult]:
        results: List[CompareResult] = []
        targets = self._registry.list_targets(environment=environment)
        for target in targets:
            if target.name == dest_name:
                continue
            result = self.compare(target.name, dest_name)
            if result is not None:
                results.append(result)
        return results
