# Cross-Subsystem + Binding Property Hardening — Slice 6 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax.

**Goal:** Extend the ADR-018 property/stateful test coverage to (a) the one validator not yet fuzzed — `target_binding` (the ADR-013 multi-target resolver) — and (b) the **cross-subsystem** route-lineage ↔ capability interaction, so the revocation-on-supersession invariant (a capability bound to a superseded route generation is no longer current, and `consume` refuses it) is exercised end-to-end across two subsystems, catching interaction failures no single-module test covers.

**Architecture:** Two new test-only files. `tests/unit/test_target_binding_properties.py` fuzzes `target_binding.{load_config, resolve_target, forbidden_roots, list_targets}` over generated config files, asserting they always either return well-formed output or raise the typed `BindingError` — never crash with an untyped exception. `tests/unit/test_lineage_capability_stateful.py` is a `RuleBasedStateMachine` modeling a growing route lineage plus capabilities bound to specific `(route_id, generation)` pairs; it interleaves supersession, issuance, currency checks, and consumption, asserting that `capability_is_current`/`consume(authoritative=tip)` agree exactly with lineage authority. No new ADR (ADR-018 already authorizes "property + stateful testing of the kernel validators"); no production change unless a property surfaces a real defect in an owned module.

**Tech Stack:** Python ≥3.11 + `hypothesis>=6` (already a dev dep, ADR-018) + pytest. Exercises `scripts/target_binding.py`, `scripts/route_lineage.py`, `scripts/route_capability.py`.

## Provenance

Extends ADR-018 (P1.4) — the audit's P1.4 envisioned "protocol-level stateful property testing of complete interleavings ... interaction failures between otherwise valid local components," naming "capability authority vs route supersession" as a target. Slice 5 covered per-validator properties + single-subsystem capability consumption; this slice adds the missing validator (`target_binding`) and the cross-subsystem interaction. No new decision — this executes ADR-018.

## Global Constraints

- Python ≥3.11; no 3.12+/3.13-only syntax (ADR-004). `hypothesis` is already in `requirements-dev.txt`; runtime unchanged.
- **Test-only:** no production module changes except a same-session fix to an OWNED module (`target_binding` / `route_lineage` / `route_capability`) if a property surfaces a real defect; the contended live `scripts/protocol_capacity.py` and `coordination/` are NOT touched. Any confirmed unfixed defect ships a strict `xfail` pin (R-VERIFY-TIER-B).
- **Anti-vacuousness (the Slice-5 lesson):** every property must be non-vacuous — the input strategy must actually REACH the interesting branch, and each test must FAIL if its invariant breaks. For each property, include a positive control (a case that provably reaches the deep/interaction branch) and ensure the stateful model actually generates supersession + stale-capability sequences (not just fresh-tip consumes). Do NOT weaken a property to make it pass.
- **Hot shared tree:** a concurrent lane commits to `main`. NEW files only. Subagents prefix EVERY git command with `env -u GIT_INDEX_FILE`; explicit pathspecs only; never bare `git commit`/`git add -A`. Before each commit run `env -u GIT_INDEX_FILE git log --oneline -5`; if new commits touch NONE of your files, proceed and note the new HEAD; else BLOCKED. Do NOT edit `conftest.py` (shared) — put any Hypothesis profile inside the new test modules. Do NOT edit `DECISIONS.md` (no ADR; avoids collision).
- Every commit body includes `User-principal directed immediate execution 2026-07-12 (all seats stale).` and ends with `Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>`. NO push (user-gated).
- Tests import bare; `pyproject.toml` sets `pythonpath = [".", "scripts"]`. Cite the producing command for factual claims (R-EVIDENCE).

---

### Task 1: property tests over the multi-target binding resolver

**Files:** Create `tests/unit/test_target_binding_properties.py`.

**Interface under test:** `target_binding.{load_config, list_targets, resolve_target, forbidden_roots, BindingError, TargetBinding}`. `BindingError` subclasses `ValueError`. All of `load_config`/`resolve_target`/`forbidden_roots` raise `BindingError` on any malformed input.

**Reference the existing example tests** (`tests/unit/test_target_binding.py`) for the config shape: `[binding].default_target`, `[targets.<name>]` tables with required `repository`+`path` (optional `route_keywords`, `description`), `[paths].forbidden_roots`.

- [ ] **Step 1: Write property tests.** Register a derandomized profile at module top (mirror `test_kernel_properties.py`). Generate config *files* under `tmp_path` from a strategy and assert the total-function invariant. Core properties:

```python
"""Property tests over the ADR-013 multi-target binding resolver (ADR-018 coverage).

Total-function invariant: load_config / resolve_target / forbidden_roots always
either return well-formed output or raise the typed BindingError — never any
other exception, never an uncaught crash.
"""
from __future__ import annotations

from pathlib import Path

from hypothesis import given, settings, HealthCheck, strategies as st

import target_binding

settings.register_profile("ci", settings(derandomize=True, max_examples=200, deadline=None,
                                         suppress_health_check=[HealthCheck.too_slow,
                                                                HealthCheck.function_scoped_fixture]))
settings.load_profile("ci")

_name = st.text(alphabet="abcdefghijklmnopqrstuvwxyz-", min_size=1, max_size=6)
_scalar = st.one_of(st.text(max_size=10), st.integers(), st.booleans())

def _toml_target(name, body: dict) -> str:
    lines = [f"[targets.{name}]"]
    for k, v in body.items():
        lines.append(f'{k} = {v!r}' if not isinstance(v, list) else f'{k} = {v!r}')
    return "\n".join(lines)

# Strategy: build a config file text from fuzzed components — sometimes valid,
# sometimes missing default_target, sometimes a target missing a required key,
# sometimes an unknown key, sometimes non-list forbidden_roots, sometimes junk.
@st.composite
def _config_text(draw):
    parts = []
    if draw(st.booleans()):
        parts.append(f'[binding]\ndefault_target = {draw(_name)!r}')
    names = draw(st.lists(_name, max_size=3, unique=True))
    for n in names:
        body = {}
        if draw(st.booleans()): body["repository"] = draw(st.text(max_size=8))
        if draw(st.booleans()): body["path"] = draw(st.text(max_size=8))
        if draw(st.booleans()): body["route_keywords"] = draw(st.lists(st.text(max_size=5), max_size=3))
        if draw(st.booleans()): body["surprise"] = draw(_scalar)  # unknown key path
        parts.append(_toml_target(n, body))
    if draw(st.booleans()):
        parts.append(f'[paths]\nforbidden_roots = {draw(st.one_of(st.lists(st.text(max_size=6), max_size=3), _scalar))!r}')
    return "\n\n".join(parts)


def _write(root: Path, text: str) -> Path:
    (root / "governance.toml").write_text(text, encoding="utf-8")
    return root


@given(_config_text())
def test_resolve_target_is_total_returns_binding_or_bindingerror(text, tmp_path):
    root = _write(tmp_path, text)
    try:
        binding = target_binding.resolve_target(root, env={})
    except target_binding.BindingError:
        return  # acceptable typed refusal
    # success path: a well-formed binding
    assert isinstance(binding, target_binding.TargetBinding)
    assert isinstance(binding.path, Path)
    assert binding.repository and binding.name


@given(_config_text())
def test_forbidden_roots_is_total(text, tmp_path):
    root = _write(tmp_path, text)
    try:
        roots = target_binding.forbidden_roots(root)
    except target_binding.BindingError:
        return
    assert all(isinstance(p, Path) for p in roots)


def test_positive_control_valid_config_resolves(tmp_path):
    # NON-VACUOUS control: a hand-built VALID config resolves to a TargetBinding.
    (tmp_path / "governance.toml").write_text(
        '[binding]\ndefault_target = "demo"\n\n'
        '[targets.demo]\nrepository = "x/demo"\npath = "~/demo"\nroute_keywords = ["demo"]\n',
        encoding="utf-8")
    b = target_binding.resolve_target(tmp_path, env={})
    assert b.name == "demo" and b.repository == "x/demo"


def test_missing_config_raises_bindingerror(tmp_path):
    import pytest
    with pytest.raises(target_binding.BindingError):
        target_binding.resolve_target(tmp_path / "nonexistent", env={})
```

Note the `HealthCheck.function_scoped_fixture` suppression is needed because `tmp_path` is a function-scoped fixture used with `@given`; verify this is the correct hypothesis idiom (or restructure to build the root inside the test via `tempfile`). If `st.text` can emit characters that make `_toml_text` unparseable in a way that raises something OTHER than BindingError (e.g. the TOML has a syntax that tomllib raises before load_config guards it) — that is FINE only if load_config wraps it as BindingError; if the property catches a raw `tomllib.TOMLDecodeError` escaping, that is a REAL finding (load_config should wrap it) — fix `target_binding.load_config` to catch and wrap, and record it.

- [ ] **Step 2: Run** `env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_target_binding_properties.py -q`. If a property fails by catching a non-BindingError exception escaping the resolver, that is a real total-function defect in an owned module — fix `target_binding` to wrap it as `BindingError` (commit the fix with the test, record the counterexample). If the property is wrong, fix the property. **Prove non-vacuousness:** confirm the positive control reaches the success path and at least some generated configs reach BOTH the success and the BindingError paths (report counts via `--hypothesis-show-statistics`).

- [ ] **Step 3: Commit** `-- tests/unit/test_target_binding_properties.py` (plus `scripts/target_binding.py` only if a real wrap-defect was fixed — name it in the pathspec + commit body with the counterexample).

---

### Task 2: cross-subsystem stateful model — lineage ↔ capability revocation-on-supersession

**Files:** Create `tests/unit/test_lineage_capability_stateful.py`.

**Interfaces under test:** `route_lineage.{RouteLineage, LineageRoute, resolve_authoritative}`; `route_capability.{consume, capability_is_current}`; the valid-capability builder (`_cap` from `test_route_capability`).

**The invariant being hardened (ADR-015 ↔ ADR-016):** a capability is current — and `consume(authoritative=tip)` succeeds — only while its `bound_route_id`/`bound_generation` equal the authoritative lineage tip; once a superseding route makes a newer generation authoritative, the capability is stale (`capability_is_current` False; `consume` refuses `stale_capability`, writing no receipt).

- [ ] **Step 1: Write the state machine.** Model a lineage that grows by supersession, and capabilities bound to specific generations; interleave operations so stale-capability sequences are actually generated (non-vacuous):

```python
"""Cross-subsystem stateful test: capability revocation follows route supersession
(ADR-015 lineage x ADR-016 capabilities; executes ADR-018)."""
from __future__ import annotations

import tempfile
from pathlib import Path

from hypothesis import settings, HealthCheck
from hypothesis.stateful import RuleBasedStateMachine, rule, invariant
from hypothesis import strategies as st

import route_capability
import route_lineage
from test_route_capability import _cap


def _lineage_route(route_id: str, generation: int, parent: str | None) -> route_lineage.LineageRoute:
    return route_lineage.LineageRoute(route_id, route_lineage.RouteLineage(generation, parent, None))


def _evidence():
    return {"result": "ok", "command": "git push", "output": "done", "commit": "deadbee"}


class LineageCapabilityMachine(RuleBasedStateMachine):
    def __init__(self):
        super().__init__()
        self._tmp = tempfile.TemporaryDirectory()
        self.store = Path(self._tmp.name)
        # start with a generation-1 tip
        self.routes = [_lineage_route("route-1", 1, None)]
        self.next_gen = 2
        # capabilities: list of (capability_dict, bound_generation, consumed_bool)
        self.caps: list[dict] = []

    def _tip(self) -> route_lineage.LineageRoute:
        res = route_lineage.resolve_authoritative(self.routes)
        assert res.mode == "lineage" and res.winner is not None
        return next(r for r in self.routes if r.route_id == res.winner)

    @rule()
    def supersede_route(self):
        tip = self._tip()
        rid = f"route-{self.next_gen}"
        self.routes.append(_lineage_route(rid, self.next_gen, tip.route_id))
        self.next_gen += 1

    @rule(at_tip=st.booleans())
    def issue_capability(self, at_tip):
        tip = self._tip()
        # bind either to the current tip (current) or an older generation (stale), if one exists
        gen = tip.lineage.generation
        rid = tip.route_id
        if not at_tip and self.next_gen > 3:
            gen = 1
            rid = "route-1"
        cap = _cap(capability_id=f"cap-{len(self.caps)}", bound_route_id=rid, bound_generation=gen)
        self.caps.append(cap)

    @rule(idx=st.integers(min_value=0, max_value=50))
    def consume_random_capability(self, idx):
        if not self.caps:
            return
        cap = self.caps[idx % len(self.caps)]
        tip = self._tip()
        current = route_capability.capability_is_current(cap, tip)
        res = route_capability.consume(cap, _evidence(), store_dir=self.store, authoritative=tip)
        cid = cap["capability_id"]
        already = (self.store / f"{cid}.receipt.json").exists()
        if not current:
            # stale: must be refused, no receipt created
            assert not res.ok and res.reason.startswith("stale_capability")
            assert not (self.store / f"{cid}.receipt.json").exists()
        elif already:
            assert not res.ok and res.reason == "already_consumed"
        else:
            assert res.ok and res.reason == "consumed"

    @invariant()
    def currency_matches_tip(self):
        tip = self._tip()
        for cap in self.caps:
            expected = (cap["bound_route_id"] == tip.route_id and
                        cap["bound_generation"] == tip.lineage.generation)
            assert route_capability.capability_is_current(cap, tip) == expected

    def teardown(self):
        self._tmp.cleanup()


LineageCapabilityMachine.TestCase.settings = settings(
    derandomize=True, max_examples=100, deadline=None, stateful_step_count=40,
    suppress_health_check=[HealthCheck.too_slow])
TestLineageCapability = LineageCapabilityMachine.TestCase
```

- [ ] **Step 2: Run** `env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_lineage_capability_stateful.py -q`. A failure is a real cross-subsystem invariant violation — fix the owned module and record the minimal trace. **Prove non-vacuousness:** instrument or reason that the model actually generates (a) supersession steps, (b) stale-capability consumes (the `not current` branch), and (c) fresh-tip consumes — report the branch frequencies (a suite where supersede/stale never fire would be vacuous; if so, adjust the rule weighting so stale sequences occur). Also confirm a mutant — e.g. `capability_is_current` returning always-True — would fail the `currency_matches_tip` invariant and the stale-consume assertion.

- [ ] **Step 3: Commit** `-- tests/unit/test_lineage_capability_stateful.py` (plus any owned-module fix, named explicitly with the counterexample).

---

### Task 3: final full-gate verification

- [ ] **Step 1: Final gates (paste outputs into the last commit body — R-EVIDENCE):**

```
env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit -q
env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_target_binding_properties.py tests/unit/test_lineage_capability_stateful.py -q
env -u GIT_INDEX_FILE .venv/bin/python scripts/ci_smoke.py
env -u GIT_INDEX_FILE git diff HEAD --stat
```

Expect: suite green (prior 480 + the new tests, 0 failures, the pre-existing xfail unchanged plus any strict-xfail pins for confirmed unfixed defects); the two new files pass; smoke OK; diff-stat shows only this slice's files. Independent verification (Codex Lane-V) is dispatched by the controller after this task; NO push.

- [ ] **Step 2:** If Tasks 1-2 already committed everything, this task is verification-only (no new commit needed) — record the gate outputs in the report. If a doc note is desired, it is optional and out of scope here.

---

## Acceptance criteria

1. `target_binding` resolution is a total function under fuzzed configs: it returns a well-formed `TargetBinding`/roots or raises `BindingError`, never an uncaught non-typed exception. (Non-vacuous: positive control + both paths reached.)
2. The cross-subsystem invariant holds under interleaved supersession/issuance/consumption: `capability_is_current` and `consume(authoritative=tip)` agree exactly with lineage authority; a stale capability is refused with no receipt.
3. The stateful model actually generates supersession and stale-capability sequences (non-vacuous), and a mutant to `capability_is_current` or `consume` would be caught.
4. Tests are derandomized/seeded (reproducible); no production change except a same-session owned-module fix (with counterexample) if a property surfaces a real defect; any unfixed defect is strict-xfail pinned.
5. No live-campaign file (`protocol_capacity.py`, `coordination/`) touched; no `DECISIONS.md`/`conftest.py` edit.

## Rollback

New test files only (plus any owned-module fix, itself an improvement). Revert the slice's commits; runtime unchanged.
