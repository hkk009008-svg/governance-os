"""Focused regression tests for the compact mailbox writer boundaries."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

import mailbox_writer


_FINDING_PATH = (
    "coordination/mailbox/sent/"
    "2026-07-16T07-00-00Z-operator-to-director-findings.md"
)


def _run(
    args: list[str | Path],
    cwd: Path,
    *,
    env: dict[str, str] | None = None,
    input_text: str | None = None,
) -> subprocess.CompletedProcess[str]:
    full_env = os.environ.copy()
    if env:
        full_env.update(env)
    return subprocess.run(
        [str(arg) for arg in args],
        cwd=cwd,
        env=full_env,
        input=input_text,
        text=True,
        capture_output=True,
        check=False,
    )


def _git(repo: Path, *args: str, env: dict[str, str] | None = None) -> str:
    result = _run(["env", "-u", "GIT_INDEX_FILE", "git", *args], repo, env=env)
    assert result.returncode == 0, result.stderr
    return result.stdout.strip()


def _init_repo(repo: Path, repo_root: Path) -> None:
    _git(repo, "init", "-q")
    _git(repo, "config", "user.email", "test@example.invalid")
    _git(repo, "config", "user.name", "Test User")
    venv = repo / ".venv/bin"
    venv.mkdir(parents=True)
    (venv / "python").symlink_to(sys.executable)
    scripts = repo / "pipeline"
    scripts.mkdir()
    (scripts / "mailbox_writer.py").write_bytes(
        (repo_root / "pipeline/mailbox_writer.py").read_bytes()
    )
    mailbox = repo / "coordination/mailbox"
    (mailbox / "sent").mkdir(parents=True)
    (mailbox / "seen").mkdir()
    (mailbox / "kinds.txt").write_text(
        "findings\nverify-request\nverification-report\n", encoding="utf-8"
    )
    for seat in ("director", "director2", "operator", "operator2", "coordinator"):
        (mailbox / "seen" / f"{seat}.txt").write_text("0\n", encoding="utf-8")
    (repo / _FINDING_PATH).write_text(
        "# Operator → Director: fixture finding\n\n"
        "**When:** 2026-07-16T07:00:00Z · **From:** operator (online)\n\n"
        "Fixture evidence for finalizer tests.\n\n"
        "Cursor at send: 0\n",
        encoding="utf-8",
    )
    _git(repo, "add", ".")
    _git(repo, "commit", "-q", "-m", "chore: fixture")


def _finding_ref(repo: Path) -> str:
    introductions = _git(
        repo, "log", "--format=%H", "--diff-filter=A", "--", _FINDING_PATH
    ).splitlines()
    assert len(introductions) == 1
    return f"{_FINDING_PATH}@{introductions[0]}"


def _prepare_verify_request(
    repo: Path,
    *,
    reviewed_repository: str | None = None,
    reviewed_range: tuple[str, str] | None = None,
) -> tuple[str, str, str, str]:
    base = _git(repo, "rev-parse", "HEAD")
    finding_ref = _finding_ref(repo)
    (repo / "pipeline/feature.py").write_text("VALUE = 1\n", encoding="utf-8")
    _git(repo, "add", "pipeline/feature.py")
    _git(repo, "commit", "-q", "-m", "feat: candidate")
    head = _git(repo, "rev-parse", "HEAD")
    if reviewed_range is not None:
        base, head = reviewed_range
    repository_line = (
        ""
        if reviewed_repository is None
        else f"Reviewed repository: {reviewed_repository}\n"
    )
    request_path = (
        "coordination/mailbox/sent/"
        "2026-07-17T08-00-00Z-author-to-reviewer-verify-request.md"
    )
    (repo / request_path).write_text(
        f"""\
# Author → Reviewer: verify compact pair candidate

**When:** 2026-07-17T08:00:00Z · **From:** author (online)

Event type: verify-request
{repository_line}Reviewed head: {head}
Reviewed base: {base}
Author seat: author
Author model: gpt-5.6-sol
Assigned operator: reviewer
Risk class: material-behavior

## Outcome

The committed change satisfies the routed maintenance outcome.

## Finding Refs

- {finding_ref}

Cursor at send: 0
""",
        encoding="utf-8",
    )
    _git(repo, "add", request_path)
    _git(repo, "commit", "-q", "-m", "coord(author): request verification")
    return base, head, request_path, _git(repo, "rev-parse", "HEAD")


def _report_body(
    base: str,
    head: str,
    request_path: str,
    trigger: str,
    *,
    verdict: str,
    finding_ref: str,
    reviewer_seat: str = "reviewer",
    reviewed_repository: str | None = None,
) -> str:
    evidence = ""
    if verdict == "GO":
        evidence = """\

## Evidence

$ env -u GIT_INDEX_FILE python -m pytest tests/unit/test_feature.py -q
→ 1 passed
"""
    repository_line = (
        ""
        if reviewed_repository is None
        else f"Reviewed repository: {reviewed_repository}\n"
    )
    return f"""\
Event type: verification-report
VERDICT: {verdict}
Verification request: {request_path}@{trigger}
{repository_line}Reviewed head: {head}
Reviewed base: {base}
Reviewer seat: {reviewer_seat}
Reviewer model: gpt-5.6-terra
Risk class: material-behavior

## Finding Refs

- {finding_ref}

## Finding Dispositions

- {finding_ref}: addressed
{evidence}

## Findings

None.
"""


def _request_body(
    base: str,
    head: str,
    *,
    finding_ref: str,
    author: str = "author",
    assigned: str = "reviewer",
) -> str:
    return f"""\
Event type: verify-request
Reviewed head: {head}
Reviewed base: {base}
Author seat: {author}
Author model: gpt-5.6-sol
Assigned operator: {assigned}
Risk class: material-behavior

## Outcome

The committed change satisfies the routed maintenance outcome.

## Finding Refs

- {finding_ref}
"""


def test_send_event_stages_ordinary_event_through_fixed_finalizer(
    tmp_path: Path, repo_root: Path
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _init_repo(repo, repo_root)

    result = _run(
        [repo_root / "coordination/bin/send-event", "author", "reviewer", "findings", "hello"],
        repo,
        input_text="body\n",
    )

    assert result.returncode == 0, result.stderr
    staged = _git(repo, "diff", "--cached", "--name-only")
    assert staged.endswith("-author-to-reviewer-findings.md")


@pytest.mark.parametrize("role", ("author", "reviewer"))
def test_every_review_role_uses_the_explicit_cursorless_marker(
    tmp_path: Path, repo_root: Path, role: str
) -> None:
    """A cursor belonged to a standing chat; neither role outlives its task."""

    repo = tmp_path / "repo"
    repo.mkdir()
    _init_repo(repo, repo_root)

    result = _run(
        [
            repo_root / "coordination/bin/send-event",
            role,
            "all",
            "findings",
            "cursorless sender",
        ],
        repo,
        input_text="body\n",
    )

    assert result.returncode == 0, result.stderr
    staged = _git(repo, "diff", "--cached", "--name-only")
    assert staged.endswith(f"-{role}-to-all-findings.md")
    event = repo / staged
    assert event.read_text(encoding="utf-8").endswith(
        "Cursor at send: cursorless\n"
    )


def test_valid_verify_request_is_validated_before_finalization(
    tmp_path: Path, repo_root: Path
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _init_repo(repo, repo_root)
    base, head, _old_request, _trigger = _prepare_verify_request(repo)

    result = _run(
        [
            repo_root / "coordination/bin/send-event",
            "author",
            "reviewer",
            "verify-request",
            "validate candidate",
        ],
        repo,
        input_text=_request_body(base, head, finding_ref=_finding_ref(repo)),
    )

    assert result.returncode == 0, result.stderr
    staged = _git(repo, "diff", "--cached", "--name-only")
    assert staged.endswith("-author-to-reviewer-verify-request.md")
    source = (repo_root / "coordination/bin/send-event").read_text(encoding="utf-8")
    assert source.index("validate-candidate") < source.index("send-event-finalize")


def test_verify_request_without_formal_risk_class_fails_before_finalization(
    tmp_path: Path, repo_root: Path
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _init_repo(repo, repo_root)
    base, head, _old_request, _trigger = _prepare_verify_request(repo)

    result = _run(
        [
            repo_root / "coordination/bin/send-event",
            "author",
            "reviewer",
            "verify-request",
            "missing risk class",
        ],
        repo,
        input_text=_request_body(
            base, head, finding_ref=_finding_ref(repo)
        ).replace(
            "Risk class: material-behavior\n", ""
        ),
    )

    assert result.returncode != 0
    assert "missing Risk class" in result.stderr
    assert _git(repo, "diff", "--cached", "--name-only") == ""
    assert len(list((repo / "coordination/mailbox/sent").glob("*verify-request.md"))) == 1


def test_a_retired_seat_cannot_open_a_verify_request(
    tmp_path: Path, repo_root: Path
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _init_repo(repo, repo_root)
    base, head, _old_request, _trigger = _prepare_verify_request(repo)

    result = _run(
        [
            repo_root / "coordination/bin/send-event",
            "coordinator",
            "reviewer",
            "verify-request",
            "invalid author",
        ],
        repo,
        input_text=_request_body(
            base,
            head,
            finding_ref=_finding_ref(repo),
            author="coordinator",
            assigned="operator",
        ),
    )

    assert result.returncode != 0
    assert "bad <from>: coordinator" in result.stderr
    assert _git(repo, "diff", "--cached", "--name-only") == ""


def test_duplicate_cursor_footer_fails_before_publication(
    tmp_path: Path, repo_root: Path
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _init_repo(repo, repo_root)

    result = _run(
        [
            repo_root / "coordination/bin/send-event",
            "author",
            "reviewer",
            "findings",
            "duplicate footer",
        ],
        repo,
        input_text="body\n\nCursor at send: 0\n",
    )

    assert result.returncode != 0
    assert "duplicate cursor footer" in result.stderr
    assert _git(repo, "diff", "--cached", "--name-only") == ""


@pytest.mark.parametrize("verdict", ("GO", "NITS", "FAIL"))
def test_valid_verification_report_uses_same_fixed_finalizer_as_ordinary_events(
    tmp_path: Path, repo_root: Path, verdict: str
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _init_repo(repo, repo_root)
    base, head, request_path, trigger = _prepare_verify_request(repo)
    subject = f"truthful {verdict} commit `{head}`" if verdict == "GO" else f"truthful {verdict}"

    result = _run(
        [
            repo_root / "coordination/bin/send-event",
            "reviewer",
            "all",
            "verification-report",
            subject,
        ],
        repo,
        input_text=_report_body(
            base,
            head,
            request_path,
            trigger,
            verdict=verdict,
            finding_ref=_finding_ref(repo),
        ),
    )

    assert result.returncode == 0, result.stderr
    staged = _git(repo, "diff", "--cached", "--name-only")
    assert staged.endswith("-reviewer-to-all-verification-report.md")
    source = (repo_root / "coordination/bin/send-event").read_text(encoding="utf-8")
    assert source.count("send-event-finalize") == 1
    assert "verification_report_gate" not in source
    assert "TRUSTED_CODE" not in source
    assert "recover" not in source.lower()


def test_fixed_finalizer_revalidates_report_changed_after_prevalidation(
    tmp_path: Path, repo_root: Path
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _init_repo(repo, repo_root)
    base, head, request_path, trigger = _prepare_verify_request(repo)
    relative = (
        "coordination/mailbox/sent/"
        "2026-07-17T08-10-00Z-reviewer-to-all-verification-report.md"
    )
    candidate = repo / (
        "coordination/mailbox/sent/"
        ".2026-07-17T08-10-00Z-reviewer-to-all-verification-report.race.tmp"
    )
    valid = (
        "# Reviewer → All: prevalidated report\n\n"
        "**When:** 2026-07-17T08:10:00Z · **From:** reviewer (online)\n\n"
        + _report_body(
            base,
            head,
            request_path,
            trigger,
            verdict="FAIL",
            finding_ref=_finding_ref(repo),
        )
        + "\nCursor at send: cursorless\n"
    )
    candidate.write_text(valid, encoding="utf-8")
    candidate.chmod(0o600)

    mailbox_writer.validate_event_candidate(repo, candidate, relative)
    candidate.write_text(
        valid.replace("VERDICT: FAIL", "VERDICT: GREEN"),
        encoding="utf-8",
    )

    with pytest.raises(
        mailbox_writer.MailboxWriterError,
        match="verification-report candidate is invalid",
    ):
        mailbox_writer._send_event_finalize(repo, candidate, relative)

    assert candidate.exists()
    assert not (repo / relative).exists()
    assert _git(repo, "diff", "--cached", "--name-only") == ""


def test_cross_repository_verification_report_uses_fixed_finalizer(
    tmp_path: Path, repo_root: Path
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _init_repo(repo, repo_root)

    target = tmp_path / "target"
    target.mkdir()
    _git(target, "init", "-q")
    _git(target, "config", "user.email", "test@example.invalid")
    _git(target, "config", "user.name", "Test User")
    (target / "feature.py").write_text("VALUE = 1\n", encoding="utf-8")
    _git(target, "add", ".")
    _git(target, "commit", "-q", "-m", "chore: target base")
    base = _git(target, "rev-parse", "HEAD")
    (target / "feature.py").write_text("VALUE = 2\n", encoding="utf-8")
    _git(target, "add", "feature.py")
    _git(target, "commit", "-q", "-m", "feat: target candidate")
    head = _git(target, "rev-parse", "HEAD")

    _local_base, _local_head, request_path, trigger = _prepare_verify_request(
        repo,
        reviewed_repository=target.as_posix(),
        reviewed_range=(base, head),
    )
    result = _run(
        [
            repo_root / "coordination/bin/send-event",
            "reviewer",
            "all",
            "verification-report",
            f"truthful GO target commit `{head}`",
        ],
        repo,
        input_text=_report_body(
            base,
            head,
            request_path,
            trigger,
            verdict="GO",
            finding_ref=_finding_ref(repo),
            reviewed_repository=target.as_posix(),
        ),
    )

    assert result.returncode == 0, result.stderr
    staged = _git(repo, "diff", "--cached", "--name-only")
    assert staged.endswith("-reviewer-to-all-verification-report.md")


@pytest.mark.xfail(
    strict=True,
    reason=(
        "VACUOUS UNDER THE TWO-ROLE COLLAPSE, recorded rather than deleted. "
        "validate_report refuses a report whose reviewer_seat differs from the "
        "request's assigned operator. That discriminated while six seat names "
        "existed: a report from operator2 could answer a request assigned to "
        "operator. With exactly one reviewer name the comparison is true by "
        "construction and can no longer fail. The surviving discriminator is "
        "the reviewer's MODEL FAMILY, which compact_pair_loop already validates "
        "for high-risk-control, plus the side recorded in a peer receipt. "
        "Restoring seat-level expressiveness means carrying the side in the "
        "identity (reviewer@codex vs reviewer@claude), which is a grammar "
        "change with its own review. When that lands this pin xpasses and must "
        "be removed."
    ),
)
def test_misassigned_verification_report_fails_before_finalization(
    tmp_path: Path, repo_root: Path
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _init_repo(repo, repo_root)
    base, head, request_path, trigger = _prepare_verify_request(repo)

    result = _run(
        [
            repo_root / "coordination/bin/send-event",
            "reviewer",
            "all",
            "verification-report",
            "misassigned",
        ],
        repo,
        input_text=_report_body(
            base,
            head,
            request_path,
            trigger,
            verdict="FAIL",
            finding_ref=_finding_ref(repo),
            reviewer_seat="reviewer",
        ),
    )

    assert result.returncode != 0
    assert "assigned Operator" in result.stderr
    assert not list((repo / "coordination/mailbox/sent").glob("*verification-report.md"))
    assert _git(repo, "diff", "--cached", "--name-only") == ""
    source = (repo_root / "coordination/bin/send-event").read_text(encoding="utf-8")
    assert source.index("validate-candidate") < source.index("send-event-finalize")


def test_go_with_bare_evidence_markers_fails_before_staging(
    tmp_path: Path, repo_root: Path
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _init_repo(repo, repo_root)
    base, head, request_path, trigger = _prepare_verify_request(repo)
    body = _report_body(
        base,
        head,
        request_path,
        trigger,
        verdict="GO",
        finding_ref=_finding_ref(repo),
    ).replace(
        "$ env -u GIT_INDEX_FILE python -m pytest tests/unit/test_feature.py -q\n"
        "→ 1 passed",
        "$ \n→ ",
    )

    result = _run(
        [
            repo_root / "coordination/bin/send-event",
            "reviewer",
            "all",
            "verification-report",
            f"bare evidence commit `{head}`",
        ],
        repo,
        input_text=body,
    )

    assert result.returncode != 0
    assert "GO requires evidence" in result.stderr
    assert _git(repo, "diff", "--cached", "--name-only") == ""


@pytest.mark.parametrize("sender", ("author", "director", "director2", "coordinator"))
def test_only_the_reviewer_may_publish_a_verification_report(
    tmp_path: Path, repo_root: Path, sender: str
) -> None:
    """Two refusals, one property: nobody but the reviewer publishes a verdict.

    `author` is refused for the reason that survived the collapse -- it is the
    other position in the pair. The three retired seat names are refused one
    step earlier, as senders that no longer exist, which is strictly stronger
    than the per-kind rule they used to trip.
    """

    repo = tmp_path / "repo"
    repo.mkdir()
    _init_repo(repo, repo_root)

    result = _run(
        [
            repo_root / "coordination/bin/send-event",
            sender,
            "all",
            "verification-report",
            "forbidden",
        ],
        repo,
        input_text="VERDICT: GO\n",
    )

    assert result.returncode == 2
    expected = (
        "only the reviewer may publish verification-report"
        if sender == "author"
        else "bad <from>"
    )
    assert expected in result.stderr
    assert not list((repo / "coordination/mailbox/sent").glob("*verification-report.md"))
    assert not list((repo / "coordination/mailbox/sent").glob(".*.tmp"))
    assert _git(repo, "diff", "--cached", "--name-only") == ""


def test_send_event_keeps_final_event_but_fails_when_index_is_locked(
    tmp_path: Path, repo_root: Path
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _init_repo(repo, repo_root)
    base, head, request_path, trigger = _prepare_verify_request(repo)
    lock = repo / ".git/index.lock"
    lock.write_text("locked\n", encoding="utf-8")
    try:
        result = _run(
            [repo_root / "coordination/bin/send-event", "reviewer", "all", "verification-report", "blocked index"],
            repo,
            input_text=_report_body(
                base,
                head,
                request_path,
                trigger,
                verdict="NITS",
                finding_ref=_finding_ref(repo),
            ),
        )
    finally:
        lock.unlink()

    assert result.returncode != 0
    assert "not staged" in result.stdout
    assert len(list((repo / "coordination/mailbox/sent").glob("*verification-report.md"))) == 1
