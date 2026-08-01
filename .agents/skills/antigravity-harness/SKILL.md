---
name: antigravity-harness
description: Use this skill when operating as Antigravity within Pipeline. Defines Layer-2 operating doctrine bindings, direct autonomous seating, native subagent mesh (define_subagent/invoke_subagent), structured artifact mesh conventions (implementation_plan.md, walkthrough.md), work-mode selection, claim formation discipline, and shared-tree staging hygiene.
---

# Antigravity Protocol Harness & Native Subagent Mesh

This skill is the Antigravity-specific runtime harness for Pipeline. AGY operates natively in direct autonomous posture, executing seated roles (`director`, `operator`, `coordinator`, `director2`, `operator2`) and leveraging native subagent orchestration and structured artifact mesh conventions.

## Operating Posture & Seating Roles

- **Direct Autonomous Mode (Default)**: AGY operates natively in direct autonomous mode by default. Seat launchers (`coordination/bin/agy-seat <seat>`) execute directly without requiring mandatory advisory posture flags.
- **Automated Session Entry Protocol (Mandatory First Turn)**: Upon initiating ANY new AGY chat session in Pipeline, AGY MUST automatically execute the complete 4-step initialization sequence on its very first turn before taking user directives:
  1. **Status Snapshot**: Run `python scripts/status.py snapshot coordinator` to inspect unhandled events & active work mode.
  2. **Git Hygiene Check**: Run `git status --short --branch` and `git log --oneline -5` to inspect worktree status & commit history.
  3. **Fast Preflight Smoke Check**: Run `python scripts/ci_smoke.py --fast` to verify governance invariants.
  4. **Register Seat Mesh**: Register `pipeline_director` and `pipeline_operator` using `define_subagent` so the 4-seat subagent mesh is 100% armed and ready.
- **Seated Role Occupancy**: AGY natively occupies Pipeline seats (`director`, `operator`, `coordinator`, `director2`, `operator2`) under unified operating doctrine.

## Operating Doctrine (Layer-2) Bindings & Native Mesh Rules

When performing substantive work, adhere to the unified operating doctrine bound to AGY primitives:

- **Evidence & Verification**: Follow R-EVIDENCE (cite exact command output), R-MEASURE (commit test instruments), and R-VERIFY-TIER (cap over-verification, strict xfail pins for deferred defects).
- **Subagent Model Tiering**: Select native subagent models based on task requirements:
  - `flash_lite`: Directory listing, `rg` searching, file reading, and log extraction (fastest).
  - `flash`: Multi-file research, codebase orientation, and doc inspection.
  - `pro` / `inherit`: Complex reasoning, heavy refactoring, and independent verifier analysis.
- **Native Subagent Mesh (`define_subagent` / `invoke_subagent`)**: Delegate sub-tasks dynamically using `define_subagent` and `invoke_subagent`. Avoid spinning external OS chat processes or polling disk mailbox files for internal task coordination.
- **Structured Artifact Mesh**:
  - **`implementation_plan.md`**: Formulate for multi-file/architectural initiatives (>50 lines or material ambiguity). Skip for routine single-file edits or minor fixes.
  - **`walkthrough.md`**: Formulate upon completion to summarize executed changes, test logs, and verification proof.
  - Save artifacts in designated working directories (`.agents/<agent_folder>/`). Legacy `brain/<conversation-id>/` paths are deprecated.
- **Seating Doctrine & Non-Author Verification**:
  - **impl ≠ verifier**: Candidate code authored by an implementer subagent/seat (`director`) MUST be verified by a distinct verifier subagent/seat (`operator`).
- **Programmatic Event Emission**: Use `scripts/agy_emit.py --to <seat> --kind <kind> --subject <subj> --body <body>` or `coordination/bin/send-event` to emit schema-compliant events programmatically when milestone records are required.
- **Environment Isolation & Native Index**: Each seat gets an isolated process environment; `scripts/agy_seat_launcher.py` emits only `AGY_SEAT`, `AGY_AGENT_MODE`, `AGY_AGENT_ROLE`, and `AGY_BEHAVIOR_SOURCE`, and drops inherited `GIT_*` authority rather than replacing it. No seat binds a per-seat Git index: every worktree uses its native index and `index-<provider>-<seat>` is retired. Never hand-roll a `GIT_INDEX_FILE` export — it silently rebinds every later Git command in the session including commits, and follows `cd` into unrelated repositories. Prefix ordinary Git and pytest with `env -u GIT_INDEX_FILE`.
- **Background Tasks**: Use `schedule` and `manage_task` tools for background command and timer execution.
- **User Delegation**: Use `ask_question` rather than deciding policy or cross-cutting changes on your own.
- **Smoke Tests**: Run `scripts/ci_smoke.py --fast` for session-start preflight verification; run full `scripts/ci_smoke.py` before final verification.
- **Claim Formation**: Before writing a load-bearing claim ("enforced", "measured", "complete", "never", a cited reference), follow `.agents/skills/probe-a-claim/SKILL.md`. Before claiming a guard or gate holds, follow `.agents/skills/prove-a-control/SKILL.md`. Scale rigor to work mode: routine `explore` observations cite the command; `validate` applies the full formation loop.
- **Work Mode Selection**: Declare `explore`, `validate`, or `promote` per `docs/protocol/work-modes.md`. Mode controls iteration and record granularity; risk controls review depth. Mode grants no authority.

## Skill-First Work

Before starting, check `.agents/skills/` for a skill that covers the work and
follow it — those files exist because the lesson was paid for once already.
When work exposes a lesson no skill covers — a trap, a measured instance, and
what to do instead — write the skill in the same session. When a skill's advice
turns out wrong or narrower than its name, correct the file rather than working
around it.

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
- **No Self-Approval**: Candidate code built by an implementer subagent/seat (`director`) MUST be verified by a distinct verifier subagent/seat (`operator`). Verifiers must strictly evaluate candidates using reproducible test runs and record actual terminal evidence in verification reports.
