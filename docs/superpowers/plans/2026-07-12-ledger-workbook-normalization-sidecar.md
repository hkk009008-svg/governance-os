# Evidence-Ledger Workbook Normalization Sidecar Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a hash-bound local Excel sidecar that normalizes only 12 proved-lossless workbook anomalies, collects 68 explicit owner corrections, and feeds a fail-closed zero-blocker refresh plan without modifying either source workbook.

**Architecture:** A new pure normalization module owns bindings, typed decisions, canonical JSON, and exact rule validation. A separate `openpyxl` CLI generates and validates the local sidecar. The existing planner accepts only canonical override JSON, records the override and normalization audit in the plan, and remains unchanged when no override is supplied; the applier consumes only the canonical plan.

**Tech Stack:** Python 3.11+, dataclasses, `openpyxl`, `psycopg`, pytest, canonical JSON, SHA-256, PostgreSQL read-only snapshots.

## Global Constraints

- Product work occurs only in `/Users/hyungkoookkim/Pipeline/.worktrees/evidence-ledger-workbook-refresh-2026-07-11` on `codex/ledger-workbook-refresh-2026-07-11`, starting at clean `d57f538`.
- Use `/Users/hyungkoookkim/evidence-ledger/.venv/bin/python` and prefix ordinary git/pytest with `env -u GIT_INDEX_FILE`.
- Never edit `/Users/hyungkoookkim/Downloads/260710.xlsx` or `/Users/hyungkoookkim/evidence-ledger/data/홈쇼핑분석.xlsx`.
- Real sidecars, overrides, plans, reports, workbook values, and dumps stay under ignored `.superpowers/sdd/` paths and never enter git or mailbox bodies.
- Tasks 1–5 use synthetic fixtures only. No real workbook read occurs before Task 6's separately bound read-only token.
- No scratch database/resource apply occurs in this plan. Task 6 stops after generating the blank real owner sidecar.
- No seat may fill the 68 owner fields by heuristic. A completed sidecar requires the user-principal's later input.
- Missing/conflicting payment months are never inferred from broadcast month, summaries, prior workbook, database placement, majority, first, earliest, or latest values.
- Summary controls never create detail or allocate residuals.
- Every product task ends with a clean commit, fresh specification review, then fresh quality review. No push, merge, publication, or canonical activation.

## File Map

| Path | Responsibility |
|---|---|
| `import/workbook_refresh_normalization.py` | Typed bindings/decisions/audits, canonical override bytes, strict validation, approved deterministic rules |
| `import/workbook_refresh_corrections.py` | `generate` and `validate` CLI; atomic `.xlsx`/JSON publication; read-only source/DB binding checks |
| `import/workbook_refresh.py` | Pure planner integration, plan audit fields, exact group/anomaly resolution |
| `import/plan_workbook_refresh.py` | Optional `--normalization-overrides`, path separation, canonical plan/report binding |
| `import/apply_workbook_refresh.py` | Canonical load and evidence projection for normalization-aware plans; no sidecar input |
| `import/tests/test_workbook_refresh_normalization.py` | Pure schema, binding, decision, and exact-rule tests |
| `import/tests/test_workbook_refresh_corrections.py` | Synthetic Excel generation/validation, alias/atomicity/formula/protection tests |
| `import/tests/test_workbook_refresh_plan.py` | Planner behavior, component bijection, zero-blocker and mutation pins |
| `import/tests/test_workbook_refresh_plan_cli.py` | CLI argument/path/read-only/canonical-output behavior |
| `import/tests/test_workbook_refresh_apply.py` | Plan load/evidence/hash compatibility |
| `import/tests/make_refresh_fixture.py` | Synthetic anomaly and owner-decision fixture shapes |
| `import/tests/refresh_test_support.py` | Reusable synthetic builders for grouped decisions and summaries |
| `ARCHITECTURE.md`, `OPERATIONS.md`, `docs/MANUAL.md`, `DECISIONS.md` | Product truth, commands, Korean owner workflow, append-only decision record |

---

### Task 1: Pure Normalization Contract

**Files:**
- Create: `import/workbook_refresh_normalization.py`
- Create: `import/tests/test_workbook_refresh_normalization.py`

**Interfaces:**
- Consumes: hashes and fact/group inventories derived from a blocked plan and parsed workbooks.
- Produces: `NormalizationBindings`, `MissingMonthDecision`, `GroupMemberAssignment`, `ConflictingGroupDecision`, `MissingFieldDecision`, `NormalizationOverrides`, `NormalizationAudit`, `canonical_override_bytes()`, `override_sha256()`, `load_normalization_overrides()`, and `validate_normalization_overrides()`.

- [ ] **Step 1: Write strict schema and canonicalization tests**

In the same test file, define `complete_overrides` plus
`replace_first_missing_month()` using only synthetic hashes/values. Add tests
that construct all 68 synthetic decisions and require stable canonical bytes:

```python
def test_canonical_override_bytes_are_order_independent(complete_overrides):
    reordered = dataclasses.replace(
        complete_overrides,
        missing_months=tuple(reversed(complete_overrides.missing_months)),
    )
    assert canonical_override_bytes(complete_overrides) == canonical_override_bytes(reordered)


@pytest.mark.parametrize("bad", [True, 202601, "2026-1", "2026-13"])
def test_missing_month_requires_exact_year_month(complete_overrides, bad):
    changed = replace_first_missing_month(complete_overrides, approved_month=bad)
    with pytest.raises(NormalizationBlocked, match="invalid-approved-month"):
        validate_normalization_overrides(changed, expected_bindings=complete_overrides.bindings)
```

Also pin exact completeness, unknown/duplicate fact IDs, changed member sets,
invalid approval dates, blank approvers, formulas represented as strings
beginning with `=`, overlapping partitions, subgroup month disagreement, and
zero/multiple amount owners.

- [ ] **Step 2: Run the focused RED suite**

```bash
env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python \
  -m pytest import/tests/test_workbook_refresh_normalization.py -q
```

Expected: collection/import failure because the module and interfaces do not exist.

- [ ] **Step 3: Implement immutable types and canonical validation**

Use explicit dataclasses; do not store polymorphic free-form decisions:

```python
@dataclasses.dataclass(frozen=True)
class NormalizationBindings:
    schema_version: str
    source_plan_parser_commit: str
    normalization_implementation_commit: str
    plan_sha256: str
    previous_workbook_sha256: str
    incoming_workbook_sha256: str
    checklist_sha256: str
    database_fingerprint: str
    evidence_chain_head: str
    reason_fact_set_sha256: tuple[tuple[str, str], ...]


@dataclasses.dataclass(frozen=True)
class MissingMonthDecision:
    group_hash: str
    member_fact_ids: tuple[str, ...]
    approved_month: str
    approved_by: str
    approval_date: str
    owner_note: str


@dataclasses.dataclass(frozen=True)
class GroupMemberAssignment:
    member_fact_id: str
    subgroup_id: str
    approved_month: str
    amount_owner: bool


@dataclasses.dataclass(frozen=True)
class ConflictingGroupDecision:
    group_hash: str
    assignments: tuple[GroupMemberAssignment, ...]
    approved_by: str
    approval_date: str
    owner_note: str


@dataclasses.dataclass(frozen=True)
class MissingFieldDecision:
    fact_id: str
    issue_kind: str
    approved_product: str | None
    approved_broadcast_date: str | None
    approved_by: str
    approval_date: str
    owner_note: str


@dataclasses.dataclass(frozen=True)
class NormalizationAudit:
    fact_id: str
    rule_code: str
    effect: str
    binding_sha256: str


@dataclasses.dataclass(frozen=True)
class NormalizationOverrides:
    bindings: NormalizationBindings
    sidecar_sha256: str
    missing_months: tuple[MissingMonthDecision, ...]
    conflicting_groups: tuple[ConflictingGroupDecision, ...]
    missing_fields: tuple[MissingFieldDecision, ...]
    decision_set_sha256: str
```

Canonicalization sorts every tuple by its stable identity before JSON encoding.
Validation requires exactly the expected fact/group/member sets supplied by the
caller; it never hard-codes the real count as a substitute for set equality.

- [ ] **Step 4: Run focused tests and static checks**

```bash
env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python \
  -m pytest import/tests/test_workbook_refresh_normalization.py -q
env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python \
  -m py_compile import/workbook_refresh_normalization.py
env -u GIT_INDEX_FILE git diff --check
```

Expected: PASS.

- [ ] **Step 5: Commit and review Task 1**

```bash
env -u GIT_INDEX_FILE git add \
  import/workbook_refresh_normalization.py \
  import/tests/test_workbook_refresh_normalization.py
env -u GIT_INDEX_FILE git commit -m "feat(import): define workbook normalization overrides"
```

Obtain fresh specification PASS, then fresh quality APPROVED.

---

### Task 2: Excel Sidecar Generator And Validator

**Files:**
- Create: `import/workbook_refresh_corrections.py`
- Create: `import/tests/test_workbook_refresh_corrections.py`
- Modify: `import/tests/refresh_test_support.py`

**Interfaces:**
- Consumes: Task 1 types plus blocked canonical plan, old/new workbooks, checklist, year, and read-only DSN.
- Produces: `build_correction_workbook()`, `validate_correction_workbook()`, atomic local `.xlsx`, canonical override JSON, and CLI subcommands `generate`/`validate`.

- [ ] **Step 1: Write generation and workbook-layout tests**

Add a `synthetic_inputs` fixture and `editable_coordinates()` /
`expected_owner_input_coordinates()` test helpers in the same test file. Build
only synthetic inputs and assert the exact workbook contract:

```python
def test_generate_has_exact_sheets_bindings_and_editable_cells(synthetic_inputs, tmp_path):
    output = tmp_path / "owner-corrections.xlsx"
    build_correction_workbook(
        blocked_plan=synthetic_inputs.blocked_plan,
        previous=synthetic_inputs.previous,
        incoming=synthetic_inputs.incoming,
        bindings=synthetic_inputs.bindings,
        output_path=output,
    )
    wb = openpyxl.load_workbook(output, data_only=False)
    assert wb.sheetnames == [
        "Instructions", "Missing_Months", "Conflicting_Groups",
        "Missing_Fields", "Auto_Resolved", "Summary_Gates", "_Bindings",
    ]
    assert wb["_Bindings"].sheet_state == "veryHidden"
    assert editable_coordinates(wb) == expected_owner_input_coordinates(synthetic_inputs)
```

Pin frozen panes, filters, Korean/English instructions, protection, data
validations, widths, styles, protected-row canonical hash, and that generation
does not modify either source workbook. Assert the canonical protected-cell
content model, not raw `.xlsx` ZIP bytes, because ZIP metadata is not the
authority surface.

- [ ] **Step 2: Write validator and atomicity RED tests**

Tests must reject:

```python
@pytest.mark.parametrize("mutation", [
    "binding", "header", "protected-cell", "formula", "hidden-row",
    "extra-row", "missing-decision", "duplicate-member", "bad-partition",
])
def test_validation_fails_closed_on_workbook_mutation(
    synthetic_inputs, complete_sidecar, mutation
):
    mutate_sidecar(complete_sidecar, mutation)
    with pytest.raises(NormalizationBlocked):
        validate_correction_workbook(
            path=complete_sidecar,
            blocked_plan=synthetic_inputs.blocked_plan,
            previous=synthetic_inputs.previous,
            incoming=synthetic_inputs.incoming,
            bindings=synthetic_inputs.bindings,
        )
```

Add identical-path, symlink, hardlink, output-exists, temp-substitution, and
pre/post-publication fsync tests. Output JSON must not exist after prepublish
failure and must be complete/canonical after successful publication.

- [ ] **Step 3: Run the Task 2 RED suite**

```bash
env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python \
  -m pytest import/tests/test_workbook_refresh_corrections.py -q
```

Expected: FAIL because the sidecar CLI does not exist.

- [ ] **Step 4: Implement generation and validation**

The CLI shape is exact:

```bash
python import/workbook_refresh_corrections.py generate \
  --plan BLOCKED_PLAN --expected-plan-sha256 PLAN_SHA \
  --previous-workbook PREVIOUS.xlsx --incoming-workbook INCOMING.xlsx \
  --checklist merges.csv --year 2026 --dsn LOCAL_READ_ONLY_DSN \
  --out-xlsx owner-corrections.xlsx

python import/workbook_refresh_corrections.py validate \
  --plan BLOCKED_PLAN --expected-plan-sha256 PLAN_SHA \
  --previous-workbook PREVIOUS.xlsx --incoming-workbook INCOMING.xlsx \
  --checklist merges.csv --year 2026 --dsn LOCAL_READ_ONLY_DSN \
  --sidecar owner-corrections.xlsx --out-json owner-corrections.json
```

Both commands establish `default_transaction_read_only=on`, fetch the same
database snapshot as the planner, recompute all bindings, and validate paths
before reading workbook/checklist/DB content. Use unique descriptor-bound
temporary outputs, file fsync, atomic replace, and containing-directory fsync.
Generation refuses any existing destination. Validation opens Excel with
`data_only=False` so formulas cannot masquerade as values.

- [ ] **Step 5: Run focused and combined tests**

```bash
env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python \
  -m pytest import/tests/test_workbook_refresh_normalization.py \
            import/tests/test_workbook_refresh_corrections.py -q
env -u GIT_INDEX_FILE git diff --check
```

Expected: PASS; source hashes before/after are identical.

- [ ] **Step 6: Commit and review Task 2**

```bash
env -u GIT_INDEX_FILE git add \
  import/workbook_refresh_corrections.py \
  import/tests/test_workbook_refresh_corrections.py \
  import/tests/refresh_test_support.py
env -u GIT_INDEX_FILE git commit -m "feat(import): generate owner correction sidecars"
```

Obtain fresh specification PASS, then fresh quality APPROVED.

---

### Task 3: Pure Planner Normalization

**Files:**
- Modify: `import/workbook_refresh.py`
- Modify: `import/tests/test_workbook_refresh_plan.py`
- Modify: `import/tests/make_refresh_fixture.py`
- Modify: `import/tests/refresh_test_support.py`

**Interfaces:**
- Consumes: `NormalizationOverrides | None` from Task 1.
- Produces: normalization-aware `build_refresh_plan(..., normalization_overrides=None)`, `RefreshPlan.normalization_overrides_sha256`, and `RefreshPlan.normalizations`.

- [ ] **Step 1: Write the 12 exact-rule tests**

Extend the synthetic fixture support with `mutate_unheaded_value()` and add a
test-local `quarantine_reasons()` helper. Add one positive and at least one
predicate-flip test for each rule family:

```python
def test_nonnumeric_derived_allowlist_becomes_audit_not_action(inputs, overrides):
    plan = build_refresh_plan(*inputs, normalization_overrides=overrides)
    audit = next(a for a in plan.normalizations if a.rule_code == "derived-not-comparable/v1")
    assert audit.effect == "warning-only:no-write:no-direction"
    assert not any(a.fact_id == audit.fact_id and a.disposition is Disposition.QUARANTINE for a in plan.actions)


def test_changed_unheaded_value_restores_quarantine(inputs, overrides):
    changed = mutate_unheaded_value(inputs)
    plan = build_refresh_plan(*changed, normalization_overrides=overrides)
    assert quarantine_reasons(plan) == {"unheaded-cell-changed"}
```

For consolidation annotations, prove exact grammar, one same-group numeric
reference, retained allocation, and exactly one placement amount. Mutation of
grammar, reference uniqueness, group, or numeric amount must restore
quarantine.

- [ ] **Step 2: Write owner-decision and summary-order tests**

Test all-missing groups, whole-group decisions, explicit partitions, missing
product/date injection at the parsed-fact layer, complete component inventory,
and summaries recomputed only after upstream decisions. Keep majority/first/
prior-workbook/DB carry-forward tests as explicit rejection pins.

- [ ] **Step 3: Run planner RED**

```bash
env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python \
  -m pytest import/tests/test_workbook_refresh_plan.py -q
```

Expected: FAIL because the planner has no override/audit interface.

- [ ] **Step 4: Implement normalization-aware planning**

Extend the plan without weakening the default path:

```python
@dataclasses.dataclass(frozen=True)
class RefreshPlan:
    # existing fields unchanged
    normalization_overrides_sha256: str | None = None
    normalizations: tuple[NormalizationAudit, ...] = ()


def build_refresh_plan(
    previous: WorkbookSnapshot,
    incoming: WorkbookSnapshot,
    database: DatabaseSnapshot,
    *,
    checklist_sha256: str,
    parser_commit: str,
    normalization_overrides: NormalizationOverrides | None = None,
) -> RefreshPlan:
    """Validate overrides, normalize immutable inputs, and classify actions."""
```

Validate all bindings before any classification. Create audit entries instead
of mutating source snapshots in place. Owner product/date decisions create a
new immutable normalized snapshot. Group decisions are passed explicitly into
`_resolve_ppl_groups`; summaries run after that resolution. Re-derive the
component inventory from normalized facts and preserve the exact inventory ↔
action bijection.

When `normalization_overrides is None`, canonical actions/blockers must equal
the pre-task baseline. Do not special-case the real hashes or counts in
production.

`build_refresh_plan()` also accepts
`expected_normalization_implementation_commit: str | None = None`. When an
override is present, this argument is mandatory and must equal the override's
bound implementation commit; it is supplied independently by the caller. Task
4 passes the current clean `resolve_parser_commit()` result. The override's
three automatic reason-class digests must exactly equal freshly derived
candidate fact sets before any predicate can normalize them.

When overrides are present, the returned `RefreshPlan.parser_commit` is the
independently supplied expected normalization-implementation commit. The
blocked source plan's parser commit remains only in the canonical override
bindings transitively covered by `normalization_overrides_sha256`; apply's
existing current-HEAD check is not relaxed.

Task 3 corrective scope may also modify
`import/workbook_refresh_corrections.py` and
`import/tests/test_workbook_refresh_corrections.py` solely to populate and test
the automatic reason-class digests in the existing
`NormalizationBindings.reason_fact_set_sha256` field.

- [ ] **Step 5: Run focused and full planner suites**

```bash
env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python \
  -m pytest import/tests/test_workbook_refresh_plan.py \
            import/tests/test_workbook_refresh_normalization.py -q
env -u GIT_INDEX_FILE git diff --check
```

Expected: PASS.

- [ ] **Step 6: Commit and review Task 3**

```bash
env -u GIT_INDEX_FILE git add \
  import/workbook_refresh.py \
  import/tests/test_workbook_refresh_plan.py \
  import/tests/make_refresh_fixture.py \
  import/tests/refresh_test_support.py
env -u GIT_INDEX_FILE git commit -m "feat(import): normalize approved workbook anomalies"
```

Obtain fresh specification PASS, then fresh quality APPROVED.

---

### Task 4: Planner CLI And Apply Compatibility

**Files:**
- Modify: `import/plan_workbook_refresh.py`
- Modify: `import/apply_workbook_refresh.py`
- Modify: `import/tests/test_workbook_refresh_plan_cli.py`
- Modify: `import/tests/test_workbook_refresh_apply.py`

**Interfaces:**
- Consumes: Tasks 1–3 override loader and normalization-aware plan.
- Produces: optional planner CLI input, canonical plan/report binding, and applier/evidence compatibility without any sidecar input.

- [ ] **Step 1: Write CLI path and read-order tests**

Add `--normalization-overrides` as optional. Test absent behavior, valid JSON,
invalid schema, wrong hash binding, identical/symlink/hardlink collision with
every existing input/output, stat failures, and that all path validation occurs
before checklist/workbook/DB reads.

```python
def test_cli_passes_validated_overrides_to_planner(
    monkeypatch, cli_paths, overrides, overrides_path
):
    captured = {}

    def capture(*args, **kwargs):
        captured["overrides"] = kwargs["normalization_overrides"]
        return _pure_output_plan()

    monkeypatch.setattr(plan_workbook_refresh, "build_refresh_plan", capture)
    assert main(_cli_args(cli_paths) + ["--normalization-overrides", str(overrides_path)]) == 0
    assert captured["overrides"].bindings.plan_sha256 == overrides.bindings.plan_sha256
```

- [ ] **Step 2: Write canonical apply/evidence tests**

Construct a normalization-aware plan, write canonical bytes, reload through
the applier, and require byte identity. Assert `plan_evidence_payload()` carries
the override SHA and canonical normalization audits. Reject unknown/missing
audit fields and edited JSON.

- [ ] **Step 3: Run Task 4 RED**

```bash
env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python \
  -m pytest import/tests/test_workbook_refresh_plan_cli.py \
            import/tests/test_workbook_refresh_apply.py -q
```

Expected: FAIL on absent CLI/load/evidence support.

- [ ] **Step 4: Implement the bounded integration**

Add the optional parser argument and include the override path in
`_require_disjoint_paths` only when present. Add all new product/test paths to
`REVIEWED_SCOPE_PATHS` so plans bind a clean reviewed implementation. Load and
validate canonical override JSON before the read-only DB snapshot is used to
build the plan.

Update `_load_plan()` and `plan_evidence_payload()` to reconstruct and carry
`NormalizationAudit`, `normalization_overrides_sha256`, and
`normalizations`. The applier receives no `--sidecar` or override argument and
never opens editable Excel.

- [ ] **Step 5: Run focused and full import suites**

```bash
env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python \
  -m pytest import/tests/test_workbook_refresh_plan_cli.py \
            import/tests/test_workbook_refresh_apply.py -q
env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python \
  -m pytest import/tests -q
env -u GIT_INDEX_FILE git diff --check
```

Expected: PASS with synthetic values only.

- [ ] **Step 6: Commit and review Task 4**

```bash
env -u GIT_INDEX_FILE git add \
  import/plan_workbook_refresh.py \
  import/apply_workbook_refresh.py \
  import/tests/test_workbook_refresh_plan_cli.py \
  import/tests/test_workbook_refresh_apply.py
env -u GIT_INDEX_FILE git commit -m "feat(import): bind normalization overrides into refresh plans"
```

Obtain fresh specification PASS, then fresh quality APPROVED.

---

### Task 5: Product Truth And Owner Operations

**Files:**
- Modify: `DECISIONS.md` (append ADR-009; never edit prior ADR text)
- Modify: `ARCHITECTURE.md`
- Modify: `OPERATIONS.md`
- Modify: `docs/MANUAL.md`

**Interfaces:**
- Consumes: reviewed Tasks 1–4 and fresh executed synthetic evidence.
- Produces: exact sidecar generation/validation/replan commands and Korean owner instructions.

- [ ] **Step 1: Collect fresh tracked facts**

```bash
env -u GIT_INDEX_FILE find import -maxdepth 1 -name '*.py' -print | sort
env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python \
  -m pytest import/tests -q
env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python \
  -m pytest db/tests -q
env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python \
  -m pytest tests/unit -q
```

Record only outputs produced by these commands; never copy real business
values into docs.

- [ ] **Step 2: Append ADR-009 and update architecture**

ADR-009 records the hybrid lossless-first choice, sidecar-vs-source-copy
decision, 12/68/3 authority split, canonical JSON boundary, and rejected broad
heuristics. Architecture names both new modules, audit fields, read-only DB
binding, ignored artifacts, and the applier's no-Excel boundary.

- [ ] **Step 3: Add exact operations and Korean owner procedure**

Document the two Task 2 CLI commands, the planner's
`--normalization-overrides`, owner-editable columns, complete partition rule,
validation failure meanings, and the mandatory stop while 68 inputs are blank.
Use absolute real paths only in local operator examples and label them local-
only. State that an incomplete sidecar cannot authorize scratch or canonical
apply.

- [ ] **Step 4: Verify and commit docs**

```bash
env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python \
  scripts/check_doc_claims.py ARCHITECTURE.md OPERATIONS.md docs/MANUAL.md DECISIONS.md
env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python scripts/ci_smoke.py
env -u GIT_INDEX_FILE git diff --check
env -u GIT_INDEX_FILE git add DECISIONS.md ARCHITECTURE.md OPERATIONS.md docs/MANUAL.md
env -u GIT_INDEX_FILE git commit -m "docs(import): document owner correction sidecars"
```

Obtain fresh specification PASS, then fresh quality APPROVED.

---

### Task 6: Cumulative Verification And Real Blank Sidecar

**Files:**
- Local only: `.superpowers/sdd/workbook-refresh.owner-corrections.xlsx`
- Local only: regenerated blocked plan/report and hash-only verification report
- Pipeline mailbox: one cumulative Director verify-request after Tasks 1–5 pass

**Interfaces:**
- Consumes: reviewed Tasks 1–5 range and existing Task 7 read-only token inputs.
- Produces: cumulative Operator request plus the blank local owner sidecar; no override JSON and no apply.

- [ ] **Step 1: Run all synthetic and smoke gates**

```bash
env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python -m pytest db/tests -q
env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python -m pytest import/tests -q
env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python -m pytest tests/unit -q
env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python scripts/ci_smoke.py
```

Require scratch catalog cleanup, clean target status, and no tracked generated
artifacts.

- [ ] **Step 2: Generate the real blank sidecar under a fresh read-only token**

Use the exact blocked plan hash and real paths from the approved Task 7 token:

```bash
env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python \
  import/workbook_refresh_corrections.py generate \
  --plan .superpowers/sdd/workbook-refresh.plan.json \
  --expected-plan-sha256 8f2acb186c7b2fedafc450f8f22863a1d35fc4b7247d3da26fbcb83f6da9cac1 \
  --previous-workbook /Users/hyungkoookkim/evidence-ledger/data/홈쇼핑분석.xlsx \
  --incoming-workbook /Users/hyungkoookkim/Downloads/260710.xlsx \
  --checklist /Users/hyungkoookkim/evidence-ledger/data/merges.csv \
  --year 2026 --dsn postgresql://postgres:postgres@127.0.0.1:54322/postgres \
  --out-xlsx .superpowers/sdd/workbook-refresh.owner-corrections.xlsx
```

Require exactly 68 owner decisions, 12 audit-only rows, 3 summary gates, source
hashes unchanged, DB/evidence fingerprints unchanged, and target git clean.

- [ ] **Step 3: Prove the blank sidecar cannot validate**

Run `validate` against the blank workbook. Expected: nonzero exit with only
missing-decision counts/reason classes; no override JSON created.

- [ ] **Step 4: Send cumulative verify-request and stop**

The Director verify-request names the exact implementation range, per-task
reviews, all test commands, real sidecar SHA-256, inventory counts, unchanged
canonical hashes/fingerprints, ignored output paths, and no-apply boundary.
Operator verifies code and blank-sidecar generation under a separate read-only
token and returns GO/NITS/FAIL.

After Operator GO, notify all seats that the engineering slice is complete and
the owner-input gate is active. Do not request scratch/apply authority until the
user completes the 68 editable decisions and the sidecar validates.

---

## Spec Coverage Self-Review

| Approved specification requirement | Plan coverage |
|---|---|
| Hash-bound immutable correction/override model | Task 1 |
| Exact six visible sheets plus `_Bindings` | Task 2 |
| Atomic alias-safe Excel/JSON publication | Task 2 |
| 12 exact deterministic rules and predicate flips | Task 3 |
| 50 missing-month, 14 nested group, and 4 missing-field decisions | Tasks 1–3 |
| Three summary controls recomputed last | Task 3 |
| Optional planner input with unchanged default behavior | Tasks 3–4 |
| Canonical plan/apply/evidence compatibility | Task 4 |
| Owner operations, Korean procedure, and append-only decision record | Task 5 |
| Real blank sidecar, owner-input stop, cumulative verification, and all-seat notice | Task 6 |
| Local-only privacy and no canonical/scratch/push side effects | Global constraints and Task 6 |

Self-review found no uncovered requirement. Type names are consistent across
Tasks 1–4: conflicting member rows canonicalize into one
`ConflictingGroupDecision` with nested `GroupMemberAssignment` values, so the
manual decision inventory remains exactly 50 + 14 + 4 = 68.

## Completion Boundary

This implementation plan is complete only when Tasks 1–5 are committed with
fresh specification PASS and quality APPROVED, cumulative Operator verification
is GO for the exact range, the real blank sidecar is generated and hash-bound,
all source/canonical fingerprints are unchanged, and all seats are notified of
the owner-input stop. Completion does not mean the database/resource refresh is
complete; the original refresh resumes only after the user completes the 68
owner decisions and a regenerated plan reaches zero blockers.
