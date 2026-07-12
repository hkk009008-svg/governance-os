# Capability Security Fixes — Slice 7 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development. Steps use checkbox (`- [ ]`) syntax.

**Goal:** Fix the confirmed authority/robustness defects in the shipped `scripts/route_capability.py` that the independent design-time coverage enumeration (R-INDEPENDENCE, ADR-019) surfaced — with a property/regression test proving each defect on the current code first (RED), then the fix (GREEN), then cross-model verification.

**Architecture:** Test-first fixes, all in `scripts/route_capability.py` + `tests/unit/`. Each defect gets a regression + property test that fails on today's code and passes after the fix. The hard piece — enforcing that a consumed command acts only on the capability's authorized `target` — follows an **independent Codex design** (`.superpowers/sdd/codex-target-design-output.md`) rather than an improvised security rule, per R-INDEPENDENCE. Cross-model (Codex) Lane-V verification closes the slice.

## Provenance — dogfooding R-INDEPENDENCE (ADR-019)

The design-time independent enumeration (Codex, `.superpowers/sdd/codex-coverage-enum-output.md`) flagged these as "Current likelihood: Fails"; direct probes **confirmed** each against the shipped, Codex-GO'd (3-round) capability code. These are the exact "computable-but-not-enforced" and "not-total" classes the 2026-07-12 retrospective identified — recurred, unfixed, because earlier fixes targeted the instance (command-class, target_binding) not the class.

Confirmed defects (severity):
- **CRITICAL — target not enforced:** `consume` checks the command *class* but not the *target*; a capability for `target: origin/main` accepts evidence `git push attacker/main`.
- **HIGH — terminal-state / expiry not enforced:** `consume` accepts any schema-valid `state`, including `revoked`/`expired`/`failed`, and never consults `expires_on`.
- **Robustness — `consume` not total:** malformed evidence (missing `result`/`output`, or a non-mapping) raises `KeyError`/`AttributeError` instead of a typed refusal.
- **MED — `logs_ref` path traversal:** `validate_receipt` accepts `logs/../../etc/passwd`.
- **LOW-MED — bool/int confusion:** `capability_is_current` treats a generation of `True` as `1`.

## Global Constraints

- Python ≥3.11; no new dependencies. All changes in `scripts/route_capability.py` + `tests/unit/`. Do NOT touch `scripts/protocol_capacity.py`, `coordination/`, `AGENTS.md` (peer-lane WIP), or any other module.
- **Fail-closed before any filesystem write:** every new refusal in `consume` must return a `ConsumeResult(ok=False, ...)` and write NOTHING (assert store unchanged in tests).
- **Preserve existing behavior:** all current `route_capability` tests must still pass; the fixes only ADD refusals for the confirmed-bad inputs and totality for malformed ones — a legitimate consume (valid capability, `issued`/`activated` state, command matching class AND target, well-formed evidence) still succeeds.
- Hot shared tree: `env -u GIT_INDEX_FILE` on every git command; explicit pathspecs; before each commit `git log --oneline -5` and proceed only if new commits miss your files. Commit bodies: `User-principal directed immediate execution 2026-07-12 (all seats stale).` + `Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>`. NO push.
- R-EVIDENCE: cite the producing command. `DECISIONS.md` append-only (an ADR-020 for the authority-semantics change is Task 4).

---

### Task 1: regression + property tests that CONFIRM each defect (RED)

**Files:** Create `tests/unit/test_capability_security.py`.

- [ ] **Step 1: Write tests that FAIL on the current code**, one group per defect, each with the confirming case + a property over the input class (from Codex's enumerated invariants). Reuse `_cap` from `test_route_capability`. Run them and record that they FAIL against HEAD (the confirmation). Groups:
  - **Target enforcement:** a capability `target="origin/main"`, `allowed_command_class="git push"`, consumed with `command="git push attacker/main"` → MUST be refused, no receipt. Plus a property over generated wrong-target commands (per the Codex target-design accept/reject cases). Positive control: `command="git push origin main"` → accepted.
  - **Lifecycle/state:** `consume` of a capability with `state` in `{"consumed","revoked","expired","failed"}` → refused, no receipt; `state in {"issued","activated"}` with an otherwise-valid consume → succeeds. Property over all six states.
  - **Evidence totality:** `consume(cap, evidence, ...)` for `evidence` in `{{}, {"command":"git push"}, [], None, {"result":1,"command":2,"output":3}, {…extra unicode…}}` → always returns a `ConsumeResult` (never raises), `ok=False`, store unchanged. Property over arbitrary mappings/non-mappings.
  - **logs_ref confinement:** `validate_receipt`/`consume` with `logs_ref` in `{"logs/../x", "logs/../../etc/passwd", "/etc/passwd", "logs//x", "logs/a/../../b"}` → refused; `logs/real/artifact.json` → accepted. Property over generated traversal forms.
  - **bool/int currency:** `capability_is_current(cap bound_generation=1, LineageRoute gen=True)` → `False` (not `True`); and a cap with `bound_generation=True` is never current. Property over bool/int/None generation pairs.
- [ ] **Step 2: Run** `env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_capability_security.py -q` — expect FAILURES (these confirm the defects). Record the exact failures in the report. **Do not commit yet** (a red test file on HEAD would break CI) — OR commit with every test `@pytest.mark.xfail(strict=True, reason="confirms defect; un-xfail in Task 2/3")` so the RED state is captured green-in-CI, then flip to real assertions per-fix in the fix tasks. Choose the xfail-capture approach so CI stays green between tasks.

---

### Task 2: fix the four clear-cut defects (lifecycle, totality, logs_ref, bool/int)

**Files:** Modify `scripts/route_capability.py`; modify `tests/unit/test_capability_security.py` (un-xfail the four groups).

- [ ] **Lifecycle/state (HIGH):** in `consume`, after `validate_capability`, add a check: `capability["state"]` must be in a `CONSUMABLE_STATES = frozenset({"issued","activated"})`; else `ConsumeResult(ok=False, reason=f"not_consumable_state: {state}", receipt_path=None)` — before any write. (Dynamic `expires_on` enforcement needs a packet-completion signal `consume` does not have; add a one-line docstring note that `expires_on` requires a packet-state input and is deferred — the terminal `expired` state IS refused here.)
- [ ] **Evidence totality (robustness):** add `_validate_evidence(evidence) -> list[str]` that checks `evidence` is a dict with `result` (a str), `command` (a str), `output` (a str), optional `commit`/`logs_ref` (str) — returning issues, never raising. Call it first in `consume`; on issues return `ConsumeResult(ok=False, reason="malformed evidence: "+…, receipt_path=None)`. Replace the raw `evidence["…"]` accesses so `consume` is TOTAL (add a property test: `consume` over `hypothesis` arbitrary objects never raises).
- [ ] **logs_ref confinement (MED):** in `validate_receipt`, when `logs_ref` is present, reject it unless it is a relative path with NO `..` component and no leading `/`, that lexically stays under `logs/` (reuse the confinement idiom from `scripts/route_compat.py:_confine` — a pure lexical check, no filesystem access). Reason: `"logs_ref escapes logs/: …"`.
- [ ] **bool/int currency (LOW-MED):** in `capability_is_current`, require `type(capability["bound_generation"]) is int` AND `type(authoritative.lineage.generation) is int` (reject `bool`) before the equality; a bool generation on either side → `False`.
- [ ] Un-xfail the four groups; run `env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit -q` — the four groups pass, all prior tests still pass, no NEW failures. Commit `-- scripts/route_capability.py tests/unit/test_capability_security.py`.

---

### Task 3: fix target enforcement (CRITICAL) — conservative rule, cross-model verified

**Files:** Modify `scripts/route_capability.py`; modify `tests/unit/test_capability_security.py` (un-xfail the target group).

**Design provenance:** The independent Codex *design-generation* run was cut off before producing a rule (its recurring flakiness). Per R-INDEPENDENCE the independent guarantee is preserved by moving the independent check to *verification* (Task 4's Codex Lane-V, where Codex is reliable). The author-proposed rule below is deliberately STRICT/fail-closed; the Codex verify pass is instructed to attack it.

**The rule — the evidence command must act on EXACTLY the capability's target, nothing more.** Add a helper:

```python
def _command_targets_match(command: str, allowed_command_class: str, target: str) -> bool:
    """True iff the command, after its command-class prefix, references EXACTLY
    the capability's target (and only that) — the non-flag argument components,
    split on whitespace and '/', must equal the target's components in order.
    Fail-closed: an empty target, extra refs, a different ref, or no target all
    return False."""
    rest = command[len(allowed_command_class):].strip()  # class prefix already verified
    non_flag = [tok for tok in rest.split() if not tok.startswith("-")]
    cmd_components: list[str] = []
    for tok in non_flag:
        cmd_components.extend(p for p in tok.replace("/", " ").split() if p)
    target_components = [p for p in target.replace("/", " ").split() if p]
    return bool(target_components) and cmd_components == target_components
```

In `consume`, AFTER the command-class check and lifecycle check, BEFORE any write:
`if not _command_targets_match(cmd, allowed, capability["target"]): return ConsumeResult(ok=False, reason=f"target_mismatch: evidence command does not act on the authorized target {capability['target']!r}", receipt_path=None)`.

- [ ] **Step 1:** implement the helper + the consume check. Verify by hand: `git push origin main` (target `origin/main`) → accept; `git push origin main --force-with-lease` → accept; `git push origin/main` → accept; `git push attacker/main` → reject; `git push origin evil` → reject; `git push origin main attacker` → reject (extra ref); `git push` alone → reject.
- [ ] **Step 2:** un-xfail the target group with those accept/reject cases + a property over generated wrong-target commands. Run the suite; confirm the CRITICAL escape is closed and legitimate consumes still succeed. Commit `-- scripts/route_capability.py tests/unit/test_capability_security.py`.

---

### Task 4: ADR-020 + final gates

- [ ] **Step 1:** Append **ADR-020** to `DECISIONS.md` recording the authority-semantics change (consume now enforces target, consumable-state, evidence totality, logs_ref confinement, int-only generations), citing the R-INDEPENDENCE enumeration as origin and that these were confirmed in shipped code. (Authority-semantics change → ADR required.)
- [ ] **Step 2: Final gates (paste into the commit body — R-EVIDENCE):** full `pytest tests/unit -q`; `ci_smoke.py`; a direct re-probe of the five confirmed cases showing each now refused/total. Commit `-- DECISIONS.md`.
- [ ] **Step 3:** Controller dispatches Codex Lane-V (cross-model, per R-INDEPENDENCE) over the slice. NO push.

---

## Acceptance criteria

1. A capability's command acts only on its authorized target — a wrong-target command is refused with no receipt (the CRITICAL escape closed), legitimate target commands still succeed.
2. A capability in a terminal/non-consumable state (`consumed`/`revoked`/`expired`/`failed`) cannot be consumed.
3. `consume` is total — arbitrary/malformed evidence yields a typed `ConsumeResult` refusal, never an exception, and writes nothing.
4. `validate_receipt` rejects a `logs_ref` that escapes `logs/`.
5. `capability_is_current` treats a boolean generation as not-current (int-only equality).
6. All prior `route_capability` tests still pass; every fix has a regression test that fails on the pre-fix code (proven via the RED capture).
7. Cross-model (Codex) verification confirms the fixes and finds no new escape.

## Rollback

Fixes + tests in one module + one ADR. Revert the slice's commits.
