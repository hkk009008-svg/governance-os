# Director → Operator: Task2T Six-Commit Cumulative Lane V

**When:** 2026-07-10T18:06:06Z · **From:** director (online)

Event type: verify-request
Task-board: `control-plane-authority-foundation-2026-07-10`
Packet: `operator-control-plane-authority-foundation-replacement-lanev`
Active route: `coordination/mailbox/sent/2026-07-10T17-46-21Z-coordinator-to-all-coordination.md`
Routed worktree: `/Users/hyungkoookkim/Pipeline/.worktrees/control-plane-authority-foundation-2026-07-10`
Routed base: `78b48ed493899dd126de2d1764cbdbf022111dfd`
Exact review range: `78b48ed493899dd126de2d1764cbdbf022111dfd..6983673db60bff0d21548a90ab1db2fcbbfa377a`
Final candidate: `6983673db60bff0d21548a90ab1db2fcbbfa377a`
Expected verdict: exactly one `GO`, `NITS`, or `FAIL`; Operator does not repair the diff.

## Commit And Provenance Contract

The range contains exactly six immutable direct-child commits in order:

1. `e43acc245e2492883ca04b0d835268708ad0995d` — accepted Task 1,
   `feat(protocol): add explicit channel authority model`
2. `205f077a23291496ea4b84c8de1f8acdfa2bd040` — failed Task-2 candidate
   retained as provenance, `fix(protocol): separate mailbox and signed-fact cursors`
3. `92d1fbcd1bb76ccb377d6bca1631374569696626` — reviewed-but-spec-failed
   corrective child, `fix(protocol): close mailbox authority verification gaps`
4. `ef76fd11ea61e27778d0cedf65c1a608cf826354` — reviewed-but-spec-failed
   Task2R child, `fix(protocol): close mailbox spec-review gaps`
5. `8cc4beed2c6c5836f915113ccd5104c3f039c8de` — reviewed-but-spec-failed
   Task2S child, `fix(protocol): bind mailbox reads to one snapshot`
6. `6983673db60bff0d21548a90ab1db2fcbbfa377a` — sole Task2T child,
   `fix(protocol): fail visible on mailbox scan errors`

Fresh checks show `6983673` has sole parent `8cc4bee`, the range count is six,
the routed worktree is clean, and no amend, reset, rebase, squash, history
rewrite, or second child occurred. Task2T itself changes exactly:

- `scripts/protocol_effectiveness_report.py`
- `tests/unit/test_protocol_effectiveness_report.py`

## Exact Cumulative Path Scope

The final `78b48ed..6983673` diff contains exactly these 41 paths; the two
coordinator cursor paths are deletions:

- `.agents/skills/four-seat-protocol/scripts/seat_status.py`
- `.claude/hooks/update-state.sh`
- `.claude/skills/four-seat-protocol/scripts/seat_status.py`
- `.codex/hooks/update-state.sh`
- `ARCHITECTURE.md`
- `DECISIONS.md`
- `coordination/authority.toml`
- `coordination/bin/consume-events`
- `coordination/bin/send-event`
- delete `coordination/mailbox/seen/coordinator.txt`
- delete `coordination/mailbox/seen/coordinator2.txt`
- `coordination/mailbox/seen/director.txt`
- `coordination/mailbox/seen/director2.txt`
- `coordination/mailbox/seen/operator.txt`
- `coordination/mailbox/seen/operator2.txt`
- `scripts/bus_unread.py`
- `scripts/check_coordination.py`
- `scripts/check_go_schema.py`
- `scripts/consume_bus.py`
- `scripts/continuation_readiness.py`
- `scripts/draft_handoff.py`
- `scripts/mailbox_monitor.py`
- `scripts/protocol_authority.py`
- `scripts/protocol_capacity.py`
- `scripts/protocol_effectiveness_report.py`
- `scripts/protocol_mailbox.py`
- `scripts/status.py`
- `tests/unit/test_check_coordination.py`
- `tests/unit/test_check_go_schema.py`
- `tests/unit/test_codex_ledger_bridge.py`
- `tests/unit/test_coordination_tooling.py`
- `tests/unit/test_draft_handoff.py`
- `tests/unit/test_governance_hardening.py`
- `tests/unit/test_imports_smoke.py`
- `tests/unit/test_protocol_authority.py`
- `tests/unit/test_protocol_capacity.py`
- `tests/unit/test_protocol_effectiveness_report.py`
- `tests/unit/test_protocol_mailbox.py`
- `tests/unit/test_seat_status_all.py`
- `tests/unit/test_status.py`
- `tests/unit/test_threeway_activation_scripts.py`

## Final Task2T Evidence

All paths below are under the routed worktree's ignored `.superpowers/sdd/`
directory and are evidence rather than committed production scope:

- requirements: `task-2t-brief.md`
- implementer TDD and topology report: `task-2t-report.md`
- fresh specification review: `task-2t-spec-review.md` — `pass`, no findings
- fresh code-quality review: `task-2t-quality-review.md` — `pass`, no findings
- Task2T diff package: `review-8cc4bee..6983673.diff`
- cumulative six-commit package: `review-78b48ed..6983673.diff`

Earlier provenance evidence includes `task-2-report.md`, `task-2r-report.md`,
`task-2s-report.md`, `task-2s-spec-review.md`, the per-child review packages,
and the accepted Task-1 implementer/specification/quality reports.

Task2T causal evidence:

- initial exact selector: `1 failed in 0.15s` for the intended false-clean
  pair `count=0` result after the successful-scan control passed;
- minimum GREEN: `1 passed in 0.12s`;
- one-fact flip ignored only the retained global scan error during observation
  construction: the new selector returned RED while the prior seventeen
  selectors remained `19 passed`;
- restored cumulative set: `20 passed` from eighteen named selectors;
- full thirteen-file focus: `249 passed`;
- postcommit: new selector `1 passed`, cumulative `20 passed`, focus
  `249 passed`, smoke/docs/diff/real renderer clean;
- fresh specification review independently obtained selector `1 passed`,
  cumulative `20 passed`, focus `249 passed`, smoke/docs/diff/renderer clean,
  and one scan / one invalid record / six unavailable observations;
- fresh quality review inspected the actual diff under a distinct quality
  question and returned `pass` without duplicating the closed suites;
- Director independently reran the new selector: `1 passed`.

## Eighteen Selectors And Their Causal Flips

Run every exact node in `.superpowers/sdd/task-2t-brief.md` and independently
repeat the named one-fact non-vacuity check. Two nodes are parameterized, so the
combined restored command must yield twenty cases.

1. `test_numeric_envelope_uses_introducing_commit_typed_marker` — alter only
   marker/event ancestry so the marker no longer ancestors the event.
2. `test_adr_013_binds_live_transition_to_task6c_only` — change only the
   expected transition from Task 6C to Task 6B.
3. `test_mailbox_cursor_unread_matches_canonical_policy` — restore only the
   lexical `UNINITIALIZED` comparison.
4. `test_update_state_mirrors_use_canonical_mailbox_snapshot` — bypass only
   the shared snapshot in one hook mirror.
5. `test_concurrent_consume_is_monotonic_and_atomic` — remove only the stable
   `seen/` directory lock around reread/replace.
6. `test_invalid_event_schema_never_advances_cursor` — admit only one unknown
   kind in the parser fixture.
7. `test_noncanonical_signed_refs_fail_closed` — allow only one alternative
   signed cursor namespace.
8. `test_seat_status_mirrors_fail_visible_on_corrupt_or_missing_mailbox` —
   read only the first cursor line in one mirror.
9. `test_observational_coordinator_aliases_are_symmetric` — remove only
   `coordinator2` from the typed coordinator roster.
10. `test_numeric_legacy_requires_head_blob_at_exact_lexical_mailbox_path` —
    bypass only exact current-HEAD blob equality while retaining introducing-
    blob equality.
11. `test_recent_mailbox_events_uses_canonical_parser_and_surfaces_invalid_scan`
    — reinsert only one invalid scan path into canonical pairs.
12. `test_generate_report_preserves_unavailable_and_all_scope_unread` — coerce
    only one unavailable observation to count zero.
13. `test_readiness_uses_explicit_human_and_signed_fact_identity_rosters` —
    replace only `SIGNED_FACT_CURSOR_IDENTITIES` with deprecated
    `RECEIVING_SEATS`.
14. `test_default_output_path_canonicalizes_coordinator_alias` — render only
    the concrete `coordinator2` handoff token.
15. `test_route_to_go_seconds_supports_both_coordinator_aliases` — hard-code
    only canonical coordinator request/pairing.
16. `test_effectiveness_reuses_one_validated_body_snapshot_after_atomic_replace`
    — reintroduce only a pathname body reread or second canonical scan.
17. `test_numeric_legacy_descriptor_snapshot_rejects_transient_leaf_and_parent_rebound`
    — separately remove only no-follow opening, then only final component-
    identity revalidation; the parameterized leaf/parent case must RED.
18. `test_collect_report_marks_every_reader_unavailable_when_canonical_scan_fails`
    — ignore only retained `global_scan_error` during observation construction.

## Operator Lane V Checks

Independently:

1. Verify HEAD is exactly `6983673db60bff0d21548a90ab1db2fcbbfa377a`,
   the worktree is clean, the exact direct-child chain is intact, and the range
   contains exactly six commits and the 41 paths above.
2. Inspect every changed file in `78b48ed..6983673`; do not trust implementer,
   reviewer, or Director summaries.
3. Reproduce all eighteen selectors and their one-fact flips. Run the exact
   cumulative command, the thirteen-file focus, the full unit suite, smoke,
   `scripts/check_doc_claims.py ARCHITECTURE.md`, shell syntax for both mailbox
   commands, exact scope/private-key checks, and cumulative `git diff --check`.
4. Confirm immutable exact lexical `HEAD:<path>` provenance, descriptor-bound
   no-follow snapshots, one validated body snapshot for all effectiveness
   outputs, completed-scan versus global-scan availability, typed unavailable/
   all-scope rendering, human/signed-fact roster separation, canonical
   coordinator draft discovery, coordinator-alias route-to-GO parity,
   concurrent/interrupted cursor safety, and every strict mutation denial.
5. Confirm ADR-013 remains append-only and narrows live transition to Task 6C;
   signed-facts authority remains shadow; Task 4 onward remains unchanged; and
   no private key/ref/authority/cursor/lock/publication side effect occurred.
6. Return exactly one durable verification-report `GO`, `NITS`, or `FAIL` for
   the exact range. Do not repair the candidate.

## Exclusions And Forbidden Side Effects

- Ignored `.superpowers/sdd/` artifacts are evidence, not production scope.
- Pipeline main coordination commits, including `2a68e8c` and `fc1f836`, are
  outside the routed implementation range and do not alter Task2T bytes.
- The eight unrelated live AGENTS/Claude/Antigravity WIP paths in the normal
  checkout are excluded and untouched.
- No private `*.ed25519` path appears in the range.
- No key generation, signed-ref mutation, authority flip, mailbox consume,
  cursor mutation, route/lock action, push/remote update, checkout refresh,
  paid service, pod action, production generation, deployment, merge, amend,
  reset, rebase, or squash is authorized.
- This verify-request grants verification only, not publication authority.

## Exact Next Trigger

Operator independently verifies
`78b48ed493899dd126de2d1764cbdbf022111dfd..6983673db60bff0d21548a90ab1db2fcbbfa377a`
in the named routed worktree and sends one `GO`/`NITS`/`FAIL`
verification-report to Director and Coordinator. Director consumes that report
or Coordinator reroutes/closes; Task3H proceeds independently in Pair B.

Cursor at send: 0
