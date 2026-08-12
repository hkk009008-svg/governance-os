# Consumable Side-Effect Capabilities + Receipts — Slice 3 (P0.4) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax.

**Goal:** Turn side-effect executor tokens into typed **capability objects** that are one-time (atomic consume; a second consume fails `already_consumed`), target-bound, receipt-backed (a consume writes a receipt carrying executed evidence), and revocable-on-supersession (a capability bound to a superseded route generation is invalid) — the "consumable, target-bound, revocable, receipt-backed" property (brief DoD #4), closing the operator2 execution-token BLOCKER's general form ("no script accepts a token at execution time", mailbox `2026-07-10T01-23-27Z`).

**Architecture:** A new stdlib-only module `scripts/route_capability.py` defines `governance.capability/v1` (a strict superset of the existing 10-field side-effect-executor token contract, plus lifecycle + route/generation binding) and `governance.capability-receipt/v1` (evidence-bearing, mirroring `check_go_schema.py`'s non-vacuous-evidence convention). Capabilities are canonicalized + hashed with the repo's single canonicalizer (`threeway.canon.canonicalize`, RFC 8785 — library reuse; the dormant signed bus stays dormant, ADR-010). Consumption is atomic via exclusive-create (`O_EXCL`) of a receipt file keyed by `capability_id`: the first consumer wins, a replay fails `already_consumed`. Revocation-on-supersession reuses Slice-2's lineage resolver — a capability is current only while its `bound_route_id`/`bound_generation` equal the authoritative route's. A `consume` CLI is the mechanical enforcement point a side-effect-performing seat calls before mutating. Everything is new files; **no live-campaign file is touched** (the active workbook-refresh campaign is unaffected).

**Tech Stack:** Python ≥3.11 stdlib + `rfc8785` (existing governance dep, via `threeway.canon`) + pytest. No new dependencies. Consumes Slice-1 route/v1 identity (ADR-014) and Slice-2 lineage (`scripts/route_lineage.py`, ADR-015).

## Provenance

Implements roadmap **Slice 5 (P0.4)** of the 2026-07-11 governance-brief audit. P0.4 verdict was **agree_with_modifications** (none refuted). Sequencing note from the audit: capability↔route binding and revocation-on-supersession "need typed route identity + CAS supersession (P0.3) to bind to" — both now landed (Slices 1+2), so P0.4 is properly unblocked. **Slices 3 (P1.3-lite) and 4 (P0.2) are deliberately deferred**: both modify `scripts/protocol_capacity.py` (the live route validator) and Slice 4 is gated on the workbook-refresh cycle close, which as of this plan is still open (2 active-wip packets). P0.4 touches none of that.

Adopted modifications, bound into this plan:
- capability/v1 is a **superset** of the existing 10-field token contract (`scripts/codex_protocol_model.py:377-388`): keep `allowed_command_class` (exact command literal — the strongest control), `observer_seats`, `final_closeout_owner`, and the stop condition.
- Receipts carry **executed evidence** (command + output + commit SHA or `logs/` artifact ref), mirroring `scripts/check_go_schema.py:49-70`; a bare `state="consumed"` flip is anti-ceremony (§8.6) and is rejected.
- Bind revocation-on-supersession to route identity + generation (Slice 2); until a route explicitly carries a capability forward (`capability_refs`, reserved `[]` in route/v1 v1.0), a superseded-generation capability is invalid.
- **Compatibility:** the existing prose token blocks in routes and the live route-time token lint (`protocol_capacity.py`) are UNCHANGED and stay fail-closed — no cutover of live token authority in this slice. capability/v1 is generated + validated alongside, not yet the live authority.
- Preserve ADR-012's invariant explicitly: **no capability state ever substitutes for the user push gate.** A consumed capability is necessary-not-sufficient; the user still gates the side effect.
- The enforcement point in THIS slice is a standalone `route_capability.py consume` CLI (a script that accepts a token at execution time and refuses replay). Wiring `--executor-token` into `scripts/execute_threeway_cutover.sh` is a follow-up that belongs with the parked signed-bus plan (`docs/superpowers/plans/2026-07-10-signed-bus-authority-identity.md`) and its dormant-bus machinery.

## Global Constraints

- Python ≥3.11 only; no 3.12+/3.13-only syntax (ADR-004). No new dependencies: `requirements-governance.txt` stays `cryptography>=42.0` + `rfc8785>=0.1.2`.
- The canonical serializer is `threeway.canon.canonicalize` (RFC 8785). Do NOT add a parallel `json.dumps`-based canonicalizer.
- **No live-campaign infrastructure:** do NOT touch `scripts/protocol_capacity.py`, `scripts/route_manifest.py`, `scripts/route_lineage.py`, `scripts/ledger_start_guard.py`, `scripts/route_compat.py`, `scripts/codex_protocol_model.py`, `scripts/check_go_schema.py`, `coordination/**`, `AGENTS.md`, `.agents/**`, `ARCHITECTURE.md`, `docs/protocol/threeway/*`. This slice IMPORTS `route_lineage` (read-only) but does not modify it.
- Subagents prefix EVERY git command with `env -u GIT_INDEX_FILE`. Explicit pathspecs only; never bare `git commit`/`git add -A` — a **very active coordinator lane** holds dirty WIP and lands commits frequently. Immediately before each commit run `env -u GIT_INDEX_FILE git log --oneline -5`; if new commits touch NONE of your task's files, proceed and note the new HEAD; else report BLOCKED.
- Every commit body includes `User-principal directed immediate execution 2026-07-12 (all seats stale).` and ends with `Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>`. NO push (user-gated).
- `DECISIONS.md` is append-only. Tests import bare (`import route_capability`); `pyproject.toml` sets `pythonpath = [".", "scripts"]`.
- All factual claims in commit bodies cite the producing command (R-EVIDENCE).

---

### Task 1: ADR-016 — consumable capability objects + receipts

**Files:** Modify `DECISIONS.md` (append after ADR-015).

- [ ] **Step 1: Append ADR-016** (verbatim; adjust cited line numbers only if re-verification shows drift — grep `SIDE_EFFECT_EXECUTOR_TOKEN_FIELDS` in `scripts/codex_protocol_model.py` and `_EVIDENCE_SECTION_RE` in `scripts/check_go_schema.py`):

```markdown
## ADR-016: Consumable side-effect capabilities (capability/v1 + receipt/v1)

**Status:** Accepted (primitive only; live token authority not cut over in this slice)

**Context:**
Side-effect executor tokens are a 10-field prose contract
(`scripts/codex_protocol_model.py` `SIDE_EFFECT_EXECUTOR_TOKEN_FIELDS`)
validated by a route-time lint (`scripts/protocol_capacity.py`). Nothing
consumes a token at execution time, nothing prevents a token being replayed,
and route supersession does not revoke an outstanding token — the gap
operator2 flagged as a BLOCKER (mailbox 2026-07-10T01-23-27Z: "no token path
or --executor-token input"). Slices 1-2 (ADR-014/ADR-015) added typed route
identity and lineage, which capability↔route binding needs.

**Decision:**
1. Add `scripts/route_capability.py`: `governance.capability/v1` — a strict
   superset of the 10-field token contract (keeping `allowed_command_class`
   as an exact command literal, `observer_seats`, `final_closeout_owner`, the
   stop condition) plus `capability_id`, `issuer`, `subject`, `bound_route_id`,
   `bound_generation`, `state`, `expires_on`, and non-goals. Canonical bytes
   and hash come from `threeway.canon.canonicalize` (RFC 8785) — library reuse;
   the dormant signed bus (ADR-010) is not activated.
2. `governance.capability-receipt/v1`: a consume writes a receipt carrying
   NON-VACUOUS executed evidence (command + output + a commit SHA or `logs/`
   artifact ref), mirroring `scripts/check_go_schema.py`. A bare
   `state="consumed"` flip with no evidence is rejected as anti-ceremony.
3. Consumption is ATOMIC and one-time: exclusive-create (`O_EXCL`) of the
   receipt keyed by `capability_id`. The first consumer wins; a replay fails
   `already_consumed`.
4. Revocation-on-supersession reuses Slice-2 lineage: a capability is current
   only while its `bound_route_id`/`bound_generation` equal the authoritative
   route's (Slice-2 `resolve_authoritative`). A capability bound to a
   superseded generation is invalid unless a newer route carries it forward
   via route/v1 `capability_refs`.
5. A `route_capability.py consume` CLI is the mechanical enforcement point
   (a script that accepts a token at execution time and refuses replay).
   Wiring `--executor-token` into the dormant `execute_threeway_cutover.sh`
   is a follow-up with the parked signed-bus plan.
6. Compatibility: the prose token blocks and the live route-time token lint
   are UNCHANGED and stay fail-closed; capability/v1 is generated + validated
   alongside, not yet the live authority.
7. ADR-012 invariant preserved: no capability state substitutes for the user
   push gate. A consumed capability is necessary, never sufficient.

**Consequences:**
- Side-effect authority becomes replay-safe and route-bound; a stale or
  already-used capability is refused at execution time by a real script.
- No behavior change to live routes or the token lint; the active campaign is
  unaffected (all new files).
- Full cutover of live token authority to capability/v1 and wiring into the
  signed-bus cutover script are scoped follow-ups.
```

- [ ] **Step 2: Commit** (Rule #7 pre-check first): `env -u GIT_INDEX_FILE git commit -m "docs(adr): ADR-016 consumable capability objects + receipts

User-principal directed immediate execution 2026-07-12 (all seats stale).

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>" -- DECISIONS.md`

---

### Task 2: capability/v1 schema + strict validator

**Files:** Create `schemas/capability-v1.schema.json`; create `scripts/route_capability.py`; create `tests/unit/test_route_capability.py`.

**Interfaces produced:** `SCHEMA_ID = "governance.capability/v1"`; `KNOWN_SEATS`; `TOKEN_FIELDS` (the 10 inherited); `REQUIRED_FIELDS`; `OPTIONAL_FIELDS`; `LIFECYCLE_STATES`; `CapabilityError`; `validate_capability(obj) -> list[str]` (empty == valid); `canonical_capability_bytes(obj) -> bytes`; `capability_hash(obj) -> str`.

- [ ] **Step 1: Write `schemas/capability-v1.schema.json`** (documentation schema; the enforcing validator is hand-rolled — no `jsonschema` dep):

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "governance.capability/v1",
  "title": "Governance OS consumable side-effect capability v1",
  "type": "object",
  "additionalProperties": false,
  "required": [
    "schema", "capability_id", "issuer", "subject",
    "bound_route_id", "bound_generation",
    "side_effect_id", "allowed_command_class", "target",
    "preflight", "stop_if_newer_mail_or_live_target_satisfied", "postcheck",
    "observer_seats", "final_closeout_owner", "non_goals",
    "expires_on", "state"
  ],
  "properties": {
    "schema": { "const": "governance.capability/v1" },
    "capability_id": { "type": "string", "pattern": "^cap-[A-Za-z0-9._-]+$" },
    "issuer": { "enum": ["director", "director2", "operator", "operator2", "coordinator", "coordinator2"] },
    "subject": { "enum": ["director", "director2", "operator", "operator2", "coordinator", "coordinator2"] },
    "bound_route_id": { "type": "string", "minLength": 1 },
    "bound_generation": { "type": "integer", "minimum": 1 },
    "side_effect_id": { "type": "string", "minLength": 1 },
    "allowed_command_class": { "type": "string", "minLength": 1 },
    "target": { "type": "string", "minLength": 1 },
    "preflight": { "type": "string", "minLength": 1 },
    "stop_if_newer_mail_or_live_target_satisfied": { "type": "string", "minLength": 1 },
    "postcheck": { "type": "string", "minLength": 1 },
    "observer_seats": { "type": "string", "minLength": 1 },
    "final_closeout_owner": { "type": "string", "minLength": 1 },
    "non_goals": { "type": "string", "minLength": 1 },
    "expires_on": {
      "type": "object",
      "additionalProperties": false,
      "required": ["event", "packet_id"],
      "properties": {
        "event": { "const": "packet_completed" },
        "packet_id": { "type": "string", "minLength": 1 }
      }
    },
    "state": { "enum": ["issued", "activated", "consumed", "revoked", "expired", "failed"] },
    "extensions": { "type": "object" }
  }
}
```

- [ ] **Step 2: Write failing tests** `tests/unit/test_route_capability.py` (validation core). Use a `_cap(**overrides)` builder returning the valid baseline, and cover: valid; unsupported schema; unknown top-level field (rejected) except `extensions`; each missing required field; `capability_id` pattern; `subject`/`issuer` seat enum; newline/CR in any string field rejected (injection guard, mirroring route/v1); `bound_generation` int≥1 (bool rejected); `expires_on` exact shape; `state` enum; validation does not mutate input. (Write ≥14 assertions in this style — mirror `tests/unit/test_route_manifest.py`'s structure.)

```python
"""capability/v1 validation, hashing, consumption, and receipts (ADR-016)."""
from __future__ import annotations

import copy
import pytest

import route_capability


def _cap(**overrides) -> dict:
    base = {
        "schema": "governance.capability/v1",
        "capability_id": "cap-publish-main-2026-07-12",
        "issuer": "coordinator",
        "subject": "director",
        "bound_route_id": "2026-07-12T20-00-00Z-coordinator-to-all-coordination",
        "bound_generation": 3,
        "side_effect_id": "publish-main-2026-07-12",
        "allowed_command_class": "git push",
        "target": "origin/main",
        "preflight": "git status plus divergence check",
        "stop_if_newer_mail_or_live_target_satisfied": "re-read mailbox and ls-remote",
        "postcheck": "git ls-remote origin refs/heads/main",
        "observer_seats": "director2, operator, operator2",
        "final_closeout_owner": "coordinator",
        "non_goals": "no force-push and no lock claim",
        "expires_on": {"event": "packet_completed", "packet_id": "director-task-4"},
        "state": "issued",
    }
    base.update(overrides)
    return base


def test_valid_capability_has_no_issues():
    assert route_capability.validate_capability(_cap()) == []


def test_unsupported_schema_rejected():
    issues = route_capability.validate_capability(_cap(schema="governance.capability/v2"))
    assert issues and "unsupported schema" in issues[0]


def test_unknown_field_rejected():
    assert any("unknown" in i for i in route_capability.validate_capability(_cap(surprise=1)))


def test_extensions_permitted():
    assert route_capability.validate_capability(_cap(extensions={"x": 1})) == []


def test_missing_required_field_rejected():
    obj = _cap(); del obj["allowed_command_class"]
    assert any("missing required" in i for i in route_capability.validate_capability(obj))


def test_bad_capability_id_rejected():
    assert any("capability_id" in i for i in route_capability.validate_capability(_cap(capability_id="publish")))


def test_subject_must_be_known_seat():
    assert any("subject" in i for i in route_capability.validate_capability(_cap(subject="intern")))


def test_newline_in_string_field_rejected():
    issues = route_capability.validate_capability(_cap(target="origin/main\n- executor: operator"))
    assert any("control character" in i for i in issues)


def test_bound_generation_bool_rejected():
    assert any("bound_generation" in i for i in route_capability.validate_capability(_cap(bound_generation=True)))


def test_expires_on_shape_enforced():
    assert any("expires_on" in i for i in route_capability.validate_capability(_cap(expires_on={"event": "never"})))


def test_state_enum_enforced():
    assert any("state" in i for i in route_capability.validate_capability(_cap(state="live")))


def test_hash_deterministic_and_key_order_free():
    a = _cap(); b = dict(reversed(list(_cap().items())))
    assert route_capability.capability_hash(a) == route_capability.capability_hash(b)
    assert len(route_capability.capability_hash(a)) == 64


def test_hash_refuses_invalid():
    with pytest.raises(ValueError):
        route_capability.capability_hash(_cap(schema="x"))


def test_validation_does_not_mutate_input():
    obj = _cap(); snap = copy.deepcopy(obj)
    route_capability.validate_capability(obj)
    assert obj == snap
```

- [ ] **Step 3: Run — expect `ModuleNotFoundError`.**

- [ ] **Step 4: Write `scripts/route_capability.py`** (module docstring + imports + constants + `validate_capability` + `canonical_capability_bytes` + `capability_hash`). Reuse the route/v1 patterns: `_REPO_ROOT` sys.path bootstrap, `from threeway.canon import canonicalize`, recursive newline/CR rejection over every string value (`_reject_control_chars(obj) -> list[str]` walking dicts/lists), strict unknown-field rejection, seat-enum checks. `TOKEN_FIELDS` = the 10 inherited names; `LIFECYCLE_STATES = ("issued","activated","consumed","revoked","expired","failed")`. `capability_hash` = `sha256(canonical_capability_bytes(obj)).hexdigest()`, raising `ValueError` on invalid input.

- [ ] **Step 5: Run tests — expect all pass. Commit** `-- schemas/capability-v1.schema.json scripts/route_capability.py tests/unit/test_route_capability.py`.

---

### Task 3: capability-receipt/v1 — evidence-bearing, non-vacuous

**Files:** Create `schemas/capability-receipt-v1.schema.json`; modify `scripts/route_capability.py` (append); modify `tests/unit/test_route_capability.py` (append).

**Interfaces produced:** `RECEIPT_SCHEMA_ID = "governance.capability-receipt/v1"`; `validate_receipt(obj) -> list[str]`; `build_receipt(capability, *, result, command, output, commit=None, logs_ref=None) -> dict`.

**Receipt/v1 fields:** `schema`, `capability_id`, `capability_hash`, `result` (`"ok"`|`"failed"`), `command` (the executed command, non-empty), `output` (non-empty), one of `commit` (7-40 hex) or `logs_ref` (`logs/…`) — at least one required (non-vacuous, mirroring `check_go_schema`); `subject`; `target`. `additionalProperties=false`.

- [ ] **Step 1: Write the schema doc + failing tests.** Tests cover: valid receipt with commit; valid with logs_ref; **rejected when NEITHER commit nor logs_ref present** (vacuous evidence — the anti-ceremony case); rejected empty `command`; rejected empty `output`; `result` enum; `capability_hash` must be 64-hex; `build_receipt` produces a valid receipt whose `capability_id`/`capability_hash` match the source capability and rejects a capability that is itself invalid. Key non-vacuity test:

```python
def test_receipt_rejected_without_commit_or_logs():
    r = route_capability.build_receipt(_cap(), result="ok", command="git push", output="done")
    del r["commit"]  # if build set one; ensure neither present
    r.pop("logs_ref", None)
    assert any("evidence" in i for i in route_capability.validate_receipt(r))


def test_build_receipt_binds_capability_id_and_hash():
    cap = _cap()
    r = route_capability.build_receipt(cap, result="ok", command="git push",
                                       output="To origin/main", commit="deadbee")
    assert route_capability.validate_receipt(r) == []
    assert r["capability_id"] == cap["capability_id"]
    assert r["capability_hash"] == route_capability.capability_hash(cap)
```

- [ ] **Step 2: RED, then implement `validate_receipt` + `build_receipt`, GREEN, commit** `-- schemas/capability-receipt-v1.schema.json scripts/route_capability.py tests/unit/test_route_capability.py`.

---

### Task 4: atomic one-time consumption + supersession-revocation binding

**Files:** Modify `scripts/route_capability.py` (append); modify `tests/unit/test_route_capability.py` (append).

**Interfaces produced:** `ConsumeResult` (frozen: `ok: bool`, `reason: str`, `receipt_path: str|None`); `consume(capability, evidence, *, store_dir) -> ConsumeResult` (atomic; writes receipt via `O_EXCL`; replay → `ok=False, reason="already_consumed"`); `capability_is_current(capability, authoritative) -> bool` where `authoritative` is a Slice-2 `route_lineage.LineageRoute` (current iff `capability["bound_route_id"] == authoritative.route_id and capability["bound_generation"] == authoritative.lineage.generation`); `AlreadyConsumed` sentinel reason.

- [ ] **Step 1: Write failing tests** — the security-critical cases:

```python
import route_lineage


def _lr(route_id, generation):
    return route_lineage.LineageRoute(route_id, route_lineage.RouteLineage(generation, None, None))


def _evidence():
    return {"result": "ok", "command": "git push", "output": "To origin/main", "commit": "deadbee"}


def test_consume_writes_receipt_and_succeeds(tmp_path):
    res = route_capability.consume(_cap(), _evidence(), store_dir=tmp_path)
    assert res.ok and res.receipt_path is not None
    from pathlib import Path
    assert Path(res.receipt_path).exists()


def test_second_consume_fails_already_consumed(tmp_path):
    first = route_capability.consume(_cap(), _evidence(), store_dir=tmp_path)
    assert first.ok
    second = route_capability.consume(_cap(), _evidence(), store_dir=tmp_path)
    assert not second.ok and second.reason == "already_consumed"


def test_consume_refuses_invalid_capability(tmp_path):
    res = route_capability.consume(_cap(state="live"), _evidence(), store_dir=tmp_path)
    assert not res.ok and "invalid capability" in res.reason


def test_consume_refuses_vacuous_evidence(tmp_path):
    ev = {"result": "ok", "command": "git push", "output": "done"}  # no commit/logs_ref
    res = route_capability.consume(_cap(), ev, store_dir=tmp_path)
    assert not res.ok and "evidence" in res.reason
    # and NO receipt file was written (fail-closed before O_EXCL)
    assert list(tmp_path.iterdir()) == []


def test_capability_current_only_at_bound_generation():
    cap = _cap(bound_route_id="r5", bound_generation=5)
    assert route_capability.capability_is_current(cap, _lr("r5", 5))
    # superseded: newer generation is authoritative -> stale
    assert not route_capability.capability_is_current(cap, _lr("r6", 6))
    # different route entirely -> stale
    assert not route_capability.capability_is_current(cap, _lr("other", 5))
```

- [ ] **Step 2: Implement.** `consume` MUST: (1) `validate_capability` → refuse `invalid capability` if issues; (2) `validate_receipt(build_receipt(...))` the evidence BEFORE any write → refuse `evidence: …` if vacuous, writing NOTHING (fail-closed); (3) atomically create `store_dir/<capability_id>.receipt.json` with `os.open(path, O_CREAT|O_EXCL|O_WRONLY)` — `FileExistsError` → `ConsumeResult(ok=False, reason="already_consumed")`; (4) on success write the canonical receipt bytes and return the path. Note in a docstring: this is filesystem-CAS, one-time per `capability_id`; a consumed capability is necessary-not-sufficient (the user still gates the push — ADR-012).

- [ ] **Step 3: RED→GREEN, commit** `-- scripts/route_capability.py tests/unit/test_route_capability.py`.

---

### Task 5: the consume CLI (mechanical enforcement point)

**Files:** Modify `scripts/route_capability.py` (append `main`); modify `tests/unit/test_route_capability.py` (append CLI tests).

**Interface produced:** `main(argv) -> int`. Subcommands (argparse): `validate --capability <path>` (exit 0/1 on validity); `consume --capability <path> --store <dir> --result ok|failed --command <str> --output <str> [--commit <sha> | --logs-ref <path>]` (exit 0 on first consume; exit 3 on `already_consumed`; exit 2 on invalid/vacuous). Prints a one-line structured result. This is the "script that accepts a token at execution time and refuses replay" that closes the BLOCKER's general form.

- [ ] **Step 1: Write failing CLI tests** (write a capability JSON to tmp, run `main(["consume", ...])` twice → exit 0 then exit 3; `main(["validate", ...])` on a good and a bad capability → 0/1; vacuous evidence → exit 2). **Step 2:** implement `main`. **Step 3:** RED→GREEN. Confirm `env -u GIT_INDEX_FILE .venv/bin/python scripts/route_capability.py validate --capability <a-fixture>` runs. **Step 4:** commit `-- scripts/route_capability.py tests/unit/test_route_capability.py`.

---

### Task 6: doc + final full-gate verification

**Files:** Create `docs/protocol/capabilities.md`.

- [ ] **Step 1: Write `docs/protocol/capabilities.md`** — what a capability is (superset of the token contract, one-time, route-bound, receipt-backed), the lifecycle (`issued→activated→consumed`; `revoked`/`expired`/`failed`), how a seat consumes one at execution time (`route_capability.py consume …`), the replay refusal, the supersession-revocation rule (`capability_is_current`), and the **explicit ADR-012 caveat**: a consumed capability never substitutes for the user push gate. Show the exact `consume`/`validate` commands and verify each runs literally.

- [ ] **Step 2: Final gates (paste outputs into the commit body — R-EVIDENCE):**

```
env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit -q
env -u GIT_INDEX_FILE .venv/bin/python scripts/ci_smoke.py
env -u GIT_INDEX_FILE .venv/bin/python scripts/route_capability.py validate --capability <a-fixture-you-write-to-tmp>
env -u GIT_INDEX_FILE git diff HEAD --stat
```

Expect: suite green (prior total + the new capability tests, 0 failures, 1 pre-existing xfail unchanged); smoke OK; validate exit 0; diff-stat shows only this slice's files.

- [ ] **Step 3: Commit** `-- docs/protocol/capabilities.md`. Independent verification (Codex Lane-V) is dispatched by the controller after this task; NO push regardless.

---

## Acceptance criteria (P0.4, from the brief as modified by the audit)

1. A capability cannot be consumed twice — atomic `O_EXCL` receipt; replay → `already_consumed` (test).
2. A capability cannot act on another target/command class — `allowed_command_class`/`target` are exact-literal fields; a receipt binds them.
3. A stale capability is invalid after route supersession unless re-bound — `capability_is_current` false at any non-bound generation/route (test).
4. Successful execution produces a typed receipt with non-vacuous evidence (command + output + commit/logs) — vacuous evidence is refused before any write (test).
5. No side-effect authority is inferred from natural-language modal verbs — authority is the typed capability object; newline-injection into any field is rejected (test).
6. ADR-012 invariant intact — a consumed capability is documented as necessary-not-sufficient; the user push gate is unchanged.
7. No live-campaign file touched — `protocol_capacity.py`, route_manifest/lineage, coordination/ unchanged across the slice range.

## Rollback

All new files (module, two schemas, one doc, tests) plus one append-only ADR. Revert the slice's commits; nothing live changed, no migration to unwind.
