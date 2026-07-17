# ARCHITECTURE.md - Governance OS

> Truth lives here. AGENTS.md and CLAUDE.md are process layers; this file is
> the verified truth layer for the Pipeline governance kernel. When process
> prose and this file disagree about Pipeline facts, this file wins and the
> stale prose must be fixed in the same change.

*Last verified: 2026-07-17 @ 2dc95ad*

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
| `load_kernel_mirror` | `scripts/target_binding.py:147` | Validates the declarative-only compact-kernel epoch/writer mirror without selecting runtime behavior. |
| `resolve_target` | `scripts/target_binding.py:184` | Resolves the active product-target binding from `governance.toml` (ADR-013); fail-closed on unknown targets. |
| `_accepted_context_keys` | `scripts/compact_state_mapping.py:98` | Independently enumerates every finite producer-backed v1 mapping context for exact fixture and shadow-gate closure. |
| `reduce_protocol_state` | `scripts/capability_reducer.py:1230` | Produces one pure, deterministic, non-authoritative compact shadow report. |
| `adapt_v1_history` | `scripts/capability_v1_adapter.py:2826` | Strictly adapts host-normalized v1 history into reducer-accepted epoch-0 shadow envelopes. |
| `main` | `scripts/protocol_capacity_board.py:16` | Renders and validates active capacity packets for a wave. |
| `LEDGER_CLI_BRIDGE` | `scripts/codex_protocol_model.py:519` | Executable model data for Pipeline-to-evidence-ledger Codex startup. |
| `render_r_independence` | `scripts/codex_protocol_model.py:744` | Renders the standing R-INDEPENDENCE contract into Codex harness output. |
| `render_ledger_start_guard` | `scripts/codex_protocol_model.py:816` | Renders guard guidance into readiness output. |
| `render_lane_v_v3` | `scripts/codex_protocol_model.py:1156` | Renders the provider-neutral Lane V v3 authority and publication contract. |
| `TaskPublicationStore` | `scripts/verification_report_gate.py:1754` | Owns the atomic task-bound Lane V v3 publication state machine. |
| `publish_candidate` | `scripts/verification_report_gate.py:3078` | Publishes one validated Lane V v3 report as a durable file-plus-stage-0-index transaction with explicit recovery. |

## 4. Runtime Invariants

- Pipeline remains the Codex four-seat governance kernel.
- evidence-ledger is the bound product target for current ledger-routed work.
- Compact-kernel v1 remains the only authority at epoch `0`. The read-only
  historical adapter imports the pure reducer; the reducer does not import the
  adapter. Neither shadow surface activates or writes runtime state.
- The shadow parity gate requires exact accepted-context key equality across
  producer-derived manifest, mapping fixture, adapter rules, and corpus cases;
  specialized lifecycle contexts remain explicit `no_route_event` evidence.
- Durable shared state beats chat memory: git commits, mailbox bodies, capacity
  packets, cursor state, and verification reports are authoritative.
- Live seats start with `scripts/ledger_start_guard.py --seat <seat> --wave 2`
  from Pipeline before entering evidence-ledger.
- Ordinary git and pytest commands use `env -u GIT_INDEX_FILE`.
- Commit, push, merge, cursor consumption, lock actions, pod spend, target
  checkout refresh, production generation, paid API spend, and every other side
  effect are separate authorities. Each requires explicit authorization or a
  valid routed executor; no model or provider identity grants authority.
- Lane V is independent verification by a non-author operator over one
  committed descriptor and lawful trigger. New reports use lane-v-report/v3
  and publish atomically through TaskPublicationStore. Model or provider
  identity grants no authority.
- `scripts/verification_report_gate.py` binds the exact full reviewed range,
  canonical `lane-v-scope/v1` descriptor, and one committed verify-request or
  shipping trigger. Missing, duplicated, stale, mismatched, or reconstructed
  authority fails closed. The operator alone issues GO/NITS/FAIL from executed
  repository evidence.
- `TaskPublicationStore` is the sole live publication state machine. Its
  task-bound `publishing -> published` transaction retains the candidate
  inode/digest and exact stage-0 Git blob facts until final bytes, object, index
  entry, blob readback, and durability checks agree. `resume` and read-only
  `status` are the crash-recovery paths. Direct mailbox writes and hooks are not
  publication authority.
- Exact pre-v3 report paths and raw-byte hashes remain accepted only through the
  committed historical manifest. Local `.codex/runtime` residue is outside the
  operative scan and is not mutated by protocol verification.
- The Codex model applies R-INDEPENDENCE before implementation: it classifies
  the four adversarial surfaces, requires a durable independent design-time
  enumeration for triggered work, and requires independent actual-diff
  verification before completion.

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

The project-smoke block proves signed-bus imports/canonicalization, the
load-bearing event-kind relationship, and the seat/mailbox registry. Lane V v3
schema, trigger, publication, and provider-decommission claims are proved by the
focused protocol tests; smoke does not substitute for those regressions or an
operator GO.

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
