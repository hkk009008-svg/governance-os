#!/usr/bin/env python3
"""Read-only quality-slope reporter: execution health over time, from durable state.

Motivation (learning-plane evidence source): scaffolding subtraction and
addition decisions need a slope, not an anecdote. This tool reports how review
outcomes, rework, overclaim vocabulary, deferred-defect pins, and
intended-vs-landed divergence move across time windows, so a
`learning-candidate` proposing to add or retire ceremony can cite a measured
trend instead of memory. Advisory by construction (contract I1/I2): output
binds nothing, gates nothing, and grants no authority; exit code is always 0.

Read-only by construction: this tool writes nothing. Every number is computed
from durable state at one resolved commit — committed mailbox events, Git
history, and committed logs — never from a live worktree, so verdicts are
checkout-independent. Events are bucketed by their filename UTC timestamp;
window boundaries count back from the measured commit's committer time.

Metrics and sources (each output line names its source):
1.  verdicts / first-pass GO   — light field scan of committed verification
                                 reports (VERDICT + Verification request
                                 lines). First-pass = the earliest report a
                                 request received is GO.
2.  fail chains                — FAIL reports joined to their recorded
                                 closure: a later `Supersedes:` GO/NITS report,
                                 a later GO/NITS report bound to the same
                                 request, or a `Remediates failed report:`
                                 request whose first report is GO/NITS.
                                 `head_changed` distinguishes rework that
                                 changed the reviewed range (the intervention
                                 produced a change) from same-head re-review
                                 (it did not). `no_recorded_closure` means no
                                 scanned field joins the FAIL to a follow-up —
                                 pre-schema chains that continued under a
                                 fresh request path land here by design.
3.  review latency             — seconds from request filename timestamp to
                                 its first report's filename timestamp.
4.  reviewed-head landing      — is each request's `Reviewed head:` reachable
                                 from the measured commit (git rev-list set
                                 membership)? Unresolvable heads are reported,
                                 never treated as landed or unlanded.
5.  overclaim flags            — claim_check.sweep_range between consecutive
                                 window boundary commits (first-parent).
                                 Vocabulary lens only; a flag is a pointer,
                                 not a judgment.
6.  regression pins open       — anchored `@pytest.mark.xfail(strict=True`
                                 decorator occurrences under tests/ at each
                                 window boundary commit (single-line
                                 decorators only; quoted fixture mentions do
                                 not match the anchor).
7.  claims ledger provenance   — logs/claims/ledger.jsonl rows at the measured
                                 commit, bucketed by their `when` field;
                                 premise statuses counted per window (ASSUMED
                                 rows are recorded blank cells, not failures).

Continuity and learning throughput are measured from the same committed
substrate: checkpoint records (findings events carrying the canonical
``Checkpoint:``/``Next action:`` shape, `protocol_mailbox.checkpoint_intent`)
bucketed by filename stamp, with their boundary kinds and Lessons answers;
learning-candidate events and ``Candidate:``/``Disposition:`` decision events
joined by candidate path for disposition latency.

Deliberately not measured, and said so in the output (`not_measurable`):
requirement retention over steps, recovery quality after context compaction,
and hook-approval intervention precision leave no durable artifact today.
Absence of a metric is reported, never silently approximated.

Interpretation discipline: these are slopes, not gates. A high first-pass GO
rate can mean healthy execution or a review that looks at nothing; a FAIL
closed with a changed head is the strongest available signal that the
intervention prevented a landed defect; a FAIL closed at the same head is
re-review that changed nothing. The numbers locate where to look — the
work-modes rule-maintenance clause (docs/protocol/work-modes.md) decides what
to do about it, through an evidence-backed learning-candidate.
"""

from __future__ import annotations

import argparse
import json
import re
import statistics
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:  # ADR-055 self-bootstrap (no PYTHONPATH)
    sys.path.insert(0, str(_REPO_ROOT))
_SCRIPTS = _REPO_ROOT / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

import claim_check  # noqa: E402
import protocol_mailbox  # noqa: E402
import git_runner  # noqa: E402
import protocol_mailbox  # noqa: E402

SENT_DIR = "coordination/mailbox/sent"
# Canonical grammar; the previous local copy dropped the Z from the stamp
# group and forbade digits in kinds.
_EVENT_NAME_RE = protocol_mailbox.EVENT_NAME_RE
_VERDICT_RE = re.compile(r"^VERDICT: (?P<verdict>GO|NITS|FAIL)\s*$", re.MULTILINE)
_REQUEST_REF_RE = re.compile(
    r"^Verification request: (?P<path>\S+\.md)@[0-9a-f]{40}\s*$", re.MULTILINE
)
_SUPERSEDES_RE = re.compile(
    r"^Supersedes: (?P<path>\S+\.md)@[0-9a-f]{40}\s*$", re.MULTILINE
)
_REMEDIATES_RE = re.compile(
    r"^Remediates failed report: (?P<path>\S+\.md)@[0-9a-f]{40}\s*$", re.MULTILINE
)
_REVIEWED_HEAD_RE = re.compile(
    r"^Reviewed head: (?P<sha>[0-9a-f]{40})\s*$", re.MULTILINE
)
_RISK_CLASS_RE = re.compile(r"^Risk class: (?P<risk>\S+)\s*$", re.MULTILINE)
# Anchored to decorator position so quoted fixture mentions do not match.
_PIN_GREP_PATTERN = r"^[[:space:]]*@pytest\.mark\.xfail\(strict=True"

SOURCES = {
    "verdicts": "light VERDICT field scan of committed verification reports",
    "first_pass": "earliest linked report per verify-request (filename timestamps)",
    "fail_chains": (
        "Supersedes:/same-request/Remediates-failed-report joins from FAIL to "
        "a GO/NITS follow-up; closure fields exist only in the current schema"
    ),
    "review_latency_seconds": "request filename timestamp to first report filename timestamp",
    "reviewed_heads": "Reviewed head: membership in git rev-list of the measured commit",
    "overclaim": "claim_check.sweep_range between consecutive first-parent window boundary commits",
    "pins_open": "git grep of anchored strict-xfail decorators under tests/ at the window boundary commit",
    "claims_ledger": "logs/claims/ledger.jsonl at the measured commit, bucketed by row `when`",
    "commits_first_parent": "git log --first-parent commit committer times",
    "continuity": (
        "findings events carrying the canonical Checkpoint:/Next action: "
        "shape (protocol_mailbox.checkpoint_intent) at the measured commit, "
        "bucketed by filename stamp"
    ),
    "learning": (
        "learning-candidate events plus Candidate:/Disposition: decision "
        "events at the measured commit, bucketed by filename stamp; "
        "disposition latency joins each disposition to its candidate's stamp"
    ),
}

NOT_MEASURABLE = {
    "requirement_retention_over_steps": (
        "no durable per-step requirement trace exists; finding-disposition "
        "completeness is enforced at publication for parse-valid reports, which "
        "is a floor, not a slope"
    ),
    "recovery_after_compaction": (
        "checkpoint records make boundary coverage measurable (continuity "
        "series); recovery quality stays unmeasured — no durable artifact "
        "ties a resumed session to the checkpoint it resumed from, and "
        "mandating a resume receipt would be ceremony (I7 guard admission)"
    ),
    "hook_intervention_precision": (
        "in-app hook approvals and denials are not durably logged; only review "
        "interventions (FAIL/NITS) are measurable"
    ),
}


@dataclass
class _RequestScan:
    path: str
    stamp: float
    reviewed_head: str | None
    risk_class: str | None
    remediates: str | None


@dataclass
class _ReportScan:
    path: str
    stamp: float
    verdict: str | None
    request_path: str | None
    reviewed_head: str | None
    supersedes: str | None


@dataclass
class _FailChain:
    report: _ReportScan
    closed_by: str | None = None
    closed_stamp: float | None = None
    closure_route: str | None = None
    head_changed: bool | None = None
    remediation_requests: list[str] = field(default_factory=list)


def _git(root: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", "-C", str(root), *args],
        capture_output=True,
        check=check,
        env=git_runner.dashboard_env(root),
    )


def _stamp_to_epoch(stamp: str) -> float:
    # The canonical stamp group includes the trailing Z.
    return (
        datetime.strptime(stamp, "%Y-%m-%dT%H-%M-%SZ")
        .replace(tzinfo=timezone.utc)
        .timestamp()
    )


def _sent_names(root: Path, commit: str) -> list[str]:
    completed = _git(
        root, "ls-tree", "-r", commit, "--name-only", SENT_DIR, check=False
    )
    if completed.returncode != 0:
        return []
    return [
        line
        for line in completed.stdout.decode("utf-8", "replace").splitlines()
        if line.endswith(".md")
    ]


def _batch_blobs(root: Path, commit: str, paths: list[str]) -> dict[str, bytes]:
    """Read many committed blobs through one `git cat-file --batch` stream."""
    if not paths:
        return {}
    requests = "".join(f"{commit}:{path}\n" for path in paths).encode("utf-8")
    completed = subprocess.run(
        ["git", "-C", str(root), "--no-replace-objects", "cat-file", "--batch"],
        input=requests,
        capture_output=True,
        check=True,
    )
    blobs: dict[str, bytes] = {}
    stream = completed.stdout
    offset = 0
    for path in paths:
        newline = stream.index(b"\n", offset)
        header = stream[offset:newline].split(b" ")
        offset = newline + 1
        if header[-1:] == [b"missing"]:
            continue
        size = int(header[2])
        blobs[path] = stream[offset : offset + size]
        offset += size + 1  # trailing newline after each object body
    return blobs


def _scan_events(
    root: Path, commit: str
) -> tuple[list[_RequestScan], list[_ReportScan], list[str]]:
    warnings: list[str] = []
    names = _sent_names(root, commit)
    wanted = [
        name
        for name in names
        if name.endswith("-verify-request.md")
        or name.endswith("-verification-report.md")
    ]
    blobs = _batch_blobs(root, commit, wanted)
    requests: list[_RequestScan] = []
    reports: list[_ReportScan] = []
    for path in wanted:
        match = _EVENT_NAME_RE.fullmatch(Path(path).name)
        if match is None:
            warnings.append(f"unparsable event filename skipped: {path}")
            continue
        raw = blobs.get(path)
        if raw is None:
            warnings.append(f"committed blob unavailable: {path}")
            continue
        text = raw.decode("utf-8", "replace")
        stamp = _stamp_to_epoch(match.group("stamp"))
        if path.endswith("-verify-request.md"):
            head = _REVIEWED_HEAD_RE.search(text)
            risk = _RISK_CLASS_RE.search(text)
            remediates = _REMEDIATES_RE.search(text)
            requests.append(
                _RequestScan(
                    path=path,
                    stamp=stamp,
                    reviewed_head=head.group("sha") if head else None,
                    risk_class=risk.group("risk") if risk else None,
                    remediates=remediates.group("path") if remediates else None,
                )
            )
        else:
            verdict = _VERDICT_RE.search(text)
            request_ref = _REQUEST_REF_RE.search(text)
            head = _REVIEWED_HEAD_RE.search(text)
            supersedes = _SUPERSEDES_RE.search(text)
            if verdict is None:
                warnings.append(f"report without parsable VERDICT: {path}")
            reports.append(
                _ReportScan(
                    path=path,
                    stamp=stamp,
                    verdict=verdict.group("verdict") if verdict else None,
                    request_path=(
                        request_ref.group("path") if request_ref else None
                    ),
                    reviewed_head=head.group("sha") if head else None,
                    supersedes=supersedes.group("path") if supersedes else None,
                )
            )
    return requests, reports, warnings


_DISPOSITION_VALUE_RE = re.compile(
    r"^Disposition: (?P<value>accepted|declined|expired)$", re.MULTILINE
)
_CANDIDATE_REF_RE = re.compile(
    r"^Candidate: (?P<path>coordination/mailbox/sent/"
    r"(?P<stamp>\d{4}-\d{2}-\d{2}T\d{2}-\d{2}-\d{2}Z)[^@\n]*"
    r"-learning-candidate\.md)@[0-9a-f]{40}$",
    re.MULTILINE,
)
_BOUNDARY_RE = re.compile(
    r"^Boundary: (?P<value>transfer|interruption|compaction|wrap)$",
    re.MULTILINE,
)
_LESSONS_RE = re.compile(r"^Lessons: (?P<value>.+)$", re.MULTILINE)


@dataclass
class _CheckpointScan:
    path: str
    stamp: float
    boundary: str | None
    lessons_refs: int
    none_considered: bool


@dataclass
class _LearningScan:
    candidate_stamps: list[tuple[str, float]]
    dispositions: list[tuple[float, str | None, float | None]]


def _scan_continuity(
    root: Path, commit: str
) -> tuple[list[_CheckpointScan], _LearningScan]:
    """Light field scan of committed continuity and learning events.

    Same discipline as _scan_events: filename stamps bucket, field regexes
    extract, a malformed body degrades to unparsed counters rather than a
    failure — this reporter is advisory (learning contract I1/I2) and must
    not become parse-strict where the writer already is.
    """

    names = _sent_names(root, commit)
    findings = [name for name in names if name.endswith("-findings.md")]
    decisions = [name for name in names if name.endswith("-decision.md")]
    candidates = [
        name for name in names if name.endswith("-learning-candidate.md")
    ]
    blobs = _batch_blobs(root, commit, findings + decisions)

    checkpoints: list[_CheckpointScan] = []
    for path in findings:
        match = _EVENT_NAME_RE.fullmatch(Path(path).name)
        raw = blobs.get(path)
        if match is None or raw is None:
            continue
        body = raw.decode("utf-8", "replace")
        if not protocol_mailbox.checkpoint_intent(body):
            continue
        boundary = _BOUNDARY_RE.search(body)
        lessons = _LESSONS_RE.search(body)
        lessons_value = lessons.group("value").strip() if lessons else ""
        none_considered = lessons_value == protocol_mailbox.CHECKPOINT_LESSONS_NONE
        checkpoints.append(
            _CheckpointScan(
                path=path,
                stamp=_stamp_to_epoch(match.group("stamp")),
                boundary=boundary.group("value") if boundary else None,
                lessons_refs=(
                    0
                    if none_considered or not lessons_value
                    else len(lessons_value.split(","))
                ),
                none_considered=none_considered,
            )
        )

    candidate_stamps: list[tuple[str, float]] = []
    stamp_by_candidate_path: dict[str, float] = {}
    for path in candidates:
        match = _EVENT_NAME_RE.fullmatch(Path(path).name)
        if match is None:
            continue
        epoch = _stamp_to_epoch(match.group("stamp"))
        candidate_stamps.append((path, epoch))
        stamp_by_candidate_path[path] = epoch

    dispositions: list[tuple[float, str | None, float | None]] = []
    for path in decisions:
        match = _EVENT_NAME_RE.fullmatch(Path(path).name)
        raw = blobs.get(path)
        if match is None or raw is None:
            continue
        body = raw.decode("utf-8", "replace")
        if not protocol_mailbox.learning_disposition_intent(body):
            continue
        stamp = _stamp_to_epoch(match.group("stamp"))
        value = _DISPOSITION_VALUE_RE.search(body)
        candidate = _CANDIDATE_REF_RE.search(body)
        latency: float | None = None
        if candidate is not None:
            candidate_epoch = stamp_by_candidate_path.get(
                candidate.group("path")
            )
            if candidate_epoch is None:
                candidate_epoch = _stamp_to_epoch(candidate.group("stamp"))
            latency = max(0.0, stamp - candidate_epoch)
        dispositions.append(
            (stamp, value.group("value") if value else None, latency)
        )

    return checkpoints, _LearningScan(
        candidate_stamps=candidate_stamps, dispositions=dispositions
    )


def _fail_chains(
    requests: list[_RequestScan], reports: list[_ReportScan]
) -> list[_FailChain]:
    """Join each FAIL report to its recorded closure, if any.

    Closure routes, in precedence order: an explicit `Supersedes:` GO/NITS
    report; a later GO/NITS report bound to the same request path (the
    dominant historical shape — the Supersedes/Remediates fields are recent
    schema); a remediation request naming the FAIL whose own first report is
    GO/NITS. `open` therefore means "no closure recorded in scanned fields",
    not "defect necessarily still live": pre-schema chains that continued
    under a fresh request path leave no machine-joinable trace.
    """
    reports_by_request: dict[str, list[_ReportScan]] = {}
    for report in sorted(reports, key=lambda r: (r.stamp, r.path)):
        if report.request_path is not None:
            reports_by_request.setdefault(report.request_path, []).append(report)
    chains = [
        _FailChain(report=report)
        for report in reports
        if report.verdict == "FAIL"
    ]
    by_failed_path = {chain.report.path: chain for chain in chains}
    for report in sorted(reports, key=lambda r: (r.stamp, r.path)):
        if report.supersedes is None or report.verdict not in {"GO", "NITS"}:
            continue
        chain = by_failed_path.get(report.supersedes)
        if chain is not None and chain.closed_by is None:
            chain.closed_by = report.path
            chain.closed_stamp = report.stamp
            chain.closure_route = "supersedes"
            chain.head_changed = (
                report.reviewed_head != chain.report.reviewed_head
                if report.reviewed_head and chain.report.reviewed_head
                else None
            )
    for chain in chains:
        if chain.closed_by is not None or chain.report.request_path is None:
            continue
        for report in reports_by_request.get(chain.report.request_path, []):
            if (
                report.stamp <= chain.report.stamp
                or report.path == chain.report.path
            ):
                continue
            if report.verdict in {"GO", "NITS"}:
                chain.closed_by = report.path
                chain.closed_stamp = report.stamp
                chain.closure_route = "same_request"
                chain.head_changed = (
                    report.reviewed_head != chain.report.reviewed_head
                    if report.reviewed_head and chain.report.reviewed_head
                    else None
                )
                break
    for request in sorted(requests, key=lambda r: (r.stamp, r.path)):
        if request.remediates is None:
            continue
        chain = by_failed_path.get(request.remediates)
        if chain is None:
            continue
        chain.remediation_requests.append(request.path)
        if chain.closed_by is not None:
            continue
        for report in reports_by_request.get(request.path, []):
            if report.verdict in {"GO", "NITS"}:
                chain.closed_by = report.path
                chain.closed_stamp = report.stamp
                chain.closure_route = "remediation_request"
                chain.head_changed = (
                    report.reviewed_head != chain.report.reviewed_head
                    if report.reviewed_head and chain.report.reviewed_head
                    else None
                )
                break
    return chains


def _first_parent_history(root: Path, commit: str) -> list[tuple[str, float]]:
    out = _git(root, "log", "--first-parent", "--format=%H %ct", commit)
    history = []
    for line in out.stdout.decode("ascii", "replace").splitlines():
        sha, _, epoch = line.partition(" ")
        history.append((sha, float(epoch)))
    return history  # newest first


def _reachable_commits(root: Path, commit: str) -> frozenset[str]:
    out = _git(root, "rev-list", commit)
    return frozenset(out.stdout.decode("ascii", "replace").split())


def _boundary_commit(
    history: list[tuple[str, float]], end_epoch: float
) -> str | None:
    """Newest first-parent commit whose committer time is <= the window end."""
    for sha, epoch in history:
        if epoch <= end_epoch:
            return sha
    return None


def _pins_open(root: Path, boundary: str) -> int | None:
    completed = _git(
        root, "grep", "-c", "-E", _PIN_GREP_PATTERN, boundary, "--", "tests",
        check=False,
    )
    if completed.returncode == 1 and not completed.stdout:
        return 0
    if completed.returncode != 0:
        return None
    total = 0
    for line in completed.stdout.decode("utf-8", "replace").splitlines():
        total += int(line.rsplit(":", 1)[-1])
    return total


def _ledger_rows(root: Path, commit: str) -> list[dict] | None:
    completed = _git(
        root, "show", f"{commit}:logs/claims/ledger.jsonl", check=False
    )
    if completed.returncode != 0:
        return None
    rows = []
    for line in completed.stdout.decode("utf-8", "replace").splitlines():
        if not line.strip():
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            rows.append({"_unparsable": True})
    return rows


def _row_epoch(row: dict) -> float | None:
    when = row.get("when")
    if not isinstance(when, str):
        return None
    try:
        parsed = datetime.fromisoformat(when.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.timestamp()


def _median(values: list[float]) -> float | None:
    return statistics.median(values) if values else None


def collect_slope(
    root: Path,
    *,
    commit: str = "HEAD",
    windows: int = 6,
    window_days: int = 14,
) -> dict:
    resolved = _git(root, "rev-parse", commit).stdout.decode("ascii").strip()
    measured_epoch = float(
        _git(root, "show", "-s", "--format=%ct", resolved).stdout.decode().strip()
    )
    history = _first_parent_history(root, resolved)
    reachable = _reachable_commits(root, resolved)
    requests, reports, warnings = _scan_events(root, resolved)
    chains = _fail_chains(requests, reports)
    chains_by_window_stamp = [(c.report.stamp, c) for c in chains]
    ledger = _ledger_rows(root, resolved)
    checkpoints, learning = _scan_continuity(root, resolved)

    reports_by_request: dict[str, list[_ReportScan]] = {}
    for report in sorted(reports, key=lambda r: (r.stamp, r.path)):
        if report.request_path is not None:
            reports_by_request.setdefault(report.request_path, []).append(report)

    starts = [
        measured_epoch - timedelta(days=window_days * (i + 1)).total_seconds()
        for i in reversed(range(windows))
    ]
    series = []
    earliest_start = starts[0]
    prev_boundary = _boundary_commit(history, earliest_start)
    for start in starts:
        end = start + timedelta(days=window_days).total_seconds()
        boundary = _boundary_commit(history, end)
        window_requests = [r for r in requests if start <= r.stamp < end]
        window_reports = [r for r in reports if start <= r.stamp < end]
        verdicts = {"GO": 0, "NITS": 0, "FAIL": 0, "unparsed": 0}
        for report in window_reports:
            verdicts[report.verdict or "unparsed"] += 1

        first_pass_total = 0
        first_pass_go = 0
        latencies = []
        heads = {"landed": 0, "unlanded": 0, "unresolvable": 0}
        for request in window_requests:
            linked = reports_by_request.get(request.path, [])
            if linked:
                first_pass_total += 1
                if linked[0].verdict == "GO":
                    first_pass_go += 1
                latencies.append(max(0.0, linked[0].stamp - request.stamp))
            if request.reviewed_head is None:
                heads["unresolvable"] += 1
            elif request.reviewed_head in reachable:
                heads["landed"] += 1
            else:
                heads["unlanded"] += 1

        window_chains = [
            chain for stamp, chain in chains_by_window_stamp if start <= stamp < end
        ]
        closures = [
            chain.closed_stamp - chain.report.stamp
            for chain in window_chains
            if chain.closed_stamp is not None
        ]
        fail_chains = {
            "fails": len(window_chains),
            "closed_head_changed": sum(
                1 for c in window_chains if c.closed_by and c.head_changed
            ),
            "closed_same_head": sum(
                1
                for c in window_chains
                if c.closed_by and c.head_changed is False
            ),
            "closed_head_unknown": sum(
                1
                for c in window_chains
                if c.closed_by and c.head_changed is None
            ),
            "no_recorded_closure": sum(
                1 for c in window_chains if c.closed_by is None
            ),
            "remediation_requests": sum(
                len(c.remediation_requests) for c in window_chains
            ),
            "median_closure_seconds": _median(closures),
        }

        if boundary is None:
            overclaim: dict | str = "unavailable: window precedes first commit"
        elif prev_boundary is None or prev_boundary == boundary:
            overclaim = {"flags": 0, "examples": [], "range": None}
        else:
            flags = claim_check.sweep_range(root, prev_boundary, boundary)
            overclaim = {
                "flags": len(flags),
                "examples": flags[:3],
                "range": f"{prev_boundary[:12]}..{boundary[:12]}",
            }

        pins = _pins_open(root, boundary) if boundary is not None else None
        commits_in_window = sum(
            1 for _, epoch in history if start < epoch <= end
        )

        claims: dict | None = None
        if ledger is not None:
            window_rows = [
                row
                for row in ledger
                if (epoch := _row_epoch(row)) is not None and start <= epoch < end
            ]
            premise_statuses: dict[str, int] = {}
            for row in window_rows:
                for premise in row.get("premises", []):
                    status = premise.get("status", "unlabelled")
                    premise_statuses[status] = premise_statuses.get(status, 0) + 1
            claims = {"rows": len(window_rows), "premises": premise_statuses}

        window_checkpoints = [
            c for c in checkpoints if start <= c.stamp < end
        ]
        boundary_counts: dict[str, int] = {}
        for item in window_checkpoints:
            key = item.boundary or "unparsed"
            boundary_counts[key] = boundary_counts.get(key, 0) + 1
        window_candidates = sum(
            1 for _path, epoch in learning.candidate_stamps if start <= epoch < end
        )
        window_dispositions = [
            (value, latency)
            for stamp, value, latency in learning.dispositions
            if start <= stamp < end
        ]
        disposition_counts = {"accepted": 0, "declined": 0, "expired": 0, "unparsed": 0}
        for value, _latency in window_dispositions:
            disposition_counts[value or "unparsed"] += 1

        series.append(
            {
                "window_start": datetime.fromtimestamp(
                    start, tz=timezone.utc
                ).isoformat(),
                "window_end": datetime.fromtimestamp(
                    end, tz=timezone.utc
                ).isoformat(),
                "boundary_commit": boundary,
                "commits_first_parent": commits_in_window,
                "requests": len(window_requests),
                "reports": len(window_reports),
                "verdicts": verdicts,
                "first_pass": {"go": first_pass_go, "total": first_pass_total},
                "review_latency_median_seconds": _median(latencies),
                "fail_chains": fail_chains,
                "reviewed_heads": heads,
                "overclaim": overclaim,
                "pins_open": pins if pins is not None else "unavailable",
                "claims_ledger": claims,
                "continuity": {
                    "checkpoints": len(window_checkpoints),
                    "boundaries": boundary_counts,
                    "lessons_refs": sum(
                        c.lessons_refs for c in window_checkpoints
                    ),
                    "none_considered": sum(
                        1 for c in window_checkpoints if c.none_considered
                    ),
                },
                "learning": {
                    "candidates": window_candidates,
                    "dispositions": disposition_counts,
                    "median_disposition_latency_seconds": _median(
                        [
                            latency
                            for _value, latency in window_dispositions
                            if latency is not None
                        ]
                    ),
                },
            }
        )
        prev_boundary = boundary

    earlier_requests = sum(1 for r in requests if r.stamp < earliest_start)
    earlier_reports = sum(1 for r in reports if r.stamp < earliest_start)

    all_verdicts = {"GO": 0, "NITS": 0, "FAIL": 0, "unparsed": 0}
    for report in reports:
        all_verdicts[report.verdict or "unparsed"] += 1
    unlinked_reports = sum(1 for r in reports if r.request_path is None)
    totals = {
        "requests": len(requests),
        "reports": len(reports),
        "verdicts": all_verdicts,
        "reports_without_request_ref": unlinked_reports,
        "fail_chains": {
            "fails": len(chains),
            "closed_head_changed": sum(
                1 for c in chains if c.closed_by and c.head_changed
            ),
            "closed_same_head": sum(
                1 for c in chains if c.closed_by and c.head_changed is False
            ),
            "closed_head_unknown": sum(
                1 for c in chains if c.closed_by and c.head_changed is None
            ),
            "no_recorded_closure": sum(
                1 for c in chains if c.closed_by is None
            ),
            "closure_routes": {
                route: sum(1 for c in chains if c.closure_route == route)
                for route in ("supersedes", "same_request", "remediation_request")
            },
        },
        "events_before_first_window": {
            "requests": earlier_requests,
            "reports": earlier_reports,
        },
        "continuity": {
            "checkpoints": len(checkpoints),
            "none_considered": sum(1 for c in checkpoints if c.none_considered),
            "lessons_refs": sum(c.lessons_refs for c in checkpoints),
        },
        "learning": {
            "candidates": len(learning.candidate_stamps),
            "dispositions": len(learning.dispositions),
        },
    }

    return {
        "commit": resolved,
        "measured_at": datetime.fromtimestamp(
            measured_epoch, tz=timezone.utc
        ).isoformat(),
        "window_days": window_days,
        "windows": windows,
        "sources": SOURCES,
        "not_measurable": NOT_MEASURABLE,
        "totals": totals,
        "series": series,
        "warnings": warnings,
    }


def _render_text(slope: dict) -> str:
    lines = [
        f"quality slope at {slope['commit'][:12]} "
        f"({slope['windows']} windows x {slope['window_days']}d, "
        f"measured {slope['measured_at']})"
    ]
    totals = slope["totals"]
    lines.append(
        f"  totals: {totals['requests']} requests, {totals['reports']} reports, "
        f"verdicts {totals['verdicts']}  [{SOURCES['verdicts']}]"
    )
    chain_totals = totals["fail_chains"]
    lines.append(
        f"  fail chains: {chain_totals['fails']} fails — "
        f"{chain_totals['closed_head_changed']} closed with changed head, "
        f"{chain_totals['closed_same_head']} closed same head, "
        f"{chain_totals['closed_head_unknown']} closed head-unknown, "
        f"{chain_totals['no_recorded_closure']} without recorded closure"
        f"  [{SOURCES['fail_chains']}]"
    )
    for window in slope["series"]:
        first_pass = window["first_pass"]
        rate = (
            f"{first_pass['go']}/{first_pass['total']}"
            if first_pass["total"]
            else "n/a"
        )
        overclaim = window["overclaim"]
        overclaim_text = (
            overclaim
            if isinstance(overclaim, str)
            else f"{overclaim['flags']} flags"
        )
        latency = window["review_latency_median_seconds"]
        latency_text = f"{latency:.0f}s" if latency is not None else "n/a"
        lines.append(
            f"  {window['window_start'][:10]}..{window['window_end'][:10]}: "
            f"req {window['requests']}, rep {window['reports']}, "
            f"first-pass GO {rate}, latency {latency_text}, "
            f"fails {window['fail_chains']['fails']} "
            f"(no-closure {window['fail_chains']['no_recorded_closure']}), "
            f"heads landed {window['reviewed_heads']['landed']}"
            f"/unlanded {window['reviewed_heads']['unlanded']}"
            f"/unresolvable {window['reviewed_heads']['unresolvable']}, "
            f"overclaim {overclaim_text}, pins {window['pins_open']}, "
            f"commits {window['commits_first_parent']}, "
            f"checkpoints {window['continuity']['checkpoints']}, "
            f"candidates {window['learning']['candidates']}"
        )
    for name, reason in slope["not_measurable"].items():
        lines.append(f"  not measurable: {name} — {reason}")
    for warning in slope["warnings"]:
        lines.append(f"  WARN {warning}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--repo-root", type=Path, default=_REPO_ROOT)
    parser.add_argument("--commit", default="HEAD")
    parser.add_argument("--windows", type=int, default=6)
    parser.add_argument("--window-days", type=int, default=14)
    parser.add_argument("--json", action="store_true")
    arguments = parser.parse_args(argv)
    slope = collect_slope(
        arguments.repo_root,
        commit=arguments.commit,
        windows=max(1, arguments.windows),
        window_days=max(1, arguments.window_days),
    )
    if arguments.json:
        print(json.dumps(slope, indent=2))
    else:
        print(_render_text(slope))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
