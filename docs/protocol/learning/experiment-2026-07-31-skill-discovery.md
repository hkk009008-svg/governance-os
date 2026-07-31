# Experiment record — Claude skill-discovery via reference stub (2026-07-31)

Decides plan §5 Stage 3 (`docs/superpowers/plans/2026-07-30-learning-plane-plan.md`):
whether `.claude` skills can be reference stubs over canonical `.agents`
bodies, or whether a manifest + materializer must be built. Recorded here so
the result is a durable artifact, not a session-private claim (round-one
review finding).

## Method

1. `.claude/skills/create-regression-pin/SKILL.md` (sha256
   `897530ae6cdd50499559f82821bf0eca0b376f22cc3ab8d5265aa3f151c45cb9`) was
   backed up and temporarily replaced in the worktree — uncommitted — by the
   stub below, preserving the frontmatter surface (name, description,
   `disable-model-invocation`) so discovery metadata was equivalent.
2. A reduced-context, read-only agent (Claude, Explore profile) was given
   ONLY the worktree path and a natural scenario — "an agent-confirmed
   defect will not be fixed this session; determine what this repository's
   own doctrine requires" — with no mention of the stub, the experiment, the
   skill name, or the `.agents` tree.
3. The original file was restored and verified byte-identical (same sha256
   before and after; independently corroborated in round-one review by
   `git show` at both range endpoints).

### The stub (exact body used)

    ---
    name: create-regression-pin
    description: Author a strict-xfail regression pin for a confirmed-but-deferred defect (R-VERIFY-TIER B), with the three recurring traps — assertion-shape, lock-column, non-vacuous flip — as built-in checks. Use when an agent-confirmed code defect is being left unfixed this session.
    disable-model-invocation: true
    ---

    # Create a Regression Pin (strict-xfail)

    The canonical body of this skill is `.agents/skills/create-regression-pin/SKILL.md`
    (repo-relative). Read that file now and follow it exactly as if its content
    were written here.

    Claude-native deltas when executing it: prefix git and pytest with
    `env -u GIT_INDEX_FILE`, and invoke Python as `.venv/bin/python`.

## Result

The probe agent reported its read order and derived procedure. The
load-bearing observations, from its report:

- Read #1–2: `CLAUDE.md` then `AGENTS.md` — routed by the doctrine line
  "`create-regression-pin` before deferring a confirmed defect."
- Read #3: `.claude/skills/create-regression-pin/SKILL.md`, which the agent
  itself described as "a pointer, not the body."
- Read #4: `.agents/skills/create-regression-pin/SKILL.md` — followed the
  reference unprompted.
- Its reported procedure composed content that exists ONLY in the canonical
  `.agents` body (all three traps, the `--runxfail` non-vacuity proof, the
  `test-infeasible` fallback) with the deltas that exist ONLY in the stub
  (`env -u GIT_INDEX_FILE`, `.venv/bin/python`) — the exact composition
  reference stubs depend on.
- Unprompted incidental finding, real on spot-check: the skill's step 6
  (seat updates the inventory row) conflicts with `wave-gate`'s
  coordinator-owned-inventory rule on an inventory with zero data rows.
  Queued for Stage 3a adjudication.

## What this does and does not establish

- ESTABLISHED: doctrine-routed discovery reaches the `.claude` stub, and a
  fresh reader follows the reference to the canonical body and composes both
  correctly. Frontmatter equivalence is structural (the stub keeps the
  discovery surface byte-comparable fields).
- NOT ESTABLISHED: a top-level harness session's native skill listing was
  not re-launched for this probe. The plan's criterion "the harness
  discovers and follows it" is therefore met only at the
  doctrine-routing layer.
- CONSEQUENCE, with its falsifier: Stage 3 proceeds as reference stubs (no
  manifest, no materializer). The residual harness-listing risk is carried
  as an explicit revert trigger: if a live session, routed to a stubbed
  skill, fails to reach the canonical body, that failure reverts the
  stub decision and reopens plan §5 Stage 3b/3c. The Stage 3 stub landing
  itself is the live re-test.
