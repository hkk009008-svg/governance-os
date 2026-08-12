# Coordinator -> All: Ledger Phase 2 Task 2.2 Publication Executor Token

**When:** 2026-07-08T13:58:26Z - **From:** coordinator (online)

Event type: coordination
Task-board: `ledger-phase2-task22-2026-07-08`
Publication range: `e446218740b96561933da66c8808f2a1fd64d253..36f5506`
Closeout: `coordination/mailbox/sent/2026-07-08T13-51-22Z-coordinator-to-all-coordination.md`
Operator GO: `coordination/mailbox/sent/2026-07-08T13-47-47Z-operator-to-all-verification-report.md`

## Capacity Packet Coverage

Capacity packet coverage list:
- `coord-ledger-t14-align-route`
- `director-ledger-publication-decision`
- `director2-ledger-next-brief`
- `operator-pipeline-tooling-verify`
- `operator2-ledger-main-verify`
- `coord-ledger-t14-align-join`
- `coord-ledger-runway-stage0-route`
- `director-ledger-runway-stage0-owner-gates`
- `director2-ledger-runway-plan-reconcile`
- `operator-ledger-runway-stage0-verify`
- `operator2-ledger-runway-worktree-verify`
- `coord-ledger-runway-stage0-join`
- `coord-ledger-phase2-task21-route`
- `director-ledger-phase2-task21-write-path`
- `director2-ledger-phase2-bounds-plan-sync`
- `operator-ledger-phase2-task21-lanev`
- `operator2-ledger-phase2-base-preflight`
- `coord-ledger-phase2-task21-join`
- `coord-unit-coherence-side-effect-token-join`
- `director-unit-coherence-side-effect-token-impl`
- `director2-unit-coherence-observer-standby`
- `operator-unit-coherence-side-effect-token-verification`
- `operator2-unit-coherence-observer-standby`
- `coord-execution-strength-broader-join`
- `director-execution-strength-broader-impl`
- `director2-execution-strength-broader-observer`
- `operator-execution-strength-broader-verification`
- `operator2-execution-strength-broader-observer`
- `coord-ledger-phase2-task22-join`
- `director-ledger-phase2-task22-validations`
- `director2-ledger-phase2-task22-observer`
- `operator-ledger-phase2-task22-lanev`
- `operator2-ledger-phase2-task22-observer`

Join condition: publication executor token is valid only after Task 2.2
coordinator closeout, operator GO for corrected range `e446218..36f5506`, live
remote preflight showing `origin/main` at `e446218`, valid capacity board, and
valid route validation for this artifact.

## Side-Effect Executor Token

- side_effect_id: evidence-ledger-phase2-task22-publication-main-2026-07-08
- executor: coordinator
- target: /Users/hyungkoookkim/Pipeline/.worktrees/evidence-ledger-phase2-task22-2026-07-08 origin/main refs/heads/main
- allowed_command_class: git push origin HEAD:refs/heads/main
- preflight: ledger_start_guard, seat_status, clean target worktree, live ls-remote origin/main, HEAD 36f5506, origin/main e446218 ancestor of HEAD, diff --check clean
- stop_if_newer_mail_or_live_target_satisfied: re-read mailbox for same side_effect_id and live ls-remote; stop if origin/main already equals 36f5506 or moved to a non-ancestor
- postcheck: ls-remote origin refs/heads/main, fetch origin main, rev-list HEAD...origin/main equals 0 0
- observer_seats: director, director2, operator, operator2
- final_closeout_owner: coordinator
- non_goals: no force-push, no lock action, no cursor consume, no paid API spend, no pod spend, no production generation, no evidence-ledger product edit, no normal evidence-ledger checkout refresh

Detailed allowed command:

```text
env -u GIT_INDEX_FILE git -C /Users/hyungkoookkim/Pipeline/.worktrees/evidence-ledger-phase2-task22-2026-07-08 push origin HEAD:refs/heads/main
```

Detailed preflight:

```text
env -u GIT_INDEX_FILE .venv/bin/python scripts/ledger_start_guard.py --seat coordinator --wave 2
env -u GIT_INDEX_FILE .venv/bin/python .agents/skills/four-seat-protocol/scripts/seat_status.py coordinator --wave 2
env -u GIT_INDEX_FILE git -C /Users/hyungkoookkim/Pipeline/.worktrees/evidence-ledger-phase2-task22-2026-07-08 status --short --branch
env -u GIT_INDEX_FILE git -C /Users/hyungkoookkim/Pipeline/.worktrees/evidence-ledger-phase2-task22-2026-07-08 ls-remote origin refs/heads/main
env -u GIT_INDEX_FILE git -C /Users/hyungkoookkim/Pipeline/.worktrees/evidence-ledger-phase2-task22-2026-07-08 rev-parse HEAD
env -u GIT_INDEX_FILE git -C /Users/hyungkoookkim/Pipeline/.worktrees/evidence-ledger-phase2-task22-2026-07-08 merge-base --is-ancestor e446218740b96561933da66c8808f2a1fd64d253 HEAD
env -u GIT_INDEX_FILE git -C /Users/hyungkoookkim/Pipeline/.worktrees/evidence-ledger-phase2-task22-2026-07-08 diff --check e446218740b96561933da66c8808f2a1fd64d253..HEAD
```

Detailed stop_if_newer_mail_or_live_target_satisfied:

- Stop without pushing if any newer same-target mailbox artifact claims `side_effect_id` `evidence-ledger-phase2-task22-publication-main-2026-07-08`.
- Stop without pushing if live `origin/main` already equals `36f55063a2d87312810e82db624b837289a4a382`.
- Stop without pushing if live `origin/main` is not `e446218740b96561933da66c8808f2a1fd64d253` and the new live ref is not an ancestor of `HEAD`.

Detailed postcheck:

```text
env -u GIT_INDEX_FILE git -C /Users/hyungkoookkim/Pipeline/.worktrees/evidence-ledger-phase2-task22-2026-07-08 ls-remote origin refs/heads/main
env -u GIT_INDEX_FILE git -C /Users/hyungkoookkim/Pipeline/.worktrees/evidence-ledger-phase2-task22-2026-07-08 fetch origin main
env -u GIT_INDEX_FILE git -C /Users/hyungkoookkim/Pipeline/.worktrees/evidence-ledger-phase2-task22-2026-07-08 rev-list --left-right --count HEAD...origin/main
```

Detailed non_goals:

- No force push.
- No lock claim or release.
- No cursor consume.
- No paid API spend.
- No pod spend.
- No production generation.
- No evidence-ledger product edit.
- No normal evidence-ledger checkout refresh.
- No Pipeline production behavior edit.

## Evidence

- User requested publication after the closeout exact next trigger named publication handling for `e446218740b96561933da66c8808f2a1fd64d253..36f5506`.
- `env -u GIT_INDEX_FILE git -C /Users/hyungkoookkim/Pipeline/.worktrees/evidence-ledger-phase2-task22-2026-07-08 ls-remote origin refs/heads/main` -> `e446218740b96561933da66c8808f2a1fd64d253 refs/heads/main`.
- `env -u GIT_INDEX_FILE git -C /Users/hyungkoookkim/Pipeline/.worktrees/evidence-ledger-phase2-task22-2026-07-08 rev-parse HEAD` -> `36f55063a2d87312810e82db624b837289a4a382`.
- `env -u GIT_INDEX_FILE git -C /Users/hyungkoookkim/Pipeline/.worktrees/evidence-ledger-phase2-task22-2026-07-08 rev-list --left-right --count HEAD...origin/main` -> `3 0`.
- `env -u GIT_INDEX_FILE git -C /Users/hyungkoookkim/Pipeline/.worktrees/evidence-ledger-phase2-task22-2026-07-08 merge-base --is-ancestor e446218740b96561933da66c8808f2a1fd64d253 HEAD` -> exit 0.
- `env -u GIT_INDEX_FILE git -C /Users/hyungkoookkim/Pipeline/.worktrees/evidence-ledger-phase2-task22-2026-07-08 diff --check e446218740b96561933da66c8808f2a1fd64d253..HEAD` -> no output.
- `env -u GIT_INDEX_FILE git -C /Users/hyungkoookkim/Pipeline/.worktrees/evidence-ledger-phase2-task22-2026-07-08 diff --name-only e446218740b96561933da66c8808f2a1fd64d253..HEAD -- data '*.xlsx' ios/EvidenceLedger/Sources/Config.plist` -> no output.

## Exact Next Trigger

Coordinator runs the command named in `allowed_command_class` after preflight,
then writes one publication-confirmed status/handoff with live remote-ref
postcheck evidence.

Cursor at send: 0
