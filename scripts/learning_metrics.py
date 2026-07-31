#!/usr/bin/env python3
"""Read-only learning-plane metrics reporter (Stage 5, ADR-067).

Reports the measurable learning-lifecycle metrics, each line naming its
measurement source. Read-only by construction: this tool writes nothing —
`logs/learning/outcomes.jsonl` is appended by seats recording real outcomes,
never by this reporter. The promotion-linkage check is ADVISORY (WARN lines,
exit stays 0): a blocking gate on a shape-only ref would fail guard admission
(contract I5), and the governance floor is carried by operator judgment.

Metrics and sources:
1. review_friction        — verification-reports per verify-request, mailbox
                            filename scan at HEAD (baseline 162/186 at 29db6aa).
2. candidates_total       — committed learning-candidate events at HEAD.
3. acceptance             — disposed candidates split by each candidate's
                            LATEST disposition (a re-disposed candidate
                            counts once; the three counters partition the
                            disposed set, never exceed candidates_total).
4. supersession_rate      — candidates carrying Supersedes / candidates_total.
5. promotion_linkage      — live accepted candidates whose ref appears as a
                            Finding Refs ENTRY of no verify-request at HEAD
                            (ADVISORY WARN); prose mentions are not linkage.
                            A candidate whose ACCEPTED replacement exists is
                            RETIRED (ADR-066 re-issue idiom) and owes
                            nothing; a proposed or declined supersession
                            retires nothing.
6. staleness/promotion    — a live accepted candidate whose target moved is
                            reported under promoted_target_moved when
                            Finding-Refs-linked (the move its acceptance
                            authorized; a partial view — promoted candidates
                            whose target has not yet moved do not appear)
                            and is STALE (WARN) only when unlinked — the
                            target changed underneath it outside the
                            governed path.
7. contradictions         — live (non-superseded) candidates sharing a Target
                            with different Proposed content hash.
8. index_coverage         — rows and built-at commit of the local Stage 1
                            index vs HEAD (workspace projection; unavailable
                            is reported, never treated as zero).
Context lines: claims-ledger rows (logs/claims/ledger.jsonl), rules-registry
rows and HARD/SOFT split (docs/PROTOCOL-RULES-LOG.md), recorded outcomes
(logs/learning/outcomes.jsonl). Retrieval precision is measured by the frozen
packs under tests/learning_packs/ (tests/unit/test_learning_packs.py), not
recomputed here.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:  # ADR-055 self-bootstrap (no PYTHONPATH)
    sys.path.insert(0, str(_REPO_ROOT))
_SCRIPTS = _REPO_ROOT / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

import learning_index  # noqa: E402
import protocol_mailbox  # noqa: E402


def _git(root: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(root), *args],
        capture_output=True,
        check=True,
    ).stdout.decode("utf-8", "replace")


def _sent_names(root: Path, commit: str) -> list[str]:
    out = _git(
        root, "ls-tree", "-r", commit, "--name-only", "coordination/mailbox/sent"
    )
    return [line for line in out.splitlines() if line.endswith(".md")]


def _candidate_statements(
    root: Path, commit: str
) -> list[protocol_mailbox.LearningCandidateStatement]:
    resolved = _git(root, "rev-parse", commit).strip()
    statements = []
    for path in _sent_names(root, resolved):
        if not path.endswith("-learning-candidate.md"):
            continue
        try:
            statements.append(
                protocol_mailbox.load_learning_candidate_statement(
                    root, f"{path}@{resolved}"
                )
            )
        except ValueError:
            continue
    return statements


def _dispositions(
    root: Path, commit: str
) -> list[protocol_mailbox.LearningDispositionStatement]:
    resolved = _git(root, "rev-parse", commit).strip()
    dispositions = []
    for path in _sent_names(root, resolved):
        if not path.endswith("-decision.md"):
            continue
        try:
            event = protocol_mailbox.load_committed_event_ref(
                root, f"{path}@{resolved}"
            )
        except ValueError:
            continue
        if not any(
            line.startswith("Candidate:") for line in event.text.splitlines()
        ):
            continue
        try:
            dispositions.append(
                protocol_mailbox.parse_learning_disposition_statement(event)
            )
        except ValueError:
            continue
    return dispositions


def collect_metrics(root: Path, *, commit: str = "HEAD") -> dict:
    resolved = _git(root, "rev-parse", commit).strip()
    names = [Path(p).name for p in _sent_names(root, resolved)]
    requests = sum(1 for n in names if n.endswith("-verify-request.md"))
    reports = sum(1 for n in names if n.endswith("-verification-report.md"))

    candidates = _candidate_statements(root, resolved)
    dispositions = _dispositions(root, resolved)
    by_ref = {d.candidate_ref.rsplit("@", 1)[0]: d for d in dispositions}
    accepted = [
        c for c in candidates
        if by_ref.get(c.event.path) is not None
        and by_ref[c.event.path].disposition == "accepted"
    ]
    # Retirement keys on the superseding candidate's OWN acceptance — a
    # merely proposed (undisposed) or declined supersession replaces nothing,
    # so the original keeps its linkage debt and its target alarm (review
    # finding: proposal-keyed retirement let any seat unilaterally silence an
    # accepted candidate by composing an undisposed superseder).
    superseded_paths = {
        c.supersedes.rsplit("@", 1)[0]
        for c in candidates
        if c.supersedes
        and by_ref.get(c.event.path) is not None
        and by_ref[c.event.path].disposition == "accepted"
    }
    live = [c for c in candidates if c.event.path not in superseded_paths]

    request_texts = []
    for path in _sent_names(root, resolved):
        if path.endswith("-verify-request.md"):
            request_texts.append(_git(root, "show", f"{resolved}:{path}"))

    # Lifecycle classification of accepted candidates. A candidate whose
    # accepted replacement exists is RETIRED (ADR-066 re-issue idiom): it
    # neither owes a promotion nor alarms about its target. A live accepted
    # candidate whose ref appears as a Finding Refs ENTRY of a verify-request
    # — the contract I3 promotion linkage, `- <path>@<sha>` — and whose
    # target moved is PROMOTED: the move the acceptance authorized. A prose
    # mention anywhere in a request body (a citation, an orphaning note, a
    # decline) is NOT linkage (review finding: the substring predicate let a
    # non-promoting mention silence the stale alarm). The stale WARN keeps
    # the genuinely alarming case: accepted, unpromoted, target moved
    # underneath it outside the governed path.
    retired = [c for c in accepted if c.event.path in superseded_paths]
    live_accepted = [c for c in accepted if c.event.path not in superseded_paths]
    finding_ref_paths: set[str] = set()
    for text in request_texts:
        finding_ref_paths.update(
            re.findall(
                r"^- (coordination/mailbox/sent/\S+\.md)@[0-9a-f]{40}\s*$",
                text,
                re.MULTILINE,
            )
        )
    linked_paths = {
        c.event.path for c in live_accepted if c.event.path in finding_ref_paths
    }
    linkage_gaps = [
        c.event.path for c in live_accepted if c.event.path not in linked_paths
    ]

    promoted = []
    stale = []
    for c in live_accepted:
        if c.target is None:
            continue
        try:
            data = subprocess.run(
                ["git", "-C", str(root), "cat-file", "blob",
                 f"{resolved}:{c.target}"],
                capture_output=True,
                check=True,
            ).stdout
        except subprocess.CalledProcessError:
            data = None
        moved = (
            data is None
            or "sha256:" + hashlib.sha256(data).hexdigest() != c.target_base_hash
        )
        if not moved:
            continue
        detail = "target absent" if data is None else "target moved"
        if c.event.path in linked_paths:
            promoted.append(f"{c.event.path} ({detail}: {c.target})")
        else:
            stale.append(f"{c.event.path} ({detail}: {c.target})")

    by_target: dict[str, list[protocol_mailbox.LearningCandidateStatement]] = {}
    for c in live:
        if c.target is not None:
            by_target.setdefault(c.target, []).append(c)
    contradictions = [
        target
        for target, group in sorted(by_target.items())
        if len({c.proposed_content_hash for c in group}) > 1
    ]

    index_commit = learning_index.built_at_commit(root)
    if index_commit is None:
        index_state = "(unavailable: index not built)"
    else:
        freshness = "current" if index_commit == resolved else "behind HEAD"
        index_state = f"built at {index_commit[:12]} ({freshness})"

    ledger = root / "logs" / "claims" / "ledger.jsonl"
    ledger_rows = (
        len(ledger.read_text(encoding="utf-8").splitlines())
        if ledger.exists()
        else None
    )
    rules_log = root / "docs" / "PROTOCOL-RULES-LOG.md"
    rules_rows = hard = 0
    if rules_log.exists():
        table_rows = re.findall(
            r"^\| \d+ \|.*$", rules_log.read_text(encoding="utf-8"), re.MULTILINE
        )
        rules_rows = len(table_rows)
        hard = sum(1 for row in table_rows if "HARD" in row)
    outcomes = root / "logs" / "learning" / "outcomes.jsonl"
    outcome_rows = (
        len(outcomes.read_text(encoding="utf-8").splitlines())
        if outcomes.exists()
        else None
    )

    return {
        "commit": resolved,
        "review_friction": f"{reports}/{requests}",
        "candidates_total": len(candidates),
        "accepted": len(accepted),
        "declined": sum(
            1 for d in by_ref.values() if d.disposition == "declined"
        ),
        "expired": sum(
            1 for d in by_ref.values() if d.disposition == "expired"
        ),
        "supersession_rate": (
            f"{sum(1 for c in candidates if c.supersedes)}/{len(candidates)}"
        ),
        "promotion_linkage_gaps": linkage_gaps,
        "promoted_target_moved": promoted,
        "retired_superseded": [c.event.path for c in retired],
        "stale_accepted": stale,
        "contradicted_targets": contradictions,
        "index_state": index_state,
        "claims_ledger_rows": ledger_rows,
        "rules_registry": f"{rules_rows} rows ({hard} HARD-marked)",
        "outcome_rows": outcome_rows,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--repo-root", type=Path, default=_REPO_ROOT)
    parser.add_argument("--commit", default="HEAD")
    parser.add_argument("--json", action="store_true")
    arguments = parser.parse_args(argv)
    metrics = collect_metrics(arguments.repo_root, commit=arguments.commit)
    if arguments.json:
        print(json.dumps(metrics, indent=2))
        return 0
    print(f"learning metrics at {metrics['commit'][:12]}")
    print(f"  review friction (reports/requests): {metrics['review_friction']}"
          f"  [mailbox filename scan]")
    print(f"  candidates: {metrics['candidates_total']}"
          f" (accepted {metrics['accepted']}, declined {metrics['declined']},"
          f" expired {metrics['expired']})  [committed events]")
    print(f"  supersession: {metrics['supersession_rate']}  [Supersedes fields]")
    print(f"  index: {metrics['index_state']}  [coordination/learning/]")
    print(f"  claims ledger rows: {metrics['claims_ledger_rows']}"
          f"  [logs/claims/ledger.jsonl]")
    print(f"  rules registry: {metrics['rules_registry']}"
          f"  [docs/PROTOCOL-RULES-LOG.md]")
    print(f"  recorded outcomes: {metrics['outcome_rows']}"
          f"  [logs/learning/outcomes.jsonl]")
    for item in metrics["promoted_target_moved"]:
        print(f"  promoted (target moved as authorized): {item}")
    for path in metrics["retired_superseded"]:
        print(f"  retired (accepted replacement exists): {path}")
    for gap in metrics["promotion_linkage_gaps"]:
        print(f"  WARN accepted candidate not named by any verify-request: {gap}")
    for item in metrics["stale_accepted"]:
        print(f"  WARN stale accepted candidate: {item}")
    for target in metrics["contradicted_targets"]:
        print(f"  WARN contradicted target: {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
