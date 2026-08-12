# Automatic Seat-Task Routing Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make Pipeline coordinators discover, deduplicate, reuse or automatically create, send to, wait for, and reconcile concrete Codex seat tasks without asking the user to relay prompts.

**Architecture:** Add one provider-specific routing capsule to the canonical Codex protocol model and reference it concisely from the three active coordinator-facing adapters. The change is instruction-backed behavior using existing Codex task tools; it adds no broker, registry, receipt, approval entity, or background service. Focused prompt-sync tests make direct delivery, automatic creation, duplicate suppression, concrete-seat use, and effect-boundary language executable.

**Tech Stack:** Python 3.11+ standard library, pytest, Markdown protocol adapters, existing Codex task tools, and the existing Pipeline four-seat mailbox model.

## Global Constraints

- Source design: `docs/superpowers/specs/2026-07-19-automatic-seat-task-routing-design.md@5b8a6c287b9cf3a85f9512c8903ddbf5cc27eb02`.
- The coordinator remains non-author for behavior-changing production work. A concrete live-seat Codex task reads and follows committed authority before acting.
- Existing compatible seat tasks are reused; a missing, stale, incompatible, or ambiguous seat task is created automatically in the saved local Pipeline project.
- One immutable dispatch identity is trigger path plus full commit, assigned seat, Pipeline checkout, and, for review, exact base/head plus required reviewer model.
- A duplicate in-flight identity is monitored, not resent. A completed identity is reconciled from its committed artifact, not chat narration.
- Never ask the user to copy or relay a seat prompt while Codex task tools are available.
- Parent-scoped subagents remain unable to publish live-seat mailbox events or formal GO; concrete user-visible Codex seat tasks remain the live-seat mechanism.
- Task routing grants no push, merge, reset, rebase, amend, cursor consume, lock, provider, service, database, dependency, ledger-resume, target-mutation, booking, spend, deployment, cleanup, or other external-effect authority.
- Do not add a scheduler, daemon, task broker, persistent registry, receipt, replay token, approval schema, or generated task state.
- Preserve unrelated peer work. Refresh the hot shared tree before every write, stage, commit, or gate decision, and stage explicit pathspecs only.
- Ordinary Git and pytest use `env -u GIT_INDEX_FILE`.
- Because this changes coordinator runtime behavior, run `scripts/ci_smoke.py` and require distinct-seat, different-model, non-author Operator GO on the actual implementation range before acceptance.
- No push, merge, cursor consumption, lock action, provider launch, ledger resume, or other external effect is authorized by this plan.

## File Structure

- `scripts/codex_protocol_model.py`: canonical automatic seat-task routing reference, rules, and renderer.
- `tests/unit/test_protocol_prompt_sync.py`: model coverage, three-surface synchronization, duplicate/no-relay requirements, and authority-boundary assertions.
- `AGENTS.md`: concise repository-level Codex coordinator default.
- `.agents/skills/seat-coordinator/SKILL.md`: concise live coordinator procedure.
- `docs/protocol/codex/continuation.md`: concise Codex continuation behavior.

---

### Task 1: Add the canonical routing capsule and thin adapters

**Files:**
- Modify: `scripts/codex_protocol_model.py:376-383`
- Modify: `scripts/codex_protocol_model.py:631-637`
- Modify: `scripts/codex_protocol_model.py:1060-1080`
- Modify: `tests/unit/test_protocol_prompt_sync.py:307-324`
- Modify: `AGENTS.md:83-100`
- Modify: `.agents/skills/seat-coordinator/SKILL.md:20-44`
- Modify: `docs/protocol/codex/continuation.md:49-84`

**Interfaces:**
- Produces: `AUTOMATIC_TASK_ROUTING_REFERENCE: str`
- Produces: `AUTOMATIC_TASK_ROUTING_RULES: tuple[str, ...]`
- Produces: `render_automatic_task_routing() -> str`
- Consumes: existing `_read()` and `_compact()` prompt-sync helpers
- Preserves: `AUTONOMOUS_SEAT_RULES`, `COORDINATOR_INVARIANTS`, `LIVE_LOOP_STEPS`, all seat/mailbox authority rules, and adapter line budgets

- [ ] **Step 1: Refresh the exact owned scope**

```bash
env -u GIT_INDEX_FILE git log --oneline -5
env -u GIT_INDEX_FILE git status --short --branch -- \
  scripts/codex_protocol_model.py \
  tests/unit/test_protocol_prompt_sync.py \
  AGENTS.md \
  .agents/skills/seat-coordinator/SKILL.md \
  docs/protocol/codex/continuation.md
```

Expected: no unexplained peer edit overlaps the five owned paths. Preserve the Fast-Resume correction and review commits; do not absorb their files or mailbox events.

- [ ] **Step 2: Add failing canonical-model and adapter-sync tests**

Add these definitions after `FAST_RESUME_ADAPTER_SURFACES` in `tests/unit/test_protocol_prompt_sync.py`:

```python
AUTOMATIC_TASK_ROUTING_REFERENCE = (
    "Automatic Seat-Task Routing: scripts/codex_protocol_model.py"
)
AUTOMATIC_TASK_ROUTING_SURFACES = (
    "AGENTS.md",
    ".agents/skills/seat-coordinator/SKILL.md",
    "docs/protocol/codex/continuation.md",
)


def test_automatic_task_routing_model_is_direct_deduplicated_and_effect_free() -> None:
    rendered = _compact(model.render_automatic_task_routing())

    required = (
        "committed immutable trigger",
        "dispatch identity",
        "already in progress",
        "monitor",
        "automatically create",
        "Never ask the user to relay",
        "concrete live-seat Codex task",
        "tooling blocker",
        "grants no external-effect authority",
    )
    for phrase in required:
        assert phrase.casefold() in rendered.casefold(), phrase

    assert "persistent task registry" not in rendered
    assert "parent-scoped subagent may issue GO" not in rendered


def test_automatic_task_routing_adapters_are_thin_and_synced() -> None:
    required = (
        "discover/deduplicate",
        "reuse one compatible task",
        "automatically create a fresh missing task",
        "send the exact trigger",
        "wait",
        "reconcile",
        "Never ask the user to relay a seat prompt",
        "grants no seat or external-effect authority",
    )
    for path in AUTOMATIC_TASK_ROUTING_SURFACES:
        text = _compact(_read(path).replace("`", ""))
        assert text.count(AUTOMATIC_TASK_ROUTING_REFERENCE) == 1, path
        for phrase in required:
            assert phrase.casefold() in text.casefold(), (path, phrase)
```

- [ ] **Step 3: Run the new tests and confirm RED**

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest \
  tests/unit/test_protocol_prompt_sync.py \
  -k 'automatic_task_routing' -q
```

Expected: FAIL because `render_automatic_task_routing()` and the three adapter references do not exist.

- [ ] **Step 4: Add the canonical model capsule**

Add this immediately after `COORDINATOR_INVARIANTS` in `scripts/codex_protocol_model.py`:

```python
AUTOMATIC_TASK_ROUTING_REFERENCE = (
    "Automatic Seat-Task Routing: scripts/codex_protocol_model.py"
)
AUTOMATIC_TASK_ROUTING_RULES = (
    "For a committed immutable trigger naming the next concrete seat, use Codex task tools before returning a prompt to the user.",
    "The dispatch identity is the trigger path and full commit, assigned seat, Pipeline checkout, and for review the exact base/head and required reviewer model.",
    "If the same dispatch identity is already in progress, monitor it; if it completed, reconcile its committed artifact instead of resending it.",
    "Reuse one unambiguous compatible seat task; if none exists or candidates are stale, incompatible, or ambiguous, automatically create a fresh local task in the saved Pipeline project.",
    "Send the exact trigger, wait for the task, reconcile its committed result, and route any correction or next seat without asking the user to relay a prompt.",
    "If Codex task tools are unavailable, preserve the exact trigger and report one concrete tooling blocker without asking the user to relay it.",
    "A concrete live-seat Codex task may exercise only its committed authority; parent-scoped subagents do not publish live-seat events or formal GO, and task routing grants no external-effect authority.",
)
```

Add this immediately after `render_autonomous_seat_contract()`:

```python
def render_automatic_task_routing() -> str:
    """Return the Codex coordinator's direct seat-task transport contract."""
    return AUTOMATIC_TASK_ROUTING_REFERENCE + "\n" + "\n".join(
        f"- {rule}" for rule in AUTOMATIC_TASK_ROUTING_RULES
    )
```

Add `render_automatic_task_routing()` immediately after `render_autonomous_seat_contract()` in the `render_surface_summary()` line list so the canonical summary exposes the rule.

- [ ] **Step 5: Add the same thin adapter paragraph to all three surfaces**

Insert this exact paragraph after the autonomous-seat paragraph in `AGENTS.md`, `.agents/skills/seat-coordinator/SKILL.md`, and `docs/protocol/codex/continuation.md`:

```markdown
Automatic Seat-Task Routing: scripts/codex_protocol_model.py
For a committed next-seat trigger, use Codex task tools to discover/deduplicate,
reuse one compatible task or automatically create a fresh missing task, send
the exact trigger, wait, and reconcile. Never ask the user to relay a seat
prompt. Task routing grants no seat or external-effect authority.
```

Do not add task-tool API schemas, thread IDs, model allowlists, mailbox fields, or a second routing checklist to any adapter.

- [ ] **Step 6: Run the new tests and confirm GREEN**

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest \
  tests/unit/test_protocol_prompt_sync.py \
  -k 'automatic_task_routing' -q
```

Expected: `2 passed`.

- [ ] **Step 7: Run the full prompt-sync regression profile**

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest \
  tests/unit/test_protocol_prompt_sync.py -q
```

Expected: PASS with no line-budget, canonical-model, retired-ceremony, fast-resume, or authority-sync regression.

- [ ] **Step 8: Run repository completion checks**

```bash
env -u GIT_INDEX_FILE .venv/bin/python scripts/check_placeholders.py
env -u GIT_INDEX_FILE .venv/bin/python scripts/ci_smoke.py
env -u GIT_INDEX_FILE git diff --check -- \
  scripts/codex_protocol_model.py \
  tests/unit/test_protocol_prompt_sync.py \
  AGENTS.md \
  .agents/skills/seat-coordinator/SKILL.md \
  docs/protocol/codex/continuation.md
```

Expected: placeholder check passes, smoke prints `OK`, and the diff check is silent.

- [ ] **Step 9: Inspect the actual diff for scope and authority leakage**

```bash
env -u GIT_INDEX_FILE git diff --name-status
env -u GIT_INDEX_FILE git diff --stat
rg -n "push|merge|cursor|lock|provider|ledger resume|spend|external-effect" \
  scripts/codex_protocol_model.py \
  AGENTS.md \
  .agents/skills/seat-coordinator/SKILL.md \
  docs/protocol/codex/continuation.md
```

Confirm that the five owned paths are the only changes, the three adapters contain one thin reference each, automatic creation is explicit, duplicate triggers are monitored, and every effect term remains a negated boundary rather than granted authority.

- [ ] **Step 10: Commit only the owned implementation paths**

```bash
env -u GIT_INDEX_FILE git log --oneline -5
env -u GIT_INDEX_FILE git status --short --branch -- \
  scripts/codex_protocol_model.py \
  tests/unit/test_protocol_prompt_sync.py \
  AGENTS.md \
  .agents/skills/seat-coordinator/SKILL.md \
  docs/protocol/codex/continuation.md
env -u GIT_INDEX_FILE git add \
  scripts/codex_protocol_model.py \
  tests/unit/test_protocol_prompt_sync.py \
  AGENTS.md \
  .agents/skills/seat-coordinator/SKILL.md \
  docs/protocol/codex/continuation.md
env -u GIT_INDEX_FILE git diff --cached --check
env -u GIT_INDEX_FILE git diff --cached --name-status
env -u GIT_INDEX_FILE git commit -m "feat(protocol): route seat tasks automatically"
```

Expected: one local implementation commit containing exactly the five owned paths.

## Completion Gate

After Task 1, the coordinator applies the approved behavior rather than asking the user to relay the review trigger:

1. reuse or automatically create a concrete Director task to publish one canonical committed verify-request binding the actual implementation parent/head, the five allowed paths, `director` plus its actual author model, non-author `operator2`, and a different reviewer model;
2. reuse or automatically create the assigned Operator2 task, send the immutable request exactly once, wait, and reconcile its committed GO/NITS/FAIL report; and
3. accept the change only after fresh focused checks at the exact head and formal Operator GO.

A NITS/FAIL routes directly back to the Director for a narrow correction and a new immutable request. It does not return a prompt to the user or restart preflight. No push, merge, cursor consumption, lock action, provider launch, ledger resume, or external effect follows from GO.
