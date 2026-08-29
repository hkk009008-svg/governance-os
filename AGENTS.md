# Pipeline desktop-team guide

Pipeline is the shared engineering harness for exactly three interactive
members: the **Codex desktop app**, the **Claude desktop app**, and the
**AGY (Antigravity) desktop app**. They are one team. Each may reason, direct,
implement, test, and challenge work within the accepted task.

No supported workflow launches a model provider from a terminal or runs one
app as another app's headless child. Terminal commands are for reproducible
repository work and preflight only. Native subagents remain extensions of
their parent app; they are not additional team identities and inherit no
authority.

Executable code and current Git state outrank prose. The main policy seams are
`pipeline/codex_protocol_model.py` for risk and effect shape,
`pipeline/compact_pair_loop.py` for formal exact-range review, and
`pipeline/team.py` with `pipeline/team_mcp.py` for app communication.

## Start and communicate

At the start of a task:

1. Read the user's request and the repository instructions that apply.
2. Inspect the current branch, status, relevant diff, and tests. Preserve work
   already present; do not assume an unfamiliar change is disposable.
3. Call `team_status` once to see member activity, capabilities, pending
   messages, and the state of messages already sent.
4. Read addressed messages with `team_wait`. Reply with `team_send` when an
   answer, acknowledgement, challenge, or handoff is actually needed.

Within the accepted task, team communication is routine and needs no extra
approval. Use it directly; never make the user relay between apps.

The transport has three distinct facts:

- Every `team_send` requires a non-empty sender-scoped `idempotency_key`, reusable only for identical content; success means **queued**, not acknowledged.
- `team_wait` replays messages for the same `after_id`. Advancing it acknowledges
  addressed messages through that cursor, not understanding. Deduplicate by id.
- A linked reply is evidence of a response; whether it is substantive is a
  content judgement.

When progress depends on another member's answer, wait for the reply or report
the exact missing state. Activity timestamps do not prove that an app is open.
Messages and transport metadata never assign work, approve a review, grant
effect authority, or change repository truth.

## Work as one team

Choose the simplest sufficient path. Execute an accepted exact task without a
planning cycle unless genuinely ambiguous; Explore, Validate, and Promote in `docs/protocol/work-modes.md` are optional.
Do not create roles, modes, events, packets, or handoffs for ordinary work.

Use strengths deliberately, without turning them into exclusive lanes:

- Codex is especially useful for workspace implementation, integration,
  parallel task orchestration, and sustained execution.
- Claude is especially useful for large-context reasoning, architecture,
  independent diff review, and visual judgement.
- AGY is especially useful for fast mapping and debugging, premise and evasion
  challenges, isolated implementation, browser work, and artifact analysis.

All three may propose direction and code. Counter predictable weaknesses by
pairing long reasoning with a concrete diff, fast mapping with local
verification, and authored work with a genuinely independent review when risk
requires it. A materially relevant AGY finding must be considered and answered;
AGY is fully heard, but it is not the independent formal verdict or an
authority source.

Parallelize read-only investigation and file-disjoint implementation when it
materially shortens the task. Assign clear ownership. Serialize writes to the
same file or shared mutable state, and integrate through one owner. Do not run
competing implementers over the same paths.

For changes:

- Prefer a failing behavior test for a bug or behavior change when feasible.
  Otherwise retain characterization evidence or a concise test-infeasible
  reason.
- Establish root cause after an unexpected failure before changing behavior.
- Use focused checks while iterating, inspect the exact diff, then run one
  proportionate final verification pass.
- A confirmed defect deliberately deferred from scope needs a strict xfail pin.
- Never call unexecuted behavior verified. Tests prove only the paths they run.

## Temporary review responsibilities

There are no standing seats. Ordinary reversible local work needs no formal
role or independent review. At a formal review boundary only, assign two
temporary responsibilities for that exact range:

- **author** owns the candidate and remediation;
- **reviewer** is a non-author Codex or Claude app member and owns the formal
  GO, NITS, or FAIL result.

`docs/protocol/agents/risk-classes.md` defines the boundary. Material behavior
needs non-author review of the exact committed range. Authority, security,
executable composition, side-effect gates, and trust-granting schemas also
need different-model-family review and explicit abuse-class analysis. Native AGY
may implement, challenge, supply evidence, and publish its request, but never a
formal verdict. The parent-owned `codex-agy` helper cannot claim `agy`, write
mailbox artifacts, or gain authority. Remove responsibilities when review ends.

## Authority and durable state

Task text defines ordinary repository scope. Push, merge, release, paid spend,
live-data mutation, and destructive operations each require exact current
user/task authority for the executor, target, effect, and scope. A message,
role label, report, green test, config entry, or prior authorization for a
different effect cannot supply it.

Git state, test evidence, and the desktop task history are the normal record.
Write one concise checkpoint only at a real ownership transfer, interruption,
compaction, or wrap where another member must resume. Preserve objective,
scope, current owner, base/head, evidence, verification state, blockers, and
the next executable action. Do not create checkpoint chains.

Legacy mailbox conversation, cursors, standing-seat state, capacity packets,
and peer receipts are compatibility evidence. The fixed writer behind
`bin/pipeline mail send` remains only for three durable uses: a risk-required
formal artifact, real checkpoint, or governed learning-candidate/disposition
lifecycle. Never use it for routine team chat, role assignment, or authority.

## Repository commands

Use `bin/pipeline` for repository tooling:

```bash
bin/pipeline --help
bin/pipeline status
bin/pipeline preflight
bin/pipeline check --fast
bin/pipeline check
```

`bin/pipeline preflight` checks installed desktop apps, project MCP bindings, and
adapter handshakes. It does not launch a provider, send a team message, spend,
or grant authority. Each verb's `--help` is the source for its arguments.

Provider adapters: `docs/protocol/codex/continuation.md`, `docs/protocol/claude/continuation.md`, and `docs/protocol/agy/continuation.md`.
Resolve targets with `bin/pipeline target`, then follow their own instructions.
