# Coordinator → All: route Packet 3 import and database invariants

**When:** 2026-07-21T02:40:20Z · **From:** coordinator (online)

Task-board: ledger-audit-remediation-packet3-import-invariants-2026-07-21
Task ID: ledger-audit-remediation-packet3-import-invariants-2026-07-21
Status: ACTIVE — PACKET 3 IMPORT AND DATABASE INVARIANTS
Route generation: 10
Supersedes route: coordination/mailbox/sent/2026-07-21T02-15-05Z-coordinator-to-all-coordination.md
Expected control HEAD: 77a5a42dbb6db37225f2f7d2d1c83cb55b24ab08
Superseded route ref: coordination/mailbox/sent/2026-07-21T02-15-05Z-coordinator-to-all-coordination.md@f69f0ec328ca42dcc572fb3d9cddd8d89c114f82
Authorization source: user-task:approved-evidence-ledger-audit-remediation-2026-07-21; user-task:continue-ledger-task-2026-07-21
Accepted Packet 2 GO: coordination/mailbox/sent/2026-07-21T01-15-02Z-operator2-to-all-verification-report.md@7b16985e74201fe572e32c132f2678c498aa5c65
Accepted Packet 2 integration evidence: coordination/mailbox/sent/2026-07-21T02-25-18Z-director-to-all-coordination.md@77a5a42dbb6db37225f2f7d2d1c83cb55b24ab08
Approved design: docs/superpowers/specs/2026-07-21-evidence-ledger-audit-remediation-design.md@c8d74fb5c15b8b016001a641d33b9d52c0269451
Approved design SHA-256: bde185a3cefaaadca98cf1eafd841c212edf66d54ba679422bafcfe6274dbfec
Packet 3 plan: docs/superpowers/plans/2026-07-21-evidence-ledger-import-database-invariants.md@c8d74fb5c15b8b016001a641d33b9d52c0269451
Packet 3 plan SHA-256: 59e333505a3b83da6acb04b7370b892804bedf81b9b772be80d431956e78ebb9
Target repository: /Users/hyungkoookkim/evidence-ledger
Target worktree: /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-audit-remediation-import-invariants
Target branch: codex/audit-remediation-import-invariants
Target base: 538c9dab07e93ada190ef318ec06dc225ec54b3b
Accepted target HEAD: 538c9dab07e93ada190ef318ec06dc225ec54b3b
Protected normal-checkout settings SHA-256: a40fae4d05b28d9ec2be89cb36c29f02bc46e3839ccb09af08a6aa4bab70c1e4
Implementation owner/model: director / gpt-5.6-sol
Assigned non-author reviewer/model: operator2 / gpt-5.6-terra

## Outcome Contract

Execute the approved Packet 3 plan test-first in one dedicated target worktree.
New internal source references become workbook-hash-bound; reconciliation uses
the emitted reference unchanged; contradictory aliases fail closed before
materialized writes and are rechecked after race-safe insertion; negative agency
cost remains evidence but blocks before database connection; checklist proposal
creation becomes exclusive and byte-preserving; and the existing hermetic import
lane plus operator documentation are refreshed truthfully.

Keep ownership of the current architecture. Use only the existing Python
standard library and repository dependencies. This packet adds no framework,
service, migration, backfill, overwrite switch, refund inference, or new approval
ceremony.

## Director Autonomous Contract Revision 11

Before target mutation, Director publishes exactly one fresh director-to-all
coordination event through the fixed writer and commits only that event. It uses:

- Task ID: ledger-audit-remediation-packet3-import-invariants-2026-07-21
- Outcome contract: Execute the approved Packet 3 plan test-first in one dedicated target worktree, create exactly two verified target commits, and submit the immutable actual range for independent Operator2 review.
- Parent contract: this committed generation-10 Coordinator route's exact path at its full commit SHA
- Contract revision: 11
- Previous owners: director
- Owners: director
- Proposal ref: self-candidate
- Acceptance refs: self-candidate
- Finding refs: the full immutable ref of this route plus sha256:bde185a3cefaaadca98cf1eafd841c212edf66d54ba679422bafcfe6274dbfec and sha256:59e333505a3b83da6acb04b7370b892804bedf81b9b772be80d431956e78ebb9

Director proves the contract effective and global route lineage valid, then runs
the ordinary ledger Director start guard against that exact committed event.
Director uses the existing compatible Director Codex task and directly executes
the written plan; a child implementer is outside scope.

## Side-Effect Executor Token

- effect: local branch and worktree creation
- executor: director
- target: /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-audit-remediation-import-invariants
- scope: branch=codex/audit-remediation-import-invariants, parent=538c9dab07e93ada190ef318ec06dc225ec54b3b

## Target Allowed Paths

- import/tests/test_parse_workbook.py
- import/tests/test_reconcile_unit.py
- import/parse_workbook.py
- import/run_import.py
- import/alias_integrity.py
- import/tests/test_alias_integrity_unit.py
- import/load_staging.py
- import/load_agency.py
- import/tests/test_parse_agency_schedule.py
- import/tests/test_run_import_unit.py
- import/parse_agency_schedule.py
- import/tests/test_propose_merges.py
- import/propose_merges.py
- .github/workflows/ci.yml
- ARCHITECTURE.md
- OPERATIONS.md

`import/reconcile.py` is verify-only and must not change. Every other target path
is frozen. All fixtures and probes are synthetic. The normal checkout's
pre-existing `.vscode/settings.json` remains untracked and byte-identical at the
protected hash above.

## Exact Preflight

Director stops without target mutation unless one fresh observation proves:

- Pipeline contains this exact committed route and its effective revision-11
  Director child; route validation, global lineage, and ledger start guard pass;
- evidence-ledger normal `main` and HEAD equal the accepted target head, with
  `.vscode/` as its only status entry and the protected settings hash unchanged;
- the authorized target worktree path and branch do not already exist;
- the approved design and Packet 3 plan bytes match their stated SHA-256 values;
- target base `538c9dab07e93ada190ef318ec06dc225ec54b3b` is available locally; and
- no separately authorized local database stack is required or inferred.

Director creates only the exact local branch/worktree in the token, confirms the
new worktree is clean at the exact parent, then executes the plan in order.

## Exact Implementation Contract

### 1. Workbook-bound internal identity

Compute the workbook SHA-256 once in `parse_workbook.parse`, return it through
`ParseOutput`, and emit every new internal row/anomaly reference as
`sha256:<64hex>:방송스케줄!rN`. `run_import` reuses that parsed digest.
Reconciliation must pass the complete emitted source reference unchanged.

### 2. Fail-closed alias integrity

Add one shared `alias_integrity.py` contract with fixed query mappings for
channel, product, tv_show, and producer. Both loaders must validate all proposed
alias bindings before the first canonical INSERT, aggregate contradictions, and
perform an authoritative target re-read after `ON CONFLICT DO NOTHING` so a race
either proves the same identity or rolls back the transaction.

### 3. Negative-cost pre-connect block

Retain an exact negative Decimal cost as evidence, emit typed `negative_cost`,
and stop the agency import before DSN construction or `psycopg.connect`. Do not
invent credit or refund semantics.

### 4. Exclusive checklist proposal

Create proposal CSVs with exclusive mode `x`. A pre-existing owner file must
raise `FileExistsError` with every existing byte unchanged. Do not add force,
overwrite, backup, suffix, or deletion behavior.

### 5. Hermetic lane and truthful docs

Add the alias-integrity, run-import, and reconciliation unit suites to the
existing import-hermetic CI lane. Keep checklist coverage for Packet 4. Record
the collection count emitted by pytest rather than guessing it, update both
architecture verification stamps against the exact route parent, repair anchors,
and document the operator-visible fail-closed behavior.

## TDD, Commits, And Verification

For each behavior, Director records a focused failing test before production
implementation, then the passing selector. Director creates exactly two local
target commits in this order:

1. `fix(import): bind rows to workbook identity`
2. `fix(import): fail closed on unsafe owner inputs`

The final range must be exactly two commits after the target base and may contain
only the 16 allowed paths. Stage explicit pathspecs only and preserve unrelated
state.

On committed bytes, run the exact Packet 3 hermetic profile from the approved
plan, the emitted collection-count command, document-claim and architecture
freshness checks, target `scripts/ci_smoke.py`, `git diff --check`, exact range
and path manifest checks, and clean-worktree checks. All required suites pass
without skip, xfail, Postgres contact, service launch, or private data.
Record `not run: local-stack authority absent` for optional scratch-database
tests; this is not an acceptance gap because the routed contract is hermetic.

## Independent Review Contract

After every committed-byte gate passes, Director publishes exactly one immutable
verify-request assigned to non-author Operator2 and dispatches the existing
compatible Operator2 Codex task exactly once. The request binds the target
repository, exact base/head/two-commit range, 16-path manifest, author and
reviewer identities, RED/GREEN evidence, exact test counts, docs/smoke evidence,
and distinct finding refs for:

- hash-bound source identity;
- exact reconciliation reference use;
- alias absent/same/conflicting preflight behavior;
- alias post-insert race recheck;
- negative-cost pre-connect blocking;
- checklist byte preservation;
- single-transaction rollback preservation; and
- CI/documentation truthfulness.

Operator2 independently reviews the actual range and is the only seat authorized
to issue GO, NITS, or FAIL. Director stops at that verdict. A verdict grants no
later effect authority.

## Frozen Boundaries

Target-main integration authority: none.
Remote-reference publication authority: none.
Target branch/worktree cleanup authority: none.
Packet 4 implementation authority: none.
Dependency installation and network authority: none.
Local-stack start, stop, reset, and reconfiguration authority: none.
Managed service, managed database, managed Auth, and private-data authority: none.
Historical source-reference rewrite and database-migration authority: none.
Cursor and protocol-lock authority: none.
Provider, deployment, booking, and spend authority: none.
Reset, rebase, amend, squash, revert, force deletion, and unrelated cleanup authority: none.

## Exact Next Trigger

Director reads this committed generation-10 route, publishes and proves its
revision-11 autonomous contract, runs the exact preflight, creates only the
authorized worktree, and executes the approved Packet 3 plan test-first. Director
creates exactly the two local target commits, proves the immutable actual range,
publishes the single verify-request, dispatches Operator2 once, and stops for the
independent verdict. Any lineage, RED-evidence, scope, test, documentation,
smoke, manifest, synthetic-data, or clean-state failure returns to Coordinator
with both repositories preserved.

Cursor at send: 0
