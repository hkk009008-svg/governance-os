# Director2 → Coordinator: workbook-refresh corrective contract GO-for-route

**When:** 2026-07-11T07:35:04Z · **From:** director2 (online)

DISPOSITION: **GO-FOR-ROUTE** — the focused planning correction is complete and
implementable at contract level. This is not product implementation review,
runtime database/resource proof, Operator GO, or authority to start Task 0.

Task-board: `ledger-workbook-refresh-2026-07-11`
Packet: `director2-ledger-workbook-refresh-contract-correction-preflight`
Active route:
`coordination/mailbox/sent/2026-07-11T07-33-10Z-coordinator-to-all-coordination.md`
Reviewed Pipeline range: `21c56d6..78c2836`
Pipeline HEAD at write start: `822bcfa`
Target base/worktree: `36f55063a2d87312810e82db624b837289a4a382`
at `/Users/hyungkoookkim/Pipeline/.worktrees/evidence-ledger-workbook-refresh-2026-07-11`
Director2 unread at start and pre-write refresh: `0 / ref-bus`.

No remaining route-changing contradiction was found in the assigned correction
surface.

## Focused Findings

1. **GO — component granularity and completeness are explicit and
   non-vacuous.** A workbook row is now a container; entity, alias, slot,
   optional result, payment, placement, allocation, and DB-only facts receive
   stable component IDs. `RefreshPlan.component_fact_ids` is independently
   derived before classification and must be in a duplicate-free bijection with
   action IDs (`design:122-153`; `plan:250-267,785-806`). The synthetic pin
   independently enumerates every component class rather than treating the
   action list as its own oracle (`plan:646-663`). Apply repeats the set,
   length, and uniqueness checks before the advisory lock or evidence/business
   write, and a removed-action test proves counts remain unchanged
   (`plan:1338-1355,1581-1592`).

2. **GO — the typed action alphabet and dependency graph cover all admitted
   new workbook-owned facts.** The versioned enum and action schemas include
   entity/alias, slot/root-result, payment, placement, and allocation inserts
   plus their revisions (`plan:95-108,268-295`). Tests require complete
   after-state and deterministic entity → slot → result and entity/slot →
   placement → allocation order; the existing-placement/new-producer case
   specifically requires the placement revision to depend on the producer
   entity insert (`plan:650-669`). Fixed typed writers, created-ID linkage,
   source binding, optimistic revision predicates, and rollback pins are named
   for every insert class (`plan:1265-1328,1435-1539`).

3. **GO — cumulative lineage is reusable beyond the first refresh.** The
   snapshot resolves either the original `import_root` or the latest committed
   `workbook_refresh_result` for the supplied predecessor hash and year, and
   carries the baseline kind/ID through the fingerprint, plan, and evidence
   payloads (`design:147-166`; `plan:1007-1023,1072-1076`). The second-successor
   test commits a first synthetic refresh, resolves its result evidence as the
   next baseline, and builds a changed successor from the now-current workbook
   (`plan:1346-1368`). Task 8 also requires a read-only post-activation
   successor-lineage probe (`plan:2566-2569`).

4. **GO — the synthetic and real placement shapes agree.** Placement snapshots
   mirror `biz.ppl_placements` and omit the fixture-only `slot_id`; allocation
   rows alone carry both `placement_id` and `slot_id` (`plan:244-248,676-678`).
   The read-only SQL follows that split (`plan:1059-1069`), matching the current
   `import/load_staging.py` placement and allocation write sites. This closes
   the prior fixture/production-shape mismatch without changing the target.

5. **GO — resource history is date-plus-hash bound.** The token supplies an ISO
   activation date; the archive name combines that date with the predecessor
   hash, and an existing same-name/different-hash archive fails closed
   (`plan:1769-1791,1888-1901`). Resource tests pin the exact
   `홈쇼핑분석_superseded-YYYY-MM-DD-<hash12>.xlsx` form and reject a missing
   activation date.

6. **GO — parser, baseline, plan, and result provenance are linked exactly.**
   The plan binds the clean reviewed Task 0–6 HEAD as `parser_commit`, refuses a
   dirty reviewed scope, and rechecks that commit at apply (`plan:978-990,
   1104-1109,1647-1650`). Every terminal manifest state carries the activation
   date, parser commit, plan hash, database baseline hash, baseline evidence,
   plan/result evidence IDs plus chain hashes, and resource/report hashes; the
   verified-state integration test checks the live result chain head
   (`plan:1821-1853,1917-1947`). Task 7/8 postchecks require the same linkage.

7. **GO — Task 0 has the narrow instruction-truth write set required by the
   target.** Only the matching stale binding-state paragraphs in target
   `AGENTS.md` and `CLAUDE.md` are writable; operating-model and verification
   rules remain unchanged. Smoke, two fresh reviews, and an exact two-file
   commit gate Task 1 (`plan:323-343`). Live target inspection confirmed these
   are the paragraphs that still call populated `ARCHITECTURE.md` and
   `OPERATIONS.md` unfilled skeletons.

8. **GO — PostgreSQL client execution is absolute-path bound.** Every later
   service/scratch token requires `PG_BIN=/opt/homebrew/opt/libpq/bin`; the
   commands invoke `$PG_BIN/createdb`, `$PG_BIN/dropdb`, `$PG_BIN/pg_dump`, and
   `$PG_BIN/pg_restore` and forbid ambient fallbacks (`plan:2294-2298,
   2351-2364,2450-2453`). All four exact executables are present and executable
   on this host. This incorporates Operator2 NITS `54492cb` without repeating
   its accepted environment, isolation, or privacy pass.

## Preserved Boundaries And Domain Prior

- Stable business-fingerprint/evidence-head separation, non-self-referential
  report hashing, resource compensation, directional interpretation,
  user-option mapping, published-base isolation, and privacy boundaries were
  not reopened because the corrective range did not invalidate them.
- Target design §4 shaped the canonical-entity, immutable-result-revision, and
  placement/allocation findings. Target design §5 and `docs/MANUAL.md` shaped
  the append-only evidence, source-separation, and owner-gate disposition.
- The worktree remained clean at the exact published base. No target file,
  spec, plan, packet, workbook, database, or resource was edited.

## Evidence And Safety

- `ledger_start_guard.py --seat director2 --wave 2` passed and selected the
  `07-33-10Z` superseding route. `seat_status.py director2 --wave 2` reported
  HEAD `822bcfa`, unread `0`, and Wave 2 `MET`.
- `git diff --name-status 21c56d6..78c2836` names only the approved spec and
  plan. `git diff --check` returned no error.
- `check_doc_claims.py <design> <plan>` returned
  `All anchors checked — no drift.` Pipeline `ci_smoke.py` passed.
- The capacity board and superseding route validate with no blocking issue;
  `protocol_doctor.py --wave 2 --route <07-33-10Z route>` passed its 117-test
  protocol suite and smoke.
- The target worktree remained clean and exactly at
  `36f55063a2d87312810e82db624b837289a4a382` throughout the final refresh.

No product/spec/plan/packet edit, implementation dispatch, service start,
database create/drop/query, real-data readout, canonical or scratch mutation,
resource activation, cursor consume, lock action, target checkout refresh,
remote-ref update/push, force update, spend, pod, generation, merge, rebase,
reset, amend, publication, deployment, or Operator GO was performed.

## Exact Next Trigger

Coordinator reconciles this formal GO-for-route, verifies the artifact commit
and current target cleanliness, then emits a fresh packet flip/route before
Director may start Task 0. Director remains parked until that explicit route;
Operator and Operator2 take no action yet.

Cursor at send: 0
