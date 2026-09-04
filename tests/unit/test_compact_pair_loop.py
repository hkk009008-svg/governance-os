from __future__ import annotations

from pathlib import Path

import pytest

import compact_pair_loop as pair
from formal_review_support import (
    add_report,
    add_request,
    commit,
    event,
    git,
    init_repo,
    report_body,
    request_body,
)


def _reviewed_change(root: Path, base: str, name: str = "pipeline/control.py") -> str:
    return commit(root, {name: "enabled = True\n"}, "candidate")


def test_exact_request_and_cross_family_go_validate(tmp_path) -> None:
    root = tmp_path / "repo"
    base = init_repo(root)
    head = _reviewed_change(root, base)
    request_path, request_commit = add_request(root, base, head)
    report_path, _ = add_report(root, request_path, request_commit)

    request = pair.parse_verify_request(root, request_path, request_commit)
    report = pair.parse_verification_report(root, report_path)
    assert request.reviewed_base == base
    assert request.reviewed_head == head
    assert pair.validate_report(root, report) == []


def test_request_must_be_added_after_reviewed_head(tmp_path) -> None:
    root = tmp_path / "repo"
    base = init_repo(root)
    path, text = event(
        "2026-09-02T10-00-00Z",
        "codex",
        "claude",
        "verify-request",
        request_body(base, base),
    )
    request_commit = commit(root, {path: text}, "request")
    with pytest.raises(pair.CompactPairError, match="strict ancestor"):
        pair.parse_verify_request(root, path, request_commit)


def test_request_commit_cannot_hide_another_change(tmp_path) -> None:
    root = tmp_path / "repo"
    base = init_repo(root)
    head = _reviewed_change(root, base)
    path, text = event(
        "2026-09-02T10-00-00Z",
        "codex",
        "claude",
        "verify-request",
        request_body(base, head),
    )
    request_commit = commit(root, {path: text, "extra.txt": "hidden\n"}, "mixed request")
    with pytest.raises(pair.CompactPairError, match="only change"):
        pair.parse_verify_request(root, path, request_commit)


def test_high_risk_request_requires_abuse_assessment(tmp_path) -> None:
    root = tmp_path / "repo"
    base = init_repo(root)
    head = _reviewed_change(root, base)
    path, text = event(
        "2026-09-02T10-00-00Z",
        "codex",
        "claude",
        "verify-request",
        request_body(base, head).split("\n\n## Abuse Class Assessment", 1)[0],
    )
    with pytest.raises(pair.CompactPairError, match="Abuse Class Assessment"):
        pair._parse_request_bytes(root, path, text.encode(), "")


def test_material_request_refuses_high_risk_abuse_field(tmp_path) -> None:
    root = tmp_path / "repo"
    base = init_repo(root)
    head = _reviewed_change(root, base)
    with pytest.raises(pair.CompactPairError, match="only valid"):
        pair.compose_request(
            root,
            author_member="codex",
            author_model="gpt-5.6-sol",
            reviewer_member="claude",
            risk_class="material-behavior",
            base_rev=base,
            head_rev=head,
            outcome="Review this range.",
            abuse_assessments=("irrelevant",),
        )


def test_author_model_must_match_member(tmp_path) -> None:
    root = tmp_path / "repo"
    base = init_repo(root)
    head = _reviewed_change(root, base)
    path, text = event(
        "2026-09-02T10-00-00Z",
        "codex",
        "claude",
        "verify-request",
        request_body(base, head, author_model="claude-sonnet-5"),
    )
    request = pair._parse_request_bytes(root, path, text.encode(), "")
    assert "author model family does not match author member" in pair.validate_request_candidate(root, request)


def test_agy_may_author_but_not_publish_verdict(tmp_path) -> None:
    root = tmp_path / "repo"
    base = init_repo(root)
    head = _reviewed_change(root, base)
    path, text = event(
        "2026-09-02T10-00-00Z",
        "agy",
        "claude",
        "verify-request",
        request_body(base, head, author_model="gemini-3.8-flash-high"),
    )
    request = pair._parse_request_bytes(root, path, text.encode(), "")
    assert pair.validate_request_candidate(root, request) == []
    bad_report, _ = event(
        "2026-09-02T10-01-00Z",
        "agy",
        "codex",
        "verification-report",
        "body",
    )
    assert pair.REPORT_RE.fullmatch(bad_report) is None


def test_report_rejects_reviewer_model_laundering(tmp_path) -> None:
    root = tmp_path / "repo"
    base = init_repo(root)
    head = _reviewed_change(root, base)
    request_path, request_commit = add_request(root, base, head)
    report_path, _ = add_report(
        root,
        request_path,
        request_commit,
        reviewer_model="gpt-5.6-terra",
    )
    report = pair.parse_verification_report(root, report_path)
    violations = pair.validate_report(root, report)
    assert "reviewer model family does not match reviewer member" in violations
    assert any("different admitted model families" in item for item in violations)


def test_go_requires_executed_evidence(tmp_path) -> None:
    root = tmp_path / "repo"
    base = init_repo(root)
    head = _reviewed_change(root, base)
    request_path, request_commit = add_request(root, base, head)
    body = report_body(request_path, request_commit).replace("$ pytest -q\n→ passed", "tests passed")
    path, text = event(
        "2026-09-02T10-01-00Z", "claude", "codex", "verification-report", body
    )
    commit(root, {path: text}, "report")
    report = pair.parse_verification_report(root, path)
    assert "GO requires command and output evidence" in pair.validate_report(root, report)


def test_report_recipient_must_match_author(tmp_path) -> None:
    root = tmp_path / "repo"
    base = init_repo(root)
    head = _reviewed_change(root, base)
    request_path, request_commit = add_request(root, base, head, author="agy", author_model="gemini-3.8-flash-high")
    report_path, _ = add_report(
        root, request_path, request_commit, recipient="codex"
    )
    report = pair.parse_verification_report(root, report_path)
    assert "report recipient does not match request author" in pair.validate_report(root, report)


def test_fail_can_be_superseded_by_exact_remediation_range(tmp_path) -> None:
    root = tmp_path / "repo"
    base = init_repo(root)
    first_head = _reviewed_change(root, base)
    request1, request1_commit = add_request(root, base, first_head)
    fail_path, fail_commit = add_report(
        root, request1, request1_commit, verdict="FAIL"
    )
    second_head = commit(root, {"pipeline/control.py": "enabled = False\n"}, "fix")
    request2, request2_commit = add_request(
        root, first_head, second_head, stamp="2026-09-02T10-02-00Z"
    )
    report2, _ = add_report(
        root,
        request2,
        request2_commit,
        stamp="2026-09-02T10-03-00Z",
        supersedes=f"{fail_path}@{fail_commit}",
    )
    assert pair.validate_report(root, pair.parse_verification_report(root, report2)) == []


def test_remediation_cannot_skip_the_failed_head(tmp_path) -> None:
    root = tmp_path / "repo"
    base = init_repo(root)
    first_head = _reviewed_change(root, base)
    request1, request1_commit = add_request(root, base, first_head)
    fail_path, fail_commit = add_report(root, request1, request1_commit, verdict="FAIL")
    second_head = commit(root, {"pipeline/control.py": "enabled = False\n"}, "fix")
    request2, request2_commit = add_request(
        root, base, second_head, stamp="2026-09-02T10-02-00Z"
    )
    report2, _ = add_report(
        root,
        request2,
        request2_commit,
        stamp="2026-09-02T10-03-00Z",
        supersedes=f"{fail_path}@{fail_commit}",
    )
    violations = pair.validate_report(root, pair.parse_verification_report(root, report2))
    assert "remediation base must equal the failed reviewed head" in violations


def test_request_composer_resolves_refs_and_self_checks_shape(tmp_path) -> None:
    root = tmp_path / "repo"
    base = init_repo(root)
    head = _reviewed_change(root, base)
    body = pair.compose_request(
        root,
        author_member="codex",
        author_model="gpt-5.6-sol",
        reviewer_member="claude",
        risk_class="high-risk-control",
        base_rev=base[:12],
        head_rev="HEAD",
        outcome="Review this range.",
        abuse_assessments=("Identity laundering",),
    )
    assert f"Reviewed base: {base}" in body
    assert f"Reviewed head: {head}" in body
    assert "Author seat:" not in body
    assert git(root, "status", "--porcelain") == ""


def test_envelope_sender_accepts_online_and_plain() -> None:
    text_online = "**When:** 2026-09-04T12:00:00Z · **From:** codex (online)\n"
    text_plain = "**When:** 2026-09-04T12:00:00Z · **From:** codex\n"
    assert pair._envelope_sender(text_online) == "codex"
    assert pair._envelope_sender(text_plain) == "codex"
    with pytest.raises(pair.CompactPairError, match="missing or duplicate envelope sender"):
        pair._envelope_sender("**When:** 2026-09-04T12:00:00Z\n")
    with pytest.raises(pair.CompactPairError, match="missing or duplicate envelope sender"):
        pair._envelope_sender(text_online + text_plain)


def test_review_pair_validates_without_online_or_cursorless(tmp_path) -> None:
    root = tmp_path / "repo"
    base = init_repo(root)
    head = _reviewed_change(root, base)
    path_req, text_req = event(
        "2026-09-04T12-00-00Z",
        "codex",
        "claude",
        "verify-request",
        request_body(base, head),
    )
    # Strip (online) and Cursor at send: cursorless
    text_req = text_req.replace(" (online)", "").replace("\n\nCursor at send: cursorless\n", "\n")
    req_commit = commit(root, {path_req: text_req}, "request without ceremony")

    path_rep, text_rep = event(
        "2026-09-04T12-05-00Z",
        "claude",
        "codex",
        "verification-report",
        report_body(path_req, req_commit),
        subject="GO",
    )
    text_rep = text_rep.replace(" (online)", "").replace("\n\nCursor at send: cursorless\n", "\n")
    commit(root, {path_rep: text_rep}, "report without ceremony")

    request = pair.parse_verify_request(root, path_req, req_commit)
    report = pair.parse_verification_report(root, path_rep)
    assert request.author_member == "codex"
    assert report.reviewer_member == "claude"
    assert pair.validate_report(root, report) == []

