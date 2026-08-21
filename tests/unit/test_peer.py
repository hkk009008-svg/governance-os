"""The peer mechanism: argv it builds, and facts it refuses to invent.

Nothing here launches a provider. Backends are exercised with `shutil.which`
monkeypatched and `run()` given a fake runner, so every assertion is about
this repository's behaviour rather than a vendor's availability.

The load-bearing test is test_a_receipt_never_reports_the_requested_model:
the whole point of a receipt is that it disagrees with the author when the
author is wrong, and a receipt that echoed the --model flag back would agree
by construction.
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

import peer
import peer_backends


def _spec(tmp_path: Path, side: str, **overrides) -> peer_backends.Spec:
    fields = dict(
        side=side, role="peer", task="t1", cwd=tmp_path, scratch=tmp_path,
        model=None, read_only=True, max_usd=1.0, timeout_s=30,
        invocation_id="0",
    )
    fields.update(overrides)
    return peer_backends.Spec(**fields)


@pytest.fixture(autouse=True)
def peers_on_path(monkeypatch):
    monkeypatch.setattr(
        peer_backends.shutil, "which",
        lambda name: f"/fake/bin/{name}" if name in
        {"claude", "codex", "claude-agy", "codex-agy"} else None,
    )


def test_claude_argv_is_headless_json_and_budget_capped(tmp_path: Path) -> None:
    argv = peer_backends.build(_spec(tmp_path, "claude", model="opus")).argv

    assert argv[0] == "/fake/bin/claude"
    assert "--print" in argv
    assert argv[argv.index("--output-format") + 1] == "json"
    assert argv[argv.index("--model") + 1] == "opus"
    assert argv[argv.index("--max-budget-usd") + 1] == "1.00"
    assert argv[argv.index("--permission-mode") + 1] == "plan"


def test_codex_argv_is_headless_jsonl_and_sandboxed(tmp_path: Path) -> None:
    invocation = peer_backends.build(_spec(tmp_path, "codex", model="gpt-5-codex"))

    assert invocation.argv[:2] == ["/fake/bin/codex", "exec"]
    assert "--json" in invocation.argv
    assert invocation.argv[invocation.argv.index("--sandbox") + 1] == "read-only"
    assert invocation.argv[-1] == "-", "the prompt must arrive on stdin"
    assert invocation.last_message_file


@pytest.mark.parametrize(
    "side,flag,written",
    [("claude", "--permission-mode", "acceptEdits"), ("codex", "--sandbox", "workspace-write")],
)
def test_write_mode_widens_exactly_one_flag(tmp_path: Path, side, flag, written) -> None:
    argv = peer_backends.build(_spec(tmp_path, side, read_only=False)).argv

    assert argv[argv.index(flag) + 1] == written


def test_a_missing_binary_fails_closed(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(peer_backends.shutil, "which", lambda name: None)

    with pytest.raises(peer_backends.PeerError, match="not on PATH"):
        peer_backends.build(_spec(tmp_path, "codex"))


def test_agy_is_advisory_and_role_closed(tmp_path: Path) -> None:
    invocation = peer_backends.build(_spec(tmp_path, "agy", role="challenge"))

    assert invocation.advisory is True
    assert invocation.argv[1] == "challenge"

    with pytest.raises(peer_backends.PeerError, match="agy role must be one of"):
        peer_backends.build(_spec(tmp_path, "agy", role="verdict"))


def test_agy_dispatches_to_the_wrapper_for_the_running_side(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("PIPELINE_SIDE", "codex")
    assert peer_backends.build(_spec(tmp_path, "agy", role="map")).argv[0].endswith("codex-agy")

    monkeypatch.setenv("PIPELINE_SIDE", "claude")
    assert peer_backends.build(_spec(tmp_path, "agy", role="map")).argv[0].endswith("claude-agy")


@pytest.mark.parametrize(
    "payload,expected",
    [
        ({"model": "claude-opus-5", "result": "ok"}, "claude-opus-5"),
        ({"modelUsage": {"claude-sonnet-5": {}}, "result": "ok"}, "claude-sonnet-5"),
        ({"result": "ok"}, None),
    ],
)
def test_claude_model_comes_from_its_own_output(payload, expected) -> None:
    model, _cost, result, notes = peer_backends.reported_result("claude", json.dumps(payload))

    assert model == expected
    assert result == "ok"
    if expected is None:
        assert notes == [] or all(isinstance(note, str) for note in notes)


def test_unparseable_claude_output_is_a_note_not_a_guess() -> None:
    model, _cost, _result, notes = peer_backends.reported_result("claude", "not json")

    assert model is None
    assert any("not one JSON object" in note for note in notes)


def test_codex_model_is_found_in_a_nested_event() -> None:
    stream = "\n".join([
        json.dumps({"type": "session.created", "session": {"model": "gpt-5-codex"}}),
        json.dumps({"type": "turn.completed"}),
    ])

    model, _cost, _result, notes = peer_backends.reported_result("codex", stream)

    assert model == "gpt-5-codex"
    assert notes == []


def test_codex_without_a_model_field_says_so() -> None:
    model, _cost, _result, notes = peer_backends.reported_result(
        "codex", json.dumps({"type": "turn.completed"})
    )

    assert model is None
    assert any("no codex event carried a model field" in note for note in notes)


def test_a_receipt_never_reports_the_requested_model(tmp_path: Path) -> None:
    """The control the whole receipt exists for.

    A receipt that echoed --model back would agree with its author by
    construction and could never contradict a false claim about who reviewed.
    Asked for one model, told another by the peer, the receipt must record
    what the peer said; told nothing, it must record nothing.
    """

    def contradicting(argv, **kwargs):
        return subprocess.CompletedProcess(
            argv, 0, json.dumps({"model": "claude-haiku-4-5", "result": "done"}), ""
        )

    outcome = peer.run(
        _spec(tmp_path, "claude", model="claude-opus-5"), "prompt", runner=contradicting
    )
    assert outcome.model_reported == "claude-haiku-4-5"

    def silent(argv, **kwargs):
        return subprocess.CompletedProcess(argv, 0, json.dumps({"result": "done"}), "")

    quiet = peer.run(
        _spec(tmp_path, "claude", model="claude-opus-5"), "prompt", runner=silent
    )
    assert quiet.model_reported is None, "an unreported model must not fall back to the request"


def test_a_timeout_is_a_recorded_absence_not_a_result(tmp_path: Path) -> None:
    def times_out(argv, **kwargs):
        raise subprocess.TimeoutExpired(argv, 30)

    outcome = peer.run(_spec(tmp_path, "codex"), "prompt", runner=times_out)

    assert outcome.exit_code == 124
    assert outcome.result == ""
    assert any("exceeded --timeout" in note for note in outcome.notes)


def test_receipts_are_sequenced_and_hash_what_ran(tmp_path: Path) -> None:
    def ok(argv, **kwargs):
        return subprocess.CompletedProcess(argv, 0, json.dumps({"result": "done"}), "")

    outcome = peer.run(_spec(tmp_path, "claude"), "the prompt", runner=ok)
    first = peer.write_receipt(tmp_path, outcome, "2026-08-21T00:00:00Z")
    second = peer.write_receipt(tmp_path, outcome, "2026-08-21T00:00:01Z")

    assert first.name == "0001-claude.json"
    assert second.name == "0002-claude.json"
    payload = json.loads(first.read_text(encoding="utf-8"))
    assert payload["schema"] == "peer-receipt/1"
    assert payload["task"] == "t1"
    assert payload["exit_code"] == 0
    assert len(payload["argv_sha256"]) == 64
    assert len(payload["prompt_sha256"]) == 64
    assert payload["advisory"] is False


def test_a_failing_peer_keeps_its_stderr_in_the_receipt(tmp_path: Path) -> None:
    def fails(argv, **kwargs):
        return subprocess.CompletedProcess(argv, 3, "", "auth expired")

    outcome = peer.run(_spec(tmp_path, "codex"), "prompt", runner=fails)

    assert outcome.exit_code == 3
    assert any("auth expired" in note for note in outcome.notes)


def test_dry_run_launches_nothing(tmp_path: Path, monkeypatch, capsys) -> None:
    def explode(*args, **kwargs):  # pragma: no cover - must never run
        raise AssertionError("dry run launched a provider")

    monkeypatch.setattr(peer.subprocess, "run", explode)

    assert peer.main(
        ["ask", "codex", "--task", "t", "--prompt", "hi", "--dry-run"]
    ) == 0
    assert "dry run: nothing launched" in capsys.readouterr().err
