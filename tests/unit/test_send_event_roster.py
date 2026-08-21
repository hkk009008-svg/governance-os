"""The shell whitelists and the Python roster must not drift apart.

`coordination/bin/send-event` hand-codes the identities it accepts in shell
`case` statements. protocol_mailbox owns the roster those statements mirror.
A comment claimed a "token-extraction test" guarded them; that test was
deleted, so the claim described a control nobody had. This is that control,
written rather than asserted.
"""
from __future__ import annotations

import re
from pathlib import Path

import protocol_mailbox

_REPO_ROOT = Path(__file__).resolve().parents[2]
_SEND_EVENT = _REPO_ROOT / "coordination/bin/send-event"


def _case_alternatives(marker: str) -> set[str]:
    """The bare-word alternatives of the first `case` arm after *marker*."""

    text = _SEND_EVENT.read_text(encoding="utf-8")
    start = text.index(marker)
    arm = re.search(r"\n\s*([a-z0-9|]+)\)\s*;;", text[start:])
    assert arm, f"no case arm found after {marker!r}"
    return set(arm.group(1).split("|"))


def test_the_sender_whitelist_is_exactly_the_live_roles() -> None:
    assert _case_alternatives('case "$FROM" in') == set(protocol_mailbox.ROLES)


def test_the_recipient_whitelist_is_the_live_roles_plus_broadcast() -> None:
    assert _case_alternatives('case "$TO" in') == set(protocol_mailbox.ROLES) | {"all"}


def test_no_retired_seat_name_survives_in_a_send_event_whitelist() -> None:
    """The collapse must have reached the wrapper, not just the writer."""

    for marker in ('case "$FROM" in', 'case "$TO" in'):
        alternatives = _case_alternatives(marker)
        assert not alternatives & set(protocol_mailbox.LEGACY_SEATS), (
            f"{marker} still admits retired identities: "
            f"{sorted(alternatives & set(protocol_mailbox.LEGACY_SEATS))}"
        )


def test_the_extractor_would_notice_a_drifted_whitelist() -> None:
    """Reversion control: the parser must actually read the file's arms.

    A regex that matched nothing would make every assertion above vacuously
    true, so pin that it returns the real, non-empty content.
    """

    senders = _case_alternatives('case "$FROM" in')
    assert senders, "the extractor found no alternatives; it is not reading the script"
    assert "author" in senders and "reviewer" in senders
