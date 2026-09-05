from __future__ import annotations

import pytest

import ci_admission_gate as gate
from formal_review_support import (
    add_report,
    add_request,
    commit,
    event,
    git,
    init_repo,
    report_body,
)


def test_range_without_authority_surface_is_admitted(tmp_path) -> None:
    root = tmp_path / "repo"
    base = init_repo(root)
    head = commit(root, {"notes.txt": "ordinary\n"}, "ordinary")
    outcome = gate.evaluate(root, base, head)
    assert outcome.authority_commits == {}
    assert outcome.admitted


@pytest.mark.parametrize("mutation", ["delete", "rewrite", "restore", "rename", "symlink"])
@pytest.mark.parametrize("introduced_in_range", [False, True])
def test_formal_artifact_mutations_block_even_mailbox_only_ranges(
    tmp_path, mutation, introduced_in_range
) -> None:
    root = tmp_path / "repo"
    base = init_repo(root)
    candidate = commit(root, {"notes.txt": "ordinary\n"}, "candidate")
    request, request_commit = add_request(root, base, candidate)
    report, report_commit = add_report(root, request, request_commit, verdict="FAIL")
    integration_base = candidate if introduced_in_range else report_commit
    original = (root / report).read_text()
    if mutation == "rewrite":
        head = commit(root, {report: original.replace("VERDICT: FAIL", "VERDICT: GO")}, "rewrite")
    elif mutation == "rename":
        git(root, "mv", report, "retired-report.md")
        git(root, "commit", "-qm", "rename")
        head = git(root, "rev-parse", "HEAD")
    else:
        git(root, "rm", "--", report)
        if mutation == "symlink":
            (root / report).symlink_to("../../../../notes.txt")
            git(root, "add", "--", report)
        git(root, "commit", "-qm", "retire")
        head = git(root, "rev-parse", "HEAD")
        if mutation == "restore":
            head = commit(root, {report: original}, "restore identical bytes")
    outcome = gate.evaluate(root, integration_base, head)
    assert not outcome.admitted, gate.render(outcome)
    assert "append-only" in gate.render(outcome)
    assert report in gate.render(outcome)


def test_plain_fail_then_sibling_go_does_not_clear_the_fail(tmp_path) -> None:
    root = tmp_path / "repo"
    base = init_repo(root)
    candidate = commit(root, {"pipeline/control.py": "bad\n"}, "candidate")
    request, request_commit = add_request(root, base, candidate)
    fail, fail_commit = add_report(root, request, request_commit, verdict="FAIL")
    git(root, "checkout", "-qb", "second-opinion", request_commit)
    add_report(root, request, request_commit, stamp="2026-09-02T10-02-00Z")
    git(root, "merge", "-q", "--no-ff", fail_commit, "-m", "combine opinions")
    outcome = gate.evaluate(root, base, git(root, "rev-parse", "HEAD"))
    assert not outcome.admitted
    assert outcome.blocking_failures[0][0] == fail


def test_merge_cannot_drop_a_report_from_only_its_second_parent(tmp_path) -> None:
    root = tmp_path / "repo"
    base = init_repo(root)
    candidate = commit(root, {"notes.txt": "ordinary\n"}, "candidate")
    request, request_commit = add_request(root, base, candidate)
    report, report_commit = add_report(root, request, request_commit, verdict="FAIL")
    git(root, "checkout", "-qb", "integration", request_commit)
    commit(root, {"other.txt": "ordinary\n"}, "diverge")
    git(root, "merge", "-q", "-s", "ours", "--no-ff", report_commit, "-m", "drop report")
    head = git(root, "rev-parse", "HEAD")
    outcome = gate.evaluate(root, candidate, head)
    assert not outcome.admitted
    assert any(f"{head}: D {report}" == item for item in outcome.artifact_mutations)


def test_cli_rejects_request_rewrite_but_accepts_ordinary_work(tmp_path, capsys) -> None:
    root = tmp_path / "repo"
    base = init_repo(root)
    candidate = commit(root, {"notes.txt": "ordinary\n"}, "candidate")
    assert gate.main(["--root", str(root), "--base", base, "--head", candidate]) == 0
    request, request_commit = add_request(root, base, candidate)
    changed = (root / request).read_text().replace("Review the exact", "Do not review the exact")
    head = commit(root, {request: changed}, "rewrite request")
    assert gate.main(["--root", str(root), "--base", request_commit, "--head", head]) == 1
    assert "append-only" in capsys.readouterr().out


def test_remediation_supersedes_fail_without_erasing_history(tmp_path) -> None:
    root = tmp_path / "repo"
    base = init_repo(root)
    first = commit(root, {"pipeline/control.py": "bad\n"}, "candidate")
    request1, request1_commit = add_request(root, base, first)
    fail, fail_commit = add_report(root, request1, request1_commit, verdict="FAIL")
    fixed = commit(root, {"pipeline/control.py": "fixed\n"}, "fix")
    request2, request2_commit = add_request(root, first, fixed, stamp="2026-09-02T10-02-00Z")
    _, head = add_report(root, request2, request2_commit, stamp="2026-09-02T10-03-00Z", supersedes=f"{fail}@{fail_commit}")
    outcome = gate.evaluate(root, first, head)
    assert outcome.admitted, gate.render(outcome)
    assert (root / fail).exists()


def test_unrelated_retained_fail_is_not_a_global_veto(tmp_path) -> None:
    root = tmp_path / "repo"
    base = init_repo(root)
    old = commit(root, {"pipeline/old.py": "bad\n"}, "old candidate")
    request1, request1_commit = add_request(root, base, old)
    fail, integration_base = add_report(root, request1, request1_commit, verdict="FAIL")
    candidate = commit(root, {"pipeline/new.py": "good\n"}, "new candidate")
    request2, request2_commit = add_request(root, integration_base, candidate, stamp="2026-09-02T10-02-00Z")
    _, head = add_report(root, request2, request2_commit, stamp="2026-09-02T10-03-00Z")
    outcome = gate.evaluate(root, integration_base, head)
    assert outcome.admitted, gate.render(outcome)
    assert (root / fail).exists()


def test_authority_change_without_report_is_blocked(tmp_path) -> None:
    root = tmp_path / "repo"
    base = init_repo(root)
    head = commit(root, {"pipeline/control.py": "enabled = True\n"}, "candidate")
    outcome = gate.evaluate(root, base, head)
    assert head in outcome.uncovered
    assert not outcome.admitted


def test_high_risk_cross_family_go_admits_exact_range(tmp_path) -> None:
    root = tmp_path / "repo"
    base = init_repo(root)
    candidate = commit(root, {"pipeline/control.py": "enabled = True\n"}, "candidate")
    request_path, request_commit = add_request(root, base, candidate)
    _report_path, report_commit = add_report(root, request_path, request_commit)
    outcome = gate.evaluate(root, base, report_commit)
    assert outcome.admitted
    assert set(outcome.authority_commits) == {candidate}
    assert len(outcome.coverages) == 1


def test_evidence_free_nits_cannot_admit_authority_surface(tmp_path) -> None:
    root = tmp_path / "repo"
    base = init_repo(root)
    candidate = commit(root, {"pipeline/control.py": "enabled = True\n"}, "candidate")
    request_path, request_commit = add_request(root, base, candidate)
    body = report_body(
        request_path, request_commit, verdict="NITS"
    ).replace("$ pytest -q\n→ passed", "tests not executed")
    report_path, report_text = event(
        "2026-09-02T10-01-00Z",
        "claude",
        "codex",
        "verification-report",
        body,
    )
    report_commit = commit(root, {report_path: report_text}, "report")

    outcome = gate.evaluate(root, base, report_commit)

    assert not outcome.admitted
    assert candidate in outcome.uncovered
    assert any(
        "admitting verdict requires command and output evidence" in reason
        for _path, reason in outcome.skipped_reports
    )


def test_material_review_does_not_admit_authority_surface(tmp_path) -> None:
    root = tmp_path / "repo"
    base = init_repo(root)
    candidate = commit(root, {"pipeline/control.py": "enabled = True\n"}, "candidate")
    request_path, request_commit = add_request(
        root, base, candidate, risk="material-behavior"
    )
    _report_path, report_commit = add_report(
        root, request_path, request_commit, high_risk=False
    )
    outcome = gate.evaluate(root, base, report_commit)
    assert not outcome.admitted
    assert candidate in outcome.uncovered
    assert any("authority surfaces require" in reason for _path, reason in outcome.skipped_reports)


def test_fail_blocks_the_reviewed_authority_range(tmp_path) -> None:
    root = tmp_path / "repo"
    base = init_repo(root)
    candidate = commit(root, {"pipeline/control.py": "enabled = True\n"}, "candidate")
    request_path, request_commit = add_request(root, base, candidate)
    _report_path, report_commit = add_report(
        root, request_path, request_commit, verdict="FAIL"
    )
    outcome = gate.evaluate(root, base, report_commit)
    assert not outcome.admitted
    assert outcome.blocking_failures


def test_invalid_reviewer_identity_cannot_admit(tmp_path) -> None:
    root = tmp_path / "repo"
    base = init_repo(root)
    candidate = commit(root, {"pipeline/control.py": "enabled = True\n"}, "candidate")
    request_path, request_commit = add_request(root, base, candidate)
    _report_path, report_commit = add_report(
        root, request_path, request_commit, reviewer_model="gpt-5.6-terra"
    )
    outcome = gate.evaluate(root, base, report_commit)
    assert not outcome.admitted
    assert any("reviewer model family" in reason for _path, reason in outcome.skipped_reports)


def test_report_added_then_deleted_in_range_is_not_evidence(tmp_path) -> None:
    root = tmp_path / "repo"
    base = init_repo(root)
    candidate = commit(root, {"pipeline/control.py": "enabled = True\n"}, "candidate")
    request_path, request_commit = add_request(root, base, candidate)
    report_path, _ = add_report(root, request_path, request_commit)
    git(root, "rm", "--", report_path)
    git(root, "commit", "-q", "-m", "prune old report")
    new_head = git(root, "rev-parse", "HEAD")
    outcome = gate.evaluate(root, base, new_head)
    assert not outcome.admitted
    assert any(report_path in item for item in outcome.artifact_mutations)
    assert "append-only" in gate.render(outcome)


def test_render_summarizes_skipped_reports_unless_verbose() -> None:
    outcome = gate.Outcome(
        base="a" * 40,
        head="b" * 40,
        authority_commits={"c" * 40: ("pipeline/control.py",)},
        skipped_reports=[
            ("first-report.md", "artifact path is not canonical"),
            ("second-report.md", "artifact path is not canonical"),
        ],
        blocking_failures=[("active-fail.md", frozenset({"c" * 40}))],
        uncovered={"c" * 40: ("pipeline/control.py",)},
    )

    compact = gate.render(outcome)
    verbose = gate.render(outcome, verbose=True)

    assert "non-admitting reports: 2" in compact
    assert "2 x artifact path is not canonical" in compact
    assert "first-report.md" not in compact
    assert "first-report.md" in verbose
    assert "active FAIL: active-fail.md" in compact
    assert "cccccccccccc touches pipeline/control.py" in compact


def test_deleted_trusted_base_fail_remains_blocking_outside_its_range(tmp_path) -> None:
    root = tmp_path / "repo"
    original_base = init_repo(root)
    failed_head = commit(
        root, {"pipeline/old_control.py": "enabled = False\n"}, "failed candidate"
    )
    failed_request, failed_request_commit = add_request(
        root, original_base, failed_head
    )
    failed_report, _failed_report_commit = add_report(
        root, failed_request, failed_request_commit, verdict="FAIL"
    )
    integration_base = git(root, "rev-parse", "HEAD")

    (root / "pipeline/new_control.py").write_text("enabled = True\n", encoding="utf-8")
    git(root, "add", "--", "pipeline/new_control.py")
    git(root, "rm", "--", failed_report)
    git(root, "commit", "-q", "-m", "replace failed control")
    reviewed_head = git(root, "rev-parse", "HEAD")
    request_path, request_commit = add_request(
        root,
        integration_base,
        reviewed_head,
        stamp="2026-09-02T10-02-00Z",
    )
    _report_path, candidate_head = add_report(
        root,
        request_path,
        request_commit,
        stamp="2026-09-02T10-03-00Z",
    )

    outcome = gate.evaluate(root, integration_base, candidate_head)

    assert not outcome.admitted, gate.render(outcome)
    assert outcome.uncovered == {}
    assert any(failed_report in item for item in outcome.artifact_mutations)


def test_clean_merge_of_review_chain_inherits_coverage(tmp_path) -> None:
    root = tmp_path / "repo"
    base = init_repo(root)
    git(root, "branch", "reviewed")
    candidate = commit(root, {"pipeline/control.py": "enabled = True\n"}, "candidate")
    request_path, request_commit = add_request(root, base, candidate)
    _report_path, _report_commit = add_report(root, request_path, request_commit)
    git(root, "branch", "-f", "reviewed", "HEAD")
    git(root, "checkout", "-q", "-B", "integration", base)
    git(root, "merge", "-q", "--no-ff", "reviewed", "-m", "merge reviewed chain")
    merge = git(root, "rev-parse", "HEAD")
    outcome = gate.evaluate(root, base, merge)
    assert outcome.admitted
    assert merge in outcome.authority_commits


def test_clean_merge_inherits_when_integration_parent_is_in_reviewed_head(tmp_path) -> None:
    root = tmp_path / "repo"
    base = init_repo(root)
    commit(root, {"pipeline/control.py": "enabled = True\n"}, "candidate")
    git(root, "branch", "reviewed")

    git(root, "checkout", "-q", "-B", "integration", base)
    integration = commit(
        root, {"pipeline/integration.py": "enabled = True\n"}, "integration"
    )
    git(root, "checkout", "-q", "reviewed")
    git(root, "merge", "-q", "--no-ff", "integration", "-m", "sync integration")
    reviewed_head = git(root, "rev-parse", "HEAD")
    request_path, request_commit = add_request(root, base, reviewed_head)
    _report_path, _report_commit = add_report(root, request_path, request_commit)

    git(root, "checkout", "-q", "integration")
    git(root, "merge", "-q", "--no-ff", "reviewed", "-m", "land reviewed chain")
    merge = git(root, "rev-parse", "HEAD")

    outcome = gate.evaluate(root, integration, merge)

    assert outcome.admitted, gate.render(outcome)
    assert merge in outcome.authority_commits


def test_clean_merge_does_not_inherit_from_unreviewed_first_parent(tmp_path) -> None:
    root = tmp_path / "repo"
    base = init_repo(root)
    reviewed_base = commit(root, {"notes.txt": "candidate\n"}, "candidate")
    reviewed_head = commit(
        root, {"pipeline/control.py": "enabled = True\n"}, "reviewed control"
    )
    request_path, request_commit = add_request(root, reviewed_base, reviewed_head)
    _report_path, report_commit = add_report(root, request_path, request_commit)
    git(root, "branch", "reviewed", report_commit)

    git(root, "checkout", "-q", "-B", "unreviewed", base)
    git(root, "commit", "-q", "--allow-empty", "-m", "unreviewed first parent")
    unreviewed = git(root, "rev-parse", "HEAD")
    git(root, "merge", "-q", "--no-ff", "reviewed", "-m", "merge reviewed chain")
    merge = git(root, "rev-parse", "HEAD")

    outcome = gate.evaluate(root, unreviewed, merge)

    assert not outcome.admitted
    assert merge in outcome.uncovered
