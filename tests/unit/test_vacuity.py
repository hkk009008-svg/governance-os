"""Both directions, on a tree built for the purpose.

The runner's own claim is that it can tell a real control from a vacuous one.
Showing it only real controls would prove nothing, so the fixtures include a
control shaped exactly like the two that fooled us today: it exercises the
guarded function directly, while the production seam it is supposed to defend
has no guard at all.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))

import vacuity  # noqa: E402

_SOURCE = '''
def guard(value):
    if value < 0:
        raise ValueError("negative")
    return value


def production(value):
    guard(value)
    return value
'''

_HONEST = '''
import subject


def test_production_refuses():
    try:
        subject.production(-1)
    except ValueError:
        return
    raise AssertionError("production accepted a negative")
'''

_VACUOUS = '''
import subject


def test_guard_refuses():
    try:
        subject.guard(-1)
    except ValueError:
        return
    raise AssertionError("guard accepted a negative")
'''


def _tree(tmp_path: Path, control: str) -> Path:
    root = tmp_path / "tree"
    root.mkdir()
    (root / "subject.py").write_text(_SOURCE)
    (root / "test_control.py").write_text(control)
    return root


def test_it_proves_a_control_that_guards_the_production_seam(tmp_path: Path) -> None:
    """Known-good: the control goes through production, so removing the call reddens it."""
    root = _tree(tmp_path, _HONEST)

    result = vacuity.prove_control_can_fail(
        root, "subject.py", "    guard(value)\n", "test_control.py"
    )

    assert result["verdict"] == "proved"


def test_it_catches_a_control_that_only_exercises_the_guard(tmp_path: Path) -> None:
    """Known-bad, and the exact shape of today's two vacuous controls.

    The guard still refuses when called directly, so the control stays green
    while the production seam ships unguarded. A runner that reported this as
    proved would be worse than no runner.
    """
    root = _tree(tmp_path, _VACUOUS)

    with pytest.raises(vacuity.VacuityError, match="VACUOUS"):
        vacuity.prove_control_can_fail(
            root, "subject.py", "    guard(value)\n", "test_control.py"
        )


def test_it_refuses_a_bypass_the_seam_does_not_contain(tmp_path: Path) -> None:
    """A declared bypass that matches nothing would silently prove the control
    against an unmodified tree, which is the vacuity it exists to detect."""
    root = _tree(tmp_path, _HONEST)

    with pytest.raises(vacuity.VacuityError, match="does not contain"):
        vacuity.prove_control_can_fail(
            root, "subject.py", "    absent(value)\n", "test_control.py"
        )
