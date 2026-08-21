"""Checkpoint record tests: durable continuation payload, typed and gated.

The parser refusals are exercised through mailbox_writer._send_event_finalize
— the production call site — so deleting the findings branch from
validate_event_candidate_bytes (the correct-but-uncalled mutation) fails
these tests, not just narrower unit calls. Fixture repos are built per test,
never the checkout under review.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

import draft_checkpoint  # noqa: E402
import mailbox_writer  # noqa: E402
import protocol_mailbox  # noqa: E402


# Hermetic fixture-git environment: the ambient VM configuration (commit
# signing via the exec-daemon shim, fsmonitor daemons) must not run inside
# throwaway test repositories; see tests/unit/test_check_coordination.py.
_GIT_ENV = {
    "PATH": "/usr/bin:/bin",
    "HOME": "/var/empty" if Path("/var/empty").is_dir() else "/nonexistent",
    "GIT_CONFIG_NOSYSTEM": "1",
    "GIT_CONFIG_COUNT": "1",
    "GIT_CONFIG_KEY_0": "init.defaultBranch",
    "GIT_CONFIG_VALUE_0": "main",
}


def _git(root: Path, *args: str) -> str:
    result = subprocess.run(
        ["/usr/bin/git", "-C", str(root), *args],
        capture_output=True,
        check=True,
        env=_GIT_ENV,
    )
    return result.stdout.decode("utf-8").strip()


def _commit(root: Path, message: str) -> str:
    _git(
        root,
        "-c", "user.name=Fixture",
        "-c", "user.email=fixture@example.invalid",
        "commit", "-q", "-m", message,
    )
    return _git(root, "rev-parse", "HEAD")


def _repo(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    root.mkdir()
    _git(root, "init", "-q")
    (root / "README.md").write_text("fixture target v1\n", encoding="utf-8")
    sent = root / "coordination" / "mailbox" / "sent"
    sent.mkdir(parents=True)
    (root / "coordination" / "mailbox" / "kinds.txt").write_text(
        "decision\nfindings\nlearning-candidate\nstatus\nverify-request\n",
        encoding="utf-8",
    )
    _git(root, "add", "-A")
    _commit(root, "chore: seed checkpoint fixture")
    return root


def _event_text(sender: str, recipient: str, stamp: str, body: str) -> str:
    colon = stamp[:11] + stamp[11:19].replace("-", ":") + "Z"
    return (
        f"# {sender.capitalize()} → {recipient.capitalize()}: probe\n\n"
        f"**When:** {colon} · **From:** {sender} (online)\n\n"
        f"{body}\n\n"
        "Cursor at send: cursorless\n"
    )


def _publish(
    root: Path, sender: str, recipient: str, kind: str, stamp: str, body: str
) -> str:
    name = f"{stamp}-{sender}-to-{recipient}-{kind}.md"
    relative = f"coordination/mailbox/sent/{name}"
    candidate = root / "coordination" / "mailbox" / "sent" / f".{name[:-3]}.fixture.tmp"
    candidate.write_text(
        _event_text(sender, recipient, stamp, body), encoding="utf-8"
    )
    candidate.chmod(0o600)
    assert mailbox_writer._send_event_finalize(root, candidate, relative)
    return relative


def _refuse(
    root: Path, sender: str, recipient: str, kind: str, stamp: str, body: str,
    match: str,
) -> None:
    name = f"{stamp}-{sender}-to-{recipient}-{kind}.md"
    relative = f"coordination/mailbox/sent/{name}"
    candidate = root / "coordination" / "mailbox" / "sent" / f".{name[:-3]}.fixture.tmp"
    candidate.write_text(
        _event_text(sender, recipient, stamp, body), encoding="utf-8"
    )
    candidate.chmod(0o600)
    with pytest.raises(mailbox_writer.MailboxWriterError, match=match):
        mailbox_writer._send_event_finalize(root, candidate, relative)
    assert not (root / relative).exists(), "a refused event must not publish"
    candidate.unlink()


def _evidence_ref(root: Path) -> str:
    relative = _publish(
        root, "reviewer", "author", "findings",
        "2026-08-12T00-00-01Z", "observed evidence for the checkpoint",
    )
    _git(root, "add", relative)
    commit = _commit(root, "mailbox: evidence event")
    return f"{relative}@{commit}"


def _checkpoint_fields(root: Path, **overrides: str) -> dict[str, str]:
    head = _git(root, "rev-parse", "HEAD")
    fields = {
        "Checkpoint": "memory-skill-evolution",
        "Boundary": "compaction",
        "Objective": "land the durable checkpoint mechanism",
        "Accepted scope": "scripts, tests, and protocol docs on this branch",
        "Owner": "author",
        "Policy revision": head,
        "Base": head,
        "Head": head,
        "Evidence refs": "none",
        "Verification status": "pytest tests/unit/test_checkpoint.py green at head",
        "Blockers": "none",
        "Next action": "publish the checkpoint and resume from the snapshot",
        "Lessons": "none-considered",
    }
    fields.update(overrides)
    return fields


def _body(fields: dict[str, str]) -> str:
    return "\n".join(f"{label}: {value}" for label, value in fields.items())


def test_checkpoint_round_trips_through_production_finalizer(tmp_path: Path) -> None:
    root = _repo(tmp_path)
    evidence = _evidence_ref(root)
    fields = _checkpoint_fields(root, **{"Evidence refs": evidence})
    relative = _publish(
        root, "author", "all", "findings",
        "2026-08-12T00-10-00Z", _body(fields),
    )
    _git(root, "add", relative)
    commit = _commit(root, "mailbox: checkpoint")

    statement = protocol_mailbox.load_checkpoint_statement(
        root, f"{relative}@{commit}"
    )

    assert statement.checkpoint == "memory-skill-evolution"
    assert statement.boundary == "compaction"
    assert statement.owner == "author"
    assert statement.evidence_refs == (evidence,)
    assert statement.lessons == ()
    assert statement.next_action.startswith("publish the checkpoint")

    committed = protocol_mailbox.committed_checkpoints(root, "HEAD")
    assert [item.event.path for item in committed] == [relative]


def test_ordinary_findings_publish_untouched(tmp_path: Path) -> None:
    root = _repo(tmp_path)
    relative = _publish(
        root, "reviewer", "author", "findings",
        "2026-08-12T00-11-00Z",
        "Checkpoint: reached the third milestone of the plan today.\n"
        "No structured payload here.",
    )
    assert (root / relative).exists()
    assert not protocol_mailbox.checkpoint_intent(
        (root / relative).read_text(encoding="utf-8")
    )


def test_owner_must_match_envelope_sender(tmp_path: Path) -> None:
    root = _repo(tmp_path)
    fields = _checkpoint_fields(root, Owner="reviewer")
    _refuse(
        root, "author", "all", "findings",
        "2026-08-12T00-12-00Z", _body(fields),
        match="Owner must match the envelope sender",
    )


def test_boundary_vocabulary_is_closed(tmp_path: Path) -> None:
    root = _repo(tmp_path)
    fields = _checkpoint_fields(root, Boundary="sometimes")
    _refuse(
        root, "author", "all", "findings",
        "2026-08-12T00-13-00Z", _body(fields),
        match="Boundary must be transfer",
    )


def test_range_fields_must_be_full_shas(tmp_path: Path) -> None:
    root = _repo(tmp_path)
    fields = _checkpoint_fields(root, Base="HEAD")
    _refuse(
        root, "author", "all", "findings",
        "2026-08-12T00-14-00Z", _body(fields),
        match="Base must be a 40-hex commit SHA",
    )


def test_unresolvable_evidence_ref_is_refused_at_publication(
    tmp_path: Path,
) -> None:
    root = _repo(tmp_path)
    ghost = (
        "coordination/mailbox/sent/"
        "2026-08-01T00-00-00Z-reviewer-to-author-findings.md@" + "b" * 40
    )
    fields = _checkpoint_fields(root, **{"Evidence refs": ghost})
    _refuse(
        root, "author", "all", "findings",
        "2026-08-12T00-15-00Z", _body(fields),
        match="checkpoint ref does not resolve",
    )


def test_lessons_must_name_learning_candidates_or_none_considered(
    tmp_path: Path,
) -> None:
    root = _repo(tmp_path)
    not_a_candidate = _evidence_ref(root)
    fields = _checkpoint_fields(root, Lessons=not_a_candidate)
    _refuse(
        root, "author", "all", "findings",
        "2026-08-12T00-16-00Z", _body(fields),
        match="Lessons refs must name learning-candidate events",
    )


def test_no_quota_exists_none_considered_always_publishes(tmp_path: Path) -> None:
    """Anti-sediment pin (ADR-066/067): the Lessons field prompts, never counts.

    Publishing many consecutive none-considered checkpoints stays valid —
    no counter, session quota, or most-sessions-should-update bias may
    refuse the honest empty answer.
    """

    root = _repo(tmp_path)
    for index in range(3):
        fields = _checkpoint_fields(
            root, Checkpoint=f"quiet-campaign-{index}"
        )
        relative = _publish(
            root, "author", "all", "findings",
            f"2026-08-12T00-2{index}-00Z", _body(fields),
        )
        assert (root / relative).exists()


def test_draft_tool_writes_scratch_only_and_output_parses(tmp_path: Path) -> None:
    root = _repo(tmp_path)
    scratch = tmp_path / "scratch"
    head = _git(root, "rev-parse", "HEAD")
    before = {path for path in root.rglob("*") if path.is_file()}

    draft_path, body = draft_checkpoint.draft_checkpoint(
        root=root,
        scratch=scratch,
        checkpoint="memory-skill-evolution",
        boundary="wrap",
        objective="wrap the campaign",
        accepted_scope="this branch",
        owner="author",
        base=head,
        head=None,
        policy_revision=None,
        evidence_refs=[],
        verification_status="targeted tests green at head",
        blockers="none",
        next_action="publish and hand off",
        lessons=[],
    )

    after = {path for path in root.rglob("*") if path.is_file()}
    assert before == after, "the draft tool must not write inside the repo"
    assert draft_path.parent == scratch
    assert f"Head: {head}" in body
    assert "Lessons: none-considered" in body

    relative = _publish(
        root, "author", "all", "findings",
        "2026-08-12T00-30-00Z", body.rstrip("\n"),
    )
    assert (root / relative).exists()


def test_draft_tool_refuses_bad_slug(tmp_path: Path) -> None:
    root = _repo(tmp_path)
    head = _git(root, "rev-parse", "HEAD")
    with pytest.raises(draft_checkpoint.CheckpointRefused):
        draft_checkpoint.draft_checkpoint(
            root=root,
            scratch=tmp_path / "scratch",
            checkpoint="Not A Slug",
            boundary="wrap",
            objective="x",
            accepted_scope="x",
            owner="author",
            base=head,
            head=None,
            policy_revision=None,
            evidence_refs=[],
            verification_status="x",
            blockers="none",
            next_action="x",
            lessons=[],
        )
    assert not (tmp_path / "scratch").exists()


def test_kernel_validators_import_no_learning_module() -> None:
    """I1 companion: the checkpoint stays typed in protocol_mailbox.

    mailbox_writer may call the shared mailbox parsers (the same module the
    learning validators live in) but the checkpoint feature must not pull a
    learning_* module into the kernel files.
    """

    import compact_pair_loop

    for module in (mailbox_writer, compact_pair_loop):
        source = Path(module.__file__).read_text(encoding="utf-8")
        assert "import learning_" not in source
        assert "from learning_" not in source
