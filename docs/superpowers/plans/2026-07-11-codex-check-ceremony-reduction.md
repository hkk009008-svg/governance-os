# Codex Check-Ceremony Reduction Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make ordinary Codex work quiet and risk-proportional while preserving live-seat Git, authority, verification, and side-effect safeguards.

**Architecture:** `scripts/codex_protocol_model.py` owns a four-tier applicability contract mirrored into `AGENTS.md` and the Codex continuation adapter. Codex hook registration becomes failure-only, session smoke is cached by content, and state refresh takes a no-seat fast path while preserving concrete-seat maintenance.

**Tech Stack:** Python 3 standard library, Bash, JSON, pytest, existing Pipeline governance scripts.

## Global Constraints

- Work only in `/Users/hyungkoookkim/Pipeline/.worktrees/reduce-check-ceremony`.
- Preserve the main checkout's unrelated dirty work.
- Use `apply_patch` for manual edits and `env -u GIT_INDEX_FILE` for ordinary Git and pytest commands.
- Do not commit, push, merge, consume mail, claim locks, mutate routes, or change `~/.codex/config.toml` without separate user authorization.
- Keep this a tightly coupled inline implementation; do not dispatch implementation subagents.
- Preserve concrete-seat heartbeat, per-seat index synchronization, operator GO, sandbox approvals, and user-gated side effects.
- Preserve Claude heartbeat and index synchronization; remove only its age-only `.git/index.lock` deletion to match the provider-neutral safety rule.

---

## File Structure

- Modify `scripts/codex_protocol_model.py`: canonical risk tiers and verification-deduplication renderer.
- Modify `tests/unit/test_protocol_prompt_sync.py`: executable model and mirror-sync tests.
- Modify `AGENTS.md`: project-level applicability router and Superpowers fast-path override.
- Modify `docs/protocol/codex/continuation.md`: compact Codex runtime mirror.
- Create `tests/unit/test_codex_hook_lifecycle.py`: hook registration, smoke-cache, and readiness fast-path behavior.
- Modify `.codex/hooks.json`: retain commands but remove success-path status messages.
- Modify `.codex/hooks/session-smoke.sh`: silent passing result and content-key cache.
- Modify `.codex/hooks/update-state.sh`: readiness fast path, throttled skip-worktree scan, and no unconditional lock deletion.
- Modify `.claude/hooks/update-state.sh`: remove only unconditional age-based lock deletion.
- Modify `.gitignore`: ignore the two new hook runtime markers.

---

### Task 1: Canonical Risk-Tier Router

**Files:**
- Modify: `scripts/codex_protocol_model.py`
- Modify: `tests/unit/test_protocol_prompt_sync.py`
- Modify: `AGENTS.md`
- Modify: `docs/protocol/codex/continuation.md`

**Interfaces:**
- Produces: `CODEX_EXECUTION_TIERS: tuple[tuple[str, str, str], ...]`
- Produces: `VERIFICATION_DEDUPLICATION_RULES: tuple[str, ...]`
- Produces: `render_codex_execution_tiers() -> str`
- Consumes: existing `render_start_session_inhabitance()` and `render_surface_summary()`.

- [ ] **Step 1: Add the failing model and mirror test**

```python
def test_codex_execution_tiers_are_model_backed_and_surface_synced():
    expected = (
        ("tier-0-conversational", "self-contained answer", "no repo orientation, implementation skills, mailbox checks, smoke, worktree, or verification commands"),
        ("tier-1-read-only", "repository inspection or evidence-backed report", "smallest scoped read commands; no implementation skills or live-seat checks without an explicit protocol trigger"),
        ("tier-2-local-mutation", "ordinary code, test, config, or documentation edit", "impact analysis, task-relevant implementation discipline, focused tests, and one completion verification pass"),
        ("tier-3-governed-side-effect", "live-seat decision, shared protocol state, or external side effect", "exact mailbox, capacity, independent-verification, and user-authorization gates"),
    )
    assert model.CODEX_EXECUTION_TIERS == expected
    rendered = model.render_codex_execution_tiers()
    for tier in expected:
        assert all(value in rendered for value in tier)
    assert "unchanged HEAD and unchanged relevant paths" in rendered
    assert "same unchanged commit" in rendered
    for path in ("AGENTS.md", "docs/protocol/codex/continuation.md"):
        text = _compact(_read(path))
        for tier, _, _ in expected:
            assert tier in text
        assert "same unchanged commit" in text
```

- [ ] **Step 2: Run the focused test and confirm RED**

```bash
env -u GIT_INDEX_FILE /Users/hyungkoookkim/Pipeline/.venv/bin/python -m pytest tests/unit/test_protocol_prompt_sync.py::test_codex_execution_tiers_are_model_backed_and_surface_synced -q
```

Expected: failure because `CODEX_EXECUTION_TIERS` is absent.

- [ ] **Step 3: Add the model contract and renderer**

Add the exact four tuples from the test and:

```python
VERIFICATION_DEDUPLICATION_RULES = (
    "Tier 2 uses focused tests plus one fresh completion verification pass.",
    "Tier 3 uses implementer evidence plus formal operator Lane V when required, then GO before push.",
    "Do not launch another generic reviewer or repeat Lane V for the same unchanged commit unless it asks a genuinely different, pre-stated question.",
    "Evidence may be reused while HEAD and the relevant paths are unchanged.",
)

def render_codex_execution_tiers() -> str:
    lines = ["Codex Risk-Tier Router:"]
    for tier, trigger, checks in CODEX_EXECUTION_TIERS:
        lines.append(f"- `{tier}`: {trigger}; {checks}.")
    lines.extend(f"- {rule}" for rule in VERIFICATION_DEDUPLICATION_RULES)
    return "\n".join(lines)
```

Include the renderer in `render_start_session_inhabitance()` and add a compact reference to `render_surface_summary()`.

- [ ] **Step 4: Mirror the contract into active Codex prose**

Add a `Codex risk-tier router` section near the Codex-specific preamble in `AGENTS.md` and near mode selection in `docs/protocol/codex/continuation.md`. State that Tier 0 and Tier 1 do not trigger brainstorming, TDD, worktree, plan-writing, implementation review, or completion-verification skills unless the user changes the task into design or mutation work.

- [ ] **Step 5: Run prompt-sync tests and review the task diff**

```bash
env -u GIT_INDEX_FILE /Users/hyungkoookkim/Pipeline/.venv/bin/python -m pytest tests/unit/test_protocol_prompt_sync.py -q
env -u GIT_INDEX_FILE git diff --check -- scripts/codex_protocol_model.py tests/unit/test_protocol_prompt_sync.py AGENTS.md docs/protocol/codex/continuation.md
```

Expected: all tests pass and the diff check is clean.

---

### Task 2: Quiet Codex Hook Registration

**Files:**
- Create: `tests/unit/test_codex_hook_lifecycle.py`
- Modify: `.codex/hooks.json`

**Interfaces:**
- Consumes: Codex hook schema in `.codex/hooks.json`.
- Produces: failure-only hook output while retaining SessionStart, PreToolUse, and PostToolUse commands.

- [ ] **Step 1: Add the failing registration test**

```python
import json
from pathlib import Path

def test_codex_hooks_keep_commands_without_success_status_messages(repo_root: Path):
    config = json.loads((repo_root / ".codex/hooks.json").read_text(encoding="utf-8"))
    commands = [
        hook
        for registrations in config["hooks"].values()
        for registration in registrations
        for hook in registration["hooks"]
    ]
    assert len(commands) == 3
    assert all("command" in hook for hook in commands)
    assert all("statusMessage" not in hook for hook in commands)
    assert any("session-smoke.sh" in hook["command"] for hook in commands)
    assert any("guard-git-index.sh" in hook["command"] for hook in commands)
    assert any("update-state.sh" in hook["command"] for hook in commands)
```

- [ ] **Step 2: Run the test and confirm RED**

```bash
env -u GIT_INDEX_FILE /Users/hyungkoookkim/Pipeline/.venv/bin/python -m pytest tests/unit/test_codex_hook_lifecycle.py::test_codex_hooks_keep_commands_without_success_status_messages -q
```

Expected: failure because the three registrations contain `statusMessage`.

- [ ] **Step 3: Remove only the status-message keys**

Keep the three matchers and commands unchanged. Remove `Running R-START smoke`, `Checking seat git-index safety`, and `Refreshing four-seat state`.

- [ ] **Step 4: Rerun the focused test and confirm GREEN**

Expected: one passing test.

---

### Task 3: Content-Addressed Session-Smoke Cache

**Files:**
- Modify: `tests/unit/test_codex_hook_lifecycle.py`
- Modify: `.codex/hooks/session-smoke.sh`
- Modify: `.gitignore`

**Interfaces:**
- Produces: `.codex/hooks/.last-smoke-pass` containing the current passing content key.
- Consumes: `HEAD`, `main`, `origin/main`, the complete tracked diff, and all untracked non-ignored contents.

- [ ] **Step 1: Add a failing cache behavior test**

Create a temporary Git repo, copy the hook, symlink `.venv/bin/python` to `sys.executable`, and install a tiny `scripts/ci_smoke.py` that increments `.smoke-runs`. Assert:

```python
first = _run([hook], repo)
assert first.returncode == 0
assert first.stdout == ""
assert (repo / ".smoke-runs").read_text() == "1"
second = _run([hook], repo)
assert second.returncode == 0
assert second.stdout == ""
assert (repo / ".smoke-runs").read_text() == "1"
(repo / "AGENTS.md").write_text("changed\n", encoding="utf-8")
third = _run([hook], repo)
assert third.returncode == 0
assert third.stdout == ""
assert (repo / ".smoke-runs").read_text() == "2"
```

- [ ] **Step 2: Run the test and confirm RED**

Expected: the first run prints the current success message and the second run increments the counter again.

- [ ] **Step 3: Implement the content key and pass-only cache**

Use the project Python to hash current `HEAD`, `main`, `origin/main`, the complete `git diff --binary HEAD`, and every untracked non-ignored path plus its bytes. Remove `GIT_INDEX_FILE` from both the helper and smoke execution environments. If the default index contains skip-worktree or assume-unchanged flags, or if key generation otherwise fails, run smoke without caching. Reuse only a non-empty passing key. Atomically write a new key after success, emit no success text, and preserve existing warning output on failure or timeout.

- [ ] **Step 4: Ignore the runtime marker and confirm GREEN**

Add `.codex/hooks/.last-smoke-pass` to `.gitignore`, then run:

```bash
env -u GIT_INDEX_FILE /Users/hyungkoookkim/Pipeline/.venv/bin/python -m pytest tests/unit/test_codex_hook_lifecycle.py -q
```

Expected: all hook-lifecycle tests pass.

---

### Task 4: Readiness Fast Path and Throttled Index Repair

**Files:**
- Modify: `tests/unit/test_codex_hook_lifecycle.py`
- Modify: `tests/unit/test_coordination_tooling.py`
- Modify: `.codex/hooks/update-state.sh`
- Modify: `.claude/hooks/update-state.sh`
- Modify: `.gitignore`

**Interfaces:**
- Produces: `.codex/hooks/.last-skip-worktree-scan-<index>` with `<HEAD> <epoch-seconds>`.
- Consumes: `CODEX_SEAT`, `CODEX_SESSION_ID`, optional session marker, `GIT_INDEX_FILE`, current HEAD, and `STATE.md`.

- [ ] **Step 1: Add failing readiness and throttle tests**

Prove these behaviors:

```python
# Bridge fast path: unchanged HEAD + STATE.md + no seat/index leaves a
# deliberately set skip-worktree bit untouched and preserves an old index.lock.
result = _run([hook], repo)
assert result.returncode == 0
assert _skip_worktree_paths(repo) == ["tracked.txt"]
assert (repo / ".git/index.lock").exists()

# Live seat: an expired scan marker clears the bit and stamps heartbeat.
result = _run([hook], repo, env={"CODEX_SEAT": "director"})
assert result.returncode == 0
assert _skip_worktree_paths(repo) == []
assert (repo / "coordination/presence/director-heartbeat.ts").exists()
```

Keep the existing markerless clean-seat-index test passing for both `.claude` and `.codex` hooks.

- [ ] **Step 2: Run focused tests and confirm RED**

```bash
env -u GIT_INDEX_FILE /Users/hyungkoookkim/Pipeline/.venv/bin/python -m pytest tests/unit/test_codex_hook_lifecycle.py tests/unit/test_coordination_tooling.py::test_update_state_syncs_markerless_clean_seeded_seat_index -q
```

Expected: readiness test fails because the current hook clears the skip-worktree bit and removes an old lock.

- [ ] **Step 3: Implement seat resolution and the readiness fast path**

Add `_resolve_seat()` returning `CODEX_SEAT` or the session marker value. After resolving repository, HEAD, last-state marker, and concrete seat, exit before maintenance when:

```bash
[ -z "$SESSION_SEAT" ]
[ -z "${GIT_INDEX_FILE:-}" ]
[ "$CURRENT" = "$LAST" ]
[ -f STATE.md ]
! _skip_worktree_scan_due
```

Pass the resolved seat into `_stamp_presence()` and delete the unconditional stale-index-lock removal.

- [ ] **Step 4: Throttle skip-worktree scanning**

Add `_skip_worktree_scan_due()` using current HEAD, active index identity, `date +%s`, and `CODEX_SKIP_WORKTREE_SCAN_INTERVAL_SECONDS` defaulting to `60`. Run `_clear_skip_worktree` only when due, then atomically write the index-scoped scan marker. A HEAD mismatch or distinct index always makes the scan due.

- [ ] **Step 5: Ignore the marker and confirm GREEN**

Ignore the per-index `.codex/hooks/.last-skip-worktree-scan*` markers, remove the age-only lock sweep from both provider hooks, run the focused Task 4 command, and expect all selected tests to pass for both provider twins.

---

### Task 5: Integrated Verification and Diff Audit

**Files:**
- Verify all files named by Tasks 1-4.
- Do not modify unrelated files.

- [ ] **Step 1: Run focused suites**

```bash
env -u GIT_INDEX_FILE /Users/hyungkoookkim/Pipeline/.venv/bin/python -m pytest tests/unit/test_codex_hook_lifecycle.py tests/unit/test_protocol_prompt_sync.py tests/unit/test_coordination_tooling.py -q
```

Expected: all selected tests pass.

- [ ] **Step 2: Run governance smoke and syntax checks**

```bash
env -u GIT_INDEX_FILE /Users/hyungkoookkim/Pipeline/.venv/bin/python scripts/ci_smoke.py
env -u GIT_INDEX_FILE /Users/hyungkoookkim/Pipeline/.venv/bin/python -m py_compile scripts/codex_protocol_model.py tests/unit/test_codex_hook_lifecycle.py tests/unit/test_protocol_prompt_sync.py tests/unit/test_coordination_tooling.py
env -u GIT_INDEX_FILE git diff --check
```

Expected: smoke ends in `OK`; syntax and diff checks exit zero.

- [ ] **Step 3: Audit final scope and sibling disposition**

```bash
env -u GIT_INDEX_FILE git status --short
env -u GIT_INDEX_FILE git diff --stat
env -u GIT_INDEX_FILE git diff -- .codex/hooks.json .codex/hooks/session-smoke.sh .codex/hooks/update-state.sh .gitignore scripts/codex_protocol_model.py tests/unit/test_codex_hook_lifecycle.py tests/unit/test_protocol_prompt_sync.py tests/unit/test_coordination_tooling.py AGENTS.md docs/protocol/codex/continuation.md docs/superpowers/specs/2026-07-11-codex-check-ceremony-reduction-design.md docs/superpowers/plans/2026-07-11-codex-check-ceremony-reduction.md
```

Expected: only approved paths, no `.claude/hooks/` mutation, no runtime marker tracked, and no commit created.
