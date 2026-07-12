"""Orthogonal packet-state derivation from legacy fields (ADR-017)."""
from __future__ import annotations

import packet_state


def _pkt(**overrides) -> dict:
    base = {
        "id": "p", "wave": 2, "cycle": "c", "owner": "director",
        "packet_type": "director-implementation", "status": "active",
        "done_evidence": [], "verify_request": None, "commit_range": None,
    }
    base.update(overrides)
    return base


# --- work_state derivation ---
def test_ready_derives_ready():
    assert packet_state.derive_work_state(_pkt(status="ready")) == "ready"


def test_active_derives_running():
    assert packet_state.derive_work_state(_pkt(status="active")) == "running"


def test_done_derives_completed():
    assert packet_state.derive_work_state(_pkt(status="done", done_evidence=["x"])) == "completed"


def test_blocked_without_evidence_stays_blocked():
    assert packet_state.derive_work_state(_pkt(status="blocked", done_evidence=[])) == "blocked"


def test_blocked_with_evidence_is_completed_the_overloading():
    # THE P0.2 thesis: a 'blocked' packet carrying completion evidence is work-complete.
    pkt = _pkt(status="blocked", packet_type="director-preflight",
               done_evidence=["coordination/mailbox/sent/…records CLEAR at reviewed route commit …"])
    assert packet_state.derive_work_state(pkt) == "completed"


def test_excepted_derives_completed():
    assert packet_state.derive_work_state(_pkt(status="excepted")) == "completed"


def test_unknown_status_is_queued():
    assert packet_state.derive_work_state(_pkt(status="")) == "queued"


# --- verification_state derivation ---
def test_coordinator_route_not_required():
    assert packet_state.derive_verification_state(_pkt(packet_type="coordinator-route", status="active")) == "not_required"


def test_preflight_not_required():
    assert packet_state.derive_verification_state(_pkt(packet_type="director-preflight", status="blocked", done_evidence=["x"])) == "not_required"


def test_completed_implementation_is_pending_verification():
    pkt = _pkt(packet_type="director-implementation", status="done", done_evidence=["landed"])
    assert packet_state.derive_verification_state(pkt) == "pending"


def test_operator_verification_parses_go():
    pkt = _pkt(packet_type="operator-verification", status="done",
               done_evidence=["verification-report: VERDICT GO for range abc..def"])
    assert packet_state.derive_verification_state(pkt) == "go"


def test_operator_verification_parses_fail():
    pkt = _pkt(packet_type="operator-verification", status="done", done_evidence=["FAIL: regression"])
    assert packet_state.derive_verification_state(pkt) == "fail"


def test_operator_verification_parses_nits():
    pkt = _pkt(packet_type="operator-verification", status="done", done_evidence=["NITS: minor doc"])
    assert packet_state.derive_verification_state(pkt) == "nits"


def test_operator_verification_completed_without_verdict_is_unable():
    pkt = _pkt(packet_type="operator-verification", status="done", done_evidence=["did the review"])
    assert packet_state.derive_verification_state(pkt) == "unable_to_verify"


def test_go_word_boundary_not_substring():
    # 'ago' or 'going' must not match the GO verdict token.
    pkt = _pkt(packet_type="operator-verification", status="done",
               done_evidence=["a while ago the work was ongoing"])
    assert packet_state.derive_verification_state(pkt) == "unable_to_verify"


# --- transition table ---
def test_valid_transitions():
    assert packet_state.is_valid_work_transition("ready", "running")
    assert packet_state.is_valid_work_transition("running", "completed")
    assert packet_state.is_valid_work_transition("running", "blocked")
    assert packet_state.is_valid_work_transition("blocked", "running")


def test_invalid_transitions():
    assert not packet_state.is_valid_work_transition("completed", "running")
    assert not packet_state.is_valid_work_transition("superseded", "running")
    assert not packet_state.is_valid_work_transition("ready", "completed")


def test_every_transition_target_is_a_known_state():
    known = set(packet_state.WORK_STATES)
    for src, dsts in packet_state.WORK_TRANSITIONS.items():
        assert src in known
        assert dsts <= known
