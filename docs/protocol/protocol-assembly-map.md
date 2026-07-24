# Protocol Assembly Map

This map reverse-engineers the current folder structure into the safest places
to reassemble protocol portions. The rule is simple: use the lowest folder that can own it without ambiguity.

The map is descriptive, not a new authority layer. When a universal protocol
rule, Codex-specific instruction, mailbox event, inventory row, or proof
artifact needs a home, place it where the folder already expresses that intent.

```mermaid
flowchart TD
    Root["AGENTS.md / CLAUDE.md"]
    Policy["docs/protocol/"]
    Skills[".agents/skills/ + .cursor/skills/"]
    Codex[".codex/agents/ + .codex/hooks/"]
    Cursor[".cursor/hooks/ + Agents Window worktrees"]
    Scope["coordination/verification/scopes/ (frozen historical)"]
    Ledger["coordination/"]
    Board["docs/REMEDIATION-INVENTORY.md"]
    Work["docs/superpowers/"]
    Evidence["scripts/ + logs/"]
    Tests["tests/unit/"]

    Root --> Policy
    Policy --> Skills
    Policy --> Codex
    Policy --> Cursor
    Skills --> Ledger
    Codex --> Ledger
    Cursor --> Ledger
    Skills --> Scope
    Scope --> Evidence
    Ledger --> Board
    Board --> Work
    Board --> Evidence
    Evidence --> Tests
```

| Protocol portion | Intended home | Example | Reason |
|---|---|---|---|
| Universal protocol policy | `docs/protocol/agents/` | `docs/protocol/agents/director-operator.md` | Rules shared by Claude, Codex, and other agents should not live in a Codex-only surface. |
| Codex protocol mapping | `docs/protocol/codex/continuation.md` | Capacity-max workflow, Codex launch pattern | Codex mechanics translate the universal rules into Codex-native tools, hooks, and role agents. |
| Target-repo CLI adoption bridge | `docs/protocol/codex/ledger-cli-adoption.md` | Evidence-ledger CLI bridge | Target-repo adoption is Codex-specific mechanics and should not duplicate universal protocol policy. |
| Cursor protocol mapping | `docs/protocol/cursor/continuation.md` | Agents Window/worktree/mailbox adapter | Cursor mechanics translate universal rules into app-native worktrees, hooks, and top-level chats without forking policy. |
| Cursor seat role prompts | `docs/protocol/cursor/roles/*.md` | `docs/protocol/cursor/roles/operator.md` | The session-start hook injects the role matching the validated worktree, conversation, and model. |
| Cursor review command | `.cursor/skills/review-next/SKILL.md` | `/review-next` | The assigned Operator resolves committed work without copied prompts or event refs. |
| Cursor app binding | `scripts/cursor_app_binding.py` | `~/.cursor/pipeline-app-seats.json` | One helper exclusively owns the user-local conversation/model registry. |
| Cursor diagnostics + mailbox wrappers | `scripts/cursor_seat_launcher.py`, `coordination/bin/cursor-*` | `cursor-seat status`, `cursor-publish`, `cursor-consume` | The former launcher is read-only; mailbox wrappers delegate effects to fixed writers. |
| Cursor session guardrails | `.cursor/hooks.json` and `.cursor/hooks/` | `.cursor/hooks/seat-policy` -> `scripts/cursor_hook_policy.py` | Hooks are fail-closed lifecycle/tool boundaries, not protocol prose or mailbox state. |
| Target-repo start guard | `scripts/ledger_start_guard.py` | Enforced Pipeline-first ledger seat startup | Executable proof belongs in scripts, then docs/skills/prompts link to it. |
| Start-session router | `AGENTS.md` | Codex start-session inhabitance block | The root file should route agents before task-specific docs are loaded. |
| Live seat checklists | `.agents/skills/` | `.agents/skills/seat-operator/SKILL.md` | Seat actions are reusable runtime instructions with clear trigger rules. |
| Spawnable Codex roles | `.codex/agents/*.toml` | `.codex/agents/protocol-operator.toml` | Role prompts are executable agent modules and should stay near Codex agent configuration. |
| Session guardrails | `.codex/hooks.json` and `.codex/hooks/` | `guard-git-index.sh`, `session-smoke.sh` | Hooks are lifecycle/tool boundaries, not protocol prose or mailbox state. |
| Lane-V trigger authority | `coordination/mailbox/sent/` (compact-pair verify-request) | `*-director-to-operator-verify-request.md` | The committed compact-pair verify-request is the sole Lane-V trigger authority (Canonical Compact Pair Invariant, `scripts/codex_protocol_model.py`). `coordination/verification/scopes/` retains only frozen historical descriptors (e.g. `<task-uuid>.json`) — no longer a live authority. |
| Mailbox events | `coordination/mailbox/sent/` | `*-operator2-to-all-verification-report.md` | Inter-seat protocol speech must be durable and commit-addressable. |
| Mailbox read cursors | `coordination/mailbox/seen/` | `coordination/mailbox/seen/director.txt` | Per-seat consumed-up-to timestamps are the single read-state truth. |
| Shared-file locks | `coordination/locks/` | `2-<entrypoint>.py.lock` when active | Locks are temporary ownership claims over shared implementation surfaces. |
| Campaign board | `docs/REMEDIATION-INVENTORY.md` | Wave row status and verifier columns | The inventory is the coordinator-owned single board for row lifecycle state. |
| Director work packets | `docs/superpowers/briefs/` | `2026-06-16-http-web-server-lock-redo.md` | R-BRIEFs are task-local instructions for one implementation or verification loop. |
| Plans and specs | `docs/superpowers/plans/`, `docs/superpowers/specs/` | Wave plans, stub-contract specs | Larger design and execution artifacts need durable but bounded homes. |
| Executable checks | `scripts/` | `wave_gate_check.py`, `ci_smoke.py` | Gate and readiness truth should be runnable, not only asserted in prose. |
| Committed evidence | `logs/` | `product-oracle-wave2.json`, `discovery-*.json` | Measurement and discovery outputs support R-MEASURE/R-EVIDENCE claims. |
| Protocol tool tests | `tests/unit/` | `test_protocol_mailbox.py`, `test_cursor_surface_sync.py`, `test_codex_ledger_bridge.py` | Tool contracts should be enforced by tests so prose drift is caught. |

## Placement Rule

Use this quick routing check before adding or moving protocol material:

```text
Universal rule?             -> docs/protocol/agents/
Codex-only rule?            -> docs/protocol/codex/
Target-repo Codex bridge?   -> docs/protocol/codex/ledger-cli-adoption.md
Cursor protocol mapping?    -> docs/protocol/cursor/continuation.md
Cursor app binding?         -> scripts/cursor_app_binding.py + .cursor/hooks/
Cursor seat role prompt?    -> docs/protocol/cursor/roles/
Cursor app command?         -> .cursor/skills/
Cursor mailbox front door?  -> scripts/cursor_mailbox.py + coordination/bin/cursor-*
Target-repo start guard?    -> scripts/ledger_start_guard.py
Seat action checklist?      -> .agents/skills/
Spawnable role prompt?      -> .codex/agents/
Lifecycle/index guardrail?  -> .codex/hooks*
Lane-V trigger authority?   -> coordination/mailbox/sent/ (compact-pair verify-request)
Actual protocol event?      -> coordination/mailbox/sent/
Read cursor?                -> coordination/mailbox/seen/
Lock/ownership state?       -> coordination/locks/
Wave/task status?           -> docs/REMEDIATION-INVENTORY.md
Specific fix brief?         -> docs/superpowers/briefs/
Wave plan or design spec?   -> docs/superpowers/plans/ or docs/superpowers/specs/
Executable proof?           -> scripts/
Proof output?               -> logs/
Tool contract test?         -> tests/unit/
```

## Non-Goals

- Do not centralize all protocol text into this file.
- Do not move live mailbox, cursor, lock, or inventory state into docs.
- Do not duplicate universal rules in Codex-specific surfaces.
- Do not treat a script's green result as an operator GO when the protocol
  requires a mailbox `verification-report`.
