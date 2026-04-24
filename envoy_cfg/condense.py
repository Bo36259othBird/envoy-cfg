"""condense.py — Remove redundant or duplicate-value keys from an env dict.

A 'condensed' env keeps only one representative key per unique value
(configurable: first-seen or last-seen) and reports which keys were
dropped as redundant.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Literal


@dataclass
class CondenseResult:
    """Result of a condense operation."""

    env: Dict[str, str]
    """The condensed environment (unique-value keys only)."""

    dropped: List[str]
    """Keys that were removed because their value already appeared."""

    strategy: str
    """Which representative was kept: 'first' or 'last'."""

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"CondenseResult(kept={len(self.env)}, "
            f"dropped={len(self.dropped)}, strategy={self.strategy!r})"
        )

    def is_clean(self) -> bool:
        """Return True when no keys were dropped (all values were already unique)."""
        return len(self.dropped) == 0


def condense_env(
    env: Dict[str, str],
    strategy: Literal["first", "last"] = "first",
    case_sensitive_values: bool = True,
) -> CondenseResult:
    """Remove keys whose value is a duplicate of an already-seen value.

    Parameters
    ----------
    env:
        Source environment mapping.
    strategy:
        ``'first'`` keeps the first key encountered for each unique value
        (default); ``'last'`` keeps the last key encountered.
    case_sensitive_values:
        When *False*, value comparison is performed in lower-case so that
        ``"True"`` and ``"true"`` are considered duplicates.

    Returns
    -------
    CondenseResult
        Contains the condensed env, the list of dropped keys, and the
        strategy label.
    """
    if strategy not in ("first", "last"):
        raise ValueError(f"strategy must be 'first' or 'last', got {strategy!r}")

    items = list(env.items())

    # For 'last', reverse the list so we can still use a first-seen scan
    # and reverse the result back at the end.
    if strategy == "last":
        items = list(reversed(items))

    seen_values: Dict[str, str] = {}  # normalised_value -> first winning key
    kept: Dict[str, str] = {}
    dropped: List[str] = []

    for key, value in items:
        normalised = value if case_sensitive_values else value.lower()
        if normalised in seen_values:
            dropped.append(key)
        else:
            seen_values[normalised] = key
            kept[key] = value

    if strategy == "last":
        # Restore original insertion order for the kept keys
        original_order = [k for k, _ in env.items() if k in kept]
        kept = {k: kept[k] for k in original_order}
        dropped = list(reversed(dropped))

    return CondenseResult(env=kept, dropped=sorted(dropped), strategy=strategy)
