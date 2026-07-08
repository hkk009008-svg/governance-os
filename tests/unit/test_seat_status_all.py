from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


SEAT_STATUS_PATH = (
    Path(__file__).resolve().parents[2]
    / ".agents/skills/four-seat-protocol/scripts/seat_status.py"
)


def _load_seat_status():
    spec = importlib.util.spec_from_file_location("seat_status_under_test", SEAT_STATUS_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _write(path: Path, body: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")
    return path


def _fake_run_for_all(cmd, cwd=None):
    del cwd
    key = tuple(cmd)
    responses = {
        ("git", "log", "-1", "--format=%h  %s"): (0, "abc1234  feat(protocol): status view", ""),
        ("git", "rev-parse", "--abbrev-ref", "HEAD"): (0, "protocol-status-visibility", ""),
        ("git", "rev-list", "--left-right", "--count", "origin/main...HEAD"): (0, "0 1", ""),
        ("git", "log", "--oneline", "-1"): (0, "abc1234 feat(protocol): status view", ""),
        (
            sys.executable,
            "scripts/protocol_capacity_board.py",
            "--wave",
            "2",
        ): (
            0,
            "# Protocol Capacity Board\n"
            "wave: 2\n"
            "valid: true\n"
            "packet state: active\n"
            "\n"
            "NEXT LAWFUL ACTIONS\n"
            "coordinator\n"
            "  startup: refresh board\n"
            "  packet: route-1\n"
            "  deps: none\n"
            "  next: wait for operator GO\n"
            "  stop: stop when routed mail changes\n",
            "",
        ),
    }
    return responses.get(key, (127, "", f"unexpected command: {cmd!r}"))


def test_main_all_prints_shared_sections_capacity_and_latest_handoffs(
    tmp_path: Path,
    monkeypatch,
    capsys,
):
    seat_status = _load_seat_status()

    for seat in seat_status.protocol_mailbox.RECEIVING_SEATS:
        _write(
            tmp_path / "coordination/mailbox/seen" / f"{seat}.txt",
            "2026-07-08T00:00:00Z\n",
        )
        token = "coordinator" if seat.startswith("coordinator") else seat
        _write(
            tmp_path / "docs" / f"HANDOFF-{token}-2026-07-09-{seat}.md",
            f"# {seat}\n",
        )
    _write(
        tmp_path
        / "coordination/mailbox/sent/2026-07-09T09-00-00Z-director-to-all-status.md",
        "# status\n",
    )
    for seat in seat_status.protocol_mailbox.SEATS:
        _write(
            tmp_path / "coordination/presence" / f"{seat}-heartbeat.ts",
            "2026-07-09T08:55:00Z abc1234\n",
        )

    monkeypatch.setattr(seat_status, "repo_root", lambda: str(tmp_path))
    monkeypatch.setattr(seat_status, "run", _fake_run_for_all)

    rc = seat_status.main(["--all", "--wave", "2", "--commits", "1"])
    out = capsys.readouterr().out

    assert rc == 0
    assert out.count("── HEAD ") == 1
    assert "NEXT LAWFUL ACTIONS" in out
    assert "next: wait for operator GO" in out
    assert "stop: stop when routed mail changes" in out
    assert "latest handoffs" in out
    for seat in seat_status.protocol_mailbox.RECEIVING_SEATS:
        assert seat in out
        assert f"{seat}:" in out


def test_main_single_seat_still_accepts_positional_seat_argument(
    tmp_path: Path,
    monkeypatch,
    capsys,
):
    seat_status = _load_seat_status()

    _write(
        tmp_path / "coordination/mailbox/seen/director.txt",
        "2026-07-08T00:00:00Z\n",
    )
    _write(
        tmp_path
        / "coordination/mailbox/sent/2026-07-09T09-00-00Z-operator-to-director-note.md",
        "# note\n",
    )
    for seat in seat_status.protocol_mailbox.SEATS:
        _write(
            tmp_path / "coordination/presence" / f"{seat}-heartbeat.ts",
            "2026-07-09T08:55:00Z abc1234\n",
        )

    monkeypatch.setattr(seat_status, "repo_root", lambda: str(tmp_path))
    monkeypatch.setattr(seat_status, "run", _fake_run_for_all)

    rc = seat_status.main(["director", "--commits", "1"])
    out = capsys.readouterr().out

    assert rc == 0
    assert "SEAT STATUS — director" in out
    assert "mailbox — unread for 'director'" in out
