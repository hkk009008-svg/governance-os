#!/usr/bin/env python3
"""ci_admission_gate.py — risk-aware admission for authority-surface ranges.

The repository classifies review depth by risk (`review_profile_for`), binds
formal review to committed Compact Pair artifacts (`compact_pair_loop`), and
already validates those artifacts in smoke. What no gate did was connect the
two at the integration boundary: a pull request that rewrites an authority
surface (fixed writers, app adapters, dispatchers, CI itself) could merge with no
committed review at all. This gate closes exactly that gap and nothing more:

  1. Resolve the admitted range (default: merge-base with origin/main .. HEAD,
     falling back to local main when no remote-tracking main exists).
  2. List the commits in that range that touch an authority surface.
  3. Reject changes to already-published formal artifacts, even in mailbox-only
     ranges. Requests and reports are append-only; supersession retains originals.
     Otherwise, if there are no authority changes, ordinary and material work keeps its
     existing proportionate verification; this gate adds no ceremony to it.
  4. Otherwise require every such commit to be covered by a committed,
     structurally valid verification-report at HEAD whose verdict is GO or
     NITS and whose bound request declares `high-risk-control`. Validation is
     delegated to the canonical `compact_pair_loop.validate_report`, which
     validates the report's declared non-author seat and model-family fields.
     A two-parent merge inherits that report only when it is a byte-clean
     landing of exactly Reviewed head -> request -> report onto an integration
     parent already contained by Reviewed head.
     A current FAIL blocks until superseded; valid remediation carries the
     failed report's reviewed range forward instead of orphaning it.
     Repository bytes cannot attest which provider actually executed a review;
     protected external review identity/rules remain a separate requirement.

The gate reports capability facts about committed evidence. It grants no
authority, publishes nothing, and never mutates the repository.

Exit codes: 0 admitted; 1 blocked; 2 usage/environment error.
"""
from __future__ import annotations

import argparse
import os
import sys
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
for _path in (_REPO_ROOT, _SCRIPTS_DIR):
    if _path not in sys.path:
        sys.path.insert(0, _path)

import compact_pair_loop as pair  # noqa: E402
import git_runner  # noqa: E402
import mailbox_writer  # noqa: E402
import protocol_mailbox  # noqa: E402

# Authority surfaces: executable authority, side-effect gating, trust-granting
# composition, and the integration gate itself. Directory entries end with a
# slash and match by prefix; file entries match exactly. Extending this list
# is itself an authority-surface change, so the extension gets reviewed.
AUTHORITY_SURFACES: tuple[str, ...] = (
    ".agents/plugins/",
    ".agents/skills/",
    ".claude/agents/",
    ".claude/settings.json",
    ".claude/skills/",
    ".codex/agents/",
    ".codex/config.toml",
    ".mcp.json",
    ".github/workflows/",
    "config/",
    ":(glob)tests/**/conftest.py",
    "AGENTS.md",
    "ARCHITECTURE.md",
    "bin/pipeline",
    "CLAUDE.md",
    "OPERATIONS.md",
    "README.md",
    "conftest.py",
    "coordination/bin/",
    "coordination/mailbox/kinds.txt",
    "docs/protocol/",
    "pyproject.toml",
    "pytest.ini",
    "requirements-dev.txt",
    "pipeline/",
    "setup.cfg",
    "sitecustomize.py",
    "tests/unit/test_provider_surface_map.py",
    "tox.ini",
    "usercustomize.py",
)

_MAILBOX_SENT = "coordination/mailbox/sent/"
_REPORT_SUFFIX = "-verification-report.md"


class AdmissionError(RuntimeError):
    """The admitted range or its evidence cannot be resolved."""


@dataclass
class Coverage:
    """One admissible report and the commits its reviewed range contains."""

    path: str
    verdict: str
    risk_class: str
    reviewed_commits: frozenset[str]


@dataclass
class Outcome:
    base: str
    head: str
    authority_commits: dict[str, tuple[str, ...]] = field(default_factory=dict)
    coverages: list[Coverage] = field(default_factory=list)
    blocking_failures: list[tuple[str, frozenset[str]]] = field(default_factory=list)
    skipped_reports: list[tuple[str, str]] = field(default_factory=list)
    uncovered: dict[str, tuple[str, ...]] = field(default_factory=dict)
    artifact_mutations: list[str] = field(default_factory=list)

    @property
    def admitted(self) -> bool:
        return not self.uncovered and not self.blocking_failures and not self.artifact_mutations


def _git(root: Path, *args: str, input_data: str | None = None) -> str:
    result = git_runner.run_git(
        root, args, mode="authority", text=True, input_data=input_data
    )
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip()
        raise AdmissionError(detail or f"git {' '.join(args)} failed")
    return result.stdout


def resolve_range(root: Path, base: str | None, head: str | None) -> tuple[str, str]:
    resolved_head = _git(root, "rev-parse", (head or "HEAD") + "^{commit}").strip()
    if base:
        resolved_base = _git(root, "rev-parse", base + "^{commit}").strip()
        return resolved_base, resolved_head
    # Model the integration target when it exists. CI supplies immutable
    # base/head SHAs explicitly; repositories without a remote fall back to
    # their local main branch.
    for candidate in ("origin/main", "main"):
        try:
            resolved_base = _git(
                root, "merge-base", candidate, resolved_head
            ).strip()
        except AdmissionError:
            continue
        return resolved_base, resolved_head
    raise AdmissionError(
        "cannot resolve a base: pass --base or provide origin/main or main"
    )


def _surface_pathspecs() -> list[str]:
    return [surface.rstrip("/") for surface in AUTHORITY_SURFACES]


def authority_commits(root: Path, base: str, head: str) -> dict[str, tuple[str, ...]]:
    """Map each range commit touching an authority surface to those paths."""

    marker = "__admission_commit__:"
    revisions = _git(root, "rev-list", f"{base}..{head}")
    output = _git(
        root,
        "diff-tree",
        "--stdin",
        "--root",
        "-m",
        "-r",
        f"--format={marker}%H",
        "--name-only",
        "--",
        *_surface_pathspecs(),
        input_data=revisions,
    )
    commit_paths: dict[str, set[str]] = {}
    current: str | None = None
    paths: list[str] = []
    for line in output.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith(marker):
            if current is not None and paths:
                commit_paths.setdefault(current, set()).update(paths)
            current = stripped[len(marker):]
            paths = []
            continue
        paths.append(stripped)
    if current is not None and paths:
        commit_paths.setdefault(current, set()).update(paths)
    return {
        commit: tuple(sorted(paths))
        for commit, paths in commit_paths.items()
    }


def _artifact_changes(root: Path, base: str, head: str) -> tuple[list[str], list[str]]:
    """Inspect every parent diff, not just the net tree, so restore cannot erase tampering.

    This protects evidence in the supplied history, not discarded/unpublished branches.
    Legacy paths are still discovered for the existing reader but do not acquire a new
    publication grammar. Rename detection is disabled: moving an artifact deletes it.
    """
    marker = "__artifact_commit__:"
    revisions = _git(root, "rev-list", f"{base}..{head}")
    output = _git(
        root,
        "diff-tree",
        "--stdin",
        "--root",
        "-m",
        "-r",
        "--no-renames",
        f"--format={marker}%H",
        "--name-status",
        "--diff-filter=AMRTD",
        "--",
        _MAILBOX_SENT.rstrip("/"),
        input_data=revisions,
    )
    paths: set[str] = set()
    mutations: set[str] = set()
    commit = ""
    for line in output.splitlines():
        if line.startswith(marker):
            commit = line[len(marker):]
            continue
        if not line:
            continue
        change, path = line.split("\t", 1)
        paths.add(path)
        if change != "A" and (pair.REQUEST_RE.fullmatch(path) or pair.REPORT_RE.fullmatch(path)):
            mutations.add(f"{commit}: {change} {path}")
    return sorted(paths), sorted(mutations)


def _known_kinds_at(root: Path, head: str) -> frozenset[str]:
    """Read the candidate commit's kind registry, never checkout bytes."""

    text = _git(root, "show", f"{head}:coordination/mailbox/kinds.txt")
    kinds = frozenset(
        line.strip()
        for line in text.splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    )
    required = {"verify-request", "verification-report"}
    if not required <= kinds:
        raise AdmissionError(
            "candidate mailbox kind registry lacks formal review kinds"
        )
    return kinds


def _validate_current_envelope(
    root: Path,
    raw: bytes,
    path: str,
    kinds: frozenset[str],
) -> None:
    envelope = mailbox_writer.validate_event_envelope_bytes(
        root, raw, path, kinds=kinds
    )
    problem = mailbox_writer.new_write_envelope_problem(
        envelope.group("kind"),
        envelope.group("sender"),
        envelope.group("recipient"),
    )
    if problem is not None:
        raise pair.CompactPairError(problem)


def _introduction_commit(root: Path, head: str, path: str) -> str:
    commit = _git(
        root, "log", "--full-history", "--diff-filter=A", "--format=%H", "-1", head, "--", path
    ).strip()
    if len(commit) != 40:
        raise AdmissionError(f"cannot resolve introduction commit for {path}")
    return commit


def _reviewed_commits(root: Path, request: pair.VerifyRequest) -> frozenset[str]:
    try:
        output = _git(
            root,
            "rev-list",
            f"{request.reviewed_base}..{request.reviewed_head}",
        )
    except AdmissionError:
        # A report about another repository resolves nowhere here and simply
        # covers nothing; it is not an error for this repository's gate.
        return frozenset()
    return frozenset(line.strip() for line in output.splitlines() if line.strip())


def _coverage_commits(
    root: Path,
    report: pair.VerificationReport,
    request: pair.VerifyRequest,
    reports_by_ref: dict[
        tuple[str, str], tuple[pair.VerificationReport, pair.VerifyRequest]
    ],
) -> frozenset[str]:
    commits = set(_reviewed_commits(root, request))
    seen: set[tuple[str, str]] = set()
    while report.supersedes in reports_by_ref and report.supersedes not in seen:
        seen.add(report.supersedes)
        report, request = reports_by_ref[report.supersedes]
        commits.update(_reviewed_commits(root, request))
    return frozenset(commits)


def _commit_parents(root: Path, commit: str) -> tuple[str, ...]:
    return tuple(_git(root, "show", "-s", "--format=%P", commit).split())


def _is_ancestor(root: Path, ancestor: str, descendant: str) -> bool:
    result = git_runner.run_git(
        root,
        ("merge-base", "--is-ancestor", ancestor, descendant),
        mode="authority",
        text=True,
    )
    if result.returncode not in (0, 1):
        detail = result.stderr.strip() or result.stdout.strip()
        raise AdmissionError(detail or "git merge-base --is-ancestor failed")
    return result.returncode == 0


def _only_commit_path(root: Path, parent: str, commit: str, path: str) -> bool:
    return _git(
        root, "diff-tree", "--no-commit-id", "--name-only", "-r", parent, commit
    ).splitlines() == [path]


def _inherited_clean_merge_commits(
    root: Path,
    report: pair.VerificationReport,
    request: pair.VerifyRequest,
    report_commit: str,
    candidates: dict[str, tuple[str, ...]],
) -> frozenset[str]:
    """Cover only a byte-clean merge of one exact reviewed artifact pair."""

    if not (
        _commit_parents(root, report.request_commit) == (request.reviewed_head,)
        and _only_commit_path(
            root, request.reviewed_head, report.request_commit, report.request_path
        )
        and _commit_parents(root, report_commit) == (report.request_commit,)
        and _only_commit_path(root, report.request_commit, report_commit, report.path)
    ):
        return frozenset()

    report_tree = _git(root, "rev-parse", f"{report_commit}^{{tree}}").strip()
    inherited: set[str] = set()
    for commit in candidates:
        parents = _commit_parents(root, commit)
        if (
            len(parents) == 2
            and parents[1] == report_commit
            and _is_ancestor(root, parents[0], request.reviewed_head)
            and _git(root, "rev-parse", f"{commit}^{{tree}}").strip() == report_tree
        ):
            inherited.add(commit)
    return frozenset(inherited)


@pair.request_read_scope()
def evaluate(root: Path, base: str, head: str) -> Outcome:
    outcome = Outcome(base=base, head=head)
    touched_events, outcome.artifact_mutations = _artifact_changes(root, base, head)
    if outcome.artifact_mutations:
        return outcome
    outcome.authority_commits = authority_commits(root, base, head)
    if not outcome.authority_commits:
        return outcome

    kinds = _known_kinds_at(root, head)
    parsed: dict[str, tuple[pair.VerificationReport, pair.VerifyRequest]] = {}
    carried_from_base: set[str] = set()
    for path in (item for item in touched_events if item.endswith(_REPORT_SUFFIX)):
        introduction = _introduction_commit(root, head, path)
        try:
            raw = _git(root, "show", f"{head}:{path}").encode("utf-8")
        except AdmissionError:
            # Retiring history is allowed, but trusted-base verdicts still
            # govern until a valid superseding report exists.
            try:
                raw = _git(root, "show", f"{base}:{path}").encode("utf-8")
            except AdmissionError:
                outcome.skipped_reports.append(
                    (path, "absent at integration base and candidate head")
                )
                continue
            carried_from_base.add(path)
        else:
            if raw != _git(root, "show", f"{introduction}:{path}").encode("utf-8"):
                raise AdmissionError(f"immutable review artifact changed: {path}")
        try:
            _validate_current_envelope(root, raw, path, kinds)
            report = pair.parse_verification_report_committed_bytes(root, path, raw)
        except (mailbox_writer.MailboxWriterError, pair.CompactPairError) as exc:
            outcome.skipped_reports.append((path, f"unparseable: {exc}"))
            continue
        # Trusted PR admission deliberately keeps the checkout at the base and
        # reads the fetched candidate by explicit SHA. Supersession ancestry
        # must use that same candidate history, not the checkout's literal HEAD.
        violations = pair.validate_published_report(
            root, report, introduction, history_head=head
        )
        if violations:
            outcome.skipped_reports.append((path, "; ".join(violations)))
            continue
        try:
            request = pair.request_for_report(root, report)
        except pair.CompactPairError as exc:
            outcome.skipped_reports.append((path, f"request binding invalid: {exc}"))
            continue
        parsed[path] = report, request

    superseded = {
        report.supersedes
        for report, _request in parsed.values()
        if report.supersedes
    }
    introductions = {path: _introduction_commit(root, head, path) for path in parsed}
    reports_by_ref = {
        (path, introductions[path]): item for path, item in parsed.items()
    }

    for path, (report, request) in sorted(parsed.items()):
        if (path, introductions[path]) in superseded:
            outcome.skipped_reports.append((path, "superseded by a later report"))
            continue
        if report.verdict not in pair.ADMITTING_VERDICTS:
            outcome.skipped_reports.append(
                (path, f"verdict {report.verdict} does not admit")
            )
            if (
                report.verdict == "FAIL"
                and report.reviewer_member in protocol_mailbox.FORMAL_REVIEWERS
            ):
                failed_commits = _coverage_commits(
                    root, report, request, reports_by_ref
                )
                failed_commits &= outcome.authority_commits.keys()
                if failed_commits or path in carried_from_base:
                    outcome.blocking_failures.append((path, frozenset(failed_commits)))
            continue
        if request.risk_class != pair.HIGH_RISK_CONTROL:
            outcome.skipped_reports.append(
                (
                    path,
                    "authority surfaces require an explicit "
                    f"{pair.HIGH_RISK_CONTROL} review "
                    f"(request declares {request.risk_class})",
                )
            )
            continue
        outcome.coverages.append(
            Coverage(
                path=path,
                verdict=report.verdict,
                risk_class=request.risk_class,
                reviewed_commits=(
                    _coverage_commits(root, report, request, reports_by_ref)
                    | _inherited_clean_merge_commits(
                        root,
                        report,
                        request,
                        introductions[path],
                        outcome.authority_commits,
                    )
                ),
            )
        )

    covered: set[str] = set()
    for coverage in outcome.coverages:
        covered |= coverage.reviewed_commits
    outcome.uncovered = {
        commit: paths
        for commit, paths in outcome.authority_commits.items()
        if commit not in covered
    }
    return outcome


def render(outcome: Outcome, *, verbose: bool = False) -> str:
    lines = [
        "ADMISSION GATE — risk-aware integration check "
        f"({outcome.base[:12]}..{outcome.head[:12]})"
    ]
    if outcome.artifact_mutations:
        lines.extend(f"  immutable artifact changed: {item}" for item in outcome.artifact_mutations)
        lines.append("  RESULT: BLOCKED — published formal artifacts are append-only")
        lines.append("  remedy: retain original artifacts and publish a valid Supersedes report")
        return "\n".join(lines)
    if not outcome.authority_commits:
        lines.append(
            "  no authority-surface commits in range — admitted without review "
            "requirement (ordinary/material verification still applies)"
        )
        return "\n".join(lines)
    lines.append(
        f"  authority-surface commits: {len(outcome.authority_commits)}"
    )
    for coverage in outcome.coverages:
        lines.append(
            f"  admissible report: {coverage.path} "
            f"[{coverage.verdict}, {coverage.risk_class}]"
        )
    if verbose:
        for path, reason in outcome.skipped_reports:
            lines.append(f"  non-admitting report: {path} — {reason}")
    elif outcome.skipped_reports:
        lines.append(
            f"  non-admitting reports: {len(outcome.skipped_reports)} "
            "(use --verbose for paths)"
        )
        for reason, count in Counter(
            reason for _path, reason in outcome.skipped_reports
        ).most_common():
            lines.append(f"    {count} x {reason}")
    for path, commits in outcome.blocking_failures:
        lines.append(
            f"  active FAIL: {path} [{len(commits)} authority commit(s) in range]"
        )
    if outcome.admitted:
        lines.append(
            "  RESULT: structurally admitted — every authority commit is covered "
            "by declared review evidence (runtime reviewer identity is externally attested)"
        )
        return "\n".join(lines)
    lines.append("  RESULT: BLOCKED — active FAIL or uncovered authority-surface commit")
    for commit, paths in sorted(outcome.uncovered.items()):
        lines.append(f"    {commit[:12]} touches {', '.join(paths)}")
    lines.append(
        "  remedy: explicitly supersede active FAILs and obtain a committed "
        f"GO/NITS {pair.HIGH_RISK_CONTROL} review for uncovered commits"
    )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(_REPO_ROOT))
    parser.add_argument(
        "--base",
        help="admitted range base (default: origin/main, then local main)",
    )
    parser.add_argument("--head", help="admitted range head (default: HEAD)")
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="list every non-admitting historical report",
    )
    args = parser.parse_args(argv)
    root = args.root.resolve()
    try:
        base, head = resolve_range(root, args.base, args.head)
        if base == head:
            print(
                "ADMISSION GATE — empty range (base equals head); nothing to admit"
            )
            return 0
        outcome = evaluate(root, base, head)
    except AdmissionError as exc:
        print(f"ADMISSION GATE — environment error: {exc}", file=sys.stderr)
        return 2
    print(render(outcome, verbose=args.verbose))
    return 0 if outcome.admitted else 1


if __name__ == "__main__":
    raise SystemExit(main())
