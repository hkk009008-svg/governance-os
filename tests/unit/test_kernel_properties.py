"""Property + fuzz tests over the ADR-014..017 kernel validators (ADR-018).

Invariants under generated inputs: validators never crash (they return issues
or raise only their own typed errors), fail closed, are deterministic and
non-mutating, and produce only vocabulary values.
"""
from __future__ import annotations

import copy

from hypothesis import HealthCheck, given, settings, strategies as st

import packet_state
import route_lineage

settings.register_profile("ci", settings(derandomize=True, max_examples=200,
                                         deadline=None,
                                         suppress_health_check=[HealthCheck.too_slow]))
settings.load_profile("ci")


# ---- route_lineage.resolve_authoritative ----
_gen = st.one_of(st.none(), st.integers(min_value=1, max_value=6))
_lineage_route = st.builds(
    route_lineage.LineageRoute,
    route_id=st.text(min_size=1, max_size=6),
    lineage=st.builds(route_lineage.RouteLineage, generation=_gen,
                      parent_route_id=st.one_of(st.none(), st.text(min_size=1, max_size=6)),
                      expected_control_head=st.none()),
)


@given(st.lists(_lineage_route, max_size=8))
def test_resolve_authoritative_never_crashes(routes):
    res = route_lineage.resolve_authoritative(routes)
    assert res.mode in ("empty", "legacy", "lineage")


@given(st.lists(_lineage_route, min_size=1, max_size=8))
def test_resolve_authoritative_order_independent(routes):
    import random as _r
    shuffled = routes[:]
    _r.Random(0).shuffle(shuffled)
    assert route_lineage.resolve_authoritative(routes).winner == \
           route_lineage.resolve_authoritative(shuffled).winner


# check_cas is fail-closed: ok is True IFF proposed.parent == current tip AND both
# generations are int AND proposed.gen == current.gen + 1 (refused in every other case).
@st.composite
def _cas_pair(draw):
    current = draw(_lineage_route)
    # Bias toward exercising the accept path: sometimes point proposed at the tip
    # and/or set its generation to the exact successor.
    parent = current.route_id if draw(st.booleans()) else draw(
        st.one_of(st.none(), st.text(min_size=1, max_size=6)))
    cur_gen = current.lineage.generation
    if draw(st.booleans()) and cur_gen is not None:
        gen = cur_gen + 1
    else:
        gen = draw(_gen)
    proposed = route_lineage.LineageRoute(
        route_id=draw(st.text(min_size=1, max_size=6)),
        lineage=route_lineage.RouteLineage(generation=gen, parent_route_id=parent,
                                           expected_control_head=None),
    )
    return current, proposed


@given(_cas_pair())
def test_check_cas_fail_closed(pair):
    current, proposed = pair
    res = route_lineage.check_cas(current, proposed)
    expected = (
        proposed.lineage.parent_route_id == current.route_id
        and isinstance(current.lineage.generation, int)
        and isinstance(proposed.lineage.generation, int)
        and proposed.lineage.generation == current.lineage.generation + 1
    )
    assert res.ok is expected


# ---- packet_state.derive_* ----
_status = st.one_of(st.sampled_from(["ready", "active", "blocked", "done", "excepted", "", "paused"]),
                    st.text(max_size=8))
_ptype = st.one_of(st.sampled_from(sorted(packet_state.NON_VERIFIED_TYPES) +
                                   ["director-implementation", "operator-verification"]),
                   st.text(max_size=10))
_packet = st.fixed_dictionaries({
    "status": _status, "packet_type": _ptype,
    "done_evidence": st.lists(st.text(max_size=20), max_size=4),
})


@given(_packet)
def test_derive_work_state_in_vocab_and_no_crash(pkt):
    assert packet_state.derive_work_state(pkt) in packet_state.WORK_STATES


@given(_packet)
def test_derive_verification_state_in_vocab(pkt):
    assert packet_state.derive_verification_state(pkt) in packet_state.VERIFICATION_STATES


@given(_packet)
def test_derive_does_not_mutate(pkt):
    snap = copy.deepcopy(pkt)
    packet_state.derive_work_state(pkt)
    packet_state.derive_verification_state(pkt)
    assert pkt == snap


@given(_packet)
def test_blocked_with_evidence_always_completed(pkt):
    ev = [e for e in pkt["done_evidence"] if e.strip()]
    if pkt["status"] == "blocked":
        expected = "completed" if ev else "blocked"
        assert packet_state.derive_work_state(pkt) == expected
