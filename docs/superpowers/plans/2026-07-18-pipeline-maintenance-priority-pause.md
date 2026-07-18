# Pipeline Maintenance Priority Pause Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Park the untouched evidence-ledger checkpoint, replace fragile handoff `mtime` selection with deterministic HEAD-backed Git-introduction chronology, correct two verified scan cleanups, and classify the sandbox claim before ledger resumption.

**Architecture:** Pipeline remains the governance kernel and evidence-ledger remains untouched. Director2 defines the adversarial handoff contract while Operator2 independently reproduces the sandbox report; Director then produces one cleanup commit and one handoff-selector commit, and the non-author Operator verifies the cumulative range. A confirmed `send-event` repository defect stops at a separate security-sensitive route rather than entering this implementation range.

**Tech Stack:** Python 3.14, Git CLI, pytest, Pipeline fixed mailbox writer, Wave-2 capacity and protocol gates.

## Global Constraints

- Binding design: `docs/superpowers/specs/2026-07-18-pipeline-maintenance-priority-pause-design.md` at or after correction commit `5598b4b`.
- Pipeline Git commands and pytest commands use `env -u GIT_INDEX_FILE`.
- No evidence-ledger file, target worktree, normal checkout, database, dependency, provider, business data, or `web/` path may be modified.
- Coordinator parks the five ledger packets as user-priority blocked; it does not mark them done, excepted, failed, or verified.
- The handoff selector is an authority-orientation surface: R-INDEPENDENCE design-time preflight and final non-author review are mandatory.
- `coordination/bin/send-event` remains read-only investigation scope. A confirmed repository defect requires a new design, plan, route, implementation commit, and Operator verdict before ledger resumption.
- Filesystem `mtime`, Git commit wall-clock time, filename-day order, and uncommitted handoff bytes are never chronology authority.
- No push, merge, remote-ref update, cursor consume, lock action, deployment, pod action, paid spend, cleanup, reset, rebase, amend, or scope widening is authorized.

---

## File Responsibility Map

- `scripts/latest_handoff.py`: discover canonical same-seat handoffs and select the newest durable HEAD-backed artifact by introducing-commit topology plus bounded legacy metadata tie-breaking.
- `tests/unit/test_latest_handoff.py`: hermetic temporary-Git-repository tests for chronology, metadata compatibility, dirty/untracked exclusion, warnings, aliases, and CLI behavior.
- `scripts/bus_unread.py`: retain behavior; correct only the stale non-vacuity test citation.
- `tests/unit/test_keys.py`: retain behavior; replace direct `.__len__()` use with `len()`.
- `coordination/bin/send-event`: read-only during this plan.
- `tests/unit/test_coordination_tooling.py`: exact sandbox reproduction selector; unchanged during this plan.
- `coordination/capacity/packets/`: coordinator-owned pause and maintenance packets, outside Director implementation scope.
- `coordination/mailbox/sent/`: fixed-writer route, findings, verify-request, and verification-report artifacts owned by their concrete seats.

### Task 1: Director2 Adversarial Handoff Preflight

**Files:**
- Read: `scripts/latest_handoff.py`
- Read: `tests/unit/test_latest_handoff.py`
- Read: `docs/HANDOFF-*.md`
- Create through fixed writer: one `coordination/mailbox/sent/*-director2-to-coordinator-findings.md`

**Interfaces:**
- Consumes: corrected design commit `5598b4b`, the committed maintenance route, and the complete canonical handoff corpus at the routed HEAD.
- Produces: one committed findings event with corpus grammar, abuse cases, exact test names, contradictions, and disposition `CLEAR` or `BLOCKED`; Director depends on `CLEAR`.

- [ ] **Step 1: Refresh live seat and route state**

Run the exact Director2 startup block printed by the committed maintenance route, then confirm the routed Pipeline HEAD and clean shared index:

```bash
env -u GIT_INDEX_FILE git rev-parse HEAD
env -u GIT_INDEX_FILE git status --short --branch
```

Expected: the route's exact HEAD and no ambient staged or tracked work.

- [ ] **Step 2: Inventory canonical metadata grammar**

Run:

```bash
find docs -maxdepth 1 -type f \( -name 'HANDOFF-director-*.md' -o -name 'HANDOFF-director2-*.md' -o -name 'HANDOFF-operator-*.md' -o -name 'HANDOFF-operator2-*.md' -o -name 'HANDOFF-coordinator-*.md' \) -print0 | while IFS= read -r -d '' handoff_path; do metadata_line=$(sed -n '1,20p' "$handoff_path" | rg -n '^(When|Created|Date): ' || true); printf '%s\t%s\n' "${handoff_path##*/}" "$metadata_line"; done | sort
```

Expected: only `When:`, `Created:`, and `Date:` fields, using full UTC or date-only values. Any additional legitimate grammar is a `BLOCKED` design contradiction.

- [ ] **Step 3: Inventory introducing commits and same-commit ties**

Run:

```bash
find docs -maxdepth 1 -type f \( -name 'HANDOFF-director-*.md' -o -name 'HANDOFF-director2-*.md' -o -name 'HANDOFF-operator-*.md' -o -name 'HANDOFF-operator2-*.md' -o -name 'HANDOFF-coordinator-*.md' \) -print0 | while IFS= read -r -d '' handoff_path; do introducing_commit=$(env -u GIT_INDEX_FILE git log --diff-filter=A --follow --format='%H' -- "$handoff_path" | tail -1); printf '%s\t%s\n' "${handoff_path##*/}" "$introducing_commit"; done | sort -k2,2 -k1,1
```

Expected: every canonical tracked path has one reachable introducing commit; same-commit coordinator and cross-seat introductions are named explicitly.

- [ ] **Step 4: Bind acceptance tests**

The findings event must require these exact test functions:

```text
test_canonical_pattern_uses_concrete_seat_identity_and_coordinator_alias
test_introduction_topology_wins_over_inverted_mtime
test_same_introducing_commit_uses_full_legacy_metadata
test_same_introducing_commit_uses_basename_with_visible_warning_when_metadata_ties
test_date_only_and_filename_mismatch_remain_compatible_with_warning
test_untracked_and_head_divergent_candidates_are_excluded
test_symlink_candidate_is_excluded
test_git_unavailable_returns_no_selection_with_warning
test_main_prints_selected_path_and_all_warnings
test_main_reports_no_valid_head_backed_handoff
```

Expected: the findings explain the non-vacuous mutation for each ordering test: replacing introduction rank with `mtime` must flip the first test, and accepting dirty/untracked bytes must flip the exclusion test.

- [ ] **Step 5: Publish and commit the preflight**

Use the fixed writer with sender `director2`, recipient `coordinator`, and kind `findings`. The body must contain the routed HEAD, commands and results, corpus grammar, abuse cases, exact tests, `CLEAR` or `BLOCKED`, and excluded effects. Inspect the staged path, then commit only the generated findings file with an explicit pathspec.

Expected: one metadata-only Director2 commit; no implementation or test file changes.

### Task 2: Operator2 Sandbox Reproduction And Classification

**Files:**
- Read: `coordination/bin/send-event`
- Read: `tests/unit/test_coordination_tooling.py`
- Create through fixed writer: one `coordination/mailbox/sent/*-operator2-to-coordinator-findings.md`

**Interfaces:**
- Consumes: committed maintenance route, exact Pipeline HEAD, managed sandbox profile, and approved evidence-gated policy.
- Produces: one committed `repository-defect`, `environment-policy`, or `unable-to-verify` classification with exact reproduction evidence; it never issues GO/NITS/FAIL.

- [ ] **Step 1: Refresh live seat and environment identity**

Run the exact Operator2 startup block printed by the route, then:

```bash
env -u GIT_INDEX_FILE git rev-parse HEAD
env -u GIT_INDEX_FILE git status --short --branch
uname -a
.venv/bin/python --version
git --version
/bin/zsh --version
```

Expected: exact routed HEAD, clean tracked state, and concrete platform versions.

- [ ] **Step 2: Run the smallest exact reproduction**

Run:

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_coordination_tooling.py::test_send_event_stages_ordinary_event_through_fixed_finalizer -q -p no:cacheprovider
```

Expected: record the literal exit status and output. Do not convert a sandbox denial into a product failure or a pass.

- [ ] **Step 3: Run the complete writer boundary file**

Run:

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_coordination_tooling.py -q -p no:cacheprovider
```

Expected: record the exact pass count or every failing node, syscall, path, errno, stdout, stderr, and exit status.

- [ ] **Step 4: Classify without changing source**

Use these binding rules:

```text
repository-defect: identical supported-profile execution fails because repository code chooses an unusable path or violates its documented platform contract.
environment-policy: managed sandbox denies /tmp, Git common-dir locking, or another resource while the identical supported-profile selector passes unchanged.
unable-to-verify: the comparison profile is unavailable or the failing syscall/path cannot be isolated exactly.
```

Expected: `conftest.py` `TMPDIR` injection and blanket bypass instructions are explicitly rejected as remedies.

- [ ] **Step 5: Publish and commit the classification**

Use the fixed writer with sender `operator2`, recipient `coordinator`, and kind `findings`. Commit only the generated event. If the disposition is `repository-defect`, state that ledger resume is blocked on a separate security-sensitive writer design and route; do not propose or author the code fix in this task.

### Task 3: Director Non-Behavioral Cleanup Commit

**Files:**
- Modify: `scripts/bus_unread.py:54-56`
- Modify: `tests/unit/test_keys.py:27`
- Test: `tests/unit/test_threeway_activation_scripts.py::test_bus_unread_script`
- Test: `tests/unit/test_keys.py`

**Interfaces:**
- Consumes: committed maintenance route and a `CLEAR` Director2 findings event.
- Produces: one behavior-neutral two-path cleanup commit; Task 4 uses its HEAD as parent.

- [ ] **Step 1: Refresh Director state and dependency**

Run the exact Director startup block printed by the route. Read the Director2 findings body and stop unless it is `CLEAR`. Refresh Git immediately before editing:

```bash
env -u GIT_INDEX_FILE git log --oneline -3
env -u GIT_INDEX_FILE git status --short --branch
```

Expected: clean tracked state and Director2's committed findings in history.

- [ ] **Step 2: Correct the unread-floor citation**

Replace only the stale two-line citation so the comment reads:

```python
        # "status.py NEVER hangs" contract. The seq gate lives in iter_events_since (pinned
        # non-vacuous in test_threeway_activation_scripts.py::test_bus_unread_script); here
        # we apply only the bus_id+addressee domain filters.
```

Expected: no executable statement changes in `scripts/bus_unread.py`.

- [ ] **Step 3: Replace direct dunder length use**

Change the assertion to:

```python
    assert len(bytes.fromhex(pub_hex)) == 32
```

Expected: no other line in `tests/unit/test_keys.py` changes.

- [ ] **Step 4: Run focused verification**

Run:

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_threeway_activation_scripts.py -k test_bus_unread_script -q -p no:cacheprovider
env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_keys.py -q -p no:cacheprovider
env -u GIT_INDEX_FILE git diff --check
```

Expected: both pytest commands pass and diff check is silent.

- [ ] **Step 5: Commit exact cleanup scope**

Run:

```bash
env -u GIT_INDEX_FILE git add -- scripts/bus_unread.py tests/unit/test_keys.py
env -u GIT_INDEX_FILE git diff --cached --name-status
env -u GIT_INDEX_FILE git commit -m "chore(protocol): correct scan cleanup findings" -- scripts/bus_unread.py tests/unit/test_keys.py
```

Expected: exactly two modified paths in one commit.

### Task 4: Director Deterministic Handoff Selector

**Files:**
- Modify: `scripts/latest_handoff.py`
- Modify: `tests/unit/test_latest_handoff.py`

**Interfaces:**
- Consumes: `canonical_pattern(seat: str) -> str`, `HandoffSelection`, the Task-3 cleanup HEAD, and the exact Director2 acceptance list.
- Produces: `find_latest_handoff(root: Path, seat: str) -> HandoffSelection` with HEAD-backed topological selection and deterministic warnings; public signatures remain unchanged.

- [ ] **Step 1: Replace the test module with the exact Git-backed acceptance suite**

Replace `tests/unit/test_latest_handoff.py` with this complete content:

```python
from __future__ import annotations

import os
from pathlib import Path
import subprocess

import pytest

import latest_handoff


def _git(root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(root), *args],
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    return result.stdout.strip()


def _init_repo(root: Path) -> Path:
    docs = root / "docs"
    docs.mkdir(parents=True)
    _git(root, "init", "-q")
    _git(root, "config", "user.email", "test@example.invalid")
    _git(root, "config", "user.name", "Test User")
    (root / ".gitignore").write_text("\n", encoding="utf-8")
    _git(root, "add", ".gitignore")
    _git(root, "commit", "-q", "-m", "chore: initialize")
    return docs


def _commit_handoff(root: Path, name: str, metadata: str, *, message: str) -> Path:
    path = root / "docs" / name
    path.write_text(f"# {name}\n\n{metadata}\n", encoding="utf-8")
    _git(root, "add", f"docs/{name}")
    _git(root, "commit", "-q", "-m", message)
    return path


def test_canonical_pattern_uses_concrete_seat_identity_and_coordinator_alias():
    assert latest_handoff.canonical_pattern("director") == "HANDOFF-director-*.md"
    assert latest_handoff.canonical_pattern("operator2") == "HANDOFF-operator2-*.md"
    assert latest_handoff.canonical_pattern("coordinator") == "HANDOFF-coordinator-*.md"
    assert latest_handoff.canonical_pattern("coordinator2") == "HANDOFF-coordinator-*.md"


def test_introduction_topology_wins_over_inverted_mtime(tmp_path: Path):
    _init_repo(tmp_path)
    older = _commit_handoff(
        tmp_path,
        "HANDOFF-director-2026-07-08-older.md",
        "When: 2026-07-08T10:00:00Z",
        message="docs: older handoff",
    )
    newer = _commit_handoff(
        tmp_path,
        "HANDOFF-director-2026-07-09-newer.md",
        "When: 2026-07-09T10:00:00Z",
        message="docs: newer handoff",
    )
    os.utime(older, (400, 400))
    os.utime(newer, (100, 100))

    selection = latest_handoff.find_latest_handoff(tmp_path, "director")

    assert selection.path == newer


def test_same_introducing_commit_uses_full_legacy_metadata(tmp_path: Path):
    docs = _init_repo(tmp_path)
    early = docs / "HANDOFF-coordinator-2026-07-08-early.md"
    late = docs / "HANDOFF-coordinator-2026-07-08-late.md"
    early.write_text("# early\n\nDate: 2026-07-08T03:00:00Z\n", encoding="utf-8")
    late.write_text("# late\n\nCreated: 2026-07-08T04:00:00Z\n", encoding="utf-8")
    _git(tmp_path, "add", "docs")
    _git(tmp_path, "commit", "-q", "-m", "docs: same commit handoffs")

    selection = latest_handoff.find_latest_handoff(tmp_path, "coordinator2")

    assert selection.path == late


def test_same_introducing_commit_uses_basename_with_visible_warning_when_metadata_ties(
    tmp_path: Path,
):
    docs = _init_repo(tmp_path)
    low = docs / "HANDOFF-operator2-2026-07-09-alpha.md"
    high = docs / "HANDOFF-operator2-2026-07-09-zulu.md"
    low.write_text("# low\n\nWhen: 2026-07-09\n", encoding="utf-8")
    high.write_text("# high\n\nDate: 2026-07-09\n", encoding="utf-8")
    _git(tmp_path, "add", "docs")
    _git(tmp_path, "commit", "-q", "-m", "docs: tied handoffs")

    selection = latest_handoff.find_latest_handoff(tmp_path, "operator2")

    assert selection.path == high
    assert any("basename tiebreak" in warning for warning in selection.warnings)


def test_date_only_and_filename_mismatch_remain_compatible_with_warning(tmp_path: Path):
    _init_repo(tmp_path)
    selected = _commit_handoff(
        tmp_path,
        "HANDOFF-operator2-2026-07-09-compatible.md",
        "When: 2026-07-08",
        message="docs: compatible legacy handoff",
    )

    selection = latest_handoff.find_latest_handoff(tmp_path, "operator2")

    assert selection.path == selected
    assert any("filename date 2026-07-09 disagrees" in item for item in selection.warnings)


def test_invalid_metadata_remains_candidate_but_loses_a_same_commit_tie(tmp_path: Path):
    docs = _init_repo(tmp_path)
    valid = docs / "HANDOFF-director2-2026-07-09-valid.md"
    invalid = docs / "HANDOFF-director2-2026-07-09-zulu.md"
    valid.write_text("# valid\n\nWhen: 2026-07-09\n", encoding="utf-8")
    invalid.write_text("# invalid\n\nWhen: someday\n", encoding="utf-8")
    _git(tmp_path, "add", "docs")
    _git(tmp_path, "commit", "-q", "-m", "docs: mixed metadata")

    selection = latest_handoff.find_latest_handoff(tmp_path, "director2")

    assert selection.path == valid
    assert any("unusable metadata" in item for item in selection.warnings)


def test_untracked_and_head_divergent_candidates_are_excluded(tmp_path: Path):
    docs = _init_repo(tmp_path)
    stable = _commit_handoff(
        tmp_path,
        "HANDOFF-director-2026-07-08-stable.md",
        "When: 2026-07-08T10:00:00Z",
        message="docs: stable handoff",
    )
    dirty = _commit_handoff(
        tmp_path,
        "HANDOFF-director-2026-07-09-dirty.md",
        "When: 2026-07-09T10:00:00Z",
        message="docs: dirty handoff base",
    )
    dirty.write_text("# changed after HEAD\n\nWhen: 2026-07-10T10:00:00Z\n", encoding="utf-8")
    untracked = docs / "HANDOFF-director-2026-07-11-untracked.md"
    untracked.write_text("# untracked\n\nWhen: 2026-07-11T10:00:00Z\n", encoding="utf-8")

    selection = latest_handoff.find_latest_handoff(tmp_path, "director")

    assert selection.path == stable
    assert any("working tree differs from HEAD" in item for item in selection.warnings)
    assert any("not tracked at HEAD" in item for item in selection.warnings)


def test_symlink_candidate_is_excluded(tmp_path: Path):
    docs = _init_repo(tmp_path)
    stable = _commit_handoff(
        tmp_path,
        "HANDOFF-director-2026-07-08-stable.md",
        "When: 2026-07-08T10:00:00Z",
        message="docs: stable handoff",
    )
    symlink = docs / "HANDOFF-director-2026-07-09-symlink.md"
    symlink.symlink_to(stable.name)
    _git(tmp_path, "add", f"docs/{symlink.name}")
    _git(tmp_path, "commit", "-q", "-m", "docs: symlink candidate")

    selection = latest_handoff.find_latest_handoff(tmp_path, "director")

    assert selection.path == stable
    assert any("not a regular non-symlink file" in item for item in selection.warnings)


def test_git_unavailable_returns_no_selection_with_warning(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "HANDOFF-director-2026-07-09-candidate.md").write_text(
        "# candidate\n\nWhen: 2026-07-09\n", encoding="utf-8"
    )

    def fail_git(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(["git", *args], 1, "", "git unavailable")

    monkeypatch.setattr(latest_handoff, "_git_text", fail_git)

    selection = latest_handoff.find_latest_handoff(tmp_path, "director")

    assert selection.path is None
    assert any("Git chronology unavailable" in item for item in selection.warnings)


def test_main_prints_selected_path_and_all_warnings(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
):
    docs = _init_repo(tmp_path)
    selected = _commit_handoff(
        tmp_path,
        "HANDOFF-coordinator-2026-07-09-good.md",
        "Date: 2026-07-09",
        message="docs: coordinator handoff",
    )
    (docs / "HANDOFF-2026-07-09-coordinator-session.md").write_text(
        "# near match\n", encoding="utf-8"
    )

    rc = latest_handoff.main(["coordinator2", "--root", str(tmp_path)])
    output = capsys.readouterr()

    assert rc == 0
    assert output.out.strip() == str(selected)
    assert "HANDOFF-2026-07-09-coordinator-session.md" in output.err


def test_main_reports_no_valid_head_backed_handoff(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
):
    docs = _init_repo(tmp_path)
    (docs / "HANDOFF-2026-07-07-director-session.md").write_text(
        "# near match\n", encoding="utf-8"
    )

    rc = latest_handoff.main(["director", "--root", str(tmp_path)])
    output = capsys.readouterr()

    assert rc == 0
    assert "no canonical handoff found for director" in output.err
    assert "HANDOFF-2026-07-07-director-session.md" in output.err
    assert output.out == ""
```

Expected: the old `_write_handoff` fixture and all `mtime`-defined expectations are gone. The suite names every routed acceptance case and includes one malformed-metadata compatibility test.

- [ ] **Step 2: Run tests to verify RED**

Run:

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_latest_handoff.py -q -p no:cacheprovider
```

Expected: failures prove the current `mtime` selector chooses the wrong path and accepts untracked or dirty candidates.

- [ ] **Step 3: Replace the selector with the exact HEAD-backed implementation**

Replace `scripts/latest_handoff.py` with this complete content:

```python
#!/usr/bin/env python3
"""Select the newest canonical handoff for a concrete seat."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import date, datetime, timezone
import os
from pathlib import Path
import re
import subprocess
import sys

import protocol_mailbox


REPO_ROOT = Path(__file__).resolve().parent.parent
VALID_SEATS = frozenset(protocol_mailbox.RECEIVING_SEATS)
_METADATA_RE = re.compile(r"^(When|Created|Date):[ \t]*(\S+)[ \t]*$")
_FULL_UTC_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_FILENAME_DATE_RE = re.compile(
    r"^HANDOFF-(?:director|director2|operator|operator2|coordinator)-(\d{4}-\d{2}-\d{2})"
)
_METADATA_LINE_LIMIT = 20


@dataclass(frozen=True)
class HandoffSelection:
    seat: str
    pattern: str
    path: Path | None
    warnings: tuple[str, ...]


@dataclass(frozen=True)
class _Candidate:
    path: Path
    introduction_rank: int
    metadata_precision: int
    metadata_value: int


def canonical_pattern(seat: str) -> str:
    if seat not in VALID_SEATS:
        raise ValueError(f"unknown seat: {seat}")
    token = "coordinator" if seat.startswith("coordinator") else seat
    return f"HANDOFF-{token}-*.md"


def _warning_tokens(seat: str) -> tuple[str, ...]:
    if seat.startswith("coordinator"):
        return ("coordinator", "coordinator2")
    return (seat,)


def _is_near_match(path: Path, seat: str, pattern: str) -> bool:
    if path.name.startswith("HANDOFF-") is False or path.suffix != ".md":
        return False
    if path.match(pattern):
        return False
    tokens = path.stem.split("-")[1:]
    return any(token in tokens for token in _warning_tokens(seat))


def _git_text(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    child_env = os.environ.copy()
    child_env.pop("GIT_INDEX_FILE", None)
    return subprocess.run(
        ["git", "-C", str(root), *args],
        env=child_env,
        text=True,
        capture_output=True,
        check=False,
    )


def _git_bytes(root: Path, *args: str) -> subprocess.CompletedProcess[bytes]:
    child_env = os.environ.copy()
    child_env.pop("GIT_INDEX_FILE", None)
    return subprocess.run(
        ["git", "-C", str(root), *args],
        env=child_env,
        text=False,
        capture_output=True,
        check=False,
    )


def _metadata_order(relative: str, content: bytes) -> tuple[int, int, tuple[str, ...]]:
    try:
        leading_lines = content.decode("utf-8").splitlines()[:_METADATA_LINE_LIMIT]
    except UnicodeDecodeError:
        return 0, 0, (f"warning: canonical handoff {relative} has unusable metadata: invalid UTF-8",)

    metadata = [match for line in leading_lines if (match := _METADATA_RE.fullmatch(line))]
    if len(metadata) != 1:
        reason = "missing metadata" if not metadata else "duplicate metadata"
        return 0, 0, (f"warning: canonical handoff {relative} has unusable metadata: {reason}",)

    value = metadata[0].group(2)
    try:
        if _FULL_UTC_RE.fullmatch(value):
            parsed = datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
            precision = 2
            order_value = int(parsed.timestamp())
            metadata_day = parsed.date().isoformat()
        elif _DATE_RE.fullmatch(value):
            parsed_day = date.fromisoformat(value)
            precision = 1
            order_value = parsed_day.toordinal()
            metadata_day = parsed_day.isoformat()
        else:
            raise ValueError("expected full UTC or date-only value")
    except (OverflowError, ValueError) as exc:
        return 0, 0, (f"warning: canonical handoff {relative} has unusable metadata: {exc}",)

    warnings: list[str] = []
    filename_match = _FILENAME_DATE_RE.match(Path(relative).name)
    if filename_match and filename_match.group(1) != metadata_day:
        warnings.append(
            f"warning: canonical handoff {relative} filename date {filename_match.group(1)} "
            f"disagrees with metadata date {metadata_day}"
        )
    return precision, order_value, tuple(warnings)


def _candidate(
    root: Path,
    path: Path,
    ranks: dict[str, int],
) -> tuple[_Candidate | None, tuple[str, ...]]:
    relative = path.relative_to(root).as_posix()
    if path.is_symlink() or not path.is_file():
        return None, (
            f"warning: ignored canonical handoff {relative}: not a regular non-symlink file",
        )

    tracked = _git_text(root, "ls-files", "--error-unmatch", "--", relative)
    if tracked.returncode != 0:
        return None, (f"warning: ignored canonical handoff {relative}: not tracked at HEAD",)

    head_content = _git_bytes(root, "show", f"HEAD:{relative}")
    if head_content.returncode != 0:
        return None, (f"warning: ignored canonical handoff {relative}: not tracked at HEAD",)
    try:
        worktree_content = path.read_bytes()
    except OSError as exc:
        return None, (f"warning: ignored canonical handoff {relative}: unreadable working tree: {exc}",)
    if worktree_content != head_content.stdout:
        return None, (f"warning: ignored canonical handoff {relative}: working tree differs from HEAD",)

    history = _git_text(
        root,
        "log",
        "--diff-filter=A",
        "--follow",
        "--format=%H",
        "--",
        relative,
    )
    introducing_shas = [line for line in history.stdout.splitlines() if line]
    introducing_sha = introducing_shas[-1] if history.returncode == 0 and introducing_shas else None
    if introducing_sha is None or introducing_sha not in ranks:
        return None, (
            f"warning: ignored canonical handoff {relative}: introducing commit unavailable",
        )

    precision, metadata_value, metadata_warnings = _metadata_order(relative, head_content.stdout)
    return (
        _Candidate(path, ranks[introducing_sha], precision, metadata_value),
        metadata_warnings,
    )


def find_latest_handoff(root: Path, seat: str) -> HandoffSelection:
    pattern = canonical_pattern(seat)
    docs_root = root / "docs"
    warnings = [
        f"warning: ignored noncanonical same-seat handoff candidate docs/{path.name}; "
        f"expected {pattern}"
        for path in sorted(docs_root.glob("HANDOFF-*.md"))
        if _is_near_match(path, seat, pattern)
    ]

    chronology = _git_text(root, "rev-list", "--topo-order", "--reverse", "HEAD")
    if chronology.returncode != 0:
        detail = chronology.stderr.strip() or "git rev-list failed"
        warnings.append(f"warning: Git chronology unavailable for canonical handoffs: {detail}")
        return HandoffSelection(seat, pattern, None, tuple(warnings))
    ranks = {sha: rank for rank, sha in enumerate(chronology.stdout.splitlines()) if sha}

    valid_candidates: list[_Candidate] = []
    for path in sorted(docs_root.glob(pattern)):
        candidate, candidate_warnings = _candidate(root, path, ranks)
        warnings.extend(candidate_warnings)
        if candidate is not None:
            valid_candidates.append(candidate)

    selected = max(
        valid_candidates,
        key=lambda item: (
            item.introduction_rank,
            item.metadata_precision,
            item.metadata_value,
            item.path.name,
        ),
        default=None,
    )
    if selected is not None:
        selected_order = (
            selected.introduction_rank,
            selected.metadata_precision,
            selected.metadata_value,
        )
        tied = [
            item
            for item in valid_candidates
            if (item.introduction_rank, item.metadata_precision, item.metadata_value)
            == selected_order
        ]
        if len(tied) > 1:
            relative = selected.path.relative_to(root).as_posix()
            warnings.append(
                "warning: canonical handoffs share introduction and metadata order; "
                f"selected {relative} by basename tiebreak"
            )

    return HandoffSelection(
        seat=seat,
        pattern=pattern,
        path=selected.path if selected else None,
        warnings=tuple(warnings),
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Print the newest canonical same-seat handoff.")
    parser.add_argument("seat", choices=protocol_mailbox.RECEIVING_SEATS)
    parser.add_argument("--root", type=Path, default=REPO_ROOT)
    args = parser.parse_args(argv)

    selection = find_latest_handoff(args.root, args.seat)
    for warning in selection.warnings:
        print(warning, file=sys.stderr)
    if selection.path is None:
        print(
            f"no canonical handoff found for {args.seat} under {args.root / 'docs'} "
            f"(expected {selection.pattern})",
            file=sys.stderr,
        )
        return 0
    print(selection.path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

Expected: no filesystem timestamp, Git commit timestamp, filename-day ordering, uncommitted content, or silent fallback participates in selection. Public signatures and canonical seat aliasing stay unchanged.

- [ ] **Step 4: Run GREEN and integration tests**

Run:

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_latest_handoff.py -q -p no:cacheprovider
env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_seat_status_all.py tests/unit/test_latest_handoff.py tests/unit/test_protocol_prompt_sync.py tests/unit/test_codex_ledger_bridge.py -q -p no:cacheprovider
env -u GIT_INDEX_FILE .venv/bin/python scripts/latest_handoff.py coordinator
env -u GIT_INDEX_FILE git diff --check
```

Expected: all tests pass, the live command selects `docs/HANDOFF-coordinator-2026-07-17-compact-phase3-closeout.md`, warnings are explicit, and diff check is silent.

- [ ] **Step 5: Commit exact handoff scope**

Run:

```bash
env -u GIT_INDEX_FILE git add -- scripts/latest_handoff.py tests/unit/test_latest_handoff.py
env -u GIT_INDEX_FILE git diff --cached --name-status
env -u GIT_INDEX_FILE git commit -m "fix(protocol): make handoff selection deterministic" -- scripts/latest_handoff.py tests/unit/test_latest_handoff.py
```

Expected: exactly two modified paths in the second Director commit.

### Task 5: Director Completion Verification And Canonical Request

**Files:**
- Read: complete two-commit Director range
- Create through fixed writer: one `coordination/mailbox/sent/*-director-to-operator-verify-request.md`

**Interfaces:**
- Consumes: Task-3 and Task-4 commits plus Director2 findings.
- Produces: one canonical request binding exact base, head, author seat/model, assigned Operator, four paths, commands, adversarial question, and exclusions.

- [ ] **Step 1: Run complete Director verification**

Run:

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_latest_handoff.py -q -p no:cacheprovider
env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_threeway_activation_scripts.py -k test_bus_unread_script -q -p no:cacheprovider
env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_keys.py -q -p no:cacheprovider
env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_seat_status_all.py tests/unit/test_latest_handoff.py tests/unit/test_protocol_prompt_sync.py tests/unit/test_codex_ledger_bridge.py -q -p no:cacheprovider
env -u GIT_INDEX_FILE .venv/bin/python scripts/protocol_doctor.py --wave 2
env -u GIT_INDEX_FILE .venv/bin/python scripts/ci_smoke.py
env -u GIT_INDEX_FILE git diff --check
env -u GIT_INDEX_FILE git status --short --branch
```

Expected: focused tests and integration tests pass, protocol doctor PASS, smoke OK, diff check silent, and no tracked/staged WIP remains.

- [ ] **Step 2: Inspect exact range and write set**

Resolve the two exact implementation commits by their unique routed messages, require them to be consecutive, then inspect the range:

```bash
cleanup_commit=$(env -u GIT_INDEX_FILE git log -1 --format=%H --grep='^chore(protocol): correct scan cleanup findings$')
handoff_commit=$(env -u GIT_INDEX_FILE git log -1 --format=%H --grep='^fix(protocol): make handoff selection deterministic$')
test -n "$cleanup_commit"
test -n "$handoff_commit"
test "$(env -u GIT_INDEX_FILE git rev-parse "${handoff_commit}^")" = "$cleanup_commit"
director_base=$(env -u GIT_INDEX_FILE git rev-parse "${cleanup_commit}^")
env -u GIT_INDEX_FILE git diff --name-status "${director_base}..${handoff_commit}"
```

Expected exact paths:

```text
scripts/bus_unread.py
scripts/latest_handoff.py
tests/unit/test_keys.py
tests/unit/test_latest_handoff.py
```

- [ ] **Step 3: Send and commit the canonical verify-request**

The request question is:

```text
Does the exact two-commit range preserve canonical seat mapping and warning visibility while selecting only clean HEAD-backed handoffs by introducing-commit topology, resisting mtime, dirty, untracked, symlink, legacy-metadata, same-commit, and Git-failure adversarial cases, with the two cleanup edits behavior-neutral and no side effect or scope leakage?
```

Use the fixed writer, inspect staged scope, and commit only the generated request file.

### Task 6: Operator Independent Verification

**Files:**
- Read: canonical verify-request and exact Director range
- Create through fixed writer: one `coordination/mailbox/sent/*-operator-to-all-verification-report.md`

**Interfaces:**
- Consumes: complete canonical request with exact immutable fields.
- Produces: the only GO/NITS/FAIL verdict for the maintenance implementation range.

- [ ] **Step 1: Validate request completeness and reviewed HEAD**

Run the exact Operator startup block from the route. Read the request body and stop with FAIL if base, head, author, assigned Operator, paths, commands, or question is absent or if current HEAD differs from the request trigger binding.

- [ ] **Step 2: Independently inspect the actual diff**

Enumerate definitions, subprocess use, warnings, callers, and tests with `rg`; confirm no obsolete `st_mtime_ns` ordering remains in `scripts/latest_handoff.py` or its tests and no non-routed path changed.

- [ ] **Step 3: Rerun all routed commands**

Run the Task-5 verification block independently. Additionally run:

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_latest_handoff.py --runxfail -q -p no:cacheprovider
env -u GIT_INDEX_FILE git diff --check
env -u GIT_INDEX_FILE git status --short --branch
```

Expected: all pass and the reviewed tree is clean.

- [ ] **Step 4: Perform adversarial mutation reasoning**

Verify from actual tests that each mutation would fail at least one assertion:

```text
restore mtime ordering
accept an untracked newer-looking handoff
accept working-tree bytes differing from HEAD
rank by commit timestamp instead of topology
let malformed metadata outrank a valid full timestamp in one introduction commit
silently basename-tie without warning
map coordinator2 to a coordinator2 filename pattern
```

- [ ] **Step 5: Publish and commit GO/NITS/FAIL**

Use findings-first ordering. Bind the exact request path and trigger commit, reviewed base/head, reviewer seat/model, commands/results, four-path scope, sandbox-report separation, and next steps. Do not repair code or consume a cursor.

### Task 7: Coordinator Maintenance Convergence And Ledger Resume Gate

**Files:**
- Modify: maintenance capacity packets only
- Modify: parked ledger packets only when resume conditions pass
- Create through fixed writer: one coordinator convergence or blocker event
- Create only at a real transfer boundary: `docs/HANDOFF-coordinator-2026-07-18-pipeline-maintenance-closeout.md`

**Interfaces:**
- Consumes: Director2 findings, Operator2 classification, Director request, Operator verdict, exact Git state, capacity and protocol gates.
- Produces: maintenance closeout plus either a separate writer-correction route or a ledger resume event restoring original packet readiness.

- [ ] **Step 1: Refresh every live boundary**

Run coordinator status, Git status/log, locks, mailbox bodies, capacity board, route validator, coordination checker, protocol doctor, and smoke against the committed maintenance route.

- [ ] **Step 2: Reconcile Operator2 sandbox classification**

Apply exactly one branch:

```text
repository-defect -> keep ledger parked; create a new writer security design and route
environment-policy -> record no-code disposition; continue maintenance closeout
unable-to-verify -> keep ledger parked and return the exact missing authority/evidence
```

- [ ] **Step 3: Reconcile Operator implementation verdict**

GO may close the implementation packets. NITS or FAIL keeps ledger parked and routes only the smallest correction. Diagnostics never replace the Operator verdict.

- [ ] **Step 4: Verify exact metadata scope and protocol health**

Run:

```bash
env -u GIT_INDEX_FILE .venv/bin/python scripts/protocol_capacity_board.py --wave 2
env -u GIT_INDEX_FILE .venv/bin/python scripts/protocol_doctor.py --wave 2
env -u GIT_INDEX_FILE .venv/bin/python scripts/check_coordination.py --git-root . --docs-root docs
env -u GIT_INDEX_FILE .venv/bin/python scripts/ci_smoke.py
env -u GIT_INDEX_FILE git diff --check
env -u GIT_INDEX_FILE git status --short --branch
```

Expected: all gates pass and no ambient tracked/staged work remains.

- [ ] **Step 5: Resume or remain parked**

Before resume, recheck evidence-ledger target HEAD `a93d07196dd8622d753cdd5f8617af7df29eb1cf`, its existing untracked `web/` inventory, and the excluded normal checkout. If unchanged and every maintenance branch is terminal GO/no-code, restore the original ledger states: Director `ready`, Director2 `ready`, Operator `blocked` on Director, Operator2 `ready`, coordinator `blocked` on all four. Publish one exact resume event. Otherwise publish one blocker/convergence event and preserve the parked state.
