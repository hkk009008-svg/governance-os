from __future__ import annotations

from pathlib import Path

import draft_handoff
import mailbox_monitor


def _event(name: str, to: str) -> dict[str, str]:
    return {
        "filename": name,
        "to": to,
        "ts": name[:20].replace("-", ":", 2),
    }


def test_mailbox_monitor_scalar_without_bus_uses_mailbox_fallback(
    tmp_path: Path,
) -> None:
    first = "2026-07-25T01-00-00Z-director-to-operator-status.md"
    second = "2026-07-25T01-00-01Z-director-to-all-status.md"
    events = [_event(first, "operator"), _event(second, "all")]

    unread = mailbox_monitor._unread_events(
        events, "1", "operator", root=tmp_path
    )

    assert unread is not None
    assert [event["filename"] for event in unread] == [second]


def test_mailbox_monitor_malformed_cursor_is_unavailable_not_empty(
    tmp_path: Path,
) -> None:
    events = [
        _event(
            "2026-07-25T01-00-00Z-director-to-operator-status.md",
            "operator",
        )
    ]

    assert mailbox_monitor._unread_events(
        events, "not-a-cursor", "operator", root=tmp_path
    ) is None


def test_draft_handoff_scalar_without_bus_uses_mailbox_fallback(
    tmp_path: Path,
) -> None:
    sent = tmp_path / "coordination/mailbox/sent"
    sent.mkdir(parents=True)
    first = "2026-07-25T01-00-00Z-director-to-operator-status.md"
    second = "2026-07-25T01-00-01Z-director-to-all-status.md"
    (sent / first).write_text("one\n", encoding="utf-8")
    (sent / second).write_text("two\n", encoding="utf-8")

    assert draft_handoff._mailbox_events(
        tmp_path, "operator", cursor="1"
    ) == [second]


def test_draft_handoff_malformed_cursor_is_visible(
    tmp_path: Path,
) -> None:
    sent = tmp_path / "coordination/mailbox/sent"
    sent.mkdir(parents=True)
    (sent / "2026-07-25T01-00-00Z-director-to-operator-status.md").write_text(
        "one\n", encoding="utf-8"
    )

    events = draft_handoff._mailbox_events(
        tmp_path, "operator", cursor="not-a-cursor"
    )

    assert len(events) == 1
    assert events[0].startswith("(unavailable:")


def test_draft_handoff_coordinator_is_explicitly_cursorless(
    tmp_path: Path,
) -> None:
    (tmp_path / "coordination/mailbox/sent").mkdir(parents=True)

    assert draft_handoff._mailbox_events(
        tmp_path, "coordinator", cursor="0"
    ) == ["(cursorless coordinator; inspect recent coordination mail read-only)"]
