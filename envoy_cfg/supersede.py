"""supersede.py — override env keys from a higher-priority source."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class SupersedeResult:
    env: Dict[str, str]
    overridden: List[str] = field(default_factory=list)
    injected: List[str] = field(default_factory=list)
    strategy: str = "supersede"

    def __repr__(self) -> str:
        return (
            f"SupersedeResult(overridden={len(self.overridden)}, "
            f"injected={len(self.injected)}, total={len(self.env)})"
        )

    def is_clean(self) -> bool:
        """True when no keys were overridden or injected."""
        return not self.overridden and not self.injected


def supersede_env(
    base: Dict[str, str],
    overrides: Dict[str, str],
    *,
    inject_new: bool = True,
) -> SupersedeResult:
    """Apply *overrides* on top of *base*.

    Args:
        base: The original environment dict.
        overrides: Higher-priority key/value pairs.
        inject_new: When True (default), keys present only in *overrides*
            are added to the result.  When False they are silently dropped.

    Returns:
        A :class:`SupersedeResult` describing what changed.
    """
    result = dict(base)
    overridden: List[str] = []
    injected: List[str] = []

    for key, value in overrides.items():
        if key in base:
            if base[key] != value:
                result[key] = value
                overridden.append(key)
        else:
            if inject_new:
                result[key] = value
                injected.append(key)

    return SupersedeResult(
        env=result,
        overridden=sorted(overridden),
        injected=sorted(injected),
    )
