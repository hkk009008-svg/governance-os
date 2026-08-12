# Coordination Hardening And Subagent Capacity Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Harden Pipeline four-seat coordination gates and make bounded subagent utilization explicit in the high-traffic Codex skills and prompts.

**Architecture:** Keep enforcement in existing protocol tooling: `check_coordination.py` for mailbox artifact quality, `protocol_capacity.py` for task-board route safety, `protocol_doctor.py` for final-claim validation, and `codex_protocol_model.py` as the executable doctrine source. Prompt/skill changes mirror the model and are pinned by unit tests so frequently used skills stay aligned with agent-neutral templates.

**Tech Stack:** Python standard library, pytest, Markdown protocol templates, existing Codex role-agent TOML prompts.

## Global Constraints

- Do not close the current Stage 0 board in this batch.
- Do not push.
- Do not consume coordinator mail.
- Do not edit evidence-ledger product files.
- Do not rewrite the whole capacity-packet schema in one pass.
- Do not require subagents for tiny, tightly coupled, or authority-sensitive no-op checks.
- Use `env -u GIT_INDEX_FILE` for ordinary git and pytest commands.
- End every task report and final response with `Exact Next Trigger`.

---

## File Structure

- Create `tests/unit/test_protocol_capacity.py`: focused tests for capacity route safety, final-claim no-packet enforcement, and subagent authority leakage.
- Modify `scripts/protocol_capacity.py`: reject unsafe route paths, weak route triggers, and subagent authority leakage.
- Modify `scripts/protocol_doctor.py`: add an explicit final-claim mode that requires packets.
- Modify `scripts/check_coordination.py` and `tests/unit/test_check_coordination.py`: reject weak terminal trigger content.
- Modify `scripts/codex_protocol_model.py` and `tests/unit/test_codex_ledger_bridge.py`: add the new capacity test selector and render subagent utilization decision text.
- Create `tests/unit/test_protocol_prompt_sync.py`: pin agent-neutral reviewer template existence and Codex skill path sync.
- Create `docs/templates/agents/reviewer.md`: agent-neutral reviewer template carrying the `reviewer-result/1` schema.
- Modify `.agents/skills/seat-director/SKILL.md` and `.agents/skills/seat-director/r-brief-template.md`: point Codex dispatch guidance at agent-neutral templates.
- Modify `docs/protocol/codex/continuation.md`, `.agents/skills/four-seat-protocol/SKILL.md`, `.agents/skills/seat-coordinator/SKILL.md`, `.agents/skills/seat-operator/SKILL.md`, and `.agents/skills/seat-director/SKILL.md`: require the subagent utilization decision after orientation.

---

### Task 1: Executable Coordination Gates

**Files:**
- Create: `tests/unit/test_protocol_capacity.py`
- Modify: `scripts/protocol_capacity.py`
- Modify: `scripts/protocol_doctor.py`
- Modify: `scripts/check_coordination.py`
- Modify: `tests/unit/test_check_coordination.py`
- Modify: `scripts/codex_protocol_model.py`
- Modify: `tests/unit/test_codex_ledger_bridge.py`

**Interfaces:**
- Consumes: `protocol_capacity.collect_capacity_report(root: Path | str, wave: int) -> CapacityReport`
- Consumes: `protocol_capacity.validate_route(root: Path | str, wave: int, route_path: Path | str) -> RouteValidation`
- Consumes: `protocol_capacity.require_packets(report: CapacityReport) -> CapacityReport`
- Produces: `protocol_doctor --final-claim`, which adds `protocol_capacity_board.py --require-packets` even without `--route`
- Produces: stronger `protocol_capacity._forbidden_side_effects(body: str) -> list[str]`
- Produces: stronger `check_coordination._has_terminal_next_trigger(text: str) -> bool`

- [ ] **Step 1: Write failing capacity tests**

Create `tests/unit/test_protocol_capacity.py` with these tests:

```python
from __future__ import annotations

import json
from pathlib import Path

import protocol_capacity


def _packet(
    *,
    packet_id: str = "coord-test-route",
    owner: str = "coordinator",
    packet_type: str = "coordinator-route",
    status: str = "active",
    cycle: str = "cycle-a",
) -> dict:
    return {
        "id": packet_id,
        "wave": 2,
        "cycle": cycle,
        "owner": owner,
        "packet_type": packet_type,
        "row_ids": ["row-a"],
        "allowed_paths": ["coordination/capacity/packets/", "coordination/mailbox/sent/"],
        "lock_keys": [],
        "dependencies": [],
        "acceptance": ["Route the current board."],
        "done_evidence": [],
        "handoff_artifact": None,
        "next_recipient": "coordinator",
        "status": status,
        "verify_request": None,
        "target_commit": None,
        "commit_range": None,
        "scope_files": ["coordination/mailbox/sent/"],
    }


def _write_packet(root: Path, packet: dict) -> None:
    packet_dir = root / "coordination" / "capacity" / "packets"
    packet_dir.mkdir(parents=True)
    (packet_dir / f"{packet['id']}.json").write_text(
        json.dumps(packet, indent=2),
        encoding="utf-8",
    )


def _write_route(root: Path, name: str, body: str) -> Path:
    sent = root / "coordination" / "mailbox" / "sent"
    sent.mkdir(parents=True)
    path = sent / name
    path.write_text(body, encoding="utf-8")
    return path


def test_require_packets_flags_empty_final_claim(tmp_path: Path):
    report = protocol_capacity.collect_capacity_report(tmp_path, 2)

    required = protocol_capacity.require_packets(report)

    assert [issue["gate"] for issue in required.blocking_issues] == ["G9"]


def test_route_validation_rejects_route_outside_mailbox_sent(tmp_path: Path):
    _write_packet(tmp_path, _packet())
    route = tmp_path / "scratch-coordinator-to-all-coordination.md"
    route.write_text(
        "Task-board: cycle-a\n\n"
        "- coord-test-route\n\n"
        "Join condition: coordinator closes.\n\n"
        "## Exact Next Trigger\n\n"
        "Coordinator sends the next route.\n",
        encoding="utf-8",
    )

    result = protocol_capacity.validate_route(tmp_path, 2, route)

    assert not result.valid
    assert any(issue["gate"] == "G7" and "coordination/mailbox/sent" in issue["message"] for issue in result.blocking_issues)


def test_route_validation_rejects_subagent_authority_leakage(tmp_path: Path):
    _write_packet(tmp_path, _packet())
    route = _write_route(
        tmp_path,
        "2026-07-07T18-10-00Z-coordinator-to-all-coordination.md",
        "Task-board: cycle-a\n\n"
        "- coord-test-route\n\n"
        "This route authorizes a subagent to issue operator GO and consume-events for operator.\n\n"
        "Join condition: coordinator closes.\n\n"
        "## Exact Next Trigger\n\n"
        "Operator sends a verification-report.\n",
    )

    result = protocol_capacity.validate_route(tmp_path, 2, route)

    assert not result.valid
    messages = "\n".join(issue["message"] for issue in result.blocking_issues)
    assert "subagent" in messages
    assert "operator GO" in messages or "consume" in messages
```

- [ ] **Step 2: Write failing trigger-quality tests**

Append to `tests/unit/test_check_coordination.py`:

```python
def test_future_event_with_placeholder_trigger_is_fatal(tmp_path: Path):
    coord = _seed_coordination(tmp_path)
    _write_event(
        coord,
        "2026-07-07T18-05-00Z-director-to-all-status.md",
        "# Director -> All: status\n\n"
        "**When:** 2026-07-07T18:05:00Z · **From:** director\n\n"
        "## Exact Next Trigger\n\n"
        "none\n",
    )

    issues = cc.run(
        coord,
        since="2026-06-11",
        now="2026-07-07T18:06:00Z",
        docs_root=tmp_path / "docs",
    )

    assert [issue for issue in issues if issue.kind == "missing_end_trigger"]
```

- [ ] **Step 3: Verify RED**

Run:

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_protocol_capacity.py tests/unit/test_check_coordination.py -q
```

Expected: at least one failure because route path/subagent authority/placeholder trigger checks are not implemented yet.

- [ ] **Step 4: Implement capacity and trigger gates**

In `scripts/protocol_capacity.py`:

- Add route-path validation in `_validate_route_file()` so `route_path.as_posix()` must include `/coordination/mailbox/sent/` or start with `coordination/mailbox/sent/`.
- Add `Exact Next Trigger` text validation for routes by requiring the body to contain an `Exact Next Trigger` heading with non-placeholder content after it.
- Extend `_forbidden_side_effects()` to detect authorizing subagents to issue GO, send mailbox events, consume cursors, create coordinator routes, push, claim/release locks, start pods, or spend.

Use clear labels such as:

```python
"subagent operator GO"
"subagent mailbox event"
"subagent cursor consume"
"subagent coordinator route"
```

In `scripts/check_coordination.py`:

- Add a weak-trigger regex near the end-trigger constants:

```python
_WEAK_TRIGGER_RE = re.compile(
    r"^(?:none|n/a|not applicable|to be decided|no trigger|same as above)$",
    re.IGNORECASE,
)
```

- In `_has_terminal_next_trigger()`, return `False` if all non-cursor content lines are weak trigger text.

- [ ] **Step 5: Add protocol doctor final-claim mode**

In `scripts/protocol_doctor.py`:

- Add `parser.add_argument("--final-claim", action="store_true", help="require capacity packets for final protocol claims")`.
- If `args.final_claim` is true, append `[py, "scripts/protocol_capacity_board.py", "--wave", str(args.wave), "--require-packets"]` even when `args.route` is absent.
- Avoid duplicating the same command when `args.route` already adds `--require-packets`.

- [ ] **Step 6: Wire verification selector**

In `scripts/codex_protocol_model.py`, add `tests/unit/test_protocol_capacity.py` to the first command in `CODEX_VERIFICATION_COMMANDS`.

In `tests/unit/test_codex_ledger_bridge.py`, add `tests/unit/test_protocol_capacity.py` to `CURRENT_PROTOCOL_TESTS` and remove any stale expectation that treats it as absent.

- [ ] **Step 7: Verify GREEN**

Run:

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_protocol_capacity.py tests/unit/test_check_coordination.py tests/unit/test_codex_ledger_bridge.py -q
env -u GIT_INDEX_FILE .venv/bin/python scripts/protocol_doctor.py --wave 2 --route coordination/mailbox/sent/2026-07-07T17-18-59Z-coordinator-to-all-coordination.md
env -u GIT_INDEX_FILE .venv/bin/python scripts/ci_smoke.py
```

Expected:

- pytest passes.
- `protocol_doctor.py --wave 2 --route ...` may fail if the current historical route lacks the newly required terminal trigger or route shape. If it fails only because the current route is intentionally historical, document that and use unit tests plus `ci_smoke.py` as the merge gate.
- `ci_smoke.py` ends `OK`; existing stale-SHA warnings may remain.

- [ ] **Step 8: Commit Task 1**

Run:

```bash
env -u GIT_INDEX_FILE git add scripts/protocol_capacity.py scripts/protocol_doctor.py scripts/check_coordination.py tests/unit/test_protocol_capacity.py tests/unit/test_check_coordination.py scripts/codex_protocol_model.py tests/unit/test_codex_ledger_bridge.py
env -u GIT_INDEX_FILE git commit -m "feat(protocol): harden coordination gates"
```

---

### Task 2: Prompt And Skill Subagent Capacity Sync

**Files:**
- Create: `tests/unit/test_protocol_prompt_sync.py`
- Create: `docs/templates/agents/reviewer.md`
- Modify: `scripts/codex_protocol_model.py`
- Modify: `docs/protocol/codex/continuation.md`
- Modify: `.agents/skills/four-seat-protocol/SKILL.md`
- Modify: `.agents/skills/seat-director/SKILL.md`
- Modify: `.agents/skills/seat-director/r-brief-template.md`
- Modify: `.agents/skills/seat-operator/SKILL.md`
- Modify: `.agents/skills/seat-coordinator/SKILL.md`

**Interfaces:**
- Consumes: `codex_protocol_model.render_seat_subagent_development() -> str`
- Produces: agent-neutral `docs/templates/agents/reviewer.md`
- Produces: required text `Subagent utilization decision`

- [ ] **Step 1: Write failing prompt-sync tests**

Create `tests/unit/test_protocol_prompt_sync.py`:

```python
from __future__ import annotations

from pathlib import Path

import codex_protocol_model as model


ROOT = Path(__file__).resolve().parents[2]


def _read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_agent_neutral_reviewer_template_exists_with_schema():
    text = _read("docs/templates/agents/reviewer.md")

    assert "schema_version" in text
    assert "reviewer-result/1" in text
    assert '"verdict": "pass | issues | unable_to_verify"' in text
    assert "env -u GIT_INDEX_FILE" in text


def test_codex_director_skill_uses_agent_neutral_templates():
    for path in (
        ".agents/skills/seat-director/SKILL.md",
        ".agents/skills/seat-director/r-brief-template.md",
    ):
        text = _read(path)
        assert "docs/templates/agents/implementer.md" in text
        assert "docs/protocol/agents/orchestration.md" in text
        assert "docs/templates/claude/implementer.md" not in text
        assert "docs/protocol/claude/orchestration.md" not in text


def test_subagent_utilization_decision_is_rendered_and_documented():
    rendered = model.render_seat_subagent_development()
    assert "Subagent utilization decision" in rendered
    assert "direct/no-op because" in rendered

    for path in (
        "docs/protocol/codex/continuation.md",
        ".agents/skills/four-seat-protocol/SKILL.md",
        ".agents/skills/seat-director/SKILL.md",
        ".agents/skills/seat-operator/SKILL.md",
        ".agents/skills/seat-coordinator/SKILL.md",
    ):
        text = _read(path)
        assert "Subagent utilization decision" in text
        assert "direct/no-op because" in text
```

- [ ] **Step 2: Verify RED**

Run:

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_protocol_prompt_sync.py -q
```

Expected: fail because `docs/templates/agents/reviewer.md` does not exist and utilization-decision text is absent.

- [ ] **Step 3: Create agent-neutral reviewer template**

Create `docs/templates/agents/reviewer.md` as an agent-neutral counterpart to `docs/templates/claude/reviewer.md`.

Required sections:

- title: `# Reviewer prompt template — agent-neutral`
- `## Canonical verdict vocabulary`
- `## Independence + verify-before-asserting`
- `## Git hygiene`
- `## RESULT SCHEMA`
- `## Evidence preamble`
- `## Spec reviewer prompt template`
- `## Code quality reviewer prompt template`

The `RESULT SCHEMA` fenced JSON block must include:

```json
{
  "schema_version": "reviewer-result/1",
  "role": "spec | code_quality",
  "verdict": "pass | issues | unable_to_verify",
  "reviewed_commit": "commit under review",
  "reviewed_head": "git rev-parse HEAD value inspected",
  "working_tree_clean": true,
  "commands": [
    {"command": "exact command run", "exit_code": 0, "summary": "literal command summary"}
  ],
  "issues": [
    {"severity": "critical | important | minor", "file": "path", "line": 0,
     "requirement": "enumerated id | unlisted", "finding": "what is wrong"}
  ],
  "commit_trailer": {"present": true,
                     "expected": "required trailer line when one is specified",
                     "observed": "verbatim trailer line or null"},
  "unverifiable_reason": null,
  "blocked": null
}
```

Keep wording agent-neutral: refer to "agent" or "reviewer", not only Claude Code. Preserve the exact verdict enum and `env -u GIT_INDEX_FILE` git hygiene.

- [ ] **Step 4: Repoint Codex director skill dispatch paths**

In `.agents/skills/seat-director/SKILL.md` and `.agents/skills/seat-director/r-brief-template.md`:

- Replace `docs/templates/claude/implementer.md` with `docs/templates/agents/implementer.md`.
- Replace `docs/protocol/claude/orchestration.md` with `docs/protocol/agents/orchestration.md`.
- Leave Claude-specific docs untouched outside Codex-facing skill files.

- [ ] **Step 5: Codify utilization decision**

In `scripts/codex_protocol_model.py`, add to `SEAT_SUBAGENT_DEVELOPMENT_RULES`:

```python
"After live-seat/coordinator orientation, record a Subagent utilization decision: dispatch a bounded helper for a named task, or direct/no-op because the work is small, tightly coupled, authority-sensitive, or already complete.",
```

Mirror this sentence in:

- `docs/protocol/codex/continuation.md`
- `.agents/skills/four-seat-protocol/SKILL.md`
- `.agents/skills/seat-director/SKILL.md`
- `.agents/skills/seat-operator/SKILL.md`
- `.agents/skills/seat-coordinator/SKILL.md`

- [ ] **Step 6: Verify GREEN**

Run:

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_protocol_prompt_sync.py tests/unit/test_codex_ledger_bridge.py -q
env -u GIT_INDEX_FILE .venv/bin/python scripts/ci_smoke.py
```

Expected:

- pytest passes.
- `ci_smoke.py` ends `OK`; existing stale-SHA warnings may remain.

- [ ] **Step 7: Commit Task 2**

Run:

```bash
env -u GIT_INDEX_FILE git add tests/unit/test_protocol_prompt_sync.py docs/templates/agents/reviewer.md scripts/codex_protocol_model.py docs/protocol/codex/continuation.md .agents/skills/four-seat-protocol/SKILL.md .agents/skills/seat-director/SKILL.md .agents/skills/seat-director/r-brief-template.md .agents/skills/seat-operator/SKILL.md .agents/skills/seat-coordinator/SKILL.md
env -u GIT_INDEX_FILE git commit -m "feat(protocol): sync subagent capacity prompts"
```

---

## Final Verification

Run:

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_protocol_capacity.py tests/unit/test_check_coordination.py tests/unit/test_protocol_prompt_sync.py tests/unit/test_codex_ledger_bridge.py -q
env -u GIT_INDEX_FILE .venv/bin/python scripts/ci_smoke.py
env -u GIT_INDEX_FILE git diff --stat HEAD~2..HEAD
```

Expected:

- pytest passes.
- `ci_smoke.py` ends `OK`; pre-existing stale-SHA warnings may remain.
- Diff scope is limited to protocol tooling, protocol tests, docs/templates, skills, and model/doc sync.

## Review And Closeout

- Request a task-scoped review after each task.
- Request a final whole-branch review after both tasks are complete.
- Fix Critical and Important findings before final response.
- Final response must end with:

```markdown
**Exact Next Trigger:** close or reroute the current Stage 0 coordinator board, or start the stale-route freshness follow-up if the board remains intentionally open.
```
