# ARCHITECTURE.md - Governance OS

> Truth lives here. AGENTS.md and CLAUDE.md are process layers; this file is
> the verified truth layer for the Pipeline governance kernel. When process
> prose and this file disagree about Pipeline facts, this file wins and the
> stale prose must be fixed in the same change.

*Last verified: 2026-07-12 @ 48bb9db*

## 1. Purpose

Pipeline is the governance kernel for multi-seat AI coding work. It provides
durable mailbox routing, live seat status, route capacity packets, protocol
verification gates, and Codex bridge mechanics. It is intentionally separate
from the private product repository: evidence-ledger is the bound product
target, while Pipeline owns the coordination harness around that target.

ARCHITECTURE.md records verified governance-kernel truth. Product behavior
truth for evidence-ledger belongs in evidence-ledger's own docs and tests.

## 2. Topology

Primary control flow:

```text
user or parent prompt
  -> Pipeline seat startup guard
  -> seat status and mailbox route body
  -> capacity packet scope
  -> implementation or verification command
  -> mailbox verify-request / verification-report
  -> coordinator closeout or reroute
```

Key directories:

| Path | Role |
|---|---|
| `scripts/` | Executable governance tooling: smoke, doc checks, mailbox monitoring, route validation, capacity board, Codex model rendering. |
| `coordination/` | Durable protocol state: mailbox events, seen cursors, presence, capacity packets, and shell mailbox tools. |
| `.agents/skills/` | Codex-readable repo skills for four-seat operation and seat-specific authority. |
| `.codex/agents/` | Codex role prompts and runtime harness configuration. |
| `docs/protocol/` | Pull-on-demand protocol docs, provider adoption guides, and assembly maps. |
| `threeway/` | Signed-bus and merge-gate substrate used by cross-provider protocol tooling. |

## 3. Module Map

| Symbol | File:line | Role |
|---|---|---|
| `_project_smoke` | `scripts/ci_smoke.py:53` | Verifies governance-OS runtime invariants before governance gates run. |
| `main` | `scripts/ci_smoke.py:100` | Runs the full smoke gate sequence. |
| `run` | `scripts/check_coordination.py:346` | Validates mailbox event filenames, cursors, kinds, and coordination hygiene. |
| `run` | `scripts/check_placeholders.py:103` | Scans for adoption-placeholder tokens outside the allowlist. |
| `check_sha_refs` | `scripts/check_doc_claims.py:1706` | Reports stale or mismatched commit-SHA citations. |
| `classify_sha_ref_baseline` | `scripts/check_doc_claims.py:1768` | Classifies SHA-reference drift as reviewed baseline or new/changed drift. |
| `collect_monitor_state` | `scripts/mailbox_monitor.py:175` | Builds a read-only snapshot of mailbox, receipt, and heartbeat state. |
| `build_guard` | `scripts/ledger_start_guard.py:175` | Enforces Pipeline-first startup for target-routed seats; paths come from the binding registry. |
| `resolve_target` | `scripts/target_binding.py:135` | Resolves the active product-target binding from `governance.toml` (ADR-013); fail-closed on unknown targets. |
| `main` | `scripts/protocol_capacity_board.py:16` | Renders and validates active capacity packets for a wave. |
| `LEDGER_CLI_BRIDGE` | `scripts/codex_protocol_model.py:482` | Executable model data for Pipeline-to-evidence-ledger Codex startup. |
| `render_ledger_start_guard` | `scripts/codex_protocol_model.py:772` | Renders guard guidance into readiness output. |

## 4. Runtime Invariants

- Pipeline remains the Codex four-seat governance kernel.
- evidence-ledger is the bound product target for current ledger-routed work.
- Durable shared state beats chat memory: git commits, mailbox bodies, capacity
  packets, cursor state, and verification reports are authoritative.
- Live seats start with `scripts/ledger_start_guard.py --seat <seat> --wave 2`
  from Pipeline before entering evidence-ledger.
- Ordinary git and pytest commands use `env -u GIT_INDEX_FILE`.
- Pushes, lock actions, cursor consumption, pod spend, paid API spend, target
  checkout refresh, and product-generation side effects require explicit
  authorization or a valid routed executor.
- Codex Lane V attempts one verdict-blind Opus review through
  `scripts/opus_review_bridge.py` after its primary analysis. Opus remains
  advisory; the bridge proves Pipeline identity and the reviewed commits,
  materializes a temporary snapshot at the reviewed HEAD, and loads verifier
  instructions from a commit that precedes the reviewed HEAD (the explicit
  base or first parent). Claude runs with `--safe-mode`,
  `--disable-slash-commands`, and the pinned prompt supplied through
  `--append-system-prompt`. A network-capable outer OS-enforced sandbox denies
  source/snapshot and persistent-home writes. Exact verification commands use
  one-shot broker tokens to enter a second default-deny sandbox outside the
  inherited outer Seatbelt; that sandbox denies network, source and sensitive
  reads, non-scratch writes, and unlisted executables. Sandbox failure is an
  explicit degraded Codex-only fallback and never reaches the provider. The
  provider and each verification command run in distinct process groups with
  whole-group cleanup, and broker socket reads are time-bounded. The bridge
  resolves the local Claude executable before sandbox launch, canonicalizes
  reviewed SHAs to lowercase, disables Git textconv for patch rendering, and
  applies the same bounded delimiter-safe finding-ID grammar in its JSON Schema
  and Python parser.

## 5. Mailbox And Capacity State

Mailbox events live under `coordination/mailbox/sent/`; read cursors live under
`coordination/mailbox/seen/`. The receiving roster comes from
`scripts/protocol_mailbox.py:11` and `scripts/protocol_mailbox.py:17`.

Capacity packets live under `coordination/capacity/packets/`. A coordinator
route is valid only when `scripts/protocol_capacity_board.py --wave <wave>` and
the route-validation form both accept the packet set.

Unknown coordinator broadcast receipt is not delivery proof. It is an unproved
receipt state surfaced by `scripts/mailbox_monitor.py`.

## 6. Verification Gates

Primary local commands:

```bash
env -u GIT_INDEX_FILE .venv/bin/python scripts/ci_smoke.py
env -u GIT_INDEX_FILE .venv/bin/python scripts/check_coordination.py
env -u GIT_INDEX_FILE .venv/bin/python scripts/protocol_capacity_board.py --wave 2
env -u GIT_INDEX_FILE .venv/bin/python scripts/check_doc_claims.py --sha-refs
```

`scripts/ci_smoke.py` stays quiet when the reviewed historical commit-SHA
baseline is unchanged. A changed SHA-ref drift set is a hard failure. Run
`scripts/check_doc_claims.py --sha-refs` for the full historical baseline
audit report.

## 7. Target-Repo Boundary

Pipeline can route, verify, and record evidence for evidence-ledger work, but it
does not own evidence-ledger product truth. Before product edits, read the
target repo's local instructions and work only inside the active route. If a
route names an isolated worktree or base, that worktree/base takes precedence
over the normal evidence-ledger checkout.

## 8. Known Sharp Edges

- The normal evidence-ledger checkout can be stale relative to routed worktrees.
- A mailbox receipt split with `unknown` seats proves only that receipt is
  unproved.
- Existing historical SHA-reference debt is baselined and quiet in smoke, not
  rewritten.
- Some protocol docs still contain adopter-facing placeholder examples by
  design; root user-facing truth docs do not.
