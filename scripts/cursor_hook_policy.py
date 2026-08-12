#!/usr/bin/env python3
"""Write-governed Cursor Desktop guardrails for Pipeline app seats.

Classified inspection reads and scratch writes are free. Unknown top-level
commands ask; unknown subagent commands deny. Repository mutations are
role-governed: Director worktree chats mutate freely; Cursor file-tool edits
outside that posture deny because preToolUse cannot enforce an ask today.
Governed shell mutations still receive one in-app approval. Bound
Director/Operator mailbox wrappers inherit the seat-start grant (allow).
Remote Git effects (push, pull, fetch, merge, rebase, cherry-pick) always ask.
Top-level MCP calls ask through their separately enforceable hook; subagent MCP
calls deny. Hard denies are reserved for protected coordination surfaces,
direct fixed-writer calls, foreign provider launchers, and subagent seat
impersonation.

This policy is fail-closed at its edges: malformed payloads, unrecognized
hook events, and preToolUse tools without a rule all deny instead of falling
through to allow. Tools that own a dedicated hook event (Shell, Task, MCP)
pass preToolUse untouched so no action is double-evaluated.

Subagent containment lives at ``subagentStart``. Cursor's tool-surface hooks
(preToolUse / beforeShellExecution / beforeMCPExecution) carry no subagent
discriminator and a child shares the parent's conversation_id, so a launched
subagent's tool calls cannot be distinguished from the parent's here; the
``_subagent`` detector is fail-closed forward-compatibility, not an enforced
control. See ``docs/protocol/cursor/continuation.md`` and
``tests/unit/test_cursor_hook_policy.py`` for the schema pin.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shlex
import shutil
import sys
from collections.abc import Mapping, Sequence
from pathlib import Path, PurePosixPath
from typing import Any

from cursor_app_binding import (
    DEFAULT_REGISTRY_PATH,
    DIRECTOR_SEATS,
    OPERATOR_SEATS,
    AppBindingError,
    AppSessionBinding,
    register_payload_session,
    resolve_registered_session,
    session_environment,
)

_PROJECT_ROOT = Path(__file__).resolve().parents[1]
_PROTECTED_PREFIXES = (
    "coordination/mailbox/sent/",
    "coordination/mailbox/seen/",
    "coordination/locks/",
    ".cursor/runtime/",
    ".git/refs/threeway/",
)
_PROTECTED_GIT_REF_PREFIXES = (
    "refs/authority/",
    "refs/heads/cursor-seat/",
    "refs/protocol/",
    "refs/replace/",
    "refs/threeway/",
)
_PROTECTED_GIT_REFS = frozenset({"refs/heads/main"})
_SCRATCH_PREFIXES = (".pytest-verify-tmp/",)
_MUTATING_FILE_COMMANDS = frozenset(
    {
        "chmod",
        "chown",
        "cp",
        "dd",
        "install",
        "ln",
        "mkdir",
        "mv",
        "rm",
        "rmdir",
        "rsync",
        "tee",
        "touch",
        "truncate",
    }
)
_GIT_TREE_MUTATORS = frozenset(
    {
        "add",
        "am",
        "apply",
        "branch",
        "checkout",
        "clean",
        "clone",
        "commit",
        "config",
        "filter-branch",
        "init",
        "mv",
        "notes",
        "read-tree",
        "remote",
        "replace",
        "reset",
        "restore",
        "revert",
        "rm",
        "stash",
        "submodule",
        "switch",
        "symbolic-ref",
        "tag",
        "update-index",
        "update-ref",
        "worktree",
    }
)
_EXTERNAL_GIT_EFFECTS = frozenset(
    {"fetch", "pull", "push", "merge", "rebase", "cherry-pick"}
)
_GIT_INSPECTION_COMMANDS = frozenset(
    {
        "blame",
        "cat-file",
        "check-attr",
        "check-ignore",
        "check-ref-format",
        "diff",
        "diff-tree",
        "for-each-ref",
        "fsck",
        "grep",
        "help",
        "log",
        "ls-files",
        "ls-tree",
        "merge-base",
        "name-rev",
        "rev-list",
        "rev-parse",
        "show",
        "show-ref",
        "status",
        "verify-commit",
        "verify-tag",
        "version",
        "whatchanged",
    }
)
_MAILBOX_WRAPPERS = frozenset(
    {"cursor-publish", "cursor-consume", "cursor_mailbox.py"}
)
_DIRECT_EFFECTS = frozenset(
    {
        "claim-lock",
        "consume-events",
        "mailbox_writer.py",
        "release-lock",
        "send-event",
    }
)
_FOREIGN_LAUNCHERS = frozenset(
    {
        "agy-seat",
        "claude-seat",
        "codex-seat",
        "cursor-agent",
        "agy_seat_launcher.py",
        "claude_seat_launcher.py",
        "codex_seat_launcher.py",
    }
)
_EPHEMERAL_WRITE_TARGETS = frozenset(
    {"/dev/null", "/dev/stdout", "/dev/stderr", "/dev/tty"}
)
_EPHEMERAL_WRITE_PREFIXES = (
    "/tmp/",
    "/private/tmp/",
    "/var/folders/",
    "/private/var/folders/",
)
_BRANCH_WRITE_FLAGS = frozenset(
    {
        "-c",
        "-C",
        "-d",
        "-D",
        "-f",
        "-m",
        "-M",
        "--copy",
        "--delete",
        "--edit-description",
        "--force",
        "--move",
        "--set-upstream-to",
        "--unset-upstream",
    }
)
_REDIRECT = re.compile(r"^(?:[0-9]*>>?|&>>?|>\|)(?P<path>.*)$")
_INSPECTION_PROGRAMS = frozenset(
    {
        "[",
        "cat",
        "cd",
        "cut",
        "diff",
        "echo",
        "false",
        "file",
        "find",
        "grep",
        "head",
        "ls",
        "md5",
        "pwd",
        "rg",
        "sha256sum",
        "shasum",
        "sort",
        "stat",
        "tail",
        "test",
        "tr",
        "true",
        "uniq",
        "wc",
    }
)
_INERT_ENVIRONMENT_OVERRIDES = frozenset(
    {
        "COLUMNS",
        "LANG",
        "LC_ALL",
        "LINES",
        "NO_COLOR",
        "PIP_DISABLE_PIP_VERSION_CHECK",
        "PYTHONDONTWRITEBYTECODE",
        "PYTHONHASHSEED",
        "TERM",
        "TZ",
    }
)
# Kept in lockstep with the canonical event-name grammar in
# scripts/protocol_mailbox.py (EVENT_NAME_RE); this local copy exists only
# because the hook must import nothing heavier than cursor_app_binding.
# ``coordinator2`` is cold capacity but remains a lawful roster identity.
_MAILBOX_EVENT_NAME = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}-\d{2}-\d{2}Z-"
    r"(?P<sender>director2?|operator2?|coordinator2?)-to-"
    r"(?:director2?|operator2?|coordinator2?|all)-[a-z0-9-]+\.md$"
)


def _allow() -> dict[str, str]:
    return {"permission": "allow"}


def _ask(message: str) -> dict[str, str]:
    return {
        "permission": "ask",
        "user_message": message,
        "agent_message": message,
    }


def _deny(message: str) -> dict[str, str]:
    return {
        "permission": "deny",
        "user_message": message,
        "agent_message": message,
    }


# Cursor's published hook schema (cursor.com/docs/hooks) gives the
# tool-surface events — preToolUse, beforeShellExecution, beforeMCPExecution —
# only the common base fields (conversation_id, generation_id, model,
# workspace_roots, ...) plus their tool-specific data. NONE of them carries a
# subagent discriminator, and a Task-tool child shares its parent's
# conversation_id. The subagent identity (subagent_type, task,
# parent_conversation_id) exists ONLY on the subagentStart event. So a child's
# file edit or shell command is, at the tool hook, indistinguishable from the
# parent's: the enforceable containment point is subagentStart, not the tool
# surface. This detector stays as fail-closed forward-compatibility — if a
# future Cursor version ever tags tool-surface payloads with any child marker,
# the mutating branches immediately treat it as a child — but it is not the
# guarantee. It scans for any plausible child marker rather than a fixed list.
_CHILD_MARKER_SUBSTRINGS = ("subagent", "parent_conversation")


def _subagent(payload: Mapping[str, Any]) -> bool:
    for key, value in payload.items():
        lowered = key.lower()
        if any(marker in lowered for marker in _CHILD_MARKER_SUBSTRINGS):
            if value not in (None, "", False):
                return True
    return False


def _normalized_path(value: object, *, root: Path) -> str:
    if not isinstance(value, str) or not value:
        return ""
    candidate = Path(value).expanduser()
    try:
        absolute = candidate.resolve(strict=False) if candidate.is_absolute() else (
            root / candidate
        ).resolve(strict=False)
        return absolute.relative_to(root.resolve()).as_posix()
    except (OSError, ValueError):
        return PurePosixPath(value.replace("\\", "/")).as_posix()


def _protected(value: object, *, root: Path) -> bool:
    path = _normalized_path(value, root=root)
    return any(
        path == prefix.rstrip("/") or path.startswith(prefix)
        for prefix in _PROTECTED_PREFIXES
    )


def _scratch(value: object, *, root: Path) -> bool:
    path = _normalized_path(value, root=root)
    return any(
        path == prefix.rstrip("/") or path.startswith(prefix)
        for prefix in _SCRATCH_PREFIXES
    )


def _repo_path(value: object, *, root: Path) -> bool:
    if not isinstance(value, str) or not value or value.startswith("-"):
        return False
    candidate = Path(value).expanduser()
    try:
        absolute = candidate.resolve(strict=False) if candidate.is_absolute() else (
            root / candidate
        ).resolve(strict=False)
        absolute.relative_to(root.resolve())
        return not _scratch(value, root=root)
    except (OSError, ValueError):
        return False


def _outside_workspace(value: object, *, root: Path) -> bool:
    if not isinstance(value, str) or not value or value.startswith("-"):
        return False
    candidate = Path(value).expanduser()
    try:
        absolute = (
            candidate.resolve(strict=False)
            if candidate.is_absolute()
            else (root / candidate).resolve(strict=False)
        )
        absolute.relative_to(root.resolve())
        return False
    except (OSError, ValueError):
        return True


def _ephemeral_write(value: object) -> bool:
    if not isinstance(value, str):
        return False
    return value in _EPHEMERAL_WRITE_TARGETS or value.startswith(
        _EPHEMERAL_WRITE_PREFIXES
    )


_FD_REDIRECT_TOKEN = re.compile(r"(?:(?:\d)?>&\d|&>\d)")


def _segments(command: str) -> list[list[str]]:
    """Parse simple shell segments; opaque syntax yields no segments."""

    if any(token in command for token in ("\n", "$(", "`", "<(", ">(")):
        return []
    # Keep ``2>&1`` / ``>&2`` intact; punctuation_chars would split on ``&``.
    protected: dict[str, str] = {}

    def _protect(match: re.Match[str]) -> str:
        key = f"__PIPELINE_FD_{len(protected)}__"
        protected[key] = match.group(0)
        return key

    sanitized = _FD_REDIRECT_TOKEN.sub(_protect, command)
    try:
        lexer = shlex.shlex(sanitized, posix=True, punctuation_chars=";&|")
        lexer.whitespace_split = True
        tokens = [protected.get(token, token) for token in lexer]
    except ValueError:
        return []
    result: list[list[str]] = []
    current: list[str] = []
    for token in tokens:
        if token in {";", "&", "|", "|&", "||", "&&"}:
            if current:
                result.append(current)
                current = []
            continue
        current.append(token)
    if current:
        result.append(current)
    return result


def _assignment(token: str) -> bool:
    return re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*=.*", token) is not None


def _unsafe_environment_prefix(tokens: list[str]) -> bool:
    """Reject environment prefixes that can redirect execution or hide parsing."""

    def unsafe_assignment(token: str) -> bool:
        name = token.split("=", 1)[0]
        return name not in _INERT_ENVIRONMENT_OVERRIDES

    index = 0
    while index < len(tokens) and _assignment(tokens[index]):
        if unsafe_assignment(tokens[index]):
            return True
        index += 1
    if index >= len(tokens) or PurePosixPath(tokens[index]).name != "env":
        return False
    index += 1
    while index < len(tokens):
        token = tokens[index]
        if token == "--":
            return False
        if token in {"-i", "--ignore-environment"}:
            index += 1
            continue
        if token in {"-u", "--unset"}:
            if index + 1 >= len(tokens):
                return True
            index += 2
            continue
        if token.startswith("--unset="):
            index += 1
            continue
        if _assignment(token):
            if unsafe_assignment(token):
                return True
            index += 1
            continue
        if token.startswith("-"):
            return True
        return False
    return False


def _unresolved_shell_expansion(tokens: list[str]) -> bool:
    return any("$" in token for token in tokens)


def _unwrap_env(tokens: list[str]) -> list[str]:
    index = 0
    while index < len(tokens) and _assignment(tokens[index]):
        index += 1
    if index >= len(tokens) or PurePosixPath(tokens[index]).name != "env":
        return tokens[index:]
    index += 1
    while index < len(tokens):
        token = tokens[index]
        if token == "--":
            return tokens[index + 1 :]
        if token in {"-u", "--unset"} and index + 1 < len(tokens):
            index += 2
            continue
        if token.startswith("--unset=") or token.startswith("-") or _assignment(token):
            index += 1
            continue
        return tokens[index:]
    return []


def _unwrap_command_builtin(tokens: list[str]) -> list[str]:
    """Strip shell ``command`` builtin wrappers used to bypass classification."""

    index = 0
    while index < len(tokens) and PurePosixPath(tokens[index]).name == "command":
        index += 1
        while index < len(tokens) and tokens[index].startswith("-") and tokens[index] != "--":
            index += 1
        if index < len(tokens) and tokens[index] == "--":
            index += 1
    return tokens[index:]


def _unwrap_prefixes(tokens: list[str]) -> list[str]:
    return _unwrap_command_builtin(_unwrap_env(tokens))


def _git_subcommand(tokens: list[str]) -> str:
    index = 1
    while index < len(tokens):
        token = tokens[index]
        if token in {"-C", "-c", "--git-dir", "--work-tree"} and index + 1 < len(tokens):
            index += 2
            continue
        if token in {"--no-optional-locks", "--no-pager", "--literal-pathspecs"}:
            index += 1
            continue
        if token.startswith("-"):
            index += 1
            continue
        return token
    return ""


def _git_arguments(tokens: list[str]) -> list[str]:
    index = 1
    while index < len(tokens):
        token = tokens[index]
        if token in {"-C", "-c", "--git-dir", "--work-tree"} and index + 1 < len(tokens):
            index += 2
            continue
        if token.startswith("-"):
            index += 1
            continue
        return tokens[index + 1 :]
    return []


def _git_inline_alias(tokens: list[str]) -> bool:
    """Detect inline Git config that can change dispatch or execute helpers."""

    index = 1
    while index < len(tokens):
        token = tokens[index]
        config: str | None = None
        if token == "-c" and index + 1 < len(tokens):
            config = tokens[index + 1]
            index += 2
        elif token.startswith("-c") and token != "-c":
            config = token[2:]
            index += 1
        elif token.startswith("--config-env="):
            config = token.removeprefix("--config-env=").split("=", 1)[0]
            index += 1
        elif token in {"-C", "--git-dir", "--work-tree"} and index + 1 < len(tokens):
            index += 2
            continue
        elif token.startswith("-"):
            index += 1
            continue
        else:
            break
        if config is not None:
            return True
    return False


def _unsafe_git_dispatch(tokens: list[str]) -> bool:
    """Fail closed on inline aliases and unknown names that may resolve as aliases."""

    if not tokens or PurePosixPath(tokens[0]).name != "git":
        return False
    if _git_inline_alias(tokens):
        return True
    subcommand = _git_subcommand(tokens)
    if not subcommand:
        return not any(token in {"--help", "--version"} for token in tokens[1:])
    return subcommand not in (
        _GIT_INSPECTION_COMMANDS | _GIT_TREE_MUTATORS | _EXTERNAL_GIT_EFFECTS
    )


def _protected_git_ref(value: str) -> bool:
    return value in _PROTECTED_GIT_REFS or any(
        value.startswith(prefix) for prefix in _PROTECTED_GIT_REF_PREFIXES
    )


def _protected_branch_name(value: str) -> bool:
    if value.startswith("refs/"):
        return _protected_git_ref(value)
    return _protected_git_ref(f"refs/heads/{value}")


def _protected_git_ref_mutation(
    tokens: list[str], binding: AppSessionBinding | None = None
) -> bool:
    """Detect direct plumbing writes to refs that carry governance state.

    ``update-ref --stdin`` is denied because the shell payload does not expose
    the refs carried on standard input. Ordinary feature-branch ref updates
    remain subject to the normal seat mutation policy.
    """

    if not tokens or PurePosixPath(tokens[0]).name != "git":
        return False
    subcommand = _git_subcommand(tokens)
    arguments = _git_arguments(tokens)
    if subcommand == "replace":
        return not any(argument in {"-l", "--list"} for argument in arguments)
    if subcommand == "branch":
        if _git_read_form(tokens, subcommand):
            return False
        positional = [
            argument
            for argument in arguments
            if argument != "--" and not argument.startswith("-")
        ]
        if (
            binding is not None
            and len(positional) < 2
            and any(
                argument in {"-m", "-M", "-c", "-C", "--move", "--copy"}
                for argument in arguments
            )
        ):
            return True
        return any(
            _protected_branch_name(argument)
            for argument in arguments
            if argument != "--" and not argument.startswith("-")
        )
    if subcommand in {"checkout", "switch"}:
        candidates: list[str] = []
        for argument in arguments:
            if argument == "--":
                break
            if not argument.startswith("-"):
                candidates.append(argument)
        return any(_protected_branch_name(argument) for argument in candidates)
    if subcommand not in {"symbolic-ref", "update-ref"}:
        return False
    if subcommand == "update-ref" and any(
        argument == "--stdin" or argument.startswith("--stdin=")
        for argument in arguments
    ):
        return True

    index = 0
    while index < len(arguments):
        argument = arguments[index]
        if argument == "--":
            index += 1
            break
        if argument in {"-m", "--message"}:
            index += 2
            continue
        if argument.startswith("-"):
            index += 1
            continue
        break
    positional = [
        argument
        for argument in arguments[index:]
        if argument != "--" and not argument.startswith("-")
    ]
    if subcommand == "symbolic-ref":
        return len(positional) >= 2 and any(
            _protected_git_ref(argument) for argument in positional[:2]
        )
    return bool(positional) and _protected_git_ref(positional[0])


def _git_read_form(tokens: list[str], subcommand: str) -> bool:
    """Detect read-only invocations of git subcommands that can also mutate."""

    arguments = _git_arguments(tokens)
    if subcommand == "worktree":
        return bool(arguments) and arguments[0] == "list"
    if subcommand == "stash":
        return bool(arguments) and arguments[0] in {"list", "show"}
    if subcommand == "remote":
        return not arguments or arguments[0] in {"-v", "--verbose", "show", "get-url"}
    if subcommand == "config":
        return any(
            argument in {"--list", "-l"} or argument.startswith("--get")
            for argument in arguments
        )
    if subcommand == "tag":
        return not arguments or "-l" in arguments or "--list" in arguments
    if subcommand == "branch":
        if any(
            argument in _BRANCH_WRITE_FLAGS
            or argument.startswith("--set-upstream-to=")
            for argument in arguments
        ):
            return False
        return "--list" in arguments or all(
            argument.startswith("-") for argument in arguments
        )
    if subcommand == "symbolic-ref":
        if "--delete" in arguments or "-d" in arguments:
            return False
        positional = [
            argument for argument in arguments if not argument.startswith("-")
        ]
        return len(positional) <= 1
    if subcommand == "notes":
        return bool(arguments) and arguments[0] in {"list", "show"}
    return False


def _git_tree_mutation(tokens: list[str]) -> bool:
    if not tokens or PurePosixPath(tokens[0]).name != "git":
        return False
    subcommand = _git_subcommand(tokens)
    if subcommand not in _GIT_TREE_MUTATORS:
        return False
    return not _git_read_form(tokens, subcommand)


def _read_only_mailbox_invocation(program: str, arguments: list[str]) -> bool:
    if program not in _MAILBOX_WRAPPERS:
        return False
    if "--dry-run" in arguments:
        return True
    return program == "cursor_mailbox.py" and bool(arguments) and arguments[0] == "next-review"


def _python_program(tokens: list[str]) -> tuple[str, list[str]]:
    if not tokens:
        return "", []
    executable = PurePosixPath(tokens[0]).name
    if not executable.startswith("python"):
        return executable, tokens[1:]
    for index, token in enumerate(tokens[1:], start=1):
        if token == "--":
            continue
        if token.startswith("-"):
            if token in {"-m", "-c"}:
                return executable, tokens[1:]
            continue
        return PurePosixPath(token).name, tokens[index + 1 :]
    return executable, []


def _shell_script_effect(tokens: list[str]) -> str | None:
    """Classify ``bash path/to/writer`` wrappers that otherwise look like reads."""

    if not tokens or PurePosixPath(tokens[0]).name not in {"bash", "dash", "sh", "zsh"}:
        return None
    if len(tokens) < 2 or tokens[1].startswith("-"):
        return None
    script = PurePosixPath(tokens[1]).name
    arguments = tokens[2:]
    if script in _FOREIGN_LAUNCHERS:
        return "launcher"
    if script in _DIRECT_EFFECTS:
        return "direct"
    if script in _MAILBOX_WRAPPERS:
        return None if _read_only_mailbox_invocation(script, arguments) else "mailbox"
    return None


def _effect(tokens: list[str]) -> str | None:
    program, arguments = _python_program(tokens)
    if program in _FOREIGN_LAUNCHERS:
        return "launcher"
    if program in _DIRECT_EFFECTS:
        return "direct"
    if program in _MAILBOX_WRAPPERS:
        return None if _read_only_mailbox_invocation(program, arguments) else "mailbox"
    wrapped = _shell_script_effect(tokens)
    if wrapped is not None:
        return wrapped
    if PurePosixPath(tokens[0]).name == "git":
        subcommand = _git_subcommand(tokens)
        if subcommand in _EXTERNAL_GIT_EFFECTS:
            return "external-git"
    if PurePosixPath(tokens[0]).name == "sudo":
        return "direct"
    return None


def _opaque_execution(tokens: list[str]) -> bool:
    if not tokens:
        return True
    executable = PurePosixPath(tokens[0]).name
    if executable in {"bash", "dash", "sh", "zsh"} and "-c" in tokens[1:]:
        return True
    if executable.startswith("python") and "-c" in tokens[1:]:
        return True
    if executable in {"node", "perl", "ruby"} and any(
        flag in tokens[1:] for flag in ("-e", "--eval")
    ):
        return True
    return False


def _embedded_redirect_path(token: str) -> str | None:
    """Return a path from glued redirects such as ``x>production.py``."""

    if ">&" in token:
        return None
    for operator in (">>", ">"):
        if operator in token and not token.startswith(operator):
            path = token.rsplit(operator, 1)[1]
            if path and not path.startswith("-"):
                return path
    return None


def _write_paths(tokens: list[str]) -> list[str]:
    paths: list[str] = []
    for index, token in enumerate(tokens):
        match = _REDIRECT.match(token)
        if match and match.group("path"):
            # File-descriptor duplication (2>&1, >&2) writes no file.
            if not match.group("path").startswith("&"):
                paths.append(match.group("path"))
            continue
        embedded = _embedded_redirect_path(token)
        if embedded is not None:
            paths.append(embedded)
            continue
        if token in {">", ">>", "1>", "1>>", "2>", "2>>"} and index + 1 < len(tokens):
            paths.append(tokens[index + 1])
    program = PurePosixPath(tokens[0]).name if tokens else ""
    if program == "git":
        paths.extend(_git_output_paths(tokens))
    if program in _MUTATING_FILE_COMMANDS:
        paths.extend(
            token
            for token in tokens[1:]
            if not token.startswith("-") and not token.startswith("+")
        )
    return paths


def _git_output_paths(tokens: list[str]) -> list[str]:
    paths: list[str] = []
    for index, token in enumerate(tokens):
        if token == "--output" and index + 1 < len(tokens):
            paths.append(tokens[index + 1])
        elif token.startswith("--output="):
            paths.append(token.split("=", 1)[1])
    return paths


def _outside_git_mutation(tokens: list[str], *, root: Path) -> bool:
    if not tokens or PurePosixPath(tokens[0]).name != "git":
        return False
    subcommand = _git_subcommand(tokens)
    mutating = (
        subcommand in _GIT_TREE_MUTATORS or subcommand in _EXTERNAL_GIT_EFFECTS
    )
    index = 1
    while index < len(tokens):
        token = tokens[index]
        if token in {"-C", "--git-dir", "--work-tree"} and index + 1 < len(tokens):
            if mutating and _outside_workspace(tokens[index + 1], root=root):
                return True
            index += 2
            continue
        attached = next(
            (
                token[len(prefix):]
                for prefix in ("-C", "--git-dir=", "--work-tree=")
                if token.startswith(prefix) and token != prefix
            ),
            None,
        )
        if attached is not None and mutating and _outside_workspace(attached, root=root):
            return True
        index += 1
    if subcommand == "config" and not _git_read_form(tokens, subcommand):
        arguments = _git_arguments(tokens)
        if any(argument in {"--global", "--system"} for argument in arguments):
            return True
        for index, argument in enumerate(arguments):
            if argument == "--file" and index + 1 < len(arguments):
                return _outside_workspace(arguments[index + 1], root=root)
            if argument.startswith("--file="):
                return _outside_workspace(argument.split("=", 1)[1], root=root)
    if any(_outside_workspace(path, root=root) for path in _git_output_paths(tokens)):
        return True
    return False


def _unsafe_inspection_options(tokens: list[str]) -> bool:
    """Recognize command options that turn an apparent reader into a writer/exec."""

    if not tokens:
        return False
    program = PurePosixPath(tokens[0]).name
    if program == "find":
        dangerous = ("-delete", "-exec", "-execdir", "-ok", "-okdir", "-fprint", "-fprintf", "-fls")
        return any(
            token == option or token.startswith(option)
            for token in tokens[1:]
            for option in dangerous
        )
    if program == "sort":
        return any(
            token == "-o"
            or (token.startswith("-o") and token != "-o")
            or token == "--output"
            or token.startswith("--output=")
            or token.startswith("--compress-program")
            for token in tokens[1:]
        )
    if program == "rg":
        return any(token == "--pre" or token.startswith("--pre=") for token in tokens[1:])
    if program == "git":
        subcommand = _git_subcommand(tokens)
        arguments = _git_arguments(tokens)
        if subcommand == "grep" and any(
            token == "-O"
            or (token.startswith("-O") and token != "-O")
            or token == "--open-files-in-pager"
            or token.startswith("--open-files-in-pager=")
            for token in arguments
        ):
            return True
        return any(
            token in {"--ext-diff", "--textconv", "--paginate"}
            or token.startswith("--output=")
            or token == "--output"
            for token in tokens[1:]
        )
    return False


def _trusted_inspection_executable(
    tokens: list[str], *, root: Path, environ: Mapping[str, str]
) -> bool:
    """Do not grant reader semantics to a spoofed executable with a trusted basename."""

    if not tokens:
        return False
    raw = tokens[0]
    name = PurePosixPath(raw).name
    if name in {"[", "cd", "echo", "false", "pwd", "test", "true"}:
        return "/" not in raw
    normalized = _normalized_path(raw, root=root) if "/" in raw else ""
    if normalized == "coordination/bin/cursor-seat":
        return True
    if "/" in raw:
        candidate = Path(raw)
        if not candidate.is_absolute():
            candidate = root / candidate
    else:
        # An explicitly supplied PATH is part of the command's provenance. If
        # the hook payload omits PATH, use the platform's non-user default
        # rather than this policy process's ambient PATH. ``python`` is kept as
        # a compatibility spelling in that synthetic/no-PATH posture: when it
        # is absent from os.defpath the shell cannot dispatch an attacker-owned
        # executable through PATH, and the command will simply fail to launch.
        resolved = shutil.which(raw, path=environ.get("PATH", os.defpath))
        if resolved is None:
            return "PATH" not in environ and (
                name == "python" or name in _INSPECTION_PROGRAMS
            )
        candidate = Path(resolved)
    absolute = candidate.absolute()
    if _ephemeral_write(str(absolute)):
        return False
    try:
        resolved_path = candidate.resolve(strict=True)
    except OSError:
        return False
    if _ephemeral_write(str(resolved_path)):
        return False
    try:
        relative = resolved_path.relative_to(root.resolve())
    except ValueError:
        return resolved_path.is_file()
    return len(relative.parts) >= 2 and relative.parts[:2] == (".venv", "bin")


def _seat_mailbox_commit(
    tokens: list[str], *, root: Path, binding: AppSessionBinding | None
) -> bool:
    if (
        binding is None
        or not tokens
        or PurePosixPath(tokens[0]).name != "git"
        or _git_subcommand(tokens) != "commit"
        or "--only" not in tokens
        or "--" not in tokens
        or not any(
            token == "-m" or token.startswith("--message=") for token in tokens
        )
        or any(flag in tokens for flag in ("--amend", "--all", "--include", "-a"))
    ):
        return False
    marker = tokens.index("--")
    paths = tokens[marker + 1 :]
    if len(paths) != 1:
        return False
    normalized = _normalized_path(paths[0], root=root)
    expected_prefix = "coordination/mailbox/sent/"
    if not normalized.startswith(expected_prefix):
        return False
    name = PurePosixPath(normalized).name
    match = _MAILBOX_EVENT_NAME.fullmatch(name)
    return match is not None and match.group("sender") == binding.seat


def _writes_protected(tokens: list[str], *, root: Path) -> bool:
    for index, token in enumerate(tokens):
        match = _REDIRECT.match(token)
        if match and match.group("path") and _protected(match.group("path"), root=root):
            return True
        embedded = _embedded_redirect_path(token)
        if embedded is not None and _protected(embedded, root=root):
            return True
        if token in {">", ">>", "1>", "1>>", "2>", "2>>"} and index + 1 < len(tokens):
            if _protected(tokens[index + 1], root=root):
                return True
    program = PurePosixPath(tokens[0]).name if tokens else ""
    return program in _MUTATING_FILE_COMMANDS and any(
        _protected(token, root=root) for token in tokens[1:]
    )


def _tool_paths(tool_input: Mapping[str, Any]) -> list[object]:
    paths = [
        tool_input[key]
        for key in ("path", "file_path", "target_file")
        if key in tool_input
    ]
    patch = tool_input.get("patch") or tool_input.get("diff")
    if isinstance(patch, str):
        paths.extend(
            match.group(1).strip()
            for match in re.finditer(
                r"^\*\*\* (?:Add|Update|Delete) File: (.+)$",
                patch,
                re.MULTILINE,
            )
        )
    return paths


def _role_prompt(root: Path, binding: AppSessionBinding) -> str:
    role = (
        "director"
        if binding.seat in DIRECTOR_SEATS
        else "coordinator"
        if binding.seat == "coordinator"
        else "operator"
    )
    path = root / "docs" / "protocol" / "cursor" / "roles" / f"{role}.md"
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        return f"Pipeline Cursor app seat: {binding.seat}."


def _bound_session(
    *,
    root: Path,
    registry_path: Path,
    environ: Mapping[str, str],
    payload: Mapping[str, Any] | None = None,
) -> AppSessionBinding | None:
    if environ.get("GIT_INDEX_FILE"):
        return None
    try:
        return resolve_registered_session(
            root,
            environ,
            registry_path=registry_path,
            payload=payload,
        )
    except AppBindingError:
        return None


_ORIENTATION_PYTHON = frozenset(
    {
        "ci_smoke.py",
        "governance_verify_all.py",
        "cursor_land_gate.py",
        "cursor_review_snapshot.py",
        "ledger_start_guard.py",
        "status.py",
        "target_binding.py",
    }
)


def _free_inspection(
    tokens: list[str], *, root: Path, environ: Mapping[str, str]
) -> bool:
    """True for classified non-mutating inspection forms that may auto-allow."""

    if not tokens:
        return False
    durable_writes = [
        path for path in _write_paths(tokens) if not _ephemeral_write(path)
    ]
    if durable_writes or _git_tree_mutation(tokens):
        return False
    if not _trusted_inspection_executable(tokens, root=root, environ=environ):
        return False
    program = PurePosixPath(tokens[0]).name
    if program == "git":
        subcommand = _git_subcommand(tokens)
        if not subcommand or subcommand in _EXTERNAL_GIT_EFFECTS:
            return False
        if subcommand in _GIT_TREE_MUTATORS:
            return _git_read_form(tokens, subcommand)
        return subcommand in _GIT_INSPECTION_COMMANDS
    name, arguments = _python_program(tokens)
    if name == "pytest" or (
        program.startswith("python")
        and "-m" in tokens[1:]
        and "pytest" in tokens[1:]
    ):
        return True
    if name in _ORIENTATION_PYTHON:
        return True
    if name in _MAILBOX_WRAPPERS and _read_only_mailbox_invocation(name, arguments):
        return True
    if program == "cursor-seat" or tokens[0].rstrip("/").endswith("/cursor-seat"):
        return any(argument in {"status", "readiness"} for argument in tokens[1:])
    if program in _MUTATING_FILE_COMMANDS:
        # Classified mutators whose only targets were ephemeral (e.g. /tmp).
        return bool(_write_paths(tokens)) and not durable_writes
    return program in _INSPECTION_PROGRAMS


def _shell_decision(
    payload: Mapping[str, Any],
    *,
    root: Path,
    registry_path: Path,
    environ: Mapping[str, str],
) -> dict[str, str]:
    command = payload.get("command")
    if not isinstance(command, str) or not command.strip():
        return _deny("Cursor hook received malformed shell input.")
    child = _subagent(payload)
    binding = _bound_session(
        root=root,
        registry_path=registry_path,
        environ=environ,
        payload=payload,
    )
    director = binding is not None and binding.seat in DIRECTOR_SEATS and not child
    posture = binding.seat if binding is not None else "readiness"
    segments = _segments(command)
    if not segments:
        if child:
            return _deny("Cursor subagents may use only auditable shell syntax.")
        return _ask(
            "Cursor cannot statically classify this shell syntax; approve one run?"
        )
    pending_ask: dict[str, str] | None = None
    for raw in segments:
        if _unsafe_environment_prefix(raw):
            return _deny(
                "Execution-bearing environment overrides are not allowed in Cursor shell commands."
            )
        if _unresolved_shell_expansion(raw):
            if child:
                return _deny("Cursor subagents may not use unresolved shell expansion.")
            pending_ask = pending_ask or _ask(
                f"Approve one shell command with unresolved expansion as {posture}?"
            )
            continue
        tokens = _unwrap_prefixes(raw)
        if not tokens:
            return _deny("Cursor hook could not resolve the shell executable.")
        if len(segments) > 1 and PurePosixPath(tokens[0]).name == "cd":
            if child:
                return _deny("Cursor subagents may not change shell context across commands.")
            pending_ask = pending_ask or _ask(
                f"Approve one compound command with a directory change as {posture}?"
            )
            continue
        if _opaque_execution(tokens):
            if child:
                return _deny(
                    "Cursor subagents may not run opaque interpreter commands."
                )
            pending_ask = pending_ask or _ask(
                f"Approve one opaque interpreter command in this {posture} session?"
            )
            continue
        if _unsafe_git_dispatch(tokens):
            return _deny(
                "Git inline aliases and unknown subcommands are not auditable; "
                "use a literal built-in Git command."
            )
        effect = _effect(tokens)
        if effect == "launcher":
            return _deny("Cursor app seats do not launch CLI or foreign provider seats.")
        if effect == "direct":
            return _deny(
                "Use the Cursor mailbox wrappers; direct fixed-writer effects are denied."
            )
        if effect == "external-git":
            if _outside_git_mutation(tokens, root=root):
                return _deny("Git effects must target the bound app worktree.")
            if child:
                return _deny(
                    "Separately authorized Git effects require a top-level session."
                )
            pending_ask = pending_ask or _ask(
                "Approve one separately authorized Git effect "
                f"({_git_subcommand(tokens)}) as {posture}?"
            )
            continue
        if effect == "mailbox":
            if binding is None or child:
                return _deny(
                    "Mailbox effects require a bound top-level Cursor app seat."
                )
            # Standing Director/Operator: seat-start is the local mailbox grant.
            if binding.seat in DIRECTOR_SEATS or binding.seat in OPERATOR_SEATS:
                continue
            pending_ask = pending_ask or _ask(
                f"Approve one mailbox effect as {binding.seat} "
                f"from model {binding.model_id}?"
            )
            continue
        if _outside_git_mutation(tokens, root=root):
            return _deny("Git mutations must remain inside the bound app worktree.")
        if _protected_git_ref_mutation(tokens, binding):
            return _deny(
                "Direct mutation of protected governance refs is forbidden; "
                "use the owning fixed writer or separately authorized gate."
            )
        if _unsafe_inspection_options(tokens):
            if child:
                return _deny(
                    "Cursor subagents may not use inspection options that write or execute."
                )
            pending_ask = pending_ask or _ask(
                f"Approve one command whose inspection options can write or execute as {posture}?"
            )
            continue
        if _writes_protected(tokens, root=root):
            return _deny(
                "Direct writes to mailbox, lock, or Cursor runtime state are forbidden."
            )
        write_paths = [
            path for path in _write_paths(tokens) if not _ephemeral_write(path)
        ]
        outside = [
            path for path in write_paths if _outside_workspace(path, root=root)
        ]
        if outside:
            if child:
                return _deny("Cursor subagents may not write outside the workspace.")
            pending_ask = pending_ask or _ask(
                f"Approve one write outside the workspace ({outside[0]})?"
            )
            continue
        repo_write = any(
            _repo_path(path, root=root) for path in write_paths
        ) or _git_tree_mutation(tokens)
        scratch_only = bool(write_paths) and all(
            _scratch(path, root=root) for path in write_paths
        ) and not _git_tree_mutation(tokens)
        if _seat_mailbox_commit(tokens, root=root, binding=binding) and not child:
            continue
        if repo_write:
            if child:
                return _deny("Cursor subagents cannot mutate the repository tree.")
            if director:
                continue
            pending_ask = pending_ask or _ask(
                f"Approve one repository mutation in this {posture} session?"
            )
            continue
        if scratch_only or _free_inspection(tokens, root=root, environ=environ):
            continue
        if child:
            return _deny(
                "Cursor subagents may run only classified non-mutating shell forms."
            )
        pending_ask = pending_ask or _ask(
            f"Approve one unclassified shell command in this {posture} session?"
        )
    return pending_ask or _allow()


def evaluate(
    payload: Mapping[str, Any],
    environ: Mapping[str, str] | None = None,
    *,
    root: Path | None = None,
    registry_path: Path = DEFAULT_REGISTRY_PATH,
) -> dict[str, Any]:
    env = os.environ if environ is None else environ
    workspace = _PROJECT_ROOT if root is None else root.resolve()
    event = payload.get("hook_event_name")
    if event == "sessionStart":
        if env.get("GIT_INDEX_FILE"):
            return {
                "additional_context": (
                    "Pipeline Cursor posture: readiness-bridge. "
                    "App worktree seats refuse inherited GIT_INDEX_FILE."
                )
            }
        try:
            binding = register_payload_session(
                workspace, payload, registry_path=registry_path
            )
        except AppBindingError as exc:
            return {
                "additional_context": (
                    "Pipeline Cursor posture: readiness-bridge. "
                    f"Seat binding was not established: {exc}"
                )
            }
        if binding is None:
            return {
                "additional_context": (
                    "Pipeline Cursor posture: readiness-bridge. "
                    "Open a reserved cursor-seat/<seat> linked worktree for a named seat."
                )
            }
        return {
            "env": session_environment(binding),
            "additional_context": _role_prompt(workspace, binding),
        }
    binding = _bound_session(
        root=workspace,
        registry_path=registry_path,
        environ=env,
        payload=payload,
    )
    if event == "subagentStart":
        task = payload.get("task", "")
        if isinstance(task, str) and re.search(
            r"\b(director2?|operator2?|coordinator2?)\s+seat\b|\bissue\s+(go|nits|fail)\b",
            task,
            re.IGNORECASE,
        ):
            return _deny("Cursor subagents are advisors and cannot impersonate a seat.")
        # Bound seats may launch parent-scoped advisors/capacity workers; the
        # child rules still deny repo mutation, mailbox effects, opaque shell,
        # and seat authority inheritance regardless of who launched them.
        return _allow()
    if event == "beforeShellExecution":
        return _shell_decision(
            payload,
            root=workspace,
            registry_path=registry_path,
            environ=env,
        )
    if event == "beforeMCPExecution":
        tool = payload.get("tool_name")
        raw_input = payload.get("tool_input")
        server = payload.get("url") or payload.get("command")
        if not isinstance(tool, str) or not tool.strip():
            return _deny("Cursor MCP hook received a malformed tool name.")
        if isinstance(raw_input, str):
            try:
                tool_input = json.loads(raw_input)
            except json.JSONDecodeError:
                return _deny("Cursor MCP hook received malformed JSON parameters.")
        else:
            tool_input = raw_input
        if not isinstance(tool_input, dict):
            return _deny("Cursor MCP hook requires object-shaped JSON parameters.")
        if not isinstance(server, str) or not server.strip():
            return _deny("Cursor MCP hook could not identify the MCP server.")
        display_tool = " ".join(tool.split())[:120]
        return _ask(
            f"Approve one MCP invocation of {display_tool}? "
            "This approval does not grant external-effect authority."
        )
    if event == "preToolUse":
        tool_input = payload.get("tool_input")
        if not isinstance(tool_input, dict):
            return _deny("Cursor hook received malformed tool input.")
        tool = payload.get("tool_name")
        if tool in {"Shell", "Task"} or (
            isinstance(tool, str) and tool.startswith("MCP")
        ):
            # Owned by beforeShellExecution / subagentStart /
            # beforeMCPExecution; a second preToolUse gate here would
            # double-evaluate the same action.
            return _allow()
        if tool in {"Write", "Delete", "Edit", "ApplyPatch"}:
            paths = _tool_paths(tool_input)
            if not paths:
                return _deny("Cursor hook could not resolve the edited file path.")
            if any(_outside_workspace(path, root=workspace) for path in paths):
                return _deny("Cursor app-seat file edits must remain inside the worktree.")
            if any(_protected(path, root=workspace) for path in paths):
                return _deny(
                    "Direct edits to mailbox, lock, or Cursor runtime state are forbidden."
                )
            if all(_scratch(path, root=workspace) for path in paths):
                # Scratch is free everywhere, matching the shell rule.
                return _allow()
            if _subagent(payload):
                return _deny("Cursor subagents cannot inherit top-level seat authority.")
            if binding is not None and binding.seat in DIRECTOR_SEATS:
                return _allow()
            posture = binding.seat if binding is not None else "readiness"
            return _deny(
                "Cursor does not currently enforce preToolUse approval for file "
                f"edits in this {posture} session. Use a bound Director or an "
                "approved shell mutation."
            )
        return _deny(
            f"Cursor hook policy has no preToolUse rule for tool {tool!r}; "
            "denying by default. Extend .cursor/hooks.json and "
            "cursor_hook_policy.py together for a new mutating tool."
        )
    return _deny(
        f"Cursor hook policy does not handle hook event {event!r}; "
        "denying by default. Wire new events through .cursor/hooks.json and "
        "cursor_hook_policy.py together."
    )


def process_bytes(
    raw: bytes,
    *,
    event_hint: str | None,
    environ: Mapping[str, str] | None = None,
    root: Path | None = None,
    registry_path: Path = DEFAULT_REGISTRY_PATH,
) -> tuple[str, int]:
    try:
        payload = json.loads(raw.decode("utf-8"))
        if not isinstance(payload, dict):
            raise ValueError("hook payload is not an object")
    except (UnicodeError, json.JSONDecodeError, ValueError):
        # Fail closed regardless of which event produced the bytes. For
        # events without permission semantics (sessionStart) the deny fields
        # are inert, which still degrades to an unbound readiness session.
        return (
            json.dumps(
                _deny(
                    "Malformed input was denied by the fail-closed Cursor app hook."
                )
            ),
            0,
        )
    if event_hint and "hook_event_name" not in payload:
        payload["hook_event_name"] = event_hint
    return (
        json.dumps(
            evaluate(
                payload,
                environ,
                root=root,
                registry_path=registry_path,
            )
        ),
        0,
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--event")
    args = parser.parse_args(sys.argv[1:] if argv is None else argv)
    output, status = process_bytes(
        sys.stdin.buffer.read(),
        event_hint=args.event,
        environ=os.environ,
    )
    print(output)
    return status


if __name__ == "__main__":
    raise SystemExit(main())
