from __future__ import annotations

import protocol_mailbox


def test_current_roster_kinds_and_routes_are_exact() -> None:
    assert protocol_mailbox.APP_MEMBERS == ("codex", "claude", "agy")
    assert protocol_mailbox.FORMAL_REVIEWERS == {"codex", "claude"}
    assert protocol_mailbox.KNOWN_KINDS == {"verify-request", "verification-report"}
    assert protocol_mailbox.formal_review_route_problem(
        "verify-request", "agy", "claude"
    ) is None
    assert protocol_mailbox.formal_review_route_problem(
        "verification-report", "claude", "agy"
    ) is None


def test_invalid_formal_routes_fail_closed() -> None:
    assert "self-addressed" in protocol_mailbox.formal_review_route_problem(
        "verify-request", "codex", "codex"
    )
    assert "publisher" in protocol_mailbox.formal_review_route_problem(
        "verification-report", "agy", "codex"
    )
    assert "not a formal-review kind" in protocol_mailbox.formal_review_route_problem(
        "status", "codex", "claude"
    )
