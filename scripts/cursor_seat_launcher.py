#!/usr/bin/env python3
"""Launch and resume Pipeline-bound local Cursor SDK seats."""

from __future__ import annotations

import argparse
import contextlib
import fcntl
import hashlib
import json
import os
import stat
import subprocess
import sys
import tempfile
import tomllib
from collections.abc import Callable, Iterator, Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from scripts import compact_pair_loop, protocol_mailbox
    from scripts.cursor_protocol_model import infer_runtime_env, render_runtime_env_contract
except ModuleNotFoundError as exc:
    if exc.name != "scripts":
        raise
    import compact_pair_loop
    import protocol_mailbox
    from cursor_protocol_model import infer_runtime_env, render_runtime_env_contract


LAUNCH_SEATS = ("director", "director2", "operator", "operator2", "coordinator")
DEFAULT_CONFIG_PATH = Path("~/.cursor/pipeline-seat-launcher.toml")
REGISTRY_SCHEMA_VERSION = 1
_SEAT_ENV_PREFIXES = ("CURSOR_", "CODEX_", "AGY_", "ANTIGRAVITY_", "GIT_")
_PRESERVED_AMBIENT_ENV = frozenset(
    {
        "CURSOR_API_KEY",
        "CURSOR_PROJECT_DIR",
        "CURSOR_VERSION",
        "CURSOR_USER_EMAIL",
        "CURSOR_TRANSCRIPT_PATH",
        "CURSOR_CODE_REMOTE",
    }
)


class ConfigError(ValueError):
    """The user-local Cursor seat configuration is invalid."""


class RegistryError(ValueError):
    """The local SDK seat registry is invalid or ambiguous."""


class LaunchError(RuntimeError):
    """A seat launch cannot proceed without guessing or new authority."""


@dataclass(frozen=True)
class SeatSettings:
    model: str


@dataclass(frozen=True)
class LauncherConfig:
    workspace: Path
    setting_sources: tuple[str, ...]
    seats: dict[str, SeatSettings]


@dataclass(frozen=True)
class LaunchSpec:
    seat: str
    operation: str
    model: str
    trigger_ref: str
    workspace: Path
    setting_sources: tuple[str, ...]
    env: dict[str, str]
    index_path: Path


def _model(value: object, label: str) -> str:
    if (
        not isinstance(value, str)
        or not value
        or value.strip() != value
        or any(character.isspace() or ord(character) < 32 for character in value)
    ):
        raise ConfigError(f"{label} must be one nonblank model identifier")
    return value


def load_config(path: Path, *, expected_workspace: Path) -> LauncherConfig:
    """Load one exact, Pipeline-scoped local Cursor seat configuration."""

    expanded = path.expanduser()
    try:
        with expanded.open("rb") as handle:
            document = tomllib.load(handle)
    except (OSError, tomllib.TOMLDecodeError) as exc:
        raise ConfigError(f"cannot load Cursor seat config {expanded}: {exc}") from exc
    if set(document) != {"runtime", "seats"}:
        raise ConfigError("config must contain exactly [runtime] and [seats.*]")
    runtime = document["runtime"]
    seats = document["seats"]
    if not isinstance(runtime, dict) or set(runtime) != {"workspace", "setting_sources"}:
        raise ConfigError("[runtime] must contain exactly workspace and setting_sources")
    if not isinstance(seats, dict) or set(seats) != set(LAUNCH_SEATS):
        raise ConfigError("config must define exactly: " + ", ".join(LAUNCH_SEATS))
    raw_workspace = runtime["workspace"]
    if not isinstance(raw_workspace, str) or not raw_workspace:
        raise ConfigError("[runtime].workspace must be one absolute path")
    workspace_path = Path(raw_workspace).expanduser()
    if not workspace_path.is_absolute():
        raise ConfigError("[runtime].workspace must be one absolute path")
    workspace = workspace_path.resolve()
    expected = expected_workspace.resolve()
    if workspace != expected:
        raise ConfigError(f"workspace is not the managed Pipeline workspace: {expected}")
    raw_sources = runtime["setting_sources"]
    if (
        not isinstance(raw_sources, list)
        or not raw_sources
        or any(not isinstance(source, str) for source in raw_sources)
        or tuple(raw_sources) != ("project",)
    ):
        raise ConfigError("[runtime].setting_sources must be exactly ['project']")
    settings: dict[str, SeatSettings] = {}
    for seat in LAUNCH_SEATS:
        value = seats[seat]
        if not isinstance(value, dict) or set(value) != {"model"}:
            raise ConfigError(f"[seats.{seat}] must contain exactly model")
        settings[seat] = SeatSettings(_model(value["model"], f"[seats.{seat}].model"))
    return LauncherConfig(workspace, tuple(raw_sources), settings)


def _without_ambient_index(environ: Mapping[str, str]) -> dict[str, str]:
    return {
        key: value
        for key, value in environ.items()
        if not key.startswith("GIT_")
    }


def _clean_inherited_environment(environ: Mapping[str, str]) -> dict[str, str]:
    """Keep normal process settings but remove inherited provider/Git identity."""

    return {
        key: value
        for key, value in environ.items()
        if (
            not key.startswith(_SEAT_ENV_PREFIXES)
            or key in _PRESERVED_AMBIENT_ENV
        )
    }


def resolve_git_dir(repo_root: Path) -> Path:
    result = subprocess.run(
        ["git", "-C", str(repo_root), "rev-parse", "--absolute-git-dir"],
        env=_without_ambient_index(os.environ),
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise LaunchError(result.stderr.strip() or "cannot resolve Pipeline git directory")
    return Path(result.stdout.strip())


def ensure_seat_index(
    repo_root: Path,
    index_path: Path,
    *,
    runner: Callable[..., subprocess.CompletedProcess[str]] = subprocess.run,
) -> None:
    """Seed a missing seat index; validate and preserve an existing one."""

    try:
        index_mode = index_path.lstat().st_mode
    except FileNotFoundError:
        index_mode = None
    except OSError as exc:
        raise LaunchError(
            f"cannot inspect existing Cursor seat index {index_path}: {exc}"
        ) from exc
    if index_mode is not None:
        if not stat.S_ISREG(index_mode):
            raise LaunchError(
                f"existing Cursor seat index {index_path} must be a regular file; "
                "refusing to launch without changing it"
            )
        index_env = _without_ambient_index(os.environ)
        index_env["GIT_INDEX_FILE"] = str(index_path)
        entries = runner(
            [
                "git",
                "-C",
                str(repo_root),
                "ls-files",
                "--stage",
                "-z",
            ],
            env=index_env,
            text=True,
            capture_output=True,
            check=False,
        )
        if entries.returncode != 0:
            detail = entries.stderr.strip() or entries.stdout.strip()
            raise LaunchError(
                f"existing seat index {index_path} is unusable: "
                f"{detail or 'cannot read index entries'}"
            )
        if not entries.stdout:
            head_entries = runner(
                [
                    "git",
                    "-C",
                    str(repo_root),
                    "ls-tree",
                    "-r",
                    "--name-only",
                    "-z",
                    "HEAD",
                ],
                env=_without_ambient_index(os.environ),
                text=True,
                capture_output=True,
                check=False,
            )
            if head_entries.returncode != 0:
                detail = head_entries.stderr.strip() or head_entries.stdout.strip()
                raise LaunchError(detail or "cannot inspect HEAD before seat launch")
            if head_entries.stdout:
                raise LaunchError(
                    f"existing seat index {index_path} is empty while HEAD tracks files; "
                    "refusing to launch without changing the index"
                )
        status = runner(
            [
                "git",
                "--no-optional-locks",
                "-C",
                str(repo_root),
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
        if status.returncode != 0:
            detail = status.stderr.strip() or status.stdout.strip()
            raise LaunchError(
                f"existing Cursor seat index {index_path} is unusable: "
                f"{detail or 'Git status validation failed'}"
            )
        return
    result = runner(
        [
            "git",
            "-C",
            str(repo_root),
            "read-tree",
            f"--index-output={index_path}",
            "HEAD",
        ],
        env=_without_ambient_index(os.environ),
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise LaunchError(result.stderr.strip() or f"cannot seed seat index {index_path}")


def build_launch_spec(
    config: LauncherConfig,
    *,
    git_dir: Path,
    seat: str,
    trigger_ref: str,
    inherited_env: Mapping[str, str],
    operation: str,
) -> LaunchSpec:
    if seat not in LAUNCH_SEATS or seat not in config.seats:
        raise LaunchError(f"unsupported Cursor seat: {seat}")
    index_path = git_dir / f"index-cursor-{seat}"
    runtime = infer_runtime_env(
        {"CURSOR_SEAT": seat, "GIT_INDEX_FILE": str(index_path)}
    )
    env = _clean_inherited_environment(inherited_env)
    env.update(
        {
            key: value
            for key, value in runtime.items()
            if not (
                key == "CURSOR_BEHAVIOR_SOURCE"
                and value == "(none)"
            )
        }
    )
    env["CURSOR_OPERATION"] = operation
    env["CURSOR_PROJECT_DIR"] = str(config.workspace)
    env["GIT_INDEX_FILE"] = str(index_path)
    return LaunchSpec(
        seat=seat,
        operation=operation,
        model=config.seats[seat].model,
        trigger_ref=trigger_ref,
        workspace=config.workspace,
        setting_sources=config.setting_sources,
        env=env,
        index_path=index_path,
    )


def dispatch_key(seat: str, trigger_ref: str, route_revision: int) -> str:
    material = f"cursor-seat/v1\0{seat}\0{trigger_ref}\0{route_revision}".encode()
    return hashlib.sha256(material).hexdigest()


def empty_registry(workspace: Path) -> dict[str, Any]:
    return {
        "schema_version": REGISTRY_SCHEMA_VERSION,
        "workspace": str(workspace.resolve()),
        "seats": {},
        "dispatches": {},
    }


def load_registry(path: Path, workspace: Path) -> dict[str, Any]:
    if not path.exists():
        return empty_registry(workspace)
    try:
        encoded = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise RegistryError(f"cannot read Cursor seat registry: {exc}") from exc
    if "prompt" in encoded.casefold():
        raise RegistryError("Cursor seat registry must not store prompt content")
    try:
        document = json.loads(encoded)
    except json.JSONDecodeError as exc:
        raise RegistryError(f"cannot read Cursor seat registry: {exc}") from exc
    if (
        not isinstance(document, dict)
        or set(document) != {"schema_version", "workspace", "seats", "dispatches"}
        or document["schema_version"] != REGISTRY_SCHEMA_VERSION
        or not isinstance(document["seats"], dict)
        or not isinstance(document["dispatches"], dict)
    ):
        raise RegistryError("Cursor seat registry schema is invalid")
    if Path(str(document["workspace"])).resolve() != workspace.resolve():
        raise RegistryError("Cursor seat registry workspace does not match Pipeline")
    return document


def save_registry(path: Path, registry: Mapping[str, Any]) -> None:
    """Atomically write local metadata without ever storing prompt text."""

    encoded = (json.dumps(registry, indent=2, sort_keys=True) + "\n").encode()
    if b"prompt" in encoded.lower():
        raise RegistryError("Cursor seat registry must not store prompt content")
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    temporary = Path(temporary_name)
    try:
        os.fchmod(fd, 0o600)
        with os.fdopen(fd, "wb", closefd=True) as handle:
            handle.write(encoded)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
        path.chmod(0o600)
        directory_fd = os.open(path.parent, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
    finally:
        temporary.unlink(missing_ok=True)


@contextlib.contextmanager
def seat_lock(runtime_dir: Path, seat: str) -> Iterator[None]:
    runtime_dir.mkdir(parents=True, exist_ok=True)
    path = runtime_dir / f"{seat}.lock"
    fd = os.open(path, os.O_CREAT | os.O_RDWR | getattr(os, "O_CLOEXEC", 0), 0o600)
    try:
        os.fchmod(fd, 0o600)
        if not stat.S_ISREG(os.fstat(fd).st_mode):
            raise RegistryError("Cursor seat lock is not a regular file")
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise LaunchError(f"Cursor seat {seat} already has an active launcher") from exc
        yield
    finally:
        os.close(fd)


def validate_review_binding(request: Any, seat: str, reviewer_model: str) -> None:
    if seat not in {"operator", "operator2"} or request.assigned_operator != seat:
        raise LaunchError("reviewer is not the assigned Operator seat")
    if reviewer_model.casefold() == request.author_model.casefold():
        raise LaunchError("review requires a different model from the author")


def confirm_provider_launch(
    *,
    seat: str,
    model: str,
    workspace: Path,
    trigger_ref: str,
    stdin_isatty: bool,
    input_fn: Callable[[str], str] = input,
) -> bool:
    if not stdin_isatty:
        raise LaunchError("provider launch requires interactive user confirmation")
    answer = input_fn(
        "Launch Cursor provider agent "
        f"seat={seat} model={model} workspace={workspace} trigger={trigger_ref} "
        "(may incur provider cost)? Type yes: "
    )
    if answer.strip().casefold() != "yes":
        raise LaunchError("provider launch was not authorized")
    return True


def _event_from_ref(root: Path, value: str) -> protocol_mailbox.CommittedEventRef:
    try:
        return protocol_mailbox.load_committed_event_ref(root, value)
    except (OSError, UnicodeError, ValueError) as exc:
        raise LaunchError(f"invalid committed trigger ref: {exc}") from exc


def _verify_request_from_ref(root: Path, value: str) -> compact_pair_loop.VerifyRequest:
    try:
        path, commit = value.rsplit("@", 1)
        return compact_pair_loop.parse_verify_request(root, path, commit)
    except (ValueError, compact_pair_loop.CompactPairError) as exc:
        raise LaunchError(f"invalid committed verify-request: {exc}") from exc


def _role_prompt(root: Path, seat: str) -> str:
    role = "director" if seat.startswith("director") else (
        "operator" if seat.startswith("operator") else "coordinator"
    )
    path = root / "docs" / "protocol" / "cursor" / "roles" / f"{role}.md"
    if not path.is_file():
        raise LaunchError(f"required Cursor role prompt is unavailable: {path}")
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise LaunchError(f"cannot read Cursor role prompt {path}: {exc}") from exc


@contextlib.contextmanager
def _seat_environment(values: Mapping[str, str]) -> Iterator[None]:
    removed = {
        key
        for key in os.environ
        if (
            key.startswith(_SEAT_ENV_PREFIXES)
            and key not in values
            and key not in _PRESERVED_AMBIENT_ENV
        )
    }
    previous = {key: os.environ.get(key) for key in {*values, *removed}}
    for key in removed:
        os.environ.pop(key, None)
    os.environ.update(values)
    try:
        yield
    finally:
        for key, value in previous.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _write_outbox(root: Path, seat: str, run_id: str, text: str, model: str) -> Path:
    outbox = root / ".cursor" / "runtime" / "outbox" / seat
    outbox.mkdir(parents=True, exist_ok=True)
    # Provider-generated IDs are data, not path components. A digest keeps the
    # local artifact deterministic without allowing separators or traversal.
    filename = hashlib.sha256(run_id.encode("utf-8")).hexdigest() + ".json"
    path = outbox / filename
    payload = {
        "run_id": run_id,
        "seat": seat,
        "actual_model": model,
        "result": text,
        "result_sha256": hashlib.sha256(text.encode()).hexdigest(),
    }
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    path.chmod(0o600)
    return path


def _run_sdk(
    spec: LaunchSpec,
    prompt: str,
    registry: dict[str, Any],
    *,
    dispatch_key: str,
    on_agent_bound: Callable[[str], None],
    on_run_started: Callable[[str], None],
) -> tuple[str, str, str]:
    try:
        from cursor_sdk import Agent, AgentOptions, LocalAgentOptions
    except ImportError as exc:
        raise LaunchError(
            "cursor-sdk is not installed; install requirements-cursor.txt"
        ) from exc
    local = LocalAgentOptions(
        cwd=str(spec.workspace),
        setting_sources=list(spec.setting_sources),
    )
    seat_state = registry["seats"].get(spec.seat)
    with _seat_environment(spec.env):
        if seat_state:
            if seat_state.get("model") != spec.model:
                raise LaunchError("configured model drift requires a separately authorized new agent")
            agent_context = Agent.resume(
                seat_state["agent_id"],
                AgentOptions(model=spec.model, local=local),
            )
        else:
            agent_context = Agent.create(
                model=spec.model,
                name=f"pipeline-{spec.seat}",
                local=local,
                idempotency_key=dispatch_key,
            )
        with agent_context as agent:
            registry["seats"][spec.seat] = {
                "agent_id": agent.agent_id,
                "model": spec.model,
                "behavior_source": spec.env.get("CURSOR_BEHAVIOR_SOURCE"),
                "updated_at": _utc_now(),
            }
            on_agent_bound(agent.agent_id)
            run = agent.send(prompt, idempotency_key=dispatch_key)
            run_id = run.id
            on_run_started(run_id)
            result = run.wait()
            status = result.status
            actual_model = (
                result.model.id
                if getattr(result, "model", None) is not None
                else spec.model
            )
            text = result.result or ""
    return run_id, status, actual_model + "\0" + text


def _run_live(
    spec: LaunchSpec,
    *,
    role_prompt: str,
    trigger_text: str,
    route_revision: int,
) -> int:
    root = spec.workspace
    runtime = root / ".cursor" / "runtime"
    registry_path = runtime / "pipeline-seats.json"
    key = dispatch_key(spec.seat, spec.trigger_ref, route_revision)
    with seat_lock(runtime, spec.seat):
        registry = load_registry(registry_path, root)
        existing = registry["dispatches"].get(key)
        if existing and existing.get("status") not in {"error", "cancelled", "expired"}:
            raise LaunchError("dispatch already exists; reconcile its recorded run instead")
        registry["dispatches"][key] = {
            "seat": spec.seat,
            "trigger_ref": spec.trigger_ref,
            "route_revision": route_revision,
            "status": "launching",
            "updated_at": _utc_now(),
        }
        save_registry(registry_path, registry)
        prompt = role_prompt + "\n\nCommitted trigger:\n" + trigger_text

        def on_agent_bound(agent_id: str) -> None:
            registry["dispatches"][key].update(
                {
                    "agent_id": agent_id,
                    "status": "starting",
                    "updated_at": _utc_now(),
                }
            )
            save_registry(registry_path, registry)

        def on_run_started(run_id: str) -> None:
            registry["dispatches"][key].update(
                {
                    "run_id": run_id,
                    "status": "running",
                    "updated_at": _utc_now(),
                }
            )
            registry["seats"][spec.seat].update(
                {
                    "last_run_id": run_id,
                    "last_trigger_ref": spec.trigger_ref,
                }
            )
            save_registry(registry_path, registry)

        try:
            run_id, status, combined = _run_sdk(
                spec,
                prompt,
                registry,
                dispatch_key=key,
                on_agent_bound=on_agent_bound,
                on_run_started=on_run_started,
            )
            actual_model, text = combined.split("\0", 1)
        except Exception:
            registry["dispatches"][key]["status"] = "unresolved"
            registry["dispatches"][key]["updated_at"] = _utc_now()
            save_registry(registry_path, registry)
            raise
        registry["dispatches"][key].update(
            {"run_id": run_id, "status": status, "updated_at": _utc_now()}
        )
        registry["seats"][spec.seat].update(
            {
                "last_run_id": run_id,
                "last_run_status": status,
                "last_actual_model": actual_model,
                "last_trigger_ref": spec.trigger_ref,
            }
        )
        outbox = _write_outbox(root, spec.seat, run_id, text, actual_model)
        save_registry(registry_path, registry)
        print(f"run={run_id} status={status} model={actual_model} outbox={outbox}")
        return 0 if status == "finished" else 2


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="cursor-seat")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG_PATH)
    parser.add_argument("--dry-run", action="store_true")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("readiness")
    commands.add_parser("status")
    for name in ("dispatch", "review"):
        sub = commands.add_parser(name)
        sub.add_argument("seat", choices=LAUNCH_SEATS)
        flag = "--verify-request" if name == "review" else "--trigger-ref"
        sub.add_argument(flag, required=True, dest="trigger_ref")
        sub.add_argument("--route-revision", type=int, default=0)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(sys.argv[1:] if argv is None else argv)
    root = Path(__file__).resolve().parents[1]
    try:
        if args.command == "readiness":
            print(render_runtime_env_contract({}))
            print("provider launch: none")
            return 0
        if args.command == "status":
            registry = load_registry(root / ".cursor/runtime/pipeline-seats.json", root)
            print(json.dumps(registry, indent=2, sort_keys=True))
            return 0
        config = load_config(args.config, expected_workspace=root)
        git_dir = resolve_git_dir(root)
        operation = "review" if args.command == "review" else "dispatch"
        spec = build_launch_spec(
            config,
            git_dir=git_dir,
            seat=args.seat,
            trigger_ref=args.trigger_ref,
            inherited_env=os.environ,
            operation=operation,
        )
        if args.dry_run:
            print(
                json.dumps(
                    {
                        "operation": operation,
                        "seat": spec.seat,
                        "model": spec.model,
                        "workspace": str(spec.workspace),
                        "trigger_ref": spec.trigger_ref,
                        "index_path": str(spec.index_path),
                        "env": {
                            key: value
                            for key, value in spec.env.items()
                            if key.startswith("CURSOR_") or key == "GIT_INDEX_FILE"
                        },
                    },
                    indent=2,
                    sort_keys=True,
                )
            )
            return 0
        if args.command == "review":
            request = _verify_request_from_ref(root, args.trigger_ref)
            validate_review_binding(request, args.seat, spec.model)
            trigger_text = request.outcome
        else:
            trigger_text = _event_from_ref(root, args.trigger_ref).text
        role_prompt = _role_prompt(root, args.seat)
        confirm_provider_launch(
            seat=spec.seat,
            model=spec.model,
            workspace=spec.workspace,
            trigger_ref=spec.trigger_ref,
            stdin_isatty=sys.stdin.isatty(),
        )
        ensure_seat_index(root, spec.index_path)
        return _run_live(
            spec,
            role_prompt=role_prompt,
            trigger_text=trigger_text,
            route_revision=args.route_revision,
        )
    except (ConfigError, RegistryError, LaunchError) as exc:
        print(f"cursor-seat: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
