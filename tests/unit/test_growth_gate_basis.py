"""The growth gate must measure the range that binds, not only the tree on disk.

`rule_python_growth` diffs the base against the WORKING TREE and folds in
untracked files. That is the conservative reading for uncommitted ADDITIONS and
the permissive one for uncommitted DELETIONS: a file committed over the per-file
cap and trimmed under it before the gate runs reported PASS, while the committed
range CI measures still violated.

Measured here on 2026-08-22, on tests/unit/test_role_cutover_gate.py:

    git diff --numstat <base> HEAD  -> 268 additions  (what CI sees: violation)
    git diff --numstat <base>       -> 250 additions  (what the gate saw: PASS)

Both numbers were true. Only one of them binds, and the gate reported the other
-- from the rule whose whole purpose is to refuse green readings that are not
what CI will measure.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

import check_no_ceremony as cnc

_ENV = {
    "PATH": "/usr/bin:/bin",
    "HOME": "/var/empty",
    "GIT_CONFIG_NOSYSTEM": "1",
    "GIT_CONFIG_GLOBAL": "/dev/null",
    "GIT_AUTHOR_NAME": "t",
    "GIT_AUTHOR_EMAIL": "t@example.invalid",
    "GIT_COMMITTER_NAME": "t",
    "GIT_COMMITTER_EMAIL": "t@example.invalid",
}


def _git(root: Path, *args: str) -> str:
    return subprocess.run(
        ["/usr/bin/git", *args], cwd=root, check=True,
        capture_output=True, text=True, env=_ENV,
    ).stdout.strip()


def _repo_whose_head_exceeds_the_ceiling(tmp_path: Path) -> tuple[Path, str]:
    """A pre-existing file grown 200 lines past the 80-net ceiling, committed."""

    root = tmp_path / "repo"
    (root / "pipeline").mkdir(parents=True)
    _git(root, "init", "-q", "-b", "main")
    (root / "pipeline" / "existing.py").write_text("x = 1\n", encoding="utf-8")
    _git(root, "add", "-A")
    _git(root, "commit", "-qm", "base")
    base = _git(root, "rev-parse", "HEAD")
    (root / "pipeline" / "existing.py").write_text(
        "x = 1\n" + "y = 1\n" * (cnc.MAX_PYTHON_NET_GROWTH + 50), encoding="utf-8"
    )
    _git(root, "add", "-A")
    _git(root, "commit", "-qm", "oversized")
    return root, base


def test_a_committed_violation_is_not_excused_by_trimming_the_working_tree(
    tmp_path, monkeypatch
) -> None:
    """The reversion control, in the exact shape that produced the false PASS."""

    root, base = _repo_whose_head_exceeds_the_ceiling(tmp_path)
    monkeypatch.setattr(cnc, "ROOT", root)
    monkeypatch.setattr(cnc, "_growth_base", lambda: base)

    status, details = cnc.rule_python_growth()
    assert status == "FAIL", details

    # Trim it back under the ceiling WITHOUT committing. Before the fix this
    # flipped the whole rule to PASS while HEAD still carried the violation.
    (root / "pipeline" / "existing.py").write_text("x = 1\n", encoding="utf-8")

    status, details = cnc.rule_python_growth()
    assert status == "FAIL", f"the committed range still violates: {details}"
    assert any("committed range" in line for line in details), details


def test_a_clean_tree_is_measured_once_and_not_twice(tmp_path, monkeypatch) -> None:
    """With nothing uncommitted the two readings cannot disagree, so only one
    is taken -- a duplicated violation line would read as two defects."""

    root, base = _repo_whose_head_exceeds_the_ceiling(tmp_path)
    monkeypatch.setattr(cnc, "ROOT", root)
    monkeypatch.setattr(cnc, "_growth_base", lambda: base)

    status, details = cnc.rule_python_growth()

    assert status == "FAIL"
    assert not any("committed range" in line for line in details), details
