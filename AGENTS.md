# Pipeline agent guide

This repository has exactly two participants: the **`claude` CLI** and the
**`codex` CLI**. There is no desktop app, no MCP server, no persistent peer,
and no browser in any supported path. If a procedure cannot be typed at a
terminal, it is not part of this system.

`ARCHITECTURE.md` describes the current system; executable code and committed
state outrank prose, including this file. Canonical policy seams:
`pipeline/codex_protocol_model.py` (identity, ownership, risk, effect shape),
`pipeline/compact_pair_loop.py` (formal exact-range review), and
`pipeline/mailbox_writer.py` behind `coordination/bin/send-event` (durable
events).

## One command

Everything runs through `bin/pipeline`. It resolves the primary checkout's
interpreter — from a linked worktree too — and clears the per-seat index
variable itself, so no caller carries a prefix.

```bash
pipeline --help          # every verb, with its one-line purpose
pipeline status          # compact current-state snapshot
pipeline check           # the completion-gate aggregate
pipeline peer ask codex --task <id> --prompt-file <f> --dry-run
```

Each verb accepts its own `--help`. `pipeline <verb> --help` is the answer to
"what arguments does this take", never a doc page.

## Universal contract

1. For direct, reversible, repository-local work, execute natively: no formal
   role, work-mode declaration, mailbox event, or independent review. Execute
   an accepted exact task without adding a brainstorming or planning cycle
   unless behavior is materially ambiguous. Use smallest-sufficient
   verification, fresh, before claiming completion, and inspect the exact
   diff before committing.
   Keep this proportionality inside formal work too: fix concrete findings
   directly, use focused checks while iterating, and run one final review and
   full verification pass. Do not turn a bounded stale instruction into a
   generalized parser or a chain of intermediate review artifacts unless the
   user explicitly asks for that system or the implementation truly needs it.
2. Preserve unrelated work and stage explicit pathspecs. Use each worktree's
   native Git index; per-seat indexes are retired — do not create or share
   them. No destructive Git operations without explicit user authorization.
3. For a behavior change or bug fix, start with a failing behavior test when
   feasible; otherwise preserve characterization evidence or a
   `test-infeasible` reason. Establish root cause before changing behavior
   after an unexpected failure. A confirmed defect deferred from the current
   scope needs a strict xfail pin.
4. Load `.agents/skills/four-seat-protocol/SKILL.md` and its role skill only
   for explicit role, ownership-transfer, mailbox, durable-continuation, or
   formal-review work; skill presence alone is not a trigger. Delegation is
   optional and owner-chosen; never run concurrent implementers on shared
   files.
5. Review depth follows risk. Ordinary reversible local work needs focused
   verification only. Material behavior changes need non-author review of the
   exact committed range. Authority, security, executable composition,
   side-effect gates, and trust-granting schemas need distinct non-author,
   different-model actual-diff review plus explicit abuse-class analysis.
   Classification criteria: `docs/protocol/agents/risk-classes.md`. Tests
   prove only what they execute; a green gate grants no authority.
6. External effects — merge, lock, cursor consumption, **peer invocation**,
   paid spend, live-data mutation — each need separate exact authority for the
   executor, target, effect, and scope. Structural protocol data never grants
   it. Transport ambiguity is reported, never converted into an empty queue.
   **Push is deliberately not on that list.** It was, in five documents, while
   the harness allowed `git push` without prompting — a control asserted in
   prose and absent from the mechanism. A document is not a gate, so the claim
   was dropped rather than kept as decoration. Restoring the obligation means
   restoring a permission rule, not a sentence.
7. At a long-horizon checkpoint (transfer, interruption, compaction, wrap),
   preserve: objective, accepted scope, owner, policy revision, base/head,
   evidence refs, verification status, unresolved blockers, and the next
   executable action. Durable shared state beats chat memory. Write it as
   one checkpoint `findings` event (draft: `pipeline checkpoint`, which runs
   `pipeline/draft_checkpoint.py`); its
   `Lessons:` line routes lessons toward learning-candidates, and
   `none-considered` is always a valid answer. Resume from one snapshot
   plus the newest campaign checkpoint; recalled state is advisory.

Work modes: ordinary work declares no mode. A long-running campaign selects
`explore`, a frozen candidate `validate`, a canonical or live mutation
`promote` — see `docs/protocol/work-modes.md`. Modes grant no authority.

Sessions start as a readiness bridge and adopt a live role only on explicit
assignment; parent-scoped helpers never inherit that authority. Factual
inventory claims cite the command and result that prove them.

## Working as one unit

The two CLIs reach each other by running each other, once, as child
processes:

```bash
pipeline peer ask codex  --task <id> --prompt-file <f>   # from a Claude session
pipeline peer ask claude --task <id> --prompt-file <f>   # from a Codex session
pipeline peer receipts --task <id>
```

Every invocation writes a receipt under `coordination/peer/<task>/` recording
the argv hash, the prompt hash, the exit code, the duration, and the model the
peer's **own output** reported. The child's exit code is the delivery
acknowledgement; the previous MCP bridge had none.

A receipt is evidence, not attestation — whoever can write the file can forge
it. It is better than prose the author typed and weaker than a signature. Do
not call it proof of who reviewed.

Peer invocation is a provider launch and paid spend: item 6 applies in full.
`--dry-run` prints the exact argv without launching, which is how you show a
proposed invocation to whoever must authorize it. Full contract:
`docs/protocol/peer.md`.

### AGY is a subagent, never a side

`pipeline peer ask agy --role <map|challenge|evasion|debug|implement|review>`
dispatches to the parent-owned `claude-agy` / `codex-agy` wrappers, which hold
one shared lane lock. Both CLIs may call it. Its receipts are marked
`"advisory": true`. AGY is never a seat, a mailbox participant, a reviewer, or
a GO/NITS/FAIL source, and `config/model-families.toml` keeps
`active_families = ["claude", "gpt"]` so a gemini-family opinion cannot
satisfy the different-family review requirement.

## Provider adapters

Both sides map the same policy onto the same kind of host — a terminal. The
differences that remain are forced by the harness, not chosen.

Load only the adapter for the CLI you are in:

- Claude: `CLAUDE.md`, then `docs/protocol/claude/continuation.md`.
- Codex: `docs/protocol/codex/continuation.md`, then `.codex/agents/`.
- Peer invocation, either direction: `docs/protocol/peer.md`.

Target-repository routes (evidence-ledger and future destinations) resolve
per task through `pipeline target` and the provider continuation docs, not
through this router.
