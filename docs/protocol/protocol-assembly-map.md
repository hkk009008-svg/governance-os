# Protocol assembly map

## Authority order

1. System/developer instructions and the current user task.
2. Current executable code and Git state.
3. `AGENTS.md` universal desktop-team contract.
4. `ARCHITECTURE.md` current implementation map.
5. Risk and formal-review contracts under `docs/protocol/agents/`.
6. Provider-specific desktop mechanics under `docs/protocol/codex/` and
   `docs/protocol/claude/`.
7. Target repository instructions for target-local product work.
8. Historical ADRs, mailbox events, receipts, packets, and handoffs as evidence
   only when they do not conflict with current sources above.

No lower layer grants an external effect or widens the task.

## Current placement

| Concern | Canonical location |
|---|---|
| Team membership and universal behavior | `AGENTS.md`, `docs/protocol/agents/core.md` |
| Implemented topology and trust boundaries | `ARCHITECTURE.md` |
| App message contract | `docs/protocol/peer.md` |
| MCP entry and tools | `pipeline/team.py`, `pipeline/team_mcp.py` |
| Message validation and storage | `pipeline/team_messages.py`, `pipeline/team_store.py` |
| App project bindings | `.codex/config.toml`, `.mcp.json`, `.agents/plugins/pipeline-team/{plugin.json,mcp_config.json}` |
| App readiness | `pipeline/harness_preflight.py`, `bin/pipeline preflight` |
| Risk and effect shape | `pipeline/codex_protocol_model.py`, `docs/protocol/agents/risk-classes.md` |
| Temporary formal review | `pipeline/compact_pair_loop.py`, `docs/protocol/agents/director-operator.md` |
| Parallelism and integration | `docs/protocol/agents/orchestration.md` |
| Codex app mechanics | `docs/protocol/codex/continuation.md` |
| Claude app mechanics | `CLAUDE.md`, `docs/protocol/claude/continuation.md` |
| Product target binding | `pipeline/target_binding.py` and the selected target repository |
| Reproducible checks | `bin/pipeline`, `pipeline/`, `tests/` |
| Durable formal review / real transfer / learning lifecycle | fixed `bin/pipeline mail send` writer; never routine chat |
| Legacy compatibility | old mailbox conversation/cursors, peer receipts, role adapters, plans and ADRs |

## Placement rule

```text
Universal team rule?           -> AGENTS.md / docs/protocol/agents/
App-only mechanic?             -> docs/protocol/<app>/ and project config
Transport behavior?            -> pipeline/team_* and docs/protocol/peer.md
Risk or effect admission?      -> pipeline/codex_protocol_model.py
Formal exact-range binding?    -> pipeline/compact_pair_loop.py
Product fact?                  -> target repository
Executable proof?              -> pipeline/ and tests/
Formal artifact/real transfer? -> fixed mailbox writer, smallest durable record
Historical evidence?           -> existing legacy corpus, never live authority
```

Do not duplicate universal rules into every adapter. Do not introduce another
message bus, standing role inventory, provider launcher, or mutable source of
authority when the existing app transport and Git/task state are sufficient.

For the registered `evidence-ledger` target, provider routes may point to
`docs/protocol/codex/ledger-cli-adoption.md` or the Claude equivalent for
historical compatibility; current work still resolves the target and reads its
own instructions before editing.
