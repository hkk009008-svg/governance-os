"""One-command review publication refuses at the wrong HEAD and lands cleanly."""
from __future__ import annotations

import io
from pathlib import Path

import pytest

import ci_admission_gate as gate
import review_flow
from formal_review_support import commit, git, init_repo


def _candidate(tmp_path: Path) -> tuple[Path, str, str]:
    root = tmp_path / "repo"
    base = init_repo(root)
    head = commit(root, {"pipeline/control.py": "enabled = True\n"}, "candidate")
    return root, base, head


def _publish(root: Path, base: str, head: str = "HEAD") -> tuple[str, str]:
    return review_flow.publish_request(
        root, author="codex", author_model="gpt-5.6-sol", reviewer="claude",
        risk_class="high-risk-control", base=base, head=head,
        outcome="Review the exact range.", subject="control change",
        abuse_classes=("Gate bypass",),
    )


def _accept(root: Path, **overrides) -> tuple[str, str]:
    arguments = dict(
        reviewer="claude", reviewer_model="claude-sonnet-5", verdict="GO",
        findings="The reviewed range is acceptable.",
        evidence="$ pytest -q\n→ passed", subject="GO on the control change",
    )
    arguments.update(overrides)
    return review_flow.accept_request(root, **arguments)


def test_publish_then_accept_yields_an_admissible_landable_chain(tmp_path: Path) -> None:
    root, base, head = _candidate(tmp_path)
    request_path, request_commit = _publish(root, base)
    assert git(root, "rev-parse", "HEAD") == request_commit
    assert git(root, "rev-parse", "HEAD^") == head
    assert git(root, "diff-tree", "--no-commit-id", "--name-only", "-r", request_commit) == request_path
    assert git(root, "status", "--porcelain") == ""

    report_path, report_commit = _accept(root)
    assert git(root, "rev-parse", "HEAD") == report_commit
    assert git(root, "diff-tree", "--no-commit-id", "--name-only", "-r", report_commit) == report_path
    text = (root / report_path).read_text(encoding="utf-8")
    assert f"Verification request: {request_path}@{request_commit}" in text
    assert "Abuse Class Assessment: bound-to-request" in text

    assert gate.evaluate(root, base, report_commit).admitted
    ready, rendered = review_flow.land_check(root, base=base, head=report_commit)
    assert ready and "READY TO LAND" in rendered and "Never squash" in rendered


def test_publish_refuses_unless_head_is_the_reviewed_head(tmp_path: Path) -> None:
    root, base, head = _candidate(tmp_path)
    commit(root, {"notes.txt": "later\n"}, "later")
    with pytest.raises(review_flow.ReviewFlowError, match="not the reviewed head"):
        _publish(root, base, head=head)
    assert list((root / "coordination/mailbox/sent").glob("*verify-request.md")) == []


def test_accept_refuses_without_a_request_commit_at_head(tmp_path: Path) -> None:
    root, base, _head = _candidate(tmp_path)
    with pytest.raises(review_flow.ReviewFlowError, match="request commit"):
        _accept(root)
    _publish(root, base)
    commit(root, {"notes.txt": "interleaved\n"}, "interleaved")
    with pytest.raises(review_flow.ReviewFlowError, match="request commit"):
        _accept(root)
    assert list((root / "coordination/mailbox/sent").glob("*verification-report.md")) == []


def test_accept_refuses_a_different_reviewer_and_a_same_family_model(tmp_path: Path) -> None:
    root, base, _head = _candidate(tmp_path)
    _publish(root, base)
    with pytest.raises(review_flow.ReviewFlowError, match="names claude as reviewer"):
        _accept(root, reviewer="codex")
    with pytest.raises(Exception, match="model family"):
        _accept(root, reviewer_model="gpt-5.6-terra")
    assert git(root, "diff-tree", "--no-commit-id", "--name-only", "-r", "HEAD").endswith(
        "verify-request.md"
    )


def test_land_check_reports_a_moved_base_as_not_ready(tmp_path: Path) -> None:
    root, base, _head = _candidate(tmp_path)
    _publish(root, base)
    _report_path, report_commit = _accept(root)
    git(root, "checkout", "-q", "-B", "integration", base)
    moved = commit(root, {"other.txt": "moved on\n"}, "integration moved")
    ready, rendered = review_flow.land_check(root, base=moved, head=report_commit)
    assert not ready and "has moved past" in rendered and "NOT READY" in rendered


def test_cli_entry_points_round_trip(tmp_path: Path, monkeypatch, capsys) -> None:
    root, base, _head = _candidate(tmp_path)
    monkeypatch.setattr("sys.stdin", io.StringIO("Review the exact range."))
    assert review_flow.publish_main([
        "--repo-root", str(root), "--author", "codex", "--author-model", "gpt-5.6-sol",
        "--reviewer", "claude", "--risk-class", "high-risk-control", "--base", base,
        "--subject", "control change", "--abuse-class", "Gate bypass",
    ]) == 0
    assert "published coordination/mailbox/sent/" in capsys.readouterr().out
    evidence = tmp_path / "evidence.txt"
    evidence.write_text("$ pytest -q\n→ passed\n", encoding="utf-8")
    monkeypatch.setattr("sys.stdin", io.StringIO("Acceptable."))
    assert review_flow.accept_main([
        "--repo-root", str(root), "--reviewer", "claude", "--reviewer-model",
        "claude-sonnet-5", "--verdict", "GO", "--subject", "GO", "--evidence-file", str(evidence),
    ]) == 0
    assert review_flow.land_check_main(["--repo-root", str(root), "--base", base]) == 0
    assert "READY TO LAND" in capsys.readouterr().out
    monkeypatch.setattr("sys.stdin", io.StringIO("Again."))
    assert review_flow.publish_main([
        "--repo-root", str(root), "--author", "codex", "--author-model", "gpt-5.6-sol",
        "--reviewer", "claude", "--risk-class", "high-risk-control", "--base", base,
        "--head", base, "--subject", "wrong head",
    ]) == 1
    assert "not the reviewed head" in capsys.readouterr().err
