# Codex Agent TOML Consolidation Design

## Goal

Make `.codex/agents/*.toml` easier to route, safer to delegate to, and more
effective for full-capacity four-seat work. The consolidation should reduce
overlap among optional `agentNN` guardrail extensions while preserving the six
core role/specialist agents as the authority surface.

## Context

The current agent set has ten TOML modules:

- Core authority agents: `protocol-director`, `protocol-operator`, and
  `protocol-coordinator`.
- Core read-only agents: `readiness-bridge`, `lane-v-verifier`, and
  `money-gate-reviewer`.
- Optional guardrail extensions: `agent01`, `agent02`, `agent03`, and
  `agent04`.

The core role agents are already well-scoped and prompt-sync tests cover many
of their load-bearing phrases. The extension agents are useful but overlap:
several can orient protocol state, discuss capacity, and warn about authority
boundaries. That overlap makes parent routing less deterministic and weakens
the capacity/capability gain from having multiple agents.

## Design

### Layered Agent Taxonomy

Keep the six core agents as the only canonical role/specialist surface:

- `protocol-director`: explicit director/director2 authority for briefs,
  implementation routing, co-sign decisions, director-owned fixes, and
  verify-requests.
- `protocol-operator`: explicit operator/operator2 authority for Lane V,
  doc-sync when routed, evidence checks, and final GO/NITS/FAIL reports.
- `protocol-coordinator`: explicit coordinator authority for all-scope
  reconciliation, routing, capacity boards, no-op reports, and closeout
  evidence.
- `readiness-bridge`: read-only orientation. It never upgrades itself into a
  live seat or coordinator.
- `lane-v-verifier`: read-only cold-context verification helper for landed
  diffs or ranges.
- `money-gate-reviewer`: read-only specialist reviewer for spend, budget, cost
  accumulator, and silent gate-degradation risks.

Treat every `agentNN.toml` file as an extension, not a role. An extension can
add diagnosis, routing advice, preparation, or bounded execution support, but
it cannot become a seat, consume a cursor, send a mailbox event, issue GO,
claim locks, push, spend budget, or create coordinator routes by itself.

### Extension Role Split

Make each `agentNN` extension distinct enough that a parent prompt can choose
one without ambiguity:

- `agent01`: capacity manager companion. It builds all-seat awareness, reads
  mailbox/gate/lock/git evidence, recommends capacity-board shape, and names
  the correct role-agent dispatches. It is the default extension for explicit
  coordinator/cycle capacity-max planning.
- `agent02`: explicit-mode bounded worker. It only runs when the parent names
  a concrete mode (`director`, `director2`, `operator`, `operator2`,
  `coordinator`, or `readiness`) and an allowed write set. It is the best
  helper for bounded protocol edits, handoffs, mailbox/cursor maintenance, or
  Codex agent/config edits.
- `agent03`: general senior repo worker. It handles ordinary repo coding or
  docs tasks with protocol awareness. If no live role is named, it defaults to
  readiness-bridge posture and does not infer seat authority.
- `agent04`: read-only protocol auditor/router. It diagnoses stale indexes,
  mailbox drift, routing gaps, gate/readiness evidence, and authority
  mismatches. It recommends the right `protocol-*` or read-only specialist
  agent when authority is required.

### Routing Contract

Add an explicit routing contract to the executable model and prompt tests:

- Authority work routes to `protocol-director`, `protocol-operator`, or
  `protocol-coordinator`.
- Proof-only work routes to `lane-v-verifier` or `money-gate-reviewer`.
- Readiness-only continuation routes to `readiness-bridge`.
- Capacity planning and all-seat situational awareness can route to `agent01`.
- Bounded explicit-mode helper work can route to `agent02`.
- Ordinary repo implementation or documentation work can route to `agent03`.
- Protocol diagnosis and route recommendation can route to `agent04`.

The parent seat or coordinator still owns final synthesis and any durable
protocol action. Extension output is evidence for the parent, not a mailbox
event, cursor advance, operator GO, coordinator route, lock action, push, or
spend authorization.

### Prompt Changes

Edit only the extension prompts and model/tests in the first implementation
pass:

- `.codex/agents/agent01.toml`
- `.codex/agents/agent02.toml`
- `.codex/agents/agent03.toml`
- `.codex/agents/agent04.toml`
- `scripts/codex_protocol_model.py`
- `tests/unit/test_protocol_prompt_sync.py`

Do not rewrite the six core agents unless a test-backed drift is discovered.
Avoid touching unrelated live WIP in protocol capacity files, mailbox packets,
or existing prompt-sync changes that are not part of this task.

## Acceptance

- `scripts/codex_protocol_model.py` exposes a compact extension routing
  contract for `agent01` through `agent04`.
- Prompt-sync tests assert that `agentNN` modules remain guardrail extensions
  and never replace core role agents.
- Prompt-sync tests assert each extension's distinct canonical job:
  `agent01` capacity manager companion, `agent02` explicit-mode bounded worker,
  `agent03` general senior repo worker, and `agent04` read-only protocol
  auditor/router.
- Prompt-sync tests assert the shared no-seat-authority boundary for all
  `agentNN` extensions.
- The four extension prompts contain less ambiguous routing language and direct
  authority work back to the core role agents.
- Orientation commands in extension prompts consistently use
  `env -u GIT_INDEX_FILE` for ordinary git commands.
- `agent04` uses target-proof or artifact-neutral wording instead of stale
  product-specific terms such as `product-oracle status`.

## Non-Goals

- Do not remove any `.codex/agents/*.toml` file in this pass.
- Do not rename agent files.
- Do not weaken the six core role/specialist agents.
- Do not let `agentNN` extensions inherit seat, mailbox, cursor, GO, route,
  lock, push, pod-spend, or paid-API-spend authority.
- Do not consolidate by copying one large prompt into every agent.
- Do not edit production pipeline behavior.
- Do not consume mail, claim locks, push, or spend budget.

## Verification

The implementation pass should run at minimum:

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_protocol_prompt_sync.py -q
env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_codex_ledger_bridge.py tests/unit/test_protocol_doc_integrity.py -q
env -u GIT_INDEX_FILE .venv/bin/python scripts/ci_smoke.py
```

If unrelated dirty-tree WIP prevents a clean commit, stage and commit only the
files listed in the implementation pass with explicit pathspecs.
