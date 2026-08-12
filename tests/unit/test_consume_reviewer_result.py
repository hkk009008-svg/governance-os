"""Adversarial-surface tests for scripts/consume_reviewer_result.py (ADR-027/028/032).

This module is the anti-fabrication reviewer-result consumer: it parses a
`reviewer-result/1` block out of an UNTRUSTED mailbox event and re-executes the
pytest commands the reviewer *claims* it ran to catch a fabricated summary. The
returned argv is handed straight to subprocess.run(argv) (no shell), so the command
sanitizer (safe_pytest_argv) is a genuine adversarial surface — these tests pin what
it ACCEPTS and REJECTS, the parser's fail-closed contract, and the ci_smoke entry.

Tests assert what the code ACTUALLY does. Where behavior diverged from the task's
stated expectation (bare `pytest ...` is REJECTED, not accepted — a deliberate C1
hardening: a bare basename is PATH-resolved, the redirection vector) the test pins
the real, stricter behavior. No dangerous-accept was found (see module-level report).
"""
from __future__ import annotations

from pathlib import Path

import pytest

import consume_reviewer_result as crr


# ---------------------------------------------------------------------------
# 1. Command sanitizer — safe_pytest_argv (the subprocess.run gate)
# ---------------------------------------------------------------------------

# ACCEPTED: the repo idioms + structurally-safe pytest invocations. Every launcher
# carries a path separator (never PATH-resolved) and is either a python-family
# interpreter immediately followed by `-m pytest`, or a `pytest` console script.
_ACCEPT = [
    # the canonical repo idiom
    "env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit -q",
    # pytest console script run directly (path-separated basename)
    ".venv/bin/pytest tests/unit -q",
    # python -m pytest with no targets
    ".venv/bin/python -m pytest",
    # versioned interpreter basename
    ".venv/bin/python3 -m pytest tests",
    # multiple `-u NAME` unsets in the env prefix
    "env -u A -u B .venv/bin/python -m pytest tests",
    # relative path launcher (has a separator)
    "./bin/python -m pytest tests",
    # arbitrary pytest flags after the head are passed through
    ".venv/bin/python -m pytest -p no:cacheprovider tests",
]

# REJECTED (returns None -> NEVER executed): injection shapes, non-pytest commands,
# PATH-resolvable bare basenames, env assignment/option smuggling, glued flags.
_REJECT = [
    # --- command injection metacharacters (never run via a shell) ---
    "pytest; rm -rf /",
    ".venv/bin/pytest && echo pwned",
    ".venv/bin/pytest | tee /tmp/log",
    ".venv/bin/pytest $(whoami)",
    ".venv/bin/pytest `whoami`",
    ".venv/bin/pytest > /tmp/out",
    "pytest\nrm -rf /",              # embedded newline
    ".venv/bin/pytest \\ evil",      # backslash metachar
    # --- bare basename: PATH-resolved -> the redirection vector (C1 hardening) ---
    "pytest tests/unit",             # NB: bare pytest is REJECTED, not accepted
    "python -m pytest",
    "env -u GIT_INDEX_FILE pytest tests",   # bare pytest even behind the env idiom
    # --- non-pytest / arbitrary binaries ---
    "git status",
    ".venv/bin/python evil.py pytest",       # python NOT followed by `-m pytest`
    ".venv/bin/pythonista -m pytest tests",  # launcher only prefixes 'python'
    ".venv/bin/mypytest tests",              # launcher only suffixes 'pytest'
    ".venv/bin/python -mpytest tests",       # glued -mpytest, not `-m pytest`
    # --- env prefix abuse: assignments / options / non-bare `env` ---
    "env PATH=/tmp/evil pytest",             # NAME=value assignment (ACE vector) refused
    "env -u X ./evil pytest",                # env launcher is not python/pytest
    "env -i .venv/bin/python -m pytest",     # residual env option after -u strip
    "/usr/bin/env .venv/bin/python -m pytest tests",  # path-y `env` is not the bare-word prefix
    # --- degenerate ---
    "",
    "env",
]


@pytest.mark.parametrize("command", _ACCEPT)
def test_sanitizer_accepts_repo_idioms(command: str) -> None:
    argv = crr.safe_pytest_argv(command)
    assert argv is not None, f"expected ACCEPT, got None for {command!r}"
    # An accepted argv is exactly shlex.split of the input (no rewriting).
    import shlex

    assert argv == shlex.split(command)


@pytest.mark.parametrize("command", _REJECT)
def test_sanitizer_rejects_injection_and_non_pytest(command: str) -> None:
    assert crr.safe_pytest_argv(command) is None, f"expected REJECT for {command!r}"


def test_sanitizer_accepted_launcher_always_has_path_separator() -> None:
    # The core C1 invariant: no accepted invocation launches a PATH-resolved basename.
    for command in _ACCEPT:
        argv = crr.safe_pytest_argv(command)
        launcher = crr._pytest_launcher(argv)
        assert "/" in launcher or "\\" in launcher, command


# ---------------------------------------------------------------------------
# 2. Target confinement — recheck_commands skips out-of-repo / unsafe pins
#    (the second defense layer: safe_pytest_argv vets the INVOCATION, this
#    confines the TARGET so an untrusted conftest can't be auto-imported).
# ---------------------------------------------------------------------------

def test_target_escaping_repo_is_never_executed(repo_root: Path) -> None:
    # Structurally valid argv, but the target resolves outside repo_root.
    argv = crr.safe_pytest_argv(".venv/bin/python -m pytest /tmp/evil")
    assert argv is not None                      # invocation looks safe...
    assert crr._target_escapes_repo(argv, repo_root)  # ...but the target escapes

    calls: list = []
    result = {"commands": [{"command": ".venv/bin/python -m pytest /tmp/evil",
                            "summary": "1 passed"}]}
    crr.recheck_commands(result, repo_root, run=lambda a, cwd: calls.append(a) or (0, ""))
    assert calls == []  # never executed


def test_unsafe_command_is_never_executed(repo_root: Path) -> None:
    calls: list = []
    result = {"commands": [{"command": "git status; rm -rf /", "summary": "x"}]}
    findings = crr.recheck_commands(
        result, repo_root, run=lambda a, cwd: calls.append(a) or (0, "")
    )
    assert calls == [] and findings == []


# ---------------------------------------------------------------------------
# 3. Fabrication detection — reported summary/exit vs the re-run
# ---------------------------------------------------------------------------

_GOOD_CMD = "env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit -q"


def test_fabricated_summary_is_flagged(repo_root: Path) -> None:
    result = {"commands": [{"command": _GOOD_CMD, "exit_code": 0,
                            "summary": "99 passed in 1s"}]}
    findings = crr.recheck_commands(
        result, repo_root, run=lambda a, cwd: (0, "1 passed in 0.1s")
    )
    assert len(findings) == 1
    assert findings[0].reported_summary == {"passed": 99}
    assert findings[0].actual_summary == {"passed": 1}


def test_honest_summary_is_not_flagged(repo_root: Path) -> None:
    # Duration + warnings differ but outcome counts match -> honest, no finding.
    result = {"commands": [{"command": _GOOD_CMD, "exit_code": 0,
                            "summary": "1 passed, 2 warnings in 9s"}]}
    findings = crr.recheck_commands(
        result, repo_root, run=lambda a, cwd: (0, "1 passed in 0.1s")
    )
    assert findings == []


def test_exit_code_mismatch_is_flagged(repo_root: Path) -> None:
    result = {"commands": [{"command": _GOOD_CMD, "exit_code": 0,
                            "summary": "1 passed in 1s"}]}
    findings = crr.recheck_commands(
        result, repo_root, run=lambda a, cwd: (1, "1 passed in 1s")
    )
    assert len(findings) == 1 and "exit_code" in findings[0].detail


@pytest.mark.parametrize(
    "text, expected",
    [
        ("=== 12 passed, 1 skipped, 3 warnings in 0.5s ===", {"passed": 12, "skipped": 1}),
        ("5 passed\n\n=== 12 passed in 1s ===", {"passed": 12}),   # tail line wins
        ("2 errors in 1s", {"error": 2}),                          # 'errors' -> 'error'
        ("no outcome here", {}),
    ],
)
def test_parse_pytest_summary_drops_noise(text: str, expected: dict) -> None:
    # warnings + duration are deliberately excluded (non-deterministic noise).
    assert crr.parse_pytest_summary(text) == expected


# ---------------------------------------------------------------------------
# 4. Parser — extract_result_block fail-closed contract
# ---------------------------------------------------------------------------

def _block(verdict: str, commit: str = "a", extra: str = "") -> str:
    return (
        "```json\n"
        f'{{"schema_version": "reviewer-result/1", "verdict": "{verdict}", '
        f'"reviewed_commit": "{commit}", "reviewed_head": "{commit}", '
        f'"issues": []{extra}}}\n'
        "```\n"
    )


def test_wellformed_block_parses() -> None:
    block = crr.extract_result_block(_block("pass"))
    assert block is not None and block["verdict"] == "pass"


def test_last_block_wins_on_duplicates() -> None:
    text = _block("pass", "aaa") + _block("issues", "bbb", extra=', "x": 1')
    block = crr.extract_result_block(text)
    assert block["verdict"] == "issues" and block["reviewed_commit"] == "bbb"


def test_absent_block_is_none_not_error() -> None:
    assert crr.extract_result_block("no fenced json at all") is None


def test_unrelated_schema_block_is_ignored() -> None:
    assert crr.extract_result_block('```json\n{"schema_version": "other/9"}\n```') is None


def test_malformed_block_of_our_schema_raises() -> None:
    # A fence carrying our schema_version KEY but invalid JSON must NOT be hidden as
    # "absent" — it is a real defect (fail-closed, ResultParseError).
    bad = '```json\n{"schema_version": "reviewer-result/1", not valid}\n```'
    with pytest.raises(crr.ResultParseError):
        crr.extract_result_block(bad)


def test_malformed_json_without_our_schema_key_is_skipped() -> None:
    # Invalid JSON that is NOT our schema is a foreign block -> silently skipped.
    assert crr.extract_result_block("```json\n{broken, not ours}\n```") is None


# ---------------------------------------------------------------------------
# 5. Schema validation — the invariants ci_smoke enforces
# ---------------------------------------------------------------------------

_VALID_PASS = {"verdict": "pass", "issues": [], "reviewed_commit": "a", "reviewed_head": "a"}


def test_valid_pass_has_no_violations() -> None:
    assert crr.validate_schema(_VALID_PASS) == []


@pytest.mark.parametrize(
    "result, needle",
    [
        # pass must have empty issues
        ({**_VALID_PASS, "issues": [{"severity": "minor"}]}, "issues to be empty"),
        # issues must be non-empty
        ({"verdict": "issues", "issues": [], "reviewed_commit": "a", "reviewed_head": "a"},
         "non-empty issues"),
        # bad verdict enum
        ({**_VALID_PASS, "verdict": "nope"}, "is not one of"),
        # unable_to_verify with a bad reason code
        ({"verdict": "unable_to_verify", "issues": [], "unverifiable_reason": "U9",
          "blocked": "x", "reviewed_commit": "a", "reviewed_head": "a"}, "unverifiable_reason"),
        # unable_to_verify with null blocked
        ({"verdict": "unable_to_verify", "issues": [], "unverifiable_reason": "U1",
          "blocked": None, "reviewed_commit": "a", "reviewed_head": "a"}, "non-null `blocked`"),
        # head != commit outside unable_to_verify
        ({**_VALID_PASS, "reviewed_head": "b"}, "reviewed_head"),
        # dirty tree outside unable_to_verify
        ({**_VALID_PASS, "working_tree_clean": False}, "working_tree_clean=false"),
        # wrong-type issues container must be a clean violation, not a crash
        ({"verdict": "issues", "issues": "nope", "reviewed_commit": "a", "reviewed_head": "a"},
         "`issues` must be a list"),
    ],
)
def test_schema_violations(result: dict, needle: str) -> None:
    violations = crr.validate_schema(result)
    assert any(needle in v for v in violations), (needle, violations)


def test_valid_unable_to_verify_passes() -> None:
    utv = {"verdict": "unable_to_verify", "issues": [], "unverifiable_reason": "U3",
           "blocked": "cmd", "reviewed_commit": "a", "reviewed_head": "b",
           "working_tree_clean": False}
    assert crr.validate_schema(utv) == []  # U3+U4 conditions all satisfied together


# ---------------------------------------------------------------------------
# 6. smoke_check — the ci_smoke entry (schema-only, never re-runs pytest)
# ---------------------------------------------------------------------------

def test_smoke_check_clean_on_current_repo(repo_root: Path) -> None:
    # This is exactly what scripts/ci_smoke.py invokes; the live mailbox must be clean.
    assert crr.smoke_check(repo_root) == 0


def _write_report(tmp_path: Path, body: str) -> Path:
    sent = tmp_path / "coordination" / "mailbox" / "sent"
    sent.mkdir(parents=True, exist_ok=True)
    path = sent / "2026-01-01-x-to-all-verification-report.md"
    path.write_text(body)
    return path


def test_smoke_check_zero_on_valid_block(tmp_path: Path) -> None:
    _write_report(tmp_path, _block("pass"))
    assert crr.smoke_check(tmp_path) == 0


def test_smoke_check_one_on_schema_invalid_block(tmp_path: Path) -> None:
    # An unambiguous invariant break: a `pass` verdict with a non-empty issues list.
    _write_report(
        tmp_path,
        '```json\n{"schema_version": "reviewer-result/1", "verdict": "pass", '
        '"issues": [{"severity": "minor"}], "reviewed_commit": "a", "reviewed_head": "a"}\n```',
    )
    assert crr.smoke_check(tmp_path) == 1


def test_smoke_check_one_on_malformed_block(tmp_path: Path) -> None:
    _write_report(
        tmp_path,
        '```json\n{"schema_version": "reviewer-result/1", broken not json}\n```',
    )
    assert crr.smoke_check(tmp_path) == 1


def test_smoke_check_zero_when_no_mailbox(tmp_path: Path) -> None:
    assert crr.smoke_check(tmp_path) == 0  # absent mailbox -> nothing to consume


# ---------------------------------------------------------------------------
# 7. consume() end-to-end (extract -> validate -> propose), recheck disabled
# ---------------------------------------------------------------------------

def test_consume_reports_clean_valid_block(repo_root: Path) -> None:
    report = crr.consume(_block("pass"), repo_root, recheck=False)
    assert report.block_present and report.ok() and report.verdict == "pass"


def test_consume_no_block_is_ok(repo_root: Path) -> None:
    report = crr.consume("nothing here", repo_root, recheck=False)
    assert not report.block_present and report.ok()
