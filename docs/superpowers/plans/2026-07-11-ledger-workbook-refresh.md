# Evidence-Ledger Workbook Refresh Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add and execute a source-scoped, provenance-preserving refresh path for the updated internal workbook, then update the canonical local resource and produce one unified directional readout without duplicating history or overwriting later human/agency facts.

**Architecture:** A pure planner compares the previous workbook, incoming workbook, signed checklist, and a read-only database snapshot and emits one canonical hash-bound plan. A guarded database applier executes only typed actions with optimistic old-value checks and append-only evidence; a separate resource component stages, atomically activates, and restores the canonical workbook around the database commit. The existing cross-source measurement command renders the post-refresh direction so there is one interpretation surface.

**Tech Stack:** Python 3.11+, openpyxl, psycopg 3, PostgreSQL/Supabase migrations, pytest, existing hash-chained `trust.evidence`, local ignored `.superpowers/sdd/` and `data/` resources.

**Execution approval:** the user approved this specification and selected
routed subagent-driven execution (option 1) on 2026-07-11.

## Global Constraints

- Governing spec: `docs/superpowers/specs/2026-07-11-ledger-workbook-refresh-design.md` in Pipeline.
- Pipeline remains the governance kernel; all product code, migrations, and product docs land in `/Users/hyungkoookkim/evidence-ledger` through an explicit four-seat route.
- Evidence-ledger's default Codex posture is read-only verification. For this
  user-selected routed cycle, the Pipeline live Director is the single target
  controller/committer, fresh subagents are bounded implementers/reviewers
  under that Director, and the live Operator is the independent Codex verifier.
  This explicit mapping preserves the target's one-controller and
  R-CODEX-VERIFY contracts; it does not create a second target committer.
- At execution time, use `superpowers:using-git-worktrees` and create a new isolated evidence-ledger worktree from a freshly resolved published `origin/main`; do not reuse the stale normal checkout or an old task worktree.
- Run isolated-worktree Python through `/Users/hyungkoookkim/evidence-ledger/.venv/bin/python`; worktrees do not contain `.venv/`.
- Prefix every git and pytest command with `env -u GIT_INDEX_FILE`.
- Never commit real workbook bytes, real business figures, database dumps, credentials, or generated readouts. `data/`, `*.xlsx`, and `.superpowers/` remain ignored and must never be force-added.
- Use synthetic values only in tests and committed documentation.
- Source priority is fixed: later human evidence wins; the incoming workbook supersedes only prior internal `excel_import` facts; agency facts remain separate; database-only rows survive; database views own computed metrics.
- The workbook summary is a reconciliation control. Payment-month precedence is explicit `지급월`, then parseable `PPL비용지급일`; never fall back to broadcast month.
- Results remain immutable revisions. Result corrections must append through `biz.record_result` with `supersedes_id` and a reason.
- Slot and internal-PPL operational corrections require exact expected-old predicates and complete before/after facts in append-only refresh evidence.
- No SQL function or table mutation privilege is granted to `authenticated` or `anon`; the local import executor remains the only refresh writer.
- Every code task follows RED → GREEN → focused/full verification → commit. Do not amend failed attempts; land a bounded fix commit and re-review.
- Because this plan has more than five reviewable tasks, R-ORCH applies: fresh implementer per task, then fresh spec review and fresh code-quality review before the Director accepts that task.
- Do not run parallel implementers: Tasks 1–6 share the versioned plan contract and are sequential.
- Important verification and every real-data step require independent Operator/Codex verification. Gate banners do not replace executed tests.
- Separate executor tokens are required for worktree creation, local service
  start, synthetic test-database mutation, real-data scratch clone/apply,
  independent Operator scratch verification, and canonical database/resource
  activation.
- Push, remote publication, remote database mutation, paid services, and external deployment remain out of scope.
- Project priors that shape this plan: evidence-ledger design spec §4 data model and §5 structural trust fences; `docs/MANUAL.md` promises that results are revisioned, computed metrics are views, and imports are owner-gated.

---

## File And Interface Map

| File | Responsibility |
|---|---|
| `import/workbook_refresh.py` | Pure refresh models, workbook control extraction, canonical serialization, matching, classification, and blockers. No DB writes. |
| `import/workbook_refresh_db.py` | Read-only database snapshot plus explicit typed DB apply functions. No resource/filesystem activation. |
| `import/plan_workbook_refresh.py` | Read-only CLI that creates canonical JSON and a local human report. |
| `import/apply_workbook_refresh.py` | Guarded dry-run/apply CLI and transaction orchestration. |
| `import/workbook_resource.py` | Hashing, staging, archive, atomic activation, restoration, and ignored manifest. |
| `import/tests/make_refresh_fixture.py` | Synthetic previous/incoming workbook pair; never real values. |
| `import/tests/refresh_test_support.py` | Shared migrated scratch-DB context manager and synthetic refresh harness used only by refresh tests. |
| `import/tests/conftest.py` | Registers lazy `seeded_refresh` and `refresh_db` fixtures; performs no work until a refresh test requests one. |
| `import/tests/test_workbook_refresh_plan.py` | Pure planner and payment-month tests. |
| `import/tests/test_workbook_refresh_plan_cli.py` | Read-only DB snapshot/CLI tests. |
| `import/tests/test_workbook_refresh_apply.py` | Live scratch-DB apply, rollback, source-priority, and idempotence tests. |
| `import/tests/test_workbook_resource.py` | Filesystem activation and recovery tests. |
| `supabase/migrations/20260711000100_workbook_refresh_evidence.sql` | Extends allowed evidence kinds only; adds no client mutation surface. |
| `db/tests/test_workbook_refresh_evidence.py` | Evidence-kind, append-only, and grant-posture pins. |
| `import/measure_cross_source_reconciliation.py` | Existing single directional readout, extended with refresh evidence. |
| `tests/unit/test_measure_cross_source_reconciliation.py` | Synthetic direction/readout pins. |
| `DECISIONS.md` | Append-only ADR for source-scoped refresh and guarded operational corrections. |
| `ARCHITECTURE.md` | Verified module/write-path/trust-kind truth and measured test inventory. |
| `OPERATIONS.md` | Planner, dry-run, canonical activation, recovery, and troubleshooting commands. |
| `docs/MANUAL.md` | Korean owner-facing refresh and conflict/recovery procedure. |

### Versioned interfaces

The following names are load-bearing across tasks and must not drift:

```python
class RefreshBlocked(RuntimeError):
    pass


class RefreshApplyError(RuntimeError):
    pass


class ResourceActivationError(RuntimeError):
    pass


class CommitOutcomeUnknown(RuntimeError):
    pass


class Disposition(str, enum.Enum):
    UNCHANGED = "unchanged"
    INSERT_SLOT = "insert_slot"
    REVISE_SLOT = "revise_slot"
    SUPERSEDE_RESULT = "supersede_result"
    REVISE_PPL_PAYMENT = "revise_ppl_payment"
    REVISE_PPL_PLACEMENT = "revise_ppl_placement"
    REVISE_PPL_ALLOCATION = "revise_ppl_allocation"
    PRESERVE_DB_ONLY = "preserve_db_only"
    CONFLICT_HUMAN_NEWER = "conflict_human_newer"
    AMBIGUOUS_IDENTITY = "ambiguous_identity"
    QUARANTINE = "quarantine"


@dataclasses.dataclass(frozen=True)
class WorkbookFact:
    fact_id: str
    source_ref: str
    natural_key: tuple[str, str | None, str, str]
    slot: dict[str, object]
    result: dict[str, object] | None
    ppl: dict[str, object]
    controls: dict[str, object]


@dataclasses.dataclass(frozen=True)
class WorkbookSnapshot:
    workbook_file: str
    workbook_sha256: str
    year: int
    facts: tuple[WorkbookFact, ...]
    payment_summary: tuple[tuple[str, str], ...]
    anomalies: tuple[dict[str, object], ...]


@dataclasses.dataclass(frozen=True)
class DbSlotFact:
    id: int
    source: str
    source_ref: str | None
    entered_by: str
    slot: dict[str, object]
    latest_result: dict[str, object] | None


@dataclasses.dataclass(frozen=True)
class DatabaseSnapshot:
    previous_import_evidence_id: int
    previous_workbook_sha256: str
    evidence_chain_head: str
    slots: tuple[DbSlotFact, ...]
    payments: tuple[dict[str, object], ...]
    placements: tuple[dict[str, object], ...]
    allocations: tuple[dict[str, object], ...]


@dataclasses.dataclass(frozen=True)
class RefreshAction:
    disposition: Disposition
    fact_id: str
    target_kind: str
    target_id: int | None
    expected_before: dict[str, object]
    after: dict[str, object]
    reason: str


@dataclasses.dataclass(frozen=True)
class RefreshPlan:
    schema_version: int
    year: int
    previous_workbook_sha256: str
    incoming_workbook_sha256: str
    checklist_sha256: str
    database_fingerprint: str
    evidence_chain_head: str
    actions: tuple[RefreshAction, ...]
    blockers: tuple[str, ...]


@dataclasses.dataclass(frozen=True)
class AppliedAction:
    fact_id: str
    disposition: Disposition
    target_kind: str
    target_id: int
    expected_before: dict[str, object]
    actual_after: dict[str, object]


@dataclasses.dataclass(frozen=True)
class ApplyResult:
    plan_sha256: str
    entered_by: str
    applied: tuple[AppliedAction, ...]
    database_fingerprint_after: str
    dispositions: dict[str, int]
    directions: dict[str, str]
    report_hashes: dict[str, str]
    result_evidence_id: int | None
    result_evidence_chain_hash: str | None


@dataclasses.dataclass(frozen=True)
class EvidenceRef:
    id: int
    chain_hash: str


@dataclasses.dataclass(frozen=True)
class ResourceEvidence:
    state: str
    previous_sha256: str
    incoming_sha256: str
    archive_sha256: str | None
    staged_sha256: str | None
```

`schema_version` starts at `1`. Canonical JSON uses UTF-8, sorted keys,
compact separators, ISO dates/times, decimal strings, and a terminal newline.

`WorkbookFact.slot` uses exactly these keys: `broadcast_date`, `start_time`,
`channel`, `product`, `commission_model`, `sale_price`, `commission_rate`,
`vendor_fee_rate`, `set_cost`, `fixed_fee`, `target_amount`, `target_qty`,
`responsible_ko`, and `source_ref`. `result` is `None` or has `stage`,
`gross_amount`, `net_amount`, and `source_ref`; `DbSlotFact.latest_result`
adds database `id`, `source`, and provenance fields. `ppl` uses `show`,
`producer`, `amount`, `allocation`, `payment_month`, `placement_key`, and
`source_ref`. `controls` uses `payment_month_raw`, `payment_date_raw`, and
`unheaded_values`.

---

## Execution Preconditions: Coordinator Route And Isolation

Before Task 1 begins, the coordinator must:

- [ ] Refresh Pipeline HEAD, current mailbox bodies, capacity state, and the live evidence-ledger `origin/main` OID.
- [ ] Reconcile rather than overwrite the currently active control-plane cycle.
- [ ] Send one coordinator-to-all route naming this plan and spec, the new evidence-ledger worktree/base, disjoint packet IDs, allowed paths, forbidden side effects, review artifacts, and join condition.
- [ ] Name Director as the sole product executor; Operator owns cumulative Lane V; Director2 and Operator2 own bounded preflight only.
- [ ] Issue a worktree-creation executor token with an exact base/path/branch and clean postcheck.
- [ ] Unless the fresh state shows a collision, bind that token to local branch
  `codex/ledger-workbook-refresh-2026-07-11` and worktree
  `/Users/hyungkoookkim/Pipeline/.worktrees/evidence-ledger-workbook-refresh-2026-07-11`.
  A pre-existing branch/path is a stop condition, not reuse authority.
- [ ] Confirm the normal evidence-ledger `data/` paths remain outside the new worktree and are referenced by absolute path only during authorized local execution.
- [ ] In the new worktree, run target R-START before Task 1: project smoke,
  `ARCHITECTURE.md` §2 topology spot-check, `git log --oneline -20`, and a
  freshness comparison against the documented `Last verified` commit. Any
  stale claim touched by this work is corrected in Task 6 or an earlier
  bounded docs prep commit.

Expected route outcome: one implementation pair, one Pair-B preflight lane, no
database/resource mutation token yet, and no push authority.

---

### Task 1: Pure Workbook Snapshot And Classification Contract

**Files:**
- Create: `import/workbook_refresh.py`
- Create: `import/tests/make_refresh_fixture.py`
- Create: `import/tests/refresh_test_support.py`
- Create: `import/tests/test_workbook_refresh_plan.py`

**Interfaces:**
- Consumes: `parse_workbook.parse(path: pathlib.Path, year: int)`, signed `MergeRow` decisions, previous and incoming workbook paths.
- Produces: the exact shared models above (including `ApplyResult`,
  `EvidenceRef`, and `ResourceEvidence`), `parse_refresh_workbook()`,
  `build_refresh_plan()`, `canonical_plan_bytes()`, `plan_sha256()`,
  `database_fingerprint()`, and `blocking_actions()`.

- [ ] **Step 1: Add the synthetic previous/incoming workbook pair**

Create `make_refresh_fixture.py` with these exact helpers:

```python
def build_pair(
    previous: pathlib.Path,
    incoming: pathlib.Path,
    *,
    summary_mismatch: bool = False,
    unheaded_value: bool = False,
) -> tuple[pathlib.Path, pathlib.Path]:
    _write_refresh_workbook(
        previous,
        SYNTHETIC_PREVIOUS,
        summary_mismatch=False,
        unheaded_value=False,
    )
    _write_refresh_workbook(
        incoming,
        SYNTHETIC_INCOMING,
        summary_mismatch=summary_mismatch,
        unheaded_value=unheaded_value,
    )
    return previous, incoming


def signed_checklist() -> tuple[MergeRow, ...]:
    return tuple(
        MergeRow(entity_type, value, value, "KEEP", "synthetic")
        for entity_type, value in SYNTHETIC_ENTITY_VALUES
    )
```

`build_pair()` must construct and save both workbooks before returning. Create
`refresh_test_support.py` with:

```python
def database_from_previous(
    previous: WorkbookSnapshot,
    *,
    human_result: bool = False,
) -> DatabaseSnapshot:
    slots = []
    payments = []
    placements = []
    allocations = []
    for index, fact in enumerate(previous.facts, start=1):
        latest = None if fact.result is None else {
            **fact.result,
            "id": 1000 + index,
            "source": "form" if human_result and index == 1 else "excel_import",
        }
        slots.append(DbSlotFact(
            id=index,
            source="excel_import",
            source_ref=fact.source_ref,
            entered_by="synthetic-owner",
            slot=dict(fact.slot),
            latest_result=latest,
        ))
        if fact.ppl.get("amount") is not None:
            placements.append({
                "id": 2000 + index,
                "slot_id": index,
                **fact.ppl,
                "source": "excel_import",
            })
        if fact.ppl.get("allocation") is not None:
            allocations.append({
                "id": 3000 + index,
                "placement_id": 2000 + index,
                "slot_id": index,
                "amount": fact.ppl["allocation"],
                "source": "excel_import",
            })
    for index, (month, amount) in enumerate(previous.payment_summary, start=1):
        payments.append({
            "id": 4000 + index,
            "pay_month": month,
            "amount": amount,
            "source": "excel_import",
        })
    return DatabaseSnapshot(
        previous_import_evidence_id=1,
        previous_workbook_sha256=previous.workbook_sha256,
        evidence_chain_head="e" * 64,
        slots=tuple(slots),
        payments=tuple(payments),
        placements=tuple(placements),
        allocations=tuple(allocations),
    )


def build_inputs(
    tmp_path: pathlib.Path,
    *,
    human_result: bool = False,
    summary_mismatch: bool = False,
    unheaded_value: bool = False,
) -> tuple[WorkbookSnapshot, WorkbookSnapshot, tuple[MergeRow, ...], DatabaseSnapshot]:
    previous_path, incoming_path = build_pair(
        tmp_path / "previous.xlsx",
        tmp_path / "incoming.xlsx",
        summary_mismatch=summary_mismatch,
        unheaded_value=unheaded_value,
    )
    checklist = signed_checklist()
    previous = parse_refresh_workbook(previous_path, 2026, checklist)
    incoming = parse_refresh_workbook(incoming_path, 2026, checklist)
    return previous, incoming, checklist, database_from_previous(
        previous, human_result=human_result
    )
```

The helper has no production imports beyond Task-1 types and no DB access.
`_write_refresh_workbook()` uses `openpyxl`, the exact sheet names
`방송스케줄` and `PPL 지급 요약`, and `make_fixture.HEADER`; it writes the marker,
owner, header, detail, and summary rows before saving. The incoming workbook
must exercise:

```python
SYNTHETIC_PREVIOUS = [
    ("01/02(금)", "GS", "상품A", "반특", 100, 80, 10, "쇼A", "제작A", 20, "1월"),
    ("01/03(토)", "NS", "상품B", "정률", 200, 150, 15, "쇼B", "제작B", 30, "1월"),
]

SYNTHETIC_INCOMING = [
    ("01/01(목)", "KT", "상품C", "정률", 50, 40, 0, "", "", None, ""),
    ("01/02(금)", "GS", "상품A", "반특", 120, 90, 12, "쇼A", "제작A", 20, "1월"),
    ("01/03(토)", "NS", "상품B", "정률", 200, 150, 15, "쇼B", "제작B2", 30, "1월"),
]
```

Use only synthetic values. Put explicit `지급월` on one placement, a parseable
`PPL비용지급일` fallback on another, one nonempty unheaded `AG` cell, and a
summary mismatch variant selectable by a function argument.

- [ ] **Step 2: Write failing pure planner tests**

Add tests with these exact names and assertions:

```python
def test_shifted_source_rows_match_proven_baseline_not_row_number(tmp_path):
    previous, incoming, checklist, database = build_inputs(tmp_path)
    plan = build_refresh_plan(previous, incoming, database, checklist_sha256="c" * 64)
    dispositions = [a.disposition for a in plan.actions]
    assert Disposition.INSERT_SLOT in dispositions
    assert Disposition.REVISE_SLOT in dispositions
    assert Disposition.SUPERSEDE_RESULT in dispositions
    assert Disposition.AMBIGUOUS_IDENTITY not in dispositions


def test_later_human_result_conflict_blocks_plan(tmp_path):
    previous, incoming, checklist, database = build_inputs(tmp_path, human_result=True)
    plan = build_refresh_plan(previous, incoming, database, checklist_sha256="c" * 64)
    assert any(a.disposition is Disposition.CONFLICT_HUMAN_NEWER for a in plan.actions)
    assert blocking_actions(plan)


def test_payment_month_precedence_never_uses_broadcast_month():
    assert normalize_payment_month("2월", None, 2026) == datetime.date(2026, 2, 1)
    assert normalize_payment_month(None, "2026-03-17", 2026) == datetime.date(2026, 3, 1)
    assert normalize_payment_month(None, None, 2026) is None


def test_summary_mismatch_and_unheaded_value_are_quarantined(tmp_path):
    previous, incoming, checklist, database = build_inputs(
        tmp_path, summary_mismatch=True, unheaded_value=True
    )
    plan = build_refresh_plan(previous, incoming, database, checklist_sha256="c" * 64)
    reasons = [a.reason for a in plan.actions if a.disposition is Disposition.QUARANTINE]
    assert any("monthly-summary-mismatch" in reason for reason in reasons)
    assert any("unheaded-cell" in reason for reason in reasons)


def test_canonical_plan_bytes_and_hash_are_deterministic(tmp_path):
    previous, incoming, checklist, database = build_inputs(tmp_path)
    plan = build_refresh_plan(previous, incoming, database, checklist_sha256="c" * 64)
    assert plan.database_fingerprint == database_fingerprint(database)
    assert plan.evidence_chain_head == database.evidence_chain_head
    assert canonical_plan_bytes(plan).endswith(b"\n")
    assert canonical_plan_bytes(plan) == canonical_plan_bytes(plan)
    assert plan_sha256(plan) == hashlib.sha256(canonical_plan_bytes(plan)).hexdigest()
```

Add these table-driven pins in the same file:

- `test_each_internal_ppl_change_has_one_typed_disposition`: independently
  change payment, placement, and allocation fields and require exactly one of
  `REVISE_PPL_PAYMENT`, `REVISE_PPL_PLACEMENT`, or
  `REVISE_PPL_ALLOCATION` for the affected fact;
- `test_database_only_and_agency_rows_are_preserved`: append one synthetic
  DB-only internal row and one agency row to the snapshot and require
  `PRESERVE_DB_ONLY` with no mutable action targeting either row;
- `test_later_human_slot_and_ppl_facts_block_when_workbook_disagrees`:
  parameterize slot, payment, placement, and allocation snapshots with
  `source='form'`, change the incoming value, and require
  `CONFLICT_HUMAN_NEWER` plus a blocker for each target kind;
- `test_duplicate_identity_is_ambiguous_and_blocking`: duplicate a normalized
  incoming identity and require `AMBIGUOUS_IDENTITY` plus a blocker;
- `test_uncovered_checklist_variant_blocks_before_database_access`: add one
  new synthetic entity absent from the checklist and require a blocker without
  calling any DB helper.

- [ ] **Step 3: Run the tests to verify RED**

Run:

```bash
env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python \
  -m pytest import/tests/test_workbook_refresh_plan.py -q
```

Expected: collection fails because `workbook_refresh` and its interfaces do not
exist. A pre-existing failure elsewhere is not acceptable RED evidence.

- [ ] **Step 4: Implement the pure models, workbook controls, matching, and plan**

Create `workbook_refresh.py` with the exact enum/dataclasses above plus:

```python
BLOCKING = {
    Disposition.CONFLICT_HUMAN_NEWER,
    Disposition.AMBIGUOUS_IDENTITY,
    Disposition.QUARANTINE,
}


def canonical_plan_bytes(plan: RefreshPlan) -> bytes:
    payload = dataclasses.asdict(plan)
    return (json.dumps(payload, sort_keys=True, ensure_ascii=False,
                       separators=(",", ":"), default=_json_default) + "\n").encode()


def plan_sha256(plan: RefreshPlan) -> str:
    return hashlib.sha256(canonical_plan_bytes(plan)).hexdigest()


def blocking_actions(plan: RefreshPlan) -> tuple[RefreshAction, ...]:
    return tuple(a for a in plan.actions if a.disposition in BLOCKING)


def database_fingerprint(snapshot: DatabaseSnapshot) -> str:
    business_state = dataclasses.asdict(snapshot)
    del business_state["evidence_chain_head"]
    payload = json.dumps(
        business_state, sort_keys=True, ensure_ascii=False,
        separators=(",", ":"), default=_json_default,
    ).encode()
    return hashlib.sha256(payload).hexdigest()


def normalize_payment_month(explicit, payment_date, year: int) -> datetime.date | None:
    for value in (explicit, payment_date):
        if value in (None, ""):
            continue
        if isinstance(value, datetime.datetime):
            return value.date().replace(day=1)
        if isinstance(value, datetime.date):
            return value.replace(day=1)
        text = str(value).strip()
        month_match = re.fullmatch(r"(\d{1,2})월", text)
        if month_match:
            return datetime.date(year, int(month_match.group(1)), 1)
        try:
            return datetime.date.fromisoformat(text[:10]).replace(day=1)
        except ValueError:
            continue
    return None
```

`parse_refresh_workbook()` must call the existing pure parser, then open the
same workbook read-only/data-only to attach `PPL비용지급일`, `지급월`, and
nonempty unnamed cells to each emitted `source_ref`. It must not modify
`parse_workbook.py` or change one-time import behavior.

`build_refresh_plan()` must implement this deterministic order:

1. prove the previous workbook hash equals the snapshot/import-root hash;
2. map previous rows to `excel_import` DB rows by previous `source_ref` and
   verify canonical natural-key equality;
3. match previous to incoming rows by normalized `(date, time, channel,
   product)` identity;
4. when both unmatched-old and unmatched-new candidates exist, emit
   `ambiguous_identity` rather than guessing a key correction;
5. preserve DB rows not represented by the previous workbook;
6. emit typed slot/result/PPL actions only for workbook-owned facts;
7. emit `conflict_human_newer` when incoming facts disagree with a later
   `form` result;
8. group PPL before payment-month normalization, reject conflicting group
   months, and compare detail-derived monthly totals to the summary;
9. sort actions by `(disposition.value, fact_id, target_kind, target_id or -1)`;
10. derive `blockers` from the sorted blocking actions;
11. bind `database_fingerprint(database)` and the independently supplied
    `database.evidence_chain_head` into the immutable plan.

`database_fingerprint()` is intentionally a business-state fingerprint. It
includes the prior import identity plus slots, payments, placements, and
allocations, but excludes `evidence_chain_head`. The chain head is a separate
optimistic-concurrency gate because appending the plan/result evidence rows
changes it even when the business state is unchanged.

- [ ] **Step 5: Run focused and existing hermetic tests**

Run:

```bash
env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python \
  -m pytest import/tests/test_workbook_refresh_plan.py \
  import/tests/test_parse_workbook.py import/tests/test_propose_merges.py -q
```

Expected: PASS with no real workbook access and no DB connection.

- [ ] **Step 6: Commit Task 1**

```bash
env -u GIT_INDEX_FILE git add \
  import/workbook_refresh.py \
  import/tests/make_refresh_fixture.py \
  import/tests/refresh_test_support.py \
  import/tests/test_workbook_refresh_plan.py
env -u GIT_INDEX_FILE git commit -m "feat(import): plan workbook refreshes deterministically"
```

After commit: fresh spec review, then fresh quality review. Fix findings in a
new commit and rerun Step 5 before Task 2.

---

### Task 2: Read-Only Database Snapshot And Planning CLI

Before running the new DB-backed fixture, obtain the target-bound synthetic
scratch-database token. It names Director as sole executor, UUID database name
pattern, localhost DSN, migration command class, forced-drop cleanup, and
synthetic-only restriction. If the local stack is not already healthy, obtain
the separate local-service-start token first. Neither token permits the
canonical database or resource paths.

**Files:**
- Create: `import/workbook_refresh_db.py`
- Create: `import/plan_workbook_refresh.py`
- Create: `import/tests/conftest.py`
- Create: `import/tests/test_workbook_refresh_plan_cli.py`
- Modify: `import/tests/refresh_test_support.py`

**Interfaces:**
- Consumes: Task-1 models, `database_fingerprint()`, and `build_refresh_plan()`.
- Produces: `fetch_database_snapshot(conn, previous_workbook_sha256, year) -> DatabaseSnapshot`, `write_plan_outputs(plan, json_path, report_path)`, and read-only `main(argv=None)`.

- [ ] **Step 1: Add one reusable migrated scratch-DB harness**

Extend `refresh_test_support.py` with:

```python
@dataclasses.dataclass
class SeededRefresh:
    name: str
    dsn: str
    conn: psycopg.Connection
    tmp_path: pathlib.Path
    previous: pathlib.Path
    incoming: pathlib.Path
    unbound_previous: pathlib.Path
    checklist: pathlib.Path
    previous_sha256: str

    def plan_args(
        self,
        json_path: pathlib.Path | None = None,
        report_path: pathlib.Path | None = None,
        *,
        previous_workbook: pathlib.Path | None = None,
    ) -> list[str]:
        json_path = json_path or self.tmp_path / "refresh.plan.json"
        report_path = report_path or self.tmp_path / "refresh.plan.md"
        return [
            "--previous-workbook", str(previous_workbook or self.previous),
            "--incoming-workbook", str(self.incoming),
            "--year", "2026",
            "--checklist", str(self.checklist),
            "--dsn", self.dsn,
            "--out-json", str(json_path),
            "--out-report", str(report_path),
        ]
```

`seeded_refresh_context(tmp_path, monkeypatch)` must use the existing
UUID-database pattern from `test_import_end_to_end.py`: create the database,
install auth helpers, apply every sorted migration, build the synthetic pair,
run the existing one-time importer on the previous workbook with a fully
decided synthetic checklist, open one non-autocommit connection, and yield the
model above. In `finally`, close the connection and `DROP DATABASE ... WITH
(FORCE)`. Create `unbound_previous` by copying the previous workbook, changing
one synthetic cell, and saving it so its hash has no `import_root` row.

Register it lazily in `import/tests/conftest.py`:

```python
@pytest.fixture()
def seeded_refresh(tmp_path, monkeypatch):
    with seeded_refresh_context(tmp_path, monkeypatch) as harness:
        yield harness
```

The context manager is the only new place that owns database creation/drop;
the fixture module performs no work at import time.

- [ ] **Step 2: Write failing snapshot and CLI tests**

Add these exact cases:

```python
def test_fetch_snapshot_binds_previous_import_root_and_latest_results(seeded_refresh):
    snapshot = fetch_database_snapshot(
        seeded_refresh.conn, seeded_refresh.previous_sha256, 2026
    )
    assert snapshot.previous_workbook_sha256 == seeded_refresh.previous_sha256
    assert snapshot.previous_import_evidence_id > 0
    assert snapshot.evidence_chain_head
    assert all(slot.latest_result is None or slot.latest_result["id"] for slot in snapshot.slots)


def test_plan_cli_is_read_only_and_writes_hash_bound_outputs(
    seeded_refresh, tmp_path
):
    snapshot_before = fetch_database_snapshot(
        seeded_refresh.conn, seeded_refresh.previous_sha256, 2026
    )
    before = database_fingerprint(snapshot_before)
    json_path = tmp_path / "refresh.plan.json"
    report_path = tmp_path / "refresh.plan.md"
    rc = main(seeded_refresh.plan_args(json_path, report_path))
    snapshot_after = fetch_database_snapshot(
        seeded_refresh.conn, seeded_refresh.previous_sha256, 2026
    )
    after = database_fingerprint(snapshot_after)
    assert rc == 0
    assert before == after
    assert snapshot_before.evidence_chain_head == snapshot_after.evidence_chain_head
    assert json.loads(json_path.read_text())["schema_version"] == 1
    assert "Plan SHA-256" in report_path.read_text()


def test_plan_cli_refuses_unbound_previous_workbook(seeded_refresh):
    with pytest.raises(RefreshBlocked, match="previous-import-root-not-found"):
        main(seeded_refresh.plan_args(previous_workbook=seeded_refresh.unbound_previous))
```

- [ ] **Step 3: Run the focused tests to verify RED**

```bash
env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python \
  -m pytest import/tests/test_workbook_refresh_plan_cli.py -q
```

Expected: FAIL because the DB snapshot and CLI modules do not exist.

- [ ] **Step 4: Implement the read-only snapshot queries**

Create `workbook_refresh_db.py`. `fetch_database_snapshot()` must execute only
SELECT statements and return canonical order. Use these query shapes:

```sql
SELECT id, payload->>'workbook_sha256', chain_hash
FROM trust.evidence
WHERE kind = 'import_root'
  AND payload->>'workbook_sha256' = %s
  AND (payload->>'year')::int = %s
ORDER BY id DESC
LIMIT 1;

SELECT s.id, s.broadcast_date::text, s.start_time::text,
       c.code, p.name_ko, s.commission_model,
       s.sale_price, s.commission_rate, s.vendor_fee_rate, s.set_cost,
       s.fixed_fee, s.target_amount, s.target_qty, s.responsible_ko,
       s.source, s.source_ref, s.entered_by, s.created_at::text,
       r.id, r.stage, r.gross_amount, r.net_amount, r.source,
       r.source_ref, r.entered_by, r.supersedes_id, r.reason,
       r.entered_at::text
FROM biz.broadcast_slots s
JOIN biz.channels c ON c.id = s.channel_id
JOIN biz.products p ON p.id = s.product_id
LEFT JOIN biz.latest_results r ON r.slot_id = s.id
ORDER BY s.id;

SELECT id, pay_month::text, amount, source, source_ref, entered_by,
       created_at::text
FROM biz.ppl_payments ORDER BY id;

SELECT pl.id, tv.name_ko, pr.name_ko, pl.amount, pl.period_month::text,
       pl.payment_status_ko, pl.source, pl.source_ref, pl.entered_by,
       pl.created_at::text
FROM biz.ppl_placements pl
JOIN biz.tv_shows tv ON tv.id = pl.tv_show_id
LEFT JOIN biz.producers pr ON pr.id = pl.producer_id
ORDER BY pl.id;

SELECT id, placement_id, slot_id, amount, method, method_reason,
       source, source_ref, entered_by, created_at::text
FROM biz.ppl_allocations ORDER BY id;
```

Also select the current evidence-chain head independently. Return it on the
snapshot, but let the Task-1 `database_fingerprint()` hash only the documented
business-state projection; neither the fingerprint nor the separate chain-head
gate includes transient connection state.

- [ ] **Step 5: Implement the read-only CLI and report**

`plan_workbook_refresh.py` arguments are exact and all required except DSN:

```text
--previous-workbook PATH
--incoming-workbook PATH
--year INT
--checklist PATH
--dsn DSN
--out-json PATH
--out-report PATH
```

Open the DB with a read-only transaction:

```python
with psycopg.connect(args.dsn, options="-c default_transaction_read_only=on") as conn:
    snapshot = fetch_database_snapshot(conn, previous_sha, args.year)
    plan = build_refresh_plan(previous, incoming, snapshot, checklist_sha)
```

Write canonical JSON verbatim from `canonical_plan_bytes(plan)`. The Markdown
report includes plan hash, workbook/checklist/database hashes, disposition
names and counts, and blocker reasons, but no business amounts. Exit nonzero
when `blocking_actions(plan)` is nonempty; still write the local report for
owner review.

- [ ] **Step 6: Run focused and full import suites**

```bash
env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python \
  -m pytest import/tests/test_workbook_refresh_plan.py \
  import/tests/test_workbook_refresh_plan_cli.py -q
env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python \
  -m pytest import/tests -q
```

Expected: both commands PASS; plan CLI tests prove the DB fingerprint is
unchanged.

- [ ] **Step 7: Commit Task 2**

```bash
env -u GIT_INDEX_FILE git add \
  import/workbook_refresh_db.py \
  import/plan_workbook_refresh.py \
  import/tests/conftest.py \
  import/tests/refresh_test_support.py \
  import/tests/test_workbook_refresh_plan_cli.py
env -u GIT_INDEX_FILE git commit -m "feat(import): add read-only workbook refresh plans"
```

After commit: fresh spec review, then fresh quality review. Fix and re-run Step
6 before Task 3.

---

### Task 3: Evidence-Bound Guarded Database Apply

**Files:**
- Create: `supabase/migrations/20260711000100_workbook_refresh_evidence.sql`
- Create: `db/tests/test_workbook_refresh_evidence.py`
- Create: `import/apply_workbook_refresh.py`
- Create: `import/tests/test_workbook_refresh_apply.py`
- Modify: `import/workbook_refresh_db.py`
- Modify: `import/tests/conftest.py`
- Modify: `import/tests/refresh_test_support.py`

**Interfaces:**
- Consumes: canonical `RefreshPlan`, `fetch_database_snapshot()`, existing `biz.record_slot`, existing `biz.record_result`, `ResourceEvidence`, output paths, and the `trust.evidence` chain.
- Produces: `ApplyResult`, `apply_refresh(conn, plan, entered_by, resource_evidence, result_json_path, result_report_path)`, `append_refresh_evidence()`, `write_apply_outputs()`, and a rollback-only `--dry-run` CLI mode. Canonical `--apply` is added only after Task 4 can keep the DB and resource aligned.

Extend the shared test support with these exact public helpers:

```python
@dataclasses.dataclass(frozen=True)
class RefreshCounts:
    slots: int
    results: int
    payments: int
    placements: int
    allocations: int
    evidence: int


@dataclasses.dataclass
class RefreshDbHarness:
    seeded: SeededRefresh
    plan: RefreshPlan

    @property
    def conn(self):
        return self.seeded.conn
```

Add methods named `counts`, `fingerprint`, `latest_result_reason`,
`agency_rows`, `internal_values`, `expected_incoming_values`, and
`change_one_expected_old_value`. Their bodies use fixed, explicit
SELECT/UPDATE statements: counts query
the five `biz` tables plus `trust.evidence`; `fingerprint()` delegates to
`fetch_database_snapshot()` and `database_fingerprint()`; result reason reads
the newest revision; agency/internal helpers return canonical ordered tuples;
and `change_one_expected_old_value()` changes one synthetic
`excel_import`-owned field named in the plan. Do not add a generic SQL
executor.

In `conftest.py`, add `refresh_db(seeded_refresh)`: parse both workbooks, read
the signed checklist, fetch the live snapshot, build the plan, seed one
synthetic agency-only reconciliation row before the snapshot, and return
`RefreshDbHarness`. Its finalizer rolls back any open transaction; database
drop remains owned by `seeded_refresh_context()`.

- [ ] **Step 1: Write the migration and grant-posture tests first**

Create failing tests that assert:

```python
@pytest.mark.parametrize("kind", ["workbook_refresh_plan", "workbook_refresh_result"])
def test_refresh_evidence_kinds_are_allowed_and_hash_chained(db, kind):
    row = db.execute(
        "INSERT INTO trust.evidence(kind,payload,content_sha256) "
        "VALUES (%s,'{}','ignored') RETURNING content_sha256,chain_hash",
        (kind,),
    ).fetchone()
    assert len(row[0]) == 64
    assert len(row[1]) == 64


def test_unknown_evidence_kind_still_fails(db):
    with pytest.raises(psycopg.errors.CheckViolation):
        db.execute(
            "INSERT INTO trust.evidence(kind,payload,content_sha256) "
            "VALUES ('refresh_unknown','{}','ignored')"
        )


def test_refresh_migration_adds_no_authenticated_write_surface(db):
    db.execute("SET ROLE authenticated")
    try:
        with pytest.raises(psycopg.errors.InsufficientPrivilege):
            db.execute(
                "INSERT INTO trust.evidence(kind,payload,content_sha256) "
                "VALUES ('workbook_refresh_plan','{}','ignored')"
            )
    finally:
        db.execute("RESET ROLE")
```

- [ ] **Step 2: Write failing apply tests**

Pin these exact behaviors using a synthetic prior import and Task-2 plan:

```python
def apply_synthetic(refresh_db):
    return apply_refresh(
        refresh_db.conn,
        refresh_db.plan,
        entered_by="owner-test",
        resource_evidence=ResourceEvidence(
            state="synthetic-test",
            previous_sha256=refresh_db.plan.previous_workbook_sha256,
            incoming_sha256=refresh_db.plan.incoming_workbook_sha256,
            archive_sha256=None,
            staged_sha256=None,
        ),
        result_json_path=refresh_db.seeded.tmp_path / "apply.result.json",
        result_report_path=refresh_db.seeded.tmp_path / "apply.result.md",
    )


def test_apply_inserts_only_new_slot_and_supersedes_changed_result(refresh_db):
    before = refresh_db.counts()
    result = apply_synthetic(refresh_db)
    after = refresh_db.counts()
    assert after.slots == before.slots + 1
    assert after.results == before.results + 2
    assert result.plan_sha256 == plan_sha256(refresh_db.plan)
    assert result.result_evidence_id is not None
    assert result.result_evidence_chain_hash is not None
    assert len(result.result_evidence_chain_hash) == 64
    assert set(result.report_hashes) == {"apply.result.json", "apply.result.md"}
    assert refresh_db.latest_result_reason() == "workbook refresh"


def test_apply_updates_only_expected_internal_slot_and_ppl_values(refresh_db):
    agency_before = refresh_db.agency_rows()
    apply_synthetic(refresh_db)
    assert refresh_db.internal_values() == refresh_db.expected_incoming_values()
    assert refresh_db.agency_rows() == agency_before


def test_optimistic_old_value_mismatch_rolls_back_all_writes(refresh_db):
    refresh_db.change_one_expected_old_value()
    before = refresh_db.fingerprint()
    with pytest.raises(RefreshApplyError, match="expected-old-mismatch"):
        apply_synthetic(refresh_db)
    refresh_db.conn.rollback()
    assert refresh_db.fingerprint() == before


def test_same_workbook_plan_cannot_apply_twice(refresh_db):
    apply_synthetic(refresh_db)
    refresh_db.conn.commit()
    with pytest.raises(RefreshApplyError, match="already-applied"):
        apply_synthetic(refresh_db)


def test_evidence_chain_head_change_rejects_stale_plan(refresh_db):
    append_refresh_evidence(
        refresh_db.conn,
        "workbook_refresh_plan",
        {"test_only": "advance-chain-head"},
    )
    with pytest.raises(RefreshApplyError, match="evidence-chain-head-changed"):
        apply_synthetic(refresh_db)


def test_refresh_evidence_contains_complete_before_after_and_hashes(refresh_db):
    result = apply_synthetic(refresh_db)
    payload = refresh_db.conn.execute(
        "SELECT payload FROM trust.evidence WHERE id=%s",
        (result.result_evidence_id,),
    ).fetchone()[0]
    assert payload["plan_sha256"] == plan_sha256(refresh_db.plan)
    assert len(payload["actions"]) == len(refresh_db.plan.actions)
    for stored, action in zip(payload["actions"], refresh_db.plan.actions, strict=True):
        assert stored["fact_id"] == action.fact_id
        assert stored["expected_before"] == action.expected_before
        assert all(stored["actual_after"][key] == value for key, value in action.after.items())
    assert payload["resource"]["incoming_sha256"] == refresh_db.plan.incoming_workbook_sha256
    assert set(payload["report_hashes"]) == {"apply.result.json", "apply.result.md"}
    assert payload["expected_evidence_chain_head"] == refresh_db.plan.evidence_chain_head
    assert len(payload["plan_evidence"]["chain_hash"]) == 64
```

- [ ] **Step 3: Run RED for DB and apply tests**

```bash
env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python \
  -m pytest db/tests/test_workbook_refresh_evidence.py \
  import/tests/test_workbook_refresh_apply.py -q
```

Expected: migration tests reject the new kinds and apply-module collection
fails. Both failures must be attributable to this task.

- [ ] **Step 4: Add the evidence-kind migration**

Use this exact DDL and no grants/functions:

```sql
alter table trust.evidence drop constraint evidence_kind_check;

alter table trust.evidence add constraint evidence_kind_check check (kind in (
  'import_root',
  'merge_checklist',
  'import_report',
  'reconciliation_report',
  'workbook_refresh_plan',
  'workbook_refresh_result'
));
```

R-SCOPE disposition: the existing RLS policy, authenticated SELECT grant, and
authenticated/anon write revokes remain unchanged; `db/tests/test_rls_grants.py`
continues to prove the sibling fence.

- [ ] **Step 5: Implement typed apply functions without arbitrary SQL**

Before editing, capture Rule #12 and Rule #13 evidence with:

```bash
env -u GIT_INDEX_FILE rg -n \
  "record_slot|record_result|insert into biz\\.(broadcast_slots|broadcast_results|ppl_)|update biz\\.(broadcast_slots|ppl_)" \
  import supabase/migrations
env -u GIT_INDEX_FILE rg -n \
  "agency_excel_import|source='excel_import'|source = 'excel_import'" \
  import supabase/migrations
```

Disposition every sibling writer in the Task-3 review artifact:

- `run_import.py`/`load_staging.py`: unchanged one-time append path, never
  selected for cumulative refresh;
- `load_agency.py`: exempt and protected by its distinct agency source;
- `biz.record_slot` and `biz.record_result`: mirror/reuse for inserts and
  immutable result revisions;
- authenticated client grants: documented no-new-write-surface;
- the local typed update helpers: sole new operational correction path,
  guarded by source, target ID, all old mutable values, lock, and evidence.

Extend `workbook_refresh_db.py` with explicit functions for each mutable
target. Do not interpolate table or column names from the plan.

```python
def _apply_slot_revision(conn, action: RefreshAction, entered_by: str) -> int:
    before = action.expected_before
    after = action.after
    row = conn.execute(
        """UPDATE biz.broadcast_slots
              SET commission_model=%s, sale_price=%s, commission_rate=%s,
                  vendor_fee_rate=%s, set_cost=%s, fixed_fee=%s,
                  target_amount=%s, target_qty=%s, responsible_ko=%s,
                  source_ref=%s, entered_by=%s
            WHERE id=%s AND source='excel_import'
              AND commission_model IS NOT DISTINCT FROM %s
              AND sale_price IS NOT DISTINCT FROM %s
              AND commission_rate IS NOT DISTINCT FROM %s
              AND vendor_fee_rate IS NOT DISTINCT FROM %s
              AND set_cost IS NOT DISTINCT FROM %s
              AND fixed_fee IS NOT DISTINCT FROM %s
              AND target_amount IS NOT DISTINCT FROM %s
              AND target_qty IS NOT DISTINCT FROM %s
              AND responsible_ko IS NOT DISTINCT FROM %s
              AND source_ref IS NOT DISTINCT FROM %s
              AND entered_by IS NOT DISTINCT FROM %s
          RETURNING id""",
        (
            after["commission_model"], after["sale_price"], after["commission_rate"],
            after["vendor_fee_rate"], after["set_cost"], after["fixed_fee"],
            after["target_amount"], after["target_qty"], after["responsible_ko"],
            after["source_ref"], entered_by, action.target_id,
            before["commission_model"], before["sale_price"], before["commission_rate"],
            before["vendor_fee_rate"], before["set_cost"], before["fixed_fee"],
            before["target_amount"], before["target_qty"], before["responsible_ko"],
            before["source_ref"], before["entered_by"],
        ),
    ).fetchone()
    if row is None:
        raise RefreshApplyError(f"expected-old-mismatch:slot:{action.target_id}")
    return row[0]
```

Add equally explicit `_apply_payment_revision`, `_apply_placement_revision`,
and `_apply_allocation_revision` with `source='excel_import'`, target ID, and
all mutable old values including `source_ref` and `entered_by` in the WHERE
clause. Each writes the command's `entered_by` identity and incoming
`source_ref`; no agency source can satisfy the predicate.

For `INSERT_SLOT`, call `biz.record_slot`. For `SUPERSEDE_RESULT`, reselect the
current `latest_results` head, require it equals `expected_before['id']`, then
call `biz.record_result` with `supersedes_id`, `reason='workbook refresh'`,
`source='excel_import'`, and the incoming source reference.
Every `_apply_action()` then reselects the written row and returns an
`AppliedAction` with the complete expected-before and actual-after row,
including source provenance and the command's `entered_by` identity.

- [ ] **Step 6: Implement transaction gates and the rollback-only CLI**

Add `fetch_direction_metrics(conn, year)` with two fixed aggregate queries:
`biz.slot_pnl` supplies year-bounded gross, net, and operating-profit totals;
`biz.ppl_monthly` supplies year-bounded internal paid and internal allocation
totals. Agency columns are read separately for preservation checks and never
enter those internal totals. `classify_direction(before, after)` returns only
`up`, `down`, `flat`, or `not_comparable`.

`apply_refresh()` order is exact:

```python
def apply_refresh(
    conn,
    plan: RefreshPlan,
    entered_by: str,
    resource_evidence: ResourceEvidence,
    result_json_path: pathlib.Path,
    result_report_path: pathlib.Path,
) -> ApplyResult:
    if plan.blockers or blocking_actions(plan):
        raise RefreshApplyError("plan-has-blockers")
    if resource_evidence.previous_sha256 != plan.previous_workbook_sha256:
        raise RefreshApplyError("previous-resource-hash-mismatch")
    if resource_evidence.incoming_sha256 != plan.incoming_workbook_sha256:
        raise RefreshApplyError("incoming-resource-hash-mismatch")
    conn.execute(
        "SELECT pg_advisory_xact_lock(hashtextextended(%s, 0))",
        (f"workbook_refresh:{plan.year}",),
    )
    if _refresh_already_applied(conn, plan.incoming_workbook_sha256):
        raise RefreshApplyError("already-applied")
    current = fetch_database_snapshot(conn, plan.previous_workbook_sha256, plan.year)
    if current.evidence_chain_head != plan.evidence_chain_head:
        raise RefreshApplyError("evidence-chain-head-changed")
    if database_fingerprint(current) != plan.database_fingerprint:
        raise RefreshApplyError("database-fingerprint-changed")
    metrics_before = fetch_direction_metrics(conn, plan.year)
    plan_evidence = append_refresh_evidence(
        conn, "workbook_refresh_plan", plan_evidence_payload(plan)
    )
    applied = tuple(_apply_action(conn, action, entered_by) for action in plan.actions)
    after_snapshot = fetch_database_snapshot(
        conn, plan.previous_workbook_sha256, plan.year
    )
    metrics_after = fetch_direction_metrics(conn, plan.year)
    result = ApplyResult(
        plan_sha256=plan_sha256(plan),
        entered_by=entered_by,
        applied=applied,
        database_fingerprint_after=database_fingerprint(after_snapshot),
        dispositions=count_dispositions(plan.actions),
        directions=classify_directions(metrics_before, metrics_after),
        report_hashes={},
        result_evidence_id=None,
        result_evidence_chain_hash=None,
    )
    report_hashes = write_apply_outputs(
        result, result_json_path, result_report_path
    )
    result = dataclasses.replace(result, report_hashes=report_hashes)
    result_evidence = append_refresh_evidence(
        conn,
        "workbook_refresh_result",
        result_evidence_payload(
            plan, result, resource_evidence, plan_evidence
        ),
    )
    return dataclasses.replace(
        result,
        result_evidence_id=result_evidence.id,
        result_evidence_chain_hash=result_evidence.chain_hash,
    )
```

`append_refresh_evidence()` returns `EvidenceRef(id, chain_hash)` from the
inserted row. `write_apply_outputs()` serializes a documented pre-evidence
projection that excludes `report_hashes`, `result_evidence_id`, and
`result_evidence_chain_hash`; it then hashes those immutable bytes and returns
the two hashes. This avoids a self-referential file-hash contract. The returned
`ApplyResult`, result evidence payload, and resource manifest carry the hashes
and final evidence reference without rewriting either attested output file.
`plan_evidence_payload()` stores the canonical plan hash and complete action
facts. `result_evidence_payload()` stores year, previous/incoming workbook
hashes, both DB fingerprints, every action's disposition/fact/target and
complete expected-before/after values, result/report hashes, resource
attestation, direction labels, the expected pre-apply evidence-chain head, and
the plan-evidence ID/chain-hash linkage. It necessarily excludes the result
row's own ID and chain hash. The
local JSON and Markdown apply outputs use canonical serialization and contain
counts/directions; they are written before result evidence so the stored
report hashes attest exact bytes.

Task 3 exposes only rollback rehearsal:

- `--dry-run` requires `--out-result-json` and `--out-result-report`, recomputes
  canonical plan bytes and requires `--expected-plan-sha256` to equal the
  separately authorized hash, recomputes the workbook/checklist hashes,
  constructs a read-only `ResourceEvidence` with state `dry_run_inspected`
  and the exact previous/incoming hashes, executes
  `apply_refresh()`, proves the in-transaction after-state differs when the
  plan contains mutable actions, then explicitly calls `conn.rollback()` and
  prints `DRY RUN ROLLED BACK`.
- A non-dry-run invocation is rejected until Task 4 adds resource staging and
  canonical `--apply --activate-resource` orchestration.

Dry run never stages, archives, or activates the workbook resource.

- [ ] **Step 7: Run focused, DB, and import verification**

```bash
env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python \
  -m pytest db/tests/test_workbook_refresh_evidence.py \
  import/tests/test_workbook_refresh_apply.py -q
env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python \
  -m pytest db/tests -q
env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python \
  -m pytest import/tests -q
```

Expected: all commands PASS; no test uses real workbook data.

- [ ] **Step 8: Commit Task 3**

```bash
env -u GIT_INDEX_FILE git add \
  supabase/migrations/20260711000100_workbook_refresh_evidence.sql \
  db/tests/test_workbook_refresh_evidence.py \
  import/workbook_refresh_db.py \
  import/apply_workbook_refresh.py \
  import/tests/conftest.py \
  import/tests/refresh_test_support.py \
  import/tests/test_workbook_refresh_apply.py
env -u GIT_INDEX_FILE git commit -m "feat(import): apply workbook refreshes safely"
```

After commit: fresh spec review, then fresh quality review. Review must include
R-SCOPE and Rule #13 disposition for every sibling writer.

---

### Task 4: Resource Activation And Compensating Recovery

**Files:**
- Create: `import/workbook_resource.py`
- Create: `import/tests/test_workbook_resource.py`
- Modify: `import/apply_workbook_refresh.py`
- Modify: `import/tests/test_workbook_refresh_apply.py`

**Interfaces:**
- Consumes: exact old/new hashes, canonical path, archive directory, ignored manifest path, plan/result output paths, and the guarded DB apply function.
- Produces: `ResourceStage`, `inspect_resource()`, `stage_resource()`, `activate_resource()`, `restore_resource()`, `write_manifest()`, `resolve_commit_outcome()`, `apply_with_resource()`, and canonical `--apply --activate-resource` mode.

- [ ] **Step 1: Write failing resource and cross-boundary rollback tests**

```python
def resource_paths(tmp_path):
    incoming = tmp_path / "incoming.xlsx"
    canonical = tmp_path / "canonical.xlsx"
    incoming.write_bytes(b"incoming")
    canonical.write_bytes(b"previous")
    return ResourcePaths(
        incoming=incoming,
        canonical=canonical,
        archive_dir=tmp_path / "archive",
        manifest=tmp_path / "refresh.manifest.json",
    )


def integration_resource_paths(refresh_db, tmp_path):
    canonical = tmp_path / "canonical.xlsx"
    shutil.copy2(refresh_db.seeded.previous, canonical)
    return ResourcePaths(
        incoming=refresh_db.seeded.incoming,
        canonical=canonical,
        archive_dir=tmp_path / "archive",
        manifest=tmp_path / "refresh.manifest.json",
    )


def test_stage_resource_hashes_copies_and_never_edits_incoming(tmp_path):
    stage = stage_resource(resource_paths(tmp_path))
    assert stage.incoming_sha256 == sha256_file(stage.paths.incoming)
    assert stage.previous_sha256 == sha256_file(stage.paths.canonical)
    assert stage.paths.incoming.read_bytes() == b"incoming"
    assert stage.paths.staged.read_bytes() == b"incoming"


def test_activate_and_restore_are_hash_verified(tmp_path):
    stage = stage_resource(resource_paths(tmp_path))
    activate_resource(stage)
    assert sha256_file(stage.paths.canonical) == stage.incoming_sha256
    restore_resource(stage)
    assert sha256_file(stage.paths.canonical) == stage.previous_sha256


def test_resource_activation_failure_rolls_back_database(
    refresh_db, tmp_path, monkeypatch
):
    before = refresh_db.fingerprint()
    paths = integration_resource_paths(refresh_db, tmp_path)
    monkeypatch.setattr(workbook_resource, "_replace", raising_replace_error)
    with pytest.raises(ResourceActivationError):
        apply_with_resource(
            refresh_db.conn, refresh_db.plan, "owner-test", paths,
            tmp_path / "apply.result.json", tmp_path / "apply.result.md",
        )
    assert refresh_db.fingerprint() == before
    assert sha256_file(paths.canonical) == refresh_db.plan.previous_workbook_sha256


def test_database_commit_failure_restores_previous_resource(refresh_db, tmp_path):
    paths = integration_resource_paths(refresh_db, tmp_path)
    failing = CommitBeforeCommitConnection(refresh_db.conn)
    with pytest.raises(RuntimeError, match="commit failed"):
        apply_with_resource(
            failing, refresh_db.plan, "owner-test", paths,
            tmp_path / "apply.result.json", tmp_path / "apply.result.md",
        )
    assert sha256_file(paths.canonical) == refresh_db.plan.previous_workbook_sha256
    assert refresh_db.fingerprint() == refresh_db.plan.database_fingerprint


def test_apply_with_resource_commits_one_aligned_db_resource_result(
    refresh_db, tmp_path
):
    paths = integration_resource_paths(refresh_db, tmp_path)
    result = apply_with_resource(
        refresh_db.conn, refresh_db.plan, "owner-test", paths,
        tmp_path / "apply.result.json", tmp_path / "apply.result.md",
    )
    assert sha256_file(paths.canonical) == refresh_db.plan.incoming_workbook_sha256
    manifest = json.loads(paths.manifest.read_text())
    assert manifest["state"] == "verified"
    assert manifest["result_evidence_id"] == result.result_evidence_id
    assert manifest["result_evidence_chain_hash"] == result.result_evidence_chain_hash
    assert manifest["report_hashes"] == result.report_hashes
    stored = refresh_db.conn.execute(
        "SELECT chain_hash FROM trust.evidence WHERE id=%s",
        (result.result_evidence_id,),
    ).fetchone()
    assert stored == (result.result_evidence_chain_hash,)
    current = fetch_database_snapshot(
        refresh_db.conn,
        refresh_db.plan.previous_workbook_sha256,
        refresh_db.plan.year,
    )
    assert current.evidence_chain_head == result.result_evidence_chain_hash
```

Define the two test doubles in the same test file:

```python
def raising_replace_error(source, destination):
    if pathlib.Path(destination).name == "canonical.xlsx":
        raise OSError(f"replace failed: {source} -> {destination}")
    os.replace(source, destination)


class CommitBeforeCommitConnection:
    def __init__(self, delegate):
        self.delegate = delegate

    def __getattr__(self, name):
        return getattr(self.delegate, name)

    def commit(self):
        raise RuntimeError("commit failed")
```

- [ ] **Step 2: Run focused tests to verify RED**

```bash
env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python \
  -m pytest import/tests/test_workbook_resource.py \
  import/tests/test_workbook_refresh_apply.py -q
```

Expected: FAIL because the resource module and activation integration do not
exist.

- [ ] **Step 3: Implement stage, activate, restore, and manifest**

Use these exact models and state transitions:

```python
@dataclasses.dataclass(frozen=True)
class ResourcePaths:
    incoming: pathlib.Path
    canonical: pathlib.Path
    archive_dir: pathlib.Path
    manifest: pathlib.Path


@dataclasses.dataclass(frozen=True)
class ResourceStage:
    paths: ResourcePaths
    previous_sha256: str
    incoming_sha256: str
    archive: pathlib.Path
    staged: pathlib.Path


_replace = os.replace


def inspect_resource(paths: ResourcePaths) -> ResourceEvidence:
    return ResourceEvidence(
        state="dry_run_inspected",
        previous_sha256=sha256_file(paths.canonical),
        incoming_sha256=sha256_file(paths.incoming),
        archive_sha256=None,
        staged_sha256=None,
    )


def stage_resource(paths: ResourcePaths) -> ResourceStage:
    previous_sha = sha256_file(paths.canonical)
    incoming_sha = sha256_file(paths.incoming)
    archive = paths.archive_dir / f"홈쇼핑분석_superseded-{previous_sha[:12]}.xlsx"
    staged = paths.canonical.with_suffix(".xlsx.refresh-staged")
    paths.archive_dir.mkdir(parents=True, exist_ok=True)
    if archive.exists() and sha256_file(archive) != previous_sha:
        raise ResourceActivationError("archive-hash-conflict")
    if not archive.exists():
        shutil.copy2(paths.canonical, archive)
    shutil.copy2(paths.incoming, staged)
    if sha256_file(staged) != incoming_sha:
        raise ResourceActivationError("staged-hash-mismatch")
    return ResourceStage(paths, previous_sha, incoming_sha, archive, staged)
```

`ResourceStage.evidence()` returns state `staged`, the exact previous/incoming
hashes from the stage, and freshly recomputed archive/staged hashes in a
`ResourceEvidence` instance.
Immediately before the swap, `activate_resource()` rehashes canonical,
archive, and staged files and refuses if any differs from the stage. It then
uses `_replace(stage.staged, canonical)`, wraps any `OSError` as
`ResourceActivationError`, and verifies the new hash. `restore_resource()`
copies archive to a restore-temp file,
verifies it, then `_replace()`s it onto canonical. `write_manifest()` writes
JSON through a temp file + `_replace()` and records states `staged`,
`activated`, `restored`, `verified`, or `commit_outcome_unknown` with
plan/evidence hashes. Manifest serialization is canonical and never includes
business values.

- [ ] **Step 4: Integrate resource activation around DB commit**

Add `--activate-resource`, `--canonical-workbook`, `--archive-dir`,
`--manifest`, `--out-result-json`, and `--out-result-report` to
`apply_workbook_refresh.py`. `--activate-resource` is legal only with
`--apply`; `--apply` is rejected without it.

Order:

1. `stage_resource()` before opening the write transaction;
2. `apply_refresh()` with `stage.evidence()` and the two output paths, without
   commit; this appends both evidence rows inside the recoverable transaction;
3. database postchecks;
4. `activate_resource()`;
5. verify the canonical hash equals the incoming hash;
6. `conn.commit()`;
7. final resource hash and result-evidence postchecks through a fresh read
   connection;
8. manifest state `verified`, binding the result evidence ID, result evidence
   chain hash, and both immutable report hashes.

`apply_with_resource(conn, plan, entered_by, paths, result_json_path,
result_report_path) -> ApplyResult` owns this order and is the only function
the apply CLI calls. It derives the fresh-check DSN from `conn.info.dsn`. On
any pre-commit or activation failure, it rolls back; if the canonical
path changed, it restores the preverified archive before returning the error.
On a definite pre-commit commit failure it rolls back, restores, verifies the
old hash, and records `restored`. If `commit()` raises with an ambiguous
outcome, `resolve_commit_outcome(dsn, plan_sha256)` opens a fresh connection:
presence of the matching `workbook_refresh_result` means keep/verify the new
resource; confirmed absence means restore; inability to query means record
`commit_outcome_unknown`, make no further resource mutation, and stop for
operator recovery. A dry run calls only `inspect_resource()` and never stages,
archives, or activates.

- [ ] **Step 5: Run resource, apply, and full import suites**

```bash
env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python \
  -m pytest import/tests/test_workbook_resource.py \
  import/tests/test_workbook_refresh_apply.py -q
env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python \
  -m pytest import/tests -q
```

Expected: PASS, including both compensation directions.

- [ ] **Step 6: Commit Task 4**

```bash
env -u GIT_INDEX_FILE git add \
  import/workbook_resource.py \
  import/apply_workbook_refresh.py \
  import/tests/test_workbook_resource.py \
  import/tests/test_workbook_refresh_apply.py
env -u GIT_INDEX_FILE git commit -m "feat(import): activate workbook resources atomically"
```

After commit: fresh spec review, then fresh quality review. Review must trace
every exception path to DB rollback and resource state.

---

### Task 5: Unified Directional Readout

**Files:**
- Modify: `import/measure_cross_source_reconciliation.py` (current lines 20–209 on the planning base)
- Modify: `tests/unit/test_measure_cross_source_reconciliation.py` (current lines 1–79 on the planning base)

**Interfaces:**
- Consumes: latest `workbook_refresh_result` evidence payload plus existing `biz.ppl_monthly`, `biz.slot_pnl`, and source-separated PPL queries.
- Produces: `RefreshDirection`, `summarize_refresh(payload)`,
  `build_measurement(conn, generated_at)`, `canonical_measurement_bytes()`, and
  one added `## Workbook Refresh Direction` section from the compatibility
  wrapper `build_report()`. The CLI writes matching Markdown and JSON via
  `--out` and `--out-json`.

- [ ] **Step 1: Write failing direction tests**

```python
def test_refresh_direction_keeps_source_priorities_and_delta_classes_separate():
    m = _module()
    summary = m.summarize_refresh({
        "dispositions": {
            "insert_slot": 1,
            "revise_slot": 2,
            "supersede_result": 1,
            "preserve_db_only": 3,
            "conflict_human_newer": 0,
            "quarantine": 0,
        },
        "directions": {
            "gross_amount": "up",
            "net_amount": "down",
            "operating_profit": "down",
            "ppl_payment": "up",
            "ppl_allocation": "flat",
        },
    })
    assert summary.preserved_db_only == 3
    assert summary.human_conflicts == 0
    assert summary.directions["operating_profit"] == "down"


class _FakeConnWithRefresh(_FakeConn):
    def execute(self, sql):
        if "kind='workbook_refresh_result'" in " ".join(sql.split()):
            return _Result([({
                "dispositions": {
                    "insert_slot": 1,
                    "revise_slot": 2,
                    "supersede_result": 1,
                    "preserve_db_only": 3,
                    "conflict_human_newer": 0,
                    "quarantine": 0,
                },
                "directions": {
                    "gross_amount": "up",
                    "net_amount": "down",
                    "operating_profit": "down",
                    "ppl_payment": "up",
                    "ppl_allocation": "flat",
                },
            },)])
        return super().execute(sql)


def test_report_has_one_refresh_section_and_no_agency_double_count_claim():
    report = _module().build_report(_FakeConnWithRefresh(), "2026-07-11T00:00:00Z")
    assert report.count("## Workbook Refresh Direction") == 1
    assert "later human evidence remains authoritative" in report
    assert "agency evidence remains reconciliation-only" in report
    assert "Do not commit it" in report


def test_machine_readable_measurement_matches_rendered_refresh_direction():
    module = _module()
    measurement = module.build_measurement(
        _FakeConnWithRefresh(), "2026-07-11T00:00:00Z"
    )
    payload = json.loads(module.canonical_measurement_bytes(measurement))
    assert payload["refresh"]["directions"]["operating_profit"] == "down"
    assert payload["source_policy"]["agency_role"] == "reconciliation_only"
    assert module.build_report(
        _FakeConnWithRefresh(), "2026-07-11T00:00:00Z"
    ).count("## Workbook Refresh Direction") == 1
```

- [ ] **Step 2: Run RED**

```bash
env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python \
  -m pytest tests/unit/test_measure_cross_source_reconciliation.py -q
```

Expected: FAIL because refresh summary/rendering does not exist.

- [ ] **Step 3: Extend the existing report, do not create a second report engine**

First run:

```bash
env -u GIT_INDEX_FILE rg -n \
  "build_report|summarize_months|measure_cross_source_reconciliation" \
  import tests scripts OPERATIONS.md docs
```

Record direct callers in the Task-5 review; preserve the existing CLI and
owner-briefing sections.

Add:

```python
@dataclasses.dataclass(frozen=True)
class RefreshDirection:
    inserted_slots: int
    revised_slots: int
    superseded_results: int
    preserved_db_only: int
    human_conflicts: int
    quarantines: int
    directions: dict[str, str]


def _fetch_latest_refresh(conn):
    return conn.execute(
        """SELECT payload FROM trust.evidence
             WHERE kind='workbook_refresh_result'
             ORDER BY id DESC LIMIT 1"""
    ).fetchone()
```

`summarize_refresh()` reads disposition counts and only directional labels
`up|down|flat|not_comparable`; it does not recompute business formulas in
Python. Refactor the existing DB reads into `build_measurement()` as the single
data model, render Markdown from that model, and serialize the same model to
canonical JSON with decimal strings. `build_report()` remains a compatibility
wrapper. If no refresh evidence exists, both formats state that no workbook
refresh has been applied. Existing pay-month/air-month/agency interpretation
remains unchanged.

- [ ] **Step 4: Run focused and all unit tests**

```bash
env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python \
  -m pytest tests/unit/test_measure_cross_source_reconciliation.py -q
env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python \
  -m pytest tests/unit -q
```

Expected: PASS with synthetic values only.

- [ ] **Step 5: Commit Task 5**

```bash
env -u GIT_INDEX_FILE git add \
  import/measure_cross_source_reconciliation.py \
  tests/unit/test_measure_cross_source_reconciliation.py
env -u GIT_INDEX_FILE git commit -m "feat(import): report workbook refresh direction"
```

After commit: fresh spec review, then fresh quality review, including an
explicit check that agency totals remain outside P&L direction.

---

### Task 6: ADR, Architecture, Operations, And Owner Manual

**Files:**
- Modify: `DECISIONS.md` (append ADR-008)
- Modify: `ARCHITECTURE.md` (current lines 26–376 on the planning base)
- Modify: `OPERATIONS.md` (current lines 83–163 and 399–425 on the planning base)
- Modify: `docs/MANUAL.md` (current lines 281–321 and 409–514 on the planning base)

**Interfaces:**
- Consumes: landed Tasks 1–5 and fresh executed verification output.
- Produces: one non-duplicative product-truth update and exact owner/operator procedure.

- [ ] **Step 1: Collect fresh measured facts from committed instruments**

Run from the routed evidence-ledger worktree:

```bash
env -u GIT_INDEX_FILE find import -maxdepth 1 -name '*.py' -print | sort
env -u GIT_INDEX_FILE find supabase/migrations -maxdepth 1 -name '*.sql' -print | sort
env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python \
  -m pytest import/tests -q
env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python \
  -m pytest db/tests -q
env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python \
  -m pytest tests/unit -q
```

Use only these fresh outputs for inventory/test counts. Do not copy discovery
counts or real business figures into tracked docs.

- [ ] **Step 2: Append ADR-008**

Record:

- cumulative successor workbooks cannot use the one-time importer;
- approved source precedence;
- planner JSON/hash as the authorization boundary;
- result supersession versus guarded operational slot/PPL correction;
- before/after evidence and optimistic predicates;
- resource compensation and same-hash idempotence;
- rejected alternatives: blind append and delete/reload.

The ADR status is `Accepted`, dated with the implementation date, and cites
the user-approved Pipeline spec without embedding real figures.

- [ ] **Step 3: Update ARCHITECTURE.md with current source-backed truth**

Update topology, module map, write-path table, trust evidence allowed kinds,
import pipeline, sharp edges, smoke inventory, test inventory, and `Last
verified` stamp. State explicitly:

- `plan_workbook_refresh.py` is read-only;
- `apply_workbook_refresh.py` is the only refresh executor;
- `workbook_refresh_db.py` uses explicit per-table SQL, not arbitrary plan SQL;
- authenticated clients still have only `record_slot`/`record_result`;
- generated plans/reports/resources remain ignored;
- worktree commands use the primary checkout venv.

- [ ] **Step 4: Add exact operational and recovery commands**

`OPERATIONS.md` must show commands for:

1. read-only plan generation;
2. blocker inspection;
3. `--dry-run` rollback rehearsal;
4. canonical `--apply --activate-resource` execution;
5. post-run measurement;
6. already-applied refusal;
7. manifest-guided restore/retry.

Use absolute data/resource paths because ignored `data/` is not present in the
isolated worktree. Every command uses the primary checkout venv.

- [ ] **Step 5: Add the Korean owner-facing refresh procedure**

Explain in `docs/MANUAL.md`:

- a new cumulative workbook is planned, not re-imported;
- human and agency facts are preserved;
- conflicts stop before writes;
- results are superseding revisions;
- resource/archive hashes and evidence preserve the old/new story;
- dry run rolls back;
- the final readout separates pay month, air month, and agency evidence.

Do not include real values or claim that nonzero PPL month differences are
corruption.

- [ ] **Step 6: Verify docs and full local code gates**

```bash
env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python \
  scripts/check_doc_claims.py ARCHITECTURE.md OPERATIONS.md docs/MANUAL.md DECISIONS.md
env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python \
  scripts/ci_smoke.py
env -u GIT_INDEX_FILE git diff --check
```

Expected: all anchors checked, smoke OK, and no whitespace errors in the Task-6
paths. Unrelated dirty paths are a stop condition, not cleanup authority.

- [ ] **Step 7: Commit Task 6**

```bash
env -u GIT_INDEX_FILE git add DECISIONS.md ARCHITECTURE.md OPERATIONS.md docs/MANUAL.md
env -u GIT_INDEX_FILE git commit -m "docs(import): document workbook refresh operations"
```

After commit: fresh spec review and fresh quality review. The Director then
synthesizes all Task 1–6 review findings and lands bounded fix commits without
amending history.

---

### Task 7: Cumulative Verification And Real-Data Scratch Rehearsal

**Files:**
- Local only: `<routed-worktree>/.superpowers/sdd/workbook-refresh-*.json`
- Local only: `<routed-worktree>/.superpowers/sdd/workbook-refresh-*.md`
- Local only: token-named temporary PostgreSQL database and scratch resource/archive paths
- Pipeline mailbox: one Director verify-request after all code/doc reviews pass

**Interfaces:**
- Consumes: exact Task 1–6 range, user workbook, canonical local workbook/checklist, read-only canonical database, and separate service/scratch tokens.
- Produces: reviewed plan hash, rollback evidence, one committed scratch DB/resource result, scratch directional reports, unchanged canonical DB/resource hashes, and one cumulative verify-request.

- [ ] **Step 1: Obtain the local-service executor token and start only the required local stack**

The Director is the sole executor. If Docker/Supabase is already healthy, cite
live health and do not repeat the side effect. Starting Docker or Supabase
without the named token is forbidden.

- [ ] **Step 2: Run full synthetic scratch verification**

```bash
env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python \
  -m pytest db/tests -q
env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python \
  -m pytest import/tests -q
env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python \
  -m pytest tests/unit -q
env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python \
  scripts/ci_smoke.py
```

These suites provide the isolated scratch-database application required by the
spec through per-test databases and synthetic refresh fixtures.

- [ ] **Step 3: Generate the read-only real-data plan**

From the routed worktree, set `WORKTREE` to its absolute path, then run:

```bash
env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python \
  "$WORKTREE/import/plan_workbook_refresh.py" \
  --previous-workbook /Users/hyungkoookkim/evidence-ledger/data/홈쇼핑분석.xlsx \
  --incoming-workbook /Users/hyungkoookkim/Downloads/260710.xlsx \
  --year 2026 \
  --checklist /Users/hyungkoookkim/evidence-ledger/data/merges.csv \
  --dsn postgresql://postgres:postgres@127.0.0.1:54322/postgres \
  --out-json "$WORKTREE/.superpowers/sdd/workbook-refresh.plan.json" \
  --out-report "$WORKTREE/.superpowers/sdd/workbook-refresh.plan.md"
```

Gate: zero blocking dispositions. Any human conflict, ambiguity, quarantine,
summary mismatch, uncovered variant, or baseline failure stops and routes an
owner decision. Do not edit the plan JSON.

- [ ] **Step 4: Prove the planner was read-only**

Capture DB fingerprint, evidence-chain head, canonical resource hash, and git
status before/after planning. They must be byte-identical/unchanged. Persist
only hashes and dispositions in the local report.

- [ ] **Step 5: Obtain the real-data scratch token and clone the canonical DB/resource**

The token names an unused `SCRATCH_DB`, Director as sole executor, the exact
localhost source DB, dump path, scratch resource root, cleanup command class,
and a no-canonical-write stop condition. Set `AUTHORIZED_PLAN_SHA256` and
`ENTERED_BY` from that token; do not derive either from the files being
executed. The identity must match the preflighted internal owner identity.

```bash
umask 077
export PGPASSWORD=postgres
SCRATCH_DSN="postgresql://postgres:postgres@127.0.0.1:54322/$SCRATCH_DB"
SCRATCH_ROOT="$WORKTREE/.superpowers/sdd/real-data-scratch"
SCRATCH_DUMP="$WORKTREE/.superpowers/sdd/$SCRATCH_DB.dump"
SCRATCH_CANONICAL="$SCRATCH_ROOT/resource/홈쇼핑분석.xlsx"
mkdir -p "$SCRATCH_ROOT/resource"
createdb --host 127.0.0.1 --port 54322 --username postgres "$SCRATCH_DB"
pg_dump --host 127.0.0.1 --port 54322 --username postgres \
  --dbname postgres --format=custom --file "$SCRATCH_DUMP"
pg_restore --exit-on-error --no-owner --no-privileges \
  --dbname "$SCRATCH_DSN" "$SCRATCH_DUMP"
cp /Users/hyungkoookkim/evidence-ledger/data/홈쇼핑분석.xlsx \
  "$SCRATCH_CANONICAL"
rm -f "$SCRATCH_DUMP"
```

`SCRATCH_DB` comes from the token and `createdb` must fail if it already
exists; never drop an unproven pre-existing database. Rerun the planner:

```bash
env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python \
  "$WORKTREE/import/plan_workbook_refresh.py" \
  --previous-workbook "$SCRATCH_CANONICAL" \
  --incoming-workbook /Users/hyungkoookkim/Downloads/260710.xlsx \
  --year 2026 \
  --checklist /Users/hyungkoookkim/evidence-ledger/data/merges.csv \
  --dsn "$SCRATCH_DSN" \
  --out-json "$WORKTREE/.superpowers/sdd/workbook-refresh.scratch.plan.json" \
  --out-report "$WORKTREE/.superpowers/sdd/workbook-refresh.scratch.plan.md"
cmp -s \
  "$WORKTREE/.superpowers/sdd/workbook-refresh.plan.json" \
  "$WORKTREE/.superpowers/sdd/workbook-refresh.scratch.plan.json"
```

Require `cmp` success, the same plan hash, and a scratch canonical hash equal
to Step 4's resource hash.
If dump or restore fails after `createdb` succeeds, run only the token-bound
cleanup for that exact newly created database and dump; never retry over a
partially restored DB.

- [ ] **Step 6: Prove rollback non-vacuity on the scratch clone**

```bash
env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python \
  "$WORKTREE/import/apply_workbook_refresh.py" \
  --plan "$WORKTREE/.superpowers/sdd/workbook-refresh.scratch.plan.json" \
  --expected-plan-sha256 "$AUTHORIZED_PLAN_SHA256" \
  --previous-workbook "$SCRATCH_CANONICAL" \
  --incoming-workbook /Users/hyungkoookkim/Downloads/260710.xlsx \
  --year 2026 \
  --checklist /Users/hyungkoookkim/evidence-ledger/data/merges.csv \
  --entered-by "$ENTERED_BY" \
  --dsn "$SCRATCH_DSN" \
  --canonical-workbook "$SCRATCH_CANONICAL" \
  --out-result-json "$WORKTREE/.superpowers/sdd/workbook-refresh.dry-run.result.json" \
  --out-result-report "$WORKTREE/.superpowers/sdd/workbook-refresh.dry-run.result.md" \
  --dry-run
```

Expected terminal line: `DRY RUN ROLLED BACK`. The command must prove its
in-transaction fingerprint changed before rollback. After rollback, rerun the
scratch planner and require byte-identical plan JSON, evidence-chain head, and
resource hash. Recheck that canonical DB/resource hashes from Step 4 never
changed.

- [ ] **Step 7: Commit one full apply on scratch and generate both reports**

```bash
env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python \
  "$WORKTREE/import/apply_workbook_refresh.py" \
  --plan "$WORKTREE/.superpowers/sdd/workbook-refresh.scratch.plan.json" \
  --expected-plan-sha256 "$AUTHORIZED_PLAN_SHA256" \
  --previous-workbook "$SCRATCH_CANONICAL" \
  --incoming-workbook /Users/hyungkoookkim/Downloads/260710.xlsx \
  --year 2026 \
  --checklist /Users/hyungkoookkim/evidence-ledger/data/merges.csv \
  --entered-by "$ENTERED_BY" \
  --dsn "$SCRATCH_DSN" \
  --canonical-workbook "$SCRATCH_CANONICAL" \
  --archive-dir "$SCRATCH_ROOT/archive" \
  --manifest "$WORKTREE/.superpowers/sdd/workbook-refresh.scratch.manifest.json" \
  --out-result-json "$WORKTREE/.superpowers/sdd/workbook-refresh.scratch.result.json" \
  --out-result-report "$WORKTREE/.superpowers/sdd/workbook-refresh.scratch.result.md" \
  --apply --activate-resource
env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python \
  "$WORKTREE/import/measure_cross_source_reconciliation.py" \
  --dsn "$SCRATCH_DSN" \
  --out "$WORKTREE/.superpowers/sdd/workbook-refresh.scratch.direction.md" \
  --out-json "$WORKTREE/.superpowers/sdd/workbook-refresh.scratch.direction.json"
```

Require the full Task-8 post-activation invariant set on scratch, including
trust-chain recomputation, exact evidence/report/resource hashes, source
preservation, supersession, and same-hash refusal. Hash the outputs, then run
the token-bound cleanup below; retain only hash-bound ignored reports/manifest:

```bash
test "$SCRATCH_ROOT" = "$WORKTREE/.superpowers/sdd/real-data-scratch"
dropdb --force --host 127.0.0.1 --port 54322 --username postgres "$SCRATCH_DB"
rm -rf -- "$SCRATCH_ROOT"
unset PGPASSWORD
```

Prove again that canonical DB/resource hashes and git status equal Step 4.

- [ ] **Step 8: Send one cumulative verify-request**

The Director mailbox artifact names:

- exact Task 1–6 commit range and paths;
- spec and this plan;
- every per-task implementer/spec/quality artifact and disposition;
- focused/full test commands;
- dry-run and committed scratch plan/result/resource/direction hashes;
- scratch cleanup plus unchanged canonical DB/resource postchecks;
- excluded real-data files and ignored output paths;
- expected Operator verdict GO/NITS/FAIL;
- no push and no canonical activation yet.

- [ ] **Step 9: Operator performs independent cumulative Lane V**

Operator reruns focused/full tests, flips one load-bearing predicate per action
class, verifies dry-run non-vacuity, reviews RLS/grants and source priority,
and—under a separate verification scratch token—independently repeats the
real-data plan/dry-run/apply/report path on a new scratch DB/resource. Operator
returns one GO/NITS/FAIL and never touches canonical resources or repairs code.

Gate: Task 8 cannot start without Operator GO for the exact range and committed
scratch evidence.

---

### Task 8: Canonical Local Activation, Verification, And All-Seat Closeout

**Files:**
- Local resource: `/Users/hyungkoookkim/evidence-ledger/data/홈쇼핑분석.xlsx`
- Local archive: `/Users/hyungkoookkim/evidence-ledger/data/archive/`
- Local manifest/readouts: `<routed-worktree>/.superpowers/sdd/`
- Pipeline mailbox/capacity/handoff: coordinator-owned closeout artifacts

**Interfaces:**
- Consumes: Operator GO, fresh zero-blocker plan, canonical activation token, exact reviewed code range.
- Produces: updated local DB/resource, verified evidence rows, unified directional report, and one all-seat closeout.

- [ ] **Step 1: Obtain a target-bound canonical activation executor token**

Token names Director as sole executor and binds exact command class, DB DSN,
incoming/canonical/archive/manifest paths, reviewed plan hash, preflight
fingerprint, stop conditions, postchecks, observer seats, and no-push
non-goals.

- [ ] **Step 2: Re-run the planner immediately before activation**

Use Task-7 Step-3 command with fresh output filenames. Require:

- zero blockers;
- same incoming/previous/checklist hashes;
- live database fingerprint equal to the freshly generated plan;
- no newer human fact or source-priority change;
- Operator-reviewed code range unchanged.

If the plan hash changes only because the database fingerprint changed, stop
and route the changed facts for review. Do not reuse stale authorization.

- [ ] **Step 3: Run the single canonical DB/resource command**

Set `AUTHORIZED_PLAN_SHA256` from the canonical activation token issued after
Step 2. It must equal the fresh plan hash and is not recomputed from the plan
inside this shell command. Set `ENTERED_BY` from that same token; do not
hard-code or infer an identity at execution time.

```bash
env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python \
  "$WORKTREE/import/apply_workbook_refresh.py" \
  --plan "$WORKTREE/.superpowers/sdd/workbook-refresh.final.plan.json" \
  --expected-plan-sha256 "$AUTHORIZED_PLAN_SHA256" \
  --previous-workbook /Users/hyungkoookkim/evidence-ledger/data/홈쇼핑분석.xlsx \
  --incoming-workbook /Users/hyungkoookkim/Downloads/260710.xlsx \
  --year 2026 \
  --checklist /Users/hyungkoookkim/evidence-ledger/data/merges.csv \
  --entered-by "$ENTERED_BY" \
  --dsn postgresql://postgres:postgres@127.0.0.1:54322/postgres \
  --canonical-workbook /Users/hyungkoookkim/evidence-ledger/data/홈쇼핑분석.xlsx \
  --archive-dir /Users/hyungkoookkim/evidence-ledger/data/archive \
  --manifest "$WORKTREE/.superpowers/sdd/workbook-refresh.manifest.json" \
  --out-result-json "$WORKTREE/.superpowers/sdd/workbook-refresh.result.json" \
  --out-result-report "$WORKTREE/.superpowers/sdd/workbook-refresh.result.md" \
  --apply --activate-resource
```

Only this command may mutate the canonical DB/resource target.

- [ ] **Step 4: Verify post-activation invariants**

Verify with committed commands:

- canonical resource hash equals incoming hash;
- archive hash equals the previous canonical hash;
- manifest state is `verified` and binds plan/result evidence IDs plus the
  result evidence chain hash;
- current business-state DB fingerprint equals the expected post-apply
  fingerprint, and the current evidence-chain head equals the manifest/result
  evidence chain hash;
- no duplicate historical slot was inserted;
- human, agency, and preserved DB-only facts are byte-equivalent to preflight;
- result corrections extend same-slot supersession chains;
- slot/PPL corrections match evidence before/after payloads;
- trust chain recomputes with zero breaks;
- applying the same incoming hash again is refused before mutation.

- [ ] **Step 5: Generate the final unified directional report**

```bash
env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python \
  "$WORKTREE/import/measure_cross_source_reconciliation.py" \
  --dsn postgresql://postgres:postgres@127.0.0.1:54322/postgres \
  --out "$WORKTREE/.superpowers/sdd/workbook-refresh-direction-final.md" \
  --out-json "$WORKTREE/.superpowers/sdd/workbook-refresh-direction-final.json"
```

Confirm it separates internal pay-month, internal air-month, agency
reconciliation, human/database-only preservation, and refresh direction.
Recompute both file hashes and add them to the ignored manifest and closeout.
Never copy its real figures into tracked files or mailbox bodies.

- [ ] **Step 6: Run final local acceptance**

```bash
cd "$WORKTREE"
PY=/Users/hyungkoookkim/evidence-ledger/.venv/bin/python
env -u GIT_INDEX_FILE "$PY" -m pytest db/tests -q
env -u GIT_INDEX_FILE "$PY" -m pytest import/tests -q
env -u GIT_INDEX_FILE "$PY" -m pytest tests/unit -q
env -u GIT_INDEX_FILE "$PY" scripts/ci_smoke.py
env -u GIT_INDEX_FILE xcodegen generate \
  --spec ios/EvidenceLedger/project.yml
env -u GIT_INDEX_FILE xcodebuild \
  -project ios/EvidenceLedger/EvidenceLedger.xcodeproj \
  -scheme EvidenceLedger \
  -destination 'platform=iOS Simulator,name=iPhone 17 Pro' \
  test
env -u GIT_INDEX_FILE git -C "$WORKTREE" status --short --branch
```

Expected: DB/import/iOS acceptance succeeds, smoke is OK, and the routed
worktree is clean. Local ignored evidence/resources do not appear in tracked
status.

- [ ] **Step 7: Notify all seats once and close the routed cycle**

Coordinator re-reads fresh mailbox/capacity/git state, then writes one
consolidated coordinator-to-all closeout citing:

- implementation range and Operator GO;
- activation side-effect ID and sole executor;
- plan/result/resource/report hashes and evidence IDs;
- final verification commands and outcomes;
- privacy confirmation that no real data entered git;
- preservation of human, agency, and DB-only facts;
- no push/remote publication;
- exact next trigger for any later publication decision.

Validate the closeout with capacity board, route validation, protocol doctor,
and Pipeline smoke, then verify the single broadcast is visible to Director,
Operator, Director2, and Operator2 seat-by-seat. Send no receipt/status churn
unless a seat is genuinely missing the event. These gates supplement rather
than replace Operator GO.

---

## Approved Spec Coverage

| Approved design requirement | Implemented and proved by |
|---|---|
| Authority boundary and source priority | Tasks 1–3 planner/apply classifications; Tasks 5–6 interpretation and owner docs; Task 7 Operator mutation checks |
| Canonical resource archive, activation, and recovery | Task 4 integration tests; Task 7 rollback rehearsal; Task 8 sole-executor activation and postchecks |
| Deterministic matching and payment-month rule | Task 1 pure/table-driven tests; Task 2 hash-bound read-only plan; Task 7 zero-blocker real-data plan |
| Result immutability and operational correction evidence | Task 3 RPC supersession, optimistic updates, evidence payload, and RLS tests; Task 7 Lane V |
| Unified directional interpretation | Task 3 DB-view direction capture; Task 5 single report surface; Tasks 7–8 local-only reports |
| Error handling and stop conditions | Tasks 1–4 blockers/idempotence/rollback; Tasks 7–8 fresh-token and fresh-fingerprint gates |
| Privacy and no publication | Global constraints; Tasks 6–8 ignored paths, status checks, mailbox hash-only reporting, and no-push closeout |
| Four-seat capacity and notification | Execution preconditions; per-task fresh reviews; Task 7 Operator GO; Task 8 consolidated coordinator-to-all closeout |

Every row must be cited in the final spec review. A requirement with no landed
code/test/doc evidence is a FAIL, not an implicit follow-up.

---

## Plan Completion Gate

The implementation plan is complete only when Tasks 1–6 are committed and
reviewed, Task 7 has a non-vacuous rollback plus committed real-data scratch
apply and Operator GO, Task 8 has one authorized successful canonical
activation, the final report is local-only, and the coordinator-to-all
closeout is durable. No push is implied.
