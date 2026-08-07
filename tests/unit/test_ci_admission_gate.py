"""Behavioral tests for the risk-aware admission gate.

Each scenario builds a throwaway repository, lands commits on and off the
authority surfaces, and asserts what the gate admits. The gate must delegate
report validity to the canonical compact_pair_loop machinery, so one scenario
proves a same-family high-risk reviewer is rejected by that delegation.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

from scripts import ci_admission_gate as gate


REQUEST_PATH = (
    "coordination/mailbox/sent/"
    "2026-08-07T12-00-00Z-director-to-operator-verify-request.md"
)
REPORT_PATH = (
    "coordination/mailbox/sent/"
    "2026-08-07T12-10-00Z-operator-to-all-verification-report.md"
)
EVIDENCE_PATH = (
    "coordination/mailbox/sent/"
    "2026-08-07T11-55-00Z-operator-to-director-findings.md"
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


def _bullets(heading: str, values: tuple[str, ...]) -> str:
    body = "\n".join(f"- {value}" for value in values)
    return f"## {heading}\n\n{body}\n"


def _request_text(
    base: str,
    head: str,
    *,
    risk_class: str,
    finding_refs: tuple[str, ...],
) -> str:
    abuse = (
        ""
        if risk_class != "high-risk-control"
        else "\n"
        + _bullets(
            "Abuse Class Assessment",
            ("untrusted request fields cannot widen authority",),
        )
    )
    return f"""\
# Pair seat -> Operator: verify outcome

**When:** 2026-08-07T12:00:00Z · **From:** director (online)

Event type: verify-request
Reviewed head: {head}
Reviewed base: {base}
Author seat: director
Author model: gpt-5.6-sol
Assigned operator: operator
Risk class: {risk_class}

## Outcome

The committed change satisfies the routed maintenance outcome.

{abuse}
{_bullets("Finding Refs", finding_refs)}
Cursor at send: 0
"""


def _report_text(
    base: str,
    head: str,
    trigger: str,
    *,
    verdict: str,
    risk_class: str,
    reviewer_model: str,
    finding_refs: tuple[str, ...],
) -> str:
    abuse_binding = (
        ""
        if risk_class != "high-risk-control"
        else "Abuse Class Assessment: bound-to-request\n"
    )
    dispositions = tuple(f"{ref}: addressed" for ref in finding_refs)
    return f"""\
# Operator -> Pair seat: outcome verification

**When:** 2026-08-07T12:10:00Z · **From:** operator (online)

Event type: verification-report
VERDICT: {verdict}
Verification request: {REQUEST_PATH}@{trigger}
Reviewed head: {head}
Reviewed base: {base}
Reviewer seat: operator
Reviewer model: {reviewer_model}
Risk class: {risk_class}
{abuse_binding}

{_bullets("Finding Refs", finding_refs)}
{_bullets("Finding Dispositions", dispositions)}

## Evidence

$ independent actual-diff inspection
→ reviewed range satisfies the outcome

## Findings

None.

Cursor at send: 0
"""


def _init_repo(tmp_path: Path) -> tuple[Path, str]:
    root = tmp_path / "repo"
    (root / "scripts").mkdir(parents=True)
    (root / "scripts/feature.py").write_text("VALUE = 1\n", encoding="utf-8")
    _git(root, "init", "-q")
    _git(root, "config", "user.name", "Admission Gate Test")
    _git(root, "config", "user.email", "admission-gate@example.invalid")
    _git(root, "config", "commit.gpgsign", "false")
    _git(root, "add", ".")
    _git(root, "commit", "-q", "-m", "chore: base")
    return root, _git(root, "rev-parse", "HEAD")


def _commit_file(root: Path, relative: str, content: str, message: str) -> str:
    target = root / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    _git(root, "add", relative)
    _git(root, "commit", "-q", "-m", message)
    return _git(root, "rev-parse", "HEAD")


def _mint_evidence(root: Path) -> str:
    commit = _commit_file(
        root,
        EVIDENCE_PATH,
        "Event type: findings\nNo blocking findings.\n",
        "coord: cited evidence",
    )
    return f"{EVIDENCE_PATH}@{commit}"


def _land_pair(
    root: Path,
    reviewed_base: str,
    reviewed_head: str,
    *,
    verdict: str = "GO",
    risk_class: str = "high-risk-control",
    reviewer_model: str = "claude-opus-5",
) -> None:
    refs = (_mint_evidence(root),)
    _commit_file(
        root,
        REQUEST_PATH,
        _request_text(
            reviewed_base, reviewed_head, risk_class=risk_class, finding_refs=refs
        ),
        "review: request verification",
    )
    trigger = _git(root, "rev-parse", "HEAD")
    _commit_file(
        root,
        REPORT_PATH,
        _report_text(
            reviewed_base,
            reviewed_head,
            trigger,
            verdict=verdict,
            risk_class=risk_class,
            reviewer_model=reviewer_model,
            finding_refs=refs,
        ),
        "review: publish verdict",
    )


def test_range_without_authority_surfaces_is_admitted(tmp_path: Path) -> None:
    root, base = _init_repo(tmp_path)
    _commit_file(root, "scripts/feature.py", "VALUE = 2\n", "feat: ordinary")
    head = _git(root, "rev-parse", "HEAD")

    outcome = gate.evaluate(root, base, head)

    assert outcome.admitted
    assert outcome.authority_commits == {}
    assert "admitted without review requirement" in gate.render(outcome)


def test_authority_commit_without_report_is_blocked(tmp_path: Path) -> None:
    root, base = _init_repo(tmp_path)
    touched = _commit_file(
        root, "scripts/cursor_hook_policy.py", "POLICY = 1\n", "feat: hook policy"
    )
    head = _git(root, "rev-parse", "HEAD")

    outcome = gate.evaluate(root, base, head)

    assert not outcome.admitted
    assert touched in outcome.uncovered
    assert "scripts/cursor_hook_policy.py" in outcome.uncovered[touched]
    assert "BLOCKED" in gate.render(outcome)


def test_valid_high_risk_go_report_admits_range(tmp_path: Path) -> None:
    root, base = _init_repo(tmp_path)
    reviewed_head = _commit_file(
        root, "scripts/cursor_hook_policy.py", "POLICY = 1\n", "feat: hook policy"
    )
    _land_pair(root, base, reviewed_head)
    head = _git(root, "rev-parse", "HEAD")

    outcome = gate.evaluate(root, base, head)

    assert outcome.admitted, gate.render(outcome)
    assert [coverage.verdict for coverage in outcome.coverages] == ["GO"]


def test_fail_verdict_does_not_admit(tmp_path: Path) -> None:
    root, base = _init_repo(tmp_path)
    reviewed_head = _commit_file(
        root, "scripts/mailbox_writer.py", "WRITER = 1\n", "feat: writer"
    )
    _land_pair(root, base, reviewed_head, verdict="FAIL")
    head = _git(root, "rev-parse", "HEAD")

    outcome = gate.evaluate(root, base, head)

    assert not outcome.admitted
    assert any("FAIL" in reason for _, reason in outcome.skipped_reports)


def test_material_behavior_report_does_not_admit_authority_surface(
    tmp_path: Path,
) -> None:
    root, base = _init_repo(tmp_path)
    reviewed_head = _commit_file(
        root, "coordination/bin/send-event", "#!/bin/sh\n", "feat: writer shim"
    )
    _land_pair(
        root,
        base,
        reviewed_head,
        risk_class="material-behavior",
        reviewer_model="gpt-5.6-terra",
    )
    head = _git(root, "rev-parse", "HEAD")

    outcome = gate.evaluate(root, base, head)

    assert not outcome.admitted
    assert any(
        "require an explicit high-risk-control" in reason
        for _, reason in outcome.skipped_reports
    )


def test_same_family_high_risk_reviewer_is_rejected_by_canonical_validator(
    tmp_path: Path,
) -> None:
    root, base = _init_repo(tmp_path)
    reviewed_head = _commit_file(
        root, "scripts/cursor_hook_policy.py", "POLICY = 1\n", "feat: hook policy"
    )
    _land_pair(root, base, reviewed_head, reviewer_model="gpt-5.6-terra")
    head = _git(root, "rev-parse", "HEAD")

    outcome = gate.evaluate(root, base, head)

    assert not outcome.admitted
    assert any(
        "model family" in reason for _, reason in outcome.skipped_reports
    )


def test_report_not_covering_the_authority_commit_does_not_admit(
    tmp_path: Path,
) -> None:
    root, base = _init_repo(tmp_path)
    reviewed_head = _commit_file(
        root, "scripts/feature.py", "VALUE = 2\n", "feat: ordinary reviewed work"
    )
    _land_pair(root, base, reviewed_head)
    touched = _commit_file(
        root, "scripts/cursor_hook_policy.py", "POLICY = 2\n", "feat: unreviewed policy"
    )
    head = _git(root, "rev-parse", "HEAD")

    outcome = gate.evaluate(root, base, head)

    assert not outcome.admitted
    assert touched in outcome.uncovered


def test_empty_range_and_cli_exit_codes(tmp_path: Path) -> None:
    root, base = _init_repo(tmp_path)
    _commit_file(root, "scripts/cursor_hook_policy.py", "POLICY = 1\n", "feat: policy")
    head = _git(root, "rev-parse", "HEAD")

    assert gate.main(["--root", str(root), "--base", head, "--head", head]) == 0
    assert gate.main(["--root", str(root), "--base", base, "--head", head]) == 1
