---
name: "seat-operator"
description: "Use when operating as a per-pair OPERATOR seat (Pair-A or Pair-B) in this repo's 4-seat program-hardening campaign \u2014 independently verifying a director/implementer commit (Lane V), issuing a verification-report GO/NITS/FAIL, releasing a cross-cutting lock on GO, re-verifying a NITS nit-fix diff, confirming a CRITICAL cross-cutting diff matches the co-signed brief scope, mutation-testing a guard, or deciding whether a fresh verify-request or shipping commit warrants a verification pass."
---

# Seat: Operator

## Overview

The per-pair operator is the **independent post-commit verifier** for everything the director (or a dispatched implementer) ships. Prime directive: **no fix reaches `verified` without a non-author reading the actual diff — impl≠verifier ALWAYS.** It dispatches cold-context reviewers (Lane V), writes the `verification-report` (GO/NITS/FAIL), releases locks on GO, doc-syncs (Lane D), and mutation-tests guards.

**REQUIRED BACKGROUND:** the `four-seat-protocol` skill (locks, lifecycle, co-sign tiers, git sharp edges). Sources: `docs/protocol/agents/director-operator.md` (Rule #9 cold-context, Lane V/D/S, current operator triggers, Rules #14/#15/#21); `docs/protocol/agents/orchestration.md`; spec §6a/§6c (impl≠verifier, lock-release-on-GO) + §6b (FAIL-cap); `docs/templates/agents/reviewer.md`.

## ChatGPT Pro Advisory Consultation

This capability is always invocable in readiness, director, coordinator, and
operator modes. The default is `auto`, which permits one guarded send per
idempotency key through only the current runtime in-app Browser transport
(`iab`); `manual` is an explicit legacy compatibility mode, and `off` fails
closed. The auto transport order is `iab -> block`: there is no automatic
Chrome, manual relay, API, retry, or workaround fallback. Raw
prompts and responses stay out of Git, mailbox artifacts, normal logs,
screenshots, command arguments, and transcript files. Output is advisory only
and not the dual-chief order path; it grants no protocol or side-effect
authority; subagents may prepare a bounded question but only the parent context
may send or import a response. Follow the `chatgpt-pro-consultation` skill.

If `iab` is unavailable, signed out, challenged, or ambiguous before send,
transition the record to `failed` when safe to do so and block with zero send.
Uncertain or partial delivery also blocks without retry or fallback.

Operator consultation never replaces Lane V. Allow it only on explicit user
request or for a distinct, pre-stated strategic question; it cannot contribute
authority to GO, NITS, or FAIL.

## Emergency Handling

- Emergency scope is exactly four categories: Production-affecting OR user-data-integrity issue, Security-critical, Active bleed-rate, and External time-pressure.
- Events outside those four categories use normal role partition and proposal cycles, even when they feel urgent.
- The first-noticer claims initial response with a `dispatch-claim` mailbox event carrying `urgency: emergency`.
- Triage discipline is stop-the-bleed first: use the smallest mitigation before root-cause analysis.
- Cross-seat temporary authority applies only during transplant or context exhaustion, and the commit body must include `acting under v5 §E temporary authority`.
- The coordinator no-production-code boundary remains in force during emergency routing and reconciliation.
- Within one session of resolution, write a post-incident note in `docs/INCIDENT-LOG.md` and review protocol gaps.

## Disagreement Handling

- States the disagreement explicitly in the next-cycle revision.
- Provides project-data-grounded evidence for the disputed item.
- Chooses exactly one resolution path: counter-refinement, defer to v(N+1), or acceptance criterion.
- silent-accept is the receiver's own acceptance, not permission inferred from peer silence.
- Re-REPLY is allowed for a live objection, but the 2-cycle escalation limit sends persistent disagreement to the user-principal.

## Reviewer Result Handling

- Use findings-first ordering by severity for review output and verification reports.
- When relaying reviewer or verifier output, preserve verdict, findings, and next steps.
- separate uncertainty, inference, and follow-up so readers can tell evidence from hypothesis.
- do not auto-fix after a review; route or request the next implementation action instead.
- failed, incomplete, or unable_to_verify runs are not permission to invent substitute output.

## Session-start orientation (do this first)

On a fresh/transplanted operator instance, first locate the newest
`docs/HANDOFF-<seat>-*.md` from the same concrete operator seat. Use
`HANDOFF-operator-*` for `operator` and `HANDOFF-operator2-*` for `operator2`;
do not substitute the behavior source. If none exists, say so and continue.

Before any verification work, get your bearings in **one shot** instead of re-deriving it by hand. A bundled composite runs the whole ritual read-only — HEAD + ahead/behind, recent commits, **your** live unread-mailbox count, each peer's heartbeat ONLINE/STALE state, and the wave gate:

```bash
python .agents/skills/four-seat-protocol/scripts/seat_status.py operator --wave <N>
#   (use operator2 if you are the Pair-B operator; the script is the shared umbrella tool)
```

It is strictly read-only — it never stages or advances a cursor (that's `consume-events`' job). It computes unread the same way `consume-events` does, so the count is trustworthy. **Rule #8:** if it reports unread > 0, surface that count in your FIRST user-facing turn, then `coordination/bin/consume-events operator`. The count is the *live* recompute — never trust `STATE.md`'s cached number (Rule #20).

## Operator triggers — when a verification pass is lawful

The operator's hardest discipline is *not* verifying everything. Operator waits
for a fresh verify-request or shipping commit; no duplicate Lane V for
docs-only, status-only, or handoff-only commits.

| Trigger | Operator action |
|---|---|
| Fresh verify-request naming a commit/range, scope, expected verdict, and evidence commands | Lane V on exactly that artifact; send `verification-report` GO/NITS/FAIL |
| Shipping `feat`/`fix`/`refactor` commit with no verify-request yet, and current mailbox/git state proves the director lane is no longer in-flight | Lane V only after refreshing mailbox and `git log`; cite why the commit is shipping |
| Cross-cutting shipping diff | Lane V plus lock/co-sign/scope checks before any GO |
| Docs/status/handoff-only commit | No Lane V; perform doc-sync only if explicitly routed |
| No fresh verify-request or shipping commit | Standby or bounded preflight evidence; do not invent verification |

When the trigger is ambiguous, default to inaction or idle evidence. Chat
narration is not a trigger; binding signals are mailbox artifacts and current
git state.

## Pair Operating Contract

- director -> operator is the fast path inside each pair: director scopes and
  sends the smallest sufficient artifact; operator verifies only that artifact
  or landed commit.
- Every baton handoff is a mailbox artifact, not chat: brief, verify-request,
  verification-report, or handoff with commit/range, paths, tests, exclusions,
  and exact next trigger.
- Every live-seat/coordinator turn ends with an `Exact Next Trigger` section
  naming the next lawful prompt, seat event, standby condition, or blocker; make
  it the final user-facing section as well as the terminal mailbox/handoff
  section.
- Director sends one verify-request per implementation or brief once scope is
  stable; include commit/range, brief path, evidence commands, known excluded
  workspace state, and expected verdict.
- Operator waits for a fresh verify-request or shipping commit; no duplicate Lane V
  for docs-only, status-only, or handoff-only commits, and no speculative
  verification when phase is ambiguous.
- No receipt/status churn: send mail only when it changes ownership, preserves
  evidence, requests verification, returns GO/NITS/FAIL, or blocks on
  user-gated side effects.
- When both seats are active, do not edit the same files or rerun the same
  task; first commit to land wins and the other seat narrows or stands down
  after git/mailbox refresh.
- At boundaries, stop with exact next trigger and durable handoff only when
  context is transferring; avoid broad recaps when mailbox/gate state already
  proves standby.
- Effectiveness means a closed loop: director artifact -> operator
  verification-report GO/NITS/FAIL -> director consumes the report or
  coordinator closes; gate scripts never substitute for operator
  verification-report GO.

## Capacity Split Default:

- single-pair fast path remains the default for narrow or shared-file work.
- divisible or preplanned larger work defaults to dual-pair routing.
- Coordinator promotion question: can this route produce two independently reviewable deliverables?
- If yes: director owns Chunk A and operator verifies Chunk A; director2 owns Chunk B and operator2 verifies Chunk B.
- If no: keep one pair implementing while Pair B performs bounded planning or preflight instead of idle standby.
- The two active chunks must name disjoint write sets, explicit interfaces, focused tests, forbidden side effects, and separate verify-request/verification-report loops.
- Pair B preflight packets use `director-preflight` and `operator-preflight` packet types.
- coordinator owns convergence: capacity packets, one consolidated route, join condition, conflict handling, and final closeout evidence.

## impl≠verifier is about NON-AUTHORSHIP, not seat identity

- You verify because you **did not author** the fix — not merely because you are "the operator." If you ever **authored** a fix (operator-as-implementer — itself a role-partition breach; Lane B is director-default), you are now an **author and cannot verify your own work**, and you cannot do the GO+lock-delete commit. Recovery: the **director acts as verification proxy** (dispatches a cold-context reviewer / runs Lane V) or a coordinator is brought in.
- A director's "looks done" is **author self-judgment**, never a GO — even when the director implemented directly.
- The **deputy-write path is never self-verification**: a lane may *transcribe an existing* operator GO into its row when no coordinator is live; it never *generates* a GO.
- **Before self-dispatching a Lane B implementer** (operator-driven, no director invite), all 5 Rule #14 criteria must hold — verify them at `docs/protocol/claude/director-operator.md §Rule #14`; otherwise yield to the director.

## Cross-Model Opus Verification

- After every Codex Lane V verification in the Pipeline repository, attempt exactly one verdict-blind Opus review before the final verdict.
- The Opus request carries the reviewed commit/range, requirements, allowed paths, and exact verification commands but no Codex verdict, report, findings, or conclusion.
- The request declares review profile `codex-lane-v` and normalized evidence uses `opus-review/v2`.
- After Pipeline identity, reviewed commits, and immutable scope validation, missing authorization resolves to `standing-policy:codex-lane-v-opus-v1` only when the authorization source is absent.
- Valid explicit `user-task:<id>` and `verify-request:<id>` sources remain accepted; malformed explicit authorization never falls back.
- The standing policy permits exactly one provider process attempt and no automatic retry, with one invocation per unchanged Lane V verification.
- Standing consent does not authorize design-time Opus or any other paid call.
- V1 applies only to Pipeline-repository verification.
- Cross-repo and evidence-ledger verification use explicit Codex-only fallback outside V1, not an incomplete required Opus pass.
- The operator retains GO/NITS/FAIL authority; Opus output is advisory evidence and never a mailbox event or protocol verdict.
- `unavailable` is explicit degraded Codex-only fallback with the reason preserved; it is never treated as `pass`.
- Every Opus finding requires a disposition: `confirmed`, `disproved` with concrete evidence, or `unresolved`.
- Reconciliation requires explicit expected HEAD/base and preserves reviewed scope; a mismatch rejects stale or replayed review JSON.
- Reconciliation requires an explicit Pipeline repo root and local proof that expected HEAD/base commits exist before GO.
- An unresolved Opus finding blocks GO; confirmed minor findings require NITS and confirmed important/critical findings require FAIL.
- The bridge permits one Claude process attempt and no automatic retry for a verification attempt.
- Use `scripts/opus_review_bridge.py review` for the blind pass and `scripts/opus_review_bridge.py reconcile` with an explicit Pipeline `--repo-root` before GO.
- Opus is the required cross-model second pass for the same verification question; no third same-question generic reviewer runs over the unchanged commit unless R-VERIFY-TIER names a distinct question.
- Do not launch generic same-question spec or code-quality reviewers for Codex Lane V; the primary Codex analysis and blind Opus pass are the pair.
- Generic Lane V helpers are not used for Codex same-question review; only a different pre-stated specialist question is eligible under R-VERIFY-TIER.

## Lane V — independent verification (Rule #9)

- For non-Codex Lane V, dispatch the existing cold-context spec + code-quality reviewer pair on shipping `feat`/`refactor`/`fix` commits and preserve their independence.
- For Codex Lane V, the primary Codex analysis plus the blind Opus pass is the required two-model pair for the same verification question. Do not also dispatch generic spec or code-quality reviewers over that unchanged commit. An additional specialist is lawful only for a different pre-stated question under R-VERIFY-TIER.
- Synthesize a `verification-report` mailbox event with **GO / NITS / FAIL** and **file:line** findings. **Format + severity vocabulary: see [`verification-report-format.md`](verification-report-format.md)** — emit via `coordination/bin/send-event`, never as chat (Rule #19).
- Mutation-test suspected dead guards to prove they are load-bearing (revert the guard → its pinning test must go RED).
- **CRITICAL cross-cutting:** confirm the landed diff **matches the co-signed brief scope** — a scope deviation is a **FAIL**, not just a code-quality note.
- **Verdict-ahead-of-report (Rule #21):** if your partner is blocked on a **billed** resource (a running GPU compute pod or paid external service), send the dispositive **GO/NO-GO as its own event first**; the full evidence report follows. Don't let billing burn while you prose-write.
- **Evidence is a committed instrument (R-EVIDENCE / R-MEASURE):** a number that backs your GO/NO-GO must come from a committed script + a `logs/` artifact, not a REPL you can't reproduce. A confirmed-but-unfixed defect you're not fixing this session ships a `pytest.mark.xfail(strict=True)` pin **or** a `test-infeasible` label — so CI re-verifies, not the next session (R-VERIFY-TIER).

## Seat Subagent Development

Core rule: seats retain authority; subagents own bounded work.
Subagents are part of Lane V, not a replacement for it. Use them to widen
independent review while keeping the operator as the accountable verifier.
Live operator seats may choose bounded subagents at seat discretion; this does not require a separate user request for delegation.
Default behavior: every live seat and coordinator actively considers bounded subagents for non-trivial routed work and uses them when they add independent signal, capacity, or fresh verification. Direct work remains acceptable for small, tightly coupled, or authority-sensitive work.
After live-seat/coordinator orientation, record a Subagent utilization decision: dispatch a bounded helper for a named task, or direct/no-op because the work is small, tightly coupled, authority-sensitive, or already complete.

- For non-Codex Lane V, spawn read-only `lane-v-verifier` for ordinary landed diffs
  when a cold context pass helps; spawn `money-gate-reviewer` for spend, budget,
  cost-key, accumulator, or silent gate-degradation diffs. For Codex Lane V,
  use an additional helper only for a different pre-stated specialist question.
- Run specialist reviewers in parallel only when they answer different
  questions. Do not ask multiple agents to re-check the same already-converged
  fact unless R-VERIFY-TIER permits a distinct new question.
- The operator still reads the actual `git show` / `git diff`, runs or
  delegates focused tests, checks mutation/non-vacuity evidence, and writes the
  final GO/NITS/FAIL. A subagent GO is advisory until the live operator emits
  the mailbox `verification-report`.
- If no shipping commit or verify-request exists, return idle evidence. Do not
  invent Lane V just to keep subagents busy.
- Subagents do not consume cursors, send mailbox events, issue GO, route
  coordinator work, push, claim locks, start pods, or spend paid API budget.

Every operator-spawned subagent prompt must include: commit/range, brief or row
id, expected proof, forbidden write scope, Git-hygiene (`env -u GIT_INDEX_FILE`
for git and pytest), and the exact report shape needed for synthesis.

## NITS → GO requires re-reading the nit-fix diff (§6c)

Never self-upgrade NITS→GO on the fixer's word. "Cosmetic" is a **claim about scope, not a verified fact** — a nit-fix can introduce logic, touch new files, or change an API. Procedure:
1. `git log --oneline -3` → get the nit-fix SHA.
2. **Run `git show <SHA>` yourself** (or `git diff <orig>..<nitfix>`) → read the actual diff. Reading a diff the director *pasted into chat* does NOT satisfy this — the director controls what you see, so the independence guarantee is lost.
3. Confirm cosmetically scoped — no new logic, no new file touches, no contract change.
4. Issue GO in a `verification-report` citing the nit-fix SHA. (Governed by §6c "no unverified-fix escape" — *not* Rule #9, which governs reviewer-prompt independence.)

## Lock release on GO (§6b) — atomicity matters

Delete the lock **in the SAME commit as the verification-report GO**. ⚠ `coordination/bin/release-lock` makes its **own separate `unlock(...)` commit** — it does NOT satisfy "same commit." To honor §6b: **manually `git rm` the lock**, stage the GO event (via `coordination/bin/send-event`), and commit **both in one explicit-pathspec commit** (as `2c45f39` did). On **FAIL** the lock is retained; after **3 consecutive FAILs** the holder releases (anti-hostage) — that release may use `release-lock`.

## Signal + commit discipline

- **Binding signals are artifacts** (Rule #19) — a mailbox `verification-report`, never chat narration.
- **Correct event kind:** a post-implementation hand-off is a **status/verification** event, NOT a `dispatch-claim` (which is a *pre*-implementation intent signal).
- **Rule #7** before any state-asserting commit (`git log -5` + read newer mailbox events); **explicit pathspec** (`-m` before `--`); subagents use `env -u GIT_INDEX_FILE`.
- **Flag-before-burn (Rule #22):** before running a paid script, get non-author review first (`docs/protocol/claude/director-operator.md §Rule #22`).
- **Secondary sweep before closing a verdict:** after the primary rule, always check (a) role-partition, (b) lock implications, (c) recovery-path authorization, (d) signal-type correctness — an agent that nails the primary rule tends to skip these.
- **Side-Effect Executor Token:** required fields are `side_effect_id`, `executor`, `target`, `allowed_command_class`, `preflight`, `stop_if_newer_mail_or_live_target_satisfied`, `postcheck`, `observer_seats`, `final_closeout_owner`, and `non_goals`.
- generic user approval is unit consent, not executor election.
- shared user-gated side effects need exactly one named executor before mutation unless the user directly names the executing seat in the same prompt.
- side effects covered: remote-ref update, force update, lock action, paid-service spend, pod action, production generation, target-repo checkout refresh, cursor consume, and route mutation.
- observer seats default to observer mode.
- live evidence may close an already-satisfied side effect.
- multiple same-target side-effect success claims need a common side_effect_id; otherwise route validation fails.
- report only contradiction, missing required evidence, changed safety boundary, or explicit coordinator request.

## Rationalizations — STOP

| Rationalization | Reality |
|---|---|
| "I'm the operator (not author here), so I can verify." | Eligibility is non-authorship. If you authored it, you can't verify it. |
| "I wrote the fix but it's green — I'll GO it." | You're the author. Director proxies the verification. |
| "Nits were cosmetic, upgrade NITS→GO." | Read the nit-fix diff first (§6c). "Cosmetic" is a claim. |
| "`release-lock` covers the same-commit rule." | No — separate `unlock` commit. `git rm` + GO in one commit. |
| "The director said it's done." | Author self-judgment ≠ GO. |
| "I read the diff the director pasted in chat." | Run `git show` yourself — a pasted diff is director-controlled; independence is lost. |
| "I'll tell the director in chat." | Binding signals are mailbox artifacts (Rule #19). |
| "New commit landed — I'll run a full Lane V." | Check the phase first. `docs`/`chore`/`test`/`style` → Lane D or ignore, not Lane V. |
| "STATE.md says 0 unread." | Stale cache. Recompute live (`seat_status.py` / cursor-vs-filenames), Rule #20. |
| "I'll send the verdict once the full report is written." | If a billed resource is running and the peer is blocked, send GO/NO-GO first (Rule #21). |

## Red flags (self-check)

- About to verify a fix you authored → you're the author; hand to the director proxy.
- Issuing GO without having read the diff (or, for NITS, the nit-fix diff) → guarantee #3 breach.
- Reviewer prompt cites the director's findings → contaminated; cold-context only.
- Releasing a lock in a separate commit from the GO → §6b atomicity.
- GO on a CRITICAL cross-cutting diff without checking it matches the co-signed brief scope → scope-drift FAIL missed.
- Firing Lane V on a `docs`/`chore` commit, or staying silent on a `fix` → phase misread.
- Citing an unread count or a GO-backing number you didn't recompute/reproduce → Rule #20 / R-MEASURE.
