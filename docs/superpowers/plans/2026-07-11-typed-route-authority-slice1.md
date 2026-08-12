# Typed Route Authority — Slice 1 (route/v1 compatibility layer) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make route meaning independent of Markdown formatting by introducing a canonical, hash-pinned `governance.route/v1` JSON object with a generated Markdown projection — compatibility-only, no live cutover, no change to the existing prose validator.

**Architecture:** A new stdlib-only module `scripts/route_manifest.py` validates route/v1 objects strictly (fail-closed, unknown fields rejected), hashes them via the repo's single canonicalizer (`threeway.canon.canonicalize`, RFC 8785 — code reuse as a *library*; this does NOT activate the dormant signed bus, ADR-010), and renders a Markdown projection that provably passes the legacy `protocol_capacity.validate_route`. Authority travels as a **sidecar** `<route>.route.json` cross-pinned to the `.md` by a `route_hash:` line — prose physically cannot carry authority, and the live prose lint (which scans every body line for side-effect directives) is never confused by embedded JSON. A committed comparator (`scripts/route_compat.py`) runs legacy and structured verdicts over a fixture corpus and writes a `logs/` artifact (R-MEASURE).

**Tech Stack:** Python ≥3.11 stdlib + `rfc8785` (already a governance dep) + pytest. No new dependencies.

## Provenance: audit of the 2026-07-11 transfer brief

This plan implements the **agreed subset** of `2026-07-11-governance-os-improvement-transfer.md` (external brief, Downloads). A 34-agent audit (7 repo grounders → 13 per-item auditors → 13 adversarial verifiers → completeness critic) verified every brief premise against source. Verdicts (none refuted, all high confidence):

| Item | Verdict | Effort | Key repo evidence |
|---|---|---|---|
| P0.1 typed route manifest | agree w/ modifications | L | Route authority today = regex-parsed prose (`protocol_capacity.py:58-123,1075-1125`); per-line negation (`:1398-1447`) makes meaning wrap-sensitive; no schema/generation/CAS exists |
| P0.2 orthogonal packet state | agree w/ modifications | L | Single `status` field overloaded: a work-complete GO-FOR-ROUTE preflight sits at `blocked` to satisfy G1 exactly-one coverage (`:601-624`); flipping it to `done` trips G1 (reproduced) |
| P0.3 route generation + CAS | agree w/ modifications | M | Only auto-resolver is reverse-lex filename sort (`ledger_start_guard.py:60`); `Supersedes route:` prose parsed by nothing; alias drift exists |
| P0.4 capability objects | agree w/ modifications | L | 10-field token contract is prose parsed line-by-line; no consumption/receipt/revocation; operator2 BLOCKER (mailbox 2026-07-10T01-23-27Z) already flagged the enforcement gap |
| P0.5 contract compiler | agree w/ modifications | XL | All 7 cited contradiction incidents confirmed in git/mailbox; 2 escaped a 3-round preflight (cfaa5b7, 306b968). Sequence last; advisory-first |
| P1.1 risk profiles | agree w/ modifications | L | Live kernel is risk-blind (grep risk/profile → 0); but 4 tier vocabularies already exist (CODEX_EXECUTION_TIERS, G10 split, threeway/tier.py T0-T3, proposed R0-R4) — must reconcile in one ADR |
| P1.2 batched parallel review | partially already implemented | M | Parallel 2-reviewer dispatch + operator synthesis already written (`director-operator.md:696-728`); gap = closure lifecycle fields on reviewer-result/1 |
| P1.3 event log + snapshots | partially already implemented | XL | `threeway/refstore.py` IS an append-only CAS event store (dormant); real bloat cause is G7 full-inventory rule (`protocol_capacity.py:1096-1108`) — fix that cheaply first |
| P1.4 stateful property testing | agree w/ modifications | L | 271 example-based tests, zero property-based; hypothesis absent; sequence after P0.2–P0.4; drop TLA+ |
| P1.5 governance telemetry | partially already implemented | L | `protocol_effectiveness_report.py` already computes route→GO latency, seat utilization, cost-leg metrics, writes `logs/` artifact; gap = campaign scoping + tests |
| P2.1 declarative binding | agree w/ modifications | M | Machine paths hard-coded (`ledger_start_guard.py:12-14`, `codex_protocol_model.py:483-489`, 22 test pins); no `[services]` in kernel config; extend `protocol_doctor.py`, not a new CLI family |
| P2.2 GO attestation | partially already implemented | M | ADR-003 built `check_go_schema.py`; ADR-005 already decided the commit↔GO convention and **deferred the push gate (user decision 2026-06-30)**; extend `reviewer-result/1` (ADR-032), don't mint a new vocabulary |
| P2.3 audit vs notification streams | partially already implemented | M | kinds taxonomy, seat_status/mailbox_monitor/status.py dashboards exist; gap = one per-campaign compact view (`scripts/campaign_status.py`) |

**Brief elements rejected or deferred (with reasons):**

- R0 profile with no independent reviewer — contradicts ADR-001 (every commit gets operator verification).
- R4 "signed attestations" now — collides with ADR-010 (signed bus dormant until a second principal/machine); define R4 as dual mailbox co-sign for now.
- `[services.postgres]` in kernel config — no service endpoints exist in the kernel; belongs to the bound product repo (brief §8.8, ADR-008).
- Multi-target repository binding — ~~conflicts with ADR-008's single designated target; not needed for portability~~ **SUPERSEDED 2026-07-11: the user-principal overrode this deferral; the multi-target registry landed as ADR-013 (`governance.toml` + `scripts/target_binding.py`), amending ADR-008 (evidence-ledger stays the default target).**
- New `governance.review-attestation/v1` vocabulary — extend live `reviewer-result/1` instead (two parallel machine review formats otherwise).
- TLA+/PlusCal — trigger (multi-principal bus) is dormant; no toolchain precedent.
- Sequential-numbered event files (`000001-*.json`) — hot-tree collision on shared sequence numbers (R-HOT-TREE lesson).
- `active_agent_seconds` / `model_and_tool_cost` metrics — no committed instrument can produce them (R-MEASURE); label estimates or drop.
- Full event-sourcing rebuild now — decide refstore-reuse-vs-new-channel by ADR first; fix G7 route bloat cheaply first.
- `hypothesis` silently inside the P0.1 slice (brief §11 deliverable 8) — dependency decision moves to the P1.4 slice ADR; this slice uses deterministic mutation fixtures.
- Brief's `assignments[].work_state/allowed_paths` inside route/v1 — capacity packets stay the assignment/state source until P0.2; route/v1 references packet IDs.
- ULID route ids — mailbox filename stems are the identity today; zero-migration, Rule #8 binding preserved.

**Cross-item conflicts the critic surfaced (bound into this plan):** route/v1 must reserve P0.3's lineage fields (`generation`, `parent_route_id`, `expected_control_head`) **day one** — adding them later is a major-version bump under brief §12.2/§12.3; route/v1 also reserves `packet_delta` and `capability_refs` so the later G7 relaxation (P1.3-lite) and P0.4 are additive-minor. P0.1/P0.2/P1.3 all rewrite `protocol_capacity.py` G1/G7 code → serialized (see roadmap). Any kernel commit moves Pipeline HEAD, which is a live coordinator-token stop condition (mailbox `2026-07-11T12-29-27Z...coordinator-to-director...md:41`) → Task 0 coordination gate.

## Program roadmap (slices after this one — each gets its own plan when scheduled)

| Slice | Content | Depends on |
|---|---|---|
| 1 (this plan) | P0.1 route/v1 compatibility layer, lineage fields reserved | Task 0 gate |
| 2 | P0.3 lineage enforcement: parse `Route generation:`/`Supersedes route:` headers (both alias spellings), lineage-first `find_latest_ledger_route` with legacy fallback, structured `stale_parent` result, ADR | 1 |
| 3 | P1.3-lite: relax G7 to cycle-delta + packet-inventory digest (uses reserved `packet_delta`) | 1; serialize with 4 |
| 4 | P0.2 state split: pure derivation module (`work_state`,`verification_state` from legacy fields), dual-read; G1/G5/G6 remap **gated on workbook-refresh cycle close** | 1 |
| 5 | P0.4 capability/v1 + receipt/v1 + one real enforcement point (`execute_threeway_cutover.sh --executor-token`; closes operator2 BLOCKER 2026-07-10T01-23-27Z) | 1, 2 |
| 6 | P2.2: extend reviewer-result/1 to operator GO attestation (base+head range), CI shape-check only; push gate stays deferred per ADR-005/ADR-010 (user decision) | 1 |
| 7 | P1.2: orchestration.md parallel-review default + reviewer-result/1 closure-lifecycle fields | 6 |
| 8 | P1.4: hypothesis dep ADR + stateful property tests over the real validators | 4, 5 |
| 9 | P1.1: risk profiles — ONE ADR reconciling all 4 tier vocabularies; fail-closed default R3; G1 profile-aware; surface R0/R1 to user-principal (PROGRAM-MANUAL §5) | 1, 4 |
| 10 | P2.1 remainder — the registry/resolver/doctor-check core LANDED 2026-07-11 as ADR-013 (`governance.toml`, `scripts/target_binding.py`, start-guard rewire, multi-target per user override); remaining: `codex_protocol_model`/`.codex` TOML prose regeneration per-target, test path-pin cleanup, wave-default consolidation | — |
| 11 | P1.5: extend `protocol_effectiveness_report.py` (campaign scoping); test-pin existing behavior first; reconcile with parked plan `2026-07-10-signed-bus-authority-identity.md` which already schedules edits to the same files | — |
| 12 | P2.3: `scripts/campaign_status.py` read-only compact campaign view (exit 0 always, no GO semantics) | — |
| 13 | P0.5 contract compiler, advisory-first, incident-pinned rules only; fail-closed gating is a user-principal policy choice | 1, 5 |

## Global Constraints

- Python ≥3.11 only; no 3.12+/3.13-only syntax (ADR-004).
- No new runtime dependencies: `requirements-governance.txt` stays exactly `cryptography>=42.0` + `rfc8785>=0.1.2`. No `jsonschema`, no `hypothesis` in this slice.
- Subagents prefix EVERY git command with `env -u GIT_INDEX_FILE` (seat-index corruption vector, 2026-06-12). Exception: `coordination/bin/*` scripts are NEVER prefixed (deliberate ambient-index design).
- Every commit uses explicit pathspecs: `git commit -m "..." -- <paths>` (R-WIP-POLLUTION). Immediately before each commit run `env -u GIT_INDEX_FILE git log --oneline -5` and check `coordination/mailbox/sent/` for events newer than your write-start (Rule #7).
- NO pushes (push is user-gated AND requires operator GO — R-VERIFY-THEN-PUSH). HEAD is currently ~114 ahead of origin; leave that alone.
- Do not touch: `ARCHITECTURE.md` (dirty in parked Task2U worktree), `AGENTS.md`, `.agents/**`, `docs/protocol/threeway/*.md` (dirty peer WIP), `coordination/mailbox/sent/*` (live campaign), `coordination/capacity/packets/*` (live campaign write scope), `scripts/protocol_capacity.py` (zero-behavior-change slice).
- `DECISIONS.md` is append-only — never edit prior ADRs.
- The canonical serializer is `threeway.canon.canonicalize` (RFC 8785). Do NOT add a parallel `json.dumps`-based canonicalizer (`threeway/canon.py:1-6` doctrine).
- Tests import modules bare (`import route_manifest`, `import protocol_capacity`) — `pyproject.toml` sets `pythonpath = [".", "scripts"]`.
- All factual claims in commit bodies cite the producing command (R-EVIDENCE).

---

### Task 0: Coordination gate + Phase-0 baseline evidence

**Files:**
- Create: `logs/protocol-effectiveness-<generated-at>.json` (written by the committed instrument)

This task has NO code. It exists because (a) the workbook-refresh campaign is open and a live coordinator executor token carries a HEAD-move stop clause (`coordination/mailbox/sent/2026-07-11T12-29-27Z-coordinator-to-director-coordination.md:41`), and (b) the improvement program needs a before-picture (brief DoD #12; the critic found Phase 0 records no cost baseline).

- [ ] **Step 1: Confirm authority to commit kernel changes.** This plan may only be executed by a session operating under a user-named seat (`CLAUDE_SEAT`/`CODEX_SEAT`) or with explicit user approval for unnamed maintenance work. Orientation-mode sessions stop here.

- [ ] **Step 2: Re-orient on live state (read-only):**

```bash
env -u GIT_INDEX_FILE git log --oneline -5
env -u GIT_INDEX_FILE .venv/bin/python .claude/skills/four-seat-protocol/scripts/seat_status.py --all --wave 2
ls coordination/locks/
```

Expected: no locks; identify the newest coordinator-to-all route and whether the workbook-refresh cycle is still open.

- [ ] **Step 3: Coordination gate.** If the workbook-refresh cycle is still open (coordinator token live), send a mailbox heads-up as the named seat announcing bounded kernel-only commits (new files + DECISIONS.md append; no `coordination/` writes), and wait for coordinator ack or cycle close:

```bash
coordination/bin/send-event <your-seat> coordinator coordination "governance-brief slice-1: new-file kernel commits ahead (schemas/, scripts/route_manifest.py, scripts/route_compat.py, tests/), DECISIONS.md append. No coordination/ writes, no push. Pipeline HEAD will move."
```

(Note: NO `env -u` prefix on `coordination/bin/*`.) If all seats are stale and the user directs immediate execution, record that user direction in the Task 1 commit body instead.

- [ ] **Step 4: Capture the Phase-0 baseline (committed instrument → logs/ artifact, R-MEASURE):**

```bash
env -u GIT_INDEX_FILE .venv/bin/python scripts/ci_smoke.py
env -u GIT_INDEX_FILE .venv/bin/python scripts/protocol_effectiveness_report.py --wave 2
```

Expected: smoke exits 0; the report prints a Markdown summary and writes `logs/protocol-effectiveness-<timestamp>.json`.

- [ ] **Step 5: Commit the baseline artifact (if logs/ is tracked):**

```bash
env -u GIT_INDEX_FILE git check-ignore -q logs/ && echo "logs/ gitignored — cite artifact path in Task 1 ADR instead" || { env -u GIT_INDEX_FILE git add logs/protocol-effectiveness-*.json && env -u GIT_INDEX_FILE git commit -m "docs(baseline): phase-0 governance-cost baseline before route/v1 work

verified via \$ .venv/bin/python scripts/protocol_effectiveness_report.py --wave 2 -> logs artifact
Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>" -- logs/; }
```

---

### Task 1: ADR-014 — typed route manifest authority

**Files:**
- Modify: `DECISIONS.md` (append only, after ADR-012)

**Interfaces:**
- Produces: the decision record every later task cites; the schema-id string `governance.route/v1`.

- [ ] **Step 1: Append ADR-014 to DECISIONS.md** (verbatim; adjust the two audit-fact citations only if re-verification shows drift):

```markdown
## ADR-014: Typed route manifests (route/v1) — JSON authority, Markdown projection

**Status:** Accepted (compatibility layer only; live cutover requires a follow-up ADR)

**Context:**
Route authority is regex-parsed Markdown prose: headings, field aliases, modal
verbs, per-physical-line negation boundaries, and side-effect phrase tables
(`scripts/protocol_capacity.py:58-123,1075-1125,1396-1448`). Because negation
scanning is per-line, wrapping a prohibition across lines changes its machine
meaning (false side-effect demands; the fail-open direction exists too). The
2026-07-11 workbook-refresh campaign and the external improvement brief
(2026-07-11 transfer) both surfaced this class. The only automatic
current-route resolver is reverse-lexicographic filename sort
(`scripts/ledger_start_guard.py:60`), and `Supersedes route:` prose is parsed
by nothing.

**Decision:**
1. Introduce `governance.route/v1`: a strictly-validated JSON object
   (`scripts/route_manifest.py`, documented by `schemas/route-v1.schema.json`).
   Canonical bytes come from `threeway.canon.canonicalize` (RFC 8785) — reuse
   of threeway code AS A LIBRARY; this does not activate the dormant signed
   bus and does not touch `refs/threeway/*` (ADR-010 boundary intact).
2. Authority-vs-projection: the object lives in a sidecar
   `<route-id>.route.json` whose bytes ARE the canonical serialization; the
   Markdown event carries a `route_hash:` pin. Embedding JSON inside the
   route body was rejected because the live prose lint scans every body line
   for side-effect directives and would false-match token field values
   (e.g. `"allowed_command_class": "git push"`).
3. Forward-compatibility fields are REQUIRED from day one so later slices are
   additive-minor, not major bumps (brief §12.2/§12.3): `generation`,
   `parent_route_id`, `expected_control_head` (P0.3 — validated for shape,
   CAS-unenforced in this slice), `packet_delta` (P1.3 — must be null),
   `capability_refs` (P0.4 — must be []).
4. Unknown top-level fields are REJECTED except under an explicit
   `extensions` object. Readers reject unsupported `schema` values.
5. Route identity = mailbox filename stem (zero migration, Rule #8 binding
   preserved). ULIDs were considered and rejected for now.
6. Compatibility only: Markdown routes remain the live authority. The
   comparator (`scripts/route_compat.py`) must show legacy/structured
   equivalence over the fixture corpus (divergences triaged as
   legacy-formatting defects vs regressions) before any cutover ADR.
7. Property-style formatting-invariance is tested with deterministic mutation
   fixtures; adopting `hypothesis` is deferred to the P1.4 slice ADR.

**Consequences:**
- Reformatting prose can no longer change what a structured reader believes;
  during compatibility the legacy validator still governs live routes.
- Known legacy wrapped-negation defect is pinned as a strict xfail
  (R-VERIFY-TIER) rather than fixed in the prose parser.
- Sidecar placement for LIVE routes (mailbox naming-lint interaction) is
  explicitly deferred to the cutover ADR; this slice writes pairs only in
  tests and fixtures.
```

- [ ] **Step 2: Commit** (Rule #7 pre-check first):

```bash
env -u GIT_INDEX_FILE git log --oneline -5
env -u GIT_INDEX_FILE git commit -m "docs(adr): ADR-014 typed route manifest authority (route/v1)

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>" -- DECISIONS.md
```

---

### Task 2: route/v1 schema document + sync test

**Files:**
- Create: `schemas/route-v1.schema.json`
- Create: `tests/unit/test_route_schema_sync.py`

**Interfaces:**
- Produces: `schemas/route-v1.schema.json` (documentation schema; the enforcing validator is hand-rolled in Task 3 — no `jsonschema` dependency). The sync test guarantees the two never drift.
- Consumes: `route_manifest` module constants (Task 3 — write the test FIRST; it fails until Task 3 lands. Execute Task 2 steps 1-2, then Task 3, then Task 2 step 3.)

- [ ] **Step 1: Write `schemas/route-v1.schema.json`:**

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "governance.route/v1",
  "title": "Governance OS route manifest v1",
  "type": "object",
  "additionalProperties": false,
  "required": [
    "schema", "route_id", "task_board", "wave", "generation",
    "parent_route_id", "expected_control_head", "created_at", "created_by",
    "target", "packet_refs", "packet_delta", "capability_refs",
    "capacity_split", "prohibitions", "side_effect_token",
    "join_condition", "next_trigger"
  ],
  "properties": {
    "schema": { "const": "governance.route/v1" },
    "route_id": {
      "type": "string",
      "pattern": "^[^/\\s]+-coordinator-to-all-[^/\\s]+$",
      "description": "Mailbox filename stem; the .md and .route.json pair share it."
    },
    "task_board": { "type": "string", "minLength": 1 },
    "wave": { "type": "integer", "minimum": 1 },
    "generation": {
      "type": "integer", "minimum": 1,
      "description": "Reserved for P0.3; shape-validated only in v1 slice 1."
    },
    "parent_route_id": {
      "type": ["string", "null"],
      "description": "Null iff generation == 1."
    },
    "expected_control_head": {
      "type": ["string", "null"], "pattern": "^[0-9a-f]{7,40}$",
      "description": "Reserved for P0.3 CAS; shape-validated only in slice 1."
    },
    "created_at": {
      "type": "string",
      "pattern": "^\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}Z$"
    },
    "created_by": {
      "enum": ["director", "director2", "operator", "operator2", "coordinator", "coordinator2"]
    },
    "target": {
      "type": ["object", "null"],
      "additionalProperties": false,
      "required": ["repository", "base_commit", "worktree"],
      "properties": {
        "repository": { "type": "string", "minLength": 1 },
        "base_commit": { "type": "string", "pattern": "^[0-9a-f]{7,40}$" },
        "worktree": { "type": ["string", "null"] }
      }
    },
    "packet_refs": {
      "type": "array", "minItems": 1, "uniqueItems": true,
      "items": { "type": "string", "minLength": 1 },
      "description": "Capacity-packet IDs. Packets stay the assignment/state source (P0.2 pending)."
    },
    "packet_delta": {
      "type": "null",
      "description": "Reserved for P1.3-lite (cycle delta + inventory digest). Must be null in v1.0."
    },
    "capability_refs": {
      "type": "array", "maxItems": 0,
      "description": "Reserved for P0.4 capability objects. Must be [] in v1.0."
    },
    "capacity_split": {
      "type": "object",
      "oneOf": [
        {
          "additionalProperties": false,
          "required": ["mode"],
          "properties": { "mode": { "const": "single_pair" } }
        },
        {
          "additionalProperties": false,
          "required": ["mode", "chunk_a", "chunk_b"],
          "properties": {
            "mode": { "const": "dual_pair" },
            "chunk_a": { "type": "array", "minItems": 1, "items": { "type": "string" } },
            "chunk_b": { "type": "array", "minItems": 1, "items": { "type": "string" } }
          }
        }
      ]
    },
    "prohibitions": {
      "type": "array", "uniqueItems": true,
      "items": {
        "enum": [
          "remote_ref_update", "lock_action", "paid_spend", "pod_action",
          "production_generation", "target_checkout_refresh",
          "cursor_consume", "route_mutation", "canonical_database_mutation"
        ]
      }
    },
    "side_effect_token": {
      "type": ["object", "null"],
      "additionalProperties": false,
      "required": [
        "side_effect_id", "executor", "target", "allowed_command_class",
        "preflight", "stop_if_newer_mail_or_live_target_satisfied",
        "postcheck", "observer_seats", "final_closeout_owner", "non_goals"
      ],
      "properties": {
        "side_effect_id": { "type": "string", "minLength": 1 },
        "executor": {
          "enum": ["director", "director2", "operator", "operator2", "coordinator", "coordinator2"]
        },
        "target": { "type": "string", "minLength": 1 },
        "allowed_command_class": { "type": "string", "minLength": 1 },
        "preflight": { "type": "string", "minLength": 1 },
        "stop_if_newer_mail_or_live_target_satisfied": { "type": "string", "minLength": 1 },
        "postcheck": { "type": "string", "minLength": 1 },
        "observer_seats": { "type": "string", "minLength": 1 },
        "final_closeout_owner": { "type": "string", "minLength": 1 },
        "non_goals": { "type": "string", "minLength": 1 }
      }
    },
    "join_condition": { "type": "string", "minLength": 1 },
    "next_trigger": { "type": "string", "minLength": 1 },
    "extensions": {
      "type": "object",
      "description": "Namespaced experimental data. Never authority-bearing."
    }
  }
}
```

- [ ] **Step 2: Write the failing sync test `tests/unit/test_route_schema_sync.py`:**

```python
"""schemas/route-v1.schema.json must never drift from the enforcing validator."""
from __future__ import annotations

import json
from pathlib import Path

import route_manifest


def _schema() -> dict:
    path = Path(__file__).resolve().parent.parent.parent / "schemas" / "route-v1.schema.json"
    return json.loads(path.read_text(encoding="utf-8"))


def test_schema_id_matches_module():
    assert _schema()["$id"] == route_manifest.SCHEMA_ID


def test_required_fields_match_module():
    assert tuple(_schema()["required"]) == route_manifest.REQUIRED_FIELDS


def test_properties_cover_required_plus_optional_only():
    props = set(_schema()["properties"])
    assert props == set(route_manifest.REQUIRED_FIELDS) | set(route_manifest.OPTIONAL_FIELDS)


def test_schema_rejects_unknown_fields():
    assert _schema()["additionalProperties"] is False


def test_prohibition_enum_matches_vocab():
    enum = _schema()["properties"]["prohibitions"]["items"]["enum"]
    assert set(enum) == set(route_manifest.PROHIBITION_VOCAB)


def test_token_fields_match_module():
    token = _schema()["properties"]["side_effect_token"]
    assert tuple(token["required"]) == route_manifest.SIDE_EFFECT_TOKEN_FIELDS
    assert set(token["properties"]) == set(route_manifest.SIDE_EFFECT_TOKEN_FIELDS)


def test_seat_enums_match_module():
    schema = _schema()
    assert tuple(schema["properties"]["created_by"]["enum"]) == route_manifest.KNOWN_SEATS
    assert (
        tuple(schema["properties"]["side_effect_token"]["properties"]["executor"]["enum"])
        == route_manifest.KNOWN_SEATS
    )
```

Run: `env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_route_schema_sync.py -q`
Expected: FAIL with `ModuleNotFoundError: No module named 'route_manifest'` (Task 3 provides it).

- [ ] **Step 3 (after Task 3): run again, expect 7 passed, then commit:**

```bash
env -u GIT_INDEX_FILE git log --oneline -5
env -u GIT_INDEX_FILE git commit -m "feat(route): route/v1 schema document + module sync test

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>" -- schemas/route-v1.schema.json tests/unit/test_route_schema_sync.py
```

---

### Task 3: strict route/v1 object validator

**Files:**
- Create: `scripts/route_manifest.py`
- Create: `tests/unit/test_route_manifest.py`

**Interfaces:**
- Produces: `SCHEMA_ID: str`, `REQUIRED_FIELDS: tuple[str, ...]`, `OPTIONAL_FIELDS: tuple[str, ...]`, `PROHIBITION_VOCAB: dict[str, str]`, `SIDE_EFFECT_TOKEN_FIELDS: tuple[str, ...]`, `KNOWN_SEATS: tuple[str, ...]`, `validate_route_object(obj) -> list[str]` (empty list == valid; issue strings otherwise).

- [ ] **Step 1: Write failing tests (validation core) in `tests/unit/test_route_manifest.py`:**

```python
"""route/v1 object validation, hashing, and sidecar manifest tests."""
from __future__ import annotations

import copy

import pytest

import route_manifest


def _route(**overrides) -> dict:
    base = {
        "schema": "governance.route/v1",
        "route_id": "2026-07-11T20-00-00Z-coordinator-to-all-coordination",
        "task_board": "route-compat-cycle",
        "wave": 2,
        "generation": 1,
        "parent_route_id": None,
        "expected_control_head": None,
        "created_at": "2026-07-11T20:00:00Z",
        "created_by": "coordinator",
        "target": None,
        "packet_refs": [
            "coord-capacity-split-route",
            "director-capacity-split-chunk-a",
            "operator-capacity-split-chunk-a",
            "director2-capacity-split-work",
            "operator2-capacity-split-work",
        ],
        "packet_delta": None,
        "capability_refs": [],
        "capacity_split": {"mode": "single_pair"},
        "prohibitions": ["remote_ref_update"],
        "side_effect_token": None,
        "join_condition": "coordinator closes after both pair lanes are accounted for.",
        "next_trigger": "Director continues Chunk A; Pair B follows the capacity split decision.",
    }
    base.update(overrides)
    return base


def _token(**overrides) -> dict:
    token = {
        "side_effect_id": "publish-main-2026-07-11",
        "executor": "director",
        "target": "origin/main",
        "allowed_command_class": "git push",
        "preflight": "git status plus divergence check",
        "stop_if_newer_mail_or_live_target_satisfied": "re-read mailbox and ls-remote",
        "postcheck": "git ls-remote origin refs/heads/main",
        "observer_seats": "director2, operator, operator2",
        "final_closeout_owner": "coordinator",
        "non_goals": "no force-push and no lock claim",
    }
    token.update(overrides)
    return token


def test_valid_route_has_no_issues():
    assert route_manifest.validate_route_object(_route()) == []


def test_valid_route_with_token_has_no_issues():
    assert route_manifest.validate_route_object(_route(side_effect_token=_token())) == []


def test_non_dict_rejected():
    assert route_manifest.validate_route_object(["not", "a", "route"])


def test_unsupported_schema_version_rejected():
    issues = route_manifest.validate_route_object(_route(schema="governance.route/v2"))
    assert issues and "unsupported schema" in issues[0]


def test_unknown_field_rejected():
    issues = route_manifest.validate_route_object(_route(surprise="x"))
    assert any("unknown" in issue for issue in issues)


def test_extensions_object_permitted():
    assert route_manifest.validate_route_object(_route(extensions={"x-lab": 1})) == []


def test_missing_field_rejected():
    obj = _route()
    del obj["join_condition"]
    issues = route_manifest.validate_route_object(obj)
    assert any("missing required fields" in issue for issue in issues)


def test_generation_above_one_requires_parent():
    issues = route_manifest.validate_route_object(_route(generation=2, parent_route_id=None))
    assert any("parent_route_id" in issue for issue in issues)


def test_generation_one_forbids_parent():
    issues = route_manifest.validate_route_object(
        _route(parent_route_id="2026-07-11T10-00-00Z-coordinator-to-all-coordination")
    )
    assert any("parent_route_id" in issue for issue in issues)


def test_packet_delta_must_be_null_in_v1():
    issues = route_manifest.validate_route_object(_route(packet_delta={"changed": []}))
    assert any("packet_delta" in issue for issue in issues)


def test_capability_refs_must_be_empty_in_v1():
    issues = route_manifest.validate_route_object(_route(capability_refs=["cap-1"]))
    assert any("capability_refs" in issue for issue in issues)


def test_multi_executor_token_rejected():
    issues = route_manifest.validate_route_object(
        _route(side_effect_token=_token(executor="director and operator"))
    )
    assert any("executor" in issue for issue in issues)


def test_unknown_prohibition_rejected():
    issues = route_manifest.validate_route_object(_route(prohibitions=["push_hard"]))
    assert any("prohibition" in issue for issue in issues)


def test_weak_next_trigger_rejected():
    issues = route_manifest.validate_route_object(_route(next_trigger="none"))
    assert any("next_trigger" in issue for issue in issues)


def test_dual_pair_requires_disjoint_chunks_from_packet_refs():
    route = _route(
        capacity_split={
            "mode": "dual_pair",
            "chunk_a": ["director-capacity-split-chunk-a"],
            "chunk_b": ["director-capacity-split-chunk-a"],
        }
    )
    issues = route_manifest.validate_route_object(route)
    assert any("chunk" in issue for issue in issues)


def test_bad_created_at_rejected():
    issues = route_manifest.validate_route_object(_route(created_at="July 11, 2026"))
    assert any("created_at" in issue for issue in issues)


def test_route_id_must_be_coordinator_to_all_stem():
    issues = route_manifest.validate_route_object(_route(route_id="2026-07-11-director-note"))
    assert any("route_id" in issue for issue in issues)


def test_target_shape_checked():
    issues = route_manifest.validate_route_object(_route(target={"repository": "x"}))
    assert any("target" in issue for issue in issues)


def test_validation_does_not_mutate_input():
    obj = _route()
    snapshot = copy.deepcopy(obj)
    route_manifest.validate_route_object(obj)
    assert obj == snapshot
```

Run: `env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_route_manifest.py -q`
Expected: FAIL — `ModuleNotFoundError: No module named 'route_manifest'`.

- [ ] **Step 2: Write `scripts/route_manifest.py` (validation core):**

```python
#!/usr/bin/env python3
"""governance.route/v1 — typed route manifest: validate, hash, pair-write, read (ADR-014).

Compatibility layer only: Markdown mailbox routes remain the live authority.
This module provides the canonical typed object + generated projection so route
meaning stops depending on prose formatting. Canonical bytes come from
threeway.canon.canonicalize (RFC 8785) — library reuse; the dormant signed bus
(ADR-010) is NOT activated and refs/threeway/* is never touched.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any, Sequence

# Bootstrap sys.path so a bare `python scripts/route_manifest.py` imports the
# repo-root `threeway` package regardless of CWD. Mirrors scripts/ci_smoke.py.
_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from threeway.canon import canonicalize  # noqa: E402

SCHEMA_ID = "governance.route/v1"

KNOWN_SEATS = (
    "director",
    "director2",
    "operator",
    "operator2",
    "coordinator",
    "coordinator2",
)

# Every prohibition renders as ONE physical line starting with "no " so the
# legacy per-line negation boundary always sees negation and term together.
PROHIBITION_VOCAB = {
    "remote_ref_update": "No push or remote-ref update by any seat in this cycle.",
    "lock_action": "No lock claim and no lock release in this cycle.",
    "paid_spend": "No paid API spend in this cycle.",
    "pod_action": "No pod action and no pod spend in this cycle.",
    "production_generation": "No production generation in this cycle.",
    "target_checkout_refresh": "No target-repo checkout refresh in this cycle.",
    "cursor_consume": "No cursor consume in this cycle.",
    "route_mutation": "No route mutation by any non-coordinator seat in this cycle.",
    "canonical_database_mutation": "No canonical database mutation in this cycle.",
}

# Field order mirrors scripts/protocol_capacity.py REQUIRED_SIDE_EFFECT_TOKEN_FIELDS.
SIDE_EFFECT_TOKEN_FIELDS = (
    "side_effect_id",
    "executor",
    "target",
    "allowed_command_class",
    "preflight",
    "stop_if_newer_mail_or_live_target_satisfied",
    "postcheck",
    "observer_seats",
    "final_closeout_owner",
    "non_goals",
)

REQUIRED_FIELDS = (
    "schema",
    "route_id",
    "task_board",
    "wave",
    "generation",
    "parent_route_id",
    "expected_control_head",
    "created_at",
    "created_by",
    "target",
    "packet_refs",
    "packet_delta",
    "capability_refs",
    "capacity_split",
    "prohibitions",
    "side_effect_token",
    "join_condition",
    "next_trigger",
)
OPTIONAL_FIELDS = ("extensions",)

_CREATED_AT_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
_HEX_HEAD_RE = re.compile(r"^[0-9a-f]{7,40}$")
_ROUTE_ID_RE = re.compile(r"^[^/\s]+-coordinator-to-all-[^/\s]+$")
# Mirrors protocol_capacity._WEAK_TRIGGER_RE (weak triggers are not authority).
_WEAK_TRIGGER_RE = re.compile(
    r"^(?:none|n/a|not applicable|to be decided|no trigger|same as above)$",
    re.IGNORECASE,
)


class RouteManifestError(ValueError):
    """A route pair (.md + .route.json) is absent, mismatched, or invalid."""


def _is_nonempty_str(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def validate_route_object(obj: Any) -> list[str]:
    """Strict fail-closed validation of a route/v1 object. Empty list == valid."""
    if not isinstance(obj, dict):
        return ["route object must be a JSON object"]
    if obj.get("schema") != SCHEMA_ID:
        return [f"unsupported schema: {obj.get('schema')!r} (expected {SCHEMA_ID})"]

    issues: list[str] = []
    unknown = sorted(set(obj) - set(REQUIRED_FIELDS) - set(OPTIONAL_FIELDS))
    if unknown:
        issues.append("unknown authority-bearing fields rejected: " + ", ".join(unknown))
    missing = sorted(set(REQUIRED_FIELDS) - set(obj))
    if missing:
        issues.append("missing required fields: " + ", ".join(missing))
        return issues

    if not (_is_nonempty_str(obj["route_id"]) and _ROUTE_ID_RE.fullmatch(obj["route_id"])):
        issues.append("route_id must be a coordinator-to-all mailbox filename stem")
    if not _is_nonempty_str(obj["task_board"]):
        issues.append("task_board must be a non-empty string")
    if not (isinstance(obj["wave"], int) and not isinstance(obj["wave"], bool) and obj["wave"] >= 1):
        issues.append("wave must be an integer >= 1")
    generation = obj["generation"]
    if not (isinstance(generation, int) and not isinstance(generation, bool) and generation >= 1):
        issues.append("generation must be an integer >= 1")
    else:
        parent = obj["parent_route_id"]
        if generation == 1 and parent is not None:
            issues.append("parent_route_id must be null when generation == 1")
        if generation > 1 and not _is_nonempty_str(parent):
            issues.append("parent_route_id is required when generation > 1")
    head = obj["expected_control_head"]
    if head is not None and not (isinstance(head, str) and _HEX_HEAD_RE.fullmatch(head)):
        issues.append("expected_control_head must be null or 7-40 lowercase hex")
    if not (isinstance(obj["created_at"], str) and _CREATED_AT_RE.fullmatch(obj["created_at"])):
        issues.append("created_at must match YYYY-MM-DDTHH:MM:SSZ")
    if obj["created_by"] not in KNOWN_SEATS:
        issues.append("created_by must be a known seat")

    target = obj["target"]
    if target is not None:
        if not isinstance(target, dict) or set(target) != {"repository", "base_commit", "worktree"}:
            issues.append("target must be null or {repository, base_commit, worktree}")
        else:
            if not _is_nonempty_str(target["repository"]):
                issues.append("target.repository must be a non-empty string")
            if not (
                isinstance(target["base_commit"], str)
                and _HEX_HEAD_RE.fullmatch(target["base_commit"])
            ):
                issues.append("target.base_commit must be 7-40 lowercase hex")
            if target["worktree"] is not None and not _is_nonempty_str(target["worktree"]):
                issues.append("target.worktree must be null or a non-empty string")

    refs = obj["packet_refs"]
    if (
        not isinstance(refs, list)
        or not refs
        or not all(_is_nonempty_str(ref) for ref in refs)
        or len(set(refs)) != len(refs)
    ):
        issues.append("packet_refs must be a non-empty list of unique packet ids")
        refs = []
    if obj["packet_delta"] is not None:
        issues.append("packet_delta is reserved (P1.3) and must be null in v1.0")
    if obj["capability_refs"] != []:
        issues.append("capability_refs is reserved (P0.4) and must be [] in v1.0")

    split = obj["capacity_split"]
    if not isinstance(split, dict) or split.get("mode") not in ("single_pair", "dual_pair"):
        issues.append("capacity_split.mode must be single_pair or dual_pair")
    elif split["mode"] == "single_pair":
        if set(split) != {"mode"}:
            issues.append("single_pair capacity_split takes no extra keys")
    else:
        if set(split) != {"mode", "chunk_a", "chunk_b"}:
            issues.append("dual_pair capacity_split requires exactly mode, chunk_a, chunk_b")
        else:
            chunk_a, chunk_b = split["chunk_a"], split["chunk_b"]
            chunks_ok = (
                isinstance(chunk_a, list)
                and isinstance(chunk_b, list)
                and chunk_a
                and chunk_b
                and all(_is_nonempty_str(item) for item in [*chunk_a, *chunk_b])
            )
            if not chunks_ok:
                issues.append("chunk_a and chunk_b must be non-empty lists of packet ids")
            else:
                if set(chunk_a) & set(chunk_b):
                    issues.append("chunk_a and chunk_b must be disjoint")
                if not (set(chunk_a) | set(chunk_b)) <= set(refs):
                    issues.append("chunk packet ids must be members of packet_refs")

    prohibitions = obj["prohibitions"]
    if not isinstance(prohibitions, list) or len(set(map(str, prohibitions))) != len(prohibitions):
        issues.append("prohibitions must be a list of unique keys")
    else:
        bad = sorted(set(map(str, prohibitions)) - set(PROHIBITION_VOCAB))
        if bad:
            issues.append("unknown prohibition keys: " + ", ".join(bad))

    token = obj["side_effect_token"]
    if token is not None:
        if not isinstance(token, dict) or set(token) != set(SIDE_EFFECT_TOKEN_FIELDS):
            issues.append(
                "side_effect_token must carry exactly the 10 required fields"
            )
        else:
            for field in SIDE_EFFECT_TOKEN_FIELDS:
                if not _is_nonempty_str(token[field]):
                    issues.append(f"side_effect_token.{field} must be a non-empty string")
            if token.get("executor") not in KNOWN_SEATS:
                issues.append(
                    "side_effect_token.executor must be exactly one known seat"
                )

    if not _is_nonempty_str(obj["join_condition"]):
        issues.append("join_condition must be a non-empty string")
    trigger = obj["next_trigger"]
    if not _is_nonempty_str(trigger) or _WEAK_TRIGGER_RE.fullmatch(trigger.strip()):
        issues.append("next_trigger must be a non-empty, non-weak trigger")
    if "extensions" in obj and not isinstance(obj["extensions"], dict):
        issues.append("extensions must be an object")
    return issues
```

- [ ] **Step 3: Run the tests:**

Run: `env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_route_manifest.py tests/unit/test_route_schema_sync.py -q`
Expected: all PASS (validation tests + the 7 sync tests from Task 2).

- [ ] **Step 4: Commit (module + tests), then finish Task 2 step 3 commit:**

```bash
env -u GIT_INDEX_FILE git log --oneline -5
env -u GIT_INDEX_FILE git commit -m "feat(route): strict route/v1 object validator (ADR-014)

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>" -- scripts/route_manifest.py tests/unit/test_route_manifest.py
```

---

### Task 4: canonical hash + sidecar manifest read

**Files:**
- Modify: `scripts/route_manifest.py` (append)
- Modify: `tests/unit/test_route_manifest.py` (append)

**Interfaces:**
- Produces: `route_hash(obj) -> str` (sha256 hex of RFC 8785 bytes; raises `ValueError` on invalid objects), `canonical_route_bytes(obj) -> bytes`, `read_manifest(md_path: Path) -> dict` (loads + verifies the sidecar; raises `RouteManifestError`), `HASH_LINE_RE`.

- [ ] **Step 1: Append failing tests to `tests/unit/test_route_manifest.py`:**

```python
def test_route_hash_is_deterministic_and_key_order_free():
    obj_a = _route()
    obj_b = dict(reversed(list(_route().items())))
    assert route_manifest.route_hash(obj_a) == route_manifest.route_hash(obj_b)
    assert len(route_manifest.route_hash(obj_a)) == 64


def test_route_hash_changes_when_authority_changes():
    assert route_manifest.route_hash(_route()) != route_manifest.route_hash(
        _route(prohibitions=[])
    )


def test_route_hash_refuses_invalid_object():
    with pytest.raises(ValueError):
        route_manifest.route_hash(_route(schema="governance.route/v2"))


def _write_pair_by_hand(tmp_path, route, *, hash_line=None, sidecar_bytes=None):
    md_path = tmp_path / f"{route['route_id']}.md"
    sidecar = tmp_path / f"{route['route_id']}.route.json"
    digest = hash_line or f"route_hash: {route_manifest.route_hash(route)}"
    md_path.write_text(
        f"# Fixture route\n\nTask-board: {route['task_board']}\n\n{digest}\n",
        encoding="utf-8",
    )
    sidecar.write_bytes(
        sidecar_bytes
        if sidecar_bytes is not None
        else route_manifest.canonical_route_bytes(route)
    )
    return md_path


def test_read_manifest_round_trips(tmp_path):
    md_path = _write_pair_by_hand(tmp_path, _route())
    assert route_manifest.read_manifest(md_path) == _route()


def test_read_manifest_rejects_missing_sidecar(tmp_path):
    md_path = _write_pair_by_hand(tmp_path, _route())
    md_path.with_suffix(".route.json").unlink()
    with pytest.raises(route_manifest.RouteManifestError):
        route_manifest.read_manifest(md_path)


def test_read_manifest_rejects_hash_mismatch(tmp_path):
    md_path = _write_pair_by_hand(tmp_path, _route(), hash_line="route_hash: " + "0" * 64)
    with pytest.raises(route_manifest.RouteManifestError):
        route_manifest.read_manifest(md_path)


def test_read_manifest_rejects_missing_hash_line(tmp_path):
    md_path = _write_pair_by_hand(tmp_path, _route(), hash_line="(no pin)")
    with pytest.raises(route_manifest.RouteManifestError):
        route_manifest.read_manifest(md_path)


def test_read_manifest_rejects_noncanonical_sidecar_bytes(tmp_path):
    pretty = json.dumps(_route(), indent=2).encode("utf-8")
    md_path = _write_pair_by_hand(tmp_path, _route(), sidecar_bytes=pretty)
    with pytest.raises(route_manifest.RouteManifestError):
        route_manifest.read_manifest(md_path)
```

Also add `import json` to the test module imports.

Run: `env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_route_manifest.py -q`
Expected: FAIL — `AttributeError: module 'route_manifest' has no attribute 'route_hash'`.

- [ ] **Step 2: Append to `scripts/route_manifest.py`:**

```python
HASH_LINE_RE = re.compile(r"(?im)^route_hash:\s*(?P<digest>[0-9a-f]{64})\s*$")


def canonical_route_bytes(obj: dict) -> bytes:
    """RFC 8785 canonical bytes of a VALID route object (these ARE the sidecar bytes)."""
    issues = validate_route_object(obj)
    if issues:
        raise ValueError("cannot canonicalize an invalid route object: " + "; ".join(issues))
    return canonicalize(obj)


def route_hash(obj: dict) -> str:
    return hashlib.sha256(canonical_route_bytes(obj)).hexdigest()


def sidecar_path(md_path: Path) -> Path:
    return md_path.with_suffix(".route.json")


def read_manifest(md_path: Path) -> dict:
    """Load and verify the route pair. Fail-closed: any absence/mismatch raises."""
    try:
        body = md_path.read_text(encoding="utf-8")
    except OSError as exc:
        raise RouteManifestError(f"unreadable route projection: {exc}") from exc
    pins = HASH_LINE_RE.findall(body)
    if len(pins) != 1:
        raise RouteManifestError(
            f"{md_path.name}: expected exactly one route_hash pin, found {len(pins)}"
        )
    sidecar = sidecar_path(md_path)
    try:
        raw = sidecar.read_bytes()
    except OSError as exc:
        raise RouteManifestError(f"missing route sidecar {sidecar.name}: {exc}") from exc
    try:
        obj = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise RouteManifestError(f"{sidecar.name}: unparseable JSON: {exc}") from exc
    issues = validate_route_object(obj)
    if issues:
        raise RouteManifestError(f"{sidecar.name}: invalid route object: " + "; ".join(issues))
    if canonicalize(obj) != raw:
        raise RouteManifestError(f"{sidecar.name}: bytes are not canonical (RFC 8785)")
    digest = hashlib.sha256(raw).hexdigest()
    if digest != pins[0]:
        raise RouteManifestError(
            f"{md_path.name}: route_hash pin {pins[0][:12]}... does not match sidecar {digest[:12]}..."
        )
    return obj
```

- [ ] **Step 3: Run: `env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_route_manifest.py -q` — expect all PASS.**

- [ ] **Step 4: Commit:**

```bash
env -u GIT_INDEX_FILE git log --oneline -5
env -u GIT_INDEX_FILE git commit -m "feat(route): canonical route hash + fail-closed sidecar manifest read

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>" -- scripts/route_manifest.py tests/unit/test_route_manifest.py
```

---

### Task 5: Markdown projection renderer with legacy-validator parity

**Files:**
- Modify: `scripts/route_manifest.py` (append)
- Create: `tests/unit/test_route_render.py`

**Interfaces:**
- Produces: `render_markdown(route, *, title, narrative=()) -> str` and `write_route_pair(sent_dir: Path, route, *, title, narrative=()) -> tuple[Path, Path]` (writes `<route_id>.md` + `<route_id>.route.json`).
- Consumes: `validate_route_object`, `route_hash`, `canonical_route_bytes` (Tasks 3-4); legacy `protocol_capacity.validate_route(root, wave, path)` as the parity oracle.

- [ ] **Step 1: Write failing tests `tests/unit/test_route_render.py`.** The green packet set mirrors `_write_capacity_split_cycle` in `tests/unit/test_protocol_capacity.py:58` (5 owners → G1 exactly-one coverage; single-pair phrases → G10):

```python
"""Renderer parity: the generated projection must satisfy the legacy validator."""
from __future__ import annotations

import json
from pathlib import Path

import protocol_capacity
import pytest

import route_manifest
from test_route_manifest import _route, _token


def _packet(**overrides) -> dict:
    base = {
        "id": "coord-capacity-split-route",
        "wave": 2,
        "cycle": "route-compat-cycle",
        "owner": "coordinator",
        "packet_type": "coordinator-route",
        "row_ids": ["row-a"],
        "allowed_paths": ["coordination/capacity/packets/", "coordination/mailbox/sent/"],
        "lock_keys": [],
        "dependencies": [],
        "acceptance": ["Route the current board."],
        "done_evidence": [],
        "handoff_artifact": None,
        "next_recipient": "coordinator",
        "status": "active",
        "verify_request": None,
        "target_commit": None,
        "commit_range": None,
        "scope_files": ["coordination/mailbox/sent/"],
    }
    base.update(overrides)
    return base


GREEN_PACKETS = [
    _packet(),
    _packet(
        id="director-capacity-split-chunk-a",
        owner="director",
        packet_type="director-implementation",
        allowed_paths=["src/chunk-a/"],
        scope_files=["src/chunk-a/"],
    ),
    _packet(
        id="operator-capacity-split-chunk-a",
        owner="operator",
        packet_type="operator-verification",
        status="blocked",
    ),
    _packet(
        id="director2-capacity-split-work",
        owner="director2",
        packet_type="director-preflight",
        status="blocked",
        allowed_paths=["docs/next-brief/"],
        acceptance=["Prepare bounded planning for the next brief."],
        scope_files=["docs/next-brief/"],
    ),
    _packet(
        id="operator2-capacity-split-work",
        owner="operator2",
        packet_type="operator-preflight",
        status="blocked",
        allowed_paths=["logs/preflight/"],
        acceptance=["Run bounded preflight selector discovery."],
        scope_files=["logs/preflight/"],
    ),
]


def _write_packets(root: Path) -> None:
    packet_dir = root / "coordination" / "capacity" / "packets"
    packet_dir.mkdir(parents=True, exist_ok=True)
    for packet in GREEN_PACKETS:
        (packet_dir / f"{packet['id']}.json").write_text(
            json.dumps(packet, indent=2), encoding="utf-8"
        )


NARRATIVE = (("Durable Disposition", "Generated projection for route-compat fixtures."),)


def _pair(tmp_path: Path, route: dict) -> Path:
    sent = tmp_path / "coordination" / "mailbox" / "sent"
    sent.mkdir(parents=True, exist_ok=True)
    md_path, _ = route_manifest.write_route_pair(
        sent, route, title="Coordinator → All: Route Compat Fixture", narrative=NARRATIVE
    )
    return md_path


def test_renderer_refuses_invalid_route(tmp_path):
    with pytest.raises(ValueError):
        route_manifest.render_markdown(
            _route(schema="governance.route/v2"), title="x"
        )


def test_rendered_projection_passes_legacy_validator(tmp_path):
    _write_packets(tmp_path)
    md_path = _pair(tmp_path, _route())
    result = protocol_capacity.validate_route(tmp_path, 2, md_path)
    assert result.valid, result.to_dict()


def test_rendered_projection_with_token_passes_legacy_validator(tmp_path):
    _write_packets(tmp_path)
    md_path = _pair(tmp_path, _route(side_effect_token=_token()))
    result = protocol_capacity.validate_route(tmp_path, 2, md_path)
    assert result.valid, result.to_dict()


def test_rendered_dual_pair_projection_passes_legacy_validator(tmp_path):
    _write_packets(tmp_path)
    # dual-pair G10 phrases require a director2 director-implementation packet
    packet_dir = tmp_path / "coordination" / "capacity" / "packets"
    packet = json.loads(
        (packet_dir / "director2-capacity-split-work.json").read_text(encoding="utf-8")
    )
    packet["packet_type"] = "director-implementation"
    packet["status"] = "active"
    (packet_dir / "director2-capacity-split-work.json").write_text(
        json.dumps(packet, indent=2), encoding="utf-8"
    )
    route = _route(
        capacity_split={
            "mode": "dual_pair",
            "chunk_a": ["director-capacity-split-chunk-a"],
            "chunk_b": ["director2-capacity-split-work"],
        }
    )
    md_path = _pair(tmp_path, route)
    result = protocol_capacity.validate_route(tmp_path, 2, md_path)
    assert result.valid, result.to_dict()


def test_pair_round_trips_through_read_manifest(tmp_path):
    _write_packets(tmp_path)
    md_path = _pair(tmp_path, _route())
    assert route_manifest.read_manifest(md_path) == _route()


def test_rendered_body_never_wraps_prohibition_lines(tmp_path):
    body = route_manifest.render_markdown(
        _route(prohibitions=list(route_manifest.PROHIBITION_VOCAB)),
        title="t",
        narrative=NARRATIVE,
    )
    rendered = [
        line for line in body.splitlines() if line.startswith("- No ")
    ]
    assert len(rendered) == len(route_manifest.PROHIBITION_VOCAB)
```

Run: `env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_route_render.py -q`
Expected: FAIL — `AttributeError: ... no attribute 'write_route_pair'`.

- [ ] **Step 2: Append renderer to `scripts/route_manifest.py`:**

```python
def render_markdown(
    route: dict,
    *,
    title: str,
    narrative: Sequence[tuple[str, str]] = (),
) -> str:
    """Generate the human projection. The object is the authority; this is a view.

    The output is engineered to satisfy the legacy prose validator
    (protocol_capacity._validate_route_file): task-board marker, full packet
    enumeration, capacity-split phrases, one-line prohibitions, dash-list
    side-effect token, join-condition line, terminal Exact Next Trigger.
    """
    issues = validate_route_object(route)
    if issues:
        raise ValueError("cannot render an invalid route object: " + "; ".join(issues))

    lines: list[str] = [f"# {title}", ""]
    lines.append(f"**When:** {route['created_at']} · **From:** {route['created_by']} (online)")
    lines.append("")
    lines.append("Event type: coordination")
    lines.append(f"Task-board: {route['task_board']}")
    if route["parent_route_id"]:
        lines.append(
            "Supersedes route: coordination/mailbox/sent/"
            f"{route['parent_route_id']}.md"
        )
    lines.append(f"Route generation: {route['generation']}")
    if route["expected_control_head"]:
        lines.append(f"Expected control HEAD: {route['expected_control_head']}")
    if route["target"]:
        if route["target"]["worktree"]:
            lines.append(f"Target worktree: {route['target']['worktree']}")
        lines.append(f"Target HEAD: {route['target']['base_commit']}")
    lines.append(f"Route manifest: {route['route_id']}.route.json")
    lines.append(f"route_hash: {route_hash(route)}")

    for heading, body in narrative:
        lines.extend(["", f"## {heading}", "", body])

    lines.extend(["", "## Capacity Split Default", ""])
    if route["capacity_split"]["mode"] == "single_pair":
        lines.append(
            "The single-pair fast path applies; the non-implementing pair holds "
            "bounded planning or preflight packets only. Coordinator owns convergence."
        )
    else:
        chunk_a = ", ".join(route["capacity_split"]["chunk_a"])
        chunk_b = ", ".join(route["capacity_split"]["chunk_b"])
        lines.append(
            "Dual-pair routing applies. "
            f"Chunk A: {chunk_a}. Chunk B: {chunk_b}. Coordinator owns convergence."
        )

    lines.extend(["", "## Capacity Packet Coverage", ""])
    lines.append(
        f"All {len(route['packet_refs'])} Wave-{route['wave']} packet IDs are named."
    )
    lines.append("")
    for packet_id in route["packet_refs"]:
        lines.append(f"- {packet_id}")

    if route["prohibitions"]:
        lines.extend(["", "## Prohibitions", ""])
        for key in route["prohibitions"]:
            lines.append(f"- {PROHIBITION_VOCAB[key]}")

    if route["side_effect_token"]:
        lines.extend(["", "## Side-Effect Executor Token", ""])
        for field in SIDE_EFFECT_TOKEN_FIELDS:
            lines.append(f"- {field}: {route['side_effect_token'][field]}")

    lines.extend(["", f"Join condition: {route['join_condition']}"])
    lines.extend(["", "## Exact Next Trigger", "", route["next_trigger"], ""])
    return "\n".join(lines) + "\n"


def write_route_pair(
    sent_dir: Path,
    route: dict,
    *,
    title: str,
    narrative: Sequence[tuple[str, str]] = (),
) -> tuple[Path, Path]:
    """Write <route_id>.md + <route_id>.route.json into sent_dir. Fail-closed."""
    body = render_markdown(route, title=title, narrative=narrative)
    md_path = sent_dir / f"{route['route_id']}.md"
    sidecar = sidecar_path(md_path)
    sidecar.write_bytes(canonical_route_bytes(route))
    md_path.write_text(body, encoding="utf-8")
    return md_path, sidecar
```

- [ ] **Step 3: Run: `env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_route_render.py tests/unit/test_route_manifest.py -q` — expect all PASS.** If a legacy-parity test fails, read the reported `route_issues` and adjust the RENDERER (never the legacy validator) until the projection satisfies it; record any adjustment in the commit body.

- [ ] **Step 4: Commit:**

```bash
env -u GIT_INDEX_FILE git log --oneline -5
env -u GIT_INDEX_FILE git commit -m "feat(route): markdown projection renderer with legacy-validator parity

verified via \$ .venv/bin/python -m pytest tests/unit/test_route_render.py -q -> all pass
Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>" -- scripts/route_manifest.py tests/unit/test_route_render.py
```

---

### Task 6: compatibility comparator + committed fixture corpus + logs artifact

**Files:**
- Create: `tests/fixtures/route_compat/packets/*.json` (the 5 GREEN packets from Task 5, written as files)
- Create: `tests/fixtures/route_compat/cases/<case>/route.json` (8 cases)
- Create: `tests/fixtures/route_compat/cases/<case>/projection.md` (hand-written prose for 5 cases)
- Create: `tests/fixtures/route_compat/expected.json`
- Create: `scripts/route_compat.py`
- Create: `tests/unit/test_route_compat.py`

**Interfaces:**
- Produces: `route_compat.run_corpus(fixtures_dir: Path) -> dict` (the report object) and CLI `python scripts/route_compat.py --fixtures tests/fixtures/route_compat --out logs/route-compat-report.json` (exit 0 iff every case matches `expected.json`).
- Consumes: `protocol_capacity.validate_route` (legacy oracle), `route_manifest` (Tasks 3-5).

**The 8 cases** (brief §11 deliverable 7, adapted to the audit findings). Every case has `route.json`; `projection.md` only where hand-written prose is the point. `divergence` names the *expected, triaged* legacy↔structured disagreement:

| case | legacy_valid | structured_valid | divergence |
|---|---|---|---|
| baseline-valid (rendered) | true | true | null |
| valid-with-token (rendered) | true | true | null |
| valid-explicit-prohibition (rendered, all 9 prohibitions) | true | true | null |
| wrapped-negative-prohibition (hand prose) | false | true | legacy-formatting-false-positive |
| wrapped-expected-phrase (hand prose) | false | true | legacy-formatting-false-positive |
| missing-side-effect-token (hand prose with a directive line, token absent) | false | true | narrative-directive-outside-manifest |
| subagent-authority-leakage (hand prose) | false | true | narrative-directive-outside-manifest |
| multi-executor-token (hand prose + invalid object) | false | false | null |
| route-outside-mailbox-boundary (rendered to `notes/`) | false | false | null |

(That is 9 rows — `route-outside-mailbox-boundary` uses `route_relpath` in `expected.json` to place the file outside `coordination/mailbox/sent/`.)

- [ ] **Step 1: Write the fixture corpus.** `packets/`: serialize the five `GREEN_PACKETS` dicts from Task 5 verbatim, one file per `id`. `cases/*/route.json`: start from the `_route()` baseline of Task 3 with per-case `route_id` stems (`2026-07-11T20-0N-00Z-coordinator-to-all-coordination`, N = case index) and these deltas — `valid-with-token`: `side_effect_token` = the `_token()` object; `valid-explicit-prohibition`: `prohibitions` = all 9 vocab keys; `multi-executor-token`: token with `"executor": "director and operator"`; all other cases: baseline. `expected.json`:

```json
{
  "baseline-valid": {"legacy_valid": true, "structured_valid": true, "divergence": null},
  "valid-with-token": {"legacy_valid": true, "structured_valid": true, "divergence": null},
  "valid-explicit-prohibition": {"legacy_valid": true, "structured_valid": true, "divergence": null},
  "wrapped-negative-prohibition": {"legacy_valid": false, "structured_valid": true, "divergence": "legacy-formatting-false-positive"},
  "wrapped-expected-phrase": {"legacy_valid": false, "structured_valid": true, "divergence": "legacy-formatting-false-positive"},
  "missing-side-effect-token": {"legacy_valid": false, "structured_valid": true, "divergence": "narrative-directive-outside-manifest"},
  "subagent-authority-leakage": {"legacy_valid": false, "structured_valid": true, "divergence": "narrative-directive-outside-manifest"},
  "multi-executor-token": {"legacy_valid": false, "structured_valid": false, "divergence": null},
  "route-outside-mailbox-boundary": {"legacy_valid": false, "structured_valid": false, "divergence": null, "route_relpath": "notes/2026-07-11T20-08-00Z-coordinator-to-all-coordination.md"}
}
```

Hand-written projections (complete bodies; each names all 5 packet ids, the task-board, single-pair phrases, join condition, and terminal trigger so the ONLY legacy failure is the case's defect):

`cases/wrapped-negative-prohibition/projection.md`:

```markdown
# Coordinator → All: Wrapped Prohibition Fixture

Task-board: route-compat-cycle

- coord-capacity-split-route
- director-capacity-split-chunk-a
- operator-capacity-split-chunk-a
- director2-capacity-split-work
- operator2-capacity-split-work

## Capacity Split Default

The single-pair fast path applies; the non-implementing pair holds bounded
planning or preflight packets only. Coordinator owns convergence.

## Prohibitions

No seat may execute a
push or remote-ref update in this cycle.

Join condition: coordinator closes after both pair lanes are accounted for.

## Exact Next Trigger

Director continues Chunk A; Pair B follows the capacity split decision.
```

(The wrap puts `push` + the directive verb on a line that no longer starts with "no " → the legacy per-line scan demands a token: the false positive under test.)

`cases/wrapped-expected-phrase/projection.md`: same skeleton, but the Capacity Split section reads:

```markdown
## Capacity Split Default

The single-pair fast
path applies; the non-implementing pair holds bounded planning or preflight
packets only. Coordinator owns convergence.
```

(`single-pair fast path` wrapped → G10 misses the phrase.)

`cases/missing-side-effect-token/projection.md`: baseline skeleton plus, before the join condition:

```markdown
## Publication Note

The director will push the release branch to origin after verification.
```

(directive + shared side-effect pattern, no token section → legacy demands a token; the structured object carries `side_effect_token: null` and no such directive — during compatibility the legacy lint remains the enforcer for free prose.)

`cases/subagent-authority-leakage/projection.md`: baseline skeleton plus:

```markdown
## Delegation Note

The director may dispatch subagents to send mailbox events for this cycle.
```

`cases/multi-executor-token/projection.md`: baseline skeleton plus the full 10-field token dash-list from Task 5's `_token()`, with the executor line replaced by `- executor: director and operator`.

- [ ] **Step 2: Write the failing test `tests/unit/test_route_compat.py`:**

```python
"""The committed comparator corpus must match expected.json exactly."""
from __future__ import annotations

from pathlib import Path

import route_compat

FIXTURES = Path(__file__).resolve().parent.parent / "fixtures" / "route_compat"


def test_corpus_matches_expectations(tmp_path):
    report = route_compat.run_corpus(FIXTURES)
    mismatches = [case for case in report["cases"] if not case["matches_expectation"]]
    assert report["all_match"], mismatches


def test_report_is_machine_readable(tmp_path):
    report = route_compat.run_corpus(FIXTURES)
    assert report["schema"] == "governance.route-compat-report/1"
    assert len(report["cases"]) == 9
    for case in report["cases"]:
        assert set(case) >= {
            "name", "legacy_valid", "legacy_gates", "structured_valid",
            "structured_issues", "divergence", "matches_expectation",
        }
```

Run: `env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_route_compat.py -q`
Expected: FAIL — `ModuleNotFoundError: No module named 'route_compat'`.

- [ ] **Step 3: Write `scripts/route_compat.py`:**

```python
#!/usr/bin/env python3
"""Legacy-vs-structured route verdict comparator (ADR-014, R-MEASURE instrument).

Runs the committed fixture corpus through BOTH the legacy prose validator
(protocol_capacity.validate_route) and the structured route/v1 validator, and
writes a machine-readable report. Exit 0 iff every case matches expected.json.
Divergences are pre-triaged in expected.json: legacy-formatting-false-positive
(the defect class route/v1 removes) and narrative-directive-outside-manifest
(free prose the legacy lint still governs during compatibility).
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
import tempfile
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
_SCRIPTS = _REPO_ROOT / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

import protocol_capacity  # noqa: E402
import route_manifest  # noqa: E402

WAVE = 2
NARRATIVE = (("Durable Disposition", "Generated projection for route-compat fixtures."),)
SENT_RELDIR = Path("coordination/mailbox/sent")


def _case_projection(case_dir: Path, route: dict, root: Path, relpath: str | None) -> Path:
    """Materialize the case's projection under root; return its path."""
    hand_written = case_dir / "projection.md"
    if relpath is not None:
        destination = root / relpath
    else:
        destination = root / SENT_RELDIR / f"{route['route_id']}.md"
    destination.parent.mkdir(parents=True, exist_ok=True)
    if hand_written.exists():
        destination.write_text(hand_written.read_text(encoding="utf-8"), encoding="utf-8")
    else:
        body = route_manifest.render_markdown(
            route, title="Coordinator → All: Route Compat Fixture", narrative=NARRATIVE
        )
        destination.write_text(body, encoding="utf-8")
        destination.with_suffix(".route.json").write_bytes(
            route_manifest.canonical_route_bytes(route)
        )
    return destination


def _structured_verdict(route: dict, projection: Path, root: Path) -> tuple[bool, list[str]]:
    issues = route_manifest.validate_route_object(route)
    relative = projection.resolve().as_posix()
    if f"/{SENT_RELDIR.as_posix()}/" not in relative:
        issues = [*issues, "route projection must live under coordination/mailbox/sent/"]
    return (not issues), issues


def run_corpus(fixtures_dir: Path) -> dict:
    expected = json.loads((fixtures_dir / "expected.json").read_text(encoding="utf-8"))
    cases = []
    for name in sorted(expected):
        spec = expected[name]
        case_dir = fixtures_dir / "cases" / name
        route = json.loads((case_dir / "route.json").read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            packet_dir = root / "coordination" / "capacity" / "packets"
            packet_dir.mkdir(parents=True)
            for packet_file in sorted((fixtures_dir / "packets").glob("*.json")):
                shutil.copy(packet_file, packet_dir / packet_file.name)
            projection = _case_projection(case_dir, route, root, spec.get("route_relpath"))
            legacy = protocol_capacity.validate_route(root, WAVE, projection)
            structured_valid, structured_issues = _structured_verdict(
                route, projection, root
            )
        # A rendered pair must also round-trip; hand-written prose has no pair.
        if not (case_dir / "projection.md").exists() and spec.get("route_relpath") is None:
            with tempfile.TemporaryDirectory() as tmp:
                sent = Path(tmp) / SENT_RELDIR
                sent.mkdir(parents=True)
                md_path, _ = route_manifest.write_route_pair(
                    sent, route, title="round-trip", narrative=NARRATIVE
                )
                assert route_manifest.read_manifest(md_path) == route
        case = {
            "name": name,
            "legacy_valid": legacy.valid,
            "legacy_gates": sorted(
                {issue.get("gate", "?") for issue in legacy.blocking_issues}
            ),
            "structured_valid": structured_valid,
            "structured_issues": structured_issues,
            "divergence": spec["divergence"],
            "matches_expectation": (
                legacy.valid == spec["legacy_valid"]
                and structured_valid == spec["structured_valid"]
            ),
        }
        cases.append(case)
    return {
        "schema": "governance.route-compat-report/1",
        "fixtures": str(fixtures_dir),
        "cases": cases,
        "all_match": all(case["matches_expectation"] for case in cases),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixtures", type=Path, default=Path("tests/fixtures/route_compat"))
    parser.add_argument("--out", type=Path, help="Write the JSON report here (logs/ artifact).")
    args = parser.parse_args(argv)
    report = run_corpus(args.fixtures)
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(rendered, encoding="utf-8")
    print(rendered)
    return 0 if report["all_match"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Run tests and iterate on fixture prose until expectations hold.** The hand-written cases pin LEGACY behavior — if a case does not produce the expected legacy verdict, fix the FIXTURE prose (e.g. strengthen the wrapped line), never the legacy validator. Cite the failing gate output in the commit body if a fixture needed adjustment.

Run: `env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_route_compat.py -q`
Expected: 2 passed.

- [ ] **Step 5: Produce the logs artifact with the committed instrument (R-MEASURE):**

```bash
env -u GIT_INDEX_FILE .venv/bin/python scripts/route_compat.py --out logs/route-compat-report.json
```

Expected: report printed; exit 0.

- [ ] **Step 6: Commit (include the artifact if `logs/` is tracked, as determined in Task 0):**

```bash
env -u GIT_INDEX_FILE git log --oneline -5
env -u GIT_INDEX_FILE git commit -m "feat(route): legacy-vs-structured comparator + 9-case fixture corpus

verified via \$ .venv/bin/python scripts/route_compat.py --out logs/route-compat-report.json -> all_match true, exit 0
Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>" -- scripts/route_compat.py tests/fixtures/route_compat/ tests/unit/test_route_compat.py logs/route-compat-report.json
```

---

### Task 7: formatting-invariance tests + legacy wrapped-negation xfail pin

**Files:**
- Create: `tests/unit/test_route_render_invariance.py`

**Interfaces:**
- Consumes: `route_manifest.write_route_pair` / `read_manifest` (Tasks 4-5), `protocol_capacity.validate_route`, and Task 5's `GREEN_PACKETS`/`_write_packets` helpers (import them from `test_route_render`).

- [ ] **Step 1: Write the tests** (deterministic mutations — the brief's property-based intent without the `hypothesis` dependency, per ADR-014 §7):

```python
"""Prose formatting must never change route authority (ADR-014).

Mutations run on the RENDERED projection only — the sidecar object is the
authority, so every benign mutant must (a) leave read_manifest output
byte-identical and (b) still satisfy the legacy validator. A mutation that
destroys the hash pin must fail CLOSED (RouteManifestError), never silently.
"""
from __future__ import annotations

import re
from pathlib import Path

import protocol_capacity
import pytest

import route_manifest
from test_route_manifest import _route
from test_route_render import NARRATIVE, _write_packets


def _pair(tmp_path: Path) -> Path:
    sent = tmp_path / "coordination" / "mailbox" / "sent"
    sent.mkdir(parents=True, exist_ok=True)
    md_path, _ = route_manifest.write_route_pair(
        sent, _route(), title="Coordinator → All: Invariance Fixture", narrative=NARRATIVE
    )
    return md_path


def _swap_bullets(body: str) -> str:
    return re.sub(r"(?m)^- ", "* ", body)


def _deepen_headings(body: str) -> str:
    return re.sub(r"(?m)^## ", "### ", body)


def _pad_blank_lines(body: str) -> str:
    return body.replace("\n\n", "\n\n\n")


def _add_trailing_whitespace(body: str) -> str:
    return "\n".join(line + "  " if line else line for line in body.splitlines()) + "\n"


BENIGN_MUTATIONS = [
    ("bullet-style", _swap_bullets),
    ("heading-depth", _deepen_headings),
    ("blank-padding", _pad_blank_lines),
    ("trailing-whitespace", _add_trailing_whitespace),
]


@pytest.mark.parametrize("name,mutate", BENIGN_MUTATIONS)
def test_benign_mutation_never_changes_authority(tmp_path, name, mutate):
    md_path = _pair(tmp_path)
    original = route_manifest.read_manifest(md_path)
    md_path.write_text(mutate(md_path.read_text(encoding="utf-8")), encoding="utf-8")
    assert route_manifest.read_manifest(md_path) == original


@pytest.mark.parametrize("name,mutate", BENIGN_MUTATIONS)
def test_benign_mutation_keeps_legacy_verdict(tmp_path, name, mutate):
    _write_packets(tmp_path)
    md_path = _pair(tmp_path)
    md_path.write_text(mutate(md_path.read_text(encoding="utf-8")), encoding="utf-8")
    result = protocol_capacity.validate_route(tmp_path, 2, md_path)
    assert result.valid, (name, result.to_dict())


def test_narrative_variants_share_one_hash(tmp_path):
    sent = tmp_path / "coordination" / "mailbox" / "sent"
    sent.mkdir(parents=True)
    md_a, _ = route_manifest.write_route_pair(
        sent, _route(), title="A", narrative=(("Note", "one line"),)
    )
    hash_a = route_manifest.HASH_LINE_RE.search(md_a.read_text(encoding="utf-8"))
    md_a.unlink()
    md_b, _ = route_manifest.write_route_pair(
        sent, _route(), title="A", narrative=(("Note", "a\nvery\nwrapped\nparagraph"),)
    )
    hash_b = route_manifest.HASH_LINE_RE.search(md_b.read_text(encoding="utf-8"))
    assert hash_a.group("digest") == hash_b.group("digest")


def test_destroyed_hash_pin_fails_closed(tmp_path):
    md_path = _pair(tmp_path)
    body = md_path.read_text(encoding="utf-8")
    md_path.write_text(
        route_manifest.HASH_LINE_RE.sub("route_hash: (redacted)", body), encoding="utf-8"
    )
    with pytest.raises(route_manifest.RouteManifestError):
        route_manifest.read_manifest(md_path)


@pytest.mark.xfail(
    strict=True,
    reason=(
        "Legacy per-line negation defect (protocol_capacity.py:1396-1448): a "
        "prohibition wrapped across lines is misread as a side-effect request. "
        "Not fixed in the prose parser by design — route/v1 typed prohibitions "
        "are the fix (ADR-014). Pinned per R-VERIFY-TIER; an XPASS means the "
        "legacy parser changed and this pin plus the route-compat expected.json "
        "row must be revisited together."
    ),
)
def test_legacy_validator_should_tolerate_wrapped_prohibition(tmp_path):
    _write_packets(tmp_path)
    md_path = _pair(tmp_path)
    body = md_path.read_text(encoding="utf-8")
    wrapped = body.replace(
        "- No push or remote-ref update by any seat in this cycle.",
        "- No seat may execute a\n  push or remote-ref update in this cycle.",
    )
    assert wrapped != body
    md_path.write_text(wrapped, encoding="utf-8")
    result = protocol_capacity.validate_route(tmp_path, 2, md_path)
    assert result.valid, result.to_dict()
```

- [ ] **Step 2: Run: `env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_route_render_invariance.py -q`**
Expected: 10 passed, 1 xfailed. If the xfail XPASSES, the legacy parser does not exhibit the defect in this exact shape — re-derive the wrap from the `wrapped-negative-prohibition` comparator case (which pins the same defect) and align both.

- [ ] **Step 3: Commit:**

```bash
env -u GIT_INDEX_FILE git log --oneline -5
env -u GIT_INDEX_FILE git commit -m "test(route): formatting-invariance suite + wrapped-negation strict xfail pin

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>" -- tests/unit/test_route_render_invariance.py
```

---

### Task 8: coordinator how-to + final full-gate verification

**Files:**
- Create: `docs/protocol/route-v1.md`

- [ ] **Step 1: Write `docs/protocol/route-v1.md`:**

```markdown
# route/v1 — typed route manifests (compatibility layer)

Status: compatibility-only (ADR-014). Markdown mailbox routes remain the live
authority; route/v1 pairs are generated alongside, compared, and never yet
consumed by live seats. Do not cut over without the follow-up ADR.

## What a coordinator does differently (today: nothing mandatory)

To EXPERIMENT with a typed route for a new cycle:

1. Build the object (all 18 fields; see `schemas/route-v1.schema.json`;
   `packet_delta` must be null, `capability_refs` must be []).
2. Validate + render the pair into a scratch directory:

       env -u GIT_INDEX_FILE .venv/bin/python - <<'EOF'
       import json, pathlib, sys
       sys.path.insert(0, "scripts"); sys.path.insert(0, ".")
       import route_manifest
       route = json.loads(pathlib.Path("my-route.json").read_text())
       issues = route_manifest.validate_route_object(route)
       if issues: raise SystemExit("\n".join(issues))
       out = pathlib.Path("/tmp/route-preview"); out.mkdir(parents=True, exist_ok=True)
       md, sidecar = route_manifest.write_route_pair(
           out, route, title="Coordinator → All: <cycle>")
       print(md, sidecar, sep="\n")
       EOF

3. Check the projection against the live validator:

       env -u GIT_INDEX_FILE .venv/bin/python scripts/protocol_capacity_board.py \
           --wave 2 --validate-route /tmp/route-preview/<route-id>.md

4. Run the comparator corpus after any change to route/v1 code:

       env -u GIT_INDEX_FILE .venv/bin/python scripts/route_compat.py \
           --out logs/route-compat-report.json

## Authority rules

- The sidecar `<route-id>.route.json` bytes are the canonical RFC 8785
  serialization; `route_hash:` in the .md pins them. Prose edits never change
  authority; breaking the pin fails closed (`RouteManifestError`).
- Unknown top-level fields are rejected; experimental data goes under
  `extensions`.
- `generation` / `parent_route_id` / `expected_control_head` are shape-checked
  but not yet CAS-enforced (that is Slice 2 / P0.3).
```

- [ ] **Step 2: Full-gate verification (R-EVIDENCE — paste outputs into the commit body):**

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit -q
env -u GIT_INDEX_FILE .venv/bin/python scripts/ci_smoke.py
env -u GIT_INDEX_FILE .venv/bin/python scripts/route_compat.py --out logs/route-compat-report.json
env -u GIT_INDEX_FILE git diff HEAD --stat
```

Expected: pytest ≈ 271 pre-existing + ~45 new tests, all pass (1 xfailed); smoke exit 0; comparator exit 0; the diff-stat shows ONLY the files this plan names.

- [ ] **Step 3: Commit docs, then request verification.** Per the pair contract, the loop closes on an operator (or Codex lane-v-verifier — the user prefers Codex as the independent cross-check) `verification-report` GO/NITS/FAIL over the full `BASE..HEAD` range of this plan's commits. NO push regardless of GO — push stays user-gated.

```bash
env -u GIT_INDEX_FILE git log --oneline -5
env -u GIT_INDEX_FILE git commit -m "docs(route): coordinator how-to for route/v1 manifests

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>" -- docs/protocol/route-v1.md
```

---

## Acceptance criteria (slice-level, from the brief §P0.1 as modified by the audit)

1. Reformatting Markdown cannot grant or remove authority — structurally guaranteed (authority lives in the sidecar; mutation suite proves it).
2. Machine decisions about a route/v1 pair come only from typed fields (`read_manifest` never consults prose beyond the hash pin).
3. The authority-bearing projection sections are reproducible from the canonical object; `title`/`narrative` are non-authority prose and can never change the route hash (`write_route_pair` round-trip + narrative-variants tests).
4. Canonical serialization + hashing are deterministic (RFC 8785 via the single repo canonicalizer; key-order test).
5. Legacy routes remain readable and authoritative — zero changes to `protocol_capacity.py`.
6. The compatibility report (`logs/route-compat-report.json`) triages every legacy↔structured divergence before any cutover discussion.
7. Malformed schemas, unknown fields, unsupported versions, and reserved-field misuse are rejected fail-closed with named issues.
8. The known legacy wrapped-negation defect is pinned (strict xfail) per R-VERIFY-TIER.

## Rollback

Compatibility-only: revert the slice's commits (all new files + one DECISIONS.md append + optional logs artifacts). No live route, packet, or validator behavior changed, so no migration to unwind.
