#!/usr/bin/env python3
"""Cursor Desktop seat binding from linked worktrees and app session metadata."""

from __future__ import annotations

import fcntl
import json
import os
import stat
import subprocess
import tempfile
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

APP_SEATS = ("director", "director2", "operator", "operator2", "coordinator")
DIRECTOR_SEATS = frozenset({"director", "director2"})
OPERATOR_SEATS = frozenset({"operator", "operator2"})
CURSOR_BRANCH_PREFIX = "cursor-seat/"
REGISTRY_VERSION = 1
DEFAULT_REGISTRY_PATH = Path("~/.cursor/pipeline-app-seats.json")


class AppBindingError(RuntimeError):
    """A Cursor app session cannot prove one unambiguous seat binding."""


@dataclass(frozen=True)
class WorktreeSeat:
    seat: str
    root: Path
    branch: str
    git_dir: Path
    common_dir: Path


@dataclass(frozen=True)
class AppSessionBinding:
    seat: str
    root: Path
    branch: str
    conversation_id: str
    model_id: str


def _clean_git_env(environ: Mapping[str, str] | None = None) -> dict[str, str]:
    source = os.environ if environ is None else environ
    return {key: value for key, value in source.items() if not key.startswith("GIT_")}


def _git(
    root: Path,
    *args: str,
    runner: Callable[..., subprocess.CompletedProcess[str]] = subprocess.run,
) -> str:
    result = runner(
        ["git", "--no-optional-locks", "-C", str(root), *args],
        env=_clean_git_env(),
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip()
        raise AppBindingError(detail or f"git {' '.join(args)} failed")
    return result.stdout.strip()


def parse_seat_branch(branch: str) -> str | None:
    """Return the seat for one reserved branch, or None for an ordinary branch."""

    if not branch.startswith(CURSOR_BRANCH_PREFIX):
        return None
    seat = branch.removeprefix(CURSOR_BRANCH_PREFIX)
    if seat not in APP_SEATS:
        raise AppBindingError(f"reserved Cursor seat branch names an unknown seat: {branch}")
    return seat


def resolve_worktree_seat(
    root: Path,
    *,
    runner: Callable[..., subprocess.CompletedProcess[str]] = subprocess.run,
) -> WorktreeSeat | None:
    """Resolve a seat only from a reserved branch in a linked Git worktree."""

    workspace = root.expanduser().resolve()
    # One rev-parse for all three paths instead of three subprocesses: the
    # seat-policy hook resolves identity on every shell command, so each saved
    # process is paid back on the hot path. --path-format=absolute applies to
    # the --git-common-dir that follows it; --show-toplevel and
    # --absolute-git-dir are already absolute.
    try:
        paths = _git(
            workspace,
            "rev-parse",
            "--show-toplevel",
            "--absolute-git-dir",
            "--path-format=absolute",
            "--git-common-dir",
            runner=runner,
        ).splitlines()
    except AppBindingError:
        return None
    if len(paths) != 3:
        raise AppBindingError("git rev-parse did not return the three seat worktree paths")
    top = Path(paths[0]).resolve()
    git_dir = Path(paths[1]).resolve()
    common_dir = Path(paths[2]).resolve()
    if top != workspace:
        raise AppBindingError("Cursor seat workspace must be the linked worktree root")
    branch = _git(
        workspace,
        "symbolic-ref",
        "--quiet",
        "--short",
        "HEAD",
        runner=runner,
    )
    seat = parse_seat_branch(branch)
    if seat is None:
        return None
    if git_dir == common_dir:
        raise AppBindingError(
            "reserved Cursor seat branch must run in a linked worktree, not the main checkout"
        )
    try:
        if not stat.S_ISDIR(git_dir.lstat().st_mode):
            raise AppBindingError("linked worktree git directory is not a directory")
    except OSError as exc:
        raise AppBindingError(f"cannot inspect linked worktree git directory: {exc}") from exc
    return WorktreeSeat(
        seat=seat,
        root=workspace,
        branch=branch,
        git_dir=git_dir,
        common_dir=common_dir,
    )


def payload_identity(payload: Mapping[str, Any]) -> tuple[str, str]:
    conversation_id = payload.get("conversation_id") or payload.get("session_id")
    model_id = payload.get("model_id") or payload.get("model")
    if not isinstance(conversation_id, str) or not conversation_id.strip():
        raise AppBindingError("Cursor hook payload has no stable conversation id")
    if not isinstance(model_id, str) or not model_id.strip():
        raise AppBindingError("Cursor hook payload has no selected model id")
    return conversation_id.strip(), model_id.strip()


def payload_workspace(root: Path, payload: Mapping[str, Any]) -> Path:
    roots = payload.get("workspace_roots")
    if not isinstance(roots, list) or len(roots) != 1:
        raise AppBindingError("Cursor app seat binding requires exactly one workspace root")
    value = roots[0]
    if not isinstance(value, str) or not value:
        raise AppBindingError("Cursor workspace root is invalid")
    workspace = Path(value).expanduser().resolve()
    if workspace != root.expanduser().resolve():
        raise AppBindingError("hook workspace root does not match the project hook root")
    return workspace


def _empty_registry() -> dict[str, object]:
    return {"version": REGISTRY_VERSION, "bindings": {}}


def _load_registry_unlocked(path: Path) -> dict[str, object]:
    if not path.exists():
        return _empty_registry()
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise AppBindingError(f"cannot read Cursor app seat registry: {exc}") from exc
    if (
        not isinstance(document, dict)
        or document.get("version") != REGISTRY_VERSION
        or not isinstance(document.get("bindings"), dict)
    ):
        raise AppBindingError("Cursor app seat registry has an unsupported schema")
    return document


def load_registry(path: Path = DEFAULT_REGISTRY_PATH) -> dict[str, object]:
    return _load_registry_unlocked(path.expanduser())


def _write_registry_unlocked(path: Path, document: Mapping[str, object]) -> None:
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=path.name + ".", suffix=".tmp", dir=path.parent
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump(document, handle, indent=2, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        temporary.chmod(0o600)
        os.replace(temporary, path)
        path.chmod(0o600)
    finally:
        try:
            temporary.unlink()
        except FileNotFoundError:
            pass


def register_session(
    identity: WorktreeSeat,
    *,
    conversation_id: str,
    model_id: str,
    registry_path: Path = DEFAULT_REGISTRY_PATH,
) -> AppSessionBinding:
    """Atomically make the newest top-level chat active for one seat worktree."""

    registry = registry_path.expanduser()
    registry.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    lock_path = registry.with_name(registry.name + ".lock")
    with lock_path.open("a+", encoding="utf-8") as lock:
        lock_path.chmod(0o600)
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
        document = _load_registry_unlocked(registry)
        bindings = document["bindings"]
        assert isinstance(bindings, dict)
        previous = bindings.get(identity.seat)
        if isinstance(previous, dict):
            previous_root = previous.get("root")
            if (
                isinstance(previous_root, str)
                and Path(previous_root).exists()
                and Path(previous_root).resolve() != identity.root
            ):
                try:
                    previous_identity = resolve_worktree_seat(Path(previous_root))
                except AppBindingError:
                    previous_identity = None
                if (
                    previous_identity is not None
                    and previous_identity.seat == identity.seat
                ):
                    raise AppBindingError(
                        f"{identity.seat} is already bound to another live worktree"
                    )
        for seat, record in list(bindings.items()):
            if (
                seat != identity.seat
                and isinstance(record, dict)
                and record.get("conversation_id") == conversation_id
            ):
                raise AppBindingError(
                    "one Cursor conversation cannot bind more than one app seat"
                )
        bindings[identity.seat] = {
            "root": str(identity.root),
            "branch": identity.branch,
            "conversation_id": conversation_id,
            "model_id": model_id,
        }
        _write_registry_unlocked(registry, document)
        fcntl.flock(lock.fileno(), fcntl.LOCK_UN)
    return AppSessionBinding(
        seat=identity.seat,
        root=identity.root,
        branch=identity.branch,
        conversation_id=conversation_id,
        model_id=model_id,
    )


def register_payload_session(
    root: Path,
    payload: Mapping[str, Any],
    *,
    registry_path: Path = DEFAULT_REGISTRY_PATH,
) -> AppSessionBinding | None:
    if payload.get("is_background_agent") is True:
        raise AppBindingError("background agents cannot register durable app seats")
    workspace = payload_workspace(root, payload)
    identity = resolve_worktree_seat(workspace)
    if identity is None:
        return None
    conversation_id, model_id = payload_identity(payload)
    return register_session(
        identity,
        conversation_id=conversation_id,
        model_id=model_id,
        registry_path=registry_path,
    )


def _payload_field(payload: Mapping[str, Any], *keys: str) -> object:
    for key in keys:
        if key in payload:
            return payload[key]
    return None


def resolve_registered_session(
    root: Path,
    environ: Mapping[str, str] | None = None,
    *,
    registry_path: Path = DEFAULT_REGISTRY_PATH,
    payload: Mapping[str, Any] | None = None,
) -> AppSessionBinding:
    """Resolve the one active seat binding from the worktree and registry.

    Identity is the linked worktree's reserved branch plus the user-local
    registry record written at ``sessionStart``. Environment values are only a
    consistency cross-check when present; they never establish identity.
    When a hook payload supplies ``conversation_id`` / ``model_id`` (or the
    legacy ``session_id`` / ``model`` aliases), those values must match the
    registry or resolution fails closed.
    """

    env = os.environ if environ is None else environ
    if env.get("GIT_INDEX_FILE"):
        raise AppBindingError("Cursor app worktree seats must not use GIT_INDEX_FILE")
    identity = resolve_worktree_seat(root)
    if identity is None:
        raise AppBindingError("current workspace is not a bound Cursor seat worktree")
    document = load_registry(registry_path)
    bindings = document["bindings"]
    assert isinstance(bindings, dict)
    record = bindings.get(identity.seat)
    if not isinstance(record, dict):
        raise AppBindingError(f"{identity.seat} has no registered Cursor app session")
    conversation_id = record.get("conversation_id")
    model_id = record.get("model_id")
    if (
        record.get("root") != str(identity.root)
        or record.get("branch") != identity.branch
        or not isinstance(conversation_id, str)
        or not conversation_id
        or not isinstance(model_id, str)
        or not model_id
    ):
        raise AppBindingError(
            "Cursor app seat registry does not match this worktree"
        )
    for key, expected in (
        ("CURSOR_SEAT", identity.seat),
        ("CURSOR_APP_CONVERSATION_ID", conversation_id),
        ("CURSOR_APP_MODEL_ID", model_id),
    ):
        supplied = env.get(key)
        if supplied and supplied != expected:
            raise AppBindingError(f"{key} disagrees with the registered app session")
    if payload is not None:
        supplied_conversation = _payload_field(
            payload, "conversation_id", "session_id"
        )
        if supplied_conversation is not None:
            if (
                not isinstance(supplied_conversation, str)
                or not supplied_conversation.strip()
                or supplied_conversation.strip() != conversation_id
            ):
                raise AppBindingError(
                    "payload conversation_id disagrees with the registered app session"
                )
        supplied_model = _payload_field(payload, "model_id", "model")
        if supplied_model is not None:
            if (
                not isinstance(supplied_model, str)
                or not supplied_model.strip()
                or supplied_model.strip() != model_id
            ):
                raise AppBindingError(
                    "payload model_id disagrees with the registered app session"
                )
    return AppSessionBinding(
        seat=identity.seat,
        root=identity.root,
        branch=identity.branch,
        conversation_id=conversation_id,
        model_id=model_id,
    )


def session_environment(binding: AppSessionBinding) -> dict[str, str]:
    behavior = (
        "director"
        if binding.seat in DIRECTOR_SEATS
        else "operator2"
        if binding.seat in OPERATOR_SEATS
        else "(none)"
    )
    return {
        "CURSOR_SEAT": binding.seat,
        "CURSOR_AGENT_MODE": (
            "coordinator" if binding.seat == "coordinator" else "live-seat"
        ),
        "CURSOR_AGENT_ROLE": binding.seat,
        "CURSOR_BEHAVIOR_SOURCE": behavior,
        "CURSOR_APP_CONVERSATION_ID": binding.conversation_id,
        "CURSOR_APP_MODEL_ID": binding.model_id,
    }
