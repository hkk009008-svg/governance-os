# Pipeline agent guide

`ARCHITECTURE.md` describes the current system; executable code and committed
state outrank prose, including this file. Canonical policy seams:
`scripts/codex_protocol_model.py` (identity, ownership, risk, effect shape),
`scripts/compact_pair_loop.py` (formal exact-range review), and
`scripts/mailbox_writer.py` behind `coordination/bin/send-event` (durable
events).

## Universal contract

1. For direct, reversible, repository-local work, execute natively: no formal
   seat, work-mode declaration, mailbox event, or independent review. Execute
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
   for explicit seat, ownership-transfer, mailbox, wave, durable-continuation,
   or formal-review work; skill presence alone is not a trigger. Delegation is
   optional and owner-chosen; never run concurrent implementers on shared
   files.
5. Review depth follows risk. Ordinary reversible local work needs focused
   verification only. Material behavior changes need non-author review of the
   exact committed range. Authority, security, executable composition,
   side-effect gates, and trust-granting schemas need distinct non-author,
   different-model actual-diff review plus explicit abuse-class analysis.
   Classification criteria: `docs/protocol/agents/risk-classes.md`. Tests
   prove only what they execute; a green gate grants no authority.
6. External effects — push, merge, lock, cursor consumption, provider launch,
   paid spend, live-data mutation — each need separate exact authority for
   the executor, target, effect, and scope. Structural protocol data never
   grants it. Transport ambiguity is reported, never converted into an empty
   queue.
7. At a long-horizon checkpoint (transfer, interruption, compaction, wrap),
   preserve: objective, accepted scope, owner, policy revision, base/head,
   evidence refs, verification status, unresolved blockers, and the next
   executable action. Durable shared state beats chat memory. Write it as
   one checkpoint `findings` event (draft: `scripts/draft_checkpoint.py`);
   its `Lessons:` line routes lessons toward learning-candidates, and
   `none-considered` is always a valid answer. Resume from one snapshot
   plus the newest campaign checkpoint; recalled state is advisory.

Work modes: ordinary work declares no mode. A long-running campaign selects
`explore`, a frozen candidate `validate`, a canonical or live mutation
`promote` — see `docs/protocol/work-modes.md`. Modes grant no authority.

Sessions start as a readiness bridge and adopt a live role only on explicit
assignment; parent-scoped helpers never inherit that authority. Factual
inventory claims cite the command and result that prove them.

## Provider adapters

For the supported Codex/Claude task connector, the user has granted standing
authority for one named `pipeline-codex-bridge` instance with a hard per-instance
`$1.00` ceiling whenever cross-app communication is needed. Use it directly without
asking the user to relay or approve the launch again, reuse the existing
instance, and stop it after the exchange. This narrow standing grant does not
authorize duplicate bridges, higher spend, repository effects, or formal
review publication.

An initial startup-time `No reachable agents` can be native registration lag,
not absence. Confirm the one named process/socket, allow one bounded re-list,
and only then report the exact refusal; never start a second bridge.

Load only the adapter for the harness you are in:

- Claude: `CLAUDE.md`, then `docs/protocol/claude/continuation.md`.
- Codex: `docs/protocol/codex/continuation.md`, then `.codex/agents/`.
- Cross-provider: `docs/protocol/threeway/`.

Target-repository routes (evidence-ledger and future destinations) resolve
per task through `scripts/target_binding.py` and the provider continuation
docs, not through this router.
