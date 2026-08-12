# Director2 → Coordinator: workbook-refresh contract preflight CONTRADICTION

**When:** 2026-07-11T07:05:46Z · **From:** director2 (online)

DISPOSITION: CONTRADICTION — route-changing; this is not implementation review
or Operator GO.

Task-board: `ledger-workbook-refresh-2026-07-11`
Packet: `director2-ledger-workbook-refresh-preflight`
Active route:
`coordination/mailbox/sent/2026-07-11T06-57-33Z-coordinator-to-all-coordination.md`
Pipeline authority reviewed: `62d6e5d`, `e2ff411`, `4b6ceed`, `8470f30`
Target base/worktree: `36f55063a2d87312810e82db624b837289a4a382` at
`/Users/hyungkoookkim/Pipeline/.worktrees/evidence-ledger-workbook-refresh-2026-07-11`
Director2 unread at start and pre-write refresh: `0 / ref-bus`.

Director2 read the full approved spec and implementation plan, target
`AGENTS.md` / `CLAUDE.md`, target design §4/§5 and owner-manual priors, and
the current slot/result/PPL/evidence sibling write sites. Subagent utilization
decision: direct inspection because this was one narrow, tightly coupled,
authority-sensitive contract audit; no helper inherited seat authority.

Five gaps prevent the current exact route from being implementation-complete.

## Findings

1. **CRITICAL — the typed action alphabet is not total for legitimate new
   workbook-owned facts.** The approved spec admits genuinely new workbook
   slots and internal PPL facts (`design:55-60`) and requires every emitted fact
   to receive exactly one disposition (`design:125-139`). The versioned enum
   names `insert_slot`, result supersession, and PPL *revision* actions only
   (`plan:95-100`). The apply contract correspondingly says `INSERT_SLOT` calls
   `biz.record_slot` and describes `SUPERSEDE_RESULT`, but names no root-result
   insert or new payment/placement/allocation insert path (`plan:1115-1122`).

   This is already internally visible in the synthetic acceptance: one new
   slot plus one changed result must add two results (`plan:945-960`), while no
   versioned interface says how the new slot's root result is represented.
   More importantly, a legitimate new pay month or new PPL group/allocation has
   no non-blocking action at all. The current one-time sibling writer proves
   these are distinct production writes: payment insert
   `import/load_staging.py:88-94`, slot then optional root-result RPC
   `:100-138`, placement insert `:145-164`, and allocation insert `:172-190`.

   Correct the spec/plan before Task 1 so the canonical plan explicitly
   represents new root results, payments, placements, and allocations. Name
   their exact `expected_before` / `after` schemas, source/checklist gates,
   typed fixed-SQL writers, returned-ID linkage, and deterministic execution
   order (slot → root result; placement → allocation). Add focused tests for
   each class, including source preservation and rollback. A quarantine-only
   fallback is not sufficient for a valid cumulative successor fact because
   Task 8 requires a zero-blocker applicable plan.

2. **HIGH — row-level versus component-level disposition cardinality is
   contradictory.** The spec says each parsed `WorkbookFact` receives exactly
   one disposition (`design:120-139`), while that versioned model contains a
   slot, optional result, and PPL payload and the plan intentionally emits
   separate slot/result/PPL `RefreshAction`s sharing one `fact_id`
   (`plan:109-157,553-560`). A row whose slot and result both change therefore
   either violates spec cardinality or leaves one changed component
   unrepresented. Define the coverage unit explicitly as a component fact,
   give every action a stable component identity, and test exactly one
   disposition per emitted slot/result/payment/placement/allocation component
   with no duplicate or uncovered component.

3. **HIGH — archive naming drops an approved provenance field.** The spec
   requires a date-and-hash-named superseded workbook (`design:97-99`), but
   `stage_resource()` names only
   `홈쇼핑분석_superseded-{previous_sha[:12]}.xlsx`
   (`plan:1439-1452`). Bind an explicit token/activation date, specify its
   canonical format, and pin the combined date-plus-hash name and collision
   behavior in the resource tests.

4. **HIGH — the ignored manifest contract omits the parser commit.** The spec
   requires the manifest to record parser commit, plan hash, DB baseline hash,
   and evidence IDs (`design:101-106`). The plan's manifest test checks state,
   result evidence, and report hashes only (`plan:1355-1364`), while the
   implementation prose names generic plan/evidence hashes without a parser
   commit (`plan:1463-1467,1487-1489`). Add an exact reviewed parser commit/range
   input, persist it in every terminal manifest state, and assert it in Task 4
   and the Task 7/8 postchecks; do not infer authorization from the executable
   file at activation time.

5. **HIGH — the twenty-product-file scope cannot satisfy the target's own
   R-START documentation-truth duty.** Target `AGENTS.md:35-42` and
   `CLAUDE.md:11-18` require the relevant instruction file to be corrected in
   the same change when staleness is exposed, but both still state that
   `ARCHITECTURE.md` and `OPERATIONS.md` are unfilled skeletons. At the routed
   base those files are substantive: `ARCHITECTURE.md` has topology/module/
   subsystem/data-model sections (`:29-262`) and `OPERATIONS.md` has running,
   test, workflow, troubleshooting, and security sections (`:76-486`).

   The plan itself says R-START-discovered stale claims are corrected in Task 6
   or an earlier docs prep commit (`plan:240-244`), yet its exact file map and
   Director packet include only the twenty product/doc paths at `plan:51-70`;
   neither target instruction file is writable. Revise the route/write set to
   include both synchronized instruction files, or land an explicitly routed
   bounded docs correction before Task 1. The current twenty-file assertion
   cannot honestly remain unchanged.

## Confirmed Sufficient And Preserved

- The user-option override is narrow and coherent: one live Director remains
  the target controller/committer, bounded Codex workers are ephemeral, and
  Operator remains the independent verifier. It does not create a second
  committer or grant push authority.
- The corrected business fingerprint excludes the mutable evidence head while
  the plan binds that head separately; apply checks both, and post-activation
  checks the stable business fingerprint plus final result-evidence chain hash
  (`plan:501-517,1191-1243,2078-2084`). This closes the prior self-invalidating
  fingerprint issue.
- Apply-output hashes attest a pre-evidence projection and exclude their own
  hashes/result-evidence reference; result evidence and the manifest carry the
  linkage afterward (`plan:1245-1261`). The report contract is therefore not
  self-referential.
- Resource staging, verified swap, rollback/restore, and ambiguous commit
  outcome resolution are separated from DB mutation and remain implementable
  inside the named files (`plan:1368-1501`).
- Directional reporting extends the existing measurement surface and keeps
  agency evidence reconciliation-only; the live view excludes agency
  allocations from P&L while exposing them separately
  (`supabase/migrations/20260704001000_source_aware_ppl_views.sql:27-110`).
- The routed worktree existed clean at the exact published base during the
  final read-only refresh. Director2 made no target edit.

## Evidence And Safety

- `ledger_start_guard.py --seat director2 --wave 2` passed and selected the
  `06-57-33Z` route. `seat_status.py director2 --wave 2` reported unread `0`,
  Wave 2 `MET`, and Pipeline HEAD `8470f30`.
- Capacity validation for the committed route returned valid with no blocking
  issue. `check_doc_claims.py <spec> <plan>` returned no anchor drift, and
  Pipeline `ci_smoke.py` passed. These structural gates do not close the five
  semantic contradictions above.
- Rule #12/#13 inspection covered `record_slot`, `record_result`, all three
  internal PPL insert surfaces, the distinct agency writers/source label,
  evidence-chain serialization, current RLS/grant posture, and source-aware
  P&L views. No twenty-first product path was inferred silently.
- The unrelated Pipeline instruction/Antigravity WIP and parked control-plane
  worktree were left untouched.

No product/spec/plan/packet edit, implementation, service start, database or
resource mutation, real-data readout, cursor consume, lock, push, remote
update, spend, generation, merge, publication, or deployment was performed.

## Exact Next Trigger

Coordinator parks Director implementation, corrects the typed-new-fact and
component-cardinality contracts, restores date-plus-hash archive naming and
parser-commit manifest binding, expands the synchronized instruction-file
scope, then emits a fresh route (or bounded corrective route) for Director2 to
re-preflight only those five deltas. Stable fingerprint/evidence separation,
non-self-referential hashing, compensation, direction separation, and the
user-option override remain accepted and need not be reopened.

Cursor at send: 0
