"""Template rendering for environment variable configs.

Supports variable interpolation within env values using ${VAR} syntax.
"""

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional

_INTERPOLATION_RE = re.compile(r"\$\{([^}]+)\}")


@dataclass
class TemplateRenderResult:
    rendered: Dict[str, str] = field(default_factory=dict)
    unresolved: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

    @property
    def success(self) -> bool:
        return len(self.errors) == 0 and len(self.unresolved) == 0

    def __repr__(self) -> str:
        return (
            f"TemplateRenderResult(keys={len(self.rendered)}, "
            f"unresolved={self.unresolved}, errors={self.errors})"
        )


def _resolve_value(value: str, env: Dict[str, str], seen: Optional[set] = None) -> tuple:
    """Resolve interpolations in a single value. Returns (resolved_value, unresolved_refs)."""
    if seen is None:
        seen = set()

    unresolved = []
    errors = []

    def replacer(match):
        ref = match.group(1)
        if ref in seen:
            errors.append(f"Circular reference detected: ${{{ref}}}")
            return match.group(0)
        if ref in env:
            seen_copy = seen | {ref}
            resolved, sub_unresolved, sub_errors = _resolve_value(env[ref], env, seen_copy)
            unresolved.extend(sub_unresolved)
            errors.extend(sub_errors)
            return resolved
        unresolved.append(ref)
        return match.group(0)

    resolved = _INTERPOLATION_RE.sub(replacer, value)
    return resolved, unresolved, errors


def render_template(env: Dict[str, str]) -> TemplateRenderResult:
    """Render all interpolations in an env dict, resolving ${VAR} references."""
    result = TemplateRenderResult()

    for key, value in env.items():
        resolved, unresolved, errors = _resolve_value(value, env)
        result.rendered[key] = resolved
        for ref in unresolved:
            if ref not in result.unresolved:
                result.unresolved.append(ref)
        for err in errors:
            if err not in result.errors:
                result.errors.append(err)

    return result
