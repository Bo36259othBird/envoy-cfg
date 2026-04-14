"""Lint environment variable configs for style and convention issues."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class LintIssue:
    key: str
    message: str
    severity: str = "warning"  # "warning" | "error"

    def __repr__(self) -> str:
        return f"LintIssue({self.severity.upper()}, {self.key!r}: {self.message})"


@dataclass
class LintResult:
    issues: List[LintIssue] = field(default_factory=list)

    @property
    def errors(self) -> List[LintIssue]:
        return [i for i in self.issues if i.severity == "error"]

    @property
    def warnings(self) -> List[LintIssue]:
        return [i for i in self.issues if i.severity == "warning"]

    @property
    def is_clean(self) -> bool:
        return len(self.issues) == 0

    def __repr__(self) -> str:
        return (
            f"LintResult(errors={len(self.errors)}, warnings={len(self.warnings)})"
        )


def lint_env(env: Dict[str, str], *, strict: bool = False) -> LintResult:
    """Run lint checks on an env dict.

    Checks performed:
    - Keys should be UPPER_CASE
    - Values should not contain literal newlines
    - Keys should not start with a digit
    - Empty values generate a warning (error in strict mode)
    - Duplicate-looking keys differing only by case generate an error
    """
    result = LintResult()
    seen_upper: Dict[str, str] = {}

    for key, value in env.items():
        # Duplicate case-insensitive keys
        upper = key.upper()
        if upper in seen_upper and seen_upper[upper] != key:
            result.issues.append(
                LintIssue(key, f"conflicts with existing key {seen_upper[upper]!r} (case-insensitive match)", "error")
            )
        else:
            seen_upper[upper] = key

        # Keys should be UPPER_CASE
        if key != key.upper():
            result.issues.append(
                LintIssue(key, "key is not UPPER_CASE", "warning")
            )

        # Keys should not start with a digit
        if key and key[0].isdigit():
            result.issues.append(
                LintIssue(key, "key starts with a digit", "error")
            )

        # Values should not contain literal newlines
        if "\n" in value or "\r" in value:
            result.issues.append(
                LintIssue(key, "value contains literal newline characters", "error")
            )

        # Empty values
        if value == "":
            severity = "error" if strict else "warning"
            result.issues.append(
                LintIssue(key, "value is empty", severity)
            )

    return result
