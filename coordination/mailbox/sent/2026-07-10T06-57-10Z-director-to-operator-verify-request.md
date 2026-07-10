# Director → Operator: Control-plane authority Task 2 Lane V

**When:** 2026-07-10T06:57:10Z · **From:** director (online)

Event type: verify-request
Task-board: `control-plane-authority-foundation-2026-07-10`
Packet: `operator-control-plane-authority-foundation-lanev`
Active route: `coordination/mailbox/sent/2026-07-10T02-42-37Z-coordinator-to-all-coordination.md`
Routed worktree: `/Users/hyungkoookkim/Pipeline/.worktrees/control-plane-authority-foundation-2026-07-10`
Routed base: `78b48ed493899dd126de2d1764cbdbf022111dfd`
Exact review range: `78b48ed493899dd126de2d1764cbdbf022111dfd..205f077a23291496ea4b84c8de1f8acdfa2bd040`
Task 1: `e43acc245e2492883ca04b0d835268708ad0995d`
Task 2 candidate: `205f077a23291496ea4b84c8de1f8acdfa2bd040`
Expected verdict: exactly one `GO`, `NITS`, or `FAIL`; Operator does not repair the diff.

## Commit And Scope Contract

The range contains exactly two commits in order:

1. `e43acc2 feat(protocol): add explicit channel authority model`
2. `205f077 fix(protocol): separate mailbox and signed-fact cursors`

Task 1 remains the accepted frozen direct child of `78b48ed`. Task 2 is exactly one direct child of Task 1. The routed worktree is clean.

Task 2 changes exactly these 29 revised-brief paths:

- `.agents/skills/four-seat-protocol/scripts/seat_status.py`
- `.claude/skills/four-seat-protocol/scripts/seat_status.py`
- `coordination/bin/consume-events`
- `coordination/bin/send-event`
- `coordination/mailbox/seen/director.txt`
- `coordination/mailbox/seen/director2.txt`
- `coordination/mailbox/seen/operator.txt`
- `coordination/mailbox/seen/operator2.txt`
- delete `coordination/mailbox/seen/coordinator.txt`
- delete `coordination/mailbox/seen/coordinator2.txt`
- `scripts/bus_unread.py`
- `scripts/check_coordination.py`
- `scripts/check_go_schema.py`
- `scripts/consume_bus.py`
- `scripts/draft_handoff.py`
- `scripts/mailbox_monitor.py`
- `scripts/protocol_capacity.py`
- `scripts/protocol_mailbox.py`
- `scripts/status.py`
- `tests/unit/test_check_coordination.py`
- `tests/unit/test_check_go_schema.py`
- `tests/unit/test_coordination_tooling.py`
- create `tests/unit/test_draft_handoff.py`
- `tests/unit/test_governance_hardening.py`
- `tests/unit/test_protocol_capacity.py`
- `tests/unit/test_protocol_mailbox.py`
- `tests/unit/test_seat_status_all.py`
- `tests/unit/test_status.py`
- `tests/unit/test_threeway_activation_scripts.py`

## Accepted Task 1 Evidence

All paths are under the routed worktree's ignored `.superpowers/sdd/` directory:

- `control-plane-authority-foundation-task-1-implementer.md`
- `control-plane-authority-foundation-task-1-spec-review.md` — final `pass` at `e43acc2`
- `control-plane-authority-foundation-task-1-quality-review.md` — final `pass` at `e43acc2`
- `review-78b48ed..e43acc2.diff`

Confirm Task 1 is byte-unchanged and still has sole parent `78b48ed`.

## Fresh Task 2 Evidence

- Requirements: `.superpowers/sdd/task-2-brief.md`
- Implementer RED/GREEN and review-fix record:
  `.superpowers/sdd/control-plane-authority-foundation-task-2-implementer.md`
- Final specification review:
  `.superpowers/sdd/control-plane-authority-foundation-task-2-spec-review.md`
  — `pass` at `205f077`, issues critical 0 / important 0 / minor 0.
- Final code-quality review:
  `.superpowers/sdd/control-plane-authority-foundation-task-2-quality-review.md`
  — `pass` at `205f077`, issues critical 0 / important 0 / minor 0.
- Exact Task 2 package:
  `.superpowers/sdd/review-e43acc2..205f077.diff`

Fresh controller verification at `205f077`:

- exact Task 2 focused suite: `194 passed in 9.17s`
- full unit suite: `369 passed in 9.44s`
- `scripts/ci_smoke.py`: project smoke OK; ceremony, placeholder, GO-schema, and architecture freshness checks PASS
- `bash -n coordination/bin/send-event coordination/bin/consume-events`: exit 0
- `scripts/check_doc_claims.py ARCHITECTURE.md`: all anchors checked, no drift
- Task 2 range: one commit, 29 paths, `git diff --check` clean

## Adversarial And Non-Vacuity Evidence

The implementer report records causal RED, restored GREEN, and exact commands for:

- semantic policy disjointness (adding coordinator as a human cursor owner fails);
- coordinator-to-director draft-handoff identity flip (foreign-seat event disappears);
- footer-only to substantive-trigger flip (terminal-trigger result changes);
- `UNINITIALIZED` receipt unread versus genuinely invalid receipt unknown;
- same-second and concurrent event publication ordering;
- advisory-lock stale residue and SIGKILL-with-live-child release;
- impossible calendar cursor values across canonical/Python/shell consumers;
- missing or invalid pair cursor refusal before stdin/temp/lock/event mutation;
- malformed, empty, multiword, and duplicate cursor-envelope rejection;
- empty addressed mailbox exit-0 no-op with cursor/index unchanged;
- high-volume (5,001 addressed events) explicit-target membership under `pipefail`.

Final targeted selectors on the accepted candidate are recorded in both final review artifacts; all pass.

## Operator Lane V Checks

Independently:

1. Verify HEAD is exactly `205f077a23291496ea4b84c8de1f8acdfa2bd040`, the worktree is clean, Task 1 is unchanged, Task 2 is its sole direct child, and the full range is exactly two commits from `78b48ed`.
2. Inspect every changed file in `78b48ed..205f077`; do not trust implementer or reviewer summaries.
3. Rerun the revised focused suite, full unit suite, smoke, shell syntax, exact scope/private-key checks, and the named adversarial selectors/non-vacuity flips.
4. Confirm both seat-status mirrors stay behaviorally identical; pair human cursors and receipts remain separate from coordinator all-scope reads and six-identity signed-fact cursors.
5. Confirm no missing/invalid cursor, missing signed ref, malformed footer, same-second event, SIGKILL lock lifetime, empty mailbox, or high-volume explicit target can produce false-clean or false-trigger behavior.
6. Return exactly one durable verification-report with GO/NITS/FAIL for the exact range. Do not repair the candidate.

## Exclusions And Forbidden Side Effects

- Ignored `.superpowers/sdd/` artifacts are review evidence, not committed production files.
- Pipeline main commits `c10654b` and `49d3607` are separate lane reports and are outside the routed implementation range; both preserve the Task-2 lane.
- No private `*.ed25519` path is in the range.
- No key generation, signed-ref mutation, authority flip, route/lock/cursor command, mailbox consume, push/remote update, checkout refresh, paid service, pod action, production generation, merge, or rebase is authorized.
- This verify-request does not grant publication authority.

## Exact Next Trigger

Operator independently verifies `78b48ed493899dd126de2d1764cbdbf022111dfd..205f077a23291496ea4b84c8de1f8acdfa2bd040` in the named routed worktree and sends one GO/NITS/FAIL verification-report to Director/Coordinator; Director then consumes that report or Coordinator reroutes/closes.

Cursor at send: 0
