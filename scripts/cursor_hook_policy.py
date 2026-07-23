#!/usr/bin/env python3
"""Deterministic guardrails for project-local Cursor seat hooks."""

from __future__ import annotations

import argparse
import json
import os
import re
import shlex
import stat
import subprocess
import sys
from collections.abc import Mapping, Sequence
from pathlib import Path, PurePosixPath
from typing import Any


_PROTECTED_PREFIXES = (
    "coordination/mailbox/sent/",
    "coordination/mailbox/seen/",
    "coordination/locks/",
    ".cursor/runtime/",
    ".git/refs/threeway/",
)
_SEAT_IMPERSONATION = re.compile(
    r"\b(live\s+)?(director2?|operator2?|coordinator2?)\s+seat\b|\bissue\s+(go|nits|fail)\b",
    re.IGNORECASE,
)
_LIVE_SEATS = frozenset(
    {"director", "director2", "operator", "operator2", "coordinator"}
)
_MUTATING_SEATS = frozenset({"director", "director2", "operator", "operator2"})
_PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _allow() -> dict[str, str]:
    return {"permission": "allow"}


def _deny(message: str) -> dict[str, str]:
    return {
        "permission": "deny",
        "user_message": message,
        "agent_message": message,
    }


def _normalized_path(value: object) -> str:
    if not isinstance(value, str):
        return ""
    try:
        path = Path(value).expanduser().resolve(strict=False)
        return path.relative_to(_PROJECT_ROOT).as_posix()
    except (OSError, ValueError):
        pass
    path = PurePosixPath(value.replace("\\", "/")).as_posix()
    while path.startswith("./"):
        path = path[2:]
    return path


def _protected(value: object) -> bool:
    path = _normalized_path(value)
    return any(path == prefix.rstrip("/") or path.startswith(prefix) for prefix in _PROTECTED_PREFIXES)


def _subagent(payload: Mapping[str, Any]) -> bool:
    return any(
        key in payload
        for key in ("subagent_id", "subagent_type")
    )


def _clean_git_env(environ: Mapping[str, str]) -> dict[str, str]:
    return {
        key: value
        for key, value in environ.items()
        if not key.startswith("GIT_")
    }


def _valid_live_binding(environ: Mapping[str, str]) -> bool:
    """Prove one exact, healthy provider-prefixed Cursor seat binding."""

    seat = environ.get("CURSOR_SEAT", "")
    raw_index = environ.get("GIT_INDEX_FILE", "")
    if seat not in _LIVE_SEATS or not raw_index:
        return False
    root = _PROJECT_ROOT
    resolved = subprocess.run(
        ["git", "-C", str(root), "rev-parse", "--absolute-git-dir"],
        env=_clean_git_env(environ),
        text=True,
        capture_output=True,
        check=False,
    )
    if resolved.returncode != 0:
        return False
    expected = Path(resolved.stdout.strip()) / f"index-cursor-{seat}"
    index = Path(raw_index)
    if (
        not index.is_absolute()
        or os.path.normpath(str(index)) != os.path.normpath(str(expected))
    ):
        return False
    try:
        if not stat.S_ISREG(index.lstat().st_mode):
            return False
    except OSError:
        return False
    index_env = _clean_git_env(environ)
    index_env["GIT_INDEX_FILE"] = str(index)
    entries = subprocess.run(
        ["git", "-C", str(root), "ls-files", "--stage", "-z"],
        env=index_env,
        text=True,
        capture_output=True,
        check=False,
    )
    if entries.returncode != 0:
        return False
    if not entries.stdout:
        head_entries = subprocess.run(
            ["git", "-C", str(root), "ls-tree", "-r", "--name-only", "-z", "HEAD"],
            env=_clean_git_env(environ),
            text=True,
            capture_output=True,
            check=False,
        )
        if head_entries.returncode != 0 or head_entries.stdout:
            return False
    status = subprocess.run(
        [
            "git",
            "--no-optional-locks",
            "-C",
            str(root),
            "status",
            "--porcelain=v1",
            "--untracked-files=no",
            "--ignore-submodules=all",
        ],
        env=index_env,
        text=True,
        capture_output=True,
        check=False,
    )
    return status.returncode == 0


def _mutation_capable(
    payload: Mapping[str, Any], environ: Mapping[str, str]
) -> bool:
    return (
        not _subagent(payload)
        and environ.get("CURSOR_OPERATION") == "dispatch"
        and environ.get("CURSOR_SEAT") in _MUTATING_SEATS
        and _valid_live_binding(environ)
    )


def _segments(command: str) -> list[list[str]]:
    if "\n" in command:
        if "<<" in command:
            # Heredoc bodies are data for the first-line command, not shell.
            command = command.split("\n", 1)[0]
        else:
            result: list[list[str]] = []
            for line in command.split("\n"):
                if not line.strip():
                    continue
                parsed = _segments(line)
                if not parsed:
                    return []
                result.extend(parsed)
            return result
    try:
        lexer = shlex.shlex(command, posix=True, punctuation_chars=";&|")
        lexer.whitespace_split = True
        tokens = list(lexer)
    except ValueError:
        return []
    result: list[list[str]] = []
    current: list[str] = []
    index = 0
    while index < len(tokens):
        token = tokens[index]
        if (
            token == "&"
            and current
            and _REDIRECT_BARE.fullmatch(current[-1])
            and index + 1 < len(tokens)
            and re.fullmatch(r"(?:[0-9]+|-)", tokens[index + 1])
        ):
            current[-1] = f"{current[-1]}&{tokens[index + 1]}"
            index += 2
            continue
        if token in {";", "&", "|", "|&", "||", "&&"}:
            if current:
                result.append(current)
                current = []
        else:
            current.append(token)
        index += 1
    if current:
        result.append(current)
    return result


_MAX_SHELL_NESTING = 8


def _backtick_substitution(command: str, start: int) -> tuple[str, int] | None:
    """Extract one unescaped legacy command substitution."""

    body: list[str] = []
    index = start + 1
    while index < len(command):
        if command[index] == "\\":
            if index + 1 >= len(command):
                return None
            if command[index + 1] == "`":
                # Legacy nested backticks escape their inner delimiters.
                # Normalize them so the recursive policy pass sees execution.
                body.append("`")
            else:
                body.extend(command[index : index + 2])
            index += 2
            continue
        if command[index] == "`":
            return "".join(body), index + 1
        body.append(command[index])
        index += 1
    return None


def _parenthesized_substitution(
    command: str,
    open_index: int,
) -> tuple[str, int] | None:
    """Extract a command/process substitution with nested quote awareness."""

    quote_stack: list[str | None] = [None]
    index = open_index + 1
    while index < len(command):
        quote = quote_stack[-1]
        character = command[index]
        if quote == "'":
            if character == "'":
                quote_stack[-1] = None
            index += 1
            continue
        if character == "\\":
            index += 2
            continue
        if quote == '"':
            if character == '"':
                quote_stack[-1] = None
                index += 1
                continue
            if command.startswith("$(", index):
                if len(quote_stack) >= _MAX_SHELL_NESTING:
                    return None
                quote_stack.append(None)
                index += 2
                continue
            if character == "`":
                nested = _backtick_substitution(command, index)
                if nested is None:
                    return None
                index = nested[1]
                continue
            index += 1
            continue
        if character in {"'", '"'}:
            quote_stack[-1] = character
            index += 1
            continue
        if (
            command.startswith("$(", index)
            or command.startswith("<(", index)
            or command.startswith(">(", index)
        ):
            if len(quote_stack) >= _MAX_SHELL_NESTING:
                return None
            quote_stack.append(None)
            index += 2
            continue
        if character == "`":
            nested = _backtick_substitution(command, index)
            if nested is None:
                return None
            index = nested[1]
            continue
        if character == ")":
            quote_stack.pop()
            if not quote_stack:
                return command[open_index + 1 : index], index + 1
        index += 1
    return None


def _shell_substitutions(command: str) -> list[str] | None:
    """Return executable substitution bodies, or None for unsafe syntax."""

    substitutions: list[str] = []
    quote: str | None = None
    index = 0
    while index < len(command):
        character = command[index]
        if quote == "'":
            if character == "'":
                quote = None
            index += 1
            continue
        if character == "\\":
            index += 2
            continue
        if character == "'" and quote is None:
            quote = "'"
            index += 1
            continue
        if character == '"':
            quote = None if quote == '"' else '"'
            index += 1
            continue
        opener = (
            command.startswith("$(", index)
            or (
                quote is None
                and (
                    command.startswith("<(", index)
                    or command.startswith(">(", index)
                )
            )
        )
        if opener:
            nested = _parenthesized_substitution(command, index + 1)
            if nested is None:
                return None
            substitutions.append(nested[0])
            index = nested[1]
            continue
        if character == "`":
            nested = _backtick_substitution(command, index)
            if nested is None:
                return None
            substitutions.append(nested[0])
            index = nested[1]
            continue
        index += 1
    return substitutions


def _assignment(token: str) -> bool:
    return re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*=.*", token) is not None


def _unwrap_env(tokens: list[str]) -> tuple[list[str], bool]:
    index = 0
    while index < len(tokens) and _assignment(tokens[index]):
        index += 1
    if index >= len(tokens) or PurePosixPath(tokens[index]).name != "env":
        return tokens[index:], False
    index += 1
    unset_index = False
    reset_index = False
    while index < len(tokens):
        token = tokens[index]
        if token == "--":
            index += 1
            break
        if token in {"-u", "--unset"} and index + 1 < len(tokens):
            unset_index = unset_index or tokens[index + 1] == "GIT_INDEX_FILE"
            index += 2
            continue
        if token.startswith("--unset="):
            unset_index = unset_index or token.partition("=")[2] == "GIT_INDEX_FILE"
            index += 1
            continue
        if _assignment(token):
            reset_index = reset_index or token.partition("=")[0] == "GIT_INDEX_FILE"
            index += 1
            continue
        if token.startswith("-"):
            index += 1
            continue
        break
    return tokens[index:], unset_index and not reset_index


_REDIRECT_GLUED = re.compile(r"^(?:[0-9]*>>?|&>>?|>\|)(?P<path>.+)$")
_REDIRECT_BARE = re.compile(r"^(?:[0-9]*>>?|&>>?|>\|)$")
_MUTATING_FILE_CMDS = {
    "tee",
    "cp",
    "mv",
    "rm",
    "dd",
    "install",
    "ln",
    "truncate",
    "touch",
    "mkdir",
    "rmdir",
    "chmod",
    "chown",
}
_GIT_MUTATION_SUBCOMMANDS = frozenset(
    {
        "add",
        "apply",
        "checkout",
        "clean",
        "commit",
        "config",
        "mv",
        "rebase",
        "reset",
        "restore",
        "revert",
        "rm",
        "stash",
        "switch",
    }
)
# Parity with .codex/hooks guard-git-index semantics: only commands that read
# or write the git index need the `env -u GIT_INDEX_FILE` prefix under a
# per-seat index. Read-only git (status/log/show/diff/...) stays usable.
_GIT_INDEX_MUTATORS = frozenset(
    {
        "add",
        "apply",
        "checkout",
        "cherry-pick",
        "clean",
        "commit",
        "merge",
        "mv",
        "read-tree",
        "rebase",
        "reset",
        "restore",
        "rm",
        "stash",
        "switch",
        "update-index",
    }
)
_SAFE_GIT_READS = frozenset(
    {
        "cat-file",
        "describe",
        "diff",
        "grep",
        "log",
        "ls-files",
        "ls-tree",
        "merge-base",
        "name-rev",
        "rev-list",
        "rev-parse",
        "show",
        "status",
    }
)
_GIT_OPTIONAL_INDEX_READS = frozenset({"diff", "ls-files", "status"})
_SAFE_READ_COMMANDS = frozenset(
    {
        "[",
        "cat",
        "cd",
        "cut",
        "echo",
        "file",
        "grep",
        "head",
        "less",
        "ls",
        "md5",
        "pwd",
        "rg",
        "sed",
        "set",
        "sha256sum",
        "shasum",
        "sort",
        "stat",
        "tail",
        "test",
        "tr",
        "uniq",
        "wc",
    }
)


def _writes_protected(tokens: list[str]) -> bool:
    """Deny only actual writes to protected state, never plain reads."""
    if not tokens:
        return False
    for index, token in enumerate(tokens):
        glued = _REDIRECT_GLUED.match(token)
        if glued and _protected(glued.group("path")):
            return True
        if _REDIRECT_BARE.match(token) and index + 1 < len(tokens) and _protected(tokens[index + 1]):
            return True
    executable = PurePosixPath(tokens[0]).name
    if executable in _MUTATING_FILE_CMDS and any(_protected(token) for token in tokens[1:]):
        return True
    return False


_SCRATCH_PREFIXES = (".pytest-verify-tmp/",)


def _repo_relative(value: object) -> str | None:
    """Return the repo-relative path, or None when it points outside."""

    path = _normalized_path(value)
    if not path or path.startswith("/") or path.startswith(".."):
        return None
    return path


def _scratch(path: str) -> bool:
    return any(
        path == prefix.rstrip("/") or path.startswith(prefix)
        for prefix in _SCRATCH_PREFIXES
    )


def _mutated_repo_path(value: object) -> bool:
    path = _repo_relative(value)
    return path is not None and not _scratch(path)


def _writes_repo_tree(tokens: list[str]) -> bool:
    """Recognize common shell mutations aimed at the repository tree.

    Writes outside the repository (e.g. /tmp scratch) and to the sanctioned
    scratch prefixes stay allowed so read-only seats can still capture logs.
    """

    if not tokens:
        return False
    for index, token in enumerate(tokens):
        glued = _REDIRECT_GLUED.match(token)
        if glued:
            target = glued.group("path")
            if not target.startswith("&") and _mutated_repo_path(target):
                return True
            continue
        if (
            _REDIRECT_BARE.match(token)
            and index + 1 < len(tokens)
            and _mutated_repo_path(tokens[index + 1])
        ):
            return True
    executable = PurePosixPath(tokens[0]).name
    mutates = executable in _MUTATING_FILE_CMDS or (
        executable == "sed"
        and any(
            token == "-i" or (token.startswith("-i") and not token.startswith("--"))
            for token in tokens[1:]
        )
    )
    if not mutates:
        return False
    return any(
        _mutated_repo_path(token)
        for token in tokens[1:]
        if not token.startswith("-")
    )


_PRIVILEGED_EXECS = {
    "send-event",
    "consume-events",
    "claim-lock",
    "release-lock",
    "cursor-seat",
    "cursor-publish",
    "cursor-consume",
    "mailbox_writer.py",
    "cursor_seat_launcher.py",
    "cursor_mailbox.py",
}
# Provider separation: Cursor sessions never launch another provider's seats.
_FOREIGN_PROVIDER_EXECS = {
    "agy-seat",
    "codex-seat",
    "agy_seat_launcher.py",
    "codex_seat_launcher.py",
}
# Documented read-only orientation entry points of the Cursor launcher.
_READ_ONLY_LAUNCHER_COMMANDS = {"readiness", "status"}
_READ_ONLY_LAUNCHERS = {"cursor-seat", "cursor_seat_launcher.py"}
_DRY_RUN_WRAPPERS = {"cursor-publish", "cursor-consume", "cursor_mailbox.py"}
_INTERPRETER_NAMES = {"bash", "sh", "zsh", "dash", "ksh", "ruby", "perl"}
_SHELL_INTERPRETERS = {"bash", "sh", "zsh", "dash", "ksh"}
_COMMAND_WRAPPERS = {"command", "exec"}


def _after_command_wrapper(tokens: list[str]) -> list[str]:
    """Return the command invoked by shell ``command`` / ``exec`` builtins."""

    index = 1
    while index < len(tokens):
        token = tokens[index]
        if token == "--":
            return tokens[index + 1 :]
        if token.startswith("-"):
            index += 1
            continue
        return tokens[index:]
    return []


def _shell_code_argument(tokens: list[str]) -> str | None:
    """Return the script passed to a shell's ``-c`` option, when present."""

    for index, token in enumerate(tokens[1:], start=1):
        if token == "--":
            return None
        if token == "-c" or (
            token.startswith("-")
            and not token.startswith("--")
            and "c" in token[1:]
        ):
            return tokens[index + 1] if index + 1 < len(tokens) else ""
    return None


def _git_subcommand(tokens: list[str]) -> str:
    index = 1
    while index < len(tokens) and tokens[index].startswith("-"):
        if tokens[index] in {"-C", "-c", "--git-dir", "--work-tree"} and index + 1 < len(tokens):
            index += 2
        else:
            index += 1
    return tokens[index] if index < len(tokens) else ""


def _launcher_read_only(arguments: list[str]) -> bool:
    """True for cursor-seat invocations that cannot produce a live launch."""

    index = 0
    while index < len(arguments):
        token = arguments[index]
        if token == "--dry-run":
            return True
        if token == "--config" and index + 1 < len(arguments):
            index += 2
            continue
        if token.startswith("-"):
            index += 1
            continue
        return token in _READ_ONLY_LAUNCHER_COMMANDS
    return False


def _bounded_read_only_segment(
    tokens: list[str],
    *,
    unsets_index: bool,
    environ: Mapping[str, str],
) -> bool:
    """Allow a small inspection/scratch subset for readiness-only sessions."""

    if not tokens:
        return False
    executable = PurePosixPath(tokens[0]).name
    if _read_only_invocation(executable, tokens[1:]):
        return True
    if (
        executable.startswith("python")
        and len(tokens) > 1
        and not tokens[1].startswith("-")
        and _read_only_invocation(
            PurePosixPath(tokens[1]).name,
            tokens[2:],
        )
    ):
        return True
    if executable == "git":
        subcommand = _git_subcommand(tokens)
        if subcommand not in _SAFE_GIT_READS:
            return False
        if environ.get("GIT_INDEX_FILE") and not unsets_index:
            return False
        if (
            subcommand in _GIT_OPTIONAL_INDEX_READS
            and "--no-optional-locks" not in tokens[1:]
        ):
            return False
        return True
    if executable == "sed" and any(
        token == "-i" or (token.startswith("-i") and not token.startswith("--"))
        for token in tokens[1:]
    ):
        return False
    if executable in _MUTATING_FILE_CMDS:
        return not _writes_repo_tree(tokens)
    return executable in _SAFE_READ_COMMANDS and not _writes_repo_tree(tokens)


def _review_test_segment(tokens: list[str], *, unsets_index: bool) -> bool:
    executable = PurePosixPath(tokens[0]).name if tokens else ""
    is_pytest = executable == "pytest" or (
        executable.startswith("python")
        and any(
            tokens[index : index + 2] == ["-m", "pytest"]
            for index in range(1, len(tokens) - 1)
        )
    )
    return is_pytest and unsets_index


def _read_only_invocation(program: str, arguments: list[str]) -> bool:
    if program in _READ_ONLY_LAUNCHERS:
        return _launcher_read_only(arguments)
    if program in _DRY_RUN_WRAPPERS:
        return "--dry-run" in arguments
    return False


def _effect_violation(tokens: list[str], *, depth: int = 0) -> str | None:
    """Classify direct and common shell-wrapped privileged executions.

    Returns ``"effect"`` for separately authorized effects, ``"foreign"`` for
    other providers' seat launchers, and ``None`` when the segment is clean.
    """

    if not tokens:
        return None
    if depth > 4:
        return "effect"
    executable = PurePosixPath(tokens[0]).name
    if executable in _FOREIGN_PROVIDER_EXECS:
        return "foreign"
    if executable in _PRIVILEGED_EXECS:
        if _read_only_invocation(executable, tokens[1:]):
            return None
        return "effect"
    if executable == "sudo":
        return "effect"
    if executable in _COMMAND_WRAPPERS:
        return _effect_violation(_after_command_wrapper(tokens), depth=depth + 1)
    if executable.startswith("python") or executable in _INTERPRETER_NAMES:
        for index, token in enumerate(tokens[1:], start=1):
            name = PurePosixPath(token).name
            if name in _FOREIGN_PROVIDER_EXECS:
                return "foreign"
            if name in _PRIVILEGED_EXECS:
                if _read_only_invocation(name, tokens[index + 1 :]):
                    return None
                return "effect"
        if executable in _SHELL_INTERPRETERS:
            shell_code = _shell_code_argument(tokens)
            if shell_code is not None:
                nested = _segments(shell_code)
                if not nested:
                    return "effect"
                for segment in nested:
                    violation = _effect_violation(
                        _unwrap_env(segment)[0], depth=depth + 1
                    )
                    if violation:
                        return violation
                return None
    if executable == "git" and _git_subcommand(tokens) in {
        "push",
        "merge",
        "rebase",
        "cherry-pick",
        "fetch",
        "pull",
    }:
        return "effect"
    return None


def _shell_decision(
    payload: Mapping[str, Any],
    environ: Mapping[str, str],
    *,
    depth: int = 0,
) -> dict[str, str]:
    command = payload.get("command")
    if not isinstance(command, str) or not command.strip():
        return _deny("Cursor seat hook received malformed shell input.")
    if depth >= _MAX_SHELL_NESTING:
        return _deny("Cursor seat hook exceeded safe shell nesting depth.")
    substitutions = _shell_substitutions(command)
    if substitutions is None:
        return _deny("Cursor seat hook could not safely parse shell substitution.")
    for nested_command in substitutions:
        nested_payload = dict(payload)
        nested_payload["command"] = nested_command
        nested_result = _shell_decision(
            nested_payload,
            environ,
            depth=depth + 1,
        )
        if nested_result.get("permission") != "allow":
            return _deny(
                "Shell substitution contains an action that is not authorized "
                "in this Cursor posture."
            )
    segments = _segments(command)
    if not segments:
        return _deny("Cursor seat hook could not parse a sensitive shell command.")
    inherited_index = bool(environ.get("GIT_INDEX_FILE"))
    is_subagent = _subagent(payload)
    binding_valid = _valid_live_binding(environ)
    mutation_capable = (
        binding_valid
        and not is_subagent
        and environ.get("CURSOR_OPERATION") == "dispatch"
        and environ.get("CURSOR_SEAT") in _MUTATING_SEATS
    )
    review_capable = (
        binding_valid
        and not is_subagent
        and environ.get("CURSOR_OPERATION") == "review"
        and environ.get("CURSOR_SEAT") in {"operator", "operator2"}
    )
    for raw in segments:
        tokens, unsets_index = _unwrap_env(raw)
        if not tokens:
            continue
        executable = PurePosixPath(tokens[0]).name
        git_subcommand = _git_subcommand(tokens) if executable == "git" else ""
        is_pytest = executable == "pytest" or (
            executable.startswith("python")
            and any(
                tokens[index : index + 2] == ["-m", "pytest"]
                for index in range(1, len(tokens) - 1)
            )
        )
        violation = _effect_violation(tokens)
        if violation == "foreign":
            return _deny(
                "Provider separation: Cursor sessions do not launch other "
                "providers' seats."
            )
        if violation == "effect":
            subject = "subagent" if is_subagent else "Cursor seat"
            return _deny(
                f"{subject} cannot perform this separately authorized effect from an agent tool."
            )
        if _writes_protected(tokens):
            return _deny("Direct writes to fixed-writer or Cursor runtime state are forbidden.")
        if (
            inherited_index
            and not unsets_index
            and (
                is_pytest
                or (
                    executable == "git"
                    and git_subcommand in _GIT_INDEX_MUTATORS
                )
            )
        ):
            return _deny(
                "GIT_INDEX_FILE is set; git index mutators and pytest require "
                "'env -u GIT_INDEX_FILE'."
            )
        if not mutation_capable:
            if (
                _writes_repo_tree(tokens)
                or (
                    executable == "git"
                    and git_subcommand in _GIT_MUTATION_SUBCOMMANDS
                )
            ):
                return _deny(
                    "Cursor readiness/review mode is repository read-only; "
                    "mutation requires an exact live dispatch seat/index binding."
                )
            if review_capable and _review_test_segment(
                tokens, unsets_index=unsets_index
            ):
                continue
            if not _bounded_read_only_segment(
                tokens,
                unsets_index=unsets_index,
                environ=environ,
            ):
                return _deny(
                    "Cursor readiness/review mode permits only bounded "
                    "read-only inspection and out-of-repository scratch output."
                )
    return _allow()


def evaluate(
    payload: Mapping[str, Any], environ: Mapping[str, str] | None = None
) -> dict[str, Any]:
    env = environ or os.environ
    event = payload.get("hook_event_name")
    if event == "sessionStart":
        seat = env.get("CURSOR_SEAT", "")
        return {
            "env": {"CURSOR_HOOK_SEAT": seat or "readiness-bridge"},
            "additional_context": (
                f"Pipeline Cursor posture: {seat or 'readiness-bridge'}. "
                "Hook identity describes context and does not grant authority."
            ),
        }
    if event == "subagentStart":
        if env.get("CURSOR_SEAT") in _LIVE_SEATS:
            return _deny(
                "A live Cursor seat cannot spawn a subagent because Cursor hooks "
                "cannot safely strip inherited seat authority from child tools."
            )
        task = payload.get("task", "")
        if isinstance(task, str) and _SEAT_IMPERSONATION.search(task):
            return _deny("Cursor subagents are advisors and cannot impersonate a live seat.")
        return _allow()
    if event == "beforeShellExecution":
        return _shell_decision(payload, env)
    if event == "preToolUse":
        tool = payload.get("tool_name")
        tool_input = payload.get("tool_input")
        if not isinstance(tool_input, dict):
            return _deny("Cursor seat hook received malformed tool input.")
        if tool in {"Write", "Delete"}:
            path = next(
                (
                    tool_input[key]
                    for key in ("path", "file_path", "target_file")
                    if key in tool_input
                ),
                "",
            )
            if _protected(path):
                return _deny("Direct edits to fixed-writer or Cursor runtime state are forbidden.")
            if _subagent(payload):
                return _deny("Cursor subagents cannot inherit parent seat mutation authority.")
            if not _mutation_capable(payload, env):
                return _deny(
                    "Write/Delete requires an exact live Cursor dispatch "
                    "seat/index binding; this session is readiness-only."
                )
        return _allow()
    return _allow()


def process_bytes(
    raw: bytes,
    *,
    event_hint: str | None,
    environ: Mapping[str, str] | None = None,
) -> tuple[str, int]:
    try:
        payload = json.loads(raw.decode("utf-8"))
        if not isinstance(payload, dict):
            raise ValueError("hook payload is not an object")
    except (UnicodeError, json.JSONDecodeError, ValueError):
        result = (
            _deny("Malformed input was denied by the fail-closed Cursor seat hook.")
            if event_hint in {"beforeShellExecution", "preToolUse", "subagentStart"}
            else {}
        )
        return json.dumps(result), 0
    if event_hint and "hook_event_name" not in payload:
        payload["hook_event_name"] = event_hint
    return json.dumps(evaluate(payload, environ)), 0


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--event")
    args = parser.parse_args(sys.argv[1:] if argv is None else argv)
    output, status = process_bytes(
        sys.stdin.buffer.read(), event_hint=args.event, environ=os.environ
    )
    print(output)
    return status


if __name__ == "__main__":
    raise SystemExit(main())
