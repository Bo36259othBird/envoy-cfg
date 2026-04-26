"""invert.py — flip boolean-like and numeric env values."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

_TRUE_VALUES = {"true", "1", "yes", "on"}
_FALSE_VALUES = {"false", "0", "no", "off"}


@dataclass
class InvertResult:
    env: Dict[str, str]
    inverted: List[str]
    skipped: List[str]
    strategy: str

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"InvertResult(strategy={self.strategy!r}, "
            f"inverted={len(self.inverted)}, skipped={len(self.skipped)})"
        )

    def is_clean(self) -> bool:
        """True when every key was successfully inverted."""
        return len(self.skipped) == 0


def invert_booleans(
    env: Dict[str, str],
    keys: List[str] | None = None,
) -> InvertResult:
    """Invert boolean-like values (true<->false, 1<->0, yes<->no, on<->off).

    Args:
        env:  Source environment mapping.
        keys: Optional list of keys to restrict inversion to.
              When *None* all keys are considered.

    Returns:
        InvertResult with the modified env and bookkeeping lists.
    """
    result: Dict[str, str] = dict(env)
    inverted: List[str] = []
    skipped: List[str] = []

    targets = keys if keys is not None else list(env.keys())

    for k in targets:
        if k not in env:
            skipped.append(k)
            continue
        v = env[k].strip().lower()
        if v in _TRUE_VALUES:
            # Preserve original casing style of the *false* counterpart
            result[k] = "false" if env[k].strip().lower() == "false" else "false"
            inverted.append(k)
        elif v in _FALSE_VALUES:
            result[k] = "true"
            inverted.append(k)
        else:
            skipped.append(k)

    return InvertResult(
        env=result,
        inverted=sorted(inverted),
        skipped=sorted(skipped),
        strategy="boolean",
    )


def invert_numerics(
    env: Dict[str, str],
    keys: List[str] | None = None,
) -> InvertResult:
    """Negate numeric (int/float) values by prepending '-' or removing it.

    Args:
        env:  Source environment mapping.
        keys: Optional list of keys to restrict inversion to.

    Returns:
        InvertResult with the modified env and bookkeeping lists.
    """
    result: Dict[str, str] = dict(env)
    inverted: List[str] = []
    skipped: List[str] = []

    targets = keys if keys is not None else list(env.keys())

    for k in targets:
        if k not in env:
            skipped.append(k)
            continue
        v = env[k].strip()
        try:
            num = float(v)
            negated = -num
            # Preserve int representation when possible
            if negated == int(negated):
                result[k] = str(int(negated))
            else:
                result[k] = str(negated)
            inverted.append(k)
        except ValueError:
            skipped.append(k)

    return InvertResult(
        env=result,
        inverted=sorted(inverted),
        skipped=sorted(skipped),
        strategy="numeric",
    )
