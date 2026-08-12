"""Stage 2b gate tests: the six learning refusals bind at publication.

Every refusal is exercised through mailbox_writer._send_event_finalize — the
production call site — so deleting the learning branches from
validate_event_candidate (the correct-but-uncalled mutation) fails these
tests, not just narrower unit calls. Fixture repos are built per test, never
the checkout under review.
"""

from __future__ import annotations

import hashlib
import subprocess
import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

import mailbox_writer  # noqa: E402
import protocol_mailbox  # noqa: E402


def _git(root: Path, *args: str) -> str:
    result = subprocess.run(
        ["/usr/bin/git", "-C", str(root), *args],
        capture_output=True,
        check=True,
    )
    return result.stdout.decode("utf-8").strip()


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
    _commit(root, "chore: seed learning fixture")
    return root


def _commit(root: Path, message: str) -> str:
    _git(
        root,
        "-c", "user.name=Fixture",
        "-c", "user.email=fixture@example.invalid",
        "commit", "-q", "-m", message,
    )
    return _git(root, "rev-parse", "HEAD")


def _event_text(sender: str, recipient: str, title: str, stamp: str, body: str) -> str:
    colon = stamp[:11] + stamp[11:19].replace("-", ":") + "Z"
    return (
        f"# {sender.capitalize()} → {recipient.capitalize()}: {title}\n\n"
        f"**When:** {colon} · **From:** {sender} (online)\n\n"
        f"{body}\n\n"
        "Cursor at send: 0\n"
    )


def _publish(
    root: Path, sender: str, recipient: str, kind: str, stamp: str, body: str
) -> str:
    """Publish one event through the production finalizer; return its path."""

    name = f"{stamp}-{sender}-to-{recipient}-{kind}.md"
    relative = f"coordination/mailbox/sent/{name}"
    candidate = root / "coordination" / "mailbox" / "sent" / f".{name[:-3]}.fixture.tmp"
    candidate.write_text(
        _event_text(sender, recipient, "probe", stamp, body), encoding="utf-8"
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
        _event_text(sender, recipient, "probe", stamp, body), encoding="utf-8"
    )
    candidate.chmod(0o600)
    with pytest.raises(mailbox_writer.MailboxWriterError, match=match):
        mailbox_writer._send_event_finalize(root, candidate, relative)
    assert not (root / relative).exists(), "a refused event must not publish"
    candidate.unlink()


def _source_ref(root: Path) -> str:
    relative = _publish(
        root, "operator", "director", "findings",
        "2026-07-30T00-00-01Z", "observed the failure mode",
    )
    commit = _commit(root, "mailbox: source event")
    return f"{relative}@{commit}"


def _candidate_fields(source_ref: str, **overrides: str | None) -> dict[str, str | None]:
    fields: dict[str, str | None] = {
        "Category": "procedure",
        "Scope": "repository",
        "Statement": "Run the doctrine diff before every range submit.",
        "Proposed content hash": None,
        "Target": None,
        "Target base hash": None,
        "Source refs": source_ref,
        "Evidence provenance": "MEASURED",
        "Applicability": "any compact-pair range",
        "Exclusions": "scratch worktrees",
        "Risk class": "material-behavior",
        "Supersedes": None,
        "Producer seat": "operator",
        "Producer model": "gpt-5.6-sol",
    }
    fields.update(overrides)
    return fields


def _candidate_body(fields: dict[str, str | None]) -> str:
    lines = [
        f"Candidate ID: {protocol_mailbox.compute_learning_candidate_id(fields)}"
    ]
    lines.extend(
        f"{label}: {value}" for label, value in fields.items() if value is not None
    )
    return "\n".join(lines)


def _published_candidate_ref(
    root: Path, fields: dict[str, str | None], stamp: str = "2026-07-30T00-00-02Z"
) -> str:
    relative = _publish(
        root, "operator", "director", "learning-candidate", stamp,
        _candidate_body(fields),
    )
    commit = _commit(root, "mailbox: learning candidate")
    return f"{relative}@{commit}"


def test_happy_path_candidate_then_disposition(tmp_path: Path) -> None:
    root = _repo(tmp_path)
    ref = _published_candidate_ref(root, _candidate_fields(_source_ref(root)))
    _publish(
        root, "director", "all", "decision", "2026-07-30T00-00-03Z",
        f"Candidate: {ref}\nDisposition: accepted",
    )


def test_malformed_candidate_payload_is_refused_at_publication(
    tmp_path: Path,
) -> None:
    root = _repo(tmp_path)
    fields = _candidate_fields(_source_ref(root), Category="vibe")
    _refuse(
        root, "operator", "director", "learning-candidate",
        "2026-07-30T00-00-02Z", _candidate_body(fields),
        match="learning-candidate candidate is invalid",
    )


def test_unresolvable_source_ref_is_refused(tmp_path: Path) -> None:
    root = _repo(tmp_path)
    _source_ref(root)  # commit real history so only the ref is bad
    phantom = (
        "coordination/mailbox/sent/"
        "2026-07-29T00-00-00Z-operator-to-director-status.md@" + "e" * 40
    )
    _refuse(
        root, "operator", "director", "learning-candidate",
        "2026-07-30T00-00-02Z",
        _candidate_body(_candidate_fields(phantom)),
        match="source ref does not resolve",
    )


def test_duplicate_candidate_id_is_refused(tmp_path: Path) -> None:
    root = _repo(tmp_path)
    fields = _candidate_fields(_source_ref(root))
    _published_candidate_ref(root, fields)
    _refuse(
        root, "operator", "director", "learning-candidate",
        "2026-07-30T00-00-09Z", _candidate_body(fields),
        match="duplicates committed candidate",
    )


def test_self_approval_is_refused(tmp_path: Path) -> None:
    root = _repo(tmp_path)
    ref = _published_candidate_ref(root, _candidate_fields(_source_ref(root)))
    # Producer seat is operator; the operator disposing it is self-approval.
    _refuse(
        root, "operator", "all", "decision", "2026-07-30T00-00-03Z",
        f"Candidate: {ref}\nDisposition: accepted",
        match="self-approval",
    )


def test_unresolvable_candidate_ref_in_decision_is_refused(
    tmp_path: Path,
) -> None:
    root = _repo(tmp_path)
    _source_ref(root)
    phantom = (
        "coordination/mailbox/sent/"
        "2026-07-29T00-00-00Z-operator-to-director-learning-candidate.md@"
        + "e" * 40
    )
    _refuse(
        root, "director", "all", "decision", "2026-07-30T00-00-03Z",
        f"Candidate: {phantom}\nDisposition: accepted",
        match="does not resolve to a committed",
    )


def test_assumed_provenance_cannot_be_accepted_but_can_be_declined(
    tmp_path: Path,
) -> None:
    root = _repo(tmp_path)
    ref = _published_candidate_ref(
        root,
        _candidate_fields(
            _source_ref(root), **{"Evidence provenance": "ASSUMED"}
        ),
    )
    _refuse(
        root, "director", "all", "decision", "2026-07-30T00-00-03Z",
        f"Candidate: {ref}\nDisposition: accepted",
        match="ASSUMED-provenance",
    )
    _publish(
        root, "director", "all", "decision", "2026-07-30T00-00-04Z",
        f"Candidate: {ref}\nDisposition: declined",
    )


def test_governance_rule_below_floor_cannot_be_accepted(tmp_path: Path) -> None:
    root = _repo(tmp_path)
    ref = _published_candidate_ref(
        root,
        _candidate_fields(
            _source_ref(root),
            Category="governance-rule",
            **{"Risk class": "material-behavior"},
        ),
    )
    _refuse(
        root, "director", "all", "decision", "2026-07-30T00-00-03Z",
        f"Candidate: {ref}\nDisposition: accepted",
        match="high-risk-control floor",
    )


def test_stale_target_base_hash_is_refused_by_cas(tmp_path: Path) -> None:
    root = _repo(tmp_path)
    source = _source_ref(root)
    base_hash = "sha256:" + hashlib.sha256(
        (root / "README.md").read_bytes()
    ).hexdigest()
    ref = _published_candidate_ref(
        root,
        _candidate_fields(
            source,
            Target="README.md",
            **{"Target base hash": base_hash},
        ),
    )
    # Fresh target: acceptance passes the CAS.
    _publish(
        root, "director", "all", "decision", "2026-07-30T00-00-03Z",
        f"Candidate: {ref}\nDisposition: accepted",
    )
    _commit(root, "mailbox: fresh acceptance")
    # The target moves; a second acceptance replays against stale bytes.
    (root / "README.md").write_text("fixture target v2\n", encoding="utf-8")
    _git(root, "add", "README.md")
    _commit(root, "docs: move the target")
    _refuse(
        root, "director2", "all", "decision", "2026-07-30T00-00-05Z",
        f"Candidate: {ref}\nDisposition: accepted",
        match="stale at the publication commit",
    )


def test_ordinary_decision_without_candidate_field_still_publishes(
    tmp_path: Path,
) -> None:
    root = _repo(tmp_path)
    _publish(
        root, "director", "all", "decision", "2026-07-30T00-00-03Z",
        "Ruling: adopt the defaults for every open item.",
    )


def test_prose_candidate_lines_do_not_trigger_disposition_validation(
    tmp_path: Path,
) -> None:
    """Round-one FAIL regression: free prose is never refused as a disposition."""

    root = _repo(tmp_path)
    # A hiring-style note: Candidate + Disposition lines, neither machine-shaped.
    _publish(
        root, "director", "all", "decision", "2026-07-30T00-00-03Z",
        "Candidate: Jane Doe for the ops role\n"
        "Disposition: hired, starts Monday",
    )
    # Quoting a real canonical ref in discussion, with no Disposition line,
    # is prose to readers and must publish.
    quoted = (
        "coordination/mailbox/sent/"
        "2026-07-29T00-00-00Z-operator-to-director-learning-candidate.md@"
        + "b" * 40
    )
    _publish(
        root, "director", "all", "decision", "2026-07-30T00-00-04Z",
        f"Discussing Candidate: {quoted} before any ruling.",
    )


def test_machine_shaped_disposition_still_validates(tmp_path: Path) -> None:
    """The intent predicate must not have loosened the real refusals."""

    root = _repo(tmp_path)
    phantom = (
        "coordination/mailbox/sent/"
        "2026-07-29T00-00-00Z-operator-to-director-learning-candidate.md@"
        + "e" * 40
    )
    _refuse(
        root, "director", "all", "decision", "2026-07-30T00-00-05Z",
        f"Candidate: {phantom}\nDisposition: accepted",
        match="does not resolve to a committed",
    )
