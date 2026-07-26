"""The `coordination/bin/*-seat` shims must not inherit their interpreter.

Each shim used to `exec /usr/bin/env python3`, so a seat ran under whichever
python3 the caller's PATH happened to offer. Locally that is the repo venv; in a
stripped environment it is macOS system 3.9.6, where the `tomllib` the AGY and
Codex launchers import does not exist. The seat then died on a
ModuleNotFoundError traceback instead of the launcher's own error contract --
an interpreter chosen by ambient state, the same shape as the flags the AGY
launcher was fixed for emitting.
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest


SHIMS = ("agy-seat", "codex-seat", "cursor-seat")

# Both launchers that parse TOML need `tomllib`, stdlib only since 3.11. The
# floor is repo-wide rather than per-shim so a seat cannot run on an interpreter
# its siblings refuse.
REQUIRED_PYTHON = (3, 11)


def _shim(repo_root: Path, name: str) -> Path:
    return repo_root / "coordination" / "bin" / name


def _executable_lines(path: Path) -> str:
    """The shim with comments removed.

    Checked against code rather than the whole file on purpose: each shim
    *documents* the `exec /usr/bin/env python3` it replaced, and a naive
    substring search over the text matches that prose and reports the fix as
    the defect.
    """
    return "\n".join(
        line
        for line in path.read_text(encoding="utf-8").splitlines()
        if not line.lstrip().startswith("#")
    )


@pytest.mark.parametrize("name", SHIMS)
def test_shim_never_execs_an_ambient_interpreter(repo_root: Path, name: str) -> None:
    """Hermetic half: always runs, needs no subprocess and no interpreter zoo."""
    code = _executable_lines(_shim(repo_root, name))

    assert "env python3" not in code, name
    assert "exec python3" not in code, name
    # Deterministic selection, then a proof the choice is adequate.
    assert '"$ROOT/.venv/bin/python"' in code, name
    assert "version_info >= (3, 11)" in code, name


@pytest.mark.parametrize("name", SHIMS)
def test_shim_survives_a_stripped_path(repo_root: Path, name: str) -> None:
    """The reproduction: a PATH without the venv must not yield a traceback.

    Pre-fix, `agy-seat` and `codex-seat` printed
    `ModuleNotFoundError: No module named 'tomllib'` here. Post-fix the shim
    either finds the repo venv or refuses in its own words; both are acceptable,
    a Python traceback is not.
    """
    completed = subprocess.run(
        [str(_shim(repo_root, name)), "--help"],
        cwd=repo_root,
        env={**os.environ, "PATH": "/usr/bin:/bin"},
        capture_output=True,
        text=True,
        check=False,
    )
    output = completed.stdout + completed.stderr

    assert "ModuleNotFoundError" not in output, output
    assert "Traceback (most recent call last)" not in output, output


@pytest.mark.parametrize("name", SHIMS)
def test_shim_refuses_an_interpreter_below_the_floor(
    repo_root: Path, name: str, tmp_path: Path
) -> None:
    """An inadequate interpreter is refused in words, and never reached.

    The fake reports itself as too old and exits 99 if it is ever handed the
    launcher script, so this doubles as its own negative control: with the
    version guard removed the shim execs through and the exit code is 99 rather
    than the launcher's refusal code of 2.
    """
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    fake_python = fake_bin / "python3"
    fake_python.write_text(
        "#!/bin/sh\n"
        'case "$*" in\n'
        "  *version_info*) exit 1 ;;\n"
        '  -V|--version) echo "Python 3.9.0"; exit 0 ;;\n'
        '  *) echo "guard bypassed: launcher was executed" >&2; exit 99 ;;\n'
        "esac\n",
        encoding="utf-8",
    )
    fake_python.chmod(0o755)

    # A tree with the shims but no `.venv`, so PATH is the only source.
    sandbox = tmp_path / "repo"
    (sandbox / "coordination").mkdir(parents=True)
    (sandbox / "scripts").mkdir()
    for shim in SHIMS:
        target = sandbox / "coordination" / "bin" / shim
        target.parent.mkdir(exist_ok=True)
        target.write_bytes(_shim(repo_root, shim).read_bytes())
        target.chmod(0o755)
    assert not (sandbox / ".venv").exists()

    completed = subprocess.run(
        [str(sandbox / "coordination" / "bin" / name), "--help"],
        cwd=sandbox,
        env={**os.environ, "PATH": f"{fake_bin}:/usr/bin:/bin"},
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 2, completed.stdout + completed.stderr
    assert "3.11+" in completed.stderr, completed.stderr
    assert "guard bypassed" not in completed.stderr, completed.stderr
