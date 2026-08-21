"""Unit tests for pipeline/check_placeholders.py — fail-closed adoption-placeholder scan.

Hermetic: uses tmp_path to build isolated file trees; does NOT depend on live repo state.
"""
from __future__ import annotations

import pathlib
import shutil
import subprocess

import pytest

import check_placeholders as cp


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

# Build token literals via concatenation so THIS file does not self-trip the
# scanner (the scanner itself does the same thing).
_P = "<"
_S = ">"
TOKEN_FILL_IN  = _P + "fill-in" + _S
TOKEN_PROJECT  = _P + "PROJECT" + _S


def _write(path: pathlib.Path, text: str) -> pathlib.Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


# ---------------------------------------------------------------------------
# (a) Allowlisted file containing a placeholder → scan PASSES (exit 0)
# ---------------------------------------------------------------------------

def test_allowlisted_file_passes(tmp_path: pathlib.Path):
    """A file listed in the allowlist that contains a placeholder must not raise a violation."""
    skel = tmp_path / "docs" / "skeleton.md"
    _write(skel, f"Fill this in: {TOKEN_FILL_IN}\n")

    allowlist = tmp_path / "allowlist.txt"
    allowlist.write_text("docs/skeleton.md\n")

    violations = cp.run(root=tmp_path, allowlist_file=allowlist)
    assert violations == [], f"Expected no violations, got: {violations}"


# ---------------------------------------------------------------------------
# (b) Non-allowlisted file containing a placeholder → scan FAILS (nonzero),
#     and the offending path is named in the output
# ---------------------------------------------------------------------------

def test_non_allowlisted_file_fails(tmp_path: pathlib.Path):
    """A file NOT in the allowlist that contains a placeholder must produce a violation."""
    bad_file = tmp_path / "config.md"
    _write(bad_file, f"Package: {TOKEN_PROJECT}\n")

    allowlist = tmp_path / "allowlist.txt"
    allowlist.write_text("")  # empty — nothing is allowed

    violations = cp.run(root=tmp_path, allowlist_file=allowlist)
    assert len(violations) >= 1, "Expected at least one violation"
    # The offending path must appear in the violation string.
    rel = bad_file.relative_to(tmp_path).as_posix()
    assert any(rel in v for v in violations), (
        f"Expected '{rel}' to appear in violations; got: {violations}"
    )


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

def test_missing_allowlist_file_passes_clean_tree(tmp_path: pathlib.Path):
    """When the allowlist file is absent and no placeholders exist, scan passes."""
    _write(tmp_path / "README.md", "No placeholders here.\n")
    nonexistent = tmp_path / "no-such-allowlist.txt"

    violations = cp.run(root=tmp_path, allowlist_file=nonexistent)
    assert violations == []


def test_git_dir_is_skipped(tmp_path: pathlib.Path):
    """Files under .git/ must be skipped even if they contain tokens."""
    git_file = tmp_path / ".git" / "COMMIT_EDITMSG"
    _write(git_file, f"ref: {TOKEN_PROJECT}\n")

    allowlist = tmp_path / "allowlist.txt"
    allowlist.write_text("")

    violations = cp.run(root=tmp_path, allowlist_file=allowlist)
    assert violations == []


def test_all_tokens_detected(tmp_path: pathlib.Path):
    """Every token in cp.TOKENS should trigger a violation when present in a non-allowlisted file."""
    allowlist = tmp_path / "allowlist.txt"
    allowlist.write_text("")

    for i, token in enumerate(cp.TOKENS):
        f = tmp_path / f"file_{i}.txt"
        _write(f, f"contains: {token}\n")

    violations = cp.run(root=tmp_path, allowlist_file=allowlist)
    # Each file must produce at least one violation. Some tokens are substrings of
    # others (e.g. <PROJECT> appears inside TODO(<PROJECT>)), so a single file may
    # produce more than one hit — we check coverage per file, not a 1:1 count.
    files_with_violations = {v.split(":")[0] for v in violations}
    expected_files = {f"file_{i}.txt" for i in range(len(cp.TOKENS))}
    assert expected_files == files_with_violations, (
        f"Expected violations in files {expected_files}, got {files_with_violations}"
    )


def test_comment_lines_in_allowlist_ignored(tmp_path: pathlib.Path):
    """Lines starting with # in the allowlist must be treated as comments, not paths."""
    bad_file = tmp_path / "notes.md"
    _write(bad_file, f"TODO: {TOKEN_PROJECT}\n")

    allowlist = tmp_path / "allowlist.txt"
    # The path is commented out, so it should NOT be allowlisted.
    allowlist.write_text("# notes.md\n")

    violations = cp.run(root=tmp_path, allowlist_file=allowlist)
    assert any("notes.md" in v for v in violations)


# ---------------------------------------------------------------------------
# Gitignored-scratch test (hermetic, requires git in PATH)
# ---------------------------------------------------------------------------

@pytest.mark.skipif(shutil.which("git") is None, reason="git not available in PATH")
def test_gitignored_scratch_excluded(tmp_path: pathlib.Path):
    """Files in a gitignored directory must NOT trigger violations (git-aware enumeration).

    Setup:
    - git init tmp_path
    - .gitignore ignoring scratch/
    - scratch/x.md contains a token  → scan must PASS
    - tracked/bad.md contains a token → scan must FAIL
    """
    # Initialise a bare git repo in tmp_path.
    subprocess.run(["git", "init", str(tmp_path)], check=True, capture_output=True)
    # Configure minimal identity so git doesn't complain.
    subprocess.run(
        ["git", "-C", str(tmp_path), "config", "user.email", "test@example.com"],
        check=True, capture_output=True,
    )
    subprocess.run(
        ["git", "-C", str(tmp_path), "config", "user.name", "Test"],
        check=True, capture_output=True,
    )

    # Create .gitignore that ignores scratch/.
    gitignore = tmp_path / ".gitignore"
    gitignore.write_text("scratch/\n")
    subprocess.run(
        ["git", "-C", str(tmp_path), "add", "--", ".gitignore"],
        check=True, capture_output=True,
    )
    subprocess.run(
        ["git", "-C", str(tmp_path), "commit", "-m", "init"],
        check=True, capture_output=True,
    )

    # Put a token in ignored scratch — scan must PASS.
    scratch_file = tmp_path / "scratch" / "x.md"
    _write(scratch_file, f"ignored token: {TOKEN_PROJECT}\n")

    allowlist = tmp_path / "allowlist.txt"
    allowlist.write_text("")

    violations_clean = cp.run(root=tmp_path, allowlist_file=allowlist)
    assert violations_clean == [], (
        f"Expected no violations (scratch is gitignored), got: {violations_clean}"
    )

    # Now add a token in a tracked non-allowlisted file — scan must FAIL.
    tracked_file = tmp_path / "tracked" / "bad.md"
    _write(tracked_file, f"token here: {TOKEN_PROJECT}\n")
    subprocess.run(
        ["git", "-C", str(tmp_path), "add", "--", "tracked/bad.md"],
        check=True, capture_output=True,
    )

    violations_fail = cp.run(root=tmp_path, allowlist_file=allowlist)
    assert any("tracked/bad.md" in v for v in violations_fail), (
        f"Expected violation in tracked/bad.md, got: {violations_fail}"
    )


# ---------------------------------------------------------------------------
# Live-repo regression (deterministic now that enumeration is git-aware)
# ---------------------------------------------------------------------------

def test_main_returns_zero_on_live_repo():
    """main() must return 0 on the actual repo (all current tokens are allowlisted)."""
    import io
    import contextlib
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = cp.main()
    assert rc == 0, f"Expected exit 0, got {rc}. Output:\n{buf.getvalue()}"
