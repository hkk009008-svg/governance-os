"""Stage 1 gate tests for the read-only episodic index (ADR-067).

Every test runs against a repository built for the test, never the checkout
under review, so the assertions cannot pass by riding this repo's real
mailbox history (environment-of-record discipline).
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from scripts import learning_index  # noqa: E402


_EVENT_NAME = (
    "2026-07-30T01-02-03Z-director2-to-operator-verify-request.md"
)


def _throwaway_repo(tmp_path: Path) -> Path:
    """A repository built for the test, never the checkout under review."""

    root = tmp_path / "repo"
    root.mkdir()

    def git(*arguments: str) -> None:
        subprocess.run(
            ["git", *arguments],
            cwd=root,
            check=True,
            capture_output=True,
            env={"PATH": "/usr/bin:/bin", "HOME": str(tmp_path)},
        )

    git("init", "-q")
    git("config", "user.email", "probe@example.invalid")
    git("config", "user.name", "probe")
    sent = root / "coordination" / "mailbox" / "sent"
    sent.mkdir(parents=True)
    (sent / _EVENT_NAME).write_text(
        "# Director2 → Operator: pin the flaky gate\n\n"
        "**When:** 2026-07-30T01:02:03Z · **From:** director2 (online)\n\n"
        "Event type: verify-request\n"
        "Reviewed base: " + "a" * 40 + "\n"
        "Reviewed head: " + "b" * 40 + "\n"
        "Risk class: material-behavior\n\n"
        "Cursor at send: 0\n",
        encoding="utf-8",
    )
    plans = root / "docs" / "superpowers" / "plans"
    plans.mkdir(parents=True)
    (plans / "2026-07-28-flaky-gate-plan.md").write_text(
        "# Plan\n\nStabilize the flaky gate before the release.\n",
        encoding="utf-8",
    )
    (root / "docs" / "HANDOFF-operator-2026-07-29-flaky.md").write_text(
        "# Handoff\n\nThe flaky gate reproduces under load.\n",
        encoding="utf-8",
    )
    logs = root / "logs" / "claims"
    logs.mkdir(parents=True)
    (logs / "ledger.jsonl").write_text(
        '{"ts": "2026-07-27T00:00:00Z", "claim": "the gate is flaky"}\n',
        encoding="utf-8",
    )
    git("add", "-A")
    git("commit", "-q", "-m", "seed governance artifacts")
    return root


def test_every_result_carries_source_timestamp_scope_hash(tmp_path: Path) -> None:
    root = _throwaway_repo(tmp_path)
    db = tmp_path / "index.sqlite"
    learning_index.build_index(root, db_path=db)
    rows = learning_index.query_index(root, "flaky", db_path=db)
    assert rows, "seeded artifacts mentioning 'flaky' must be retrievable"
    for row in rows:
        assert row.path, "row lost its source path"
        assert row.scope == "repository"
        assert row.timestamp, "row lost its timestamp"
        assert row.timestamp_rule in ("filename", "row-field", "commit-date")
        assert len(row.blob_sha) == 40, "content hash must be the git blob SHA"
    paths = {row.path for row in rows}
    assert f"coordination/mailbox/sent/{_EVENT_NAME}" in paths
    # The mailbox row's timestamp comes from the fixed-writer filename.
    event_row = next(r for r in rows if r.path.startswith("coordination/"))
    assert event_row.timestamp == "2026-07-30T01:02:03Z"
    assert event_row.timestamp_rule == "filename"
    assert event_row.kind == "mailbox:verify-request"


def test_index_records_built_at_commit(tmp_path: Path) -> None:
    root = _throwaway_repo(tmp_path)
    db = tmp_path / "index.sqlite"
    report = learning_index.build_index(root, db_path=db)
    head = (
        subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=root,
            check=True,
            capture_output=True,
            env={"PATH": "/usr/bin:/bin", "HOME": str(tmp_path)},
        )
        .stdout.decode("ascii")
        .strip()
    )
    assert report["built_at_commit"] == head
    assert learning_index.built_at_commit(root, db_path=db) == head


def test_absent_index_is_labeled_unavailable_not_empty(tmp_path: Path) -> None:
    root = _throwaway_repo(tmp_path)
    missing = tmp_path / "never-built.sqlite"
    assert learning_index.query_index(root, "flaky", db_path=missing) is None
    assert learning_index.built_at_commit(root, db_path=missing) is None
    # An empty result from a PROVEN-BUILT index is a real zero, not None.
    db = tmp_path / "index.sqlite"
    learning_index.build_index(root, db_path=db)
    assert learning_index.query_index(root, "zzzunmatchable", db_path=db) == []


def test_repository_scope_guard_refuses_user_scope_shapes() -> None:
    """Defense-in-depth unit: the guard refuses the shapes the contract names.

    Honest scope: the production ingest stream is `git ls-tree` output, which
    cannot emit these shapes — the load-bearing boundary is
    committed-tree-only reads, pinned by
    test_index_reads_committed_tree_never_worktree below. This guard exists
    so a future source route cannot silently widen scope.
    """

    for user_scope in (
        "/Users/someone/.claude/projects/memory/MEMORY.md",
        "~/.claude/CLAUDE.md",
        "../outside/notes.md",
        "",
    ):
        with pytest.raises(learning_index.LearningIndexError):
            learning_index._require_repository_scope(user_scope)
    assert learning_index._require_repository_scope("docs/x.md") == "docs/x.md"


def test_index_reads_committed_tree_never_worktree(tmp_path: Path) -> None:
    """The central Stage 1 claim, pinned: only committed bytes are ingested."""

    root = _throwaway_repo(tmp_path)
    # Mutate a committed file in the worktree and add an uncommitted event;
    # neither may reach the index.
    (root / "docs" / "HANDOFF-operator-2026-07-29-flaky.md").write_text(
        "# Handoff\n\nWORKTREEWORD only exists uncommitted.\n", encoding="utf-8"
    )
    (
        root / "coordination" / "mailbox" / "sent"
        / "2026-07-31T00-00-00Z-operator-to-director-status.md"
    ).write_text(
        "# Operator → Director: s\n\n"
        "**When:** 2026-07-31T00:00:00Z · **From:** operator (online)\n\n"
        "UNCOMMITTEDWORD\n\nCursor at send: 0\n",
        encoding="utf-8",
    )
    db = tmp_path / "index.sqlite"
    learning_index.build_index(root, db_path=db)
    assert learning_index.query_index(root, "WORKTREEWORD", db_path=db) == []
    assert learning_index.query_index(root, "UNCOMMITTEDWORD", db_path=db) == []
    # The committed version of the mutated file is what got indexed.
    rows = learning_index.query_index(root, "flaky", db_path=db)
    assert any(r.path == "docs/HANDOFF-operator-2026-07-29-flaky.md" for r in rows)


def test_malformed_query_raises_instead_of_reporting_unavailable(
    tmp_path: Path,
) -> None:
    """A healthy index must never call itself unavailable on bad query text."""

    root = _throwaway_repo(tmp_path)
    db = tmp_path / "index.sqlite"
    learning_index.build_index(root, db_path=db)
    for bad in ("flaky AND", '"unterminated', "NEAR("):
        with pytest.raises(learning_index.LearningIndexError, match="FTS5"):
            learning_index.query_index(root, bad, db_path=db)
    # Availability is untouched in both directions.
    assert learning_index.query_index(root, "flaky", db_path=db)
    assert learning_index.built_at_commit(root, db_path=db) is not None


def test_non_md_handoff_lookalikes_are_not_ingested(tmp_path: Path) -> None:
    root = _throwaway_repo(tmp_path)
    binary = root / "docs" / "HANDOFF-binaryish.png"
    binary.write_bytes(b"\x89PNG fake")
    subprocess.run(
        ["git", "add", "-A"], cwd=root, check=True, capture_output=True,
        env={"PATH": "/usr/bin:/bin", "HOME": str(tmp_path)},
    )
    subprocess.run(
        ["git", "commit", "-q", "-m", "binary lookalike"],
        cwd=root, check=True, capture_output=True,
        env={"PATH": "/usr/bin:/bin", "HOME": str(tmp_path)},
    )
    db = tmp_path / "index.sqlite"
    learning_index.build_index(root, db_path=db)
    rows = learning_index.query_index(root, "PNG", db_path=db)
    assert rows == []


def test_query_availability_survives_a_corrupt_index(tmp_path: Path) -> None:
    root = _throwaway_repo(tmp_path)
    db = tmp_path / "index.sqlite"
    db.write_bytes(b"this is not a sqlite database")
    assert learning_index.query_index(root, "flaky", db_path=db) is None
