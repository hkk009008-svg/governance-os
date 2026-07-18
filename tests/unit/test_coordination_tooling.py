"""Focused regression tests for the compact mailbox writer boundaries."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest


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
    scripts = repo / "scripts"
    scripts.mkdir()
    (scripts / "mailbox_writer.py").write_bytes(
        (repo_root / "scripts/mailbox_writer.py").read_bytes()
    )
    mailbox = repo / "coordination/mailbox"
    (mailbox / "sent").mkdir(parents=True)
    (mailbox / "seen").mkdir()
    (mailbox / "kinds.txt").write_text(
        "status\nverify-request\nverification-report\n", encoding="utf-8"
    )
    for seat in ("director", "director2", "operator", "operator2", "coordinator"):
        (mailbox / "seen" / f"{seat}.txt").write_text("0\n", encoding="utf-8")
    _git(repo, "add", ".")
    _git(repo, "commit", "-q", "-m", "chore: fixture")


def _prepare_verify_request(repo: Path) -> tuple[str, str, str, str]:
    base = _git(repo, "rev-parse", "HEAD")
    (repo / "scripts/feature.py").write_text("VALUE = 1\n", encoding="utf-8")
    _git(repo, "add", "scripts/feature.py")
    _git(repo, "commit", "-q", "-m", "feat: candidate")
    head = _git(repo, "rev-parse", "HEAD")
    request_path = (
        "coordination/mailbox/sent/"
        "2026-07-17T08-00-00Z-director-to-operator-verify-request.md"
    )
    (repo / request_path).write_text(
        f"""\
# Director → Operator: verify compact pair candidate

**When:** 2026-07-17T08:00:00Z · **From:** director (online)

Event type: verify-request
Reviewed head: {head}
Reviewed base: {base}
Author seat: director
Author model: gpt-5.6-sol
Assigned operator: operator

## Outcome

The committed change satisfies the routed maintenance outcome.

## Finding Refs

- coordination/mailbox/sent/2026-07-18T06-05-32Z-operator-to-director-findings.md@fedfbe37f042045e844c2a7de90437445ccd6e0e

Cursor at send: 0
""",
        encoding="utf-8",
    )
    _git(repo, "add", request_path)
    _git(repo, "commit", "-q", "-m", "coord(director): request verification")
    return base, head, request_path, _git(repo, "rev-parse", "HEAD")


def _report_body(
    base: str,
    head: str,
    request_path: str,
    trigger: str,
    *,
    verdict: str,
    reviewer_seat: str = "operator",
) -> str:
    evidence = ""
    if verdict == "GO":
        evidence = """\

## Evidence

$ env -u GIT_INDEX_FILE python -m pytest tests/unit/test_feature.py -q
→ 1 passed
"""
    return f"""\
Event type: verification-report
VERDICT: {verdict}
Verification request: {request_path}@{trigger}
Reviewed head: {head}
Reviewed base: {base}
Reviewer seat: {reviewer_seat}
Reviewer model: gpt-5.6-terra

## Finding Refs

- coordination/mailbox/sent/2026-07-18T06-05-32Z-operator-to-director-findings.md@fedfbe37f042045e844c2a7de90437445ccd6e0e

## Finding Dispositions

- coordination/mailbox/sent/2026-07-18T06-05-32Z-operator-to-director-findings.md@fedfbe37f042045e844c2a7de90437445ccd6e0e: addressed
{evidence}

## Findings

None.
"""


def test_send_event_stages_ordinary_event_through_fixed_finalizer(
    tmp_path: Path, repo_root: Path
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _init_repo(repo, repo_root)

    result = _run(
        [repo_root / "coordination/bin/send-event", "director", "operator", "status", "hello"],
        repo,
        input_text="body\n",
    )

    assert result.returncode == 0, result.stderr
    staged = _git(repo, "diff", "--cached", "--name-only")
    assert staged.endswith("-director-to-operator-status.md")


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
            "operator",
            "all",
            "verification-report",
            subject,
        ],
        repo,
        input_text=_report_body(
            base, head, request_path, trigger, verdict=verdict
        ),
    )

    assert result.returncode == 0, result.stderr
    staged = _git(repo, "diff", "--cached", "--name-only")
    assert staged.endswith("-operator-to-all-verification-report.md")
    source = (repo_root / "coordination/bin/send-event").read_text(encoding="utf-8")
    assert source.count("send-event-finalize") == 1
    assert "verification_report_gate" not in source
    assert "TRUSTED_CODE" not in source
    assert "recover" not in source.lower()


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
            "operator",
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
            reviewer_seat="operator2",
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
        base, head, request_path, trigger, verdict="GO"
    ).replace(
        "$ env -u GIT_INDEX_FILE python -m pytest tests/unit/test_feature.py -q\n"
        "→ 1 passed",
        "$ \n→ ",
    )

    result = _run(
        [
            repo_root / "coordination/bin/send-event",
            "operator",
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


@pytest.mark.parametrize("sender", ("director", "director2", "coordinator"))
def test_non_operator_fails_before_verification_report_publication(
    tmp_path: Path, repo_root: Path, sender: str
) -> None:
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
    assert "only operator seats" in result.stderr
    assert not list((repo / "coordination/mailbox/sent").glob("*verification-report.md"))
    assert not list((repo / "coordination/mailbox/sent").glob(".*.tmp"))
    assert _git(repo, "diff", "--cached", "--name-only") == ""


def test_send_event_keeps_final_event_when_index_is_locked(
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
            [repo_root / "coordination/bin/send-event", "operator", "all", "verification-report", "blocked index"],
            repo,
            input_text=_report_body(
                base,
                head,
                request_path,
                trigger,
                verdict="NITS",
            ),
        )
    finally:
        lock.unlink()

    assert result.returncode == 0, result.stderr
    assert "not staged" in result.stdout
    assert len(list((repo / "coordination/mailbox/sent").glob("*verification-report.md"))) == 1
