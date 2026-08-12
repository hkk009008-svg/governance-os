# Kernel Property/Stateful Testing — Slice 5 (P1.4) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax.

**Goal:** Harden the four governance-kernel validators built this session (route/v1, route lineage, capabilities, packet-state — ADR-014..017) by driving them with Hypothesis property and stateful tests, so invariants (no-crash, fail-closed, determinism, no-mutation, vocabulary-membership, round-trips, one-time consumption) hold under generated inputs rather than only hand-picked examples.

**Architecture:** A dev-only dependency (`hypothesis`) is added to `requirements-dev.txt` (the governance *runtime* stays exactly two deps — `requirements-governance.txt` is untouched). New `tests/unit/test_kernel_properties.py` holds stateless property tests over each validator; new `tests/unit/test_capability_stateful.py` holds a `RuleBasedStateMachine` over capability consumption (the richest state: issue → consume → replay) asserting the one-time invariant across random operation sequences. Hypothesis runs under a **derandomized, fixed-seed profile** so CI is reproducible. This is test-only: no production module changes, except a same-session fix if a property surfaces a real defect in one of the four validators (all owned/authored this session; none is the contended live `protocol_capacity.py`). Any confirmed defect not fixed this session ships a `pytest.mark.xfail(strict=True, reason=...)` pin (R-VERIFY-TIER).

**Tech Stack:** Python ≥3.11 + `hypothesis>=6` (dev/CI only) + pytest. Exercises `scripts/route_manifest.py`, `scripts/route_lineage.py`, `scripts/route_capability.py`, `scripts/packet_state.py`.

## Provenance

Implements roadmap **Slice P1.4** of the 2026-07-11 governance-brief audit (verdict: agree_with_modifications). The audit sequenced P1.4 *after* P0.2/P0.3/P0.4 because "most model actions have no implementation today" — those are now done (Slices route/v1, lineage, capabilities, packet-state, all Codex-verified). Adopted modifications:
- Add `hypothesis` to `requirements-dev.txt` **only**; the runtime stays minimal (ADR-004 context). Record in an ADR.
- Run **derandomized/seeded** in CI for reproducibility (R-MEASURE).
- Property tests over a real validator that surface a defect must ship a strict `xfail` pin the same session (R-VERIFY-TIER-B) rather than leave CI red.
- **Scope to the four session-owned validators**, NOT the contended live `protocol_capacity.py` route/packet validator (the workbook-refresh campaign is mid-pivot; do not touch it). Exercising my own new modules keeps every finding fixable in-lane.

## Global Constraints

- Python ≥3.11; no 3.12+/3.13-only syntax (ADR-004). `hypothesis` goes in `requirements-dev.txt` only; `requirements-governance.txt` stays exactly `cryptography>=42.0` + `rfc8785>=0.1.2`.
- **No production logic change** except a same-session fix to one of the four owned validators if a property surfaces a real defect; the contended live `scripts/protocol_capacity.py` and everything under `coordination/` are NOT touched.
- **Hot shared tree:** a concurrent director2/codex lane is committing to `main` every few seconds. Prefer NEW files. Subagents prefix EVERY git command with `env -u GIT_INDEX_FILE`; explicit pathspecs only; never bare `git commit`/`git add -A`. Immediately before each commit run `env -u GIT_INDEX_FILE git log --oneline -5`; if new commits touch NONE of your task's files, proceed and note the new HEAD; else report BLOCKED. Do NOT edit `conftest.py` (shared) — register the Hypothesis profile inside the new test modules.
- Every commit body includes `User-principal directed immediate execution 2026-07-12 (all seats stale).` and ends with `Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>`. NO push (user-gated).
- `DECISIONS.md` is append-only. Tests import bare; `pyproject.toml` sets `pythonpath = [".", "scripts"]`.
- All factual claims in commit bodies cite the producing command (R-EVIDENCE).

---

### Task 1: ADR-018 + hypothesis dev dependency

**Files:** Modify `DECISIONS.md` (append after ADR-017); modify `requirements-dev.txt`.

- [ ] **Step 1: Add hypothesis to `requirements-dev.txt`** — append a line after `pytest>=8.0`:

```
hypothesis>=6
```

- [ ] **Step 2: Append ADR-018 to DECISIONS.md:**

```markdown
## ADR-018: Property + stateful testing of the kernel validators (hypothesis, dev-only)

**Status:** Accepted

**Context:**
The Slices ADR-014..017 validators (route/v1, lineage, capabilities,
packet-state) are covered by example-based unit tests. Interaction and
edge-case failures (the class an independent Codex pass repeatedly surfaced
on the capability slice) are better caught by generated inputs. The audit
sequenced this after ADR-016/017, which are now complete.

**Decision:**
Add `hypothesis>=6` to `requirements-dev.txt` ONLY — the governance runtime
stays two dependencies (`requirements-governance.txt` unchanged, ADR-004
context). Add property tests driving the four session-owned validators
(no-crash, fail-closed, determinism, no-mutation, vocabulary-membership,
round-trips) and a `RuleBasedStateMachine` over capability consumption (the
one-time invariant). Hypothesis runs under a fixed-seed/derandomized profile
so CI is reproducible (R-MEASURE). Scope excludes the contended live
`protocol_capacity.py` validator (campaign mid-pivot); a property that
surfaces a real defect in an owned validator is fixed the same session or
pinned strict-xfail (R-VERIFY-TIER-B).

**Consequences:**
- The kernel validators gain generated-input coverage; regressions and edge
  cases are caught in CI, not post-hoc.
- Dev/CI installs one more package; runtime install is unchanged.
- Non-determinism is avoided via the seeded profile; failures reproduce.
```

- [ ] **Step 3: Commit** (Rule #7 pre-check first): `env -u GIT_INDEX_FILE git commit -m "docs(adr): ADR-018 property/stateful testing of kernel validators (hypothesis dev-only)

User-principal directed immediate execution 2026-07-12 (all seats stale).

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>" -- DECISIONS.md requirements-dev.txt`

---

### Task 2: stateless property tests over the four validators

**Files:** Create `tests/unit/test_kernel_properties.py`.

**Interfaces consumed:** `route_manifest.{validate_route_object, route_hash, canonical_route_bytes, render_markdown, read_manifest, write_route_pair}`; `route_lineage.{RouteLineage, LineageRoute, resolve_authoritative, check_cas, parse_lineage}`; `route_capability.{validate_capability, capability_hash}`; `packet_state.{derive_work_state, derive_verification_state, WORK_STATES, VERIFICATION_STATES, is_valid_work_transition, WORK_TRANSITIONS}`.

- [ ] **Step 1: Write the property tests.** Register a deterministic profile at module top and use it, then assert the invariants. Skeleton (fill every strategy/assert; the reusable builders from `test_route_manifest.py` / `test_route_capability.py` may be imported for valid baselines):

```python
"""Property + fuzz tests over the ADR-014..017 kernel validators (ADR-018).

Invariants under generated inputs: validators never crash (they return issues
or raise only their own typed errors), fail closed, are deterministic and
non-mutating, and produce only vocabulary values.
"""
from __future__ import annotations

import copy

from hypothesis import given, settings, HealthCheck, strategies as st
from hypothesis import Verbosity

import packet_state
import route_capability
import route_lineage
import route_manifest

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


# A generated VALID route (built from the known-good baseline with fuzzed benign fields)
# round-trips render -> read_manifest and hashes deterministically. (Import _route from
# test_route_manifest and override only safe fields; assert route_hash is order-independent.)


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


# check_cas is always fail-closed unless parent==tip AND gen==tip+1 (property over random pairs).


# ---- route_capability.validate_capability ----
@given(st.dictionaries(st.text(max_size=10), _arb, max_size=12))
def test_validate_capability_never_crashes_and_no_mutation(obj):
    snap = copy.deepcopy(obj)
    issues = route_capability.validate_capability(obj)
    assert isinstance(issues, list)
    assert obj == snap


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
```

- [ ] **Step 2: Fill in the elided properties** (route/v1 round-trip + hash-order-independence; `check_cas` fail-closed property). **Run:** `env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_kernel_properties.py -q`. If a property FAILS, Hypothesis prints a minimal counterexample — that is a real finding: (a) if it's a defect in an owned validator, fix the validator module (commit the fix with the test) and record the counterexample in the report; (b) if the behavior is actually correct and the property was wrong, fix the property. Never weaken a property to hide a real defect.

- [ ] **Step 3: Commit** `-- tests/unit/test_kernel_properties.py` (plus any owned-validator fix file if a real defect was found — name it explicitly in the pathspec and the commit body with the counterexample).

---

### Task 3: stateful capability-consumption machine + final gates

**Files:** Create `tests/unit/test_capability_stateful.py`.

**Interface consumed:** `route_capability.{consume, ConsumeResult}` and the valid-capability builder (import `_cap` from `test_route_capability`).

- [ ] **Step 1: Write a `RuleBasedStateMachine`** modeling capability consumption against a temp store, asserting the one-time invariant across random operation interleavings:

```python
"""Stateful property test: capability consumption is one-time (ADR-018)."""
from __future__ import annotations

import tempfile
from pathlib import Path

from hypothesis import settings, HealthCheck
from hypothesis.stateful import RuleBasedStateMachine, rule, invariant, initialize
from hypothesis import strategies as st

import route_capability
from test_route_capability import _cap


class CapabilityConsumeMachine(RuleBasedStateMachine):
    def __init__(self):
        super().__init__()
        self._tmp = tempfile.TemporaryDirectory()
        self.store = Path(self._tmp.name)
        self.consumed: set[str] = set()  # capability_ids we've successfully consumed

    @rule(cid=st.text(alphabet="abcdef0123456789", min_size=1, max_size=6))
    def consume_capability(self, cid):
        cap = _cap(capability_id=f"cap-{cid}")
        evidence = {"result": "ok", "command": "git push", "output": "done", "commit": "deadbee"}
        res = route_capability.consume(cap, evidence, store_dir=self.store)
        key = cap["capability_id"]
        if key in self.consumed:
            # a replay must always be refused as already_consumed
            assert not res.ok and res.reason == "already_consumed"
        else:
            assert res.ok and res.reason == "consumed"
            self.consumed.add(key)

    @invariant()
    def one_receipt_per_consumed_capability(self):
        for key in self.consumed:
            assert (self.store / f"{key}.receipt.json").exists()

    def teardown(self):
        self._tmp.cleanup()


CapabilityConsumeMachine.TestCase.settings = settings(
    derandomize=True, max_examples=100, deadline=None,
    stateful_step_count=30, suppress_health_check=[HealthCheck.too_slow])
TestCapabilityConsume = CapabilityConsumeMachine.TestCase
```

- [ ] **Step 2: Run:** `env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_capability_stateful.py -q`. A failure is a real one-time-consumption violation — fix `route_capability.consume` (owned) and record the minimal trace. **Commit** `-- tests/unit/test_capability_stateful.py`.

- [ ] **Step 3: Final gates (paste outputs into the commit body — R-EVIDENCE):**

```
env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit -q
env -u GIT_INDEX_FILE .venv/bin/python scripts/ci_smoke.py
env -u GIT_INDEX_FILE git diff HEAD --stat
```

Expect: suite green (prior total + the new property/stateful tests, 0 failures, the pre-existing xfail unchanged plus any strict-xfail pins added for confirmed unfixed defects); smoke OK; diff-stat shows only this slice's files. Independent verification (Codex Lane-V) is dispatched by the controller after this task; NO push regardless.

---

## Acceptance criteria (P1.4, from the brief as modified by the audit)

1. Each of the four validators is exercised by generated inputs and never crashes (returns typed issues / raises only its own typed errors).
2. Fail-closed and no-mutation properties hold under fuzzing (validate_* never mutates input; refusals write nothing).
3. Resolution is order-independent and derivations are vocabulary-bounded under generated inputs.
4. The one-time consumption invariant holds across random operation interleavings (stateful machine): a replay is always `already_consumed`; exactly one receipt per consumed capability.
5. Hypothesis runs derandomized/seeded so CI is reproducible; `hypothesis` is a dev-only dependency (runtime unchanged).
6. Any property that surfaces a real defect in an owned validator is fixed the same session (with the counterexample recorded) or pinned `xfail(strict=True)`.

## Rollback

Test files + one dev-dependency line + one append-only ADR (and any owned-validator fix, which is itself an improvement). Revert the slice's commits; the runtime is unchanged.
