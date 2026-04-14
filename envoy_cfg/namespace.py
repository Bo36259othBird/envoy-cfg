"""Namespace support for grouping and prefixing environment variable keys."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class NamespaceResult:
    namespace: str
    original: Dict[str, str]
    transformed: Dict[str, str]
    keys_affected: int

    def __repr__(self) -> str:
        return (
            f"<NamespaceResult ns={self.namespace!r} "
            f"keys_affected={self.keys_affected}>"
        )


def apply_namespace(env: Dict[str, str], namespace: str, separator: str = "__") -> NamespaceResult:
    """Prefix all keys in env with the given namespace."""
    if not namespace:
        raise ValueError("Namespace must not be empty.")
    prefix = namespace.upper() + separator
    transformed = {prefix + k: v for k, v in env.items()}
    return NamespaceResult(
        namespace=namespace,
        original=dict(env),
        transformed=transformed,
        keys_affected=len(transformed),
    )


def strip_namespace(env: Dict[str, str], namespace: str, separator: str = "__") -> NamespaceResult:
    """Remove a namespace prefix from all matching keys."""
    if not namespace:
        raise ValueError("Namespace must not be empty.")
    prefix = namespace.upper() + separator
    transformed = {
        (k[len(prefix):] if k.startswith(prefix) else k): v
        for k, v in env.items()
    }
    keys_affected = sum(1 for k in env if k.startswith(prefix))
    return NamespaceResult(
        namespace=namespace,
        original=dict(env),
        transformed=transformed,
        keys_affected=keys_affected,
    )


def extract_namespace(env: Dict[str, str], namespace: str, separator: str = "__") -> Dict[str, str]:
    """Return only the keys belonging to a namespace, with the prefix stripped."""
    if not namespace:
        raise ValueError("Namespace must not be empty.")
    prefix = namespace.upper() + separator
    return {k[len(prefix):]: v for k, v in env.items() if k.startswith(prefix)}


def list_namespaces(env: Dict[str, str], separator: str = "__") -> List[str]:
    """Detect all distinct namespace prefixes present in the env keys."""
    namespaces = set()
    for key in env:
        if separator in key:
            ns = key.split(separator, 1)[0]
            namespaces.add(ns)
    return sorted(namespaces)
