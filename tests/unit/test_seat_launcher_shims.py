"""The `coordination/bin/*-seat` shims must not inherit their interpreter.

Each shim used to `exec /usr/bin/env python3`, so a seat ran under whichever
python3 the caller's PATH happened to offer. Locally that is the repo venv; in a
stripped environment it is macOS system 3.9.6, where the `tomllib` the Codex
launcher imports does not exist. The seat then died on a
ModuleNotFoundError traceback instead of the launcher's own error contract --
an interpreter chosen by ambient state rather than repository policy.
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest


SHIMS = ("codex-seat",)

# The launcher parses TOML and needs `tomllib`, stdlib only since 3.11.
REQUIRED_PYTHON = (3, 11)


def _shim(repo_root: Path, name: str) -> Path:
    return repo_root / "coordination" / "bin" / name


@pytest.mark.parametrize("name", SHIMS)
def test_shim_never_execs_an_ambient_interpreter(repo_root: Path, name: str) -> None:
    """Hermetic half: always runs, needs no subprocess and no interpreter zoo.

    Reads the file RAW. An earlier version stripped comments first, so the
    shims could quote the ambient exec they replaced without tripping it -- and
    that filter was line-based with no shell lexical state, so this stayed green
    against a valid two-line mutation whose second physical line began with `#`
    inside an open quote, closed it, and ran the ambient interpreter:

        HIDDEN='...
        #'; if [ -x "$ROOT/.venv/bin/python" ]; then exec /usr/bin/env python3 ...; fi

    Nothing strips anything now: the shims simply do not name the literal, in
    prose or otherwise, so its presence anywhere in the file is a defect.
    `test_shim_execs_the_venv_interpreter_and_never_the_ambient_one` is the
    behavioural counterpart, since no text check can decide what shell executes.
    """
    text = _shim(repo_root, name).read_text(encoding="utf-8")

    assert "env python3" not in text, name
    assert "exec python3" not in text, name
    # Deterministic selection, then a proof the choice can run the launcher.
    assert '"$ROOT/.venv/bin/python"' in text, name
    assert "version_info >= (3, 11)" in text, name


@pytest.mark.parametrize("name", SHIMS)
def test_shim_execs_the_venv_interpreter_and_never_the_ambient_one(
    repo_root: Path, name: str, tmp_path: Path
) -> None:
    """Behavioural: which interpreter actually ran, not what the text looks like.

    A venv interpreter that announces itself, and a PATH `python3` booby-trapped
    to exit 99. Any path through the shim that reaches the ambient interpreter
    -- including one hidden from a static reader by shell quoting -- shows up as
    99 rather than as the sentinel. The venv is present on purpose: the known
    bypass was conditional on it existing, so a sandbox without one leaves the
    mutation dormant and the test asleep.
    """
    sandbox = tmp_path / "repo"
    (sandbox / "coordination" / "bin").mkdir(parents=True)
    (sandbox / "scripts").mkdir()
    for shim in SHIMS:
        target = sandbox / "coordination" / "bin" / shim
        target.write_bytes(_shim(repo_root, shim).read_bytes())
        target.chmod(0o755)

    venv_python = sandbox / ".venv" / "bin" / "python"
    venv_python.parent.mkdir(parents=True)
    venv_python.write_text(
        "#!/bin/sh\n"
        'case "$1" in\n'
        "  -c) exit 0 ;;\n"
        '  -V|--version) echo "Python 3.99.0" ;;\n'
        '  *) echo "VENV_INTERPRETER_RAN" ;;\n'
        "esac\n",
        encoding="utf-8",
    )
    venv_python.chmod(0o755)

    trap_bin = tmp_path / "trap"
    trap_bin.mkdir()
    trap = trap_bin / "python3"
    trap.write_text(
        '#!/bin/sh\necho "AMBIENT_INTERPRETER_RAN" >&2\nexit 99\n', encoding="utf-8"
    )
    trap.chmod(0o755)

    completed = subprocess.run(
        [str(sandbox / "coordination" / "bin" / name), "--help"],
        cwd=sandbox,
        env={**os.environ, "PATH": f"{trap_bin}:/usr/bin:/bin"},
        capture_output=True,
        text=True,
        check=False,
    )
    output = completed.stdout + completed.stderr

    assert "AMBIENT_INTERPRETER_RAN" not in output, output
    assert completed.returncode != 99, output
    assert "VENV_INTERPRETER_RAN" in completed.stdout, output


@pytest.mark.parametrize("name", SHIMS)
def test_shim_survives_a_stripped_path(repo_root: Path, name: str) -> None:
    """The reproduction: a PATH without the venv must not yield a traceback.

    Pre-fix, `codex-seat` printed
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
