from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

import compact_pair_loop as pair


REQUEST_PATH = (
    "coordination/mailbox/sent/"
    "2026-07-17T08-00-00Z-director-to-operator-verify-request.md"
)
REPORT_PATH = (
    "coordination/mailbox/sent/"
    "2026-07-17T08-10-00Z-operator-to-all-verification-report.md"
)


def _git(root: Path, *args: str) -> str:
    completed = subprocess.run(
        ["env", "-u", "GIT_INDEX_FILE", "git", *args],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def _request_text(base: str, head: str, *, allowed: str = "scripts/") -> str:
    return f"""\
# Director → Operator: verify compact pair candidate

**When:** 2026-07-17T08:00:00Z · **From:** director (online)

Event type: verify-request
Reviewed head: {head}
Reviewed base: {base}
Author seat: director
Author model: gpt-5.6-sol
Assigned operator: operator

## Acceptance Question

Does the exact candidate satisfy the compact pair contract?

## Allowed Paths

- {allowed}

## Verification Commands

$ env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_feature.py -q

Cursor at send: 0
"""


def _report_text(
    base: str,
    head: str,
    trigger: str,
    *,
    verdict: str = "GO",
    request_path: str = REQUEST_PATH,
    reviewer_seat: str = "operator",
    reviewer_model: str = "gpt-5.6-terra",
    allowed: str = "scripts/",
    evidence: bool = True,
) -> str:
    evidence_block = ""
    if evidence:
        evidence_block = """\

## Evidence

$ env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_feature.py -q
→ 1 passed
"""
    return f"""\
# Operator → All: compact pair verification

**When:** 2026-07-17T08:10:00Z · **From:** operator (online)

Event type: verification-report
VERDICT: {verdict}
Verification request: {request_path}@{trigger}
Reviewed head: {head}
Reviewed base: {base}
Reviewer seat: {reviewer_seat}
Reviewer model: {reviewer_model}
Verification harness: pytest plus independent actual-diff review
Verification context: fresh non-author Operator context

## Allowed Paths

- {allowed}
{evidence_block}

## Findings

None.

Cursor at send: 0
"""


def _repo(
    tmp_path: Path,
    *,
    transform_request=lambda text: text,
    allowed: str = "scripts/",
) -> tuple[Path, str, str, str]:
    root = tmp_path / "repo"
    root.mkdir()
    (root / "scripts").mkdir()
    (root / "scripts/feature.py").write_text("VALUE = 1\n", encoding="utf-8")
    _git(root, "init", "-q")
    _git(root, "config", "user.name", "Compact Pair Test")
    _git(root, "config", "user.email", "compact-pair@example.invalid")
    _git(root, "add", ".")
    _git(root, "commit", "-q", "-m", "chore: base")
    base = _git(root, "rev-parse", "HEAD")

    (root / "scripts/feature.py").write_text("VALUE = 2\n", encoding="utf-8")
    _git(root, "add", "scripts/feature.py")
    _git(root, "commit", "-q", "-m", "feat: candidate")
    head = _git(root, "rev-parse", "HEAD")

    request = root / REQUEST_PATH
    request.parent.mkdir(parents=True)
    request.write_text(
        transform_request(_request_text(base, head, allowed=allowed)),
        encoding="utf-8",
    )
    _git(root, "add", REQUEST_PATH)
    _git(root, "commit", "-q", "-m", "coord(director): request verification")
    trigger = _git(root, "rev-parse", "HEAD")
    return root, base, head, trigger


def _write_report(
    root: Path,
    base: str,
    head: str,
    trigger: str,
    **overrides: object,
) -> Path:
    report = root / REPORT_PATH
    report.write_text(
        _report_text(base, head, trigger, **overrides),
        encoding="utf-8",
    )
    return report


def test_valid_request_and_report_bind_exact_commits_scope_and_independence(
    tmp_path: Path,
) -> None:
    root, base, head, trigger = _repo(tmp_path)
    request = pair.parse_verify_request(root, REQUEST_PATH, trigger)
    report = pair.parse_verification_report(
        root, _write_report(root, base, head, trigger)
    )

    assert request.reviewed_base == base
    assert request.reviewed_head == head
    assert request.allowed_paths == ("scripts/",)
    assert request.commands == (
        "env -u GIT_INDEX_FILE .venv/bin/python -m pytest "
        "tests/unit/test_feature.py -q",
    )
    assert report.verdict == "GO"
    assert pair.validate_report(root, report) == []


@pytest.mark.parametrize(
    "mutation",
    (
        lambda text: text.replace("Event type: verification-report\n", ""),
        lambda text: text.replace(
            "Event type: verification-report\n",
            "Event type: verification-report\nEvent type: verification-report\n",
        ),
    ),
)
def test_report_requires_exactly_one_verification_report_event_marker(
    tmp_path: Path, mutation
) -> None:
    root, base, head, trigger = _repo(tmp_path)
    report = root / REPORT_PATH
    report.write_text(
        mutation(_report_text(base, head, trigger)), encoding="utf-8"
    )

    with pytest.raises(pair.CompactPairError, match="Event type: verification-report"):
        pair.parse_verification_report(root, report)


@pytest.mark.parametrize(
    ("mutation", "reason"),
    (
        (lambda text: text.replace("Reviewed head:", "Missing head:"), "Reviewed head"),
        (
            lambda text: text.replace(
                "Reviewed head:", "Reviewed head: " + "a" * 40 + "\nReviewed head:", 1
            ),
            "duplicate",
        ),
        (
            lambda text: text.replace(
                next(line for line in text.splitlines() if line.startswith("Reviewed head: ")),
                "Reviewed head: deadbee",
            ),
            "full lowercase",
        ),
        (
            lambda text: text.replace(
                next(line for line in text.splitlines() if line.startswith("Reviewed head: ")),
                "Reviewed head: " + "A" * 40,
            ),
            "full lowercase",
        ),
        (
            lambda text: text.replace(
                next(line for line in text.splitlines() if line.startswith("Reviewed head: ")),
                "Reviewed head: " + "f" * 40,
            ),
            "commit",
        ),
    ),
)
def test_request_rejects_missing_duplicate_abbreviated_uppercase_or_mismatched_sha(
    tmp_path: Path, mutation, reason: str
) -> None:
    root, _, _, trigger = _repo(tmp_path, transform_request=mutation)

    with pytest.raises(pair.CompactPairError, match=reason):
        pair.parse_verify_request(root, REQUEST_PATH, trigger)


def test_request_rejects_path_commit_mismatch(tmp_path: Path) -> None:
    root, _, head, _ = _repo(tmp_path)

    with pytest.raises(pair.CompactPairError, match="added by trigger commit"):
        pair.parse_verify_request(root, REQUEST_PATH, head)


@pytest.mark.parametrize(
    ("overrides", "expected"),
    (
        ({"reviewer_seat": "operator2"}, "assigned Operator"),
        ({"reviewer_seat": "director"}, "author seat"),
        ({"reviewer_model": "gpt-5.6-sol"}, "author model"),
        ({"request_path": REQUEST_PATH.replace("08-00-00", "08-00-01")}, "request"),
        ({"allowed": "docs/"}, "allowed paths"),
    ),
)
def test_report_rejects_wrong_identity_binding_or_changed_scope(
    tmp_path: Path, overrides: dict[str, str], expected: str
) -> None:
    root, base, head, trigger = _repo(tmp_path)
    report = pair.parse_verification_report(
        root, _write_report(root, base, head, trigger, **overrides)
    )

    assert any(expected in violation for violation in pair.validate_report(root, report))


def test_report_rejects_request_commit_and_reviewed_range_mismatch(
    tmp_path: Path,
) -> None:
    root, base, head, trigger = _repo(tmp_path)
    report_path = _write_report(root, base, base, head)
    report = pair.parse_verification_report(root, report_path)

    violations = pair.validate_report(root, report)
    assert any("request binding" in item for item in violations)


@pytest.mark.parametrize("verdict", ("NITS", "FAIL"))
def test_truthful_non_go_verdict_needs_no_successful_command_or_external_tool(
    tmp_path: Path, verdict: str
) -> None:
    root, base, head, trigger = _repo(tmp_path)
    report = pair.parse_verification_report(
        root,
        _write_report(
            root,
            base,
            head,
            trigger,
            verdict=verdict,
            evidence=False,
        ),
    )

    assert pair.validate_report(root, report) == []


def test_request_scope_must_cover_every_reviewed_path(tmp_path: Path) -> None:
    root, base, head, trigger = _repo(tmp_path, allowed="docs/")
    report = pair.parse_verification_report(
        root,
        _write_report(root, base, head, trigger, allowed="docs/"),
    )

    assert any("outside allowed paths" in item for item in pair.validate_report(root, report))


def test_report_parser_rejects_non_operator_filename_and_malformed_sha(
    tmp_path: Path,
) -> None:
    root, base, head, trigger = _repo(tmp_path)
    director_path = root / REPORT_PATH.replace("-operator-to-", "-director-to-")
    director_path.write_text(
        _report_text(base, head, trigger).replace(
            f"Reviewed head: {head}", "Reviewed head: DEADBEEF"
        ),
        encoding="utf-8",
    )

    with pytest.raises(pair.CompactPairError, match="canonical Operator"):
        pair.parse_verification_report(root, director_path)
