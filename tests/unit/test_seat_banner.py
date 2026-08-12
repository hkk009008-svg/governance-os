"""Coverage for scripts/seat_banner.py (previously untested live CLI)."""

from __future__ import annotations

import seat_banner


def test_banner_renders_the_six_field_contract(capsys) -> None:
    code = seat_banner.main(
        [
            "--objective", "harden the kernel",
            "--permissions", "director in worktree",
            "--scope", "scripts/",
            "--verify", "pytest tests -q",
            "--done", "green gate",
        ]
    )
    assert code == 0
    out = capsys.readouterr().out
    for marker in ("Seat contract:", "S-OBJ: harden the kernel", "S-DONE: green gate"):
        assert marker in out


def test_require_complete_rejects_missing_fields(capsys) -> None:
    code = seat_banner.main(["--objective", "only this", "--require-complete"])
    assert code == 2
    err = capsys.readouterr().err
    assert "missing contract fields" in err
    # The unset required fields are named so the caller can fix them.
    for field in ("permissions", "scope", "verify", "done"):
        assert field in err


def test_defaults_render_unset_without_require_complete(capsys) -> None:
    code = seat_banner.main([])
    assert code == 0
    assert "(unset)" in capsys.readouterr().out
