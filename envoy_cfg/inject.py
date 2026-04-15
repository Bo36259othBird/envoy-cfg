"""inject.py — Inject environment variables into a template string or file."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional
import re

_PLACEHOLDER_RE = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}")


@dataclass
class InjectResult:
    output: str
    resolved: List[str] = field(default_factory=list)
    missing: List[str] = field(default_factory=list)

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"InjectResult(resolved={len(self.resolved)}, "
            f"missing={len(self.missing)})"
        )

    @property
    def is_clean(self) -> bool:
        """True when every placeholder was resolved."""
        return len(self.missing) == 0


def inject_env(
    template: str,
    env: Dict[str, str],
    *,
    strict: bool = False,
    default: Optional[str] = None,
) -> InjectResult:
    """Replace ``${KEY}`` placeholders in *template* with values from *env*.

    Args:
        template: The template string containing ``${KEY}`` placeholders.
        env: Mapping of environment variable names to values.
        strict: If ``True``, raise ``KeyError`` for any unresolved placeholder.
        default: Fallback string used when a key is absent and *strict* is
            ``False``.  Defaults to keeping the original placeholder text.

    Returns:
        :class:`InjectResult` with the rendered output and resolution metadata.
    """
    resolved: List[str] = []
    missing: List[str] = []

    def _replace(match: re.Match) -> str:  # type: ignore[type-arg]
        key = match.group(1)
        if key in env:
            resolved.append(key)
            return env[key]
        if strict:
            raise KeyError(f"Missing env key referenced in template: '{key}'")
        missing.append(key)
        return default if default is not None else match.group(0)

    output = _PLACEHOLDER_RE.sub(_replace, template)
    return InjectResult(output=output, resolved=resolved, missing=missing)
