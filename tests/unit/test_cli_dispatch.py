"""The one command surface: what it dispatches, and what it refuses.

`bin/pipeline` turns a file path into a verb. Two defects found on 2026-08-22
were both about the dispatcher being too permissive: a typo silently widened
to the parent verb and ran a gate, and --help performed the action it was
asked to describe.
"""
from __future__ import annotations

from pathlib import Path

import cli


def test_an_unknown_subcommand_is_refused_not_silently_widened(capsys) -> None:
    """A typo must not run the gate it was aiming at.

    Measured 2026-08-22 before the fix: `pipeline check bogus` fell through to
    the bare `check` verb, ran the entire governance aggregate, and exited 0 --
    so a mistyped subcommand reported success for a check nobody asked for.
    """

    assert cli.main(["check", "bogus"]) == 2
    error = capsys.readouterr().err
    assert "unknown subcommand 'bogus'" in error
    assert "coordination" in error, "the refusal must name the real subcommands"


def test_help_describes_and_never_denies_a_flag_that_works(capsys) -> None:
    """--help must not perform the action, and must not deny a working flag.

    `pipeline check --help` first ran the full aggregate and exited 0. The fix
    routed it through an _ARGLESS table printing "Takes no arguments" -- true
    for two gates, false for two others, hiding `check --fast` and
    `check arch --base REF`. Help that denies a real flag is the same class of
    false signal as help that performs the action.
    """

    assert cli.main(["check", "--help"]) == 0
    out = capsys.readouterr().out
    assert "--fast" in out, "help must name the mode that exists"
    assert "PROJECT SMOKE" not in out, "the gate must not have run"

    assert cli.main(["check", "ceremony", "--help"]) == 0
    out = capsys.readouterr().out
    assert "Takes no arguments" in out
    assert "CEREMONY CHECK" not in out, "the gate must not have run"


def test_argless_names_only_commands_that_truly_take_nothing() -> None:
    """The interception is a claim about the module, so ask the module.

    Two of the four original entries were wrong and each concealed a working
    flag instead of failing loudly. A module that builds an ArgumentParser
    answers --help better than this table can, so listing it is always a
    defect.
    """

    root = Path(cli.__file__).resolve().parent
    for key in cli._ARGLESS:
        module = cli._MODULE_COMMANDS[key][0]
        source = (root / f"{module}.py").read_text(encoding="utf-8")
        assert "ArgumentParser" not in source, f"{module} can answer --help itself"

    for key in (("check",), ("check", "arch")):
        assert key not in cli._ARGLESS, "these two hid --fast and --base REF"


def test_the_banner_does_not_overclaim_help_coverage() -> None:
    """The usage text must describe what the dispatcher actually does."""

    usage = cli._usage()

    assert "Most commands accept their own --help" in usage
    assert "Every command accepts its own --help" not in usage


def test_a_known_subcommand_still_dispatches() -> None:
    """Reversion control: the refusal must not swallow real subcommands."""

    for key in (("check", "arch"), ("check", "coordination"), ("peer", "receipts")):
        resolved = cli._resolve(list(key))
        assert resolved is not None, key
        assert resolved.name.split()[0] == key[0]
        assert resolved.module, key


def test_a_delegated_group_reaches_its_module(capsys) -> None:
    """Regression: `pipeline peer ask` was refused against an empty expected-set.

    ("peer", None) declares that the MODULE owns every subcommand under `peer`.
    Treating `peer` as an enumerated group made every real subcommand unknown --
    five independent readers hit it within minutes of it landing.
    """

    for sub in ("ask", "receipts"):
        resolved = cli._resolve(["peer", sub])
        assert resolved is not None, sub
        assert resolved.module == "peer"
        assert resolved.rest[0] == sub, "the subcommand must reach the module"
