"""Unit tests for threeway.canon — the RFC 8785 (JCS) canonicalizer.

canonicalize() is the single chokepoint over which every signature/digest in the
package is computed, so determinism and key-order independence are load-bearing.
These tests pin the contract: stable bytes output, key-order independence, a known
encoding, order-preserving lists, and refusal to canonicalize NaN/Infinity/non-JSON.
"""
from __future__ import annotations

import pytest
import rfc8785

from threeway import canon


def test_returns_bytes():
    out = canon.canonicalize({"a": 1})
    assert isinstance(out, bytes)


def test_known_encoding():
    # RFC 8785: no whitespace, minimal separators.
    assert canon.canonicalize({"a": 1}) == b'{"a":1}'


def test_deterministic_repeated_calls():
    obj = {"b": 1, "a": 2, "c": [3, 2, 1]}
    first = canon.canonicalize(obj)
    second = canon.canonicalize(obj)
    assert first == second


def test_key_order_independence():
    # Two dicts with the same entries in different insertion order must
    # canonicalize identically — keys are sorted by RFC 8785.
    assert canon.canonicalize({"b": 1, "a": 2}) == canon.canonicalize({"a": 2, "b": 1})


def test_keys_are_sorted_in_output():
    # Explicit byte form proves lexicographic key ordering, not just equality.
    assert canon.canonicalize({"b": 1, "a": 2}) == b'{"a":2,"b":1}'


def test_list_preserves_order():
    # Array order is semantically significant and must NOT be reordered.
    assert canon.canonicalize([3, 1, 2]) == b"[3,1,2]"
    assert canon.canonicalize([3, 1, 2]) != canon.canonicalize([1, 2, 3])


def test_nested_structures_stable_and_keys_sorted():
    nested = {"z": {"b": 1, "a": 2}, "a": [1, 2]}
    reordered = {"a": [1, 2], "z": {"a": 2, "b": 1}}
    # Same logical value built with different key orders -> identical bytes,
    # with both the outer and inner object keys sorted.
    assert canon.canonicalize(nested) == canon.canonicalize(reordered)
    assert canon.canonicalize(nested) == b'{"a":[1,2],"z":{"a":2,"b":1}}'


@pytest.mark.parametrize("bad", [float("nan"), float("inf"), float("-inf")])
def test_raises_on_non_finite_floats(bad):
    # NaN/Infinity are not representable in JSON; canonicalize must refuse them
    # rather than silently sign unrepresentable input. FloatDomainError is a
    # subclass of the public CanonicalizationError.
    with pytest.raises(rfc8785.CanonicalizationError):
        canon.canonicalize(bad)


def test_raises_on_non_json_object():
    # A set is not a JSON value; canonicalize must raise rather than coerce.
    with pytest.raises(rfc8785.CanonicalizationError):
        canon.canonicalize({1, 2, 3})


def test_unicode_encoded_as_utf8():
    # Non-ASCII strings are emitted as raw UTF-8 bytes (RFC 8785 does not
    # \u-escape them), and the result round-trips back through UTF-8 decode.
    out = canon.canonicalize({"ñ": "é"})
    assert isinstance(out, bytes)
    assert out == '{"ñ":"é"}'.encode("utf-8")
