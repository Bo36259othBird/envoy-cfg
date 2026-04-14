"""Export environment configs to various formats (dotenv, JSON, shell)."""

from __future__ import annotations

import json
from typing import Dict, Optional

from envoy_cfg.masking import mask_env

SUPPORTED_FORMATS = ("dotenv", "json", "shell")


def export_dotenv(env: Dict[str, str], mask_secrets: bool = False) -> str:
    """Export env vars in .env file format."""
    data = mask_env(env) if mask_secrets else env
    lines = []
    for key, value in sorted(data.items()):
        escaped = value.replace('"', '\\"')
        lines.append(f'{key}="{escaped}"')
    return "\n".join(lines) + ("\n" if lines else "")


def export_json(env: Dict[str, str], mask_secrets: bool = False) -> str:
    """Export env vars as a JSON object."""
    data = mask_env(env) if mask_secrets else env
    return json.dumps(dict(sorted(data.items())), indent=2) + "\n"


def export_shell(env: Dict[str, str], mask_secrets: bool = False) -> str:
    """Export env vars as shell export statements."""
    data = mask_env(env) if mask_secrets else env
    lines = []
    for key, value in sorted(data.items()):
        escaped = value.replace("'", "'\\''")
        lines.append(f"export {key}='{escaped}'")
    return "\n".join(lines) + ("\n" if lines else "")


def export_env(
    env: Dict[str, str],
    fmt: str,
    mask_secrets: bool = False,
    output_path: Optional[str] = None,
) -> str:
    """Export env vars in the specified format, optionally writing to a file.

    Args:
        env: Dictionary of environment variables.
        fmt: Output format — one of 'dotenv', 'json', 'shell'.
        mask_secrets: Whether to mask secret values before export.
        output_path: If provided, write the output to this file path.

    Returns:
        The rendered output string.

    Raises:
        ValueError: If an unsupported format is specified.
        OSError: If writing to ``output_path`` fails.
    """
    if fmt not in SUPPORTED_FORMATS:
        raise ValueError(
            f"Unsupported format '{fmt}'. Choose from: {', '.join(SUPPORTED_FORMATS)}"
        )

    exporters = {
        "dotenv": export_dotenv,
        "json": export_json,
        "shell": export_shell,
    }
    output = exporters[fmt](env, mask_secrets=mask_secrets)

    if output_path:
        try:
            with open(output_path, "w", encoding="utf-8") as fh:
                fh.write(output)
        except OSError as exc:
            raise OSError(
                f"Failed to write export output to '{output_path}': {exc}"
            ) from exc

    return output
