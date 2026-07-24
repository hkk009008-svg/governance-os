from __future__ import annotations

import json
from pathlib import Path
import subprocess

import pytest

from scripts import cursor_mailbox as mailbox
from scripts.cursor_app_binding import AppSessionBinding


def _binding(
    seat: str = "director", model: str = "composer-2.5"
) -> AppSessionBinding:
    return AppSessionBinding(
        seat=seat,
        root=Path("/tmp/seat"),
        branch=f"cursor-seat/{seat}",
        conversation_id=f"{seat}-conversation",
        model_id=model,
    )


def _resolver(active: AppSessionBinding):
    return lambda root, environ: active


def _writers(root: Path, *, functional: bool = False) -> Path:
    bindir = root / "coordination" / "bin"
    bindir.mkdir(parents=True, exist_ok=True)
    captured = root / "captured-body.txt"
    if functional:
        (bindir / "send-event").write_text(
            f"#!/bin/sh\n/bin/cat > {captured}\n",
            encoding="utf-8",
        )
        (bindir / "send-event").chmod(0o755)
    else:
        (bindir / "send-event").write_text("#!/bin/sh\n", encoding="utf-8")
    (bindir / "consume-events").write_text("#!/bin/sh\n", encoding="utf-8")
    (bindir / "consume-events").chmod(0o755)
    return captured


def _body(root: Path, text: str = "body\n") -> Path:
    path = root / ".pytest-verify-tmp" / "body.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def test_build_publish_argv_delegates_to_fixed_writer(tmp_path: Path) -> None:
    _writers(tmp_path)
    argv = mailbox.build_publish_argv(
        tmp_path, seat="director", to="operator", kind="status", subject="hello"
    )
    assert argv[-4:] == ["director", "operator", "status", "hello"]
    assert argv[0].endswith("coordination/bin/send-event")


def test_body_file_must_be_regular_scratch_file(tmp_path: Path) -> None:
    outside = tmp_path / "body.md"
    outside.write_text("body", encoding="utf-8")
    with pytest.raises(mailbox.MailboxBindingError, match=".pytest-verify-tmp"):
        mailbox.read_body_file(tmp_path, outside)

    scratch = _body(tmp_path)
    link = scratch.parent / "link.md"
    link.symlink_to(scratch)
    with pytest.raises(mailbox.MailboxBindingError, match="non-symlink"):
        mailbox.read_body_file(tmp_path, link)


def test_publish_dry_run_reports_bound_app_identity(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    _writers(tmp_path)
    body = _body(tmp_path, "hello\n")
    active = _binding()
    result = mailbox.main(
        [
            "publish",
            "--to",
            "operator",
            "--kind",
            "status",
            "--subject",
            "hello",
            "--body-file",
            str(body),
            "--dry-run",
        ],
        root=tmp_path,
        environ={},
        binding_resolver=_resolver(active),
    )
    payload = json.loads(capsys.readouterr().out)
    assert result == 0
    assert payload["seat"] == "director"
    assert payload["model_id"] == "composer-2.5"
    assert payload["requires_app_approval"] is True


def test_default_subprocess_runner_accepts_body_input(tmp_path: Path) -> None:
    captured = _writers(tmp_path, functional=True)
    body = _body(tmp_path, "real runner body\n")
    result = mailbox.main(
        [
            "publish",
            "--to",
            "operator",
            "--kind",
            "status",
            "--subject",
            "hello",
            "--body-file",
            str(body),
        ],
        root=tmp_path,
        environ={},
        binding_resolver=_resolver(_binding()),
    )
    assert result == 0
    assert captured.read_text(encoding="utf-8") == "real runner body\n"


def test_publish_rejects_self_addressed_event(tmp_path: Path) -> None:
    _writers(tmp_path)
    result = mailbox.main(
        [
            "publish",
            "--to",
            "director",
            "--kind",
            "status",
            "--subject",
            "hello",
            "--body-file",
            str(_body(tmp_path)),
        ],
        root=tmp_path,
        environ={},
        binding_resolver=_resolver(_binding()),
        runner=lambda *args, **kwargs: subprocess.CompletedProcess([], 0),
    )
    assert result == 2


def test_coordinator_cannot_consume_cursor(tmp_path: Path) -> None:
    _writers(tmp_path)
    result = mailbox.main(
        ["consume", "--dry-run"],
        root=tmp_path,
        environ={},
        binding_resolver=_resolver(_binding("coordinator")),
    )
    assert result == 2


def _git(root: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(root), *args],
        text=True,
        capture_output=True,
        check=True,
    ).stdout.strip()


def _repo_with_request(tmp_path: Path, author_model: str = "composer-2.5") -> Path:
    root = tmp_path / "repo"
    root.mkdir()
    _git(root, "init", "-q")
    _git(root, "config", "user.email", "tests@example.invalid")
    _git(root, "config", "user.name", "Tests")
    (root / "payload.txt").write_text("base\n", encoding="utf-8")
    _git(root, "add", "payload.txt")
    _git(root, "commit", "-q", "-m", "base")
    base = _git(root, "rev-parse", "HEAD")
    (root / "payload.txt").write_text("head\n", encoding="utf-8")
    _git(root, "add", "payload.txt")
    _git(root, "commit", "-q", "-m", "head")
    head = _git(root, "rev-parse", "HEAD")
    path = (
        root
        / "coordination"
        / "mailbox"
        / "sent"
        / "2026-07-24T01-00-00Z-director-to-operator-verify-request.md"
    )
    path.parent.mkdir(parents=True)
    path.write_text(
        "\n".join(
            (
                "# Director → Operator: test",
                "",
                "**When:** 2026-07-24T01:00:00Z · **From:** director (online)",
                "",
                "Event type: verify-request",
                f"Reviewed repository: {root}",
                f"Reviewed base: {base}",
                f"Reviewed head: {head}",
                "Author seat: director",
                f"Author model: {author_model}",
                "Assigned operator: operator",
                "",
                "## Outcome",
                "",
                "Verify the test range.",
                "",
                "## Finding Refs",
                "",
                "- sha256:" + "1" * 64,
                "",
                "Cursor at send: 0",
                "",
            )
        ),
        encoding="utf-8",
    )
    _git(root, "add", str(path.relative_to(root)))
    _git(root, "commit", "-q", "-m", "verify request")
    return root


def test_next_review_resolves_latest_pending_committed_request(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = _repo_with_request(tmp_path)
    result = mailbox.main(
        ["next-review"],
        root=root,
        environ={},
        binding_resolver=_resolver(_binding("operator", "claude-sonnet-5")),
    )
    payload = json.loads(capsys.readouterr().out)
    assert result == 0
    assert payload["assigned_operator"] == "operator"
    assert payload["models_differ"] is True
    assert payload["verify_request"].endswith(_git(root, "rev-parse", "HEAD"))


def test_next_review_discovers_request_on_director_worktree_branch(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = _repo_with_request(tmp_path)
    request_commit = _git(root, "rev-parse", "HEAD")
    operator_base = _git(root, "rev-parse", "HEAD^")
    _git(root, "branch", "cursor-seat/director", request_commit)
    _git(root, "branch", "cursor-seat/operator", operator_base)
    operator = tmp_path / "operator"
    _git(
        root,
        "worktree",
        "add",
        "-q",
        str(operator),
        "cursor-seat/operator",
    )

    result = mailbox.main(
        ["next-review"],
        root=operator,
        environ={},
        binding_resolver=_resolver(_binding("operator", "claude-sonnet-5")),
    )

    payload = json.loads(capsys.readouterr().out)
    assert result == 0
    assert payload["verify_request"].endswith(request_commit)


def test_next_review_rejects_same_runtime_model(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = _repo_with_request(tmp_path, author_model="composer-2.5")
    result = mailbox.main(
        ["next-review"],
        root=root,
        environ={},
        binding_resolver=_resolver(_binding("operator", "composer-2.5")),
    )
    assert result == 2
    assert "must differ" in capsys.readouterr().err


def test_invalid_report_cannot_suppress_pending_request(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = _repo_with_request(tmp_path)
    request_path = (
        "coordination/mailbox/sent/"
        "2026-07-24T01-00-00Z-director-to-operator-verify-request.md"
    )
    request_commit = _git(root, "rev-parse", "HEAD")
    report = (
        root
        / "coordination/mailbox/sent/"
        "2026-07-24T01-10-00Z-operator-to-director-verification-report.md"
    )
    report.write_text(
        "\n".join(
            (
                "# Operator → Director: invalid report",
                "",
                f"Verification request: {request_path}@{request_commit}",
                "",
            )
        ),
        encoding="utf-8",
    )
    _git(root, "add", str(report.relative_to(root)))
    _git(root, "commit", "-q", "-m", "invalid report")

    result = mailbox.main(
        ["next-review"],
        root=root,
        environ={},
        binding_resolver=_resolver(_binding("operator", "claude-sonnet-5")),
    )

    payload = json.loads(capsys.readouterr().out)
    assert result == 0
    assert payload["verify_request"] == f"{request_path}@{request_commit}"


def test_structurally_invalid_report_cannot_suppress_pending_request(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = _repo_with_request(tmp_path)
    request_path = (
        "coordination/mailbox/sent/"
        "2026-07-24T01-00-00Z-director-to-operator-verify-request.md"
    )
    request_commit = _git(root, "rev-parse", "HEAD")
    base = _git(root, "rev-parse", "HEAD^^")
    report = (
        root
        / "coordination/mailbox/sent/"
        "2026-07-24T01-10-00Z-operator-to-director-verification-report.md"
    )
    report.write_text(
        "\n".join(
            (
                "# Operator → Director: structurally invalid report",
                "",
                "**When:** 2026-07-24T01:10:00Z · **From:** operator (online)",
                "",
                "Event type: verification-report",
                "VERDICT: FAIL",
                f"Verification request: {request_path}@{request_commit}",
                f"Reviewed repository: {root}",
                # Deliberately mismatch the request head so structure validation fails.
                f"Reviewed head: {base}",
                f"Reviewed base: {base}",
                "Reviewer seat: operator",
                "Reviewer model: claude-sonnet-5",
                "",
                "## Finding Refs",
                "",
                "- sha256:" + "1" * 64,
                "",
                "## Finding Dispositions",
                "",
                f"- sha256:{'1' * 64}: unresolved-hard-boundary",
                "",
                "## Evidence",
                "",
                "$ independent actual-diff inspection",
                "→ structure mismatch intentionally retained",
                "",
                "## Findings",
                "",
                "Reviewed head does not match the bound request.",
                "",
                "Cursor at send: 0",
                "",
            )
        ),
        encoding="utf-8",
    )
    _git(root, "add", str(report.relative_to(root)))
    _git(root, "commit", "-q", "-m", "structurally invalid report")

    result = mailbox.main(
        ["next-review"],
        root=root,
        environ={},
        binding_resolver=_resolver(_binding("operator", "claude-sonnet-5")),
    )

    payload = json.loads(capsys.readouterr().out)
    assert result == 0
    assert payload["verify_request"] == f"{request_path}@{request_commit}"


def test_next_review_is_operator_only(tmp_path: Path) -> None:
    root = _repo_with_request(tmp_path)
    result = mailbox.main(
        ["next-review"],
        root=root,
        environ={},
        binding_resolver=_resolver(_binding("director")),
    )
    assert result == 2
