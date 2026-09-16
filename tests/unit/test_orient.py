"""The orient digest is short, read-only, and member-aware."""
from __future__ import annotations

import json
from pathlib import Path

import orient
import team
from team_test_support import make_repo


def test_orient_is_one_short_read_only_digest(tmp_path: Path, capsys) -> None:
    repo = make_repo(tmp_path / "repo")
    codex = team.Team(repo, "codex")
    queued = codex.send("claude", "please look at the gate", idempotency_key="look")
    claude = team.Team(repo, "claude")
    claude.status(
        focus="mapping the gate; owns pipeline/status.py",
        handoff="DONE: read plan\nNEXT: probe cache",
    )
    store_dir = claude.store_path.parent
    before = {path.name: path.stat().st_mtime_ns for path in store_dir.iterdir()}

    assert orient.main(["--repo-root", str(repo), "--member", "claude"]) == 0
    text = capsys.readouterr().out
    lines = text.splitlines()

    assert 5 < len(lines) <= orient.MAX_LINES
    assert lines[0].startswith("Pipeline orient ")
    assert "  claude focus: mapping the gate; owns pipeline/status.py" in text
    assert "  codex focus: -" in text
    assert (
        f"You: claude resume_cursor={queued['id'] - 1} "
        f"next_unread={queued['id']} pending=1"
    ) in text
    assert "  handoff: DONE: read plan" in text and "NEXT: probe cache" in text
    assert "Formal review: none" in text and "Recent artifacts: none" in text
    assert "Next: continue scoped team work" in text
    # Reading never acknowledges, touches the store, or records activity.
    assert {path.name: path.stat().st_mtime_ns for path in store_dir.iterdir()} == before
    assert team.Team(repo, "codex").status()["sent"][0]["acknowledged_by"] == []


def test_orient_json_lists_the_newest_artifacts(tmp_path: Path, capsys) -> None:
    repo = make_repo(tmp_path / "repo")
    sent = repo / "coordination/mailbox/sent"
    sent.mkdir(parents=True)
    for minute in ("01", "02", "03", "04"):
        (sent / f"2026-09-02T10-{minute}-00Z-codex-to-claude-verify-request.md").write_text(
            f"# Codex → Claude: request {minute}\n\nbody\n", encoding="utf-8"
        )

    assert orient.main(["--repo-root", str(repo), "--json"]) == 0
    digest = json.loads(capsys.readouterr().out)

    assert [item["subject"] for item in digest["recent_artifacts"]] == [
        "Codex → Claude: request 02",
        "Codex → Claude: request 03",
        "Codex → Claude: request 04",
    ]
    assert digest["you"] is None
    assert set(digest) >= {"git", "desktop", "team_transport", "formal_review"}
