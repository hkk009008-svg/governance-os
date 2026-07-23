# ARCHITECTURE.md - Governance OS

> Truth lives here. AGENTS.md and CLAUDE.md are process layers; this file is
> the verified truth layer for the Pipeline governance kernel. When process
> prose and this file disagree about Pipeline facts, this file wins and the
> stale prose must be fixed in the same change.

*Last verified: 2026-07-24 @ d39314e*

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
  -> readiness or named-seat orientation
  -> active outcome contract + durable owner
  -> seat-chosen implementation, collaboration, or ownership exchange
  -> committed actual change + outcome-bound verify-request
  -> distinct-identity non-author Operator GO/NITS/FAIL with finding dispositions
  -> separately user-authorized exact external-effect tuple, if any
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
| `run` | `scripts/check_coordination.py:287` | Validates mailbox event filenames, cursors, kinds, and coordination hygiene. |
| `run` | `scripts/check_placeholders.py:103` | Scans for adoption-placeholder tokens outside the allowlist. |
| `check_sha_refs` | `scripts/check_doc_claims.py:1706` | Reports stale or mismatched commit-SHA citations. |
| `classify_sha_ref_baseline` | `scripts/check_doc_claims.py:1768` | Classifies SHA-reference drift as reviewed baseline or new/changed drift. |
| `collect_monitor_state` | `scripts/mailbox_monitor.py:175` | Builds a read-only snapshot of mailbox, receipt, and heartbeat state. |
| `build_guard` | `scripts/ledger_start_guard.py:175` | Enforces Pipeline-first startup for target-routed seats; paths come from the binding registry. |
| `resolve_target` | `scripts/target_binding.py:143` | Resolves the active product-target binding from `governance.toml` (ADR-013); fail-closed on unknown targets. |
| `writer_fence` | `scripts/mailbox_writer.py:62` | Serializes fixed mailbox-event and cursor finalizers with one Git-common-dir lock. |
| `main` | `scripts/protocol_capacity_board.py:16` | Renders and validates active capacity packets for a wave. |
| `LEDGER_CLI_BRIDGE` | `scripts/codex_protocol_model.py:456` | Executable model data for Pipeline-to-evidence-ledger Codex startup. |
| `render_r_independence` | `scripts/codex_protocol_model.py:684` | Renders the standing R-INDEPENDENCE contract into Codex harness output. |
| `render_ledger_start_guard` | `scripts/codex_protocol_model.py:718` | Renders guard guidance into readiness output. |
| `chatgpt_pro_consult.reserve` | `scripts/chatgpt_pro_consult.py:195` | Reserves one parent-owned consultation key in the shared Git-common-dir record. |
| `parse_verify_request` | `scripts/compact_pair_loop.py:289` | Validates one committed Director verify-request and its exact reviewed range. |
| `validate_report` | `scripts/compact_pair_loop.py:448` | Binds one assigned non-author Operator verdict to that exact request, range, and scope. |

## 4. Runtime Invariants

- Pipeline remains the Codex four-seat governance kernel.
- evidence-ledger is the bound product target for current ledger-routed work.
- The fixed mailbox writer serializes event and cursor publication with one
  Git-common-dir lock. No activation selector or alternate writer exists.
- Durable shared state beats chat memory: git commits, mailbox bodies, capacity
  packets, cursor state, and verification reports are authoritative.
- A conflict-free autonomous seat event may supersede a legacy coordinator route
  only when it binds the exact current parent and next revision. Stale or
  dangling parents, forks, and conflicting same-task tips leave only the
  overlapping task non-actionable until a durable successor resolves them.
- Capacity tools are diagnostics, and preflight is advisory; neither grants
  route authority nor substitutes for review of the actual committed change.
- Live seats start with `scripts/ledger_start_guard.py --seat <seat> --wave 2`
  from Pipeline before entering evidence-ledger.
- Ordinary git and pytest commands use `env -u GIT_INDEX_FILE`.
- Commit, push, merge, cursor consumption, lock actions, pod spend, target
  checkout refresh, production generation, paid API spend, and every other side
  effect are separate authorities. Each requires separately granted user
  authority for the exact effect, executor, target, and scope; a structurally
  complete seat token and any model or provider identity grant no authority.
- Material finding references remain immutable through ownership and review,
  and every accepted report dispositions each carried reference explicitly.
- Behavior-changing acceptance requires actual-diff GO from an assigned
  non-author Operator using both a distinct Operator seat and a different
  system-visible model; changing seats cannot let the same model self-approve.
- Canonical Compact Pair Invariant: `scripts/codex_protocol_model.py`. This
  truth layer intentionally does not restate its lifecycle grammar.
- The optional parent-owned ChatGPT Pro tool uses one Git-common-dir
  `reserved|sent|failed` record, one Browser send, no retry or fallback, and
  grants no protocol or side-effect authority.
- `coordination/bin/send-event` permits verification reports only from Operator
  seats, then sends every mailbox kind through the unchanged fixed finalizer in
  `scripts/mailbox_writer.py`.
- Historical report paths remain immutable evidence and grant no current
  publication authority. Local `.codex/runtime` residue is outside the operative
  scan and is not mutated by protocol verification.
- For adversarial surfaces, the owner assesses plausible abuse classes before
  implementation and preserves material independent findings. Early independent
  enumeration is advisory when useful, not a universal requirement or CLEAR
  gate; actual-diff review by a distinct-seat, different-model non-author Operator remains mandatory.

## 5. Mailbox And Capacity State

Mailbox events live under `coordination/mailbox/sent/`; read cursors live under
`coordination/mailbox/seen/`. The receiving roster comes from
`scripts/protocol_mailbox.py:11` and `scripts/protocol_mailbox.py:17`.

Capacity boards and packets remain available as optional diagnostic evidence;
they keep capacity issues visible but do not grant route authority. Coordinator
route validity comes from route and hard-boundary validation.

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
load-bearing event-kind relationship, and the seat/mailbox registry. Compact-pair
request/report binding is proved by focused protocol tests; smoke does not
substitute for those regressions or an Operator GO.

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
