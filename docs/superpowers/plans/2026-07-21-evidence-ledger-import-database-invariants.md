# Evidence-Ledger Import and Database Invariants Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make new internal imports immutable by workbook identity, reject contradictory alias decisions and negative costs before materialized writes, and prevent checklist proposal from overwriting an existing owner file.

**Architecture:** Bind internal broadcast source references to the full workbook SHA-256 at parse time. Add one shared alias-integrity module used by both import lanes for preflight comparison and race-safe insertion. Treat negative agency cost as a blocking typed anomaly before `psycopg.connect`. Make proposal creation exclusive with standard file mode `x`. Preserve the existing single-transaction load and historical rows.

**Tech Stack:** Python 3.11+, pytest, openpyxl, psycopg interfaces, standard-library `hashlib`, `dataclasses`, `pathlib`, and CSV.

## Global Constraints

- Bind this packet to the locally integrated, Operator2-accepted Packet 2 head. Before Task 1, set the task-specific shell variable `EVIDENCE_LEDGER_PACKET_PARENT_SHA` to the route's exact 40-hex parent, assert `git rev-parse HEAD` equals it, and keep that shell active for the packet.
- Use a dedicated evidence-ledger worktree and the main checkout's Python environment only as an interpreter/dependency source.
- Preserve `.vscode/`, historical rows, existing `source_ref` values, and the one-transaction rollback contract.
- Use synthetic fixtures only. Do not connect to a managed database or inspect private workbook values.
- A separately authorized, already-running local Supabase stack may be used for optional scratch-database integration tests. This plan does not authorize starting, stopping, resetting, or reconfiguring it.
- Do not add a migration, backfill source refs, infer refund/credit semantics, add an overwrite flag, or change CI ceremony rules.
- Do not merge or push.

---

## Task 1: Bind new internal source references to the full workbook SHA-256

**Files:**

- Modify: `import/tests/test_parse_workbook.py`
- Create: `import/tests/test_reconcile_unit.py`
- Modify: `import/parse_workbook.py`
- Modify: `import/run_import.py`
- Verify: `import/reconcile.py`

- [ ] Add a test that creates two valid synthetic workbooks with the same sheet and row number but different workbook bytes. Parse both and assert:

```python
assert len(first.workbook_sha256) == 64
assert len(second.workbook_sha256) == 64
assert first.workbook_sha256 != second.workbook_sha256
assert first.rows[0].source_ref == (
    f"sha256:{first.workbook_sha256}:방송스케줄!r2"
)
assert second.rows[0].source_ref == (
    f"sha256:{second.workbook_sha256}:방송스케줄!r2"
)
assert first.rows[0].source_ref != second.rows[0].source_ref
```

Modify only workbook metadata or a non-business synthetic cell to make the bytes differ; keep the row coordinate constant.

- [ ] Extend the existing anomaly provenance test to assert each internal anomaly starts with `f"sha256:{out.workbook_sha256}:"` and still ends with `방송스케줄!rN`.

- [ ] Run these tests before implementation:

```bash
env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python \
  -m pytest import/tests/test_parse_workbook.py \
  -k 'source_ref or anomalies' -q
```

Expected: FAIL because `ParseOutput` has no `workbook_sha256` and current refs are yearless `방송스케줄!rN`.

- [ ] Add a required `workbook_sha256: str` field to `ParseOutput`. At the start of `parse`, compute exactly once:

```python
workbook_sha256 = hashlib.sha256(path.read_bytes()).hexdigest()
```

Add a local helper:

```python
def source_ref(sheet: str, row_no: int) -> str:
    return f"sha256:{workbook_sha256}:{sheet}!r{row_no}"
```

Use it for every internal `BroadcastRow` and `WorkbookAnomaly` created from `방송스케줄`. Return the same hash on `ParseOutput`.

- [ ] In `run_import.main`, replace the second `hashlib.sha256(wb_path.read_bytes())` for the internal lane with `out.workbook_sha256`. Leave the agency lane's existing workbook-root hash behavior unchanged.

- [ ] In `test_reconcile_unit.py`, construct one minimal row with source ref `f"sha256:{'a' * 64}:방송스케줄!r2"` and a fake connection that records `(sql, params)` and returns matching metric values. Call `reconcile` and assert the query params are exactly `(row.source_ref,)`. Do not strip or reconstruct the hash in reconciliation; the existing `(r.source_ref,)` parameter is the required behavior.

- [ ] Re-run `test_parse_workbook.py`. Expected: all tests pass and every new internal row/anomaly ref carries the full 64-hex digest.

- [ ] Commit the identity change:

```bash
env -u GIT_INDEX_FILE git add \
  import/parse_workbook.py import/run_import.py \
  import/tests/test_parse_workbook.py import/tests/test_reconcile_unit.py
env -u GIT_INDEX_FILE git commit -m "fix(import): bind rows to workbook identity"
```

## Task 2: Define one fail-closed alias-integrity contract

**Files:**

- Create: `import/alias_integrity.py`
- Create: `import/tests/test_alias_integrity_unit.py`
- Modify: `import/load_staging.py`
- Modify: `import/load_agency.py`

- [ ] Create tests for this public module contract:

```python
@dataclass(frozen=True)
class AliasBinding:
    entity_type: str
    alias: str
    canonical: str

@dataclass(frozen=True)
class AliasConflict:
    entity_type: str
    alias: str
    existing_entity_id: int
    existing_canonical: str
    proposed_canonical: str

class AliasConflictError(ValueError):
    conflicts: tuple[AliasConflict, ...]

def validate_alias_plan(conn, bindings: Iterable[AliasBinding]) -> None:
    conflicts = tuple(find_alias_conflicts(conn, bindings))
    if conflicts:
        raise AliasConflictError(conflicts)

def insert_alias_checked(
    conn, binding: AliasBinding, entity_id: int, source: str, approved_by: str
) -> None:
    insert_alias_if_absent(conn, binding, entity_id, source, approved_by)
    assert_alias_target(conn, binding, entity_id)
```

Use synthetic names such as `채널갑`, `채널을`, and `별칭하나`. Test three preflight dispositions with a deterministic fake connection:

1. absent alias: validation returns normally;
2. existing alias targeting the same canonical identity: validation returns normally;
3. existing alias targeting a different canonical identity: `AliasConflictError` includes entity type, alias, existing id/name, and proposed canonical name.

Also test `insert_alias_checked` re-reads the binding after its `ON CONFLICT DO NOTHING` insert, accepting the same id and rejecting a simulated conflicting race.

- [ ] Run the new tests before implementation:

```bash
env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python \
  -m pytest import/tests/test_alias_integrity_unit.py -q
```

Expected: collection FAIL because `alias_integrity` does not exist.

- [ ] Implement fixed query mappings for the four known entity types. Each lookup joins `biz.entity_aliases` to the correct canonical table and returns `(entity_id, canonical_text)`:

  - channel -> `biz.channels.code`;
  - product -> `biz.products.name_ko`;
  - tv_show -> `biz.tv_shows.name_ko`;
  - producer -> `biz.producers.name_ko`.

Reject any unknown `entity_type` instead of interpolating a table name. Parameterize all values.

- [ ] `validate_alias_plan` must query every `variant != canonical` before either loader performs canonical entity INSERTs. Accumulate all contradictory bindings and raise one structured `AliasConflictError`; do not stop at the first conflict and do not write anything in this phase.

- [ ] `insert_alias_checked` may use `ON CONFLICT DO NOTHING`, but only as a race-safe insert attempt. It must immediately query the authoritative target and compare its entity id with the proposed `entity_id`; a mismatch raises `AliasConflictError`, causing the surrounding transaction to roll back.

- [ ] In both `_ensure_entities` implementations:

  1. build `seen` as today;
  2. convert every `variant != canonical` into an `AliasBinding`;
  3. call `validate_alias_plan` before the first canonical entity insert;
  4. materialize canonical entities;
  5. replace raw alias INSERTs with `insert_alias_checked` using the correct source (`excel_import` or `agency_excel_import`).

- [ ] Re-run the alias tests plus the two hermetic loader/checklist suites:

```bash
env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python -m pytest \
  import/tests/test_alias_integrity_unit.py \
  import/tests/test_load_agency_unit.py \
  import/tests/test_checklist_coverage_unit.py -q
```

Expected: all selected tests pass. The fake connection records SELECT-only preflight before any INSERT.

## Task 3: Block negative cost before opening a database connection

**Files:**

- Modify: `import/tests/test_parse_agency_schedule.py`
- Create: `import/tests/test_run_import_unit.py`
- Modify: `import/parse_agency_schedule.py`
- Modify: `import/run_import.py`

- [ ] Add a generated-workbook parser test with cost `-12.5`. Assert the row retains `Decimal("-12.5")` for evidence, and exactly one matching anomaly has kind `negative_cost`, the exact `source_ref`, and the raw cost in `detail`.

- [ ] Add a pure selector in `run_import.py`:

```python
AGENCY_BLOCKING_ANOMALY_KINDS = frozenset({"negative_cost"})

def agency_blocking_anomalies(output):
    return [a for a in output.anomalies if a.kind in AGENCY_BLOCKING_ANOMALY_KINDS]
```

- [ ] In `test_run_import_unit.py`, construct a synthetic `AgencyParseOutput` with one `negative_cost` anomaly, monkeypatch `parse_agency`, checklist coverage, and `psycopg.connect`, then call `_agency_main`. Assert `SystemExit(1)`, the Korean output names `negative_cost` and its source ref, and the fake `connect` was never called.

- [ ] Run both tests before implementation. Expected: FAIL because no negative anomaly or pre-connect blocker exists.

- [ ] In `_extract_rows`, after exact Decimal parsing, emit `negative_cost` when `cost < 0`. Do not convert it to `None`; retain the signed parsed value in `AgencyPlacementRow` so the anomaly evidence is auditable.

- [ ] In `_agency_main`, evaluate `agency_blocking_anomalies(output)` on non-proposal import before constructing the DSN or calling `psycopg.connect`. Print one bounded Korean blocker line plus every anomaly's kind and source ref, then raise `SystemExit(1)`. Do not infer credit/refund handling.

- [ ] Re-run both tests. Expected: pass; the connection sentinel remains untouched.

## Task 4: Make checklist proposal exclusive and byte-preserving

**Files:**

- Modify: `import/tests/test_propose_merges.py`
- Modify: `import/propose_merges.py`
- Verify: `import/run_import.py`
- Verify: `import/parse_agency_schedule.py`

- [ ] Add this regression contract:

```python
path.write_bytes(b"owner-signed-existing-bytes\n")
before = path.read_bytes()
with pytest.raises(FileExistsError):
    write_checklist(merges, path)
assert path.read_bytes() == before
```

- [ ] Update `test_checklist_roundtrip_requires_decisions` so its owner-signing simulation edits the already-created CSV directly with `csv.DictReader`/`csv.DictWriter`; it must not call proposal creation a second time.

- [ ] Run `test_propose_merges.py` before implementation. Expected: FAIL because the current write-mode `open` call truncates the existing path.

- [ ] Change only the proposal open mode:

```python
with open(path, "x", newline="", encoding="utf-8-sig") as f:
```

Do not add `overwrite`, `force`, suffix generation, automatic deletion, or backup behavior. Let `FileExistsError` stop both internal and agency proposal paths before a byte changes; their existing calls already share `write_checklist`.

- [ ] Re-run `test_propose_merges.py`. Expected: all tests pass and the existing-byte assertion is exact.

## Task 5: Add the new hermetic invariant suites to the import lane

**Files:**

- Modify: `.github/workflows/ci.yml`
- Modify: `ARCHITECTURE.md`
- Modify: `OPERATIONS.md`

- [ ] Add these exact paths to the folded `import-hermetic` pytest command, before `--tb=short -q`:

```text
import/tests/test_alias_integrity_unit.py
import/tests/test_run_import_unit.py
import/tests/test_reconcile_unit.py
```

Keep `test_checklist_coverage_unit.py` out until Packet 4, where its prior omission is corrected as its own audit finding.

- [ ] Run the exact expanded lane locally with the main checkout interpreter. Expected: exit 0, no DB connection attempt, and no skip/xfail introduced.

- [ ] Run collection and record the emitted integer in the CI lane comment, `ARCHITECTURE.md`, and `OPERATIONS.md` rather than guessing it:

```bash
env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python \
  -m pytest --collect-only -q \
  import/tests/test_parse_workbook.py \
  import/tests/test_parse_agency_schedule.py \
  import/tests/test_propose_merges.py \
  import/tests/test_load_agency_unit.py \
  import/tests/test_profile_agency_workbook.py \
  import/tests/test_alias_integrity_unit.py \
  import/tests/test_run_import_unit.py \
  import/tests/test_reconcile_unit.py
```

Expected: exit 0 and one final `N tests collected` line where `N` is an integer. Paste that emitted integer; do not preserve the stale five-file/80-test claim.

- [ ] Update both `*Last verified:*` stamps in `ARCHITECTURE.md` to `2026-07-21 @ ` followed by the exact value of `EVIDENCE_LEDGER_PACKET_PARENT_SHA`. Describe hash-bound new source refs, alias conflict behavior, negative-cost preflight, exclusive checklist creation, and the expanded hermetic lane. Update `OPERATIONS.md` with the same operator-visible failures and commands.

- [ ] Repair and verify anchors:

```bash
env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python scripts/check_doc_claims.py --fix
env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python scripts/check_doc_claims.py OPERATIONS.md
env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python scripts/check_arch_freshness.py --base "${EVIDENCE_LEDGER_PACKET_PARENT_SHA:?route parent missing}"
```

Expected: all three commands exit 0.

- [ ] Commit Tasks 2-5 with explicit paths:

```bash
env -u GIT_INDEX_FILE git add \
  import/alias_integrity.py \
  import/load_staging.py import/load_agency.py import/parse_agency_schedule.py \
  import/propose_merges.py import/run_import.py \
  import/tests/test_alias_integrity_unit.py \
  import/tests/test_parse_agency_schedule.py \
  import/tests/test_run_import_unit.py \
  import/tests/test_reconcile_unit.py \
  import/tests/test_propose_merges.py \
  .github/workflows/ci.yml ARCHITECTURE.md OPERATIONS.md
env -u GIT_INDEX_FILE git commit -m "fix(import): fail closed on unsafe owner inputs"
```

## Task 6: Verify the packet and request independent review

**Files:**

- Verify only; no new production files.

- [ ] Run the exact Packet 3 hermetic profile:

```bash
env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python -m pytest \
  import/tests/test_parse_workbook.py \
  import/tests/test_parse_agency_schedule.py \
  import/tests/test_propose_merges.py \
  import/tests/test_load_agency_unit.py \
  import/tests/test_profile_agency_workbook.py \
  import/tests/test_alias_integrity_unit.py \
  import/tests/test_run_import_unit.py \
  import/tests/test_reconcile_unit.py \
  --tb=short -q
```

Expected: exit 0; all tests pass without contacting Postgres.

- [ ] If and only if a separately authorized local stack is already running, run any new scratch-database alias tests with the explicit interpreter. Otherwise record `not run: local-stack authority absent`; do not start the stack and do not weaken the hermetic acceptance evidence.

- [ ] Run smoke and range checks:

```bash
env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python scripts/ci_smoke.py
env -u GIT_INDEX_FILE git diff --check "${EVIDENCE_LEDGER_PACKET_PARENT_SHA:?route parent missing}"..HEAD
env -u GIT_INDEX_FILE git diff --name-only "${EVIDENCE_LEDGER_PACKET_PARENT_SHA:?route parent missing}"..HEAD
env -u GIT_INDEX_FILE git status --short --branch
```

Expected: smoke ends in `OK`; diff check is silent; only the paths named in this plan changed; the worktree is clean.

- [ ] Publish an immutable verify-request to non-author Operator2. Use distinct finding references for hash-bound source identity, reconciliation exactness, alias absent/same/conflicting behavior, race recheck, negative-cost pre-connect block, checklist byte preservation, and transaction preservation.

- [ ] Stop. Operator2 GO does not authorize local integration, service changes, merge, or push.
