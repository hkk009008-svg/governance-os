#!/usr/bin/env python3
"""Supervised extraction: draft ONE learning candidate from named evidence.

Stage 4 of the learning plane (ADR-067, `docs/protocol/learning/contract.md`).
Capability boundary, executable and deliberately narrow (O4 ruling: drafts
only): this tool writes exactly one draft candidate body into the scratch
directory it is given and prints it. It never publishes (no mailbox-finalize
path), never mutates git state, never touches a skill tree. The author reads
the draft and runs `coordination/bin/send-event` themselves.

Triggers are evidence, not counters or a session-update quota (the rejected
Hermes sediment machine): every draft names at least one immutable evidence
ref, and the `recurrence` trigger additionally demands the Stage 1 index
return the pattern from at least two distinct committed sources — an
unavailable index is not evidence. A MEASURED statement whose shape is
claim-bearing (claim_check's grammar) must carry an instrument mark somewhere
in the record (laundering defense, contract §4) — honestly scoped:
INSTRUMENT_MARK is a coarse vocabulary heuristic that refuses the absent
citation, not a validity check on the citation offered; any backticked
token satisfies it, and the disposition review is what judges citation
quality.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:  # ADR-055 self-bootstrap (no PYTHONPATH)
    sys.path.insert(0, str(_REPO_ROOT))
_SCRIPTS = _REPO_ROOT / "pipeline"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

import claim_check  # noqa: E402
import learning_index  # noqa: E402
import protocol_mailbox  # noqa: E402


TRIGGERS = (
    "user-correction",
    "handoff-workflow",
    "skill-contradicted",
    "measured-improvement",
    "recurrence",
)

EXIT_DRAFTED = 0
EXIT_NO_TRIGGER = 3


class ExtractionRefused(Exception):
    """The evidence offered does not clear the trigger bar; no draft."""


def _require_evidence_refs(values: list[str]) -> tuple[str, ...]:
    refs = tuple(values)
    if not refs:
        raise ExtractionRefused("a trigger needs at least one evidence ref")
    for value in refs:
        if not protocol_mailbox.immutable_reference_is_canonical(value):
            raise ExtractionRefused(
                f"evidence ref is not an immutable canonical ref: {value!r}"
            )
    if len(refs) != len(set(refs)):
        raise ExtractionRefused("evidence refs must be unique")
    return refs


def _require_recurrence(root: Path, terms: str) -> tuple[str, ...]:
    rows = learning_index.query_index(root, terms, limit=50)
    if rows is None:
        raise ExtractionRefused(
            "recurrence needs the Stage 1 index and it is unavailable — "
            "an absent index is not evidence; run learning_index.py build"
        )
    sources = sorted({row.path for row in rows})
    if len(sources) < 2:
        raise ExtractionRefused(
            f"recurrence needs the pattern in >=2 distinct committed sources; "
            f"index returned {len(sources)}"
        )
    return tuple(sources)


def _require_instrument_mark(fields: dict[str, str | None]) -> None:
    statement = fields["Statement"] or ""
    shapes = claim_check.classify(statement)
    if not shapes:
        return
    record_text = " ".join(
        value for value in (
            statement, fields.get("Applicability"), fields.get("Exclusions")
        ) if value
    )
    if fields["Evidence provenance"] == "MEASURED" and not claim_check.INSTRUMENT_MARK.search(
        record_text
    ):
        raise ExtractionRefused(
            "a MEASURED claim-shaped statement needs an instrument mark "
            f"(shapes: {', '.join(shapes)}); prose is not a citation"
        )


def draft_candidate(
    *,
    root: Path,
    scratch: Path,
    trigger: str,
    evidence_refs: list[str],
    statement: str,
    category: str,
    scope: str,
    provenance: str,
    applicability: str,
    exclusions: str,
    risk_class: str,
    producer_seat: str,
    producer_model: str,
    recurrence_terms: str | None = None,
    target: str | None = None,
    target_base_hash: str | None = None,
    proposed_content_hash: str | None = None,
    supersedes: str | None = None,
) -> tuple[Path, str, tuple[str, ...]]:
    """Validate the trigger evidence and write ONE draft body to scratch."""

    if trigger not in TRIGGERS:
        raise ExtractionRefused(f"unknown trigger {trigger!r}")
    refs = _require_evidence_refs(evidence_refs)
    recurrence_sources: tuple[str, ...] = ()
    if trigger == "recurrence":
        if not recurrence_terms:
            raise ExtractionRefused("recurrence needs --recurrence-terms")
        recurrence_sources = _require_recurrence(root, recurrence_terms)
    fields: dict[str, str | None] = {
        "Category": category,
        "Scope": scope,
        "Statement": statement,
        "Proposed content hash": proposed_content_hash,
        "Target": target,
        "Target base hash": target_base_hash,
        "Source refs": ", ".join(refs),
        "Evidence provenance": provenance,
        "Applicability": applicability,
        "Exclusions": exclusions,
        "Risk class": risk_class,
        "Supersedes": supersedes,
        "Producer seat": producer_seat,
        "Producer model": producer_model,
    }
    _require_instrument_mark(fields)
    candidate_id = protocol_mailbox.compute_learning_candidate_id(fields)
    lines = [f"Candidate ID: {candidate_id}"]
    lines.extend(
        f"{label}: {value}" for label, value in fields.items() if value is not None
    )
    body = "\n".join(lines) + "\n"
    scratch.mkdir(parents=True, exist_ok=True)
    draft_path = scratch / f"learning-candidate-{candidate_id[:12]}.md"
    draft_path.write_text(body, encoding="utf-8")
    return draft_path, body, recurrence_sources


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--repo-root", type=Path, default=_REPO_ROOT)
    parser.add_argument("--scratch", type=Path, required=True,
                        help="directory the ONE draft file is written into")
    parser.add_argument("--trigger", choices=TRIGGERS, required=True)
    parser.add_argument("--evidence-ref", action="append", default=[],
                        help="immutable sent-path@sha or sha256: ref (repeatable)")
    parser.add_argument("--recurrence-terms", default=None)
    parser.add_argument("--statement", required=True)
    parser.add_argument("--category", required=True,
                        choices=protocol_mailbox.LEARNING_CATEGORIES)
    parser.add_argument("--scope", default="repository")
    parser.add_argument("--provenance", required=True, choices=claim_check.PROVENANCE)
    parser.add_argument("--applicability", required=True)
    parser.add_argument("--exclusions", required=True)
    parser.add_argument("--risk-class", required=True)
    parser.add_argument("--producer-seat", required=True)
    parser.add_argument("--producer-model", required=True)
    parser.add_argument("--target", default=None)
    parser.add_argument("--target-base-hash", default=None)
    parser.add_argument("--proposed-content-hash", default=None)
    parser.add_argument("--supersedes", default=None)
    arguments = parser.parse_args(argv)

    try:
        draft_path, body, recurrence_sources = draft_candidate(
            root=arguments.repo_root,
            scratch=arguments.scratch,
            trigger=arguments.trigger,
            evidence_refs=arguments.evidence_ref,
            statement=arguments.statement,
            category=arguments.category,
            scope=arguments.scope,
            provenance=arguments.provenance,
            applicability=arguments.applicability,
            exclusions=arguments.exclusions,
            risk_class=arguments.risk_class,
            producer_seat=arguments.producer_seat,
            producer_model=arguments.producer_model,
            recurrence_terms=arguments.recurrence_terms,
            target=arguments.target,
            target_base_hash=arguments.target_base_hash,
            proposed_content_hash=arguments.proposed_content_hash,
            supersedes=arguments.supersedes,
        )
    except ExtractionRefused as refusal:
        print(f"no candidate: {refusal}", file=sys.stderr)
        return EXIT_NO_TRIGGER

    print(f"draft written: {draft_path}")
    if recurrence_sources:
        print("recurrence sources:")
        for source in recurrence_sources:
            print(f"  - {source}")
    print("--- body ---")
    print(body, end="")
    print("--- this tool never publishes; review the draft, then run "
          "coordination/bin/send-event yourself ---")
    return EXIT_DRAFTED


if __name__ == "__main__":
    raise SystemExit(main())
