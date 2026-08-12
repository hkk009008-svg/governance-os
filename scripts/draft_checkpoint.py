#!/usr/bin/env python3
"""Draft ONE durable continuation checkpoint into scratch.

The checkpoint record carries the AGENTS.md universal-contract item 7
payload — objective, accepted scope, owner, policy revision, base/head,
evidence refs, verification status, unresolved blockers, and the next
executable action — as one ``findings`` event body typed at read time by
``protocol_mailbox.parse_checkpoint_statement``. Write one at a real
long-horizon boundary: ownership transfer, interruption, pre-compaction,
or campaign wrap. Ordinary reversible local work needs no checkpoint.

Capability boundary, mirroring ``learning_extract.py`` (drafts only): this
tool writes exactly one draft body into the scratch directory it is given
and prints it. It never publishes (no mailbox-finalize path) and never
mutates git state. The author reads the draft and runs
``coordination/bin/send-event`` themselves, with whatever publication
authority that requires.

The required ``Lessons:`` field is the boundary's anti-forgetting prompt,
not a quota: name the learning-candidate refs this stretch produced, or
state ``none-considered`` after actually considering the evidence
triggers in ``learning_extract.py``. Both answers are always valid;
nothing counts sessions or demands an update (ADR-066/067 anti-sediment).
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:  # ADR-055 self-bootstrap (no PYTHONPATH)
    sys.path.insert(0, str(_REPO_ROOT))
_SCRIPTS = _REPO_ROOT / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

import protocol_mailbox  # noqa: E402


EXIT_DRAFTED = 0
EXIT_REFUSED = 3

_FIELD_ORDER = (
    "Checkpoint",
    "Boundary",
    "Objective",
    "Accepted scope",
    "Owner",
    "Policy revision",
    "Base",
    "Head",
    "Evidence refs",
    "Verification status",
    "Blockers",
    "Next action",
    "Lessons",
)


class CheckpointRefused(Exception):
    """The offered payload cannot form a parseable checkpoint; no draft."""


def _rev_parse(root: Path, revision: str) -> str:
    clean_env = {
        key: value
        for key, value in os.environ.items()
        if not key.startswith("GIT_")
    }
    clean_env.update({"LANG": "C", "LC_ALL": "C"})
    try:
        result = subprocess.run(
            ["/usr/bin/git", "-C", str(root), "rev-parse", revision],
            capture_output=True,
            check=True,
            env=clean_env,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        raise CheckpointRefused(f"cannot resolve {revision!r} in {root}") from exc
    return result.stdout.decode("ascii", errors="replace").strip()


def draft_checkpoint(
    *,
    root: Path,
    scratch: Path,
    checkpoint: str,
    boundary: str,
    objective: str,
    accepted_scope: str,
    owner: str,
    base: str,
    head: str | None,
    policy_revision: str | None,
    evidence_refs: list[str],
    verification_status: str,
    blockers: str,
    next_action: str,
    lessons: list[str],
) -> tuple[Path, str]:
    """Validate the payload shape and write ONE draft body to scratch."""

    fields = {
        "Checkpoint": checkpoint,
        "Boundary": boundary,
        "Objective": objective,
        "Accepted scope": accepted_scope,
        "Owner": owner,
        "Policy revision": policy_revision or _rev_parse(root, "HEAD"),
        "Base": base,
        "Head": head or _rev_parse(root, "HEAD"),
        "Evidence refs": (
            ", ".join(evidence_refs)
            if evidence_refs
            else protocol_mailbox.CHECKPOINT_NONE
        ),
        "Verification status": verification_status,
        "Blockers": blockers,
        "Next action": next_action,
        "Lessons": (
            ", ".join(lessons)
            if lessons
            else protocol_mailbox.CHECKPOINT_LESSONS_NONE
        ),
    }
    body = "\n".join(f"{label}: {fields[label]}" for label in _FIELD_ORDER) + "\n"
    if not protocol_mailbox.checkpoint_intent(body):
        raise CheckpointRefused(
            "the drafted body does not carry the canonical checkpoint shape"
        )
    # Round-trip the exact draft through the read-side parser so a draft
    # the writer would refuse never leaves this tool. The synthetic
    # envelope mirrors what send-event will wrap around the body.
    stamp = "2026-01-01T00-00-00Z"
    probe_path = (
        f"coordination/mailbox/sent/{stamp}-{owner}-to-all-findings.md"
    )
    probe_text = (
        f"# {owner.capitalize()} → All: checkpoint {checkpoint}\n\n"
        f"**When:** 2026-01-01T00:00:00Z · **From:** {owner} (online)\n\n"
        f"{body}\n"
        "Cursor at send: 0\n"
    )
    try:
        probe = protocol_mailbox.parse_committed_event_text(
            f"{probe_path}@{'0' * 40}", probe_text
        )
        protocol_mailbox.parse_checkpoint_statement(probe)
    except ValueError as exc:
        raise CheckpointRefused(str(exc)) from exc
    scratch.mkdir(parents=True, exist_ok=True)
    draft_path = scratch / f"checkpoint-{checkpoint}.md"
    draft_path.write_text(body, encoding="utf-8")
    return draft_path, body


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--repo-root", type=Path, default=_REPO_ROOT)
    parser.add_argument("--scratch", type=Path, required=True,
                        help="directory the ONE draft file is written into")
    parser.add_argument("--checkpoint", required=True,
                        help="campaign/task slug (lowercase, hyphens)")
    parser.add_argument("--boundary", required=True,
                        choices=protocol_mailbox.CHECKPOINT_BOUNDARIES)
    parser.add_argument("--objective", required=True)
    parser.add_argument("--accepted-scope", required=True)
    parser.add_argument("--owner", required=True,
                        help="pair seat; must equal the send-event sender")
    parser.add_argument("--base", required=True,
                        help="40-hex base commit of the owned range")
    parser.add_argument("--head", default=None,
                        help="40-hex head commit (default: repo-root HEAD)")
    parser.add_argument("--policy-revision", default=None,
                        help="instruction-surface commit (default: repo-root HEAD)")
    parser.add_argument("--evidence-ref", action="append", default=[],
                        help="immutable sent-path@sha or sha256: ref (repeatable)")
    parser.add_argument("--verification-status", required=True,
                        help="what was verified, with the command, or a plain 'none yet'")
    parser.add_argument("--blockers", required=True,
                        help="unresolved blockers, or the single word none")
    parser.add_argument("--next-action", required=True,
                        help="the one next executable action")
    parser.add_argument("--lesson-ref", action="append", default=[],
                        help="learning-candidate path@sha (repeatable); "
                             "omit for none-considered")
    arguments = parser.parse_args(argv)

    try:
        draft_path, body = draft_checkpoint(
            root=arguments.repo_root,
            scratch=arguments.scratch,
            checkpoint=arguments.checkpoint,
            boundary=arguments.boundary,
            objective=arguments.objective,
            accepted_scope=arguments.accepted_scope,
            owner=arguments.owner,
            base=arguments.base,
            head=arguments.head,
            policy_revision=arguments.policy_revision,
            evidence_refs=arguments.evidence_ref,
            verification_status=arguments.verification_status,
            blockers=arguments.blockers,
            next_action=arguments.next_action,
            lessons=arguments.lesson_ref,
        )
    except CheckpointRefused as refusal:
        print(f"no checkpoint: {refusal}", file=sys.stderr)
        return EXIT_REFUSED

    print(f"draft written: {draft_path}")
    print("--- body ---")
    print(body, end="")
    print("--- this tool never publishes; review the draft, then run "
          "coordination/bin/send-event yourself ---")
    return EXIT_DRAFTED


if __name__ == "__main__":
    raise SystemExit(main())
