"""Property + fuzz tests over the ADR-014..017 kernel validators (ADR-018).

Invariants under generated inputs: validators never crash (they return issues
or raise only their own typed errors), fail closed, are deterministic and
non-mutating, and produce only vocabulary values.
"""
from __future__ import annotations

import copy
import tempfile
from pathlib import Path

from hypothesis import HealthCheck, given, settings, strategies as st

import packet_state
import route_lineage
import route_manifest
import test_route_manifest as tr  # sibling test module: reusable valid-baseline builders

settings.register_profile("ci", settings(derandomize=True, max_examples=200,
                                         deadline=None,
                                         suppress_health_check=[HealthCheck.too_slow]))
settings.load_profile("ci")

# --- arbitrary JSON-ish values (bounded) ---
_json_scalars = st.one_of(st.none(), st.booleans(), st.integers(min_value=-5, max_value=5),
                          st.text(max_size=8))
_arb = st.recursive(_json_scalars,
                    lambda c: st.one_of(st.lists(c, max_size=4),
                                        st.dictionaries(st.text(max_size=6), c, max_size=4)),
                    max_leaves=12)

# Printable-ASCII text with NO control chars (codepoints 32..126 exclude \n=10, \r=13),
# used to fuzz benign route fields so a generated route stays VALID + round-trippable.
_benign_text = st.text(alphabet=st.characters(min_codepoint=32, max_codepoint=126), max_size=40)


# ---- route_manifest.validate_route_object ----
@given(st.dictionaries(st.text(max_size=10), _arb, max_size=10))
def test_validate_route_object_never_crashes_and_returns_list(obj):
    issues = route_manifest.validate_route_object(obj)
    assert isinstance(issues, list)


@given(st.dictionaries(st.text(max_size=10), _arb, max_size=10))
def test_validate_route_object_does_not_mutate(obj):
    snap = copy.deepcopy(obj)
    route_manifest.validate_route_object(obj)
    assert obj == snap


# A generated VALID route (built from the known-good baseline with fuzzed benign text
# fields) is valid, hashes key-order-independently, and round-trips
# render_markdown -> write_route_pair -> read_manifest back to the same object.
@given(tb=_benign_text, jc=_benign_text, nt=_benign_text)
def test_valid_route_roundtrips_and_hash_order_independent(tb, jc, nt):
    # Prefix each fuzzed value with fixed non-weak, non-empty text so the field stays
    # a valid non-empty / non-weak trigger and (for next_trigger, rendered at line
    # start) can never form a second "route_hash:" pin line in the projection.
    route = tr._route(
        task_board="board-" + tb,
        join_condition="coordinator closes: " + jc,
        next_trigger="Director continues: " + nt,
    )
    assert route_manifest.validate_route_object(route) == []

    reversed_route = dict(reversed(list(route.items())))
    assert route_manifest.route_hash(route) == route_manifest.route_hash(reversed_route)
    assert len(route_manifest.route_hash(route)) == 64

    with tempfile.TemporaryDirectory() as d:
        md_path, _sidecar = route_manifest.write_route_pair(Path(d), route, title="fuzz")
        assert route_manifest.read_manifest(md_path) == route


# Any string field carrying a newline/CR is ALWAYS rejected (the prose-injection
# guard fires before field-specific checks, for every top-level string field).
@given(field=st.sampled_from(["route_id", "task_board", "created_at", "created_by",
                              "join_condition", "next_trigger"]),
       nl=st.sampled_from(["\n", "\r", "\r\n"]),
       pre=_benign_text, post=_benign_text)
def test_newline_in_any_string_field_always_rejected(field, nl, pre, post):
    route = tr._route()
    route[field] = pre + nl + post
    issues = route_manifest.validate_route_object(route)
    assert any("control characters rejected" in i for i in issues), issues


# ... and the same holds for every nested side_effect_token string field.
@given(field=st.sampled_from(list(route_manifest.SIDE_EFFECT_TOKEN_FIELDS)),
       nl=st.sampled_from(["\n", "\r"]),
       pre=_benign_text, post=_benign_text)
def test_newline_in_nested_token_field_always_rejected(field, nl, pre, post):
    token = tr._token()
    token[field] = pre + nl + post
    route = tr._route(side_effect_token=token)
    issues = route_manifest.validate_route_object(route)
    assert any("control characters rejected" in i for i in issues), issues


# ---- DEEP validation is exercised, fail-closed (non-vacuity) ----
# The arbitrary-dict properties above only ever reach the early "unsupported
# schema" return (the bounded `_arb` strategy can never spell the schema
# constant), so they never touch the deep field checks. These properties start
# from the KNOWN-VALID baseline and corrupt exactly one field to an invalid
# value that trips a DEEP (post-schema, post-missing) check: each corruption
# MUST yield a non-empty issues list. This is the property a validator mutated
# to "accept every schema-correct object" fails.
#
# Each pair corrupts a distinct deep branch of validate_route_object:
_ROUTE_DEEP_CORRUPTIONS = [
    ("created_by", "intern"),      # not a known seat
    ("generation", 0),             # integer < 1
    ("wave", "two"),               # not an integer
    ("packet_refs", []),           # empty (must be non-empty unique list)
    ("next_trigger", "none"),      # weak trigger (not authority)
    ("task_board", ""),            # empty string
]


def test_route_baseline_is_valid_positive_control():
    # Positive control: the UNcorrupted baseline validates clean, so the
    # corruption properties below are meaningful (only the corruption fails it).
    assert route_manifest.validate_route_object(tr._route()) == []


@given(pair=st.sampled_from(_ROUTE_DEEP_CORRUPTIONS))
def test_corrupted_route_field_reaches_deep_validation_fail_closed(pair):
    field, bad = pair
    route = tr._route()
    route[field] = copy.deepcopy(bad)
    snap = copy.deepcopy(route)
    issues = route_manifest.validate_route_object(route)
    assert issues, f"deep check did not fire for corrupted {field}={bad!r}"
    assert route == snap  # deep validation must not mutate the input


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
