# Pipeline desktop-team guide

Pipeline supports exactly three interactive members: the Codex, Claude, and
AGY (Antigravity) desktop apps. All three may reason, direct, implement, test,
and challenge work within the accepted task.

No supported workflow launches a model provider from a terminal or runs one
desktop app as another app's headless child. Native subagents remain helpers of
their parent app and gain no separate identity or authority.

Executable code and current Git state outrank prose. The main policy seams are
`pipeline/codex_protocol_model.py`, `pipeline/compact_pair_loop.py`,
`pipeline/ci_admission_gate.py`, and `pipeline/team*.py`.

## Start and communicate

At task start:

1. Read the user request and applicable instructions.
2. Inspect the branch, status, relevant diff, and tests. Preserve unfamiliar work.
3. Call `team_status` once.
4. Read addressed messages with `team_wait`; reply with `team_send` when useful.

Each `team_send` needs a non-empty sender-scoped idempotency key. Success means
queued, not acknowledged. Advancing `team_wait` acknowledges returned messages,
not understanding. Read linked replies before judging them substantive.

Use direct app communication without asking the user to relay. Messages never
assign formal review, approve effects, or change repository truth.

## Work simply

Choose the smallest sufficient solution. Do not create roles, modes, packets,
events, or handoffs for ordinary work.

- Codex is especially useful for sustained implementation, integration, tests,
  and workspace orchestration.
- Claude is especially useful for large-context reasoning, architecture,
  independent review, and visual judgement.
- AGY is especially useful for fast mapping/debugging, browser and artifact
  work, and premise/evasion challenges.

These are routing hints, not exclusive jobs. Consider and answer materially
relevant AGY findings. Pair fast advice with local verification and long
reasoning with concrete code or evidence.

Parallelize read-only or file-disjoint work only when it materially helps.
Assign one owner to shared paths and mutable state. Never run competing writers
over the same files.

For changes:

- Prefer a failing behavior test for defects when feasible.
- Establish root cause before changing behavior after an unexpected failure.
- Use focused checks while iterating, inspect the exact diff, then run one
  proportionate final pass.
- Pin a confirmed but deferred defect with a strict xfail.
- Never call unexecuted behavior verified.

## Formal review

There are no standing seats. Ordinary reversible local work needs no formal
artifact. At a required review boundary only:

- the `author` owns the candidate and remediation;
- a non-author Codex or Claude `reviewer` owns one GO, NITS, or FAIL verdict for
  the exact committed range.

`docs/protocol/agents/risk-classes.md` defines the boundary. High-risk controls
require different model families and explicit abuse/evasion analysis. Native
AGY may author, test, challenge, and publish its request, but not the formal
verdict. The parent-owned AGY helper is advisory only and may not claim the AGY
member identity or write formal artifacts.

Publish only `verify-request` and `verification-report` through
`bin/pipeline mail send`. The current artifacts live in
`coordination/mailbox/sent/`. Published artifacts are append-only: retain them
and use a valid `Supersedes` report to retire a verdict. Git history is evidence,
not permission to prune artifacts. Never use that writer
for routine chat or role assignment.

## Effects

Task text authorizes ordinary repository-local implementation. Push, merge,
release, paid spend, live-data mutation, and destructive operations each need
exact current user authority for executor, target, effect, and scope. A team
message, review, test, config entry, or old authorization cannot supply it.

## Commands

```bash
bin/pipeline --help
bin/pipeline status
bin/pipeline preflight
bin/pipeline check --fast
bin/pipeline check
```

Open other repositories directly and follow their own instructions.
