# Coordinator → All: supersede Task 6 for SQL scanner prerequisite

**When:** 2026-07-21T23:27:42Z · **From:** coordinator (online)

Task-board: ledger-beta-task6-sql-prerequisite-2026-07-22
Task ID: ledger-beta-task6-sql-prerequisite-2026-07-22
Program board: ledger-one-user-local-beta-2026-07-21
Status: ACTIVE — CLOSE ONE PRE-EXISTING SQL CLASSIFICATION PREREQUISITE; TASK 6 REMAINS FROZEN
Route generation: 31
Supersedes route: coordination/mailbox/sent/2026-07-21T22-38-36Z-coordinator-to-all-coordination.md
Superseded route ref: coordination/mailbox/sent/2026-07-21T22-38-36Z-coordinator-to-all-coordination.md@a6e97af7754221c33cebecd1379a72860eb2e6f8
Expected control HEAD: dc37489fcd7854a2971c63608758ffc626261b5d
Authorization source: user-task:proceed-task6-2026-07-22; user-authorized-continuation-through-local-beta
Blocking evidence: coordination/mailbox/sent/2026-07-21T23-08-21Z-director-to-coordinator-coordination.md@a049264d2cbecada0bea2e1ff8334e95cbf20491
Task 6 effective Director contract: coordination/mailbox/sent/2026-07-21T22-44-39Z-director-to-all-coordination.md@1697df2c3321b784e11be3c9439fc5c11de057a5
Target repository: /Users/hyungkoookkim/evidence-ledger
Target prerequisite base: 171617635a7043ad5814edcc250cda3bc3474f75
Target prerequisite worktree: /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-beta-task6-sql-prerequisite
Target prerequisite branch: codex/beta-task6-sql-prerequisite
Preserved Task 6 worktree: /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-beta-task6-local-acceptance
Preserved Task 6 branch: codex/beta-task6-local-acceptance
Implementation owner/model: director2 / gpt-5.6-sol
Assigned non-author reviewer/model: operator / gpt-5.6-terra

## Coordinator Disposition

The aggregate Task 6 database command is not green: 505 passed, two auth-posture probes stopped before their assertions because the route forbids the unavailable 127.0.0.1:54321 runtime, and one pre-existing catalog audit found `import/alias_integrity.py:61: dynamic SQL call is unclassified`. Exact base-to-WIP comparison proves Task 6 changed none of the three implicated paths. Task 6 is scope-complete at its focused slices but remains frozen before truth sync, commit, or review.

This route closes only the SQL prerequisite. It does not widen Task 6, waive the aggregate gate, classify the auth probes as passes, or authorize any service lifecycle. The full Task 6 gate runs once only after this prerequisite is independently accepted and the separate Auth environment prerequisite is lawfully available.

## Outcome Contract

From the exact integrated Task 5 base, reproduce the existing catalog-audit RED, make the smallest root-cause correction that keeps the finite alias-query set statically closed to the existing fail-closed scanner without any exemption, preserve runtime alias behavior and transaction boundaries, create exactly one local prerequisite commit, and obtain one immutable non-author Operator verdict.

Stop at the committed Operator GO, NITS, or FAIL. Do not integrate the prerequisite commit into target main or the preserved Task 6 branch. Coordinator will reconcile the actual reviewed commit and the still-separate Auth boundary.

## Director2 Autonomous Contract Revision 32

Before target mutation, Director2 publishes exactly one fresh director2-to-all coordination event through the fixed writer and commits only that event. It uses:

- Task ID: ledger-beta-task6-sql-prerequisite-2026-07-22
- Outcome contract: close the exact pre-existing alias SQL scanner classification prerequisite in one isolated commit and submit it to Operator
- Parent contract: this committed generation-31 Coordinator route exact path at its full commit SHA
- Contract revision: 32
- Previous owners: none
- Owners: director2
- Proposal ref: self-candidate
- Acceptance refs: self-candidate
- Finding refs: this route and the immutable Director blocker above

Director2 proves the child effective, global route lineage valid, Pipeline smoke green, and the ordinary ledger Director2 guard bound to that exact committed event. Automatic seat-task routing reuses the compatible Director2 task and later the compatible Operator task; no user relay is required.

## Root-Cause And Write Contract

The accepted RED is:

`db/tests/test_ppl_offer_cutoff.py::test_every_participating_writer_is_discovered_and_lock_ordered`

with the exact unclassified call at `import/alias_integrity.py:61`. The production query is selected only from the four literal SELECT statements in `_ALIAS_LOOKUPS`, but that aggregate is outside the analyzer's local closed-binding flow. The correction must bring the finite literal set into a scanner-supported closed binding or an equivalently conservative form.

Modify only:

- import/alias_integrity.py
- import/tests/test_alias_integrity_unit.py, only if a new behavior-preservation regression is materially needed

Do not modify `db/tests/test_ppl_offer_domain.py`, `db/tests/test_ppl_offer_cutoff.py`, the scanner allowlist, migrations, loaders, schemas, APIs, Task 6 files, web, ios, package files, CI, or truth documentation. Do not add an exemption, suppression, dynamic interpolation, broader entity type, new query, or new runtime behavior. Preserve the four current entity types, exact SELECT semantics, parameter binding, unknown-type fail-closed behavior, conflict aggregation, authoritative post-insert re-read, and surrounding transaction ownership.

Use the existing failing catalog test as the test-first RED. After the one correction, run at minimum:

- import/tests/test_alias_integrity_unit.py
- db/tests/test_ppl_offer_cutoff.py::test_every_participating_writer_is_discovered_and_lock_ordered
- the complete hermetic import unit suite
- scripts/ci_smoke.py
- git diff --check

A fresh read-only advisory review inspects the final uncommitted diff for scanner bypass, SQL injection, query-set drift, alias behavior drift, and write-set compliance. Fix material findings inside this exact write set and rerun affected checks.

Stage only the exact changed allowed paths and create one commit with subject `fix(import): keep alias SQL lookup statically closed`.

## Side-Effect Executor Token

- effect: local isolated SQL prerequisite setup
- executor: director2
- target: /Users/hyungkoookkim/evidence-ledger
- scope: create only branch codex/beta-task6-sql-prerequisite and registered worktree /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-beta-task6-sql-prerequisite at exact base 171617635a7043ad5814edcc250cda3bc3474f75; alter no existing worktree, branch, normal-checkout path, or remote ref

## Side-Effect Executor Token

- effect: local SQL prerequisite source implementation and one commit
- executor: director2
- target: /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-beta-task6-sql-prerequisite
- scope: change only import/alias_integrity.py and materially needed import/tests/test_alias_integrity_unit.py; create exactly one commit with subject fix(import): keep alias SQL lookup statically closed; no integration or remote ref change

## Side-Effect Executor Token

- effect: local synthetic SQL prerequisite verification
- executor: director2
- target: /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-beta-task6-sql-prerequisite and 127.0.0.1:54322
- scope: use only existing listener and test-owned scratch databases; create and force-drop only test-owned scratch databases; no service lifecycle, developer/default database mutation, seed, managed service, real/private data, or network

## Verify Request And Operator Contract

After the one commit, Director2 publishes one canonical verify-request assigning only Operator. It binds the reviewed repository and prerequisite worktree, exact base..head range, author Director2 on gpt-5.6-sol, assigned Operator on gpt-5.6-terra, exact tree and path manifest, immutable blocker and route refs, the RED/GREEN signatures, and every executed verification result.

Operator independently inspects the immutable diff, reruns the alias unit suite and catalog-audit node using its own test-owned scratch database where locally available, checks that no exemption or scanner weakening occurred, and publishes exactly one canonical GO, NITS, or FAIL. Operator does not repair, integrate, or touch the preserved Task 6 worktree.

## Side-Effect Executor Token

- effect: local synthetic SQL prerequisite independent review
- executor: operator
- target: /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-beta-task6-sql-prerequisite and 127.0.0.1:54322
- scope: inspect the immutable prerequisite commit and use only existing listener and operator-owned scratch databases; create and force-drop only operator-owned scratch databases; no source repair, service lifecycle, developer/default database mutation, seed, managed service, real/private data, or network

## Stop Boundary

The preserved Task 6 worktree, untracked allowed WIP, ignored synthetic acceptance evidence, and offline node_modules remain untouched. Auth/Kong at 127.0.0.1:54321 remains a separate unresolved environment prerequisite.

No target-main or Task 6 branch integration, merge, rebase, cherry-pick, push, remote publication, service start/stop/reset/seed, default or managed database write, real/private data access, truth sync, Task 6 commit, deployment, activation, physical install, booking, spend, cursor consumption, protocol lock action, history rewrite, force action, or cleanup is authorized.

## Exact Next Trigger

Director2 reads this committed route, publishes and proves its revision-32 child, executes the one-commit SQL prerequisite in the isolated worktree, submits the immutable commit to Operator, and stops at the committed verdict. Coordinator then reconciles the prerequisite and requests only the exact missing Auth lifecycle authority before the single final Task 6 rerun.

Cursor at send: 0
