---
name: antigravity-harness
description: Use this skill when operating as Antigravity within Pipeline. Defines readiness-bridge posture, explicit role adoption, parent-scoped native helpers, work-mode selection, claim formation discipline, and shared-tree staging hygiene.
---

# Antigravity protocol harness

This is the AGY-specific adapter to Pipeline's shared executable policy. A
repository-root AGY session starts as a readiness bridge. It adopts a live role
or coordinator posture only when the user explicitly assigns one.

## Operating posture

- **Readiness bridge by default.** Inspect only the evidence needed for the
  request. Do not claim a role or run a mandatory root-startup sequence.
- **Explicit roles only.** A concrete Director, Operator, or Coordinator
  assignment selects that role's shared skill and current status view. A label,
  prompt fragment, launcher, or helper definition grants no authority.
- **Parent-scoped helpers.** Native AGY helpers are not formal seats. They return
  bounded evidence to their parent and never issue a binding GO, NITS, or FAIL,
  publish mailbox events, consume cursors, or inherit authority.

## Operating Doctrine (Layer-2) Bindings & Native Mesh Rules

When performing substantive work, adhere to the unified operating doctrine bound to AGY primitives:

- **Evidence & Verification**: Follow R-EVIDENCE (cite exact command output), R-MEASURE (commit test instruments), and R-VERIFY-TIER (cap over-verification, strict xfail pins for deferred defects).
- **Subagent Model Tiering**: Current custom-agent tiers are `inherit`,
  `flash`, and `pro`. The tracked read-only advisors omit `model` and inherit
  the parent by default. A tier selects capacity, never seat standing or
  reviewer independence.
- **Native helpers (`define_subagent` / `invoke_subagent`)**: Delegate bounded
  local tasks when useful. Helper output returns to the parent; it is not a
  formal handoff, review verdict, seat claim, or durable protocol event.
- **Working notes**: Optional scratch notes under `.agents/<agent_folder>/`
  grant no authority and do not replace repository evidence or mailbox events.
- **Seating Doctrine & Non-Author Verification**:
  - **impl ≠ verifier**: Formal review uses the explicitly assigned non-author
    Operator and the committed Compact Pair. Helper analysis is advisory and
    cannot satisfy or author the formal verdict.
- **Event publication**: When separately authorized, assigned live roles use
  `coordination/bin/send-event`; helpers never publish. `scripts/agy_emit.py
  --dispatch` prints a routing hint only and does not execute or prove a
  dispatch.
- **Read-only observer**: `python scripts/agy_observer.py --snapshot` prints a
  labelled compact status snapshot before the labelled raw, unverified bus
  summary; it does not consume a cursor or grant authority.
- **Environment Isolation & Native Index**: Each seat gets an isolated process environment; `scripts/agy_seat_launcher.py` emits only `AGY_SEAT`, `AGY_AGENT_MODE`, `AGY_AGENT_ROLE`, and `AGY_BEHAVIOR_SOURCE`, preserves the explicit `AGY_API_KEY` credential, and drops inherited `GIT_*` plus other ambient `AGY_*` identity or project state rather than replacing it. Model discovery fails closed when `agy models` errors or returns no IDs. No seat binds a per-seat Git index: every worktree uses its native index and `index-<provider>-<seat>` is retired. Never hand-roll a `GIT_INDEX_FILE` export — it silently rebinds every later Git command in the session including commits, and follows `cd` into unrelated repositories. Prefix ordinary Git and pytest with `env -u GIT_INDEX_FILE`.
- **Background Tasks**: Use `schedule` and `manage_task` tools for background command and timer execution.
- **User Delegation**: Use `ask_question` rather than deciding policy or cross-cutting changes on your own.
- **Smoke Tests**: Run full `scripts/ci_smoke.py` when a change affects
  governance/runtime topology or relies on an `ARCHITECTURE.md` invariant.
- **Claim Formation**: Before writing a load-bearing claim ("enforced", "measured", "complete", "never", a cited reference), follow `.agents/skills/probe-a-claim/SKILL.md`. Before claiming a guard or gate holds, follow `.agents/skills/prove-a-control/SKILL.md`. Scale rigor to work mode: routine `explore` observations cite the command; `validate` applies the full formation loop.
- **Work Mode Selection**: Declare `explore`, `validate`, or `promote` per `docs/protocol/work-modes.md`. Mode controls iteration and record granularity; risk controls review depth. Mode grants no authority.

## Skill-First Work and Learning Candidates

Before starting, check `.agents/skills/` for a skill that covers the work and
follow it — those files exist because the lesson was paid for once already.
Current code and higher-priority instructions remain controlling. If a loaded
skill conflicts with either, stop relying on it and record the conflict in the
task evidence; do not silently work around it. Correct canonical skill bytes
only when the current accepted task authorizes that correction and its required
review completes.

Finish the scoped task before extracting a lesson. Then draft and, only with the
applicable publication authority, publish an evidence-backed
`learning-candidate` with truthful provider scope. There is no canonical skill
creation or edit solely because a lesson arose. Promotion into a canonical
skill is a separately accepted, risk-classed Compact Pair change; the candidate
is evidence for that later decision, not authority to make it.

## Shared-Tree Staging Hygiene

This repo has concurrent sessions across providers. Surgical, named-file
staging is mandatory:

- **Never `git add -A`, `git add .`, or `git add --all`.** Stage by explicit path: `git add path/to/file1 path/to/file2`.
- **Never force-push.** If a force-push is truly needed, obtain explicit user consent and prefer `--force-with-lease`.
- **Refresh before staging.** Run `git log --oneline -3` and scoped `git status` before writes and gate decisions.
- **Preserve peer work.** First landed shared-file commit wins; refresh and narrow rather than recreate.
- **Edit → stage → commit → push are separate acts.** Each requires its own decision.

## Model-Family Independence Constraint

All AGY seat profiles resolve to the `gemini` model family.
`codex_protocol_model.models_are_independent` compares families, not labels.
This means AGY **cannot satisfy `high-risk-control` review on its own** —
route those reviews to a seat on a different model family (Claude, GPT, etc.).
State the author/reviewer model as the exact ID from `agy models`, undecorated.

## Hard Boundaries & User Consent

- **User-Gated Side Effects**: Pushing to `main`, merging candidates, locking resources, or initiating paid spend MUST receive explicit user consent (`ask_question`).
- **No Self-Approval**: The author never issues the formal verdict for authored
  work. Native helper separation does not create reviewer independence or a
  formal seat.
