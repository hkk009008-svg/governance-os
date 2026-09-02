from __future__ import annotations

import ci_admission_gate as gate
from formal_review_support import add_report, add_request, commit, git, init_repo


def test_range_without_authority_surface_is_admitted(tmp_path) -> None:
    root = tmp_path / "repo"
    base = init_repo(root)
    head = commit(root, {"notes.txt": "ordinary\n"}, "ordinary")
    outcome = gate.evaluate(root, base, head)
    assert outcome.authority_commits == {}
    assert outcome.admitted


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


def test_deleted_historical_reports_are_not_replayed(tmp_path) -> None:
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
    assert outcome.skipped_reports == []


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
