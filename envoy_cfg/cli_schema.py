"""CLI commands for schema validation of environment configs."""

from __future__ import annotations

import json
import sys
from argparse import ArgumentParser, Namespace
from pathlib import Path
from typing import Dict

from envoy_cfg.schema import EnvSchema, SchemaField


def _load_env_from_dotenv(path: str) -> Dict[str, str]:
    env: Dict[str, str] = {}
    for line in Path(path).read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            k, _, v = line.partition("=")
            env[k.strip()] = v.strip().strip('"').strip("'")
    return env


def cmd_schema_validate(args: Namespace) -> None:
    schema_path = Path(args.schema)
    if not schema_path.exists():
        print(f"[error] Schema file not found: {args.schema}", file=sys.stderr)
        sys.exit(1)

    schema_data = json.loads(schema_path.read_text())
    schema = EnvSchema.from_dict(schema_data)

    env = _load_env_from_dotenv(args.env_file)
    errors = schema.validate(env)

    if errors:
        print(f"[schema] Validation failed for '{schema.name}':")
        for err in errors:
            print(f"  - {err}")
        sys.exit(1)
    else:
        print(f"[schema] '{schema.name}' — all checks passed ({len(env)} keys).")


def cmd_schema_show(args: Namespace) -> None:
    schema_path = Path(args.schema)
    if not schema_path.exists():
        print(f"[error] Schema file not found: {args.schema}", file=sys.stderr)
        sys.exit(1)

    schema_data = json.loads(schema_path.read_text())
    schema = EnvSchema.from_dict(schema_data)

    print(f"Schema: {schema.name}")
    print(f"  {'KEY':<30} {'REQUIRED':<10} {'DEFAULT':<20} DESCRIPTION")
    print("  " + "-" * 70)
    for f in schema.fields:
        req = "yes" if f.required else "no"
        default = f.default if f.default is not None else ""
        print(f"  {f.key:<30} {req:<10} {default:<20} {f.description}")


def register_schema_commands(subparsers: Any) -> None:  # noqa: F821
    schema_parser = subparsers.add_parser("schema", help="Schema validation commands")
    schema_sub = schema_parser.add_subparsers(dest="schema_cmd")

    p_validate = schema_sub.add_parser("validate", help="Validate an env file against a schema")
    p_validate.add_argument("--schema", required=True, help="Path to schema JSON file")
    p_validate.add_argument("--env-file", required=True, help="Path to .env file to validate")
    p_validate.set_defaults(func=cmd_schema_validate)

    p_show = schema_sub.add_parser("show", help="Display schema fields")
    p_show.add_argument("--schema", required=True, help="Path to schema JSON file")
    p_show.set_defaults(func=cmd_schema_show)
