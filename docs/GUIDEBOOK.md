# Pipeline guidebook

This is the practical guide for using Codex, Claude, and AGY as one desktop-app
engineering team. The short rule is: communicate directly, use the best
available strength, keep repository work simple, and add formal governance only
where actual risk requires it.

## Meet the team

Every member may reason, direct, implement, test, and challenge. Capability
labels help routing; they do not reserve work.

| Member | Strong starting point | Compensating practice |
|---|---|---|
| Codex | workspace integration, worktrees, parallel orchestration, sustained execution | refresh exact task/diff after parallel branches; seek another family for high-risk review |
| Claude | large-context synthesis, architecture, independent diff and visual review | turn analysis into a bounded change and executable evidence before expanding scope |
| AGY | rapid mapping/debugging, browser and artifact work, premise/evasion attacks, multi-model advice | validate returned facts, commands, and diffs locally; do not treat advice as formal acceptance |

AGY is an interactive team member, not a disposable helper. Hear and answer its
material findings. Its only governance limitation is that it cannot be the sole
independent formal verdict or authority source.

## Start a task

1. Read the user's current objective and constraints.
2. Inspect the repository branch, status, relevant diff, and tests.
3. Call `team_status` once.
4. Read pending addressed messages with `team_wait`.
5. Choose the smallest change or investigation that can settle the question.

Do not begin by allocating seats, publishing events, replaying old mail, or
writing a plan when the accepted task is already clear.

## Ask another member

Use `team_send` with one concrete request. A useful message includes:

- the objective;
- the paths, commit, output, or claim to inspect;
- the form of response needed;
- whether the requester can continue independently.

Use `recipient: all` only for information or a question that truly concerns all
members. Use `reply_to` for a response so acknowledgement and reply state remain easy
to inspect.

Remember the state ladder:

```text
queued != returned != acknowledged != replied != substantively answered
```

If the answer blocks work, wait with `team_wait` at a natural boundary. If it
does not, continue independent work and check later. Never treat a timeout or
activity timestamp as agreement, refusal, liveness, or authority.

## Split implementation

Split when the pieces are genuinely independent:

- read-only mapping of different subsystems;
- independent review or premise attacks;
- changes to nonoverlapping modules;
- platform-specific checks that produce comparable evidence.

Name one owner per path and one integrator. Do not assign concurrent writers to
the same file, database, lock, build output, or other mutable resource. When a
design choice affects several pieces, settle it before parallel writes.

Parallelism should remove elapsed time, not create reconciliation work. A
single direct implementation is preferable when it will finish faster and be
easier to verify.

## Build and test

For a behavior change, start with a failing behavior test when feasible. If it
is not feasible, retain a characterization or state why. After unexpected
failure, find root cause before modifying behavior.

Use focused checks while iterating. Inspect the exact diff. Run one final test
pass proportionate to the changed surface and report exactly what ran. A green
suite does not establish app liveness, message substance, provider identity,
or external authority.

## Review at the risk boundary

Ordinary local work needs no formal roles. For a material behavior change,
temporarily name the candidate owner `author` and a non-author Codex or Claude
member `reviewer` for the exact committed range. For a high-risk control, the
reviewer must also be from a different model family and assess plausible abuse
and evasion classes.

The reviewer reads the actual diff and relevant code, not only a summary. AGY
may challenge assumptions, run tests, or review evidence; material findings are
explicitly addressed. AGY cannot be the only formal GO/NITS/FAIL source. End
the author/reviewer responsibilities when the range is resolved.

## Perform an external effect

Push, merge, release, paid spend, live-data mutation, and destructive
operations are not implied by implementation authority. Before any one of
them, confirm the current task or user explicitly names:

- who will execute;
- the target;
- the effect;
- the allowed scope.

Ask if any field is missing. Team messages, config, tests, reports, and old
approvals do not fill it.

## Transfer or finish

Git, executed tests, and desktop task history are the normal continuation
record. For a real ownership transfer, interruption, compaction, or wrap where
someone else must resume, leave one concise checkpoint:

- objective and accepted scope;
- current owner;
- base/head and relevant paths;
- evidence and verification status;
- unresolved blockers;
- next executable action.

Do not create a checkpoint for every turn or maintain parallel handoff chains.
Legacy mailbox conversation, cursors, seats, capacity packets, and peer
receipts are historical evidence. Use the fixed mailbox writer only when a
risk-required formal review artifact, a real transfer/checkpoint `findings`
event, or the governed learning-candidate/disposition lifecycle must persist
beyond the app task; never for routine chat.

## When something goes wrong

- Team tools missing: confirm the app opened this repository; run
  `bin/pipeline preflight`.
- Wrong member label: repair its checked-in MCP config; do not override the
  label in a prompt or environment variable. The label is not attestation.
- AGY tool missing or repeatedly asks: reload the repository's `pipeline-team`
  workspace plugin, confirm its `plugin.json` manifest and `mcp_config.json`,
  and explicitly allow `mcp(pipeline-team/*)` in Antigravity.
- Message remains queued: the recipient has not received it through
  `team_wait`; continue independent work or wait.
- Advice conflicts with code: inspect current code and execute the deciding
  check. Repository truth outranks narration.
- Members disagree: compare premises and evidence against the user objective.
  Ask the user only when a real scope, product, or effect choice remains.
- Legacy artifacts disagree with current task: retain them as history and use
  current Git/task state and active doctrine.

No recovery path launches a headless model provider. Terminal commands remain
for reproducible repository work and preflight.
