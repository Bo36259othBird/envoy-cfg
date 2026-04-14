"""Redaction module: strip or replace sensitive values before output or logging."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envoy_cfg.masking import is_secret_key

REDACTED_PLACEHOLDER = "[REDACTED]"


@dataclass
class RedactResult:
    original_count: int
    redacted_keys: List[str]
    env: Dict[str, str]

    def __repr__(self) -> str:
        return (
            f"<RedactResult redacted={len(self.redacted_keys)}/{self.original_count} "
            f"keys={self.redacted_keys}>"
        )

    @property
    def is_clean(self) -> bool:
        """True when no keys were redacted."""
        return len(self.redacted_keys) == 0


def redact_env(
    env: Dict[str, str],
    extra_keys: Optional[List[str]] = None,
    placeholder: str = REDACTED_PLACEHOLDER,
) -> RedactResult:
    """Return a copy of *env* with sensitive values replaced by *placeholder*.

    Keys are considered sensitive when ``is_secret_key`` returns True or the
    key appears in the optional *extra_keys* allowlist.
    """
    deny = set(k.upper() for k in (extra_keys or []))
    redacted_keys: List[str] = []
    result: Dict[str, str] = {}

    for key, value in env.items():
        if is_secret_key(key) or key.upper() in deny:
            result[key] = placeholder
            redacted_keys.append(key)
        else:
            result[key] = value

    return RedactResult(
        original_count=len(env),
        redacted_keys=sorted(redacted_keys),
        env=result,
    )


def redact_value(
    key: str,
    value: str,
    extra_keys: Optional[List[str]] = None,
    placeholder: str = REDACTED_PLACEHOLDER,
) -> str:
    """Redact a single *value* if *key* is considered sensitive."""
    deny = set(k.upper() for k in (extra_keys or []))
    if is_secret_key(key) or key.upper() in deny:
        return placeholder
    return value
