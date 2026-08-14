"""The seat↔sender authority invariant survives `python -O`.

seat_emit hard-binds the seat into `ev.signer` and then requires the
builder-produced `ev.sender` to agree. That check used to be an `assert`,
whose stripped form under `-O` / PYTHONOPTIMIZE does not raise — it falls
through and RETURNS the event, producing exactly the signer/sender identity
split this module exists to prevent (see its docstring on the
bootstrap_emit.py:50 injection hole). These tests pin the refusal, the
matching case that proves the guard is not simply always firing, and the
optimized-interpreter run that the assert form failed.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

import seat_emit


ROOT = Path(__file__).resolve().parents[2]


def _args(seat: str) -> SimpleNamespace:
    """A candidate_aborted request, the one builder branch that needs no repo."""

    return SimpleNamespace(
        seat=seat,
        fact="candidate_aborted",
        candidate_id="cand-1",
        bus_id="bus-1",
        brief_id="brief-1",
        brief_version=1,
        session="session-1",
    )


def test_builder_sender_disagreeing_with_seat_is_refused() -> None:
    # candidate_aborted stamps sender=pair.coordinator, so asking for it as
    # `operator` is a real mismatch reached without mocking the builder.
    assert seat_emit.SEAT_PAIR["operator"].coordinator != "operator"
    with pytest.raises(ValueError, match=r"builder sender coordinator != seat operator"):
        seat_emit._build_event(_args("operator"))


def test_matching_seat_is_accepted_and_signer_is_bound() -> None:
    # Non-vacuity: the guard must not refuse everything. The coordinator seat
    # matches the stamped sender, so the event is returned with its signer
    # hard-bound to that seat.
    event = seat_emit._build_event(_args("coordinator"))
    assert event.sender == "coordinator"
    assert event.signer.startswith("coordinator:")
    assert event.signer.endswith(":session-1")


def test_invariant_still_refuses_under_optimized_interpreter() -> None:
    """Evasion control: `-O` strips asserts, so the assert form passed here."""

    program = (
        "import sys; sys.path.insert(0, %r)\n"
        "from types import SimpleNamespace\n"
        "import seat_emit\n"
        "assert __debug__ is False, 'interpreter is not optimized'\n"
        "a = SimpleNamespace(seat='operator', fact='candidate_aborted',\n"
        "                    candidate_id='cand-1', bus_id='bus-1',\n"
        "                    brief_id='brief-1', brief_version=1,\n"
        "                    session='session-1')\n"
        "try:\n"
        "    seat_emit._build_event(a)\n"
        "except ValueError:\n"
        "    print('REFUSED')\n"
        "else:\n"
        "    print('RETURNED')\n"
    ) % str(ROOT / "scripts")
    result = subprocess.run(
        [sys.executable, "-O", "-c", program],
        capture_output=True,
        text=True,
        cwd=str(ROOT),
        check=True,
    )
    # `assert __debug__ is False` inside the child is itself stripped by -O, so
    # confirm the optimization separately rather than trusting that line.
    assert (
        subprocess.run(
            [sys.executable, "-O", "-c", "import sys; sys.exit(0 if not __debug__ else 1)"],
            check=False,
        ).returncode
        == 0
    ), "child interpreter did not actually run optimized"
    assert result.stdout.strip() == "REFUSED"
