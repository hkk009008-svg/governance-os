"""Each case is a measurement that actually misled someone today.

The point of the fixtures is not that the functions work on tidy inputs. It is
that they refuse the specific readings that looked correct at the time: a
command that failed while its caller printed a reassuring line, the SHA-256 of
an argument that never arrived, and an instrument trusted without ever being
shown a value it should reject.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))

import instrument  # noqa: E402


def test_it_returns_output_from_a_command_that_ran() -> None:
    assert instrument.measured([sys.executable, "-c", "print('42')"]).strip() == "42"


def test_it_refuses_output_from_a_command_that_died() -> None:
    """The probe printed PASS while this exact thing had happened underneath.

    The subprocess exited 1, nobody read the code, and the assertions that
    followed compared a file against itself and reported success.
    """
    with pytest.raises(instrument.InstrumentError, match="exited 1"):
        instrument.measured([sys.executable, "-c", "import sys; sys.exit(1)"])


def test_it_refuses_a_command_that_measured_nothing() -> None:
    """Success with no output is the most credible-looking wrong answer."""
    with pytest.raises(instrument.InstrumentError, match="measured nothing"):
        instrument.measured([sys.executable, "-c", "pass"])

    assert instrument.measured([sys.executable, "-c", "pass"], allow_empty=True) == ""


def test_it_refuses_the_hash_of_nothing() -> None:
    """A shell modifier ate the argument and every revision hashed identically.

    The sweep returned e3b0c442... four times, which read as four real
    mismatches rather than four arguments that never arrived.
    """
    with pytest.raises(instrument.InstrumentError, match="did not arrive"):
        instrument.digest(b"")

    assert instrument.digest(b"x") != instrument.EMPTY_SHA256


def test_it_passes_an_instrument_that_agrees_with_known_values() -> None:
    doubled = instrument.calibrated(lambda value: value * 2, [(2, 4), (0, 0)])

    assert doubled(5) == 10


def test_it_refuses_an_instrument_that_disagrees() -> None:
    """The known-bad direction. An instrument shown only inputs it accepts has
    never demonstrated it can disagree, which is decoration, not a control."""
    with pytest.raises(instrument.InstrumentError, match="disagreed on a known value"):
        instrument.calibrated(lambda value: value * 3, [(2, 4)])
