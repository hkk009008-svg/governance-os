#!/usr/bin/env python3
"""Write-governed Cursor Desktop guardrails for Pipeline app seats.

Reads are free. Repository mutations are role-governed: Director worktree
chats mutate freely, every other top-level posture receives one in-app
approval. Separately authorized effects (mailbox, push, pull, fetch, merge,
rebase, cherry-pick) always surface one in-app approval. Hard denies are
reserved for protected coordination surfaces, direct fixed-writer calls,
foreign provider launchers, and subagent seat impersonation.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shlex
import sys
from collections.abc import Mapping, Sequence
from pathlib import Path, PurePosixPath
from typing import Any

try:
    from scripts.cursor_app_binding import (
        DEFAULT_REGISTRY_PATH,
        DIRECTOR_SEATS,
        AppBindingError,
        AppSessionBinding,
        register_payload_session,
        resolve_registered_session,
        session_environment,
    )
except ModuleNotFoundError as exc:
    if exc.name != "scripts":
        raise
    from cursor_app_binding import (  # type: ignore[no-redef]
        DEFAULT_REGISTRY_PATH,
        DIRECTOR_SEATS,
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
_MAILBOX_EVENT_NAME = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}-\d{2}-\d{2}Z-"
    r"(?P<sender>director2?|operator2?|coordinator)-to-"
    r"(?:director2?|operator2?|coordinator|all)-[a-z0-9-]+\.md$"
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


def _subagent(payload: Mapping[str, Any]) -> bool:
    return any(
        key in payload
        for key in ("subagent_id", "subagent_type", "parent_conversation_id")
    )


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


def _segments(command: str) -> list[list[str]]:
    """Parse simple shell segments; opaque syntax yields no segments."""

    if any(token in command for token in ("\n", "$(", "`", "<(", ">(")):
        return []
    try:
        lexer = shlex.shlex(command, posix=True, punctuation_chars=";&|")
        lexer.whitespace_split = True
        tokens = list(lexer)
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
    return "--dry-run" in arguments or "next-review" in arguments


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


def _effect(tokens: list[str]) -> str | None:
    program, arguments = _python_program(tokens)
    if program in _FOREIGN_LAUNCHERS:
        return "launcher"
    if program in _DIRECT_EFFECTS:
        return "direct"
    if program in _MAILBOX_WRAPPERS:
        return None if _read_only_mailbox_invocation(program, arguments) else "mailbox"
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


def _write_paths(tokens: list[str]) -> list[str]:
    paths: list[str] = []
    for index, token in enumerate(tokens):
        match = _REDIRECT.match(token)
        if match and match.group("path"):
            # File-descriptor duplication (2>&1, >&2) writes no file.
            if not match.group("path").startswith("&"):
                paths.append(match.group("path"))
        elif token in {">", ">>", "1>", "1>>", "2>", "2>>"} and index + 1 < len(tokens):
            paths.append(tokens[index + 1])
    program = PurePosixPath(tokens[0]).name if tokens else ""
    if program in _MUTATING_FILE_COMMANDS:
        paths.extend(
            token
            for token in tokens[1:]
            if not token.startswith("-") and not token.startswith("+")
        )
    return paths


def _outside_git_mutation(tokens: list[str], *, root: Path) -> bool:
    if not tokens or PurePosixPath(tokens[0]).name != "git":
        return False
    subcommand = _git_subcommand(tokens)
    if (
        subcommand not in _GIT_TREE_MUTATORS
        and subcommand not in _EXTERNAL_GIT_EFFECTS
    ):
        return False
    for index, token in enumerate(tokens[:-1]):
        if token == "-C":
            return _outside_workspace(tokens[index + 1], root=root)
    return False


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
) -> AppSessionBinding | None:
    if environ.get("GIT_INDEX_FILE"):
        return None
    try:
        return resolve_registered_session(
            root, environ, registry_path=registry_path
        )
    except AppBindingError:
        return None


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
        root=root, registry_path=registry_path, environ=environ
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
        tokens = _unwrap_env(raw)
        if not tokens:
            return _deny("Cursor hook could not resolve the shell executable.")
        if _opaque_execution(tokens):
            if child:
                return _deny(
                    "Cursor subagents may not run opaque interpreter commands."
                )
            pending_ask = pending_ask or _ask(
                f"Approve one opaque interpreter command in this {posture} session?"
            )
            continue
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
            pending_ask = pending_ask or _ask(
                f"Approve one mailbox effect as {binding.seat} "
                f"from model {binding.model_id}?"
            )
            continue
        if _outside_git_mutation(tokens, root=root):
            return _deny("Git mutations must remain inside the bound app worktree.")
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
        if not repo_write:
            continue
        if _seat_mailbox_commit(tokens, root=root, binding=binding) and not child:
            continue
        if child:
            return _deny("Cursor subagents cannot mutate the repository tree.")
        if director:
            continue
        pending_ask = pending_ask or _ask(
            f"Approve one repository mutation in this {posture} session?"
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
        root=workspace, registry_path=registry_path, environ=env
    )
    if event == "subagentStart":
        if binding is not None:
            return _deny(
                "Durable Cursor app seats are top-level chats; use an unbound advisor chat."
            )
        task = payload.get("task", "")
        if isinstance(task, str) and re.search(
            r"\b(director2?|operator2?|coordinator)\s+seat\b|\bissue\s+(go|nits|fail)\b",
            task,
            re.IGNORECASE,
        ):
            return _deny("Cursor subagents are advisors and cannot impersonate a seat.")
        return _allow()
    if event == "beforeShellExecution":
        return _shell_decision(
            payload,
            root=workspace,
            registry_path=registry_path,
            environ=env,
        )
    if event == "preToolUse":
        tool_input = payload.get("tool_input")
        if not isinstance(tool_input, dict):
            return _deny("Cursor hook received malformed tool input.")
        tool = payload.get("tool_name")
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
            if _subagent(payload):
                return _deny("Cursor subagents cannot inherit top-level seat authority.")
            if binding is not None and binding.seat in DIRECTOR_SEATS:
                return _allow()
            if all(_scratch(path, root=workspace) for path in paths):
                return _allow()
            posture = binding.seat if binding is not None else "readiness"
            return _ask(
                f"Approve one repository file edit in this {posture} session?"
            )
        return _allow()
    return _allow()


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
        result = (
            _deny("Malformed input was denied by the fail-closed Cursor app hook.")
            if event_hint in {"beforeShellExecution", "preToolUse", "subagentStart"}
            else {}
        )
        return json.dumps(result), 0
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
