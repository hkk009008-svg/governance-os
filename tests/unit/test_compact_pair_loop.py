from __future__ import annotations

from pathlib import Path
import io

import pytest


def test_request_reads_are_reused_only_in_one_scope(tmp_path, monkeypatch):
    from formal_review_support import init_repo, commit, add_request
    root = tmp_path / "repo"
    base = init_repo(root)
    head = commit(root, {"notes.txt": "change\n"}, "candidate")
    path, trigger = add_request(root, base, head)
    real = pair.parse_verify_request_structure
    calls = []
    def read(*args):
        calls.append(args)
        return real(*args)
    monkeypatch.setattr(pair, "parse_verify_request_structure", read)
    with pair.request_read_scope():
        first = pair.parse_verify_request(root, path, trigger)
        assert pair.parse_verify_request(root, path, trigger) == first
        assert len(calls) == 1
        # Identical path and SHA in another repository must not reuse this result.
        other = tmp_path / "other"
        init_repo(other)
        with pytest.raises(pair.CompactPairError):
            pair.parse_verify_request(other, path, trigger)
        assert len(calls) == 2
    pair.parse_verify_request(root, path, trigger)
    assert len(calls) == 3


def test_request_scope_does_not_reuse_failures_or_survive_exceptions(tmp_path, monkeypatch):
    from formal_review_support import init_repo, commit, add_request
    root = tmp_path / "repo"
    base = init_repo(root)
    head = commit(root, {"notes.txt": "change\n"}, "candidate")
    path, trigger = add_request(root, base, head)
    with pytest.raises(RuntimeError, match="abort"):
        with pair.request_read_scope():
            pair.parse_verify_request(root, path, trigger)
            raise RuntimeError("abort")
    real = pair.parse_verify_request_structure
    calls = []
    def unavailable(*args):
        calls.append(args)
        raise pair.CompactPairError("unavailable")
    monkeypatch.setattr(pair, "parse_verify_request_structure", unavailable)
    with pair.request_read_scope():
        for _ in range(2):
            with pytest.raises(pair.CompactPairError, match="unavailable"):
                pair.parse_verify_request(root, path, trigger)
        assert len(calls) == 2
        monkeypatch.setattr(pair, "parse_verify_request_structure", real)
        assert pair.parse_verify_request(root, path, trigger).trigger_commit == trigger

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


@pytest.mark.parametrize("verdict", ("GO", "NITS"))
def test_admitting_verdict_requires_executed_evidence(
    tmp_path, verdict: str
) -> None:
    root = tmp_path / "repo"
    base = init_repo(root)
    head = _reviewed_change(root, base)
    request_path, request_commit = add_request(root, base, head)
    body = report_body(
        request_path, request_commit, verdict=verdict
    ).replace("$ pytest -q\n→ passed", "tests passed")
    path, text = event(
        "2026-09-02T10-01-00Z", "claude", "codex", "verification-report", body
    )
    commit(root, {path: text}, "report")
    report = pair.parse_verification_report(root, path)
    assert "admitting verdict requires command and output evidence" in pair.validate_report(
        root, report
    )


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
    evidence_path = "coordination/mailbox/sent/2026-09-04T12-00-00Z-codex-to-claude-verification-report.md"
    evidence_commit = commit(
        root,
        {evidence_path: "Event type: verification-report\nVERDICT: GO\n"},
        "review: evidence",
    )
    head = _reviewed_change(root, evidence_commit)
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
        finding_refs=(f"{evidence_path}@{evidence_commit}",),
    )
    assert f"Reviewed base: {base}" in body
    assert f"Reviewed head: {head}" in body
    assert "Author seat:" not in body
    assert "## Finding Refs" in body
    assert f"- {evidence_path}@{evidence_commit}" in body
    assert git(root, "status", "--porcelain") == ""


def test_compose_refuses_a_finding_ref_whose_object_does_not_exist(tmp_path) -> None:
    root = tmp_path / "repo"
    base = init_repo(root)
    relative = (
        "coordination/mailbox/sent/"
        "2026-07-26T00-00-00Z-operator-to-director-verification-report.md"
    )
    real_commit = commit(
        root,
        {relative: "Event type: verification-report\nVERDICT: FAIL\n"},
        "review: cited evidence",
    )
    arguments: dict[str, object] = {
        "author_member": "codex",
        "author_model": "gpt-5.6-sol",
        "reviewer_member": "claude",
        "risk_class": "high-risk-control",
        "base_rev": base,
        "head_rev": "HEAD",
        "outcome": "Cites evidence.",
        "abuse_assessments": ("Identity laundering",),
    }

    # The resolvable reference composes
    body = pair.compose_request(
        root, **arguments, finding_refs=(f"{relative}@{real_commit}",)
    )
    assert f"{relative}@{real_commit}" in body

    absent_path = (
        "coordination/mailbox/sent/"
        "2026-01-01T00-00-00Z-operator-to-director-verification-report.md"
    )
    for reference in (f"{relative}@{'0' * 40}", f"{absent_path}@{real_commit}"):
        with pytest.raises(
            pair.CompactPairError, match="names an object that does not exist"
        ):
            pair.compose_request(root, **arguments, finding_refs=(reference,))


def test_compose_still_accepts_a_digest_reference_it_cannot_verify(tmp_path) -> None:
    root = tmp_path / "repo"
    base = init_repo(root)
    _reviewed_change(root, base)
    body = pair.compose_request(
        root,
        author_member="codex",
        author_model="gpt-5.6-sol",
        reviewer_member="claude",
        risk_class="high-risk-control",
        base_rev=base,
        head_rev="HEAD",
        outcome="Cites a digest.",
        abuse_assessments=("Identity laundering",),
        finding_refs=("sha256:" + "b" * 64,),
    )
    assert "sha256:" + "b" * 64 in body


def test_compose_refuses_duplicate_finding_refs(tmp_path) -> None:
    root = tmp_path / "repo"
    base = init_repo(root)
    relative = "coordination/mailbox/sent/2026-07-26T00-00-00Z-test.md"
    commit_sha = commit(
        root,
        {relative: "Event type: verification-report\nVERDICT: FAIL\n"},
        "review: test",
    )
    ref = f"{relative}@{commit_sha}"
    with pytest.raises(pair.CompactPairError, match="finding refs must be unique"):
        pair.compose_request(
            root,
            author_member="codex",
            author_model="gpt-5.6-sol",
            reviewer_member="claude",
            risk_class="high-risk-control",
            base_rev=base,
            head_rev="HEAD",
            outcome="Duplicate refs.",
            abuse_assessments=("Identity laundering",),
            finding_refs=(ref, ref),
        )


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


def test_compose_request_cli_with_finding_ref(tmp_path, monkeypatch, capsys) -> None:
    root = tmp_path / "repo"
    base = init_repo(root)
    relative = "coordination/mailbox/sent/2026-07-26T00-00-00Z-test.md"
    commit_sha = commit(root, {relative: "Event type: verification-report\nVERDICT: FAIL\n"}, "test")
    head = _reviewed_change(root, commit_sha)
    ref = f"{relative}@{commit_sha}"
    monkeypatch.setattr("sys.stdin", io.StringIO("CLI outcome"))
    exit_code = pair._main([
        "compose-request",
        "--repo-root", str(root),
        "--author", "codex",
        "--author-model", "gpt-5.6-sol",
        "--reviewer", "claude",
        "--risk-class", "high-risk-control",
        "--base", base,
        "--head", head,
        "--abuse-class", "Identity laundering",
        "--finding-ref", ref,
    ])
    assert exit_code == 0
    captured = capsys.readouterr()
    assert f"- {ref}" in captured.out
    assert "## Finding Refs" in captured.out

    # Non-existent reference fails closed with exit code 1
    monkeypatch.setattr("sys.stdin", io.StringIO("CLI outcome"))
    exit_code_bad = pair._main([
        "compose-request",
        "--repo-root", str(root),
        "--author", "codex",
        "--author-model", "gpt-5.6-sol",
        "--reviewer", "claude",
        "--risk-class", "high-risk-control",
        "--base", base,
        "--head", head,
        "--abuse-class", "Identity laundering",
        "--finding-ref", f"{relative}@{'0' * 40}",
    ])
    assert exit_code_bad == 1
