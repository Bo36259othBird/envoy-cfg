"""Tests for envoy_cfg.encrypt."""

import pytest

from envoy_cfg.encrypt import (
    decrypt_env,
    decrypt_value,
    encrypt_env,
    encrypt_value,
    is_encrypted,
)

PASS = "super-secret-passphrase"


# ---------------------------------------------------------------------------
# is_encrypted
# ---------------------------------------------------------------------------

def test_is_encrypted_returns_true_for_token():
    token = encrypt_value("hello", PASS)
    assert is_encrypted(token) is True


def test_is_encrypted_returns_false_for_plaintext():
    assert is_encrypted("plaintext") is False


def test_is_encrypted_returns_false_for_empty_string():
    assert is_encrypted("") is False


# ---------------------------------------------------------------------------
# encrypt_value / decrypt_value round-trip
# ---------------------------------------------------------------------------

def test_encrypt_decrypt_roundtrip():
    original = "my-database-password"
    token = encrypt_value(original, PASS)
    assert decrypt_value(token, PASS) == original


def test_encrypt_produces_different_tokens_each_call():
    """Random salt means two encryptions of the same value differ."""
    t1 = encrypt_value("value", PASS)
    t2 = encrypt_value("value", PASS)
    assert t1 != t2


def test_decrypt_wrong_passphrase_gives_garbage_not_original():
    token = encrypt_value("secret", PASS)
    result = decrypt_value(token, "wrong-passphrase")
    assert result != "secret"


def test_decrypt_invalid_token_raises():
    with pytest.raises(ValueError, match="does not appear to be encrypted"):
        decrypt_value("plaintext", PASS)


def test_encrypt_empty_string():
    token = encrypt_value("", PASS)
    assert decrypt_value(token, PASS) == ""


def test_encrypt_unicode_value():
    original = "pässwörд-🔑"
    token = encrypt_value(original, PASS)
    assert decrypt_value(token, PASS) == original


# ---------------------------------------------------------------------------
# encrypt_env / decrypt_env
# ---------------------------------------------------------------------------

def test_encrypt_env_all_keys():
    env = {"DB_PASS": "secret", "APP_NAME": "myapp"}
    encrypted = encrypt_env(env, PASS)
    assert is_encrypted(encrypted["DB_PASS"])
    assert is_encrypted(encrypted["APP_NAME"])


def test_encrypt_env_selected_keys_only():
    env = {"DB_PASS": "secret", "APP_NAME": "myapp"}
    encrypted = encrypt_env(env, PASS, keys=["DB_PASS"])
    assert is_encrypted(encrypted["DB_PASS"])
    assert not is_encrypted(encrypted["APP_NAME"])


def test_encrypt_env_skips_already_encrypted():
    env = {"DB_PASS": "secret"}
    once = encrypt_env(env, PASS)
    twice = encrypt_env(once, PASS)
    # Still only one layer of encryption
    assert decrypt_value(twice["DB_PASS"], PASS) == "secret"


def test_decrypt_env_roundtrip():
    env = {"DB_PASS": "s3cr3t", "PORT": "5432"}
    encrypted = encrypt_env(env, PASS)
    decrypted = decrypt_env(encrypted, PASS)
    assert decrypted == env


def test_decrypt_env_leaves_plaintext_untouched():
    env = {"APP_NAME": "myapp", "PORT": "8080"}
    result = decrypt_env(env, PASS)
    assert result == env
