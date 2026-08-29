"""Focused regression tests for the compact mailbox writer boundaries."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

import compact_pair_loop
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


def _checkpoint_body(repo: Path, owner: str) -> str:
    head = _git(repo, "rev-parse", "HEAD")
    return f"""\
Checkpoint: send-event-finalizer
Boundary: compaction
Objective: exercise send-event through the fixed writer
Accepted scope: the throwaway coordination-tooling fixture
Owner: {owner}
Policy revision: {head}
Base: {head}
Head: {head}
Evidence refs: none
Verification status: the fixture payload is structurally valid
Blockers: none
Next action: inspect the staged checkpoint
Lessons: none-considered
"""


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
        "2026-07-17T08-00-00Z-codex-to-claude-verify-request.md"
    )
    (repo / request_path).write_text(
        f"""\
# Codex → Claude: verify compact pair candidate

**When:** 2026-07-17T08:00:00Z · **From:** codex (online)

Event type: verify-request
{repository_line}Reviewed head: {head}
Reviewed base: {base}
Author seat: codex
Author model: gpt-5.6-sol
Assigned operator: claude
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
    _git(repo, "commit", "-q", "-m", "coord(codex): request verification")
    return base, head, request_path, _git(repo, "rev-parse", "HEAD")


def _report_body(
    base: str,
    head: str,
    request_path: str,
    trigger: str,
    *,
    verdict: str,
    finding_ref: str,
    reviewer_seat: str = "claude",
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
Reviewer model: {"claude-opus-4-6-thinking" if reviewer_seat == "claude" else "gpt-5.6-terra"}
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
    author: str = "codex",
    assigned: str = "claude",
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


def test_send_event_stages_checkpoint_through_fixed_finalizer(
    tmp_path: Path, repo_root: Path
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _init_repo(repo, repo_root)

    result = _run(
        [repo_root / "coordination/bin/send-event", "codex", "claude", "findings", "hello"],
        repo,
        input_text=_checkpoint_body(repo, "codex"),
    )

    assert result.returncode == 0, result.stderr
    staged = _git(repo, "diff", "--cached", "--name-only")
    assert staged.endswith("-codex-to-claude-findings.md")


@pytest.mark.parametrize("member", ("codex", "claude", "agy"))
def test_every_desktop_member_uses_the_explicit_cursorless_marker(
    tmp_path: Path, repo_root: Path, member: str
) -> None:
    """A cursor belonged to a standing chat, not a desktop app member."""

    repo = tmp_path / "repo"
    repo.mkdir()
    _init_repo(repo, repo_root)

    result = _run(
        [
            repo_root / "coordination/bin/send-event",
            member,
            "all",
            "findings",
            "cursorless sender",
        ],
        repo,
        input_text=_checkpoint_body(repo, member),
    )

    assert result.returncode == 0, result.stderr
    staged = _git(repo, "diff", "--cached", "--name-only")
    assert staged.endswith(f"-{member}-to-all-findings.md")
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
            "codex",
            "claude",
            "verify-request",
            "validate candidate",
        ],
        repo,
        input_text=_request_body(base, head, finding_ref=_finding_ref(repo)),
    )

    assert result.returncode == 0, result.stderr
    staged = _git(repo, "diff", "--cached", "--name-only")
    assert staged.endswith("-codex-to-claude-verify-request.md")
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
            "codex",
            "claude",
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
            "codex",
            "claude",
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
            "claude",
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
    assert staged.endswith("-claude-to-all-verification-report.md")
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
        "2026-07-17T08-10-00Z-claude-to-all-verification-report.md"
    )
    candidate = repo / (
        "coordination/mailbox/sent/"
        ".2026-07-17T08-10-00Z-claude-to-all-verification-report.race.tmp"
    )
    valid = (
        "# Claude → All: prevalidated report\n\n"
        "**When:** 2026-07-17T08:10:00Z · **From:** claude (online)\n\n"
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
            "claude",
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
    assert staged.endswith("-claude-to-all-verification-report.md")


def test_report_recipient_must_match_the_request_author(
    tmp_path: Path, repo_root: Path
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _init_repo(repo, repo_root)
    base, head, request_path, trigger = _prepare_verify_request(repo)
    body = _report_body(
        base, head, request_path, trigger,
        verdict="FAIL",
        finding_ref=_finding_ref(repo),
    )
    relative = (
        "coordination/mailbox/sent/"
        "2026-07-17T09-00-00Z-claude-to-agy-verification-report.md"
    )
    raw = (
        "# Claude → AGY: misaddressed report\n\n"
        "**When:** 2026-07-17T09:00:00Z · **From:** claude (online)\n\n"
        + body
        + "\nCursor at send: cursorless\n"
    )
    report = compact_pair_loop._parse_verification_report_bytes(
        repo, relative, raw.encode("utf-8")
    )
    violations = compact_pair_loop.validate_report(repo, report)
    assert "report recipient does not match request author" in violations

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
            "claude",
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


@pytest.mark.parametrize("sender", ("agy", "author", "director", "director2", "coordinator"))
def test_only_codex_or_claude_may_publish_a_verification_report(
    tmp_path: Path, repo_root: Path, sender: str
) -> None:
    """AGY and every retired identity are refused on the report path."""

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

    assert result.returncode != 0
    expected = (
        "publisher must be codex or claude"
        if sender == "agy"
        else (
            "path is not canonical" if sender == "author" else "bad <from>"
        )
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
            [repo_root / "coordination/bin/send-event", "claude", "all", "verification-report", "blocked index"],
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
