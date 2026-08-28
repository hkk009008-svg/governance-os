from pathlib import Path

import compact_pair_loop as pair
from test_compact_pair_loop import (
    SECOND_REPORT_PATH,
    SECOND_REQUEST_PATH,
    _commit_report,
    _cross_repo,
    _git,
    _request_text,
)


def test_cross_repository_remediation_starts_at_failed_reviewed_head(
    tmp_path: Path,
) -> None:
    root, target, base, failed_head, trigger = _cross_repo(tmp_path)
    fail_path, fail_commit = _commit_report(
        root, base, failed_head, trigger,
        reviewed_repository=target.as_posix(), verdict="FAIL",
    )
    (target / "feature.py").write_text("VALUE = 3\n", encoding="utf-8")
    _git(target, "add", "feature.py")
    _git(target, "commit", "-q", "-m", "fix: remediate failed review")
    remediation_head = _git(target, "rev-parse", "HEAD")
    failed_ref = f"{fail_path}@{fail_commit}"

    (root / SECOND_REQUEST_PATH).write_text(
        _request_text(
            failed_head, remediation_head,
            reviewed_repository=target.as_posix(),
            remediates_failed_report=failed_ref,
        ),
        encoding="utf-8",
    )
    _git(root, "add", SECOND_REQUEST_PATH)
    _git(root, "commit", "-q", "-m", "coord(pair): request target remediation")
    trigger = _git(root, "rev-parse", "HEAD")
    _commit_report(
        root, failed_head, remediation_head, trigger,
        report_path=SECOND_REPORT_PATH, request_path=SECOND_REQUEST_PATH,
        reviewed_repository=target.as_posix(), supersedes=failed_ref,
    )

    report = pair.parse_verification_report(root, root / SECOND_REPORT_PATH)

    assert pair.validate_report(root, report) == []
