"""Property + fuzz tests over the ADR-014..017 kernel validators (ADR-018).

Invariants under generated inputs: validators never crash (they return issues
or raise only their own typed errors), fail closed, are deterministic and
non-mutating, and produce only vocabulary values.
"""
from __future__ import annotations

import copy

from hypothesis import HealthCheck, given, settings, strategies as st

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
