# Pipeline desktop-team guide

Pipeline supports exactly three interactive members: the Codex, Claude, and
AGY (Antigravity) desktop apps. All three may reason, direct, implement, test,
and challenge work within the accepted task. No workflow launches a model
provider from a terminal or runs one app as another app's child; native
subagents are helpers of their parent app with no separate identity.

Executable code and current Git state outrank prose. The policy seams are
`pipeline/codex_protocol_model.py`, `pipeline/compact_pair_loop.py`,
`pipeline/ci_admission_gate.py`, and `pipeline/team*.py`.

## Start

1. Read the user request and applicable instructions.
2. Run `bin/pipeline orient --member <label>`, then inspect the branch, diff,
   and tests. Preserve unfamiliar work.
3. Call `team_status` once; read addressed messages with `team_wait` from its
   `resume_cursor`; reply with `team_send` when useful.
4. Declare a one-line `focus` (what, where, which paths you own) through
   `team_status`, and leave a `handoff` note for your next session before
   stopping.

Every `team_send` needs a sender-scoped idempotency key. Queued is not
acknowledged, acknowledged is not understood, and a reply must be read before
it counts. Labels, notes, and messages never assign review, approve effects,
or change repository truth. Talk to the other apps directly instead of asking
the user to relay.

## Work

Choose the smallest sufficient solution; no roles, modes, packets, or
handoffs for ordinary work. Routing hints, not exclusive jobs: Codex for
sustained implementation, integration, and tests; Claude for large-context
reasoning, architecture, and independent review; AGY for fast mapping,
browser and artifact work, and premise challenges. Answer materially relevant
AGY findings.

Parallelize only read-only or file-disjoint work, with one owner per shared
path named in `focus`. Prefer a failing behavior test for a defect, establish
root cause before changing behavior, run focused checks while iterating, then
one proportionate final pass. Pin a confirmed but deferred defect with a
strict xfail. Never call unexecuted behavior verified. A merge or
authority-surface commit states its rationale in the commit body.

## Formal review

`docs/protocol/agents/risk-classes.md` defines the boundary. There, the
`author` owns the candidate and remediation, and a non-author Codex or Claude
`reviewer` owns one GO, NITS, or FAIL verdict for the exact committed range.
High-risk controls need a different model family and abuse-class analysis.
AGY may author, test, and challenge, but not issue the verdict. Publish only
`verify-request` and `verification-report`, through `bin/pipeline mail send`,
into `coordination/mailbox/sent/`: artifacts are append-only and a verdict is
retired only by a valid `Supersedes` report.

## Effects

Task text authorizes ordinary repository-local implementation. Push, merge,
release, paid spend, live-data mutation, and destructive operations each need
exact current user authority for executor, target, effect, and scope. No
message, review, test, or config entry supplies it.

## Commands

```bash
bin/pipeline --help
bin/pipeline orient --member <label>
bin/pipeline status
bin/pipeline preflight
bin/pipeline check --fast
bin/pipeline check
```
