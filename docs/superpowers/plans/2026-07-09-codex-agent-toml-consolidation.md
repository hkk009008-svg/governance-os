# Codex Agent TOML Consolidation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Consolidate `.codex/agents/agent01.toml` through `.codex/agents/agent04.toml` into distinct, test-backed guardrail extensions while preserving the six core Codex role/specialist agents as the authority surface.

**Architecture:** The executable model owns the extension routing contract, prompt-sync tests enforce it, and the four `agentNN` TOML prompts carry the human-readable routing language. Core role agents remain unchanged unless a test-backed sync defect is discovered.

**Tech Stack:** Python 3 via `.venv/bin/python`, pytest, TOML prompt files, Markdown protocol docs, `env -u GIT_INDEX_FILE` git hygiene.

## Global Constraints

- Preserve unrelated dirty work in the shared tree.
- Use `apply_patch` for manual file edits.
- Use `env -u GIT_INDEX_FILE` for ordinary git and pytest commands.
- Stage and commit only task-owned paths with explicit pathspecs.
- Do not remove or rename any `.codex/agents/*.toml` file.
- Do not weaken `protocol-director`, `protocol-operator`, `protocol-coordinator`, `readiness-bridge`, `lane-v-verifier`, or `money-gate-reviewer`.
- Do not edit production pipeline behavior.
- Do not consume mail, claim locks, push, start pods, or spend paid API budget.

---

## File Structure

- Modify `scripts/codex_protocol_model.py`: add the model-backed extension routing contract and a renderer.
- Modify `tests/unit/test_protocol_prompt_sync.py`: add prompt-sync tests for the routing contract and `agentNN` authority boundary.
- Modify `.codex/agents/agent01.toml`: make it the capacity manager companion.
- Modify `.codex/agents/agent02.toml`: make it the explicit-mode bounded worker.
- Modify `.codex/agents/agent03.toml`: make it the general senior repo worker.
- Modify `.codex/agents/agent04.toml`: make it the read-only protocol auditor/router and remove stale product-specific wording.

---

### Task 1: Model-Backed Extension Routing Contract

**Files:**
- Modify: `scripts/codex_protocol_model.py`
- Modify: `tests/unit/test_protocol_prompt_sync.py`

**Interfaces:**
- Consumes: existing `AGENT_EXTENSION_RULES`, `is_agent_extension_name()`, and `render_agent_extension_summary()`.
- Produces: `AGENT_EXTENSION_ROUTING_CONTRACT: tuple[tuple[str, str, str], ...]` and `render_agent_extension_routing_contract() -> str`.

- [ ] **Step 1: Add failing model tests**

Add this test after `test_subagent_utilization_decision_is_rendered_and_documented()` in `tests/unit/test_protocol_prompt_sync.py`:

```python
def test_agent_extension_routing_contract_is_model_backed():
    expected_contract = (
        (
            "agent01",
            "capacity manager companion",
            "explicit coordinator/cycle capacity-max planning",
        ),
        (
            "agent02",
            "explicit-mode bounded worker",
            "a parent names a concrete mode and allowed write set",
        ),
        (
            "agent03",
            "general senior repo worker",
            "ordinary repo coding or documentation work with protocol awareness",
        ),
        (
            "agent04",
            "read-only protocol auditor/router",
            "read-only protocol diagnosis and route recommendation",
        ),
    )

    assert model.AGENT_EXTENSION_ROUTING_CONTRACT == expected_contract

    rendered = model.render_agent_extension_routing_contract()
    assert "Agent Extension Routing Contract:" in rendered
    for agent, purpose, route_when in expected_contract:
        assert agent in rendered
        assert purpose in rendered
        assert route_when in rendered

    assert "extension output is evidence for the parent" in rendered
    assert "not a mailbox event, cursor advance, operator GO, coordinator route, lock action, push, or spend authorization" in rendered
```

- [ ] **Step 2: Run the focused test and confirm RED**

Run:

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_protocol_prompt_sync.py::test_agent_extension_routing_contract_is_model_backed -q
```

Expected result:

```text
FAILED ... AttributeError: module 'codex_protocol_model' has no attribute 'AGENT_EXTENSION_ROUTING_CONTRACT'
```

- [ ] **Step 3: Add the routing contract to the model**

In `scripts/codex_protocol_model.py`, add this block immediately after `AGENT_EXTENSION_RULES`:

```python
AGENT_EXTENSION_ROUTING_CONTRACT = (
    (
        "agent01",
        "capacity manager companion",
        "explicit coordinator/cycle capacity-max planning",
    ),
    (
        "agent02",
        "explicit-mode bounded worker",
        "a parent names a concrete mode and allowed write set",
    ),
    (
        "agent03",
        "general senior repo worker",
        "ordinary repo coding or documentation work with protocol awareness",
    ),
    (
        "agent04",
        "read-only protocol auditor/router",
        "read-only protocol diagnosis and route recommendation",
    ),
)
```

Then add this function immediately after `render_agent_extension_summary()`:

```python
def render_agent_extension_routing_contract() -> str:
    """Return the routing contract for optional agentNN guardrail extensions."""
    lines = ["Agent Extension Routing Contract:"]
    for agent, purpose, route_when in AGENT_EXTENSION_ROUTING_CONTRACT:
        lines.append(f"- `{agent}`: {purpose}; use for {route_when}.")
    lines.append(
        "extension output is evidence for the parent, not a mailbox event, "
        "cursor advance, operator GO, coordinator route, lock action, push, or "
        "spend authorization"
    )
    return "\n".join(lines)
```

Finally update `render_start_session_inhabitance()` so it prints the new routing contract after the extension summary:

```python
    lines.append(render_agent_extension_summary(agent_names))
    lines.append(render_agent_extension_routing_contract())
```

- [ ] **Step 4: Run the focused test and confirm GREEN**

Run:

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_protocol_prompt_sync.py::test_agent_extension_routing_contract_is_model_backed -q
```

Expected result:

```text
1 passed
```

- [ ] **Step 5: Commit Task 1**

Run:

```bash
env -u GIT_INDEX_FILE git diff --check -- scripts/codex_protocol_model.py tests/unit/test_protocol_prompt_sync.py
env -u GIT_INDEX_FILE git add scripts/codex_protocol_model.py tests/unit/test_protocol_prompt_sync.py
env -u GIT_INDEX_FILE git commit -m "test(codex): codify agent extension routing" -- scripts/codex_protocol_model.py tests/unit/test_protocol_prompt_sync.py
```

Expected staged scope before commit:

```text
M	scripts/codex_protocol_model.py
M	tests/unit/test_protocol_prompt_sync.py
```

---

### Task 2: AgentNN Prompt Consolidation

**Files:**
- Modify: `.codex/agents/agent01.toml`
- Modify: `.codex/agents/agent02.toml`
- Modify: `.codex/agents/agent03.toml`
- Modify: `.codex/agents/agent04.toml`
- Modify: `tests/unit/test_protocol_prompt_sync.py`

**Interfaces:**
- Consumes: `model.AGENT_EXTENSION_ROUTING_CONTRACT` from Task 1.
- Produces: four distinct extension prompts with test-backed canonical jobs and shared no-seat-authority language.

- [ ] **Step 1: Add failing prompt-sync tests**

Add these tests after `test_agent_extension_routing_contract_is_model_backed()` in `tests/unit/test_protocol_prompt_sync.py`:

```python
def test_agentnn_extensions_have_distinct_routing_prompts():
    expected = {
        "agent01": (
            "capacity manager companion",
            "explicit coordinator/cycle capacity-max planning",
            "build all-seat awareness",
        ),
        "agent02": (
            "explicit-mode bounded worker",
            "a parent names a concrete mode and allowed write set",
            "bounded protocol edits, handoffs, mailbox/cursor maintenance, or Codex agent/config edits",
        ),
        "agent03": (
            "general senior repo worker",
            "ordinary repo coding or documentation work with protocol awareness",
            "defaults to readiness-bridge posture when no live role is named",
        ),
        "agent04": (
            "read-only protocol auditor/router",
            "read-only protocol diagnosis and route recommendation",
            "diagnose stale indexes, mailbox drift, routing gaps, gate/readiness evidence, and authority mismatches",
        ),
    }

    assert dict(
        (agent, (purpose, route_when))
        for agent, purpose, route_when in model.AGENT_EXTENSION_ROUTING_CONTRACT
    ) == {
        agent: values[:2]
        for agent, values in expected.items()
    }

    for agent, phrases in expected.items():
        text = _compact(_read(f".codex/agents/{agent}.toml"))
        for phrase in phrases:
            assert phrase in text


def test_agentnn_extensions_keep_no_seat_authority_boundary():
    required_phrases = (
        "extension, not a protocol seat",
        "cannot consume cursors, send mailbox events, issue GO, create coordinator routes, claim locks, push, start pods, or spend paid API budget",
        "authority work routes to `protocol-director`, `protocol-operator`, or `protocol-coordinator`",
        "extension output is evidence for the parent",
    )

    for agent in ("agent01", "agent02", "agent03", "agent04"):
        text = _compact(_read(f".codex/agents/{agent}.toml"))
        for phrase in required_phrases:
            assert phrase in text


def test_agent04_uses_artifact_neutral_capacity_language():
    text = _read(".codex/agents/agent04.toml")

    assert "target proof artifacts" in text
    assert "product-oracle status" not in text
    assert "co-sign/product-oracle review" not in text
```

- [ ] **Step 2: Run the new prompt tests and confirm RED**

Run:

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_protocol_prompt_sync.py::test_agentnn_extensions_have_distinct_routing_prompts tests/unit/test_protocol_prompt_sync.py::test_agentnn_extensions_keep_no_seat_authority_boundary tests/unit/test_protocol_prompt_sync.py::test_agent04_uses_artifact_neutral_capacity_language -q
```

Expected result:

```text
FAILED ... AssertionError
```

- [ ] **Step 3: Update `agent01` canonical role language**

In `.codex/agents/agent01.toml`, replace the opening `Use when...` paragraph with:

```text
Canonical extension role: capacity manager companion.

Use when the parent explicitly asks for `agent01`, asks for active mailbox
situational awareness, or wants explicit coordinator/cycle capacity-max
planning. You build all-seat awareness from mailbox, git, gate, lock, packet,
and verification evidence, then recommend the correct capacity-board shape and
role-agent dispatches.
```

In the same file, add this paragraph after the canonical role paragraph:

```text
You are an extension, not a protocol seat. Authority work routes to
`protocol-director`, `protocol-operator`, or `protocol-coordinator`; proof-only
work routes to `lane-v-verifier` or `money-gate-reviewer`; readiness-only
continuation routes to `readiness-bridge`. Extension output is evidence for the
parent. You cannot consume cursors, send mailbox events, issue GO, create
coordinator routes, claim locks, push, start pods, or spend paid API budget.
```

- [ ] **Step 4: Update `agent02` canonical role language**

In `.codex/agents/agent02.toml`, replace the opening `Use only when...` paragraph with:

```text
Canonical extension role: explicit-mode bounded worker.

Use only when the parent explicitly names `agent02` or asks for an explicit-mode
bounded worker, and the parent prompt names both a concrete mode and an allowed
write set. Valid concrete modes are `director`, `director2`, `operator`,
`operator2`, `coordinator`, and `readiness`. Use this agent for bounded protocol
edits, handoffs, mailbox/cursor maintenance, or Codex agent/config edits.
If no concrete mode or allowed write set is named, stay read-only, report the
missing input, and do not consume cursors, send mailbox events, edit inventory,
claim locks, or modify production files.
```

In the same file, add this paragraph after the canonical role paragraph:

```text
You are an extension, not a protocol seat. Authority work routes to
`protocol-director`, `protocol-operator`, or `protocol-coordinator`; proof-only
work routes to `lane-v-verifier` or `money-gate-reviewer`; readiness-only
continuation routes to `readiness-bridge`. Extension output is evidence for the
parent. You cannot consume cursors, send mailbox events, issue GO, create
coordinator routes, claim locks, push, start pods, or spend paid API budget.
```

- [ ] **Step 5: Update `agent03` canonical role language and git commands**

In `.codex/agents/agent03.toml`, add this paragraph after `You are agent03, a general Codex protocol agent for Pipeline.`:

```text
Canonical extension role: general senior repo worker.

Use for ordinary repo coding or documentation work with protocol awareness. You
default to readiness-bridge posture when no live role is named, and you do not
infer director, operator, or coordinator authority from recent chat context.
```

In the same file, add this paragraph after the canonical role paragraph:

```text
You are an extension, not a protocol seat. Authority work routes to
`protocol-director`, `protocol-operator`, or `protocol-coordinator`; proof-only
work routes to `lane-v-verifier` or `money-gate-reviewer`; readiness-only
continuation routes to `readiness-bridge`. Extension output is evidence for the
parent. You cannot consume cursors, send mailbox events, issue GO, create
coordinator routes, claim locks, push, start pods, or spend paid API budget.
```

Also change the two protocol-orientation git commands so they include `env -u GIT_INDEX_FILE`:

```text
   and `env -u GIT_INDEX_FILE git log --oneline -5` before decisions.
3. For coordinator work, run `seat_status.py coordinator --wave 2`,
   `env -u GIT_INDEX_FILE git log --oneline -5`,
   `env -u GIT_INDEX_FILE .venv/bin/python scripts/wave_gate_check.py 2`, and
   `env -u GIT_INDEX_FILE .venv/bin/python scripts/ci_smoke.py` before reconciliation claims.
```

- [ ] **Step 6: Update `agent04` canonical role language and artifact-neutral terms**

In `.codex/agents/agent04.toml`, replace the opening `Use when...` paragraph with:

```text
Canonical extension role: read-only protocol auditor/router.

Use when the parent asks for `agent04`, protocol readiness, cross-seat routing
advice, mailbox/git hygiene, stale-index diagnosis, or read-only protocol
diagnosis and route recommendation. Diagnose stale indexes, mailbox drift,
routing gaps, gate/readiness evidence, and authority mismatches. Recommend the
right `protocol-*` or read-only specialist agent when authority is required.
```

In the same file, add this paragraph after the canonical role paragraph:

```text
You are an extension, not a protocol seat. Authority work routes to
`protocol-director`, `protocol-operator`, or `protocol-coordinator`; proof-only
work routes to `lane-v-verifier` or `money-gate-reviewer`; readiness-only
continuation routes to `readiness-bridge`. Extension output is evidence for the
parent. You cannot consume cursors, send mailbox events, issue GO, create
coordinator routes, claim locks, push, start pods, or spend paid API budget.
```

In `Capacity-max support`, replace:

```text
  inventory rows, active locks, gate output, product-oracle status, and
  landed-but-unverified diffs.
```

with:

```text
  inventory rows, active locks, gate output, target proof artifacts, and
  landed-but-unverified diffs.
```

Then replace:

```text
  operator Lane V, co-sign/product-oracle review, routing-only, blocked, or
```

with:

```text
  operator Lane V, co-sign or target-proof review, routing-only, blocked, or
```

- [ ] **Step 7: Run the new prompt tests and confirm GREEN**

Run:

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_protocol_prompt_sync.py::test_agentnn_extensions_have_distinct_routing_prompts tests/unit/test_protocol_prompt_sync.py::test_agentnn_extensions_keep_no_seat_authority_boundary tests/unit/test_protocol_prompt_sync.py::test_agent04_uses_artifact_neutral_capacity_language -q
```

Expected result:

```text
3 passed
```

- [ ] **Step 8: Run the full prompt-sync file**

Run:

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_protocol_prompt_sync.py -q
```

Expected result:

```text
passed
```

- [ ] **Step 9: Commit Task 2**

Run:

```bash
env -u GIT_INDEX_FILE git diff --check -- .codex/agents/agent01.toml .codex/agents/agent02.toml .codex/agents/agent03.toml .codex/agents/agent04.toml tests/unit/test_protocol_prompt_sync.py
env -u GIT_INDEX_FILE git add .codex/agents/agent01.toml .codex/agents/agent02.toml .codex/agents/agent03.toml .codex/agents/agent04.toml tests/unit/test_protocol_prompt_sync.py
env -u GIT_INDEX_FILE git commit -m "docs(codex): consolidate agent extension prompts" -- .codex/agents/agent01.toml .codex/agents/agent02.toml .codex/agents/agent03.toml .codex/agents/agent04.toml tests/unit/test_protocol_prompt_sync.py
```

Expected staged scope before commit:

```text
M	.codex/agents/agent01.toml
M	.codex/agents/agent02.toml
M	.codex/agents/agent03.toml
M	.codex/agents/agent04.toml
M	tests/unit/test_protocol_prompt_sync.py
```

---

### Task 3: Acceptance Verification And Handoff

**Files:**
- Read: `docs/superpowers/specs/2026-07-09-codex-agent-toml-consolidation-design.md`
- Verify: `scripts/codex_protocol_model.py`
- Verify: `tests/unit/test_protocol_prompt_sync.py`
- Verify: `.codex/agents/agent01.toml`
- Verify: `.codex/agents/agent02.toml`
- Verify: `.codex/agents/agent03.toml`
- Verify: `.codex/agents/agent04.toml`

**Interfaces:**
- Consumes: Task 1 model contract and Task 2 prompt changes.
- Produces: evidence that the implementation satisfies the approved spec.

- [ ] **Step 1: Run the approved spec's minimum verification**

Run:

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_protocol_prompt_sync.py -q
env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_codex_ledger_bridge.py tests/unit/test_protocol_doc_integrity.py -q
env -u GIT_INDEX_FILE .venv/bin/python scripts/ci_smoke.py
```

Expected result:

```text
tests/unit/test_protocol_prompt_sync.py passes
tests/unit/test_codex_ledger_bridge.py and tests/unit/test_protocol_doc_integrity.py pass
ci_smoke.py prints OK
```

- [ ] **Step 2: Confirm no stale product-specific wording remains in `agent04`**

Run:

```bash
rg -n "product-oracle status|co-sign/product-oracle review" .codex/agents/agent04.toml
```

Expected result:

```text
no matches
```

- [ ] **Step 3: Confirm the final changed scope**

Run:

```bash
env -u GIT_INDEX_FILE git show --stat --oneline HEAD
env -u GIT_INDEX_FILE git status --short
```

Expected result:

```text
HEAD shows the Task 2 prompt consolidation commit.
git status may still show unrelated pre-existing WIP, but no staged files remain from this plan.
```

- [ ] **Step 4: Record the final implementation summary**

In the final response, report:

```text
- model contract added: AGENT_EXTENSION_ROUTING_CONTRACT and renderer
- prompt-sync tests added for agentNN distinct roles and no-seat-authority boundary
- agent01 through agent04 rewritten to distinct extension roles
- verification commands and outcomes
- unrelated dirty-tree files left untouched
```

No commit is required for Step 4 because it is the user-facing closeout.
