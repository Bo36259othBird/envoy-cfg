"""Encryption utilities for securing environment variable values at rest."""

import base64
import hashlib
import os
from dataclasses import dataclass
from typing import Dict, Optional

_MARKER = "enc:"


def _derive_key(passphrase: str, salt: bytes) -> bytes:
    """Derive a 32-byte key from a passphrase using PBKDF2."""
    return hashlib.pbkdf2_hmac("sha256", passphrase.encode(), salt, iterations=100_000)


def encrypt_value(value: str, passphrase: str) -> str:
    """Encrypt a plaintext value and return a base64-encoded ciphertext string.

    The returned string is prefixed with ``enc:`` so it can be identified later.
    Uses XOR with a derived key (lightweight; swap for AES in production).
    """
    salt = os.urandom(16)
    key = _derive_key(passphrase, salt)
    data = value.encode("utf-8")
    # Repeat key to cover data length
    key_stream = (key * (len(data) // len(key) + 1))[: len(data)]
    ciphertext = bytes(b ^ k for b, k in zip(data, key_stream))
    payload = salt + ciphertext
    return _MARKER + base64.b64encode(payload).decode("ascii")


def decrypt_value(token: str, passphrase: str) -> str:
    """Decrypt a value previously encrypted with :func:`encrypt_value`.

    Raises ``ValueError`` if the token is not a valid encrypted value.
    """
    if not token.startswith(_MARKER):
        raise ValueError(f"Value does not appear to be encrypted: {token!r}")
    payload = base64.b64decode(token[len(_MARKER):])
    salt, ciphertext = payload[:16], payload[16:]
    key = _derive_key(passphrase, salt)
    key_stream = (key * (len(ciphertext) // len(key) + 1))[: len(ciphertext)]
    plaintext = bytes(b ^ k for b, k in zip(ciphertext, key_stream))
    return plaintext.decode("utf-8")


def is_encrypted(value: str) -> bool:
    """Return True if *value* looks like an encrypted token."""
    return value.startswith(_MARKER)


def encrypt_env(env: Dict[str, str], passphrase: str, keys: Optional[list] = None) -> Dict[str, str]:
    """Return a copy of *env* with selected (or all) values encrypted."""
    result = dict(env)
    targets = keys if keys is not None else list(env.keys())
    for k in targets:
        if k in result and not is_encrypted(result[k]):
            result[k] = encrypt_value(result[k], passphrase)
    return result


def decrypt_env(env: Dict[str, str], passphrase: str) -> Dict[str, str]:
    """Return a copy of *env* with all encrypted values decrypted."""
    result = {}
    for k, v in env.items():
        result[k] = decrypt_value(v, passphrase) if is_encrypted(v) else v
    return result
