"""Confirmed authority/robustness defects in route_capability (R-INDEPENDENCE, ADR-019).

Each group has: the exact confirming case (the escape the design-time coverage
enumeration flagged and a direct probe confirmed against the shipped code), a
positive control (a fully-legitimate operation still succeeds), and a small
property over the input class. The five defects:

  1. CRITICAL  target not enforced   — a cap for target "origin/main" accepted
     evidence command "git push attacker/main".
  2. HIGH      terminal state        — consume accepted state "revoked"/"expired".
  3. Robustness consume not total    — malformed evidence raised KeyError/AttributeError.
  4. MED       logs_ref traversal    — validate_receipt accepted "logs/../../etc/passwd".
  5. LOW-MED   bool/int currency     — capability_is_current treated True as 1.
"""
from __future__ import annotations

import tempfile
from pathlib import Path

import pytest
from hypothesis import given, settings, strategies as st

import route_capability
import route_lineage
from test_route_capability import _cap


def _evidence(**overrides) -> dict:
    """Well-formed evidence whose command acts on the default cap target origin/main."""
    ev = {
        "result": "ok",
        "command": "git push origin main",
        "output": "To origin/main",
        "commit": "deadbee",
    }
    ev.update(overrides)
    return ev


def _lr(route_id, generation):
    return route_lineage.LineageRoute(
        route_id, route_lineage.RouteLineage(generation, None, None)
    )


# --- Defect 1: CRITICAL — the command must act on the authorized target -------


def test_target_wrong_ref_refused_no_receipt(tmp_path):
    # cap target "origin/main"; a command pushing "attacker/main" is the CRITICAL
    # escape: same command class, DIFFERENT target -> must be refused, no receipt.
    ev = _evidence(command="git push attacker/main")
    res = route_capability.consume(_cap(), ev, store_dir=tmp_path)
    assert not res.ok
    assert "target_mismatch" in res.reason
    assert list(tmp_path.iterdir()) == []  # fail-closed BEFORE any write


def test_target_extra_ref_refused(tmp_path):
    ev = _evidence(command="git push origin main attacker")
    res = route_capability.consume(_cap(), ev, store_dir=tmp_path)
    assert not res.ok and "target_mismatch" in res.reason
    assert list(tmp_path.iterdir()) == []


def test_target_bare_class_refused(tmp_path):
    # "git push" alone references NO target -> fail-closed.
    ev = _evidence(command="git push")
    res = route_capability.consume(_cap(), ev, store_dir=tmp_path)
    assert not res.ok and "target_mismatch" in res.reason
    assert list(tmp_path.iterdir()) == []


def test_target_match_slash_or_space_accepted(tmp_path):
    # Positive control: the legitimate target command consumes.
    res = route_capability.consume(_cap(), _evidence(command="git push origin main"), store_dir=tmp_path)
    assert res.ok and res.reason == "consumed"


def test_target_match_slash_form_accepted(tmp_path):
    res = route_capability.consume(_cap(), _evidence(command="git push origin/main"), store_dir=tmp_path)
    assert res.ok and res.reason == "consumed"


def test_target_match_no_flags_plain_command_accepted(tmp_path):
    # Plain `<class> <target>` with no flags and no exotic whitespace consumes.
    # (Flag-bearing commands are now REFUSED — see the slice-7 hardening battery
    # test_flag_and_unicode_target_bypasses_all_refused below.)
    res = route_capability.consume(
        _cap(), _evidence(command="git push origin main"), store_dir=tmp_path
    )
    assert res.ok and res.reason == "consumed"


@settings(max_examples=60, deadline=None)
@given(ref=st.text(alphabet="abcdefghijklmnopqrstuvwxyz", min_size=1, max_size=8))
def test_property_wrong_single_ref_always_refused(ref):
    # Any single lowercase ref that is not exactly "origin"+"main" cannot match the
    # two-component target "origin/main" -> consume MUST refuse, writing nothing.
    if ref in ("origin", "main"):
        return
    with tempfile.TemporaryDirectory() as d:
        store = Path(d)
        ev = _evidence(command=f"git push {ref}")
        res = route_capability.consume(_cap(), ev, store_dir=store)
        assert not res.ok and "target_mismatch" in res.reason
        assert list(store.iterdir()) == []


# --- Slice-7 hardening battery: _command_targets_match is fail-closed ---------
#
# An adversarial battery found the pre-hardening target check accepted dangerous
# commands for a cap authorizing exactly `git push origin/main`. Two families:
#
#   (A) FLAG bypasses — the old rule stripped ALL `-` tokens, so any option rode
#       through. --receive-pack / --exec run an attacker program on the REMOTE (a
#       git RCE vector); --repo overrides the remote to an attacker's; --force /
#       --force-with-lease violate the token non_goals ("no force-push");
#       --push-option was blindly accepted. A capability authorizes its class
#       acting on its target — NO options — so every flag-bearing command refuses.
#
#   (B) UNICODE-whitespace parsing differential — Python str.split() treats NBSP
#       (U+00A0), line/para separators (U+2028/U+2029) and em-space (U+2003) as
#       separators, so the old rule saw [origin, main] and matched; a POSIX shell
#       does NOT split on them, so git would receive ONE bogus argument. Only
#       ASCII space/tab are real arg separators — any other whitespace refuses.
#
# Every command below must refuse fail-closed (ok=False, target_mismatch, and
# NOTHING written), and the two legit forms must still consume.

_BYPASS_COMMANDS_MUST_REFUSE = [
    # (A) flag bypasses — the confirmed escapes plus adjacent force-flags.
    "git push --receive-pack=evil origin main",   # runs a program on the remote
    "git push --exec=evil origin main",           # runs a program on the remote
    "git push --repo=attacker/main origin main",  # attacker-controlled remote override
    "git push --push-option=x origin main",       # any flag was blindly accepted
    "git push --force origin main",               # violates non_goals (no force-push)
    "git push origin main --force-with-lease",    # trailing force flag
    # (B) unicode-whitespace differential — Python splits these, a shell does not.
    "git push origin\u00a0main",                  # NBSP U+00A0
    "git push origin\u2028main",                  # LINE SEPARATOR
    "git push origin\u2029main",                  # PARAGRAPH SEPARATOR
    "git push origin\u2003main",                  # EM SPACE U+2003
    # already-refused controls (regression-lock the pre-existing target checks).
    "git push attacker/main",                     # different remote
    "git push origin evil",                       # different ref
    "git push origin main attacker",              # extra ref
    "git push",                                   # bare class, no target
    "git push origin main:attacker",              # refspec renaming the remote ref
    "git push +main/HEAD:main",                   # force-refspec form
    "git push https://evil/x main",               # url-form remote override
]


@pytest.mark.parametrize("command", _BYPASS_COMMANDS_MUST_REFUSE)
def test_flag_and_unicode_target_bypasses_all_refused(tmp_path, command):
    # Cap authorizes exactly `git push` on `origin/main`. Every command here is a
    # confirmed bypass or an already-refused control — all must refuse with NO
    # receipt written (fail-closed BEFORE any write).
    res = route_capability.consume(_cap(), _evidence(command=command), store_dir=tmp_path)
    assert not res.ok, f"BYPASS: {command!r} was accepted"
    assert "target_mismatch" in res.reason, (command, res.reason)
    assert list(tmp_path.iterdir()) == []  # nothing written on a refused command


_LEGIT_COMMANDS_MUST_CONSUME = [
    "git push origin main",   # space-separated target
    "git push origin/main",   # slash form of the same target
]


@pytest.mark.parametrize("command", _LEGIT_COMMANDS_MUST_CONSUME)
def test_legit_target_commands_still_consume(tmp_path, command):
    # The hardening must not break the authorized operation: the exact target,
    # in either the space or slash form, still consumes with a receipt.
    res = route_capability.consume(_cap(), _evidence(command=command), store_dir=tmp_path)
    assert res.ok and res.reason == "consumed", (command, res.reason)
    assert list(tmp_path.iterdir()) != []  # a receipt was written


# --- Defect 2: HIGH — a non-consumable (terminal) state cannot be consumed ----


@pytest.mark.parametrize("state", ["consumed", "revoked", "expired", "failed"])
def test_terminal_state_refused_no_receipt(tmp_path, state):
    res = route_capability.consume(_cap(state=state), _evidence(), store_dir=tmp_path)
    assert not res.ok
    assert "not_consumable_state" in res.reason
    assert list(tmp_path.iterdir()) == []


@pytest.mark.parametrize("state", ["issued", "activated"])
def test_consumable_state_succeeds(tmp_path, state):
    res = route_capability.consume(_cap(state=state), _evidence(), store_dir=tmp_path)
    assert res.ok and res.reason == "consumed"


@pytest.mark.parametrize("state", list(route_capability.LIFECYCLE_STATES))
def test_property_state_consumable_iff_issued_or_activated(tmp_path, state):
    res = route_capability.consume(_cap(state=state), _evidence(), store_dir=tmp_path)
    assert res.ok == (state in route_capability.CONSUMABLE_STATES)


# --- Defect 3: Robustness — consume is TOTAL (never raises) -------------------

_MALFORMED_EVIDENCE = [
    {},
    {"command": "git push origin main"},
    [],
    None,
    "not a mapping",
    123,
    {"result": 1, "command": 2, "output": 3},
    # unicode content that is a valid str but fails the downstream result enum:
    {"result": "완료", "command": "git push origin main", "output": "유니코드", "commit": "deadbee"},
]


@pytest.mark.parametrize("evidence", _MALFORMED_EVIDENCE)
def test_malformed_evidence_returns_result_never_raises(tmp_path, evidence):
    res = route_capability.consume(_cap(), evidence, store_dir=tmp_path)
    assert isinstance(res, route_capability.ConsumeResult)
    assert not res.ok
    assert list(tmp_path.iterdir()) == []  # nothing written on malformed input


def test_wellformed_evidence_still_consumes(tmp_path):
    res = route_capability.consume(_cap(), _evidence(), store_dir=tmp_path)
    assert res.ok and res.reason == "consumed"


@settings(max_examples=80, deadline=None)
@given(
    evidence=st.recursive(
        st.none()
        | st.booleans()
        | st.integers()
        | st.text(max_size=20)
        | st.lists(st.text(max_size=8), max_size=4),
        lambda children: st.dictionaries(st.text(max_size=8), children, max_size=5),
        max_leaves=12,
    )
)
def test_property_consume_total_over_arbitrary_evidence(evidence):
    # consume must be TOTAL: any object yields a typed ConsumeResult, never an
    # exception. (Success is possible only for a well-formed dict; the property
    # asserts the no-raise / typed-return invariant over the whole input class.)
    with tempfile.TemporaryDirectory() as d:
        res = route_capability.consume(_cap(), evidence, store_dir=Path(d))
        assert isinstance(res, route_capability.ConsumeResult)


# --- Defect 4: MED — logs_ref must not escape logs/ --------------------------

_TRAVERSING_LOGS_REFS = [
    "logs/../x",
    "logs/../../etc/passwd",
    "/etc/passwd",
    "logs//x",
    "logs/a/../../b",
]


def _receipt_with_logs(logs_ref):
    return {
        "schema": route_capability.RECEIPT_SCHEMA_ID,
        "capability_id": "cap-x",
        "capability_hash": "a" * 64,
        "result": "ok",
        "command": "git push origin main",
        "output": "To origin/main",
        "subject": "director",
        "target": "origin/main",
        "logs_ref": logs_ref,
    }


@pytest.mark.parametrize("logs_ref", _TRAVERSING_LOGS_REFS)
def test_traversing_logs_ref_refused(logs_ref):
    issues = route_capability.validate_receipt(_receipt_with_logs(logs_ref))
    assert any("logs_ref" in i for i in issues), issues


def test_clean_logs_ref_accepted():
    assert route_capability.validate_receipt(_receipt_with_logs("logs/real/artifact.json")) == []


def test_consume_refuses_traversing_logs_ref(tmp_path):
    ev = {"result": "ok", "command": "git push origin main", "output": "done",
          "logs_ref": "logs/../../etc/passwd"}
    res = route_capability.consume(_cap(), ev, store_dir=tmp_path)
    assert not res.ok
    assert list(tmp_path.iterdir()) == []


@settings(max_examples=60, deadline=None)
@given(
    depth=st.integers(min_value=1, max_value=4),
    tail=st.text(alphabet="abcdefghijklmnop", min_size=1, max_size=6),
)
def test_property_dotdot_logs_ref_always_refused(depth, tail):
    logs_ref = "logs/" + "../" * depth + tail
    issues = route_capability.validate_receipt(_receipt_with_logs(logs_ref))
    assert any("logs_ref" in i for i in issues), (logs_ref, issues)


# --- Defect 5: LOW-MED — int-only generation currency (bool is not 1) --------


def test_bool_route_generation_not_current():
    cap = _cap(bound_route_id="r", bound_generation=1)
    assert route_capability.capability_is_current(cap, _lr("r", True)) is False


def test_bool_bound_generation_never_current():
    cap = _cap(bound_route_id="r", bound_generation=True)
    assert route_capability.capability_is_current(cap, _lr("r", 1)) is False


def test_int_generations_compare_correctly():
    cap = _cap(bound_route_id="r5", bound_generation=5)
    assert route_capability.capability_is_current(cap, _lr("r5", 5)) is True
    assert route_capability.capability_is_current(cap, _lr("r5", 6)) is False


@settings(max_examples=80, deadline=None)
@given(
    bound=st.one_of(st.integers(min_value=1, max_value=5), st.booleans(), st.none()),
    route=st.one_of(st.integers(min_value=1, max_value=5), st.booleans(), st.none()),
)
def test_property_currency_requires_int_generations(bound, route):
    cap = {"bound_route_id": "r", "bound_generation": bound}
    result = route_capability.capability_is_current(cap, _lr("r", route))
    expected = type(bound) is int and type(route) is int and bound == route
    assert result is expected
