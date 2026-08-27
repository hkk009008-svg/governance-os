"""Committed-payload admission for new formal and durable mailbox events."""
from __future__ import annotations

from pathlib import Path

import codex_protocol_model
import compact_pair_loop
import mailbox_writer
import protocol_mailbox


def projected_request(
    projection, repo_root: Path, path: str, commit: str, *, current_policy: bool
):
    """Parse and bind one exact committed request without worktree bytes."""

    introduction = projection.introductions.get(path)
    raw = projection.introduction_events.get(path)
    if introduction is None or raw is None or introduction[0] != commit:
        raise mailbox_writer.MailboxWriterError(
            f"request binding is not its exact introduction: {path}@{commit}"
        )
    request = compact_pair_loop.parse_verify_request_committed_bytes(
        repo_root,
        path,
        commit,
        raw,
        allow_frozen_legacy=False,
        historical_remediation_base_compatibility=(
            projection.commits.object_types.get(
                compact_pair_loop.REMEDIATION_BASE_CUTOFF
            ) == "commit"
            and projection.commits.is_ancestor(
                commit, compact_pair_loop.REMEDIATION_BASE_CUTOFF
            )
        ),
        commit_projection=projection.commits,
        # Explicit target repositories need their own object graph. This reads
        # Git objects, never the mutable worktree payload.
        allow_git_fallback=True,
    )
    if current_policy and not codex_protocol_model.model_is_current_author(
        request.author_model
    ):
        raise mailbox_writer.MailboxWriterError(
            "Author model must resolve to a currently admitted author model "
            "for a new verify-request"
        )
    if current_policy:
        compact_pair_loop._require_path_references_resolve(
            repo_root, request.finding_refs
        )
    violations = compact_pair_loop.validate_request_range(
        repo_root,
        request,
        commit_projection=projection.commits,
        allow_git_fallback=True,
    )
    if violations:
        raise mailbox_writer.MailboxWriterError("; ".join(violations))
    if current_policy and request.remediates_failed_report is not None:
        target_path, target_commit = request.remediates_failed_report
        target, _ = projected_report(
            projection,
            repo_root,
            target_path,
            target_commit,
            current_policy=False,
        )
        violations = compact_pair_loop.remediation_request_violations(
            request, target, target_commit
        )
        if violations:
            raise mailbox_writer.MailboxWriterError(
                "remediation binding invalid: " + "; ".join(violations)
            )
    return request


def projected_report(
    projection, repo_root: Path, path: str, commit: str, *, current_policy: bool
):
    """Parse and bind one exact committed report without worktree bytes."""

    introduction = projection.introductions.get(path)
    raw = projection.introduction_events.get(path)
    if introduction is None or raw is None or introduction[0] != commit:
        raise mailbox_writer.MailboxWriterError(
            f"report binding is not its exact introduction: {path}@{commit}"
        )
    historical_model_policy = not current_policy and (
        projection.review_family_cutover_events is None
        or projection.review_family_cutover_events.get(path) == raw
    )
    report = compact_pair_loop.parse_verification_report_committed_bytes(
        repo_root,
        path,
        raw,
        frozen_legacy=path in projection.frozen_legacy_reports,
        historical_model_family_compatibility=historical_model_policy,
    )
    if current_policy:
        compact_pair_loop._require_path_references_resolve(
            repo_root, report.finding_refs
        )
        compact_pair_loop._require_path_references_resolve(
            repo_root, tuple(ref for ref, _ in report.finding_dispositions)
        )
    request_raw = projection.introduction_events.get(report.request_path)
    request_is_current = current_policy and (
        projection.review_family_cutover_events is not None
        and request_raw is not None
        and projection.review_family_cutover_events.get(report.request_path)
        != request_raw
    )
    request = projected_request(
        projection,
        repo_root,
        report.request_path,
        report.request_commit,
        current_policy=request_is_current,
    )
    violations = compact_pair_loop.validate_report_binding(report, request)
    if violations:
        raise mailbox_writer.MailboxWriterError("; ".join(violations))
    if report.request_commit == commit or not projection.commits.is_ancestor(
        report.request_commit, commit
    ):
        raise mailbox_writer.MailboxWriterError(
            "report introduction must be strictly after its request"
        )
    if not current_policy:
        return report, request
    if request.remediates_failed_report is not None and report.supersedes is None:
        raise mailbox_writer.MailboxWriterError(
            "supersession binding invalid: remediation report must explicitly "
            "supersede the failed report"
        )
    if report.supersedes is not None:
        target_path, target_commit = report.supersedes
        target, _ = projected_report(
            projection,
            repo_root,
            target_path,
            target_commit,
            current_policy=False,
        )
        violations = compact_pair_loop.supersession_report_violations(
            report,
            target,
            request=request,
            superseded_commit=target_commit,
        )
        if violations:
            raise mailbox_writer.MailboxWriterError(
                "supersession binding invalid: " + "; ".join(violations)
            )
        if target_commit == commit or not projection.commits.is_ancestor(
            target_commit, commit
        ):
            raise mailbox_writer.MailboxWriterError(
                "superseded report must be strictly before its replacement"
            )
    return report, request


def validate_committed_new_event(
    projection, repo_root: Path, path: str, raw: bytes, introduction_commit: str
) -> None:
    """Apply new-write payload policy using only committed projections."""

    match = mailbox_writer.validate_event_envelope_bytes(
        repo_root, raw, path, kinds=projection.kinds
    )
    kind = match.group("kind")
    problem = mailbox_writer.new_write_envelope_problem(
        kind, match.group("sender"), match.group("recipient")
    )
    if problem is not None:
        raise mailbox_writer.MailboxWriterError(problem)
    if kind == "verify-request":
        projected_request(
            projection, repo_root, path, introduction_commit, current_policy=True
        )
        return
    if kind == "verification-report":
        projected_report(
            projection, repo_root, path, introduction_commit, current_policy=True
        )
        return
    if kind == "findings":
        try:
            text = raw.decode("utf-8", errors="strict")
            event = protocol_mailbox.parse_committed_event_text(
                f"{path}@{introduction_commit}", text
            )
            statement = protocol_mailbox.parse_checkpoint_statement(event)
            with protocol_mailbox.CommittedObjectBatchReader(repo_root) as reader:
                protocol_mailbox.validate_checkpoint_references(reader, statement)
        except (UnicodeDecodeError, ValueError) as exc:
            raise mailbox_writer.MailboxWriterError(
                f"findings checkpoint is invalid: {exc}"
            ) from exc
        return
    if kind == "decision":
        try:
            text = raw.decode("utf-8", errors="strict")
        except UnicodeDecodeError as exc:
            raise mailbox_writer.MailboxWriterError(
                "decision candidate is not UTF-8"
            ) from exc
        if not protocol_mailbox.learning_disposition_intent(text):
            raise mailbox_writer.MailboxWriterError(
                "decision candidate is invalid: durable decision must be a fully "
                "typed learning disposition"
            )
        return
    if kind == "learning-candidate":
        return
    raise mailbox_writer.MailboxWriterError(f"unhandled new-write kind: {kind}")
