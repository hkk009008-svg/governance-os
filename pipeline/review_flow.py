#!/usr/bin/env python3
"""One-command publication for the formal review pair, and a landing check.

`review publish` composes, validates, publishes, and commits a verify-request
directly after the reviewed head; `review accept` publishes and commits the
bound verification-report directly after its request; `review land-check`
confirms a reviewed chain admits and can land byte-clean. Each command calls
the existing composer, validators, and fixed writer, commits only the emitted
artifact, and refuses at the wrong HEAD. Nothing here pushes, merges, or
grants authority.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import ci_admission_gate
import compact_pair_loop
import git_runner
import mailbox_writer


ROOT = Path(__file__).resolve().parent.parent


class ReviewFlowError(RuntimeError):
    pass


def _git(root: Path, *arguments: str, mode: str = "authority") -> str:
    result = git_runner.run_git(root, arguments, mode=mode, text=True)
    if result.returncode != 0:
        raise ReviewFlowError(result.stderr.strip() or f"git {arguments[0]} failed")
    return result.stdout.strip()


def _head(root: Path) -> str:
    return _git(root, "rev-parse", "--verify", "HEAD^{commit}")


def _is_ancestor(root: Path, ancestor: str, descendant: str) -> bool:
    result = git_runner.run_git(
        root, ("merge-base", "--is-ancestor", ancestor, descendant), mode="authority"
    )
    if result.returncode not in (0, 1):
        raise ReviewFlowError("Git ancestry check failed")
    return result.returncode == 0


def _commit_only(root: Path, relative: str, message: str) -> str:
    # The caller's own Git identity signs the artifact commit, so this one
    # call keeps the ambient configuration; the artifact bytes were already
    # validated and staged by the fixed writer under its hermetic environment.
    _git(root, "commit", "-q", "--only", "-m", message, "--", relative, mode="dashboard")
    return _head(root)


def _request_added_by(root: Path, commit: str) -> str:
    changed = _git(
        root, "diff-tree", "--root", "--no-commit-id", "--name-status", "-r", commit
    ).splitlines()
    added = [
        line.split("\t", 1)[1]
        for line in changed
        if line.startswith("A\t") and compact_pair_loop.REQUEST_RE.fullmatch(line.split("\t", 1)[1])
    ]
    if len(changed) != 1 or len(added) != 1:
        raise ReviewFlowError(
            "HEAD must be the request commit, which adds exactly one verify-request "
            "and nothing else; check it out before accepting"
        )
    return added[0]


def publish_request(
    root: Path,
    *,
    author: str,
    author_model: str,
    reviewer: str,
    risk_class: str,
    base: str,
    head: str,
    outcome: str,
    subject: str,
    abuse_classes: tuple[str, ...] = (),
    finding_refs: tuple[str, ...] = (),
) -> tuple[str, str]:
    """Compose, publish, and commit one verify-request directly after ``head``."""
    root = root.resolve()
    current = _head(root)
    reviewed_head = _git(root, "rev-parse", "--verify", f"{head}^{{commit}}")
    if reviewed_head != current:
        raise ReviewFlowError(
            f"HEAD is {current[:12]}, not the reviewed head {reviewed_head[:12]}; "
            "check out the reviewed head so the request commit follows it directly"
        )
    body = compact_pair_loop.compose_request(
        root,
        author_member=author,
        author_model=author_model,
        reviewer_member=reviewer,
        risk_class=risk_class,
        base_rev=base,
        head_rev=reviewed_head,
        outcome=outcome,
        abuse_assessments=abuse_classes,
        finding_refs=finding_refs,
    )
    relative = mailbox_writer.publish(
        root, sender=author, recipient=reviewer, kind="verify-request",
        subject=subject, body=body,
    )
    commit = _commit_only(root, relative, f"review: request {subject}")
    # Self-check against the same parser the gate uses.
    compact_pair_loop.parse_verify_request(root, relative, commit)
    return relative, commit


def compose_report(
    *,
    verdict: str,
    request_path: str,
    request_commit: str,
    reviewer_model: str,
    findings: str,
    evidence: str,
    high_risk: bool,
    supersedes: str | None = None,
) -> str:
    lines = [
        "Event type: verification-report",
        f"VERDICT: {verdict}",
        f"Verification request: {request_path}@{request_commit}",
        f"Reviewer model: {reviewer_model}",
    ]
    if high_risk:
        lines.append(f"Abuse Class Assessment: {compact_pair_loop.ABUSE_ASSESSMENT_BOUND_TO_REQUEST}")
    if supersedes:
        lines.append(f"Supersedes: {supersedes}")
    lines += ["", "## Findings", "", findings.strip()]
    if evidence.strip():
        lines += ["", "## Evidence", "", evidence.strip()]
    return "\n".join(lines)


def accept_request(
    root: Path,
    *,
    reviewer: str,
    reviewer_model: str,
    verdict: str,
    findings: str,
    evidence: str,
    subject: str,
    request_path: str | None = None,
    supersedes: str | None = None,
) -> tuple[str, str]:
    """Publish and commit one bound verification-report directly after HEAD's request."""
    root = root.resolve()
    current = _head(root)
    if request_path is None:
        request_path = _request_added_by(root, current)
    try:
        request = compact_pair_loop.parse_verify_request(root, request_path, current)
    except compact_pair_loop.CompactPairError as exc:
        raise ReviewFlowError(
            f"HEAD {current[:12]} is not the valid request commit for {request_path}: {exc}"
        ) from exc
    if request.reviewer_member != reviewer:
        raise ReviewFlowError(
            f"the request names {request.reviewer_member} as reviewer, not {reviewer}"
        )
    body = compose_report(
        verdict=verdict,
        request_path=request_path,
        request_commit=current,
        reviewer_model=reviewer_model,
        findings=findings,
        evidence=evidence,
        high_risk=request.risk_class == compact_pair_loop.HIGH_RISK_CONTROL,
        supersedes=supersedes,
    )
    relative = mailbox_writer.publish(
        root, sender=reviewer, recipient=request.author_member,
        kind="verification-report", subject=subject, body=body,
    )
    commit = _commit_only(root, relative, f"review: {verdict} {subject}")
    report = compact_pair_loop.parse_verification_report(root, relative)
    violations = compact_pair_loop.validate_published_report(root, report, commit)
    if violations:
        raise ReviewFlowError("; ".join(violations))
    return relative, commit


def land_check(root: Path, *, base: str | None, head: str | None) -> tuple[bool, str]:
    """Admission plus the byte-clean landing precondition for one chain."""
    root = root.resolve()
    try:
        base_sha, head_sha = ci_admission_gate.resolve_range(root, base, head)
        outcome = ci_admission_gate.evaluate(root, base_sha, head_sha)
    except ci_admission_gate.AdmissionError as exc:
        raise ReviewFlowError(str(exc)) from exc
    lines = [ci_admission_gate.render(outcome)]
    fast_forward = _is_ancestor(root, base_sha, head_sha)
    if fast_forward:
        lines.append(
            f"  landing: {base_sha[:12]} is an ancestor of {head_sha[:12]}; a "
            "fast-forward or merge commit lands the reviewed chain byte-clean. "
            "Never squash: a squash commit lies outside every reviewed range."
        )
    else:
        lines.append(
            f"  landing: {base_sha[:12]} has moved past the reviewed chain; a merge "
            "commit inherits coverage only when the integration tip is contained "
            "by the reviewed head. Merge the base into the candidate, re-review "
            "the new head, then check again."
        )
    ready = outcome.admitted and fast_forward
    lines.append(
        "  RESULT: READY TO LAND (landing itself still needs exact current user authority)"
        if ready else "  RESULT: NOT READY TO LAND"
    )
    return ready, "\n".join(lines)


def _read_text(path: str | None) -> str:
    if path in (None, "-"):
        return sys.stdin.read()
    return Path(path).read_text(encoding="utf-8")


def publish_main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="bin/pipeline review publish",
        description=(
            "Compose, validate, publish, and commit one verify-request directly "
            "after the reviewed head (Outcome text from --outcome-file or stdin)."
        ),
    )
    parser.add_argument("--repo-root", type=Path, default=ROOT)
    parser.add_argument("--author", required=True)
    parser.add_argument("--author-model", required=True)
    parser.add_argument("--reviewer", required=True)
    parser.add_argument("--risk-class", required=True)
    parser.add_argument("--base", required=True)
    parser.add_argument("--head", default="HEAD")
    parser.add_argument("--subject", required=True)
    parser.add_argument("--outcome-file", default="-")
    parser.add_argument("--abuse-class", action="append", default=[])
    parser.add_argument("--finding-ref", action="append", default=[])
    arguments = parser.parse_args(argv)
    try:
        relative, commit = publish_request(
            arguments.repo_root,
            author=arguments.author,
            author_model=arguments.author_model,
            reviewer=arguments.reviewer,
            risk_class=arguments.risk_class,
            base=arguments.base,
            head=arguments.head,
            outcome=_read_text(arguments.outcome_file),
            subject=arguments.subject,
            abuse_classes=tuple(arguments.abuse_class),
            finding_refs=tuple(arguments.finding_ref),
        )
    except (ReviewFlowError, compact_pair_loop.CompactPairError,
            mailbox_writer.MailboxWriterError, OSError, UnicodeError) as exc:
        print(f"review publish failed: {exc}", file=sys.stderr)
        return 1
    print(f"published {relative} at {commit}")
    return 0


def accept_main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="bin/pipeline review accept",
        description=(
            "Publish and commit one bound verification-report directly after the "
            "request commit at HEAD (Findings from --findings-file or stdin)."
        ),
    )
    parser.add_argument("--repo-root", type=Path, default=ROOT)
    parser.add_argument("--reviewer", required=True)
    parser.add_argument("--reviewer-model", required=True)
    parser.add_argument("--verdict", required=True, choices=sorted(compact_pair_loop.VALID_VERDICTS))
    parser.add_argument("--subject", required=True)
    parser.add_argument("--request", help="request path; default: the one HEAD added")
    parser.add_argument("--findings-file", default="-")
    parser.add_argument("--evidence-file")
    parser.add_argument("--supersedes")
    arguments = parser.parse_args(argv)
    try:
        relative, commit = accept_request(
            arguments.repo_root,
            reviewer=arguments.reviewer,
            reviewer_model=arguments.reviewer_model,
            verdict=arguments.verdict,
            findings=_read_text(arguments.findings_file),
            evidence=_read_text(arguments.evidence_file) if arguments.evidence_file else "",
            subject=arguments.subject,
            request_path=arguments.request,
            supersedes=arguments.supersedes,
        )
    except (ReviewFlowError, compact_pair_loop.CompactPairError,
            mailbox_writer.MailboxWriterError, OSError, UnicodeError) as exc:
        print(f"review accept failed: {exc}", file=sys.stderr)
        return 1
    print(f"published {relative} at {commit}")
    return 0


def land_check_main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="bin/pipeline review land-check",
        description="Check that a reviewed chain admits and can land byte-clean.",
    )
    parser.add_argument("--repo-root", type=Path, default=ROOT)
    parser.add_argument("--base", help="integration base (default: origin/main, then main)")
    parser.add_argument("--head", help="chain head (default: HEAD)")
    arguments = parser.parse_args(argv)
    try:
        ready, text = land_check(arguments.repo_root, base=arguments.base, head=arguments.head)
    except ReviewFlowError as exc:
        print(f"review land-check failed: {exc}", file=sys.stderr)
        return 2
    print(text)
    return 0 if ready else 1


if __name__ == "__main__":
    raise SystemExit(publish_main())
