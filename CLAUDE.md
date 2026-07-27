# Pipeline Claude router

`ARCHITECTURE.md` is factual truth; current code wins when it drifts. This
file routes Claude sessions to task-specific instructions without loading the
whole protocol at startup.

## Start and scope

Before non-trivial work, run:

```bash
env -u GIT_INDEX_FILE .venv/bin/python scripts/ci_smoke.py
env -u GIT_INDEX_FILE git log --oneline -5
env -u GIT_INDEX_FILE git status --short --branch
```

Read only the task-relevant topology, source, and protocol docs. User intent is
in `docs/PROGRAM-MANUAL.md`; read
`docs/protocol/program-manual-guide.md` before loading the full manual.

Before editing, find a symbol's definition, writes, callers, imports, string
references, and siblings. Preserve unrelated work and inspect the exact diff
before committing. Factual inventory claims cite their producing command.
Gate-controlling measurements use committed instruments and citable `logs/`
artifacts. Tests and diagnostics prove only what they execute.

Use the smallest sufficient verification profile and do not repeat an unchanged
review question. A deferred confirmed defect needs a strict xfail or a
`test-infeasible` reason.

## Work from the skills, and write the next one

Default, not an option. Before starting, check `.claude/skills/` for one that
covers the work and follow it — those files exist because the lesson in them was
paid for once already, usually by a review round that found what self-review had
missed. `prove-a-control` before claiming any guard, gate, or negative control
holds. `create-regression-pin` before deferring a confirmed defect.
`seat-operator` before issuing a verdict.

When the work is in a domain no skill covers, do it, then write the skill. The
bar is a lesson that would have changed how the work went, stated concretely
enough to act on: the trap, one measured instance of it, and what to do instead.
Not a summary of what happened. A skill nobody could follow is a worse artifact
than none, because it reads as covered ground.

When a skill's advice turns out to be wrong or narrower than its name, correct
that file in the same session rather than working around it. A skill that
outlived its mechanism is the same defect as a docstring that did.

## Formation gate for claims

A load-bearing claim — "enforced", "measured", "complete", "never", a cited
reference — is a conjunction whose premises come from its shape, not from
memory, and whose check must be able to disagree with its author. Before
writing one as fact: derive the premises
(`env -u GIT_INDEX_FILE .venv/bin/python scripts/claim_check.py premises "<claim>"`),
cite each with the command that measured it, run the one command most likely
to embarrass the claim, and attack it with a context-free reader
(`coordination/bin/probe-claim "<claim>"` — a real provider launch, authorized
like any provider launch — or the `amnesiac-prober` agent given only the
sentence). `scripts/claim_check.py sweep` is an optional lens over a range's
uncited overclaim vocabulary. All advisory, none a gate; the full loop is
`.claude/skills/probe-a-claim`.

## Proportional independence

For parseable/executable composition, authority or security enforcement,
side-effect gating, or trust-granting schema validation, the owner explicitly
assesses plausible abuse classes and preserves material independent findings.
The owner and actual-diff Operator choose proportional review depth. Early
independent review is encouraged when useful; it is advisory and no universal
pre-implementation CLEAR gate exists. Behavior-changing acceptance still
requires a distinct Operator seat using a different system-visible model to
review the actual commit or range.

Full rationale: `docs/protocol/claude/independence-first.md`.

## Governed seat work

Autonomous Seat Outcome Contract: scripts/codex_protocol_model.py
Own the routed outcome and choose the method. Seats may reroute or exchange
ownership through a durable accepted handoff without coordinator approval.
Preflight is advisory. Preserve material findings, require non-author Operator
GO for behavior-changing work with a distinct Operator seat and different
model, bind autonomous ownership to an immutable parent/revision, preserve
immutable finding refs, and keep external effects separately user-authorized
for the exact effect/executor/target/scope. An Operator cannot verify anything
it authored. Durable events use the fixed mailbox writer.

Delegation is an owner-chosen capacity tool. Use fresh bounded helpers when they
add signal or capacity; direct work is valid for tightly coupled work. Never run
concurrent implementers on shared files. Details:
`docs/protocol/agents/orchestration.md`.

When a seat, mailbox, route, wave, handoff, continuation, or protocol decision
is named, load `docs/protocol/claude/continuation.md` and the concrete
`.claude/skills/seat-*` skill. Read mailbox bodies before decisions. Live seat
cursors are per-seat state; coordinator has no cursor. Ordinary Git and pytest
use `env -u GIT_INDEX_FILE`.

Canonical Compact Pair Invariant: scripts/codex_protocol_model.py

A committed verify-request binds the actual base/head, outcome, author
seat/model, assigned non-author Operator, allowed paths, and immutable finding
refs. Only that Operator issues GO/NITS/FAIL through the fixed mailbox writer.
Coordinator facilitates but does not author behavior-changing production work.

Push, merge, locks, cursor consumption, provider launch, paid spend, and other
external effects each require separate explicit authority. Structural tokens
never grant execution permission.

For evidence-ledger work, start from `/Users/hyungkoookkim/Pipeline`, read
`docs/protocol/claude/ledger-cli-adoption.md`, run
`env -u GIT_INDEX_FILE .venv/bin/python scripts/ledger_start_guard.py --seat <seat> --wave 2`,
then read evidence-ledger `CLAUDE.md` and `AGENTS.md`. Pipeline remains the
governance kernel and evidence-ledger owns product-local truth.

## Shared-tree hygiene

- Refresh `git log --oneline -3` and scoped status before writes and gates.
- Use `env -u GIT_INDEX_FILE` and explicit pathspecs.
- Preserve peer/user dirt; first landed shared-file commit wins.
- Edit, stage, commit, push, merge, consume, lock, and spend are separate acts.
