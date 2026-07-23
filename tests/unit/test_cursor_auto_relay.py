from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts import cursor_auto_relay as relay


def _live_env(seat: str = "director") -> dict[str, str]:
    return {
        "CURSOR_SEAT": seat,
        "CURSOR_OPERATION": "dispatch",
        "GIT_INDEX_FILE": "/repo/.git/index-cursor-" + seat,
    }


def test_live_bound_requires_exact_seat_index_and_operation() -> None:
    assert relay.live_bound(_live_env("director"))
    assert not relay.live_bound({"CURSOR_SEAT": "director"})
    assert not relay.live_bound(
        {
            "CURSOR_SEAT": "director",
            "CURSOR_OPERATION": "readiness",
            "GIT_INDEX_FILE": "/repo/.git/index-cursor-director",
        }
    )
    assert not relay.live_bound(
        {
            "CURSOR_SEAT": "director",
            "CURSOR_OPERATION": "dispatch",
            "GIT_INDEX_FILE": "/repo/.git/index-cursor-operator",
        }
    )


def test_parse_relay_directive_reads_fence() -> None:
    fence = relay._FENCE
    text = (
        "summary\n\n"
        + fence
        + "cursor-relay\n"
        + '{"to":"operator","kind":"verify-request","subject":"review me","trigger_ref":"path@sha"}'
        + "\n"
        + fence
        + "\n"
    )
    payload = relay.parse_relay_directive(text)
    assert payload["to"] == "operator"
    assert payload["kind"] == "verify-request"


@pytest.mark.parametrize(
    ("to", "kind", "operation"),
    [
        ("operator", "verify-request", "review"),
        ("operator2", "verify-request", "review"),
        ("director", "status", "dispatch"),
    ],
)
def test_wake_operation_maps_verify_request_to_review(
    to: str, kind: str, operation: str
) -> None:
    assert relay.wake_operation(to=to, kind=kind) == operation


def test_publish_requires_live_binding(tmp_path: Path) -> None:
    bindir = tmp_path / "coordination" / "bin"
    bindir.mkdir(parents=True)
    (bindir / "send-event").write_text("#!/bin/sh\n", encoding="utf-8")
    with pytest.raises(relay.RelayError, match="live Cursor seat binding"):
        relay.publish(
            tmp_path,
            seat="director",
            to="operator",
            kind="status",
            subject="hello",
            body="body",
            environ={},
            runner=lambda *a, **k: 0,
        )


def test_publish_delegates_to_send_event(tmp_path: Path) -> None:
    bindir = tmp_path / "coordination" / "bin"
    bindir.mkdir(parents=True)
    (bindir / "send-event").write_text("#!/bin/sh\n", encoding="utf-8")
    seen: dict[str, object] = {}

    def runner(argv, **kwargs):
        seen["argv"] = argv
        seen["input"] = kwargs.get("input")
        return 0

    rc = relay.publish(
        tmp_path,
        seat="director",
        to="operator",
        kind="status",
        subject="hello",
        body="the body",
        environ=_live_env("director"),
        runner=runner,
    )
    assert rc == 0
    assert seen["argv"][-4:] == ["director", "operator", "status", "hello"]
    assert seen["input"] == "the body"


def test_wake_seat_dry_run_argv_has_no_foreign_launchers(tmp_path: Path) -> None:
    bindir = tmp_path / "coordination" / "bin"
    bindir.mkdir(parents=True)
    (bindir / "cursor-seat").write_text("#!/bin/sh\n", encoding="utf-8")
    directive = {
        "to": "operator",
        "kind": "verify-request",
        "subject": "review",
        "trigger_ref": "coordination/mailbox/sent/x.md@aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
    }
    argv, rc = relay.wake_seat(
        tmp_path,
        directive=directive,
        environ=_live_env("director"),
        dry_run=True,
    )
    assert rc == 0
    joined = " ".join(argv)
    assert "agy-seat" not in joined
    assert "codex-seat" not in joined
    assert argv[1] == "review"
