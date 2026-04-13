"""Tests for envoy_cfg.template module."""

import pytest
from envoy_cfg.template import render_template, TemplateRenderResult


def test_render_no_interpolation():
    env = {"HOST": "localhost", "PORT": "8080"}
    result = render_template(env)
    assert result.rendered == {"HOST": "localhost", "PORT": "8080"}
    assert result.success
    assert result.unresolved == []
    assert result.errors == []


def test_render_simple_interpolation():
    env = {"BASE_URL": "http://${HOST}:${PORT}", "HOST": "example.com", "PORT": "443"}
    result = render_template(env)
    assert result.rendered["BASE_URL"] == "http://example.com:443"
    assert result.success


def test_render_chained_interpolation():
    env = {
        "PROTO": "https",
        "HOST": "api.example.com",
        "BASE": "${PROTO}://${HOST}",
        "FULL_URL": "${BASE}/v1",
    }
    result = render_template(env)
    assert result.rendered["FULL_URL"] == "https://api.example.com/v1"
    assert result.success


def test_render_unresolved_reference():
    env = {"URL": "http://${UNDEFINED_HOST}/path"}
    result = render_template(env)
    assert "UNDEFINED_HOST" in result.unresolved
    assert not result.success
    assert "${UNDEFINED_HOST}" in result.rendered["URL"]


def test_render_circular_reference():
    env = {"A": "${B}", "B": "${A}"}
    result = render_template(env)
    assert len(result.errors) > 0
    assert any("Circular" in e for e in result.errors)


def test_render_empty_env():
    result = render_template({})
    assert result.rendered == {}
    assert result.success


def test_render_value_without_template_syntax():
    env = {"PLAIN": "no-interpolation-here", "NUM": "42"}
    result = render_template(env)
    assert result.rendered["PLAIN"] == "no-interpolation-here"
    assert result.rendered["NUM"] == "42"


def test_render_partial_interpolation():
    env = {"MSG": "Hello ${NAME}, your id is ${MISSING_ID}", "NAME": "Alice"}
    result = render_template(env)
    assert result.rendered["MSG"] == "Hello Alice, your id is ${MISSING_ID}"
    assert "MISSING_ID" in result.unresolved
    assert not result.success


def test_render_result_repr():
    result = TemplateRenderResult(
        rendered={"A": "1"},
        unresolved=["X"],
        errors=[]
    )
    r = repr(result)
    assert "TemplateRenderResult" in r
    assert "unresolved" in r


def test_render_multiple_unresolved_deduplicated():
    env = {
        "A": "${MISSING}",
        "B": "${MISSING}/extra",
    }
    result = render_template(env)
    assert result.unresolved.count("MISSING") == 1
