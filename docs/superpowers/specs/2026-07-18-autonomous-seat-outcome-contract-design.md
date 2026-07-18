# Autonomous Seat Outcome Contract Design

**Date:** 2026-07-18

**Status:** User-approved design; implementation not yet authorized by this document

**Scope:** Pipeline four-seat ownership, routing, convergence, verification, and
protocol surfaces

## 1. Problem

The current four-seat process gives models responsibility for results while
prescribing too much of their reasoning and execution. Routes and plans can
require exact test names, enumerated cases, packet shapes, review sequences,
and coordinator-authored convergence before implementation begins. A preflight
review can therefore keep discovering new plan omissions even when an owning
seat could choose a sound implementation and an independent Operator could
verify the actual result.

The maintenance handoff chronology task demonstrates the failure mode. The
first Director2 preflight found real design contradictions. After correction,
the second preflight found two further acceptance-coverage gaps. Those findings
are useful, but the route makes a committed Director2 `CLEAR` a prerequisite,
so new design discovery prevents implementation and actual-diff verification.

The protocol should trust seats to choose the right path while retaining the
few boundaries that protect independence, durable truth, and external effects.

## 2. Design Principle

> Own the outcome, choose the method, show the evidence, obtain independent
> approval for consequential changes, and announce ownership changes before
> conflicting work begins.

Routes describe outcomes rather than implementation recipes. Models choose
their investigation, implementation, testing, collaboration, and review depth.
Protocol machinery makes ownership and evidence visible; it does not attempt to
encode good engineering judgment as an exhaustive checklist.

## 3. Hard Boundaries

Only these boundaries remain mandatory:

1. Durable repository and mailbox evidence outranks chat summaries and stale
   prose.
2. An author cannot approve its own behavior-changing work. A non-author
   Operator supplies the acceptance verdict for the actual committed change.
3. External or difficult-to-reverse effects require explicit user authority,
   an identified executor, a target, and authorized scope.
4. Known material evidence cannot be concealed or silently discarded.
5. A coordinator remains a facilitator and system-wide observer. It does not
   author behavior-changing production work unless the user explicitly assigns
   that model a director seat.

No other process step becomes a universal invariant merely because it appears
in a template, diagnostic, preflight, plan, or earlier route. A live outcome
contract remains binding until a durable ownership or transition event
supersedes it.

## 4. Outcome Contract

Each active task carries five binding facts:

1. **Outcome:** the observable result to achieve.
2. **Owner:** the seat or accepted collaborating seats currently responsible.
3. **Evidence bar:** what kind of evidence would credibly demonstrate the
   outcome, without prescribing exact commands or test names.
4. **Hard boundaries:** the applicable constraints from section 3 and any
   task-specific prohibition.
5. **External effect authority:** any separately authorized effect, or an
   explicit statement that none is authorized.

The owner may revise its working approach, tests, task decomposition, and
collaborators without rewriting the outcome contract. A material outcome or
hard-boundary change creates a new contract; an implementation decision does
not.

## 5. Autonomous Ownership

Seats may claim unowned work, split or merge tasks, transfer work, exchange
ownership, choose a verifier, or reroute work without coordinator approval.
These internal ownership changes require no separate user authorization and are
not treated as external effects.

Ownership uses a minimal durable handshake:

- The first durable claim owns unowned work.
- A transfer is effective when the receiving seat accepts it.
- An exchange is effective when all affected seats acknowledge the same
  exchange.
- The incumbent remains responsible until acceptance, so a proposal cannot
  orphan work or assign it to an unwilling seat.
- An ownership event identifies the task, prior owner, accepted new owner, and
  unchanged or revised outcome.

If an owner is inactive, another seat may take over after checking for fresh
work and active locks and durably recording the takeover assumption. No fixed
timeout is imposed; the claiming seat uses current evidence and judgment. If
overlapping claims appear, seats pause only the overlapping writes and resolve
ownership directly. Unrelated work continues.

The coordinator may observe, suggest, claim eligible non-production work, or
mediate a collision. It is not an approval gate for ordinary ownership changes.

## 6. Work States and Convergence

The operative states are intentionally small:

- **WORKING:** the owner can still make meaningful progress.
- **NEEDS_PEER:** help, review, or an ownership exchange would improve progress.
- **FINDING:** evidence of risk that the owner must consider; it does not
  automatically stop work.
- **BLOCKED:** no lawful path exists without new authority, unavailable
  external state, or resolution of a hard-boundary violation.
- **READY_FOR_REVIEW:** the owner presents a committed change and evidence to a
  chosen non-author Operator.
- **ACCEPTED:** a non-author Operator issues GO for the reviewed commit or
  range.

The normal cycle is:

1. A seat accepts an outcome.
2. It chooses how to investigate, implement, test, and collaborate.
3. Other seats may publish findings or propose ownership changes.
4. The owner decides how to address the evidence and remains accountable for
   the outcome.
5. The owner submits the actual committed change for independent review.
6. The Operator chooses sufficient verification and issues GO, NITS, FAIL, or
   unable-to-verify from repository evidence.
7. GO satisfies independent acceptance. Any subsequent external effect still
   uses its own authorization.

Plan completeness, a preflight `CLEAR`, a capacity-board result, or a green
diagnostic cannot substitute for actual-diff Operator GO.

## 7. Preflight and Review

Preflight is advisory. It discovers risks early and may influence ownership,
design, or tests, but it is not a mandatory implementation gate. A preflight
seat records material findings and distinguishes evidence from inference. The
owner decides whether to fix, counter, accept ordinary engineering risk, change
approach, or exchange ownership.

An Operator reviews the delivered outcome rather than compliance with a
prewritten reasoning script. `FAIL` is appropriate when the actual committed
change fails the outcome, lacks credible evidence, or violates a hard boundary.
Preference differences, missing preflight detail, or an alternative adequate
test strategy are not sufficient by themselves.

The author may revise the change, provide counter-evidence, narrow the outcome,
exchange ownership, or request another independent review. Any later reviewer
must receive the earlier material findings; changing reviewers cannot erase
evidence. Only a non-author GO accepts behavior-changing work.

## 8. Failure and Disagreement

A finding states the observed risk and likely impact without needing to
prescribe the repair. Seats resolve disagreement using whichever path best
advances the outcome:

- revise the change;
- supply counter-evidence;
- narrow or redefine the outcome;
- exchange ownership;
- request another independent review while preserving prior findings; or
- ask the user when a product decision, new external authority, or genuinely
  irreconcilable evidence requires it.

There is no fixed disagreement-cycle limit, mandatory coordinator escalation,
or automatic SLA. Seats keep working while a lawful path exists. They use
`BLOCKED` only when it does not.

Models may accept ordinary engineering risk with a stated rationale. They may
not conceal evidence, self-approve behavior-changing work, or broaden an
external-effect authorization.

## 9. Proportional Artifacts

Durable artifacts are created only when they change ownership, carry authority,
preserve a real transfer, record executed evidence, or state an actual blocker.

The minimum useful forms are:

- **Outcome assignment:** outcome, owner, evidence bar, hard boundaries.
- **Ownership change:** task identity, prior owner, accepted new owner, outcome
  disposition.
- **Verification request:** reviewed commit or range, outcome, author, chosen
  non-author verifier.
- **Verification report:** verdict, material evidence, actionable findings.
- **External-effect authorization:** effect, executor, target, authorized scope.

These are semantic contents, not rigid prose templates. Exact headings, field
order, repeated receipts, and prescribed test names are not authority.

## 10. Protocol Surface Consolidation

Policy will have one compact source. Other surfaces become thin adapters:

- `scripts/codex_protocol_model.py` owns hard invariants, work-state meanings,
  and the outcome-contract semantics.
- `AGENTS.md` decides when governed protocol applies and points to the compact
  source.
- `docs/protocol/codex/continuation.md` contains Codex commands and mechanics,
  without copied policy capsules.
- `.agents/skills/four-seat-protocol/SKILL.md` performs lightweight orientation.
- Concrete seat skills describe purpose, authority, and evidence expectations,
  not mandatory step-by-step behavior.
- The existing mailbox remains the durable communication channel. Ordinary
  ownership changes need no coordinator-authored route or capacity packet.

Capacity boards, protocol doctors, preflights, and wave gates become optional
observability and diagnostic tools. They may report facts and inconsistencies,
but they do not decide discretionary engineering choices or replace Operator
review.

Exact prompt-text synchronization, required test-function names, exhaustive
pre-implementation case lists, mandatory subagent decisions, coordinator-only
convergence, fixed SLAs, and duplicate policy capsules will be removed or
demoted. Unwired validators will not be retained merely because tests exist for
them.

## 11. External Effects

External effects remain separately authorized. The durable authorization needs
only:

- the effect;
- one executor;
- the target; and
- the authorized scope.

The executor chooses appropriate prechecks, stop conditions, and postchecks
using current evidence. It may recover from a failure within the authorized
scope, but it may not silently broaden the target, effect, spend, or authority.
Other seats observe and must not repeat the same effect unless ownership is
durably transferred.

## 12. Verification Strategy

Protocol tests protect semantic outcomes and authority boundaries rather than
exact wording or prescribed reasoning. They will prove that:

- an author cannot approve its own behavior-changing work;
- an external effect cannot proceed without explicit scope and one executor;
- seats can claim, transfer, exchange, split, and merge ownership without
  coordinator approval;
- an accepted transfer cannot assign work to an unwilling seat;
- a preflight finding remains visible without automatically blocking
  implementation;
- only actual-diff non-author GO satisfies independent verification;
- prior material findings remain visible to a later reviewer;
- legacy routes remain readable while newer autonomous ownership events can
  supersede them; and
- diagnostics report inconsistencies without controlling model judgment.

Tests should use semantic assertions against the compact model. They should not
require exact prompt copies, exact test names chosen by future seats, or dormant
machinery without a production consumer.

## 13. Compatibility and Migration

Migration is incremental and preserves durable history:

1. Commit the compact outcome-contract model and a compatibility
   interpretation for existing route and mailbox artifacts.
2. Update adapters, seat skills, diagnostics, and semantic tests together.
3. Publish a small transition event for the active maintenance task.
4. Preserve Director2's committed chronology findings but reclassify them from
   a mandatory preflight gate to advisory evidence.
5. Allow Director, or any accepted replacement owner, to implement immediately
   using its own approach.
6. Obtain non-author Operator verification of the actual committed change.
7. Resume the evidence ledger only after GO and the separately required resume
   authorization and live ledger guard.
8. After one successful autonomous cycle, remove remaining duplicated or
   obsolete protocol machinery exposed by that cycle.

Existing artifacts remain readable and are not rewritten retroactively. A new
ownership or transition event supersedes an older route only when it says so
durably. Until that transition is implemented, the currently committed route
and its Director2 `BLOCKED` prerequisite remain binding live state.

## 14. Current Maintenance Route Application

The two Director2 findings remain technically useful:

- fail-closed Git chronology behavior should cover both merge-base failure
  sites; and
- metadata parsing should detect header occurrences before validating their
  values so a valid header plus a blank or malformed sibling remains visible.

Under this design they are `FINDING` evidence, not proof that no lawful
implementation path exists. The Director may implement a robust solution,
counter with evidence, narrow the outcome, or exchange ownership. The chosen
Operator independently decides whether the delivered implementation and tests
satisfy the outcome.

The conditional ledger-resume gate becomes:

1. actual implementation commit;
2. non-author Operator GO on that commit or reviewed range;
3. live ledger guard; and
4. separate authorization for the resume effect when required.

Director2 preflight `CLEAR` and coordinator-authored convergence are not resume
prerequisites after the transition event takes effect.

## 15. Non-Goals

This design does not:

- remove independent verification;
- authorize push, merge, spend, lock, cursor, ledger, or other external effects;
- permit evidence suppression or self-approval;
- require a new task-board service, lease system, schema, or mailbox transport;
- prescribe the maintenance implementation; or
- rewrite historical mailbox and route artifacts.

## 16. Success Criteria

The design succeeds when:

- ordinary ownership changes do not wait for coordinator approval;
- seats can reroute and exchange work through a minimal accepted handshake;
- preflight `CLEAR` is not an implementation prerequisite;
- routes specify outcomes and evidence rather than implementation recipes;
- models choose sufficient methods, tests, and collaborators;
- findings remain visible without automatically becoming blockers;
- independent actual-diff approval and external-effect authority remain
  enforceable;
- protocol policy has one compact source instead of duplicated capsules; and
- the maintenance route progresses to implementation, Operator review, and the
  conditional ledger-resume decision.
