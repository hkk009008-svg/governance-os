from __future__ import annotations

import json
from pathlib import Path

import cursor_seat_launcher as launcher


def test_status_reports_all_app_seats_without_launching(tmp_path: Path) -> None:
    worktree = tmp_path / "director"
    worktree.mkdir()
    registry = tmp_path / "registry.json"
    registry.write_text(
        json.dumps(
            {
                "version": 1,
                "bindings": {
                    "director": {
                        "root": str(worktree),
                        "branch": "cursor-seat/director",
                        "conversation_id": "conversation-1",
                        "model_id": "composer-2.5",
                    }
                },
            }
        ),
        encoding="utf-8",
    )

    document = launcher.status_document(registry)

    assert set(document) == {
        "director",
        "director2",
        "operator",
        "operator2",
        "coordinator",
    }
    assert document["director"]["bound"] is True
    assert document["director"]["worktree_exists"] is True
    assert document["operator"] == {"bound": False}


def test_readiness_describes_app_runtime(capsys) -> None:
    assert launcher.main(["readiness"]) == 0
    output = capsys.readouterr().out
    assert "Cursor Desktop" in output
    assert "cursor-seat/" in output
    assert "cursor-agent" not in output


def test_status_command_is_read_only(capsys, tmp_path: Path) -> None:
    registry = tmp_path / "registry.json"
    registry.write_text(
        json.dumps({"version": 1, "bindings": {}}),
        encoding="utf-8",
    )
    assert launcher.main(["--registry", str(registry), "status"]) == 0
    assert json.loads(capsys.readouterr().out)["director"] == {"bound": False}
