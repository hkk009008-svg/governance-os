from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts import cursor_mailbox as mailbox

LAUNCH_SEATS = ("director", "director2", "operator", "operator2", "coordinator")


def _writers(root: Path) -> None:
    bindir = root / "coordination" / "bin"
    bindir.mkdir(parents=True, exist_ok=True)
    for name in ("send-event", "consume-events"):
        (bindir / name).write_text("#!/bin/sh\n", encoding="utf-8")


def test_resolve_seat_uses_explicit_when_unbound_then_env() -> None:
    assert mailbox.resolve_seat("operator", {}) == "operator"
    assert mailbox.resolve_seat(None, {"CURSOR_SEAT": "director"}) == "director"


def test_resolve_seat_rejects_explicit_mismatch_with_bound_seat() -> None:
    with pytest.raises(mailbox.MailboxBindingError, match="does not match"):
        mailbox.resolve_seat("operator", {"CURSOR_SEAT": "director"})


@pytest.mark.parametrize("value", [None, "", "readiness-bridge", "operator3", "coordinator2"])
def test_resolve_seat_rejects_unknown_from_seat(value: str | None) -> None:
    with pytest.raises(mailbox.MailboxBindingError):
        mailbox.resolve_seat(value, {} if value is None else {"CURSOR_SEAT": value})


def test_build_publish_argv_delegates_to_fixed_writer(tmp_path: Path) -> None:
    _writers(tmp_path)
    argv = mailbox.build_publish_argv(
        tmp_path, seat="director", to="operator", kind="status", subject="a subject"
    )

    assert argv == [
        str(tmp_path / "coordination" / "bin" / "send-event"),
        "director",
        "operator",
        "status",
        "a subject",
    ]


def test_build_publish_argv_rejects_self_addressed(tmp_path: Path) -> None:
    _writers(tmp_path)
    with pytest.raises(mailbox.MailboxBindingError, match="self-addressed"):
        mailbox.build_publish_argv(
            tmp_path, seat="director", to="director", kind="status", subject="x"
        )


@pytest.mark.parametrize(
    ("to", "kind", "subject"),
    [("", "status", "s"), ("operator", "", "s"), ("operator", "status", "")],
)
def test_build_publish_argv_requires_all_fields(
    tmp_path: Path, to: str, kind: str, subject: str
) -> None:
    _writers(tmp_path)
    with pytest.raises(mailbox.MailboxBindingError):
        mailbox.build_publish_argv(tmp_path, seat="director", to=to, kind=kind, subject=subject)


def test_build_consume_argv_delegates_to_fixed_writer(tmp_path: Path) -> None:
    _writers(tmp_path)
    argv = mailbox.build_consume_argv(tmp_path, seat="operator", extra=["--limit", "5"])

    assert argv == [
        str(tmp_path / "coordination" / "bin" / "consume-events"),
        "operator",
        "--limit",
        "5",
    ]


def test_builders_fail_when_fixed_writer_absent(tmp_path: Path) -> None:
    with pytest.raises(mailbox.MailboxBindingError, match="unavailable"):
        mailbox.build_publish_argv(
            tmp_path, seat="director", to="operator", kind="status", subject="x"
        )


def test_confirm_requires_typed_yes() -> None:
    assert mailbox.confirm(action="publish", detail="d", prompt_fn=lambda _: "yes\n")
    with pytest.raises(mailbox.MailboxBindingError, match="not authorized"):
        mailbox.confirm(action="publish", detail="d", prompt_fn=lambda _: "no")


def test_confirm_fails_closed_without_terminal() -> None:
    def _no_tty(_: str) -> str:
        raise mailbox.MailboxBindingError("no controlling terminal for interactive confirmation")

    with pytest.raises(mailbox.MailboxBindingError, match="terminal"):
        mailbox.confirm(action="consume", detail="d", prompt_fn=_no_tty)


def test_publish_dry_run_previews_without_effect(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    _writers(tmp_path)
    called: list[list[str]] = []

    rc = mailbox.main(
        [
            "publish",
            "--seat",
            "director",
            "--to",
            "operator",
            "--kind",
            "status",
            "--subject",
            "hello",
            "--dry-run",
        ],
        root=tmp_path,
        stdin_text="body text",
        runner=lambda argv, **_: called.append(argv) or 0,  # type: ignore[func-returns-value]
        prompt_fn=lambda _: "yes",
    )

    payload = json.loads(capsys.readouterr().out)
    assert rc == 0
    assert called == []
    assert payload["argv"][-4:] == ["director", "operator", "status", "hello"]
    assert payload["would_confirm"] is True


def test_publish_confirms_then_delegates(tmp_path: Path) -> None:
    _writers(tmp_path)
    seen: dict[str, object] = {}

    def _runner(argv: list[str], **kwargs: object) -> int:
        seen["argv"] = argv
        seen["input"] = kwargs.get("input")
        return 0

    rc = mailbox.main(
        [
            "publish",
            "--seat",
            "director",
            "--to",
            "operator",
            "--kind",
            "status",
            "--subject",
            "hello",
        ],
        root=tmp_path,
        stdin_text="the body",
        runner=_runner,
        prompt_fn=lambda _: "yes",
    )

    assert rc == 0
    assert seen["argv"][-4:] == ["director", "operator", "status", "hello"]
    assert seen["input"] == "the body"


def test_publish_aborts_when_confirmation_declined(tmp_path: Path) -> None:
    _writers(tmp_path)
    called: list[list[str]] = []

    rc = mailbox.main(
        [
            "publish",
            "--seat",
            "director",
            "--to",
            "operator",
            "--kind",
            "status",
            "--subject",
            "hello",
        ],
        root=tmp_path,
        stdin_text="body",
        runner=lambda argv, **_: called.append(argv) or 0,  # type: ignore[func-returns-value]
        prompt_fn=lambda _: "no",
    )

    assert rc == 2
    assert called == []


def test_consume_confirms_then_delegates(tmp_path: Path) -> None:
    _writers(tmp_path)
    seen: list[list[str]] = []

    rc = mailbox.main(
        ["consume", "--seat", "operator"],
        root=tmp_path,
        stdin_text="",
        runner=lambda argv, **_: seen.append(argv) or 0,  # type: ignore[func-returns-value]
        prompt_fn=lambda _: "yes",
    )

    assert rc == 0
    assert seen[0][-1] == "operator"
    assert seen[0][-2].endswith("consume-events")

def test_publish_skips_confirm_when_live_bound(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _writers(tmp_path)
    seen: dict[str, object] = {}

    def _runner(argv: list[str], **kwargs: object) -> int:
        seen["argv"] = argv
        return 0

    monkeypatch.setenv("CURSOR_SEAT", "director")
    monkeypatch.setenv("CURSOR_OPERATION", "dispatch")
    monkeypatch.setenv("GIT_INDEX_FILE", "/repo/.git/index-cursor-director")
    rc = mailbox.main(
        [
            "publish",
            "--seat",
            "director",
            "--to",
            "operator",
            "--kind",
            "status",
            "--subject",
            "hello",
        ],
        root=tmp_path,
        stdin_text="body",
        runner=_runner,
        prompt_fn=lambda _: (_ for _ in ()).throw(AssertionError("confirm should not run")),
    )
    assert rc == 0
    assert seen["argv"][-4:] == ["director", "operator", "status", "hello"]

