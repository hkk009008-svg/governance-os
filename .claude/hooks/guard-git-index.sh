#!/usr/bin/env bash
# PreToolUse(Bash|Write|Edit): fail closed unless the current Claude session is
# bound to its exact provider-prefixed regular seat index. Invalid sessions may
# perform a conservative read-only Bash subset, but no mutation.
set -uo pipefail

PAYLOAD=$(cat 2>/dev/null || true)
ROOT="${CLAUDE_PROJECT_DIR:-}"
if [ -z "$ROOT" ]; then
  ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." 2>/dev/null && pwd) || exit 2
fi
command -v python3 >/dev/null 2>&1 || {
  echo "BLOCKED: python3 unavailable; cannot validate Claude seat binding." >&2
  exit 2
}

exec python3 - "$ROOT" "$PAYLOAD" <<'PY'
import json
import os
import re
import shlex
import stat
import subprocess
import sys
from pathlib import Path

SEATS = {"director", "director2", "operator", "operator2"}
SAFE_GIT = {
    "cat-file", "describe", "diff", "grep", "log", "ls-files", "ls-tree",
    "merge-base", "name-rev", "rev-list", "rev-parse", "show", "status",
}
SAFE_COMMANDS = {
    "cat", "cut", "echo", "file", "grep", "head", "ls", "md5", "pwd",
    "rg", "sed", "sha256sum", "shasum", "sort", "stat", "tail", "test",
    "tr", "uniq", "wc", "[",
}
GIT_MUTATORS = {
    "add", "apply", "checkout", "cherry-pick", "clean", "commit", "merge",
    "mv", "read-tree", "rebase", "reset", "restore", "rm", "stash", "switch",
    "update-index",
}


def deny(message: str) -> None:
    sys.stderr.write(f"BLOCKED: {message}\n")
    raise SystemExit(2)


def clean_git_env() -> dict[str, str]:
    return {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}


def cursor_policy_decision(root: Path, data: dict[str, object]) -> dict[str, object] | None:
    cursor_root = os.environ.get("CURSOR_PROJECT_DIR", "")
    if not (
        cursor_root
        and os.environ.get("CURSOR_VERSION")
        and os.environ.get("CLAUDE_PROJECT_DIR") == cursor_root
    ):
        return None
    try:
        workspace = Path(cursor_root).resolve(strict=True)
    except OSError:
        deny("Cursor compatibility host root is unavailable")
    if workspace != root.resolve():
        deny("Cursor and Claude compatibility roots disagree")
    cursor_data = dict(data)
    tool = cursor_data.get("tool_name")
    tool_input = cursor_data.get("tool_input")
    if tool in {"Bash", "Shell"}:
        cursor_data["hook_event_name"] = "beforeShellExecution"
        if isinstance(tool_input, dict):
            cursor_data["command"] = tool_input.get("command", "")
    else:
        cursor_data["hook_event_name"] = "preToolUse"
    cursor_data.setdefault(
        "conversation_id", os.environ.get("CURSOR_APP_CONVERSATION_ID", "")
    )
    cursor_data.setdefault("model_id", os.environ.get("CURSOR_APP_MODEL_ID", ""))
    sys.path.insert(0, str(workspace))
    try:
        from scripts import cursor_hook_policy

        result = cursor_hook_policy.evaluate(
            cursor_data,
            os.environ,
            root=workspace,
        )
    except Exception as exc:
        deny(f"Cursor compatibility policy failed closed: {exc}")
    if not isinstance(result, dict):
        deny("Cursor compatibility policy returned no decision")
    if result.get("permission") == "ask":
        # This compatibility host has no in-app approval surface; the
        # approval-gated action must run from the Cursor app seat chat.
        message = (
            "Cursor in-app approval is unavailable in this compatibility host; "
            "run this action from the bound Cursor app seat chat."
        )
        return {
            "permission": "deny",
            "user_message": message,
            "agent_message": message,
        }
    return result


def binding_is_valid(root: Path, data: dict[str, object]) -> bool:
    if "agent_id" in data or "agent_type" in data:
        return False
    seat = os.environ.get("CLAUDE_SEAT", "")
    raw_index = os.environ.get("GIT_INDEX_FILE", "")
    if seat not in SEATS or not raw_index:
        return False
    result = subprocess.run(
        ["git", "-C", str(root), "rev-parse", "--absolute-git-dir"],
        env=clean_git_env(),
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        return False
    expected = Path(result.stdout.strip()) / f"index-claude-{seat}"
    index = Path(raw_index)
    if not index.is_absolute() or os.path.normpath(str(index)) != str(expected):
        return False
    try:
        if not stat.S_ISREG(index.lstat().st_mode):
            return False
    except OSError:
        return False
    index_env = clean_git_env()
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
            env=clean_git_env(),
            text=True,
            capture_output=True,
            check=False,
        )
        if head_entries.returncode != 0 or head_entries.stdout:
            return False
    status_result = subprocess.run(
        [
            "git", "--no-optional-locks", "-C", str(root), "status",
            "--porcelain=v1", "--untracked-files=no", "--ignore-submodules=all",
        ],
        env=index_env,
        text=True,
        capture_output=True,
        check=False,
    )
    return status_result.returncode == 0


def segments(command: str) -> list[list[str]] | None:
    if any(token in command for token in ("$(", "`", ">", "<", "\n")):
        return None
    parsed: list[list[str]] = []
    for part in re.split(r"&&|\|\||;|\|", command):
        try:
            tokens = shlex.split(part)
        except ValueError:
            return None
        if tokens:
            parsed.append(tokens)
    return parsed or None


def unwrap_env(tokens: list[str]) -> tuple[list[str], bool]:
    if Path(tokens[0]).name != "env":
        return tokens, False
    index = 1
    unset_index = False
    while index < len(tokens):
        if tokens[index] == "-u" and index + 1 < len(tokens):
            unset_index = unset_index or tokens[index + 1] == "GIT_INDEX_FILE"
            index += 2
            continue
        if tokens[index] == "--":
            index += 1
            break
        if tokens[index].startswith("-") or "=" in tokens[index]:
            return [], False
        break
    return tokens[index:], unset_index


def git_subcommand(tokens: list[str]) -> str | None:
    index = 1
    while index < len(tokens):
        token = tokens[index]
        if token == "-C" and index + 1 < len(tokens):
            index += 2
            continue
        if token in {"--no-pager", "--no-optional-locks", "--literal-pathspecs"}:
            index += 1
            continue
        if token.startswith("-"):
            return None
        return token
    return None


def read_only_shell(command: str) -> bool:
    parsed = segments(command)
    if parsed is None:
        return False
    for raw in parsed:
        tokens, unset_index = unwrap_env(raw)
        if not tokens:
            return False
        command_name = Path(tokens[0]).name
        if command_name == "git":
            if git_subcommand(tokens) not in SAFE_GIT:
                return False
            if "--no-optional-locks" not in tokens[1:]:
                return False
            if os.environ.get("GIT_INDEX_FILE") and not unset_index:
                return False
            continue
        if command_name == "sed" and any(token.startswith("-i") for token in tokens[1:]):
            return False
        if command_name == "find" or command_name not in SAFE_COMMANDS:
            return False
    return True


def valid_binding_bash_is_safe(command: str) -> bool:
    parsed = segments(command)
    if parsed is None:
        return False
    for raw in parsed:
        tokens, unset_index = unwrap_env(raw)
        if not tokens:
            return False
        command_name = Path(tokens[0]).name
        if command_name == "pytest" and not unset_index:
            return False
        if command_name.startswith("python") and not unset_index:
            if any(
                tokens[i] == "-m" and i + 1 < len(tokens) and tokens[i + 1] == "pytest"
                for i in range(1, len(tokens))
            ):
                return False
        if command_name == "git" and git_subcommand(tokens) in GIT_MUTATORS and not unset_index:
            return False
    return True


try:
    data = json.loads(sys.argv[2])
except Exception:
    deny("malformed hook payload; mutation authority cannot be established")
if not isinstance(data, dict):
    deny("non-object hook payload; mutation authority cannot be established")
root = Path(sys.argv[1])
tool = data.get("tool_name")
tool_input = data.get("tool_input")
command = tool_input.get("command", "") if isinstance(tool_input, dict) else ""
cursor_result = cursor_policy_decision(root, data)
if cursor_result is not None:
    print(json.dumps(cursor_result))
    raise SystemExit(0)
valid = binding_is_valid(root, data)

if tool in {"Write", "Edit"}:
    if valid:
        raise SystemExit(0)
    deny("Write/Edit requires exact CLAUDE_SEAT and index-claude-<same-seat> binding")
if tool == "Bash":
    if not isinstance(command, str) or not command:
        deny("Bash payload has no auditable command")
    if valid:
        if valid_binding_bash_is_safe(command):
            raise SystemExit(0)
        deny("seat-bound Git mutators and pytest require exact env -u GIT_INDEX_FILE")
    if read_only_shell(command):
        raise SystemExit(0)
    deny("unpinned or foreign-bound Claude sessions are read-only")
deny("unexpected mutating tool cannot be authorized")
PY
