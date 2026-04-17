import pytest
from envoy_cfg.copy import copy_keys, CopyResult


@pytest.fixture
def source():
    return {"DB_HOST": "localhost", "DB_PORT": "5432", "SECRET_KEY": "abc123", "DEBUG": "true"}


@pytest.fixture
def dest():
    return {"APP_NAME": "myapp", "DB_HOST": "prod-host"}


def test_copy_keys_returns_copy_result(source, dest):
    result = copy_keys(source, dest, keys=["DEBUG"])
    assert isinstance(result, CopyResult)


def test_copy_keys_copies_missing_key(source, dest):
    result = copy_keys(source, dest, keys=["DEBUG"])
    assert "DEBUG" in result.copied
    assert result.copied["DEBUG"] == "true"


def test_copy_keys_skips_existing_without_overwrite(source, dest):
    result = copy_keys(source, dest, keys=["DB_HOST"])
    assert "DB_HOST" in result.skipped
    assert "DB_HOST" not in result.copied


def test_copy_keys_overwrites_when_flag_set(source, dest):
    result = copy_keys(source, dest, keys=["DB_HOST"], overwrite=True)
    assert "DB_HOST" in result.copied
    assert result.copied["DB_HOST"] == "localhost"
    assert "DB_HOST" in result.overwritten


def test_copy_keys_skips_missing_source_key(source, dest):
    result = copy_keys(source, dest, keys=["NONEXISTENT"])
    assert "NONEXISTENT" in result.skipped


def test_copy_keys_with_prefix(source, dest):
    result = copy_keys(source, dest, keys=["DB_HOST", "DB_PORT"], prefix="COPY_", overwrite=True)
    assert "COPY_DB_HOST" in result.copied
    assert "COPY_DB_PORT" in result.copied


def test_copy_keys_is_clean_when_no_skips(source, dest):
    result = copy_keys(source, dest, keys=["DEBUG", "DB_PORT"])
    assert result.is_clean()


def test_copy_keys_not_clean_when_skipped(source, dest):
    result = copy_keys(source, dest, keys=["DB_HOST"])
    assert not result.is_clean()


def test_copy_keys_strategy_keep_dest(source, dest):
    result = copy_keys(source, dest, keys=["DEBUG"])
    assert result.strategy == "keep-dest"


def test_copy_keys_strategy_overwrite(source, dest):
    result = copy_keys(source, dest, keys=["DB_HOST"], overwrite=True)
    assert result.strategy == "overwrite"


def test_copy_keys_does_not_mutate_dest(source, dest):
    original_dest = dict(dest)
    copy_keys(source, dest, keys=["DEBUG", "DB_PORT"])
    assert dest == original_dest


def test_copy_result_repr(source, dest):
    result = copy_keys(source, dest, keys=["DEBUG"])
    r = repr(result)
    assert "CopyResult" in r
    assert "strategy" in r
