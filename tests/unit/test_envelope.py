"""Unit tests for threeway.envelope — signed event envelope (spec §6.2).

Exercises the sign/verify roundtrip, the signed-vs-ephemeral field split,
payload_digest determinism, idempotency_key sensitivity to revokes_event_id,
JSON roundtrip, and the well_formed structural guard. Signing keys come from
keys.generate_keypair(). Hermetic: no filesystem, network, or env access.
"""
from __future__ import annotations

import pytest
from cryptography.exceptions import InvalidSignature

from threeway import envelope, keys
from threeway.envelope import Event


def _make_event(**overrides) -> Event:
    """Build a minimally-complete, well-formed Event; overrides patch fields."""
    base = dict(
        id="evt-0001",
        seq=1,
        bus_id="bus-main",
        schema_version="1",
        kind="brief.publish",
        sender="seat:A:dir",
        recipient="seat:A:op",
        signer="seat:A:dir:session-uuid",
        payload={"pair": "A", "note": "hello"},
    )
    base.update(overrides)
    return Event(**base)


def test_sign_then_verify_passes():
    priv, pub_hex = keys.generate_keypair()
    ev = _make_event()
    assert ev.signature is None
    envelope.sign_event(ev, priv)
    assert isinstance(ev.signature, str) and ev.signature
    # No exception means the signature verifies.
    assert envelope.verify_event(ev, pub_hex) is None


def test_mutating_signed_field_breaks_verify():
    priv, pub_hex = keys.generate_keypair()
    ev = _make_event()
    envelope.sign_event(ev, priv)
    envelope.verify_event(ev, pub_hex)  # baseline passes

    # kind is part of the 14-field signed view -> tamper is detected.
    ev.kind = "brief.revoke"
    with pytest.raises(InvalidSignature):
        envelope.verify_event(ev, pub_hex)


def test_mutating_payload_breaks_verify_via_digest():
    # payload itself is not signed, but its digest is; changing payload changes
    # payload_digest, which IS in the signed view.
    priv, pub_hex = keys.generate_keypair()
    ev = _make_event()
    envelope.sign_event(ev, priv)
    ev.payload = {"pair": "A", "note": "tampered"}
    with pytest.raises(InvalidSignature):
        envelope.verify_event(ev, pub_hex)


def test_mutating_ephemeral_fields_does_not_break_verify():
    priv, pub_hex = keys.generate_keypair()
    ev = _make_event()
    envelope.sign_event(ev, priv)

    # created_at and signer are excluded from signed_bytes -> still verifies.
    ev.created_at = "2026-06-30T00:00:00Z"
    ev.signer = "seat:A:dir:some-other-session"
    assert envelope.verify_event(ev, pub_hex) is None


def test_verify_with_missing_signature_raises():
    _, pub_hex = keys.generate_keypair()
    ev = _make_event()  # never signed; signature is None
    with pytest.raises(InvalidSignature):
        envelope.verify_event(ev, pub_hex)


def test_payload_digest_is_deterministic_and_property_matches():
    ev1 = _make_event(payload={"b": 2, "a": 1})
    ev2 = _make_event(payload={"a": 1, "b": 2})  # different insertion order
    # Canonicalization makes key order irrelevant -> same digest.
    assert envelope.payload_digest(ev1) == envelope.payload_digest(ev2)
    # The property delegates to the module function.
    assert ev1.payload_digest == envelope.payload_digest(ev1)
    # A different payload yields a different digest.
    assert envelope.payload_digest(_make_event(payload={"a": 9})) != ev1.payload_digest


def test_idempotency_key_differs_with_revokes_event_id():
    ev_plain = _make_event()
    ev_revoke = _make_event(revokes_event_id="evt-prior")
    # Only revokes_event_id differs -> distinct dedup identity.
    assert envelope.idempotency_key(ev_plain) != envelope.idempotency_key(ev_revoke)
    # Two revokes of different targets are also distinct.
    ev_revoke_other = _make_event(revokes_event_id="evt-other")
    assert (
        envelope.idempotency_key(ev_revoke)
        != envelope.idempotency_key(ev_revoke_other)
    )
    # Stable for identical inputs.
    assert envelope.idempotency_key(ev_plain) == envelope.idempotency_key(_make_event())


def test_json_roundtrip_preserves_verifiability():
    priv, pub_hex = keys.generate_keypair()
    ev = _make_event(
        brief_id="brief-7",
        candidate_id="cand-3",
        subject_sha="abc123",
        brief_version=2,
        causation_id="evt-cause",
    )
    envelope.sign_event(ev, priv)

    obj = envelope.to_json_obj(ev)
    # Derived completeness fields are written at rest.
    assert obj["payload_digest"] == ev.payload_digest
    assert obj["idempotency_key"] == envelope.idempotency_key(ev)
    assert obj["from"] == ev.sender and obj["to"] == ev.recipient

    restored = envelope.from_json_obj(obj)
    assert restored.sender == ev.sender
    assert restored.recipient == ev.recipient
    assert restored.signature == ev.signature
    # The rebuilt event still verifies against the same public key.
    assert envelope.verify_event(restored, pub_hex) is None


def test_well_formed_true_for_good_event():
    assert envelope.well_formed(_make_event()) is True
    # Optional fields populated with correct types remain well-formed.
    ev = _make_event(brief_id="b", candidate_id="c", subject_sha="s", brief_version=3)
    assert envelope.well_formed(ev) is True


def test_well_formed_false_for_bad_types():
    # kind must be a str.
    assert envelope.well_formed(_make_event(kind=123)) is False
    # payload must be a dict.
    assert envelope.well_formed(_make_event(payload=["not", "a", "dict"])) is False
    # brief_version, when present, must be an int.
    assert envelope.well_formed(_make_event(brief_version="2")) is False
