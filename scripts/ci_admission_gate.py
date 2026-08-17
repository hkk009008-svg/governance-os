#!/usr/bin/env python3
"""ci_admission_gate.py — risk-aware admission for authority-surface ranges.

The repository classifies review depth by risk (`review_profile_for`), binds
formal review to committed Compact Pair artifacts (`compact_pair_loop`), and
already validates those artifacts in smoke. What no gate did was connect the
two at the integration boundary: a pull request that rewrites an authority
surface (hook policy, fixed writers, launchers, CI itself) could merge with no
committed review at all. This gate closes exactly that gap and nothing more:

  1. Resolve the admitted range (default: merge-base with main .. HEAD).
  2. List the commits in that range that touch an authority surface.
  3. If there are none, admit silently — ordinary and material work keeps its
     existing proportionate verification; this gate adds no ceremony to it.
  4. Otherwise require every such commit to be covered by a committed,
     structurally valid verification-report at HEAD whose verdict is GO or
     NITS and whose bound request declares `high-risk-control`. Validation is
     delegated to the canonical `compact_pair_loop.validate_report`, which
     validates the report's declared non-author seat and model-family fields.
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
from dataclasses import dataclass, field
from pathlib import Path

_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
for _path in (_REPO_ROOT, _SCRIPTS_DIR):
    if _path not in sys.path:
        sys.path.insert(0, _path)

import compact_pair_loop as pair  # noqa: E402
import git_runner  # noqa: E402

# Authority surfaces: executable authority, side-effect gating, trust-granting
# composition, and the integration gate itself. Directory entries end with a
# slash and match by prefix; file entries match exactly. Extending this list
# is itself an authority-surface change, so the extension gets reviewed.
AUTHORITY_SURFACES: tuple[str, ...] = (
    ".agents/skills/",
    ".claude/agents/",
    ".claude/settings.json",
    ".claude/skills/",
    ".codex/agents/",
    ".codex/config.toml",
    ".github/workflows/",
    "config/",
    ":(glob)tests/**/conftest.py",
    "AGENTS.md",
    "ARCHITECTURE.md",
    "CLAUDE.md",
    "OPERATIONS.md",
    "README.md",
    "RUNBOOK-DAILY.md",
    "conftest.py",
    "coordination/bin/",
    "coordination/mailbox/kinds.txt",
    "coordination/threeway/keys/",
    "docs/PROGRAM-MANUAL.md",
    "docs/REMEDIATION-INVENTORY.md",
    "docs/protocol/",
    "governance.toml",
    "pyproject.toml",
    "pytest.ini",
    "requirements-dev.txt",
    "requirements-connector.in",
    "requirements-connector.txt",
    "requirements-governance.txt",
    "scripts/",
    "setup.cfg",
    "sitecustomize.py",
    "tests/unit/test_provider_surface_map.py",
    "tox.ini",
    "threeway/",
    "usercustomize.py",
)

_MAILBOX_SENT = "coordination/mailbox/sent/"
_REPORT_SUFFIX = "-verification-report.md"
_ADMITTING_VERDICTS = frozenset({"GO", "NITS"})


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
    # Equal to `head` on the embedded path, where evidence rides the
    # implementation branch. A distinct value is a separate governance tip.
    governance_head: str = ""
    authority_commits: dict[str, tuple[str, ...]] = field(default_factory=dict)
    coverages: list[Coverage] = field(default_factory=list)
    skipped_reports: list[tuple[str, str]] = field(default_factory=list)
    uncovered: dict[str, tuple[str, ...]] = field(default_factory=dict)

    @property
    def admitted(self) -> bool:
        return not self.uncovered


def _git(root: Path, *args: str) -> str:
    result = git_runner.run_git(
        root, args, mode="authority", text=True
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
    output = _git(
        root,
        "log",
        "-m",
        f"--format={marker}%H",
        "--name-only",
        f"{base}..{head}",
        "--",
        *_surface_pathspecs(),
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


def _reports_added_in_range(root: Path, base: str, head: str) -> list[str]:
    output = _git(
        root,
        "diff",
        "--name-only",
        "--diff-filter=A",
        f"{base}..{head}",
        "--",
        _MAILBOX_SENT.rstrip("/"),
    )
    return sorted(
        line.strip()
        for line in output.splitlines()
        if line.strip().endswith(_REPORT_SUFFIX)
    )


def _introduction_commit(root: Path, head: str, path: str) -> str:
    commit = _git(
        root, "log", "--diff-filter=A", "--format=%H", "-1", head, "--", path
    ).strip()
    if len(commit) != 40:
        raise AdmissionError(f"cannot resolve introduction commit for {path}")
    return commit


def _governance_commits(root: Path, head: str, governance_head: str) -> list[str]:
    """Return a governance-only span proven descendant and one-parent linear.

    This stage does not prove commit content or canonical-event completeness;
    evidence still comes from `base..head`, so the tip remains inert until the
    content and envelope successors land. Reads Git objects without checkout
    or execution.
    """

    if governance_head == head:
        return []
    try:
        _git(root, "merge-base", "--is-ancestor", head, governance_head)
    except AdmissionError:
        raise AdmissionError(
            "governance head must descend from the reviewed head"
        ) from None
    span = f"{head}..{governance_head}"
    commits = _git(root, "rev-list", "--reverse", span).split()
    for commit in commits:
        if len(_git(root, "rev-list", "--parents", "-1", commit).split()) != 2:
            raise AdmissionError(
                f"governance commit {commit[:12]} is not a linear successor"
            )
    return commits


def _reviewed_commits(root: Path, report: pair.VerificationReport) -> frozenset[str]:
    try:
        output = _git(
            root,
            "rev-list",
            f"{report.reviewed_base}..{report.reviewed_head}",
        )
    except AdmissionError:
        # A report about another repository resolves nowhere here and simply
        # covers nothing; it is not an error for this repository's gate.
        return frozenset()
    return frozenset(line.strip() for line in output.splitlines() if line.strip())


def evaluate(
    root: Path, base: str, head: str, governance_head: str | None = None
) -> Outcome:
    governance = governance_head or head
    outcome = Outcome(base=base, head=head, governance_head=governance)
    # Validate before the no-authority return; evidence still comes from
    # base..head.
    _governance_commits(root, head, governance)
    # Authority is always computed from the reviewed range, never from the
    # governance tip: evidence may advance, the range under review may not.
    outcome.authority_commits = authority_commits(root, base, head)
    if not outcome.authority_commits:
        return outcome


    parsed: dict[str, pair.VerificationReport] = {}
    for path in _reports_added_in_range(root, base, head):
        raw = _git(root, "show", f"{head}:{path}").encode("utf-8")
        try:
            report = pair.parse_verification_report_committed_bytes(root, path, raw)
        except pair.CompactPairError as exc:
            outcome.skipped_reports.append((path, f"unparseable: {exc}"))
            continue
        violations = pair.validate_report(root, report)
        if violations:
            outcome.skipped_reports.append((path, "; ".join(violations)))
            continue
        parsed[path] = report

    superseded: set[tuple[str, str]] = set()
    introductions: dict[str, str] = {}
    for path, report in parsed.items():
        if report.supersedes is not None:
            superseded.add(report.supersedes)
    for path in parsed:
        introductions[path] = _introduction_commit(root, head, path)

    for path, report in sorted(parsed.items()):
        if (path, introductions[path]) in superseded:
            outcome.skipped_reports.append((path, "superseded by a later report"))
            continue
        if report.verdict not in _ADMITTING_VERDICTS:
            outcome.skipped_reports.append(
                (path, f"verdict {report.verdict} does not admit")
            )
            continue
        if report.risk_class != pair.HIGH_RISK_CONTROL or not report.risk_class_explicit:
            outcome.skipped_reports.append(
                (
                    path,
                    "authority surfaces require an explicit "
                    f"{pair.HIGH_RISK_CONTROL} review "
                    f"(report declares {report.risk_class})",
                )
            )
            continue
        outcome.coverages.append(
            Coverage(
                path=path,
                verdict=report.verdict,
                risk_class=report.risk_class,
                reviewed_commits=_reviewed_commits(root, report),
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


def render(outcome: Outcome) -> str:
    lines = [
        "ADMISSION GATE — risk-aware integration check "
        f"({outcome.base[:12]}..{outcome.head[:12]})"
    ]
    if outcome.governance_head and outcome.governance_head != outcome.head:
        lines.append(f"  governance head: {outcome.governance_head[:12]}")
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
    for path, reason in outcome.skipped_reports:
        lines.append(f"  non-admitting report: {path} — {reason}")
    if outcome.admitted:
        lines.append(
            "  RESULT: structurally admitted — every authority commit is covered "
            "by declared review evidence (runtime reviewer identity is externally attested)"
        )
        return "\n".join(lines)
    lines.append(
        "  RESULT: BLOCKED — authority-surface commits lack a committed "
        f"GO/NITS {pair.HIGH_RISK_CONTROL} verification-report covering them:"
    )
    for commit, paths in sorted(outcome.uncovered.items()):
        lines.append(f"    {commit[:12]} touches {', '.join(paths)}")
    lines.append(
        "  remedy: obtain an externally attestable non-author, different-model "
        "review of the exact range, then publish its Compact Pair verify-request "
        "and GO/NITS report through the fixed writer and commit both events on "
        "this branch"
    )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(_REPO_ROOT))
    parser.add_argument("--base", help="admitted range base (default: merge-base with main)")
    parser.add_argument("--head", help="admitted range head (default: HEAD)")
    parser.add_argument(
        "--governance-head",
        help="separate governance tip carrying the evidence (default: the head)",
    )
    args = parser.parse_args(argv)
    root = args.root.resolve()
    try:
        base, head = resolve_range(root, args.base, args.head)
        governance = (
            _git(root, "rev-parse", args.governance_head + "^{commit}").strip()
            if args.governance_head
            else head
        )
        # Route empty ranges through the same evaluation seam before
        # presentation.
        outcome = evaluate(root, base, head, governance)
        if base == head:
            print(
                "ADMISSION GATE — empty range (base equals head); nothing to admit"
            )
            return 0
    except AdmissionError as exc:
        print(f"ADMISSION GATE — environment error: {exc}", file=sys.stderr)
        return 2
    print(render(outcome))
    return 0 if outcome.admitted else 1


if __name__ == "__main__":
    raise SystemExit(main())
