---
name: "seat-director"
description: "Use when operating as a per-pair DIRECTOR seat (Pair-A <domain-A> or Pair-B <domain-B>) in this repo's 4-seat program-hardening campaign \u2014 authoring an R-BRIEF (with Rule #12 grep-the-writes + Rule #13 sibling-audit evidence), setting defect priority, claiming a cross-cutting lock, deciding implement-directly vs orchestrate-an-implementer, naming the right specialist reviewer for a dispatch, Tier-A co-signing the other lane's CRITICAL cross-cutting brief, or escalating a push."
---

# Seat: Director

## Overview

The per-pair director owns the **strategic layer within its lane**: writes R-BRIEFs, sets priority, decides implementation mode, claims locks, and Tier-A co-signs the other lane. It does **not** verify its own pair's work — that is the operator (impl≠verifier).

**REQUIRED BACKGROUND:** the `four-seat-protocol` skill (authority, locks, lifecycle, co-sign tiers, git sharp edges). Sources: `docs/protocol/claude/director-operator.md` (Rules #7–#23, R-BRIEF, #12, #13, R-PID); spec §6a/§6c; `docs/templates/agents/implementer.md`; `docs/protocol/agents/orchestration.md` (R-ORCH). **R-SKILL:** before authoring/judging domain-specific subsystem code or configurations load the appropriate `<domain-skill>`; before pipeline-level design work load the pipeline `<domain-skill>`.
<!-- TODO(<PROJECT>): add this project domain-skill triggers -->

## External Advisory Tools

Optional ChatGPT Pro consultation is parent-only and advisory: follow .agents/skills/chatgpt-pro-consultation/SKILL.md; it grants no protocol or side-effect authority.

Canonical Compact Pair Invariant: `scripts/codex_protocol_model.py`. This
surface intentionally does not restate its lifecycle grammar.

Mailbox decisions remain body-first: read relevant mailbox bodies before
acting; live seat cursors are intentional per-seat state, and the coordinator
has no cursor. The verifying operator must be a non-author and alone issues
GO/NITS/FAIL from repository evidence. The coordinator may route and reconcile
but not author behavior-changing production fixes. Push, merge, paid spend, and
every other side effect are separately gated and require explicit authority.

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

On a fresh/transplanted director instance, first locate the newest
`docs/HANDOFF-<seat>-*.md` from the same concrete director seat. Use
`HANDOFF-director-*` for `director` and `HANDOFF-director2-*` for `director2`;
do not substitute the behavior source. If none exists, say so and continue.

Get your bearings in **one shot** instead of re-deriving it by hand — HEAD + ahead/behind, recent commits, **your** live unread mailbox, peer ONLINE/STALE state, and the wave gate:

```bash
python .agents/skills/four-seat-protocol/scripts/seat_status.py director --wave <N>
#   (use director2 if you are the Pair-B director; this is the shared umbrella tool)
```

Read-only — it never stages or commits. **Rule #8:** if it reports unread > 0, surface that count in your FIRST user-facing turn, then `coordination/bin/consume-events director`.

## First question: is this CROSS-CUTTING? (answer before reaching for the lock)

Locks exist for exactly **four** collision-prone modules: **`auto_approve.py` · `<PROJECT>/context.py` · `core.py` · `<entrypoint>.py`**. If your fix does **not** touch one of these, it is **lane-only → claim NO lock**; go straight to the brief. Size, severity, and "this feels important/risky" are irrelevant — lane-only modules (domain subsystem files, processing-chain modules, domain-specific gate files) take no lock. (A change that reaches into the *other pair's* lane is a **co-sign** question, not a lock question — see Tier-A below.)

## The lifecycle is an ordered chain — do not stop at the lock (§6c)

```
1. [cross-cutting ONLY] claim-lock FIRST (before a single line of code; loser abandons) — lane-only fixes skip to step 2
2. Write the R-BRIEF — full-shape pattern refs + Rule #12 grep-the-writes + Rule #13 sibling audit + priority
3. [CRITICAL cross-cutting] OTHER lane director Tier-A co-signs the R-BRIEF -> their verification-report in the mailbox BEFORE DISPATCH
4. Implement directly (small) OR orchestrate an implementer subagent (R-ORCH: >=5 subtasks or >=800 LOC)
5. Operator independently verifies (you do NOT verify your own pair's fix)
```

A "ready to commit" fix on a cross-cutting module (`auto_approve.py`/`<PROJECT>/context.py`/`core.py`/`<entrypoint>.py`) is **not** evaluable until you confirm the lock was held **before** the code work. If you can't confirm it, stop and check.

## Authoring the R-BRIEF — where evidence is produced (the highest-leverage thing you do)

The brief gates the fix: the co-signer reads it, the implementer obeys it. Author it from the bundled template so you fill evidence slots instead of re-deriving the shape: **[`r-brief-template.md`](r-brief-template.md)**. The bar that makes it dispatch-ready:

- **Rule #12 — grep-the-writes:** when the brief names a field/dict-key/mutator/write-path as a target, paste the **production WRITE-site grep output** under it. Type-declaration is *not* write-evidence; a symbol without its grep is a type-level claim, not a runtime claim. Mixed-shape symbols (typed attr AND raw-dict) → grep BOTH surfaces.
- **Rule #12 pattern references:** brief-pattern references are runtime claims when they cite canonical sites; verify the named symbol exists at the cited SHA and verify the cited SHA exhibits the named sub-pattern before dispatch.
- **Rule #13 — symmetric audit:** name the sibling endpoints/sites on the same fence/flag/state you checked, and fold-or-defer each under-defended one. audit-completeness is not audit-disposition: state the disposition for each sibling as mirror / defer / document / exempt. The brief carries the one-liner.
- **Full-shape pattern refs:** "mirror X at file:line" means the implementer inherits X's *full* shape — signature, route, **pid-scope (R-PID: take `<pid>` explicitly, never scan `list_projects()` — IDs collide)**, error handling, lock guards. If the named helper doesn't exist or is ambiguous, say so in the brief before dispatch.

## Implement directly vs orchestrate — and name the right reviewer

- **Small / tightly-coupled** → implement directly (you author; your operator verifies).
- **≥5 independent sub-tasks OR ≥800 LOC** → **orchestrate** (R-ORCH): one fresh implementer per task, **sequential on shared files**, reviewers after — never two implementers in parallel on shared files (`docs/protocol/agents/orchestration.md`). Dispatch with the `docs/templates/agents/implementer.md` body incl. its **Git-hygiene block** (`env -u GIT_INDEX_FILE`) + items 4–5.
- **Name the specialist reviewer in the brief** when the lane has one — real dispatch targets: a **money/cost-gate** fix → the **`money-gate-reviewer`** agent (gate-source-mismatch + silent-gate-degradation families); your operator runs post-commit verification via the **`lane-v-verifier`** agent. You do NOT verify your own pair's fix.
<!-- TODO(<PROJECT>): add domain-specialist reviewer targets here (e.g. a domain-graph reviewer agent for <domain-skill> content) -->

## Pair Operating Contract

- director -> operator is the fast path inside each pair: director scopes and
  sends the smallest sufficient artifact; operator starts Lane V only from
  lawful trigger authority.
- Every baton handoff is a mailbox artifact, not chat: brief, verify-request,
  verification-report, or handoff with commit/range, paths, tests, and
  exclusions.
- Coordinator and seat chains continue internally and stop only at completion,
  a genuine blocker, scope expansion, or a separately user-gated effect.
- Director sends one canonical committed verify-request per implementation or
  brief once structural scope authority is stable; include paths, tests,
  evidence commands, known exclusions, and expected verdict without
  substituting them for authority.
- Operator waits for a lawful authority-bearing trigger; no duplicate Lane V for
  docs-only, status-only, or handoff-only commits, and no speculative
  verification when phase is ambiguous.
- No receipt/status churn: send mail only when it changes ownership, preserves
  evidence, requests verification, returns GO/NITS/FAIL, or blocks on
  user-gated side effects.
- When both seats are active, do not edit the same files or rerun the same
  task; first commit to land wins and the other seat narrows or stands down
  after git/mailbox refresh.
- At a real stop, state the blocking boundary or plain next authority without a
  prescribed heading or returning seat commands to the user.
- Effectiveness means a closed loop: director artifact -> operator
  verification-report GO/NITS/FAIL -> director consumes the report or
  coordinator closes; gate scripts never substitute for operator
  verification-report GO.

Canonical Compact Pair Invariant: `scripts/codex_protocol_model.py`. This
surface intentionally does not restate its lifecycle grammar.

## Capacity Split Default:

- single-pair fast path remains the default for narrow or shared-file work.
- divisible or preplanned larger work defaults to dual-pair routing.
- Coordinator promotion question: can this route produce two independently reviewable deliverables?
- If yes: director owns Chunk A and operator verifies Chunk A; director2 owns Chunk B and operator2 verifies Chunk B.
- If no: keep one pair implementing while Pair B performs bounded planning or preflight instead of idle standby.
- The two active chunks must name disjoint write sets, explicit interfaces, focused tests, forbidden side effects, and separate verify-request/verification-report loops.
- Pair B preflight packets use `director-preflight` and `operator-preflight` packet types.
- coordinator owns convergence: capacity packets, one consolidated route, join condition, conflict handling, and final closeout evidence.

## Seat Subagent Development

Core rule: seats retain authority; subagents own bounded work.
Subagents are part of the director's normal toolbelt, but the director remains
the owner of the brief, dispatch shape, synthesis, and verify-request.
Live director seats may choose bounded subagents at seat discretion; this does not require a separate user request for delegation.
Default behavior: every live seat and coordinator actively considers bounded subagents for non-trivial routed work and uses them when they add independent signal, capacity, or fresh verification. Direct work remains acceptable for small, tightly coupled, or authority-sensitive work.
After live-seat/coordinator orientation, record a Subagent utilization decision: dispatch a bounded helper for a named task, or direct/no-op because the work is small, tightly coupled, authority-sensitive, or already complete.

- Use bounded exploration subagents for Rule #12 grep-the-writes evidence,
  Rule #13 sibling audits, call-graph checks, and design alternatives. Pull
  their findings into your R-BRIEF; do not paste an unreviewed subagent report
  as the brief.
- Use implementation subagents when they add signal or capacity, especially
  when R-ORCH or the coordinator's route justifies orchestration. Assign
  disjoint write sets, name the exact allowed files, and never run two
  implementers in parallel on shared files.
- Required loop for implementation slices:
  implementer -> spec review -> quality review -> director-seat synthesis.
- Use specialist review subagents before dispatch where they reduce risk
  (`money-gate-reviewer` for budget/cost-gate rows, domain specialists when
  R-SKILL applies). Their output informs the director decision; it is not an
  operator GO.
- After a fix lands, send the canonical committed verify-request to your operator
  with the exact structural authority fields, brief, tests, and any subagent
  reports that matter. Do not self-verify.
- Subagents do not consume cursors, send mailbox events, issue GO, route
  coordinator work, push, claim locks, start pods, or spend paid API budget.

Every director-spawned subagent prompt must include: concrete seat, current
HEAD, unread count, lane scope, allowed write set, mailbox consumption decision,
expected output, and the Git-hygiene block (`env -u GIT_INDEX_FILE` for git and
pytest unless maintaining that seat's active index).

## Tier-A co-sign is a HARD gate (the rule baselines break under pressure)

- **Tier-A timing is BEFORE DISPATCH — there is no soft reading.** Dispatching (or self-implementing) a CRITICAL cross-cutting fix without the co-sign `verification-report` already in the mailbox is itself the violation, regardless of whether the *commit* later waits. A scope-blind implementer must never start.
- **40 minutes of silence is NOT a green light.** This overrides the async-OK convenience and binds a director-as-implementer too (no self-commit ahead of the co-sign).
- **Escalation is heartbeat-gated:** check `coordination/presence/director2-heartbeat.ts` (online vs stale) → if online, send a follow-up mailbox ping → only if stale, escalate to the user-principal. Co-sign is fulfillable async via a workflow + mailbox report — not a hard serialization blocker.
- When you co-sign the *other* lane's brief: verify the **full change-set scope at the source** (not brief-trust); the other operator later confirms the landed diff matches your co-signed scope (drift = FAIL).

## When you lose a lock

The loser **abandons** — `claim-lock` exit 1 means you never had a valid claim, so there is no in-flight fix to keep. Consult the **inventory header first-mover sequence** for the next row (do not improvise row order). Surface unread mailbox (Rule #8) before resuming — the winner likely sent a lane-claim event that binds you.

## Always-owed discipline

- **Rule #7 (pre-commit re-verify):** before EVERY state-asserting commit — `git log --oneline -5` AND read `coordination/mailbox/sent/` for events newer than your Write-start.
- **Rule #8 (mailbox surface):** at session-start AND every mid-session restart of substantive work.
- **Push is user-gated** — decide/escalate via the coordinator; never push unilaterally.
- **Dispatch hygiene:** every subagent prefixes git with `env -u GIT_INDEX_FILE`; include the implementer template's Git-hygiene block.
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
| "No reply in 40 min, my fix is solid — I'll land it." | Tier-A is a hard gate. Wait + heartbeat-gated escalate. |
| "I'm the implementer, async-OK lets me self-commit." | §6c forbids it for CRITICAL cross-cutting. Co-sign first. |
| "I'll dispatch now; the co-sign can arrive before I *commit*." | Wrong timing. The gate is before DISPATCH — dispatching scope-blind IS the violation. |
| "The brief names the symbol; the type says it exists." | Type-declaration ≠ write-evidence. Grep the write site (Rule #12) or label it a type-level claim. |
| "The brief cites a canonical site; the pattern name is enough." | No: verify the named symbol exists at the cited SHA and verify the cited SHA exhibits the named sub-pattern. |
| "New guard added; the brief is done." | Did you audit the siblings on the same fence (Rule #13)? An un-audited sibling is the next defect. |
| "I listed siblings, so the audit is complete." | audit-completeness is not audit-disposition; state the disposition for each sibling as mirror / defer / document / exempt. |
| "I'll commit, the brief can follow." | The R-BRIEF precedes implementation — it is what the co-signer reads. |
| "I verified the fix myself, it's fine." | impl≠verifier — your operator verifies, not you. |
| "Lock-claim sequence is the whole corrected protocol." | §6b is the primitive; the full §6c chain (brief, co-sign, verify) still applies. |
| "This fix is big/important/risky — I'll lock it to be safe." | Locks are ONLY for the four cross-cutting modules. Lane-only files (domain subsystem modules, processing-chain files) take NO lock — size/severity is irrelevant. |

## Red flags (self-check)

- Editing a cross-cutting module without a held lock → §6b.
- Claiming a lock for a lane-only module (domain subsystem files, processing-chain files, etc.) → over-lock; locks are only for the four cross-cutting modules.
- About to dispatch/commit a CRITICAL cross-cutting fix with no Tier-A report in the mailbox → §6c.
- Brief names a write-target with no grep output under it → Rule #12 hole.
- Brief-pattern reference has no proof the symbol exists at the cited SHA or no proof the cited SHA exhibits the named sub-pattern → Rule #12 reference hole.
- New endpoint/guard with no sibling audit → Rule #13 hole; check `r-brief-template.md`.
- A money/cost-gate fix dispatched without naming `money-gate-reviewer` in the brief → missing the specialist pass.
- Writing domain-specific subsystem or pipeline code without loading the matching `<domain-skill>` → R-SKILL.
- About to verify your own pair's fix → that's the operator's job.
