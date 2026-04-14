"""CLI commands for namespace operations on environment variable keys."""

import argparse
import json
from typing import Dict

from envoy_cfg.namespace import (
    apply_namespace,
    strip_namespace,
    extract_namespace,
    list_namespaces,
)


def _load_dotenv(path: str) -> Dict[str, str]:
    env: Dict[str, str] = {}
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, _, v = line.partition("=")
            env[k.strip()] = v.strip()
    return env


def cmd_namespace_apply(args: argparse.Namespace) -> None:
    env = _load_dotenv(args.file)
    result = apply_namespace(env, args.namespace, args.separator)
    if args.format == "json":
        print(json.dumps(result.transformed, indent=2))
    else:
        for k, v in sorted(result.transformed.items()):
            print(f"{k}={v}")
    print(f"# {result.keys_affected} key(s) prefixed with '{args.namespace}'.")


def cmd_namespace_strip(args: argparse.Namespace) -> None:
    env = _load_dotenv(args.file)
    result = strip_namespace(env, args.namespace, args.separator)
    if args.format == "json":
        print(json.dumps(result.transformed, indent=2))
    else:
        for k, v in sorted(result.transformed.items()):
            print(f"{k}={v}")
    print(f"# {result.keys_affected} key(s) had prefix '{args.namespace}' stripped.")


def cmd_namespace_extract(args: argparse.Namespace) -> None:
    env = _load_dotenv(args.file)
    extracted = extract_namespace(env, args.namespace, args.separator)
    if args.format == "json":
        print(json.dumps(extracted, indent=2))
    else:
        for k, v in sorted(extracted.items()):
            print(f"{k}={v}")


def cmd_namespace_list(args: argparse.Namespace) -> None:
    env = _load_dotenv(args.file)
    namespaces = list_namespaces(env, args.separator)
    if namespaces:
        for ns in namespaces:
            print(ns)
    else:
        print("No namespaces detected.")


def register_namespace_commands(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("namespace", help="Namespace operations on env keys")
    sub = p.add_subparsers(dest="ns_cmd")

    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("file", help="Path to .env file")
    common.add_argument("--namespace", "-n", required=True, help="Namespace prefix")
    common.add_argument("--separator", default="__", help="Separator (default: __)")
    common.add_argument("--format", choices=["dotenv", "json"], default="dotenv")

    sub.add_parser("apply", parents=[common]).set_defaults(func=cmd_namespace_apply)
    sub.add_parser("strip", parents=[common]).set_defaults(func=cmd_namespace_strip)
    sub.add_parser("extract", parents=[common]).set_defaults(func=cmd_namespace_extract)

    lp = sub.add_parser("list", help="List detected namespaces")
    lp.add_argument("file", help="Path to .env file")
    lp.add_argument("--separator", default="__")
    lp.set_defaults(func=cmd_namespace_list)
