# Seat End-Trigger Enforcement Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Enforce that every future live-seat/coordinator protocol turn ends with an `Exact Next Trigger`.

**Architecture:** Extend the existing coordination linter (`scripts/check_coordination.py`) because it already parses mailbox events and is called by `scripts/ci_smoke.py`. Keep historical mailbox events exempt with a fixed adoption timestamp, then update Codex protocol model/docs/skills so all seats know the rule before emitting new artifacts.

**Tech Stack:** Python standard library, pytest, existing Pipeline protocol docs and skills.

## Global Constraints

- Do not consume coordinator mail.
- Do not push.
- Do not change evidence-ledger product files.
- Do not make old historical mailbox events fail normal smoke unless the validator is explicitly asked to check them.
- Use `env -u GIT_INDEX_FILE` for ordinary git and pytest commands.
- End this implementation turn with an explicit `Exact Next Trigger`.

---

## File Structure

- Create `tests/unit/test_check_coordination.py`: focused unit coverage for the end-trigger validator on synthetic mailbox events.
- Modify `scripts/check_coordination.py`: add terminal-trigger detection and wire it into `run()`.
- Modify `scripts/codex_protocol_model.py`: make the executable protocol model state that every live-seat/coordinator turn ends with `Exact Next Trigger`.
- Modify `docs/protocol/codex/continuation.md`: mirror the operational rule in the Codex continuation guide.
- Modify `.agents/skills/four-seat-protocol/SKILL.md`: add the Codex skill instruction.
- Modify `.agents/skills/seat-director/SKILL.md`, `.agents/skills/seat-operator/SKILL.md`, `.agents/skills/seat-coordinator/SKILL.md`: make role-specific skills repeat the end-trigger rule.
- Modify `docs/superpowers/specs/2026-07-08-seat-end-trigger-enforcement-design.md` only if implementation reveals a stale or ambiguous spec statement.

---

### Task 1: Enforce Terminal `Exact Next Trigger`

**Files:**
- Create: `tests/unit/test_check_coordination.py`
- Modify: `scripts/check_coordination.py`
- Modify: `scripts/codex_protocol_model.py`
- Modify: `docs/protocol/codex/continuation.md`
- Modify: `.agents/skills/four-seat-protocol/SKILL.md`
- Modify: `.agents/skills/seat-director/SKILL.md`
- Modify: `.agents/skills/seat-operator/SKILL.md`
- Modify: `.agents/skills/seat-coordinator/SKILL.md`

**Interfaces:**
- Consumes: `check_coordination.run(coord_root, since, now, git_root, docs_root)`
- Produces: `check_coordination._has_terminal_next_trigger(text: str) -> bool`
- Produces: `check_coordination._check_end_triggers(coord_root: Path, names: list[str], trigger_since: str = END_TRIGGER_ADOPTION_TS) -> list[CoordIssue]`
- Produces: new `CoordIssue.kind == "missing_end_trigger"` with `severity == "FATAL"`

- [ ] **Step 1: Write the failing tests**

Create `tests/unit/test_check_coordination.py`:

```python
from __future__ import annotations

from pathlib import Path

import check_coordination as cc


def _seed_coordination(tmp_path: Path) -> Path:
    coord = tmp_path / "coordination"
    sent = coord / "mailbox" / "sent"
    seen = coord / "mailbox" / "seen"
    sent.mkdir(parents=True)
    seen.mkdir(parents=True)
    for seat in cc.ROLES:
        (seen / f"{seat}.txt").write_text("0", encoding="utf-8")
    return coord


def _write_event(coord: Path, name: str, body: str) -> None:
    (coord / "mailbox" / "sent" / name).write_text(body, encoding="utf-8")


def test_future_live_seat_event_without_terminal_trigger_is_fatal(tmp_path: Path):
    coord = _seed_coordination(tmp_path)
    _write_event(
        coord,
        "2026-07-07T18-01-00Z-director-to-all-status.md",
        "# Director -> All: status\n\n"
        "**When:** 2026-07-07T18:01:00Z · **From:** director\n\n"
        "Body without the required terminal trigger.\n",
    )

    issues = cc.run(
        coord,
        since="2026-06-11",
        now="2026-07-07T18:02:00Z",
        docs_root=tmp_path / "docs",
    )

    fatal = [issue for issue in issues if issue.kind == "missing_end_trigger"]
    assert fatal
    assert fatal[0].severity == "FATAL"
    assert "must end with Exact Next Trigger" in fatal[0].message


def test_future_live_seat_event_with_terminal_trigger_passes(tmp_path: Path):
    coord = _seed_coordination(tmp_path)
    _write_event(
        coord,
        "2026-07-07T18-01-00Z-operator-to-all-verification-report.md",
        "# Operator -> All: verification\n\n"
        "**When:** 2026-07-07T18:01:00Z · **From:** operator\n\n"
        "VERDICT: GO\n\n"
        "## Exact Next Trigger\n\n"
        "Coordinator closes the route or sends a new verify-request.\n\n"
        "Cursor at send: 0\n",
    )

    issues = cc.run(
        coord,
        since="2026-06-11",
        now="2026-07-07T18:02:00Z",
        docs_root=tmp_path / "docs",
    )

    assert not [issue for issue in issues if issue.kind == "missing_end_trigger"]


def test_historical_live_seat_event_before_trigger_adoption_is_exempt(tmp_path: Path):
    coord = _seed_coordination(tmp_path)
    _write_event(
        coord,
        "2026-07-07T17-53-30Z-director-to-coordinator-status.md",
        "# Director -> Coordinator: old status\n\n"
        "**When:** 2026-07-07T17:53:30Z · **From:** director\n\n"
        "Historical body without the new trigger section.\n",
    )

    issues = cc.run(
        coord,
        since="2026-06-11",
        now="2026-07-07T18:02:00Z",
        docs_root=tmp_path / "docs",
    )

    assert not [issue for issue in issues if issue.kind == "missing_end_trigger"]
```

- [ ] **Step 2: Run tests to verify RED**

Run:

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_check_coordination.py -q
```

Expected: FAIL with `AttributeError: module 'check_coordination' has no attribute 'ROLES'` only if imports are not visible in pytest path, or more likely FAIL because `missing_end_trigger` is never produced.

- [ ] **Step 3: Implement the validator**

Modify `scripts/check_coordination.py` near the existing regex constants:

```python
END_TRIGGER_ADOPTION_TS = "2026-07-07T17-58-38Z"
_END_TRIGGER_HEADING_RE = re.compile(
    r"(?im)^(?:#{1,6}\s*)?Exact Next Trigger\s*:?\s*$"
)
_MARKDOWN_HEADING_RE = re.compile(r"(?m)^#{1,6}\s+\S")
_CURSOR_AT_SEND_RE = re.compile(r"(?im)^Cursor at send:\s*\d+\s*$")
```

Add helpers after `_check_events`:

```python
def _has_terminal_next_trigger(text: str) -> bool:
    matches = list(_END_TRIGGER_HEADING_RE.finditer(text))
    if not matches:
        return False
    trigger = matches[-1]
    later_headings = [
        match for match in _MARKDOWN_HEADING_RE.finditer(text)
        if match.start() > trigger.start()
    ]
    if later_headings:
        return False
    tail_lines = text[trigger.end():].splitlines()
    content_lines = []
    for line in tail_lines:
        stripped = line.strip()
        if not stripped:
            continue
        if _CURSOR_AT_SEND_RE.fullmatch(stripped):
            continue
        content_lines.append(stripped)
    return bool(content_lines)


def _check_end_triggers(
    coord_root: Path,
    names: list[str],
    trigger_since: str = END_TRIGGER_ADOPTION_TS,
) -> list[CoordIssue]:
    issues: list[CoordIssue] = []
    sent = coord_root / "mailbox" / "sent"
    for name in names:
        m = _EVENT_NAME_RE.match(name)
        if not m or m.group("ts") < trigger_since:
            continue
        rel = f"mailbox/sent/{name}"
        text = (sent / name).read_text(errors="replace")
        if not _has_terminal_next_trigger(text):
            issues.append(CoordIssue(
                rel,
                "missing_end_trigger",
                "FATAL",
                "live-seat/coordinator event must end with Exact Next Trigger",
            ))
    return issues
```

Wire it into `run()` immediately after `_check_events(...)`:

```python
    issues += _check_end_triggers(coord_root, names)
```

- [ ] **Step 4: Run focused tests to verify GREEN**

Run:

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_check_coordination.py -q
```

Expected: `3 passed`.

- [ ] **Step 5: Update executable protocol model**

Modify `scripts/codex_protocol_model.py`.

In `PAIR_OPERATING_RULES`, replace:

```python
"Every baton handoff is a mailbox artifact, not chat: brief, verify-request, verification-report, or handoff with commit/range, paths, tests, exclusions, and exact next trigger.",
```

with:

```python
"Every baton handoff is a mailbox artifact, not chat: brief, verify-request, verification-report, or handoff with commit/range, paths, tests, exclusions, and exact next trigger.",
"Every live-seat/coordinator turn ends with an `Exact Next Trigger` section naming the next lawful prompt, seat event, standby condition, or blocker.",
```

In `LIVE_LOOP_STEPS`, replace:

```python
"When a full coordinator/live-seat cycle reaches a real completion boundary and assigned tasks are complete, write a durable handoff before transplant or context switch, including fresh git/mailbox/gate/smoke state and the exact next trigger.",
```

with:

```python
"When a full coordinator/live-seat cycle reaches a real completion boundary and assigned tasks are complete, write a durable handoff before transplant or context switch, including fresh git/mailbox/gate/smoke state and the exact next trigger.",
"Before ending any live-seat/coordinator turn, output `Exact Next Trigger` as the final section in the mailbox artifact and user-facing final response.",
```

- [ ] **Step 6: Update protocol docs and skills**

Patch the Pair Operating Contract blocks in:

- `docs/protocol/codex/continuation.md`
- `.agents/skills/four-seat-protocol/SKILL.md`
- `.agents/skills/seat-director/SKILL.md`
- `.agents/skills/seat-operator/SKILL.md`
- `.agents/skills/seat-coordinator/SKILL.md`

Add this bullet immediately after the existing baton-handoff bullet:

```markdown
- Every live-seat/coordinator turn ends with an `Exact Next Trigger` section
  naming the next lawful prompt, seat event, standby condition, or blocker; make
  it the final user-facing section as well as the terminal mailbox/handoff
  section.
```

In `docs/protocol/codex/continuation.md`, also update the handoff wording so:

```markdown
`next trigger`.
```

becomes:

```markdown
`Exact Next Trigger`.
```

- [ ] **Step 7: Run focused and protocol verification**

Run:

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_check_coordination.py tests/unit/test_codex_ledger_bridge.py -q
env -u GIT_INDEX_FILE .venv/bin/python scripts/ci_smoke.py
```

Expected:

- pytest passes.
- `scripts/ci_smoke.py` ends with `OK`.
- Existing stale-SHA warnings may remain unchanged.

- [ ] **Step 8: Inspect diff scope**

Run:

```bash
env -u GIT_INDEX_FILE git diff --stat
env -u GIT_INDEX_FILE git diff -- scripts/check_coordination.py tests/unit/test_check_coordination.py scripts/codex_protocol_model.py docs/protocol/codex/continuation.md .agents/skills/four-seat-protocol/SKILL.md .agents/skills/seat-director/SKILL.md .agents/skills/seat-operator/SKILL.md .agents/skills/seat-coordinator/SKILL.md
```

Expected: only the enforcement test, coordination validator, and protocol wording files changed.

- [ ] **Step 9: Commit implementation**

Run:

```bash
env -u GIT_INDEX_FILE git add scripts/check_coordination.py tests/unit/test_check_coordination.py scripts/codex_protocol_model.py docs/protocol/codex/continuation.md .agents/skills/four-seat-protocol/SKILL.md .agents/skills/seat-director/SKILL.md .agents/skills/seat-operator/SKILL.md .agents/skills/seat-coordinator/SKILL.md
env -u GIT_INDEX_FILE git commit -m "feat(protocol): enforce seat end triggers"
```

Expected: one implementation commit with only the listed files.

- [ ] **Step 10: Final response**

The final response must include:

```markdown
**Exact Next Trigger:** wait for the next live-seat/coordinator mailbox event, or ask me to close the current Stage 0 coordinator board now that trigger enforcement is in place.
```
