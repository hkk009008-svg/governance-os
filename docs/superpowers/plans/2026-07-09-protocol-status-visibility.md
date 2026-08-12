# Protocol Status Visibility Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Integrate the agent TOML consolidation and add read-only protocol status helpers that reduce startup friction without status/mailbox churn.

**Architecture:** Preserve existing command boundaries and compose existing state collectors. Add only small read-only surfaces: `seat_status.py --all`, monitor note classification, and `scripts/latest_handoff.py`.

**Tech Stack:** Python standard library, pytest, existing protocol scripts, git with `env -u GIT_INDEX_FILE`.

## Global Constraints

- All git and pytest commands use `env -u GIT_INDEX_FILE`.
- Read-only helpers must not consume cursors, send mailbox events, stage files, claim locks, push, start pods, or spend API budget.
- Preserve current single-seat `seat_status.py <seat>` behavior.
- Preserve monitor facts; only downgrade attention classification under closed/no-unread/no-blocker state.
- Concrete seat identity wins for handoffs: `director` reads `HANDOFF-director-*`, `operator2` reads `HANDOFF-operator2-*`, coordinators read `HANDOFF-coordinator-*`.

---

### Task 1: Integrate Completed Agent TOML Consolidation

**Files:**
- Merge from branch: `agent-toml-consolidation`
- Verify: `.codex/agents/agent01.toml`
- Verify: `.codex/agents/agent02.toml`
- Verify: `.codex/agents/agent03.toml`
- Verify: `.codex/agents/agent04.toml`
- Verify: `scripts/codex_protocol_model.py`
- Verify: `tests/unit/test_protocol_prompt_sync.py`
- Verify: `ARCHITECTURE.md`

**Interfaces:**
- Produces `AGENT_EXTENSION_ROUTING_CONTRACT` and `render_agent_extension_routing_contract()`.
- Preserves `main` commit `5302951` SHA-baseline quieting work.

- [ ] **Step 1: Merge the completed branch**

```bash
env -u GIT_INDEX_FILE git merge --no-ff agent-toml-consolidation -m "merge: integrate agent toml consolidation"
```

- [ ] **Step 2: Verify prompt sync**

```bash
env -u GIT_INDEX_FILE /Users/hyungkoookkim/Pipeline/.venv/bin/python -m pytest tests/unit/test_protocol_prompt_sync.py -q
```

- [ ] **Step 3: Verify smoke**

```bash
env -u GIT_INDEX_FILE /Users/hyungkoookkim/Pipeline/.venv/bin/python scripts/ci_smoke.py
```

### Task 2: Add Latest Handoff Selector

**Files:**
- Create: `scripts/latest_handoff.py`
- Create: `tests/unit/test_latest_handoff.py`

**Interfaces:**
- Produces `canonical_pattern(seat: str) -> str`.
- Produces `find_latest_handoff(root: Path, seat: str) -> HandoffSelection`.
- CLI: `scripts/latest_handoff.py <seat> [--root PATH]`.

- [ ] **Step 1: Write failing tests**

Tests must create canonical and noncanonical `docs/HANDOFF-*.md` files in a
temporary root and assert:

```python
selection = latest_handoff.find_latest_handoff(tmp_path, "director")
assert selection.path.name == "HANDOFF-director-2026-07-09-good.md"
assert "HANDOFF-2026-07-09-director-session.md" in selection.warnings[0]
```

- [ ] **Step 2: Run tests to verify RED**

```bash
env -u GIT_INDEX_FILE /Users/hyungkoookkim/Pipeline/.venv/bin/python -m pytest tests/unit/test_latest_handoff.py -q
```

Expected: import or attribute failure because the helper does not exist.

- [ ] **Step 3: Implement helper**

Use `protocol_mailbox.RECEIVING_SEATS` for valid seats. Use file mtime as the
primary newest selector and basename as the deterministic tiebreaker.

- [ ] **Step 4: Verify GREEN and commit**

```bash
env -u GIT_INDEX_FILE /Users/hyungkoookkim/Pipeline/.venv/bin/python -m pytest tests/unit/test_latest_handoff.py -q
env -u GIT_INDEX_FILE git add scripts/latest_handoff.py tests/unit/test_latest_handoff.py
env -u GIT_INDEX_FILE git commit -m "feat(protocol): add latest handoff selector" -- scripts/latest_handoff.py tests/unit/test_latest_handoff.py
```

### Task 3: Add All-Seat Status

**Files:**
- Modify: `.agents/skills/four-seat-protocol/scripts/seat_status.py`
- Create: `tests/unit/test_seat_status_all.py`

**Interfaces:**
- CLI: `seat_status.py --all --wave 2 --commits 3`
- Reuses `latest_handoff.find_latest_handoff()`.

- [ ] **Step 1: Write failing tests**

Tests must call `seat_status.main(["--all", "--wave", "2", "--commits", "1"])`
with monkeypatched collectors and assert output includes every receiving seat,
one HEAD section, capacity-board next actions, and latest handoff lines.

- [ ] **Step 2: Run tests to verify RED**

```bash
env -u GIT_INDEX_FILE /Users/hyungkoookkim/Pipeline/.venv/bin/python -m pytest tests/unit/test_seat_status_all.py -q
```

Expected: argparse failure because `--all` is not supported.

- [ ] **Step 3: Implement `--all`**

Add an argparse mutually exclusive shape that accepts either a single `seat` or
`--all`. Keep the single-seat path as the existing behavior. The all-seat path
prints shared git sections once, then compact mailbox/handoff/heartbeat/capacity
sections.

- [ ] **Step 4: Verify GREEN and commit**

```bash
env -u GIT_INDEX_FILE /Users/hyungkoookkim/Pipeline/.venv/bin/python -m pytest tests/unit/test_seat_status_all.py tests/unit/test_latest_handoff.py -q
env -u GIT_INDEX_FILE git add .agents/skills/four-seat-protocol/scripts/seat_status.py tests/unit/test_seat_status_all.py
env -u GIT_INDEX_FILE git commit -m "feat(protocol): add all-seat status view" -- .agents/skills/four-seat-protocol/scripts/seat_status.py tests/unit/test_seat_status_all.py
```

### Task 4: Downgrade Closed-Cycle Monitor Noise

**Files:**
- Modify: `scripts/mailbox_monitor.py`
- Modify: `tests/unit/test_governance_hardening.py`

**Interfaces:**
- `collect_monitor_state(..., wave: int | None = None)` returns `alerts` and `notes`.
- `render_snapshot()` renders both sections.

- [ ] **Step 1: Write failing tests**

Add a test where all unread counts are `0`, latest broadcast receipts are
unknown, pair heartbeats are stale, capacity board is closed, and coordination
passes. Assert receipt/heartbeat facts remain visible but `alerts` is empty and
`notes` contains the downgraded facts.

- [ ] **Step 2: Run tests to verify RED**

```bash
env -u GIT_INDEX_FILE /Users/hyungkoookkim/Pipeline/.venv/bin/python -m pytest tests/unit/test_governance_hardening.py::test_mailbox_monitor_downgrades_closed_cycle_receipt_and_heartbeat_noise -q
```

Expected: failure because `notes` does not exist and alerts still contain the
closed-cycle facts.

- [ ] **Step 3: Implement downgrade**

Add small helpers that evaluate closed/no-unread/no-blocker state without
mutating repo state. Default behavior without `wave` remains conservative:
existing alerts stay alerts.

- [ ] **Step 4: Verify GREEN and commit**

```bash
env -u GIT_INDEX_FILE /Users/hyungkoookkim/Pipeline/.venv/bin/python -m pytest tests/unit/test_governance_hardening.py -q
env -u GIT_INDEX_FILE git add scripts/mailbox_monitor.py tests/unit/test_governance_hardening.py
env -u GIT_INDEX_FILE git commit -m "feat(protocol): downgrade closed-cycle monitor noise" -- scripts/mailbox_monitor.py tests/unit/test_governance_hardening.py
```

### Task 5: Final Protocol Verification

**Files:**
- Verify: all changed files

- [ ] **Step 1: Run focused protocol suites**

```bash
env -u GIT_INDEX_FILE /Users/hyungkoookkim/Pipeline/.venv/bin/python -m pytest tests/unit/test_latest_handoff.py tests/unit/test_seat_status_all.py tests/unit/test_governance_hardening.py tests/unit/test_protocol_prompt_sync.py tests/unit/test_codex_ledger_bridge.py -q
```

- [ ] **Step 2: Run protocol doctor and smoke**

```bash
env -u GIT_INDEX_FILE /Users/hyungkoookkim/Pipeline/.venv/bin/python scripts/protocol_doctor.py --wave 2
env -u GIT_INDEX_FILE /Users/hyungkoookkim/Pipeline/.venv/bin/python scripts/ci_smoke.py
```

- [ ] **Step 3: Verify read-only status commands**

```bash
env -u GIT_INDEX_FILE /Users/hyungkoookkim/Pipeline/.venv/bin/python .agents/skills/four-seat-protocol/scripts/seat_status.py --all --wave 2 --commits 3
env -u GIT_INDEX_FILE /Users/hyungkoookkim/Pipeline/.venv/bin/python scripts/latest_handoff.py director
env -u GIT_INDEX_FILE /Users/hyungkoookkim/Pipeline/.venv/bin/python scripts/mailbox_monitor.py --once --wave 2
env -u GIT_INDEX_FILE git status --short
```

Expected: commands exit 0 and `git status --short` is clean.
