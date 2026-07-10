# Evidence-Ledger Workbook Refresh Design

**Status:** user-approved design, awaiting written-spec review

**Approved direction:** source-scoped, provenance-preserving differential refresh

**Governance home:** Pipeline coordinator route and acceptance contract

**Product target:** `/Users/hyungkoookkim/evidence-ledger`

## 1. Objective

Use `/Users/hyungkoookkim/Downloads/260710.xlsx` to refresh the local
evidence-ledger database and the canonical local workbook resource without
replaying the cumulative workbook as a second import.

The refresh must produce one coherent direction of truth across the workbook,
the operational database, the agency comparison lane, and the decision
readout. It must preserve later human evidence, keep agency facts separate,
retain prior workbook provenance, and stop rather than guess when the sources
cannot be reconciled safely.

This document is the coordinator-owned route and acceptance contract. Product
implementation truth remains in evidence-ledger code, migrations, tests, and
local evidence artifacts created by the routed Director.

## 2. Authority Decision

The user approved this source-scoped authority rule:

1. The new workbook supersedes the previous workbook only for facts owned by
   the internal `excel_import` lane.
2. Later human-entered or human-corrected database evidence is never silently
   overwritten. A disagreement with later human evidence is a blocking
   conflict for owner review.
3. Agency-sourced placements and allocations remain a separate reconciliation
   lane. The internal workbook cannot rewrite them or make them enter P&L
   arithmetic.
4. Database-only records survive when they are absent from the new workbook.
   Absence is recorded as `preserve_db_only`, never interpreted as deletion.
5. Database views and formulas are authoritative for computed metrics. Cached
   workbook formulas are reconciliation controls, not independent facts.
6. The `PPL 지급 요약` sheet is accepted only when it reconciles with the
   normalized workbook detail under the documented payment-month rule. A
   mismatch blocks the refresh.

## 3. Scope

### In scope

- Preserve and version the old and new local workbook resources by content
  hash without committing either workbook.
- Compare the previous canonical workbook, the new workbook, and the live
  database through one deterministic planner.
- Insert genuinely new workbook-owned slots.
- Apply workbook-owned slot corrections with append-only before/after evidence
  and optimistic baseline checks.
- Append result corrections through the existing result-supersession chain.
- Correct internal-lane PPL payments, placements, and allocations with
  append-only before/after evidence and guarded operational updates.
- Produce a local-only directional report that unifies internal workbook,
  database, and agency reconciliation signals.
- Notify all four seats through one consolidated coordinator route after the
  design and implementation plan are approved.

### Out of scope

- Deleting or retiring database-only rows.
- Rewriting human-entered facts or agency-sourced facts.
- Treating an Excel row number as a stable record identifier.
- Loading malformed marker rows, unheaded cells, or formula errors as facts.
- Committing real workbook contents, real-data reports, credentials, or local
  database dumps.
- Push, remote publication, production deployment, paid services, or any
  remote database mutation.
- Reusing a stale normal checkout or an old task worktree as the new route.

## 4. Source-Of-Truth Matrix

| Fact | Authority | Conflict disposition |
|---|---|---|
| Human form entry or correction | Latest valid human evidence | Preserve it; report workbook disagreement |
| Internal workbook baseline | New approved workbook | Refresh only `excel_import`-owned facts |
| Result correction | Existing immutable revision chain | Append a superseding result with a reason |
| Slot and internal PPL correction | New workbook plus exact old-value check | Record before/after evidence, then guarded update |
| Agency placement/allocation | Agency lane | Reconcile separately; never overwrite |
| Calculated P&L and ratios | Current database views | Workbook cached formulas are comparison controls |
| Monthly PPL payment | Normalized workbook detail reconciled to summary | Block on disagreement |
| Database-only row | Database | Preserve and label in the plan |

## 5. Components

### 5.1 Local resource versioning

The incoming workbook remains unchanged at its user-provided path. The refresh
executor computes the full SHA-256 of the incoming and canonical workbooks,
copies the previous canonical workbook to a date-and-hash-named file under the
existing ignored `data/archive/` convention, and stages the new workbook beside
the canonical target.

An ignored local manifest under `.superpowers/sdd/` records:

- incoming, previous-canonical, archive, staged, and canonical paths;
- full old and new workbook hashes;
- parser commit, refresh-plan hash, database baseline hash, and evidence IDs;
- activation phase and any compensating recovery action.

The canonical `data/홈쇼핑분석.xlsx` changes only inside the final authorized
activation command. Pre-staged copies are hash-verified before the database
transaction begins.

### 5.2 Deterministic refresh planner

The product implementation adds one pure planning module and CLI. The planner
accepts the previous workbook, the new workbook, a read-only database snapshot,
the signed entity checklist, and an explicit year. It emits canonical JSON and
a human-readable local report from the same in-memory plan.

The canonical JSON is stable under repeated execution and is hashed before any
write. Each parsed workbook fact receives exactly one disposition:

- `unchanged`
- `insert_slot`
- `revise_slot`
- `supersede_result`
- `revise_ppl_payment`
- `revise_ppl_placement`
- `revise_ppl_allocation`
- `preserve_db_only`
- `conflict_human_newer`
- `ambiguous_identity`
- `quarantine`

Matching first proves that the previous workbook hash is bound to the existing
import-root evidence. It then bridges the previous workbook rows to database
records using the prior source reference plus a canonical natural-key
consistency check. The new workbook is matched to that proven baseline through
normalized business identity, never by its row number alone. Any duplicate or
non-unique candidate becomes `ambiguous_identity`.

The planner performs no database, workbook, or resource writes. It refuses to
produce an applicable plan when entity variants are uncovered, human conflicts
exist, the baseline cannot be proven, or the workbook summary and normalized
detail disagree.

Payment-month normalization is deterministic. After the existing placement
grouping/deduplication rule has identified one placement amount, an explicit
`지급월` wins; otherwise a parseable `PPL비용지급일` supplies the month. The
planner never falls back to broadcast month. An amount-bearing placement with
no usable payment month, conflicting months inside one placement group, or a
detail-derived monthly sum that differs from `PPL 지급 요약` becomes a blocking
quarantine. The summary is a reconciliation control, not a second amount to
load.

### 5.3 Guarded refresh applier

The product implementation adds one explicit apply command. It requires the
approved canonical plan, the exact incoming workbook, the expected old and new
hashes, the expected live database fingerprint, the signed checklist, an
entered-by identity, and an affirmative apply flag.

The command:

1. Recomputes every supplied hash and rejects a stale or edited plan.
2. Acquires a transaction-scoped advisory lock for the internal workbook/year.
3. Re-runs the read-only database fingerprint and all conflict gates.
4. Appends a `workbook_refresh_plan` evidence row containing the canonical plan
   hash and complete before/after facts.
5. Uses the existing slot validation path for new slots.
6. Uses the existing result RPC to append superseding result revisions with a
   workbook-refresh reason.
7. Applies slot and internal-PPL corrections only when every affected row still
   equals the plan's expected old values. Agency rows are ineligible.
8. Appends a `workbook_refresh_result` evidence row with applied dispositions,
   report hashes, resource hashes, and verification facts.
9. Atomically activates the staged canonical resource while the database
   transaction is still recoverable.
10. Commits only after the canonical resource hash matches the new workbook.

If database commit fails after resource activation, the command restores the
canonical workbook from the preverified archive and records the recovery in
the ignored manifest. If resource activation fails, the database transaction
rolls back. The same new workbook hash cannot be applied twice.

### 5.4 Directional analysis

After a successful scratch run and again after canonical activation, a
committed measurement command writes a local-only Markdown and machine-readable
report. It extends the existing cross-source reconciliation language rather
than creating a second interpretation of the same totals.

The report separates:

- schedule additions and workbook-owned corrections;
- result direction and computed P&L direction;
- internal PPL payment and allocation direction;
- agency-only reconciliation differences;
- preserved human/database-only facts;
- quarantines, conflicts, and unresolved owner decisions.

Tracked docs and mailbox events cite only report hashes, dispositions, and
verification commands. They do not embed sensitive business amounts.

## 6. Data Flow

```text
incoming workbook + previous canonical workbook
                 + signed entity checklist
                 + read-only live DB snapshot
                              |
                              v
                 deterministic refresh planner
                              |
                    canonical plan + hash
                              |
                  scratch database application
                              |
                tests + reconciliation + review
                              |
                 authorized guarded activation
                    /                       \
          DB transaction/evidence       resource swap
                    \                       /
                              v
                 unified local-only readout
```

The scratch and canonical executions use the same plan format and apply code.
Only the target database and side-effect token differ.

## 7. Stop Conditions And Recovery

The refresh makes no canonical change when any of these occurs:

- local database or required service is unavailable;
- old import-root evidence or workbook hash is missing or inconsistent;
- the live database fingerprint differs from the approved plan;
- a natural key is duplicate, missing, or ambiguous;
- a later human fact conflicts with the workbook;
- a checklist decision is missing or a loader write variant is uncovered;
- a load-bearing workbook value is malformed or formula-derived controls do
  not reconcile;
- an unheaded value lacks an explicit disposition;
- the plan, workbook, report, or resource hash changes;
- the trust chain fails verification;
- scratch execution, independent review, or Operator verification is not GO.

All database writes occur in one transaction. The executor retains the old
resource and an explicit recovery manifest until post-activation verification
passes.

## 8. Testing And Verification

Implementation follows TDD with synthetic fixtures that contain no real
business values.

### Pure planner tests

- stable canonical JSON and plan hash;
- shifted Excel row numbers do not change identity;
- new row, slot correction, result correction, and each PPL correction class;
- later human evidence becomes a blocking conflict;
- database-only facts are preserved;
- duplicate or ambiguous identities fail closed;
- checklist coverage, marker rows, formula errors, and unheaded values;
- detail-to-monthly-summary disagreement blocks application.

### Database and resource integration tests

- no duplicate historical slot is inserted;
- result changes append the correct same-slot supersession;
- optimistic old-value mismatch rolls back everything;
- only internal-lane PPL rows are eligible for correction;
- trust evidence stores the exact plan and before/after facts;
- second application of the same workbook is rejected;
- resource activation failure rolls back the database;
- database commit failure restores the previous canonical resource;
- trust-chain, report-hash, and canonical-resource checks pass after success.

### Required acceptance evidence

- focused unit and integration selectors;
- full evidence-ledger import and database suites;
- project smoke and documentation freshness;
- scratch-database plan/apply/reconcile output;
- canonical preflight with zero conflicts and zero ambiguities;
- post-activation cross-source directional report;
- independent Operator mutation checks and GO for the exact implementation
  range.

Ad-hoc discovery counts are not acceptance evidence. Gate counts and business
measurements must come from the committed planner or measurement command and
persist only in the approved local evidence paths.

## 9. Four-Seat Routing

The coordinator sends one consolidated all-seat route only after this written
spec and its implementation plan are approved. The route must reconcile the
then-current control-plane cycle rather than overwrite it.

Capacity decision: one implementation pair plus Pair-B preflight. Planner,
applier, migration, and resource activation share one data contract and are too
tightly coupled for parallel implementers.

- **Director:** create the isolated evidence-ledger worktree from a freshly
  pinned published base; implement the planner, applier, schema/evidence seam,
  tests, and local measurement command; obtain fresh spec and quality review;
  send one verify-request.
- **Operator:** independently verify the exact range, run mutation flips,
  challenge idempotence/rollback/source-priority behavior, and return GO/NITS/
  FAIL. Operator does not repair the diff.
- **Director2:** preflight the identity, source-priority, migration, and
  before/after evidence contract without product edits.
- **Operator2:** preflight scratch/canonical execution safety, resource
  recovery, privacy, and test feasibility without starting services or
  mutating data.
- **Coordinator:** own the consolidated route, side-effect executor tokens,
  joins, and final reconciliation. Coordinator authors no product fix.

Separate target-bound executor tokens are required for:

1. evidence-ledger worktree creation;
2. local service or pod start;
3. scratch-database mutation;
4. canonical local database plus resource activation.

The Director is the sole executor for product-local actions. Other seats are
observers unless their routed verification scope requires read-only access.
No token grants push, remote update, production generation, or publication.

## 10. Acceptance Criteria

The cycle is complete only when:

- every emitted workbook fact has exactly one deterministic disposition;
- no ambiguous, uncovered, or unresolved human-conflict disposition remains;
- the live database still matches the approved baseline at activation time;
- workbook-owned updates apply without duplicating historical slots;
- human, agency, and database-only facts remain unchanged;
- result corrections use the immutable supersession chain;
- slot and PPL corrections have append-only before/after evidence;
- the old workbook remains recoverable and the canonical resource hash equals
  the applied new-workbook hash;
- the same workbook cannot be applied twice;
- trust-chain and directional reconciliation checks pass;
- Operator returns GO for the exact implementation range;
- one consolidated coordinator closeout cites all evidence and leaves push and
  remote publication unperformed.

## 11. Design Evidence

The current one-time import shape was verified during design discovery with:

```text
$ rg -n "_lock_import_root|record_slot|ON CONFLICT \(pay_month\) DO NOTHING" import supabase/migrations
-> the internal rerun guard is byte-hash scoped, slots use the insert path, and
   existing monthly payments ignore conflicts.

$ env -u GIT_INDEX_FILE .venv/bin/python import/run_import.py --help
-> the existing public interface exposes one cumulative workbook import path;
   it has no differential-refresh mode.
```

These commands explain why the approved design adds a planner and guarded
refresh path instead of invoking the current importer directly. Exact runtime
inventory and business measurements must be regenerated by the committed
instrument on the routed evidence-ledger base.
