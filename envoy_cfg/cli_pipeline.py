"""CLI commands for the pipeline feature."""

import argparse
import json
from typing import Dict

from envoy_cfg.pipeline import EnvPipeline
from envoy_cfg.masking import mask_env
from envoy_cfg.validate import validate_env
from envoy_cfg.interpolate import interpolate_env


def _load_dotenv(path: str) -> Dict[str, str]:
    env: Dict[str, str] = {}
    with open(path) as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            env[key.strip()] = value.strip().strip('"').strip("'")
    return env


def cmd_pipeline_run(args: argparse.Namespace) -> None:
    env = _load_dotenv(args.file)

    pipeline = EnvPipeline()

    if args.interpolate:
        def _interp(e: Dict[str, str]) -> Dict[str, str]:
            from envoy_cfg.interpolate import interpolate_env as _ie
            r = _ie(e)
            return r.env
        pipeline.add_step("interpolate", _interp)

    if args.mask:
        pipeline.add_step("mask", mask_env)

    result = pipeline.run(env)

    if not result.success:
        print(f"[error] Pipeline failed: {result.error}")
        return

    print(f"Steps applied : {result.steps_applied}")
    print(f"Steps skipped : {result.steps_skipped}")
    print()
    if args.output_format == "json":
        print(json.dumps(result.final_env, indent=2))
    else:
        for k, v in sorted(result.final_env.items()):
            print(f"{k}={v}")


def register_pipeline_commands(subparsers: argparse._SubParsersAction) -> None:  # noqa: SLF001
    p = subparsers.add_parser("pipeline", help="Run a transformation pipeline on an env file")
    p.add_argument("file", help="Path to .env file")
    p.add_argument("--interpolate", action="store_true", help="Apply variable interpolation")
    p.add_argument("--mask", action="store_true", help="Mask secret values in output")
    p.add_argument(
        "--output-format",
        choices=["dotenv", "json"],
        default="dotenv",
        help="Output format (default: dotenv)",
    )
    p.set_defaults(func=cmd_pipeline_run)
