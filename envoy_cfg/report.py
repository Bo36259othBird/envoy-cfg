"""Report formatting for environment config diffs with secret masking."""

from typing import Dict, Optional
from envoy_cfg.diff import DiffResult, ChangeType, diff_envs
from envoy_cfg.masking import mask_env


ANSI_GREEN = "\033[92m"
ANSI_RED = "\033[91m"
ANSI_YELLOW = "\033[93m"
ANSI_RESET = "\033[0m"
ANSI_BOLD = "\033[1m"


def _colorize(text: str, color: str, use_color: bool = True) -> str:
    if not use_color:
        return text
    return f"{color}{text}{ANSI_RESET}"


def format_diff_report(
    current: Dict[str, str],
    incoming: Dict[str, str],
    target_name: Optional[str] = None,
    mask_secrets: bool = True,
    use_color: bool = True,
    include_unchanged: bool = False,
) -> str:
    """Format a human-readable diff report between two env configs."""
    if mask_secrets:
        current = mask_env(current)
        incoming = mask_env(incoming)

    result: DiffResult = diff_envs(current, incoming, include_unchanged=include_unchanged)

    lines = []
    header = f"Diff Report"
    if target_name:
        header += f" — {target_name}"
    lines.append(_colorize(f"{ANSI_BOLD}{header}", ANSI_BOLD, use_color))
    lines.append("-" * 40)

    if not result.has_changes:
        lines.append("No changes detected.")
        return "\n".join(lines)

    for change in result.changes:
        if change.change_type == ChangeType.ADDED:
            line = f"  + {change.key}={change.new_value}"
            lines.append(_colorize(line, ANSI_GREEN, use_color))
        elif change.change_type == ChangeType.REMOVED:
            line = f"  - {change.key}={change.old_value}"
            lines.append(_colorize(line, ANSI_RED, use_color))
        elif change.change_type == ChangeType.MODIFIED:
            line = f"  ~ {change.key}: {change.old_value!r} -> {change.new_value!r}"
            lines.append(_colorize(line, ANSI_YELLOW, use_color))
        elif change.change_type == ChangeType.UNCHANGED:
            lines.append(f"    {change.key}={change.new_value}")

    lines.append("-" * 40)
    lines.append(result.summary())
    return "\n".join(lines)
