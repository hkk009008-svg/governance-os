# PROGRAM MANUAL - Governance OS

**Canonical expression of the user-principal's intent for Pipeline.**

Pipeline is the governance kernel. Its job is to make bounded AI coding work
durable, verifiable, and gated by explicit authority. It does that with one CLI
entry point, append-only mailbox events, two review positions, review depth
proportional to risk, and one-shot invocation of the other CLI with a receipt.

evidence-ledger is the bound product target for current ledger-routed work.
Pipeline should help work reach that target only through an explicit per-task
binding; it must not blur product truth into governance-kernel truth.

## 1. What We Build

We build an executable governance OS for AI-assisted software work, and it is
CLI-exclusive: exactly two participants, the `claude` CLI and the `codex` CLI.
Every path is a terminal path — no desktop app, no MCP server, no persistent
agent peer, no browser. A procedure that cannot be typed at a terminal is not
part of this system.

The system turns user intent into durable artifacts: committed mailbox events,
verify-requests, verification-reports, peer receipts, and gate evidence.

The output the user receives is not prose. It is a repository state that can be
audited by git, tests, committed event bodies, and the checks behind
`bin/pipeline check`.

## 2. Product Goals And Non-Goals

Goals:
- Keep Pipeline the authoritative governance kernel for both CLIs.
- Keep one front door. `bin/pipeline <verb>` clears `GIT_INDEX_FILE`, resolves
  the repository interpreter (including from a linked worktree), and
  dispatches; `bin/pipeline --help` is the list of what exists.
- Make review depth follow the actual risk of the actual diff, and keep the
  request/report binding executable rather than conventional.
- Preserve separately authorized side effects: merge, lock, cursor
  consumption, peer invocation, paid spend, live-data mutation.
- Prefer executable proof over status theater.
- Keep product-specific truth in the target product repo.

Non-goals:
- Pipeline is not the private evidence-ledger application.
- Pipeline does not silently publish, merge, refresh a target checkout, launch
  a provider, or spend money.
- An advisory opinion — a subagent, the AGY backend, a peer receipt — never
  replaces a reviewer's `GO` / `NITS` / `FAIL`.
- A green check proves only its own call path, and grants no authority.

## 3. How The Machine Interconnects

A task names an outcome and, when governed work is involved, one of two
positions: `author` (owns the accepted outcome and its implementation range)
or `reviewer` (independently reviews a foreign-authored exact range). Those are
the only two identities a new mailbox event may carry. The six pre-collapse
seat names still parse so committed history stays readable; they are
compatibility identities, not positions anyone occupies.

One compact snapshot (`bin/pipeline status snapshot <role>`) reads current Git,
mailbox, and gate state before a protocol decision. `pipeline/ledger_start_guard.py`
additionally enforces the Pipeline-first boundary for ledger-routed work.

Mailbox events in `coordination/mailbox/sent/` preserve task communication and
create no external-effect authority. Transient cross-CLI conversation is not a
mailbox event at all: `pipeline peer ask <claude|codex|agy>` runs the other CLI
once as a child process and writes a receipt under `coordination/peer/`. The
exit code is the delivery acknowledgement. A receipt is evidence, not
attestation, and no verdict path accepts one.

A formal review loop closes only when the triggered risk profile is satisfied
by an exact-range verification report bound to the committed request.

## 4. Operational Contract

Required inputs:
- A user or parent prompt naming the requested outcome; a protocol role is
  needed only for governed work.
- A current Pipeline checkout, or a native Git worktree of one.
- The accepted task record when governed work is active.

Successful run output:
- For implementation: the requested scoped change and fresh sufficient
  verification. Commit and publication remain separate actions.
- For review: a `GO` / `NITS` / `FAIL` verification-report with command
  evidence, bound to the exact committed range.
- For coordination: an event only when ownership, evidence, or a hard boundary
  materially changes; no no-op artifact is required.

Canonical Compact Pair Invariant: `pipeline/codex_protocol_model.py`. This
manual intentionally does not restate its lifecycle grammar.

Known failure modes:
- Stale prose is trusted over newer mailbox and git evidence. Fix by rereading
  current event bodies, recent commits, and later reports before acting.
- Unknown broadcast receipt is treated as delivery. Fix by treating unknown as
  unproved until identity-specific evidence exists.
- A normal target checkout is treated as the base. Fix by following the task's
  named base or worktree first.
- A documented command is trusted without running it. Fix by running it; a doc
  that names a verb `bin/pipeline --help` does not list is a defect.

## 5. Capability-Maximization Playbook

Use the smallest sufficient task record. Governed work names the outcome,
owner, target, evidence bar, hard boundaries, reviewer when required, and any
separately authorized external effect.

Use subagents when they add independent signal or capacity, but keep authority
in the live role. Subagents do not consume cursors, issue verdicts, invoke a
peer, claim locks, merge, or spend.

Use tests and checks as the evidence layer. New behavior belongs behind a
focused regression test before implementation. Gate numbers belong in committed
command output, not in memory.

## 6. Operating Guidance For Roles

An author scopes and implements only inside the accepted range, then publishes
one committed verify-request once its structural authority fields are ready.

A reviewer verifies only from a lawful committed trigger and returns
`GO` / `NITS` / `FAIL`. Review depth follows actual behavior and risk;
documentation and status paths are not automatically exempt when they change
authority or operation. An author cannot approve authored work, and reviewer
independence is validated at publication by `pipeline/compact_pair_loop.py`.

Work continues internally and stops only at completion, a genuine blocker,
scope expansion, or a separately user-gated effect. At a real stop, state the
blocking boundary or the plain next authority needed.
