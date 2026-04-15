"""Patch: apply partial key-value updates to an environment dict."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class PatchOperation:
    op: str          # 'set', 'delete', 'rename'
    key: str
    value: Optional[str] = None
    new_key: Optional[str] = None

    def __repr__(self) -> str:
        if self.op == "set":
            return f"PatchOperation(set {self.key!r}={self.value!r})"
        if self.op == "delete":
            return f"PatchOperation(delete {self.key!r})"
        if self.op == "rename":
            return f"PatchOperation(rename {self.key!r} -> {self.new_key!r})"
        return f"PatchOperation(op={self.op!r}, key={self.key!r})"


@dataclass
class PatchResult:
    original: Dict[str, str]
    patched: Dict[str, str]
    applied: List[PatchOperation] = field(default_factory=list)
    skipped: List[PatchOperation] = field(default_factory=list)

    def __repr__(self) -> str:
        return (
            f"PatchResult(applied={len(self.applied)}, "
            f"skipped={len(self.skipped)})"
        )

    @property
    def is_clean(self) -> bool:
        """True when no operations were skipped."""
        return len(self.skipped) == 0


VALID_OPS = {"set", "delete", "rename"}


def apply_patch(
    env: Dict[str, str],
    operations: List[PatchOperation],
) -> PatchResult:
    """Apply a list of patch operations to *env* and return a PatchResult."""
    result = dict(env)
    applied: List[PatchOperation] = []
    skipped: List[PatchOperation] = []

    for op in operations:
        if op.op not in VALID_OPS:
            skipped.append(op)
            continue

        if op.op == "set":
            if op.value is None:
                skipped.append(op)
                continue
            result[op.key] = op.value
            applied.append(op)

        elif op.op == "delete":
            if op.key not in result:
                skipped.append(op)
                continue
            del result[op.key]
            applied.append(op)

        elif op.op == "rename":
            if op.new_key is None or op.key not in result:
                skipped.append(op)
                continue
            result[op.new_key] = result.pop(op.key)
            applied.append(op)

    return PatchResult(
        original=dict(env),
        patched=result,
        applied=applied,
        skipped=skipped,
    )
