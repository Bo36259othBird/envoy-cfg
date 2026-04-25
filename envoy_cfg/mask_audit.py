"""mask_audit.py — Combine secret masking with audit logging for env operations."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envoy_cfg.masking import mask_env, is_secret_key
from envoy_cfg.audit import AuditLog, AuditEntry


@dataclass
class MaskAuditResult:
    masked_env: Dict[str, str]
    audit_entries: List[AuditEntry]
    masked_keys: List[str] = field(default_factory=list)
    total: int = 0

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"MaskAuditResult(total={self.total}, "
            f"masked={len(self.masked_keys)}, "
            f"audit_entries={len(self.audit_entries)})"
        )

    @property
    def is_clean(self) -> bool:
        """True when no keys required masking."""
        return len(self.masked_keys) == 0


def mask_and_audit(
    env: Dict[str, str],
    target: str,
    operation: str = "mask",
    log: Optional[AuditLog] = None,
    actor: str = "system",
) -> MaskAuditResult:
    """Mask secret keys in *env* and record an audit entry for each masked key.

    Args:
        env: The environment dict to process.
        target: Deployment target name used in audit entries.
        operation: Label recorded in each audit entry.
        log: Optional :class:`AuditLog` to persist entries.
        actor: Who triggered the operation (stored in audit metadata).

    Returns:
        :class:`MaskAuditResult` with the masked env and generated audit entries.
    """
    masked = mask_env(env)
    masked_keys = sorted(k for k in env if is_secret_key(k))

    entries: List[AuditEntry] = []
    for key in masked_keys:
        entry = AuditEntry(
            target=target,
            operation=operation,
            key=key,
            old_value="[REDACTED]",
            new_value=masked.get(key, ""),
            actor=actor,
        )
        entries.append(entry)
        if log is not None:
            log.append(entry)

    return MaskAuditResult(
        masked_env=masked,
        audit_entries=entries,
        masked_keys=masked_keys,
        total=len(env),
    )
