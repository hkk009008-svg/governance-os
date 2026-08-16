#!/usr/bin/env python3
"""Refuse a reading whose instrument never checked that it read anything.

Five measurements failed in one day, and not one of them looked like a
failure. A probe printed "DB BYTES PRESERVED: True" while the subprocess it was
measuring had exited 1, so the reassuring line described a comparison of a file
against itself. A hash sweep returned the SHA-256 of empty input for every
revision, because a shell modifier had eaten the argument, and four phantom
mismatches were one keystroke from being reported as findings. Both readings
were confident, well formed, and about nothing.

The shared defect is that each instrument reported a result without checking
its own preconditions. So each function here refuses rather than returns:
`measured` refuses output from a command that failed or said nothing, `digest`
refuses the empty hash, and `calibrated` refuses an instrument that disagrees
with a value whose answer is already known.

Advisory tooling: it gates nothing and grants nothing.
"""

from __future__ import annotations

import hashlib
import subprocess
from collections.abc import Callable, Iterable
from pathlib import Path
from typing import Any

EMPTY_SHA256 = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"


class InstrumentError(RuntimeError):
    """A reading that must not be used as evidence."""


def measured(
    command: list[str], *, cwd: Path | None = None, allow_empty: bool = False
) -> str:
    """Stdout of a command, or an exception -- never a quiet empty string.

    The probe that reported success while its subprocess died did so because
    nobody looked at the return code, and the surrounding assertions then
    compared a file with itself. Empty output is refused by default for the
    same reason: a command that printed nothing has usually not measured
    anything, and an empty string is the most credible-looking wrong answer
    there is.
    """

    result = subprocess.run(
        command, cwd=cwd, capture_output=True, text=True, check=False
    )
    if result.returncode != 0:
        raise InstrumentError(
            f"{command[0]} exited {result.returncode}: {result.stderr.strip()[:200]}"
        )
    if not allow_empty and not result.stdout.strip():
        raise InstrumentError(f"{command[0]} succeeded but measured nothing")
    return result.stdout


def digest(data: bytes) -> str:
    """SHA-256 of real bytes, refusing the hash of nothing.

    e3b0c442... is what an eaten argument produces, and it is identical for
    every input that never arrived, so a sweep returning it looks like a set of
    genuine mismatches. Naming the constant makes the tell mechanical.
    """

    if not data:
        raise InstrumentError("refusing to digest empty input; the argument did not arrive")
    return hashlib.sha256(data).hexdigest()


def calibrated(
    instrument: Callable[[Any], Any], cases: Iterable[tuple[Any, Any]]
) -> Callable[[Any], Any]:
    """Return the instrument only if it agrees with answers already known.

    Both directions are required by the caller supplying them: an instrument
    shown only inputs it accepts has never demonstrated it can disagree, which
    is the difference between a control and a decoration.
    """

    for value, expected in cases:
        actual = instrument(value)
        if actual != expected:
            raise InstrumentError(
                f"instrument disagreed on a known value: {value!r} gave {actual!r}, expected {expected!r}"
            )
    return instrument
