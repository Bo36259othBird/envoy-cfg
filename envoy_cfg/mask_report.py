"""mask_report.py — Generate a summary report of masked/secret keys in an env dict."""

from dataclasses import dataclass, field
from typing import Dict, List
from envoy_cfg.masking import is_secret_key, mask_value


@dataclass
class MaskReportEntry:
    key: str
    masked: bool
    original_length: int
    masked_value: str

    def to_dict(self) -> dict:
        return {
            "key": self.key,
            "masked": self.masked,
            "original_length": self.original_length,
            "masked_value": self.masked_value,
        }

    def __repr__(self) -> str:
        status = "SECRET" if self.masked else "plain"
        return f"<MaskReportEntry key={self.key!r} status={status}>"


@dataclass
class MaskReport:
    entries: List[MaskReportEntry] = field(default_factory=list)

    @property
    def total(self) -> int:
        return len(self.entries)

    @property
    def masked_count(self) -> int:
        return sum(1 for e in self.entries if e.masked)

    @property
    def plain_count(self) -> int:
        return self.total - self.masked_count

    @property
    def is_clean(self) -> bool:
        return self.masked_count == 0

    def masked_keys(self) -> List[str]:
        return sorted(e.key for e in self.entries if e.masked)

    def __repr__(self) -> str:
        return (
            f"<MaskReport total={self.total} masked={self.masked_count} "
            f"plain={self.plain_count}>"
        )


def build_mask_report(env: Dict[str, str]) -> MaskReport:
    """Analyse env and return a MaskReport describing which keys are secret."""
    entries: List[MaskReportEntry] = []
    for key in sorted(env):
        value = env[key]
        secret = is_secret_key(key)
        entries.append(
            MaskReportEntry(
                key=key,
                masked=secret,
                original_length=len(value),
                masked_value=mask_value(value) if secret else value,
            )
        )
    return MaskReport(entries=entries)
