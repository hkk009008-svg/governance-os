from __future__ import annotations

import subprocess
from pathlib import Path


def git(root: Path, *arguments: str) -> str:
    result = subprocess.run(
        ["git", *arguments], cwd=root, capture_output=True, text=True, check=False
    )
    if result.returncode:
        raise RuntimeError(result.stderr or result.stdout)
    return result.stdout.strip()


def init_repo(root: Path) -> str:
    root.mkdir(parents=True, exist_ok=True)
    git(root, "init", "-q")
    git(root, "config", "user.email", "test@example.com")
    git(root, "config", "user.name", "Test")
    (root / "coordination/mailbox/sent").mkdir(parents=True)
    return commit(
        root,
        {
            "README.md": "base\n",
            "coordination/mailbox/kinds.txt": "verification-report\nverify-request\n",
            "coordination/mailbox/sent/.gitkeep": "",
        },
        "base",
    )


def commit(root: Path, files: dict[str, str], message: str) -> str:
    for relative, content in files.items():
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        git(root, "add", "--", relative)
    git(root, "commit", "-q", "-m", message)
    return git(root, "rev-parse", "HEAD")


def event(
    stamp: str,
    sender: str,
    recipient: str,
    kind: str,
    body: str,
    subject: str = "test",
) -> tuple[str, str]:
    path = f"coordination/mailbox/sent/{stamp}-{sender}-to-{recipient}-{kind}.md"
    when = stamp[:11] + stamp[11:19].replace("-", ":") + "Z"
    text = (
        f"# {sender.capitalize()} → {recipient.capitalize()}: {subject}\n\n"
        f"**When:** {when} · **From:** {sender} (online)\n\n"
        f"{body.rstrip()}\n\nCursor at send: cursorless\n"
    )
    return path, text


def request_body(
    base: str,
    head: str,
    *,
    author_model: str = "gpt-5.6-sol",
    risk: str = "high-risk-control",
) -> str:
    body = (
        "Event type: verify-request\n"
        f"Reviewed base: {base}\n"
        f"Reviewed head: {head}\n"
        f"Author model: {author_model}\n"
        f"Risk class: {risk}\n\n"
        "## Outcome\n\nReview the exact committed range."
    )
    if risk == "high-risk-control":
        body += "\n\n## Abuse Class Assessment\n\n- Identity laundering\n- Gate bypass"
    return body


def report_body(
    request_path: str,
    request_commit: str,
    *,
    verdict: str = "GO",
    reviewer_model: str = "claude-sonnet-5",
    high_risk: bool = True,
    supersedes: str | None = None,
) -> str:
    lines = [
        "Event type: verification-report",
        f"VERDICT: {verdict}",
        f"Verification request: {request_path}@{request_commit}",
        f"Reviewer model: {reviewer_model}",
    ]
    if high_risk:
        lines.append("Abuse Class Assessment: bound-to-request")
    if supersedes:
        lines.append(f"Supersedes: {supersedes}")
    lines += [
        "",
        "## Findings",
        "",
        "The reviewed range is acceptable." if verdict != "FAIL" else "A blocking defect remains.",
        "",
        "## Evidence",
        "",
        "$ pytest -q",
        "→ passed",
    ]
    return "\n".join(lines)


def add_request(
    root: Path,
    base: str,
    head: str,
    *,
    stamp: str = "2026-09-02T10-00-00Z",
    author: str = "codex",
    reviewer: str = "claude",
    author_model: str = "gpt-5.6-sol",
    risk: str = "high-risk-control",
) -> tuple[str, str]:
    path, text = event(
        stamp,
        author,
        reviewer,
        "verify-request",
        request_body(base, head, author_model=author_model, risk=risk),
    )
    return path, commit(root, {path: text}, "request")


def add_report(
    root: Path,
    request_path: str,
    request_commit: str,
    *,
    stamp: str = "2026-09-02T10-01-00Z",
    reviewer: str = "claude",
    recipient: str = "codex",
    verdict: str = "GO",
    reviewer_model: str = "claude-sonnet-5",
    high_risk: bool = True,
    supersedes: str | None = None,
) -> tuple[str, str]:
    path, text = event(
        stamp,
        reviewer,
        recipient,
        "verification-report",
        report_body(
            request_path,
            request_commit,
            verdict=verdict,
            reviewer_model=reviewer_model,
            high_risk=high_risk,
            supersedes=supersedes,
        ),
    )
    return path, commit(root, {path: text}, "report")
