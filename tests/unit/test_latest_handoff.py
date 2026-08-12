from __future__ import annotations

import os
from pathlib import Path
import shutil
import subprocess

import pytest

import latest_handoff


def _git(root: Path, *args: str, env: dict[str, str] | None = None) -> str:
    child_env = os.environ.copy()
    child_env.pop("GIT_INDEX_FILE", None)
    child_env.update(env or {})
    result = subprocess.run(
        ["git", "-C", str(root), *args],
        env=child_env,
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


def _commit_handoff(
    root: Path,
    name: str,
    metadata: str,
    *,
    message: str,
    commit_env: dict[str, str] | None = None,
) -> Path:
    path = root / "docs" / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"# {name}\n\n{metadata}\n", encoding="utf-8")
    _git(root, "add", f"docs/{name}")
    _git(root, "commit", "-q", "-m", message, env=commit_env)
    return path


def test_canonical_pattern_uses_concrete_seat_identity_and_coordinator_alias():
    assert latest_handoff.canonical_pattern("director") == "HANDOFF-director-*.md"
    assert latest_handoff.canonical_pattern("operator2") == "HANDOFF-operator2-*.md"
    assert latest_handoff.canonical_pattern("coordinator") == "HANDOFF-coordinator-*.md"
    assert latest_handoff.canonical_pattern("coordinator2") == "HANDOFF-coordinator-*.md"


def test_exact_current_path_introduction_does_not_follow_copy_lineage(tmp_path: Path):
    docs = _init_repo(tmp_path)
    source = docs / "HANDOFF-coordinator-2026-07-01-source.md"
    source.write_text(
        "# copied source\n\nWhen: 2026-07-01T00:00:00Z\n\n" + "same body\n" * 20,
        encoding="utf-8",
    )
    _git(tmp_path, "add", f"docs/{source.name}")
    _git(tmp_path, "commit", "-q", "-m", "docs: source handoff")
    _commit_handoff(
        tmp_path,
        "HANDOFF-coordinator-2026-07-02-stable.md",
        "When: 2026-07-02T00:00:00Z",
        message="docs: stable handoff",
    )
    copied = docs / "HANDOFF-coordinator-2026-07-03-copied.md"
    shutil.copyfile(source, copied)
    _git(tmp_path, "add", f"docs/{copied.name}")
    _git(tmp_path, "commit", "-q", "-m", "docs: copy handoff")

    selection = latest_handoff.find_latest_handoff(tmp_path, "coordinator")

    assert selection.path == copied


@pytest.mark.parametrize("equal_mtime", (False, True))
def test_introduction_topology_wins_without_mtime_authority(
    tmp_path: Path, equal_mtime: bool
):
    _init_repo(tmp_path)
    older = _commit_handoff(
        tmp_path,
        "HANDOFF-director-2026-07-08-older.md",
        "When: 2026-07-08T09:00:00Z",
        message="docs: older handoff",
    )
    newer = _commit_handoff(
        tmp_path,
        "HANDOFF-director-2026-07-08-newer.md",
        "When: 2026-07-08T10:00:00Z",
        message="docs: newer handoff",
    )
    os.utime(older, (200 if equal_mtime else 400, 200 if equal_mtime else 400))
    os.utime(newer, (200 if equal_mtime else 100, 200 if equal_mtime else 100))

    selection = latest_handoff.find_latest_handoff(tmp_path, "director")

    assert selection.path == newer


def test_incomparable_introductions_use_metadata_not_commit_time(tmp_path: Path):
    _init_repo(tmp_path)
    main_branch = _git(tmp_path, "branch", "--show-current")
    _git(tmp_path, "checkout", "-q", "-b", "left")
    left = _commit_handoff(
        tmp_path,
        "HANDOFF-coordinator-2026-07-08-left.md",
        "When: 2026-07-08T09:00:00Z",
        message="docs: left branch handoff",
        commit_env={
            "GIT_AUTHOR_DATE": "2030-01-01T00:00:00+0000",
            "GIT_COMMITTER_DATE": "2030-01-01T00:00:00+0000",
        },
    )
    _git(tmp_path, "checkout", "-q", main_branch)
    _git(tmp_path, "checkout", "-q", "-b", "right")
    right = _commit_handoff(
        tmp_path,
        "HANDOFF-coordinator-2026-07-08-right.md",
        "When: 2026-07-08T10:00:00Z",
        message="docs: right branch handoff",
        commit_env={
            "GIT_AUTHOR_DATE": "2000-01-01T00:00:00+0000",
            "GIT_COMMITTER_DATE": "2000-01-01T00:00:00+0000",
        },
    )
    _git(tmp_path, "merge", "-q", "--no-ff", "left", "-m", "merge handoffs")

    selection = latest_handoff.find_latest_handoff(tmp_path, "coordinator")

    assert selection.path == right
    assert selection.path != left
    assert any("incomparable introducing commits" in item for item in selection.warnings)


def test_same_introduction_uses_legacy_metadata_and_precision(tmp_path: Path):
    docs = _init_repo(tmp_path)
    early = docs / "HANDOFF-coordinator-2026-07-08-early.md"
    date_only = docs / "HANDOFF-coordinator-2026-07-31-date.md"
    full = docs / "HANDOFF-coordinator-2026-07-01-full.md"
    early.write_text("# early\n\nCreated: 2026-07-08T03:00:00Z\n", encoding="utf-8")
    date_only.write_text("# date\n\nDate: 2026-07-31\n", encoding="utf-8")
    full.write_text("# full\n\nWhen: 2026-07-08T04:00:00Z\n", encoding="utf-8")
    _git(tmp_path, "add", "docs")
    _git(tmp_path, "commit", "-q", "-m", "docs: same introduction")

    selection = latest_handoff.find_latest_handoff(tmp_path, "coordinator2")

    assert selection.path == full


def test_metadata_tie_uses_basename_with_visible_warning(tmp_path: Path):
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


def test_filename_metadata_disagreement_remains_compatible_with_warning(tmp_path: Path):
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


@pytest.mark.parametrize(
    ("case", "body"),
    [
        ("missing", b"# invalid\n"),
        ("duplicate", b"# invalid\n\nWhen: 2026-07-09\nDate: 2026-07-09\n"),
        ("malformed", b"# invalid\n\nWhen: someday\n"),
        ("non-UTC", b"# invalid\n\nWhen: 2026-07-09T10:00:00+00:00\n"),
        ("out-of-range", b"# invalid\n\nWhen: 2026-13-40\n"),
        ("invalid-UTF-8", b"# invalid\n\nWhen: \xff\n"),
        ("valid-plus-blank", b"# invalid\n\nWhen: 2026-07-09\nDate:\n"),
        ("valid-plus-malformed", b"# invalid\n\nWhen: 2026-07-09\nDate: someday\n"),
    ],
)
def test_invalid_metadata_classes_warn_and_lose_same_introduction_tie(
    tmp_path: Path, case: str, body: bytes
):
    docs = _init_repo(tmp_path)
    valid = docs / "HANDOFF-director2-2026-07-09-valid.md"
    invalid = docs / "HANDOFF-director2-2026-07-09-zulu.md"
    valid.write_text("# valid\n\nWhen: 2026-07-09\n", encoding="utf-8")
    invalid.write_bytes(body)
    _git(tmp_path, "add", "docs")
    _git(tmp_path, "commit", "-q", "-m", "docs: mixed metadata")

    selection = latest_handoff.find_latest_handoff(tmp_path, "director2")

    assert selection.path == valid
    assert any(invalid.name in item and "unusable metadata" in item for item in selection.warnings)
    assert case


def test_deleted_untracked_and_divergent_candidates_warn_and_do_not_win(tmp_path: Path):
    docs = _init_repo(tmp_path)
    stable = _commit_handoff(
        tmp_path,
        "HANDOFF-director-2026-07-08-stable.md",
        "When: 2026-07-08T10:00:00Z",
        message="docs: stable handoff",
    )
    deleted = _commit_handoff(
        tmp_path,
        "HANDOFF-director-2026-07-09-deleted.md",
        "When: 2026-07-09T10:00:00Z",
        message="docs: deleted handoff",
    )
    dirty = _commit_handoff(
        tmp_path,
        "HANDOFF-director-2026-07-10-dirty.md",
        "When: 2026-07-10T10:00:00Z",
        message="docs: dirty handoff",
    )
    deleted.unlink()
    dirty.write_text("# changed\n\nWhen: 2026-07-11T10:00:00Z\n", encoding="utf-8")
    untracked = docs / "HANDOFF-director-2026-07-12-untracked.md"
    untracked.write_text("# untracked\n\nWhen: 2026-07-12T10:00:00Z\n", encoding="utf-8")

    selection = latest_handoff.find_latest_handoff(tmp_path, "director")

    assert selection.path == stable
    assert any("missing from working tree" in item for item in selection.warnings)
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


def test_concrete_seat_selection_excludes_cross_seat_candidates(tmp_path: Path):
    _init_repo(tmp_path)
    selected = _commit_handoff(
        tmp_path,
        "HANDOFF-director-2026-07-08-selected.md",
        "When: 2026-07-08T10:00:00Z",
        message="docs: director handoff",
    )
    _commit_handoff(
        tmp_path,
        "HANDOFF-director2-2026-07-09-other.md",
        "When: 2026-07-09T10:00:00Z",
        message="docs: director2 handoff",
    )

    selection = latest_handoff.find_latest_handoff(tmp_path, "director")

    assert selection.path == selected
    assert all("director2" not in item for item in selection.warnings)


@pytest.mark.parametrize(
    ("failure", "expected_warning"),
    [
        ("history", "exact-path introduction unavailable"),
        ("reachability", "exact-path introduction unreachable from HEAD"),
        ("comparison", "Git chronology unavailable while comparing"),
    ],
)
def test_per_candidate_git_failures_fail_closed_with_visible_warning(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    failure: str,
    expected_warning: str,
):
    _init_repo(tmp_path)
    _commit_handoff(
        tmp_path,
        "HANDOFF-director-2026-07-08-stable.md",
        "When: 2026-07-08T10:00:00Z",
        message="docs: stable handoff",
    )
    stable_sha = _git(tmp_path, "rev-parse", "HEAD")
    failing = _commit_handoff(
        tmp_path,
        "HANDOFF-director-2026-07-09-failing.md",
        "When: 2026-07-09T10:00:00Z",
        message="docs: failing handoff",
    )
    failing_sha = _git(tmp_path, "rev-parse", "HEAD")
    real_git = latest_handoff._git_text

    def fail_branch(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
        if (
            failure == "history"
            and args[:2] == ("log", "--diff-filter=A")
            and args[-1].endswith(failing.name)
        ):
            return subprocess.CompletedProcess(["git", *args], 2, "", "history failed")
        if args[:2] == ("merge-base", "--is-ancestor"):
            if failure == "reachability" and args[2:] == (failing_sha, "HEAD"):
                return subprocess.CompletedProcess(["git", *args], 2, "", "reachability failed")
            if failure == "comparison" and args[3] != "HEAD":
                assert {args[2], args[3]} == {stable_sha, failing_sha}
                return subprocess.CompletedProcess(["git", *args], 2, "", "comparison failed")
        return real_git(root, *args)

    monkeypatch.setattr(latest_handoff, "_git_text", fail_branch)

    selection = latest_handoff.find_latest_handoff(tmp_path, "director")

    assert selection.path is None
    assert any(expected_warning in item for item in selection.warnings)


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
    untracked = docs / "HANDOFF-coordinator-2026-07-10-untracked.md"
    untracked.write_text("# untracked\n\nWhen: 2026-07-10\n", encoding="utf-8")

    rc = latest_handoff.main(["coordinator2", "--root", str(tmp_path)])
    output = capsys.readouterr()

    assert rc == 0
    assert output.out.strip() == str(selected)
    assert "HANDOFF-2026-07-09-coordinator-session.md" in output.err
    assert untracked.name in output.err
    assert output.err.count("warning:") >= 2


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
