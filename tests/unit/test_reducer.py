"""Unit tests for threeway.reducer.reduce -> EffectiveState (spec §6.1).

The reducer folds append-only facts in seq order; it does NOT verify signatures,
so unsigned (but well-formed) Events suffice here. Events are built minimally via
_ev(); behavior asserted is read directly from reducer.py / envelope.py.
"""
from __future__ import annotations

from threeway.envelope import Event
from threeway.reducer import EffectiveState, reduce


def _ev(kind, *, signer, seq=0, payload=None, candidate_id=None, brief_id=None,
        brief_version=None, subject_sha=None, ev_id=None, revokes_event_id=None,
        supersedes_event_id=None) -> Event:
    """A minimal well_formed Event. payload defaults to an empty dict (required:
    well_formed insists payload is a dict). id defaults to a kind/signer-derived
    string so seat_by_id indexing stays sane."""
    return Event(
        id=ev_id if ev_id is not None else f"{kind}-{signer}-{candidate_id}-{seq}",
        seq=seq,
        bus_id="bus1",
        schema_version="threeway/1",
        kind=kind,
        sender=signer.split(":", 1)[0],
        recipient="all",
        signer=signer,
        payload={} if payload is None else payload,
        brief_id=brief_id,
        candidate_id=candidate_id,
        brief_version=brief_version,
        subject_sha=subject_sha,
        revokes_event_id=revokes_event_id,
        supersedes_event_id=supersedes_event_id,
    )


def test_reduce_empty_yields_default_state():
    st = reduce([])
    assert isinstance(st, EffectiveState)
    # Default state: every documented accessor is empty / returns None.
    assert st.assignments() == []
    assert st.aborted_candidate_ids() == []
    assert st.authoritative_candidate("A:c1") is None
    assert st.brief("b1", 1) is None
    assert st.is_aborted("A:c1") is False


def test_brief_then_candidate_become_queryable():
    # brief is overseer-authority (must be signed by an overseer seat to land).
    brief = _ev("brief", signer="overseer:claude:s1", seq=1,
                brief_id="b1", brief_version=2, candidate_id="A:c1")
    # assignment binds pair "A" to executing_coordinator "coordA".
    assignment = _ev("assignment", signer="overseer:claude:s1", seq=2,
                     payload={"pair": "A", "executing_coordinator": "coordA"})
    # candidate declares pair "A", signed by the assigned coordinator seat.
    candidate = _ev("candidate", signer="coordA:claude:s9", seq=3,
                    candidate_id="A:c1", payload={"pair": "A"})

    st = reduce([brief, assignment, candidate])

    # brief is queryable by (brief_id, version) and is the latest live version.
    assert st.brief("b1", 2) is brief
    assert st.latest_brief_version("b1") == 2
    # candidate is authoritative: namespace "A" == declared pair == assigned coordinator's seat.
    assert st.authoritative_candidate("A:c1") is candidate
    # locate-only candidate() also finds it.
    assert st.candidate("A:c1") is candidate
    assert st.candidate("A:c1", "coordA") is candidate


def test_candidate_with_no_abort_is_not_aborted():
    assignment = _ev("assignment", signer="overseer:claude:s1", seq=1,
                     payload={"pair": "A", "executing_coordinator": "coordA"})
    candidate = _ev("candidate", signer="coordA:claude:s9", seq=2,
                    candidate_id="A:c1", payload={"pair": "A"})
    st = reduce([assignment, candidate])
    assert st.is_aborted("A:c1") is False
    assert st.aborted_candidate_ids() == []


def test_authorized_abort_marks_candidate_aborted():
    # ADR-059: abort is effective iff the bound pair's executing_coordinator is among
    # the aborting seats.
    assignment = _ev("assignment", signer="overseer:claude:s1", seq=1,
                     payload={"pair": "A", "executing_coordinator": "coordA"})
    abort = _ev("candidate_aborted", signer="coordA:claude:s9", seq=2,
                candidate_id="A:c1")
    st = reduce([assignment, abort])
    assert st.is_aborted("A:c1") is True
    assert st.aborted_candidate_ids() == ["A:c1"]


def test_unauthorized_abort_is_recorded_but_not_effective():
    # An abort from a seat that is NOT the bound pair's coordinator must be dropped
    # by is_aborted (fail-safe), though it is still listed by aborted_candidate_ids.
    assignment = _ev("assignment", signer="overseer:claude:s1", seq=1,
                     payload={"pair": "A", "executing_coordinator": "coordA"})
    abort = _ev("candidate_aborted", signer="attacker:claude:s9", seq=2,
                candidate_id="A:c1")
    st = reduce([assignment, abort])
    assert st.is_aborted("A:c1") is False
    # The id is still surfaced for the rework breaker to re-check authority.
    assert st.aborted_candidate_ids() == ["A:c1"]


def test_duplicate_attestation_latest_seq_wins():
    # Two attestations on the same (candidate_id, att_kind, seat): folded in seq order,
    # so the higher-seq event wins the slot (ADR "latest verdict" semantics).
    older = _ev("attestation", signer="operator:claude:s1", seq=5,
                candidate_id="A:c1", payload={"kind": "release", "verdict": "old"})
    newer = _ev("attestation", signer="operator:claude:s2", seq=9,
                candidate_id="A:c1", payload={"kind": "release", "verdict": "new"})
    # Feed out of order to prove the seq sort, not list order, decides.
    st = reduce([newer, older])
    eff = st.effective_attestation("A:c1", "release", "operator")
    assert eff is newer
    assert eff.payload["verdict"] == "new"


def test_attestation_revoked_by_signer_seat_drops_it():
    # ADR-036: a revoke is authorized from the target event's own signer seat.
    att = _ev("attestation", signer="operator:claude:s1", seq=1,
              candidate_id="A:c1", payload={"kind": "release"}, ev_id="att-1")
    revoke = _ev("attestation_revoked", signer="operator:claude:s2", seq=2,
                 candidate_id="A:c1", revokes_event_id="att-1")
    st = reduce([att, revoke])
    # The attestation event is in the revoked set, so effective lookup returns None.
    assert st.effective_attestation("A:c1", "release", "operator") is None


def test_unauthorized_revoke_is_ignored():
    # A revoke from a different (non-overseer, non-target) seat must NOT take effect.
    att = _ev("attestation", signer="operator:claude:s1", seq=1,
              candidate_id="A:c1", payload={"kind": "release"}, ev_id="att-1")
    revoke = _ev("attestation_revoked", signer="attacker:claude:s2", seq=2,
                 candidate_id="A:c1", revokes_event_id="att-1")
    st = reduce([att, revoke])
    # Revoke ignored -> attestation still effective.
    assert st.effective_attestation("A:c1", "release", "operator") is att


def test_non_overseer_brief_is_dropped():
    # brief is an overseer-authority singleton; a brief signed by any other seat is
    # dropped at record time and never becomes queryable.
    forged = _ev("brief", signer="attacker:claude:s1", seq=1,
                 brief_id="b1", brief_version=1, candidate_id="A:c1")
    st = reduce([forged])
    assert st.brief("b1", 1) is None
    assert st.latest_brief_version("b1") is None


def test_malformed_envelope_event_is_dropped_not_raised():
    # ADR-041: well_formed filter drops an event with a non-dict payload (here a list)
    # up front, with a warning — it must not raise nor partially enter state.
    bad = _ev("candidate", signer="coordA:claude:s9", seq=1,
              candidate_id="A:c1", payload={"pair": "A"})
    bad.payload = ["not", "a", "dict"]  # corrupt the envelope post-build
    good_assignment = _ev("assignment", signer="overseer:claude:s1", seq=2,
                          payload={"pair": "A", "executing_coordinator": "coordA"})
    st = reduce([bad, good_assignment])
    # The malformed candidate never landed; the well-formed assignment did.
    assert st.candidate("A:c1") is None
    assert st.authoritative_candidate("A:c1") is None
    assert len(st.assignments()) == 1


def test_shadow_candidate_does_not_capture_authority():
    # ADR-042: a candidate whose declared pair != the candidate_id namespace, or whose
    # signer != the assigned coordinator, is not self-consistent and cannot be authoritative.
    assignment = _ev("assignment", signer="overseer:claude:s1", seq=1,
                     payload={"pair": "A", "executing_coordinator": "coordA"})
    # Legit candidate for A:c1, signed by coordA, declares pair A.
    legit = _ev("candidate", signer="coordA:claude:s2", seq=2,
                candidate_id="A:c1", payload={"pair": "A"})
    # Shadow: same id, but signed by a non-coordinator seat (not self-consistent).
    shadow = _ev("candidate", signer="rogue:claude:s3", seq=3,
                 candidate_id="A:c1", payload={"pair": "A"})
    st = reduce([assignment, legit, shadow])
    assert st.authoritative_candidate("A:c1") is legit
