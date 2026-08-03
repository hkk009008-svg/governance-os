"""Unit tests for scripts/protocol_mailbox.py — the shared mailbox vocabulary.

Covers the seat/recipient rosters and the kinds.txt-backed KNOWN_KINDS set.
Hermetic: reads only the committed kinds.txt for module-level constants, and
uses tmp_path for the loader-with-custom-root path.
"""

from __future__ import annotations

from pathlib import Path
import subprocess

import pytest

import protocol_mailbox


# --- Static roster invariants -------------------------------------------------


def test_seats_exact_membership():
    # The four pair seats; assert membership so a future reorder doesn't break us,
    # plus the exact set so no extras sneak in.
    expected = {"director", "director2", "operator", "operator2"}
    assert set(protocol_mailbox.SEATS) == expected
    for seat in expected:
        assert seat in protocol_mailbox.SEATS
    # No duplicates in the roster tuple.
    assert len(protocol_mailbox.SEATS) == len(set(protocol_mailbox.SEATS))


def test_receiving_seats_superset_of_seats_plus_coordinators():
    receiving = set(protocol_mailbox.RECEIVING_SEATS)
    seats = set(protocol_mailbox.SEATS)
    assert seats <= receiving
    assert "coordinator" in receiving
    assert "coordinator2" in receiving
    # `all` is a broadcast target only — never a receiving seat.
    assert "all" not in receiving
    assert receiving == seats | {"coordinator", "coordinator2"}


def test_senders_roster():
    senders = set(protocol_mailbox.SENDERS)
    assert set(protocol_mailbox.SEATS) <= senders
    assert "coordinator" in senders
    assert "coordinator2" in senders
    # `all` is not a sender.
    assert "all" not in senders
    # Senders mirror the receiving roster (every receiver can also send).
    assert senders == set(protocol_mailbox.RECEIVING_SEATS)


def test_recipients_includes_all_but_all_is_not_a_seat():
    recipients = set(protocol_mailbox.RECIPIENTS)
    assert "all" in recipients
    assert "all" not in protocol_mailbox.SEATS
    # Every receiving seat is also a valid recipient target.
    assert set(protocol_mailbox.RECEIVING_SEATS) <= recipients
    # RECIPIENTS is exactly the receiving roster plus the broadcast target.
    assert recipients == set(protocol_mailbox.RECEIVING_SEATS) | {"all"}


# --- KNOWN_KINDS loaded from coordination/mailbox/kinds.txt --------------------


def test_known_kinds_is_nonempty_frozenset():
    assert isinstance(protocol_mailbox.KNOWN_KINDS, frozenset)
    assert len(protocol_mailbox.KNOWN_KINDS) > 0


def test_known_kinds_contains_representative_kinds():
    for kind in ("verification-report", "status", "findings", "dispatch-claim"):
        assert kind in protocol_mailbox.KNOWN_KINDS


def test_known_kinds_count_matches_nonblank_noncomment_lines():
    kind_file = Path(protocol_mailbox.KIND_FILE)
    lines = kind_file.read_text(encoding="utf-8").splitlines()
    meaningful = [
        ln.strip()
        for ln in lines
        if ln.strip() and not ln.strip().startswith("#")
    ]
    assert len(protocol_mailbox.KNOWN_KINDS) == len(meaningful)
    # The frozenset is exactly the deduped set of those lines.
    assert protocol_mailbox.KNOWN_KINDS == frozenset(meaningful)


def test_coordination_kinds_excludes_verification_report():
    assert "verification-report" not in protocol_mailbox.COORDINATION_KINDS
    assert protocol_mailbox.COORDINATION_KINDS == (
        protocol_mailbox.KNOWN_KINDS - {"verification-report"}
    )


# --- load_known_kinds() loader behavior with an explicit root -----------------


def test_load_known_kinds_with_custom_root(tmp_path):
    mbox = tmp_path / "coordination" / "mailbox"
    mbox.mkdir(parents=True)
    (mbox / "kinds.txt").write_text(
        "# a comment line\n"
        "status\n"
        "  findings  \n"          # whitespace stripped
        "\n"                       # blank line ignored
        "   \n"                    # whitespace-only line ignored
        "  # indented comment\n"   # comment after strip → ignored
        "status\n"                 # duplicate → deduped by frozenset
        "dispatch-claim\n",
        encoding="utf-8",
    )
    result = protocol_mailbox.load_known_kinds(root=tmp_path)
    assert isinstance(result, frozenset)
    assert result == frozenset({"status", "findings", "dispatch-claim"})


def test_load_known_kinds_default_root_matches_module_constant():
    # Calling with no root reproduces the module-level KNOWN_KINDS.
    assert protocol_mailbox.load_known_kinds() == protocol_mailbox.KNOWN_KINDS


# --- Immutable fixed-writer event references ---------------------------------


def _git(repo: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=repo,
        text=True,
        capture_output=True,
        check=check,
    )


def _init_repo(repo: Path) -> None:
    _git(repo, "init", "-q")
    _git(repo, "config", "user.name", "Protocol Test")
    _git(repo, "config", "user.email", "protocol@example.test")


def _commit_event(
    repo: Path,
    *,
    sender: str = "director",
    envelope_sender: str | None = None,
    recipient: str = "operator",
    kind: str = "proposal",
    timestamp: str = "2026-07-18T06-30-00Z",
    body: str = "Task ID: task-1",
) -> tuple[Path, str]:
    sent = repo / "coordination" / "mailbox" / "sent"
    sent.mkdir(parents=True, exist_ok=True)
    path = sent / f"{timestamp}-{sender}-to-{recipient}-{kind}.md"
    iso_timestamp = timestamp[:11] + timestamp[11:19].replace("-", ":") + "Z"
    path.write_text(
        "# Director → Operator: immutable event\n\n"
        f"**When:** {iso_timestamp} · **From:** {envelope_sender or sender} (online)\n\n"
        f"{body.rstrip()}\n",
        encoding="utf-8",
    )
    rel = path.relative_to(repo).as_posix()
    _git(repo, "add", "--", rel)
    _git(repo, "commit", "-q", "-m", "event")
    commit = _git(repo, "rev-parse", "HEAD").stdout.strip()
    return path, commit


def test_load_committed_event_ref_uses_exact_committed_fixed_writer_blob(tmp_path: Path):
    _init_repo(tmp_path)
    path, commit = _commit_event(tmp_path)
    rel = path.relative_to(tmp_path).as_posix()

    loaded = protocol_mailbox.load_committed_event_ref(tmp_path, f"{rel}@{commit}")

    assert loaded.path == rel
    assert loaded.commit == commit
    assert loaded.sender == "director"
    assert loaded.recipient == "operator"
    assert loaded.kind == "proposal"
    assert loaded.ref == f"{rel}@{commit}"

    # The loader is pinned to commit:path, not to later working-tree bytes.
    path.write_text("mutable working tree replacement\n", encoding="utf-8")
    assert protocol_mailbox.load_committed_event_ref(tmp_path, f"{rel}@{commit}") == loaded


@pytest.mark.parametrize(
    "reference",
    [
        "coordination/mailbox/sent/missing.md@" + "0" * 40,
        "docs/not-mail.md@" + "0" * 40,
        "coordination/mailbox/sent/event.md@abcdef0",
        "coordination/mailbox/sent/../event.md@" + "0" * 40,
        "./coordination/mailbox/sent/event.md@" + "0" * 40,
        "coordination//mailbox/sent/event.md@" + "0" * 40,
        "coordination\\mailbox\\sent\\event.md@" + "0" * 40,
        "/coordination/mailbox/sent/event.md@" + "0" * 40,
    ],
)
def test_load_committed_event_ref_rejects_missing_nonmailbox_or_nonfull_refs(
    tmp_path: Path, reference: str
):
    _init_repo(tmp_path)
    with pytest.raises(ValueError):
        protocol_mailbox.load_committed_event_ref(tmp_path, reference)


def test_load_committed_event_ref_rejects_filename_envelope_sender_mismatch(tmp_path: Path):
    _init_repo(tmp_path)
    path, commit = _commit_event(tmp_path, sender="director", envelope_sender="operator")
    ref = f"{path.relative_to(tmp_path).as_posix()}@{commit}"

    with pytest.raises(ValueError, match="sender"):
        protocol_mailbox.load_committed_event_ref(tmp_path, ref)


def test_load_committed_event_ref_rejects_uncommitted_working_tree_event(tmp_path: Path):
    _init_repo(tmp_path)
    tracked, _ = _commit_event(tmp_path)
    uncommitted = tracked.with_name(
        "2026-07-18T06-31-00Z-director-to-operator-proposal.md"
    )
    uncommitted.write_text(tracked.read_text(encoding="utf-8"), encoding="utf-8")
    commit = _git(tmp_path, "rev-parse", "HEAD").stdout.strip()

    with pytest.raises(ValueError):
        protocol_mailbox.load_committed_event_ref(
            tmp_path,
            f"{uncommitted.relative_to(tmp_path).as_posix()}@{commit}",
        )


def test_load_committed_event_ref_rejects_path_not_present_in_named_commit(tmp_path: Path):
    _init_repo(tmp_path)
    first_path, first_commit = _commit_event(tmp_path)
    second_path, _ = _commit_event(
        tmp_path,
        timestamp="2026-07-18T06-32-00Z",
        kind="proposal-reply",
        sender="operator",
        recipient="director",
    )
    assert first_path.exists()

    with pytest.raises(ValueError):
        protocol_mailbox.load_committed_event_ref(
            tmp_path,
            f"{second_path.relative_to(tmp_path).as_posix()}@{first_commit}",
        )


def test_load_committed_event_ref_rejects_tree_object_instead_of_commit(tmp_path: Path):
    _init_repo(tmp_path)
    path, _ = _commit_event(tmp_path)
    tree = _git(tmp_path, "rev-parse", "HEAD^{tree}").stdout.strip()

    with pytest.raises(ValueError, match="commit object"):
        protocol_mailbox.load_committed_event_ref(
            tmp_path,
            f"{path.relative_to(tmp_path).as_posix()}@{tree}",
        )


def test_pure_event_parser_matches_existing_git_backed_loader(tmp_path: Path):
    _init_repo(tmp_path)
    path, commit = _commit_event(tmp_path)
    ref = f"{path.relative_to(tmp_path).as_posix()}@{commit}"
    text = _git(tmp_path, "show", f"{commit}:{path.relative_to(tmp_path).as_posix()}").stdout

    assert protocol_mailbox.parse_committed_event_text(ref, text) == (
        protocol_mailbox.load_committed_event_ref(tmp_path, ref)
    )


def test_pure_statement_parsers_preserve_duplicate_and_mismatch_rejection(tmp_path: Path):
    _init_repo(tmp_path)
    proposal_body = "\n".join(
        (
            "Task ID: task-1",
            "Parent contract: sha256:" + "1" * 64,
            "Contract revision: 1",
            "Previous owners: director",
            "Proposed owners: operator",
            "Outcome: tested outcome",
            "Finding refs: (none)",
        )
    )
    path, commit = _commit_event(tmp_path, body=proposal_body)
    ref = f"{path.relative_to(tmp_path).as_posix()}@{commit}"
    event = protocol_mailbox.load_committed_event_ref(tmp_path, ref)

    parsed = protocol_mailbox.parse_ownership_proposal_statement(event)
    assert parsed.task_id == "task-1"
    assert parsed.proposed_owners == ("operator",)

    duplicate = protocol_mailbox.CommittedEventRef(
        **{**event.__dict__, "text": event.text + "Task ID: duplicate\n"}
    )
    with pytest.raises(ValueError, match="exactly one"):
        protocol_mailbox.parse_ownership_proposal_statement(duplicate)

    wrong_kind = protocol_mailbox.CommittedEventRef(
        **{**event.__dict__, "kind": "proposal-reply"}
    )
    with pytest.raises(ValueError, match="proposal"):
        protocol_mailbox.parse_ownership_proposal_statement(wrong_kind)

    evidence = protocol_mailbox.CommittedEventRef(
        **{
            **event.__dict__,
            "kind": "dispatch-claim",
            "text": event.text
            + "Observed at: 2026-07-18T06:30:01Z\n"
            + "Fresh work state: no fresh work\n"
            + "Lock state: no active lock\n",
        }
    )
    with pytest.raises(ValueError, match="observation time"):
        protocol_mailbox.parse_takeover_evidence_statement(evidence)
