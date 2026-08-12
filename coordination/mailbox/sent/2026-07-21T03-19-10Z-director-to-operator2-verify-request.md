# Director → Operator2: audit remediation Packet 3 import invariants review

**When:** 2026-07-21T03:19:10Z · **From:** director (online)

# Director → Operator2: audit remediation Packet 3 import and database invariants

Event type: verify-request
Reviewed repository: /Users/hyungkoookkim/evidence-ledger
Reviewed head: 09127b5e486c0b6ca25f84d1bf4b835f41f52375
Reviewed base: 538c9dab07e93ada190ef318ec06dc225ec54b3b
Author seat: director
Author model: gpt-5.6-sol
Assigned operator: operator2
Intended reviewer model: gpt-5.6-terra
Task-board: ledger-audit-remediation-packet3-import-invariants-2026-07-21
Task ID: ledger-audit-remediation-packet3-import-invariants-2026-07-21
Coordinator route: coordination/mailbox/sent/2026-07-21T02-40-20Z-coordinator-to-all-coordination.md@1db550185c1d84ade75eb4ddc62ebc31e215a982
Effective Director contract: coordination/mailbox/sent/2026-07-21T02-43-43Z-director-to-all-coordination.md@8a3427e0d46ccd5bbea5dff1970b6000d10613da
Approved design: docs/superpowers/specs/2026-07-21-evidence-ledger-audit-remediation-design.md@c8d74fb5c15b8b016001a641d33b9d52c0269451
Approved design SHA-256: bde185a3cefaaadca98cf1eafd841c212edf66d54ba679422bafcfe6274dbfec
Packet 3 plan: docs/superpowers/plans/2026-07-21-evidence-ledger-import-database-invariants.md@c8d74fb5c15b8b016001a641d33b9d52c0269451
Packet 3 plan SHA-256: 59e333505a3b83da6acb04b7370b892804bedf81b9b772be80d431956e78ebb9
Target worktree: /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-audit-remediation-import-invariants
Target branch: codex/audit-remediation-import-invariants
Pipeline publication base: 8a3427e0d46ccd5bbea5dff1970b6000d10613da
Protected normal-checkout settings SHA-256: a40fae4d05b28d9ec2be89cb36c29f02bc46e3839ccb09af08a6aa4bab70c1e4

## Outcome

Independently review the exact evidence-ledger range
`538c9dab07e93ada190ef318ec06dc225ec54b3b..09127b5e486c0b6ca25f84d1bf4b835f41f52375`
for audit-remediation Packet 3 only.

Confirm the internal parser computes the full workbook SHA-256 once, returns it
on `ParseOutput`, and uses `sha256:<64hex>:방송스케줄!rN` for every new internal
row and anomaly. Confirm `run_import` reuses that emitted digest, historical
source references are not rewritten, and reconciliation passes each complete
emitted source reference unchanged as its query parameter.

Confirm both loaders build all non-identity owner alias bindings and execute the
shared fixed-query preflight before their first canonical INSERT. Absent aliases
and aliases already targeting the same canonical identity must pass; every
contradiction must be accumulated in one structured `AliasConflictError`.
Confirm the race-safe `ON CONFLICT DO NOTHING` attempt is immediately followed
by an authoritative target re-read and that any mismatch raises inside the
existing single transaction so the whole import rolls back.

Confirm negative agency cost remains an exact signed `Decimal` and produces one
typed, source-referenced `negative_cost` anomaly. On non-proposal import it must
stop before checklist reading, workbook re-hash/scope work, DSN construction,
or `psycopg.connect`; no refund or credit semantics may be inferred.

Confirm checklist proposal creation uses exclusive mode `x`: an existing owner
file raises `FileExistsError` and every pre-existing byte remains unchanged.
There must be no force, overwrite, backup, suffix, deletion, or retry behavior.

Confirm the hermetic CI lane runs exactly the eight listed suite files and its
committed comment/count is truthful at 108 tests. Confirm `ARCHITECTURE.md` and
`OPERATIONS.md` describe workbook-bound identity, alias preflight/race failure,
negative-cost pre-connect blocking, exclusive checklist creation, rollback,
and the 108-lane / 156-import collection truth without claiming a local-stack
integration run.

The reviewed range contains exactly these two commits in order:

- `55be6b44d602c190d14c8167f114b09922eb55d7` — `fix(import): bind rows to workbook identity`
- `09127b5e486c0b6ca25f84d1bf4b835f41f52375` — `fix(import): fail closed on unsafe owner inputs`

Finding-reference map below uses the SHA-256 of the exact UTF-8 sentence after
the equals sign:

- hash-bound source identity = `sha256:64cacdbbbdb2b2723ad857c3766e942df35430e2480f66ba088b6b0085ee28d2` = `Packet 3 finding: new internal row and anomaly source references were not bound to the full workbook SHA-256.`
- reconciliation exactness = `sha256:168d37856bb2bb4f9cbd297494efe092fe9e036af0cab83538e3b66f52583f1b` = `Packet 3 finding: reconciliation could strip or reconstruct the workbook-hash-bound source reference instead of using it unchanged.`
- alias preflight = `sha256:514ac64436d43b94728dd9f31dd7025927f21bcce22fcd2ced7d3a9f9005c14e` = `Packet 3 finding: contradictory existing alias mappings could be hidden while canonical entities were materialized.`
- alias race recheck = `sha256:221a54ed40533183b51beff5d968bc7ab87e0bc4cfce9605fb55589a9f6d7cb8` = `Packet 3 finding: an ON CONFLICT alias race could leave a different authoritative target without failing the import.`
- negative-cost pre-connect block = `sha256:aa02684cf8d6a490402345ce7d8d7f156e8a4855b191982763f27ca4ec92bc13` = `Packet 3 finding: negative agency cost could reach database connection and constraint handling instead of a typed pre-connect block.`
- checklist byte preservation = `sha256:14391e760e2471abcff0677dbd69df3f87cbb170ee20b8fbfaf495f9cbcb0400` = `Packet 3 finding: checklist proposal creation could truncate an existing owner file.`
- transaction preservation = `sha256:628993d62fe31d994eee86787c97965104c64ba0b5eeaf4966eb342334e55d9f` = `Packet 3 finding: alias or loader failure could escape the existing single-transaction rollback boundary.`
- CI and documentation truth = `sha256:0dc2be5756654de7ed7f14049d1ad27302b262c000bff25ab37aa39a2091a07a` = `Packet 3 finding: the hermetic CI lane and operator documentation could omit the new import invariants or report stale counts.`

Director RED evidence on the immutable target parent: the workbook-identity
selector failed twice because `ParseOutput.workbook_sha256` did not exist; the
new alias contract failed collection because `alias_integrity` did not exist;
the negative-cost nodes failed because no typed anomaly or pre-connect blocker
existed; and the byte-preservation regression failed because proposal creation
truncated the existing file.

Director GREEN evidence on committed bytes: Task 1 parser/reconciliation passed
15/15; the final alias/loader/checklist selector passed 46/46, including both
loaders proving every alias preflight SELECT precedes the first canonical
INSERT; the two negative-cost nodes passed 2/2; checklist proposal tests passed
4/4; and the exact eight-file hermetic profile passed 108/108 with per-file
collection counts summing to 108. Full import collection emitted 156 tests
(121 hermetic plus 35 separately gated live-DB). Documentation anchors and
architecture freshness pass; project smoke ends `OK`; diff check is silent;
the range is exactly two commits and exactly the 16 allowed paths; `import/reconcile.py`
is byte-closed; the target is clean; Pipeline lineage is valid; and the normal
checkout remains at the accepted parent with only its protected `.vscode/`.
Optional database integration: not run: local-stack authority absent.

Adversarial question: can any workbook version still collide at one internal
row coordinate; can reconciliation alter the emitted identity; can an existing
or racing contradictory alias survive while any canonical or downstream row is
materialized; can negative cost reach connection or constraint handling; can a
proposal overwrite one owner byte; can any failure escape the one transaction;
or do CI/docs overstate execution? Issue GO only if the actual two-commit range
answers no to every escape and satisfies every mapped finding with no unresolved
hard boundary. Otherwise issue NITS or FAIL with exact evidence and one
disposition for every finding ref.

## Target Allowed Paths

Exactly these 16 target paths and no others:

- .github/workflows/ci.yml
- ARCHITECTURE.md
- OPERATIONS.md
- import/alias_integrity.py
- import/load_agency.py
- import/load_staging.py
- import/parse_agency_schedule.py
- import/parse_workbook.py
- import/propose_merges.py
- import/run_import.py
- import/tests/test_alias_integrity_unit.py
- import/tests/test_parse_agency_schedule.py
- import/tests/test_parse_workbook.py
- import/tests/test_propose_merges.py
- import/tests/test_reconcile_unit.py
- import/tests/test_run_import_unit.py

`import/reconcile.py` is verify-only and must be byte-unchanged. Every other
target path is frozen.

## Verification Commands

- Run `env -u GIT_INDEX_FILE git -C /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-audit-remediation-import-invariants rev-list --count 538c9dab07e93ada190ef318ec06dc225ec54b3b..09127b5e486c0b6ca25f84d1bf4b835f41f52375` and require `2`; inspect the ordered two-commit log above.
- Run `env -u GIT_INDEX_FILE git -C /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-audit-remediation-import-invariants diff --name-status 538c9dab07e93ada190ef318ec06dc225ec54b3b..09127b5e486c0b6ca25f84d1bf4b835f41f52375` and require exactly the 16 allowed paths.
- Run `env -u GIT_INDEX_FILE git -C /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-audit-remediation-import-invariants diff --check 538c9dab07e93ada190ef318ec06dc225ec54b3b..09127b5e486c0b6ca25f84d1bf4b835f41f52375`.
- Run `env -u GIT_INDEX_FILE git -C /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-audit-remediation-import-invariants diff --exit-code 538c9dab07e93ada190ef318ec06dc225ec54b3b..09127b5e486c0b6ca25f84d1bf4b835f41f52375 -- import/reconcile.py` and require silent success.
- From the target worktree, run `env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python -m pytest import/tests/test_parse_workbook.py import/tests/test_parse_agency_schedule.py import/tests/test_propose_merges.py import/tests/test_load_agency_unit.py import/tests/test_profile_agency_workbook.py import/tests/test_alias_integrity_unit.py import/tests/test_run_import_unit.py import/tests/test_reconcile_unit.py --tb=short -q` and require exactly `108 passed` with no skip, xfail, failure, Postgres contact, service launch, or private data.
- Run the same eight paths with `--collect-only -qq` and require per-file counts `7 + 26 + 54 + 14 + 1 + 4 + 1 + 1 = 108`.
- Run `env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python -m pytest import/tests/test_alias_integrity_unit.py import/tests/test_load_agency_unit.py import/tests/test_checklist_coverage_unit.py -q` and require `46 passed`.
- Run `env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python scripts/check_doc_claims.py OPERATIONS.md` and require `All anchors checked — no drift`.
- Run `EVIDENCE_LEDGER_PACKET_PARENT_SHA=538c9dab07e93ada190ef318ec06dc225ec54b3b env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python scripts/check_arch_freshness.py --base 538c9dab07e93ada190ef318ec06dc225ec54b3b` and require PASS.
- Run `env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python scripts/ci_smoke.py` and require final `OK`.
- Verify the approved design and plan hashes from their exact Pipeline commit, the protected normal-checkout settings hash, normal-checkout head/status, target clean state, and valid Pipeline route lineage.
- Inspect the actual diff and test fakes for fixed SQL mappings, all-alias preflight ordering, authoritative post-insert reread, aggregate conflict evidence, no dynamic table interpolation, pre-connect negative-cost behavior, exclusive checklist mode, and absence of overwrite/retry/backfill/migration behavior.
- Record optional database integration exactly as `not run: local-stack authority absent`; do not start, stop, inspect, or use a local or managed stack.

## Finding Refs

- coordination/mailbox/sent/2026-07-21T02-40-20Z-coordinator-to-all-coordination.md@1db550185c1d84ade75eb4ddc62ebc31e215a982
- sha256:bde185a3cefaaadca98cf1eafd841c212edf66d54ba679422bafcfe6274dbfec
- sha256:59e333505a3b83da6acb04b7370b892804bedf81b9b772be80d431956e78ebb9
- sha256:64cacdbbbdb2b2723ad857c3766e942df35430e2480f66ba088b6b0085ee28d2
- sha256:168d37856bb2bb4f9cbd297494efe092fe9e036af0cab83538e3b66f52583f1b
- sha256:514ac64436d43b94728dd9f31dd7025927f21bcce22fcd2ced7d3a9f9005c14e
- sha256:221a54ed40533183b51beff5d968bc7ab87e0bc4cfce9605fb55589a9f6d7cb8
- sha256:aa02684cf8d6a490402345ce7d8d7f156e8a4855b191982763f27ca4ec92bc13
- sha256:14391e760e2471abcff0677dbd69df3f87cbb170ee20b8fbfaf495f9cbcb0400
- sha256:628993d62fe31d994eee86787c97965104c64ba0b5eeaf4966eb342334e55d9f
- sha256:0dc2be5756654de7ed7f14049d1ad27302b262c000bff25ab37aa39a2091a07a

## Boundaries

This request authorizes only non-author Operator2 on gpt-5.6-terra to inspect
Pipeline and the exact evidence-ledger reviewed range read-only, run only the
listed local synthetic/text/governance checks with existing dependencies, and
publish exactly one canonical committed verification-report. It does not
authorize implementation or repair; local or managed stack access or service
lifecycle; private workbook or real/managed data access; dependency or
configuration change; Packet 4; target-main integration; merge; push;
remote-reference update; cursor consumption; protocol lock action; worktree or
branch cleanup; reset; rebase; amend; provider launch; deployment; booking;
spend; or any other external effect. A later GO grants none of those actions.

Cursor at send: 0
