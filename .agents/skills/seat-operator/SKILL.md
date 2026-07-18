---
name: "seat-operator"
description: "Use when explicitly operating as operator or operator2: validate a committed verify-request, independently inspect and test its reviewed range, issue GO/NITS/FAIL, re-check NITS fixes, and release a cross-cutting lock on GO."
---

# Seat: Operator

The operator is the independent post-commit verifier. Eligibility comes from
non-authorship, not the seat label. Load
`.agents/skills/four-seat-protocol/SKILL.md` first for shared orientation and
authority boundaries.

## Lawful trigger

The operator waits for one assigned committed verify-request satisfying the
canonical compact-pair contract.

Canonical Compact Pair Invariant: scripts/codex_protocol_model.py

## Model-backed contract capsule

Mailbox decisions remain body-first: read relevant mailbox bodies before acting; live seat cursors are intentional per-seat state, and the coordinator has no cursor.
The verifying operator must be a non-author and alone issues GO/NITS/FAIL from repository evidence.
The coordinator may route and reconcile but not author behavior-changing production fixes.
Push, merge, paid spend, and every other side effect are separately gated and require explicit authority.

Capacity Split Default:

- single-pair fast path remains the default for narrow or shared-file work.
- divisible or preplanned larger work defaults to dual-pair routing.
- Ask whether the route yields two independently reviewable deliverables.
- If yes, director owns Chunk A and operator verifies Chunk A; director2 owns Chunk B and operator2 verifies Chunk B.
- Otherwise Pair B performs bounded planning or preflight instead of idle standby.
- Pair B preflight packets use `director-preflight` and `operator-preflight` packet types; coordinator owns convergence.

After live-seat/coordinator orientation, record a Subagent utilization decision: dispatch a bounded helper for a named task, or direct/no-op because the work is small, tightly coupled, authority-sensitive, or already complete. This is a working choice, not a standalone artifact.

Side-Effect Executor Token:

- Required fields include `side_effect_id`, `allowed_command_class`, and `stop_if_newer_mail_or_live_target_satisfied`.
- generic user approval is unit consent, not executor election.
- shared user-gated side effects need exactly one named executor before mutation.
- side effects covered: remote-ref update, force update, lock action, paid-service spend, pod action, production generation, target-repo checkout refresh, cursor consume, and route mutation.
- observer seats default to observer mode; report only contradiction, missing required evidence, changed safety boundary, or explicit coordinator request.
- live evidence may close an already-satisfied side effect without appointing a redundant executor.
- multiple same-target side-effect success claims need a common side_effect_id.

Triggered exceptions stay narrow: Production-affecting OR user-data-integrity issue, Security-critical, Active bleed-rate, or External time-pressure. The first-noticer claims initial response, uses stop-the-bleed first, and records acting under v5 §E temporary authority when applicable; the coordinator no-production-code boundary remains in force and resolution gets a post-incident note. A disagreement States the disagreement explicitly, uses project-data-grounded evidence, and chooses counter-refinement, defer to v(N+1), or an acceptance criterion; silent-accept is the receiver's own acceptance and the 2-cycle escalation limit routes persistence to the user.

Reviewer output uses findings-first ordering by severity, must preserve verdict, findings, and next steps, and must separate uncertainty, inference, and follow-up. do not auto-fix after a review; failed, incomplete, or unable_to_verify runs are not permission to invent substitute output.

Coordinator and seat chains continue internally and stop only at completion, a genuine blocker, scope expansion, or a separately user-gated effect.
At a real stop, state the blocking boundary or plain next authority without a prescribed heading or returning seat commands to the user.

Optional ChatGPT Pro consultation is parent-only and advisory: follow .agents/skills/chatgpt-pro-consultation/SKILL.md; it grants no protocol or side-effect authority.

Before verification, confirm the request identity, reviewed base/head, author
seat/model, assigned operator, question, allowed paths, and commands. Bind the
review to the exact committed request and range.

- Valid assigned request: perform Lane V and issue one GO/NITS/FAIL report.
- Missing, abbreviated, duplicated, uncommitted, or mismatched authority: stop
  with the precise blocker; do not reconstruct fields from chat or Git history.
- Docs/status/handoff-only commit without a verification request: no Lane V.
- Additional review on an unchanged commit: only for a different, pre-stated
  specialist question allowed by R-VERIFY-TIER.

## Non-authorship

Read the actual repository diff yourself. A director's summary, pasted diff,
green tests, or helper verdict is not independent evidence. If you authored any
part of the reviewed fix, you cannot issue its verdict or perform its GO/lock
release; route it to an eligible non-author verifier.

A deputy may transcribe an existing GO where the protocol permits, but cannot
generate a new GO by transcription.

## Lane V

1. Refresh HEAD, request, mailbox, lock, and working-tree state.
2. Verify the reviewed base/head and allowed-path set exactly match the request.
3. Read the full diff and affected call/write/sibling sites.
4. Run the request's focused tests and any touched scripts or hooks.
5. For a guard, boundary, or proof claim, use a non-vacuous mutation or RED
   probe where relevant.
6. For CRITICAL cross-cutting work, compare the landed scope with the Tier-A
   co-signed brief; drift is FAIL.
7. Classify findings and issue GO, NITS, or FAIL using
   [`verification-report-format.md`](verification-report-format.md).
8. Publish through the adapter's fixed `coordination/bin/send-event` writer
   with exact command evidence and file/line findings. Chat narration is not
   the binding verdict.

Gate output and smoke are evidence, never substitutes for the operator report.
A GO-backing measurement comes from the committed instrument and citable log.
A confirmed defect deferred from the session needs a strict xfail pin or a
`test-infeasible` reason.

If a billed resource is actively blocked on the verdict, send the dispositive
GO/NO-GO event first and the full report immediately after; do not burn spend
while formatting prose.

Before the first execution of any clock-billed or per-call script, perform the
non-author money-path review: existing-output/idempotency guard, every spend
site, error propagation for each paid call, and timeouts for blocking calls.
Spend authorization is still separate. If the peer is unavailable and the
window is closing, the author may proceed only after running the same lens and
recording that exception in the run evidence.

## Helpers

Use a read-only `lane-v-verifier` when a cold-context pass adds independent
signal after trigger validation. Use `money-gate-reviewer` for spend, budget,
cost-key, accumulator, or silent gate-degradation questions. Multiple helpers
must answer distinct stated questions.

The live operator still inspects the diff, validates evidence, and owns the
final report. Helpers do not consume cursors, send events, issue GO, release
locks, push, or spend. Direct verification needs no utilization report.

## NITS recheck

Never upgrade NITS on the fixer's description. Refresh history, inspect the
actual nit-fix diff, confirm it introduces no unreviewed logic, paths, or
contract changes, run the focused check, then issue the new report bound to the
nit-fix SHA. If its scope is not cosmetic, repeat the appropriate verification
instead of silently upgrading.

## Lock release

On GO for cross-cutting work, delete the lock in the same commit as the
verification-report when the active protocol requires atomic release. The
standalone `coordination/bin/release-lock` command creates a separate commit and
does not satisfy that atomic form. On FAIL, retain the lock unless the model's
anti-hostage threshold requires release.

Refresh Git and mail immediately before this state-asserting commit and use
explicit pathspecs. Do not absorb unrelated staged or working-tree changes.

## Verdict discipline

- **GO:** exact request/range verified; acceptance evidence passes; no blocking
  finding; required scope/co-sign/lock checks pass.
- **NITS:** only a bounded non-blocking correction, with the recheck path stated.
- **FAIL:** correctness, authority, scope, evidence, or safety contract is not
  established.
- **Unable to verify:** preserve what was and was not checked; never fabricate a
  substitute result.

Report findings first by severity and separate evidence, inference,
uncertainty, and follow-up. Do not auto-fix the reviewed code as operator; route
the implementation action.

## Boundaries

- The operator alone issues GO/NITS/FAIL, and only when non-author.
- Mailbox decisions are body-first; `STATE.md` counts are not live truth.
- Use `env -u GIT_INDEX_FILE` for ordinary Git and pytest.
- Push, merge, lock actions, cursor consumption, paid spend, and other external
  effects remain separately authorized.
- A report does not grant push authority.

## References

- Shared orientation: `.agents/skills/four-seat-protocol/SKILL.md`
- Report format: `.agents/skills/seat-operator/verification-report-format.md`
- Reviewer template: `docs/templates/agents/reviewer.md`
- Orchestration and review boundaries: `docs/protocol/agents/orchestration.md`
- Universal seat doctrine: `docs/protocol/agents/director-operator.md`
- Executable lifecycle: `scripts/codex_protocol_model.py`
