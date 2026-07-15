#!/usr/bin/env python3
"""Parent-owned collector for the fixed capability-first runtime cohort."""

from __future__ import annotations

import argparse
import contextlib
import hashlib
import importlib.util
import json
import os
import re
import secrets
import shlex
import shutil
import signal
import socket
import stat
import subprocess
import sys
import tempfile
import threading
import time
from dataclasses import dataclass, replace
from pathlib import Path, PurePosixPath
from typing import Callable, ContextManager, Mapping, NamedTuple, Sequence, TextIO


PROFILES = ("none", "verification_only", "coordination_only", "effect_only", "combined")
EFFECT_PROFILES = {"effect_only", "combined"}
PROFILE_CLASSES = {
    "none": set(),
    "verification_only": {"verification"},
    "coordination_only": {"coordination"},
    "effect_only": {"effect"},
    "combined": {"coordination", "verification", "effect"},
}
HOOK_RECORD_SCHEMA = "capability-baseline-hook-record/v1"
EFFECT_RESERVATION_SCHEMA = "capability-baseline-effect-reservation/v1"
RUN_RESERVATION_SCHEMA = "capability-baseline-run-reservation/v1"
RUN_RECORD_SCHEMA = "capability-baseline-run-record/v1"
CLOCK_DOMAIN = "host-monotonic-v1"
INSTRUMENTATION_IDENTITY = "codex-runtime-hook-observation-v1"
MAX_HOOK_INPUT_BYTES, MAX_HOOK_RECORD_BYTES = 1_048_576, 16_384
MAX_TRACE_BYTES, MAX_TRACE_LINE_BYTES, MAX_TRACE_LINES = 16_777_216, 1_048_576, 16_384
RUN_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,180}$")
SUPPORTED_REASONING_EFFORTS = frozenset({"low", "medium", "high", "xhigh", "max"})
SHA_RE = re.compile(r"^[0-9a-f]{40}$")
DIGEST_RE = re.compile(r"^sha256:[0-9a-f]{64}$")
IDENTITY_RE = re.compile(r"^\S+@sha256:[0-9a-f]{64}$")
ALLOWED_TRACE_EVENTS = {
    "thread.started", "turn.started", "item.started", "item.updated",
    "item.completed", "turn.completed", "turn.failed", "error",
}
TRACE_FAILURE_CODES = frozenset({
    "input-hook-unobserved",
    "runtime-failed-after-input-hook",
})
COLLECTOR_RELATIVE_PATH = "scripts/capability_baseline_runtime.py"
CONTRACT_RELATIVE_PATH = "scripts/baselines/capability_first_five_profile_v1.json"
REPORTER_RELATIVE_PATH = "scripts/protocol_effectiveness_report.py"
REQUIRED_COMMITTED_PATHS = (
    COLLECTOR_RELATIVE_PATH,
    REPORTER_RELATIVE_PATH,
    CONTRACT_RELATIVE_PATH,
)
REPOSITORY_ROOT = Path(__file__).resolve().parent.parent
GIT_BINARY = Path("/usr/bin/git")
DISABLED_CHILD_FEATURES = (
    "apps", "auth_elicitation", "browser_use", "browser_use_external",
    "browser_use_full_cdp_access", "computer_use", "enable_fanout",
    "image_generation", "in_app_browser", "memories", "multi_agent",
    "plugin_sharing", "remote_plugin", "skill_mcp_dependency_install",
    "standalone_web_search", "tool_call_mcp_elicitation", "workspace_dependencies",
)
QUESTION_DIGEST = "sha256:" + hashlib.sha256(
    b"Does the exact benchmark fixture diff match the fixed scenario and expected output?"
).hexdigest()
class CollectorError(RuntimeError): pass
class EffectUncertain(CollectorError): pass
class ReplayConflict(CollectorError): pass
class PreflightError(CollectorError): pass
class TraceFailure(CollectorError):
    def __init__(self, code: str) -> None:
        if code not in TRACE_FAILURE_CODES: raise CollectorError("invalid trace failure code")
        self.code = code
        super().__init__(code)


class TraceEndpoints(NamedTuple):
    session_id: str
    turn_id: str
    accepted_input_ns: int
    first_tool_callback_ns: int
    first_tool_name: str


class ProcessCapture(NamedTuple):
    returncode: int
    stdout: str
    stderr: str
    timed_out: bool = False


class EffectResult(NamedTuple):
    path: str
    nonce: str
    attempted: bool
    reconciled: bool


class ProfileEvidence(NamedTuple):
    artifacts: tuple[dict[str, str], ...]
    reviews: tuple[dict[str, str], ...]
    route_endpoints: dict[str, int]
    effect_attempted: bool


@dataclass(frozen=True)
class CollectorConfig:
    repo_root: Path
    source_head: str
    contract_path: Path
    cohort_id: str
    cohort_root: Path
    codex_binary: Path
    codex_identity: str
    collector_identity: str
    model: str
    reasoning_effort: str
    host_identity: str
    timeout_seconds: int = 300
    resume: bool = False
    local_markers_authorized: bool = False
    runtime_blob_digests: tuple[tuple[str, str], ...] = ()

    def __post_init__(self) -> None:
        if not SHA_RE.fullmatch(self.source_head) or not RUN_ID_RE.fullmatch(self.cohort_id):
            raise CollectorError("invalid source or cohort identity")
        if not self.codex_binary.is_absolute() or not self.model or not self.host_identity:
            raise CollectorError("Codex path, model, and host identity must be explicit")
        if not IDENTITY_RE.fullmatch(self.codex_identity) or not IDENTITY_RE.fullmatch(self.collector_identity):
            raise CollectorError("collector and Codex identities must bind sha256 bytes")
        if self.reasoning_effort not in SUPPORTED_REASONING_EFFORTS or self.timeout_seconds <= 0:
            raise CollectorError("invalid reasoning effort or timeout")
        if type(self.resume) is not bool or type(self.local_markers_authorized) is not bool:
            raise CollectorError("invalid collection authorization flags")
        if self.runtime_blob_digests:
            blobs = dict(self.runtime_blob_digests)
            if len(blobs) != len(self.runtime_blob_digests) or set(blobs) != set(REQUIRED_COMMITTED_PATHS) or any(not DIGEST_RE.fullmatch(value) for value in blobs.values()):
                raise CollectorError("invalid committed runtime seal")


@dataclass(frozen=True)
class RunRecord:
    run_id: str
    request_digest: str
    status: str
    observation_json: str
    error: str | None
    effect_attempted: bool
    runtime_evidence_digest: str | None
    profile_evidence_digest: str | None
    record_digest: str

    @property
    def observation(self) -> dict[str, object]:
        return json.loads(self.observation_json)

    def as_json(self) -> dict[str, object]:
        return {
            "schema_version": RUN_RECORD_SCHEMA, "run_id": self.run_id,
            "request_digest": self.request_digest, "status": self.status,
            "observation": self.observation, "error": self.error,
            "effect_attempted": self.effect_attempted,
            "runtime_evidence_digest": self.runtime_evidence_digest,
            "profile_evidence_digest": self.profile_evidence_digest,
            "record_digest": self.record_digest,
        }


class CohortResult(NamedTuple):
    observations: dict[str, object]
    records: tuple[RunRecord, ...]
    provenance: object
    evidence_root: Path


ProcessRunner = Callable[[Sequence[str], str, Path, Mapping[str, str], int], ProcessCapture]
WorkspaceFactory = Callable[[CollectorConfig, str], ContextManager[Path]]
_REPORTER_MODULE: object | None = None


def _bytes(value: object) -> bytes:
    try:
        return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode()
    except (TypeError, ValueError) as exc:
        raise CollectorError("non-canonical JSON value") from exc


def _digest_json(value: object) -> str: return "sha256:" + hashlib.sha256(_bytes(value)).hexdigest()
def _digest_text(value: str) -> str: return "sha256:" + hashlib.sha256(value.encode()).hexdigest()


def _text(value: object, limit: int = 4_096) -> str:
    if not isinstance(value, str) or not value or len(value.encode()) > limit or any(ord(c) < 32 or ord(c) == 127 for c in value):
        raise CollectorError("absent, oversized, or unsafe identity field")
    return value


def _run_id(value: str) -> str:
    if not isinstance(value, str) or not RUN_ID_RE.fullmatch(value):
        raise CollectorError("unsafe run identity")
    return value


def _profile_ordinal_from_run_id(value: str) -> tuple[str, int]:
    _run_id(value)
    for profile in PROFILES:
        match = re.search(rf"-{re.escape(profile)}-([1-5])$", value)
        if match: return profile, int(match.group(1))
    raise CollectorError("run identity lacks fixed profile/ordinal suffix")


def hook_main(event_kind: str, run_id: str, socket_path: Path | str, *, stdin: TextIO | None = None) -> int:
    """Send one bounded, redacted Codex hook record to its parent."""
    try:
        if event_kind not in {"UserPromptSubmit", "PreToolUse"}: raise CollectorError("unsupported hook")
        _run_id(run_id)
        raw = (stdin or sys.stdin).read(MAX_HOOK_INPUT_BYTES + 1)
        if len(raw.encode()) > MAX_HOOK_INPUT_BYTES: raise CollectorError("oversized hook input")
        payload = json.loads(raw)
        if not isinstance(payload, dict) or payload.get("hook_event_name") != event_kind:
            raise CollectorError("wrong hook object")
        record: dict[str, object] = {
            "schema_version": HOOK_RECORD_SCHEMA, "event_kind": event_kind,
            "run_id": run_id, "session_id": _text(payload.get("session_id")),
            "turn_id": _text(payload.get("turn_id")), "agent_id": payload.get("agent_id"),
        }
        if record["agent_id"] is not None: _text(record["agent_id"])
        _text(payload.get("cwd"), 16_384)
        if event_kind == "UserPromptSubmit":
            if not isinstance(payload.get("prompt"), str): raise CollectorError("missing prompt")
            record["prompt_digest"] = _digest_text(payload["prompt"])
        else:
            if "tool_input" not in payload: raise CollectorError("missing tool input")
            record["tool_name"] = _text(payload.get("tool_name"))
            record["tool_use_id_digest"] = _digest_text(_text(payload.get("tool_use_id")))
        path, encoded = Path(socket_path), _bytes(record) + b"\n"
        if not path.is_absolute() or len(encoded) > MAX_HOOK_RECORD_BYTES: raise CollectorError("bad socket record")
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as client:
            client.settimeout(2); client.connect(str(path)); client.sendall(encoded)
        return 0
    except Exception:
        return 2


def parse_runtime_trace(
    jsonl: str,
    *,
    exit_code: int,
    hook_records: Sequence[object],
    expected_run_id: str,
    expected_prompt_digest: str,
) -> TraceEndpoints:
    """Cross-check host hook endpoints with one strict Codex JSONL lifecycle."""
    _run_id(expected_run_id)
    if exit_code: raise CollectorError("Codex process exited nonzero")
    if len(jsonl.encode()) > MAX_TRACE_BYTES: raise CollectorError("oversized runtime trace")
    lines = jsonl.splitlines()
    if not lines or len(lines) > MAX_TRACE_LINES: raise CollectorError("absent or oversized runtime trace")
    events: list[dict[str, object]] = []
    for line in lines:
        if not line or len(line.encode()) > MAX_TRACE_LINE_BYTES: raise CollectorError("malformed runtime trace line")
        try: event = json.loads(line)
        except json.JSONDecodeError as exc: raise CollectorError("malformed runtime trace JSON") from exc
        if not isinstance(event, dict) or not isinstance(event.get("type"), str): raise CollectorError("untyped runtime event")
        if event["type"] not in ALLOWED_TRACE_EVENTS: raise CollectorError("unknown runtime event")
        events.append(event)
    kinds = [event["type"] for event in events]
    terminal = "turn.failed" in kinds or "error" in kinds
    if terminal and "turn.completed" in kinds: raise CollectorError("contradictory runtime terminal state")
    for required in ("thread.started", "turn.started"):
        if kinds.count(required) != 1: raise CollectorError(f"requires exactly one {required}")
    thread_i, turn_i = map(kinds.index, ("thread.started", "turn.started"))
    if not thread_i < turn_i: raise CollectorError("runtime lifecycle reordered")
    if terminal and min(i for i, kind in enumerate(kinds) if kind in {"turn.failed", "error"}) < turn_i:
        raise CollectorError("runtime lifecycle reordered")
    thread_id = _text(events[thread_i].get("thread_id"))

    clean: list[dict[str, object]] = []
    for raw in hook_records:
        if not isinstance(raw, dict): raise CollectorError("non-object hook record")
        kind = raw.get("event_kind")
        base = {"schema_version", "event_kind", "run_id", "session_id", "turn_id", "agent_id", "received_ns"}
        expected = base | ({"prompt_digest"} if kind == "UserPromptSubmit" else {"tool_name", "tool_use_id_digest"})
        if kind not in {"UserPromptSubmit", "PreToolUse"} or set(raw) != expected: raise CollectorError("wrong hook record fields")
        if raw.get("schema_version") != HOOK_RECORD_SCHEMA or raw.get("run_id") != expected_run_id: raise CollectorError("wrong hook schema or run")
        _text(raw.get("session_id")); _text(raw.get("turn_id"))
        if raw.get("agent_id") is not None: _text(raw.get("agent_id"))
        if type(raw.get("received_ns")) is not int or raw["received_ns"] < 0: raise CollectorError("invalid hook timestamp")
        digest = raw.get("prompt_digest" if kind == "UserPromptSubmit" else "tool_use_id_digest")
        if not isinstance(digest, str) or not DIGEST_RE.fullmatch(digest): raise CollectorError("invalid hook digest")
        if kind == "PreToolUse": _text(raw.get("tool_name"))
        clean.append(raw)
    root = [(i, record) for i, record in enumerate(clean) if record["agent_id"] is None]
    prompts = [i for i, record in root if record["event_kind"] == "UserPromptSubmit"]
    tools = [i for i, record in root if record["event_kind"] == "PreToolUse"]
    if not prompts and terminal: raise TraceFailure("input-hook-unobserved")
    if len(prompts) != 1: raise CollectorError("requires exactly one accepted-input hook")
    prompt = clean[prompts[0]]
    if not DIGEST_RE.fullmatch(expected_prompt_digest) or prompt["prompt_digest"] != expected_prompt_digest:
        raise CollectorError("accepted-input prompt digest differs from parent prompt")
    session_id, turn_id = str(prompt["session_id"]), str(prompt["turn_id"])
    if session_id != thread_id: raise CollectorError("hook session differs from runtime session")
    if any(record["session_id"] != session_id for _, record in root): raise CollectorError("hook session changed")
    if any(record["turn_id"] != turn_id for _, record in root): raise CollectorError("hook turn changed")
    if terminal: raise TraceFailure("runtime-failed-after-input-hook")
    if kinds.count("turn.completed") != 1: raise CollectorError("requires exactly one turn.completed")
    done_i = kinds.index("turn.completed")
    if not turn_i < done_i: raise CollectorError("runtime lifecycle reordered")
    if not tools: raise CollectorError("requires first-tool hook")
    if tools[0] < prompts[0]: raise CollectorError("first-tool precedes accepted-input")
    tool = clean[tools[0]]
    if tool["received_ns"] < prompt["received_ns"]: raise CollectorError("first-tool timestamp precedes input")
    return TraceEndpoints(session_id, turn_id, int(prompt["received_ns"]), int(tool["received_ns"]), str(tool["tool_name"]))


class _Receiver:
    def __init__(self, clock: Callable[[], int]) -> None:
        base = Path("/tmp") if Path("/tmp").is_dir() else Path(tempfile.gettempdir())
        self.directory = Path(tempfile.mkdtemp(prefix="cbr-", dir=base)); os.chmod(self.directory, 0o700)
        self.socket_path, self.clock = self.directory / "h.sock", clock
        self.records: list[dict[str, object]] = []; self.error: str | None = None
        self.ready, self.done = threading.Event(), threading.Event()
        self.thread = threading.Thread(target=self._serve, daemon=True)

    def _serve(self) -> None:
        try:
            with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as server:
                server.bind(str(self.socket_path)); os.chmod(self.socket_path, 0o600)
                server.listen(64); server.settimeout(.1); self.ready.set()
                while True:
                    try: connection, _ = server.accept()
                    except TimeoutError:
                        if self.done.is_set(): break
                        continue
                    with connection:
                        chunks: list[bytes] = []; size = 0
                        while True:
                            chunk = connection.recv(min(4_096, MAX_HOOK_RECORD_BYTES + 1 - size))
                            if not chunk: break
                            chunks.append(chunk); size += len(chunk)
                            if size > MAX_HOOK_RECORD_BYTES: raise CollectorError("oversized hook record")
                        data = b"".join(chunks)
                    value = json.loads(data)
                    if not isinstance(value, dict): raise CollectorError("non-object hook record")
                    value["received_ns"] = self.clock(); self.records.append(value)
        except Exception as exc:
            self.error = str(exc); self.ready.set()

    def __enter__(self) -> "_Receiver":
        self.thread.start()
        if not self.ready.wait(2) or self.error: raise CollectorError("hook receiver unavailable")
        return self

    def __exit__(self, *_: object) -> None:
        self.done.set(); self.thread.join(3); self.socket_path.unlink(missing_ok=True); shutil.rmtree(self.directory, ignore_errors=True)
        if self.thread.is_alive() or self.error: raise CollectorError("hook receiver failed")


def _scrub_environment(source: Mapping[str, str] | None = None) -> dict[str, str]:
    values = os.environ if source is None else source
    return {key: values[key] for key in ("HOME", "PATH", "CODEX_HOME") if key in values}


def _binary_digest(path: Path) -> str:
    try:
        mode = path.stat().st_mode
        if path.is_symlink() or not stat.S_ISREG(mode) or not os.access(path, os.X_OK): raise CollectorError("Codex binary is not a regular executable")
        return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError as exc:
        raise CollectorError("Codex binary is unavailable") from exc


def _codex_binary_identity(path: Path) -> tuple[Path, str]:
    try: resolved = path.expanduser().resolve(strict=True)
    except OSError as exc: raise CollectorError("Codex binary is unavailable") from exc
    digest = _binary_digest(resolved)
    try:
        completed = subprocess.run(
            [str(resolved), "--version"], env=_scrub_environment(),
            capture_output=True, text=True, timeout=10,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise CollectorError("Codex version probe failed") from exc
    version = completed.stdout.strip()
    if completed.returncode or not version or "\n" in version or "\r" in version: raise CollectorError("Codex version probe failed")
    _text(version, 256)
    label = re.sub(r"[^A-Za-z0-9._/+:-]", "-", version.replace(" ", "/"))
    identity = f"{label}@{digest}"
    if not IDENTITY_RE.fullmatch(identity): raise CollectorError("invalid derived Codex identity")
    return resolved, identity


def _assert_codex_binary_identity(config: CollectorConfig) -> None:
    expected = config.codex_identity.rsplit("@", 1)[-1]
    if _binary_digest(config.codex_binary) != expected: raise CollectorError("Codex binary changed after identity derivation")


def _approved_codex_runtime(contract: Mapping[str, object], *, home: Path | None = None) -> tuple[Path, str]:
    runtime = contract.get("codex_runtime")
    if not isinstance(runtime, dict) or set(runtime) != {"home_relative_path", "identity"}: raise CollectorError("approved Codex runtime is absent")
    relative, expected = runtime.get("home_relative_path"), runtime.get("identity")
    if not isinstance(relative, str) or not isinstance(expected, str) or not IDENTITY_RE.fullmatch(expected): raise CollectorError("approved Codex runtime is invalid")
    path = _relative(relative)
    binary, actual = _codex_binary_identity((home or Path.home()).joinpath(*path.parts))
    if actual != expected: raise CollectorError("approved Codex runtime identity mismatch")
    return binary, actual


def _derived_host_identity() -> str:
    uname = os.uname()
    facts = {"hostname": socket.gethostname(), "machine": uname.machine, "system": uname.sysname}
    return "host@" + _digest_json(facts)


def _build_child_command(codex_binary: Path, *, model: str, reasoning_effort: str, worktree: Path) -> list[str]:
    if not codex_binary.is_absolute() or reasoning_effort not in SUPPORTED_REASONING_EFFORTS: raise CollectorError("invalid Codex command identity")
    disabled = [value for feature in DISABLED_CHILD_FEATURES for value in ("--disable", feature)]
    trusted_project = f'projects={{{json.dumps(str(worktree.resolve()))}={{trust_level="trusted"}}}}'
    return [
        str(codex_binary), "exec", "--json", "--ephemeral", "--ignore-user-config",
        "--ignore-rules", "--strict-config", "--dangerously-bypass-hook-trust",
        *disabled,
        "--sandbox", "workspace-write",
        "-m", model, "-c", f'model_reasoning_effort="{reasoning_effort}"',
        "-c", trusted_project,
        "-c", "sandbox_workspace_write.network_access=false",
        "-c", "sandbox_workspace_write.exclude_slash_tmp=true",
        "-c", "sandbox_workspace_write.exclude_tmpdir_env_var=true",
        "--skip-git-repo-check", "-C", str(worktree / ".capability-benchmark"), "-",
    ]


def _install_hooks(worktree: Path, run_id: str, socket_path: Path, collector_identity: str | None = None) -> None:
    script = Path(__file__).resolve()
    if not script.is_file() or worktree.resolve() in script.parents: raise CollectorError("parent collector path is not isolated")
    if collector_identity is not None:
        expected = collector_identity.rsplit("@", 1)[-1]
        actual = "sha256:" + hashlib.sha256(script.read_bytes()).hexdigest()
        if expected != actual: raise CollectorError("parent collector bytes changed")
    def command(kind: str) -> str:
        return shlex.join([str(Path(sys.executable).resolve()), str(script), "hook", "--event-kind", kind, "--run-id", run_id, "--socket-path", str(socket_path)])
    hooks = {"hooks": {
        "UserPromptSubmit": [{"hooks": [{"type": "command", "command": command("UserPromptSubmit")}]}],
        "PreToolUse": [{"matcher": "*", "hooks": [{"type": "command", "command": command("PreToolUse")}]}],
    }}
    path = worktree / ".codex/hooks.json"; path.parent.mkdir(parents=True, exist_ok=True); path.write_bytes(_bytes(hooks) + b"\n")


def _expected_fixture_contents(profile: str, ordinal: int) -> dict[str, str]:
    if profile not in PROFILES or type(ordinal) is not int or ordinal not in range(1, 6): raise CollectorError("invalid profile/ordinal")
    result = {".capability-benchmark/result-a.txt": f"accepted:{profile}:{ordinal}:a\n"}
    if profile in {"coordination_only", "combined"}: result[".capability-benchmark/result-b.txt"] = f"accepted:{profile}:{ordinal}:b\n"
    return result


def _expected_fixture_inputs(profile: str, ordinal: int) -> dict[str, str]:
    result = {".capability-benchmark/input-a.txt": f"profile={profile}\nordinal={ordinal}\nfixture=a\n"}
    if profile in {"coordination_only", "combined"}: result[".capability-benchmark/input-b.txt"] = f"profile={profile}\nordinal={ordinal}\nfixture=b\n"
    return result


def _load_contract(path: Path) -> dict[str, object]:
    try: value = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as exc: raise CollectorError("cannot load fixed contract") from exc
    profiles = value.get("profiles") if isinstance(value, dict) else None
    if not isinstance(profiles, list) or tuple(item.get("id") for item in profiles if isinstance(item, dict)) != PROFILES: raise CollectorError("wrong contract profiles")
    runtime = value.get("codex_runtime")
    if not isinstance(runtime, dict) or set(runtime) != {"home_relative_path", "identity"} or not isinstance(runtime.get("home_relative_path"), str) or not isinstance(runtime.get("identity"), str) or not IDENTITY_RE.fullmatch(runtime["identity"]): raise CollectorError("wrong contract Codex runtime")
    _relative(runtime["home_relative_path"])
    for item in profiles:
        if item.get("ordinals") != [1, 2, 3, 4, 5] or item.get("scenario_input_digest") != _digest_text(item.get("scenario_input", "")): raise CollectorError("wrong contract scenario")
    return value


def _profile(contract: dict[str, object], name: str) -> dict[str, object]:
    return next(item for item in contract["profiles"] if item["id"] == name)


def _prompt(contract: dict[str, object], profile: str, ordinal: int) -> str:
    fixed = (
        "Work only in the current directory. Use any suitable local tool. Do not use network, Git, providers, coordination, .codex/runtime, or logs. "
        "The parent alone derives route, review, effect, and benchmark evidence. Create exactly the requested result files with exact UTF-8 contents, then reply DONE."
    )
    expected = "\n".join(
        f"- {path.removeprefix('.capability-benchmark/')}: {content.rstrip()}"
        for path, content in _expected_fixture_contents(profile, ordinal).items()
    )
    return f"Scenario: {_profile(contract, profile)['scenario_input']}\nProfile: {profile}; ordinal: {ordinal}.\n{fixed}\nExpected results:\n{expected}\nBenchmark instruction digest: {_digest_text(fixed)}\n"


def _git(repo: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[bytes]:
    env = {
        "PATH": "/usr/bin:/bin:/usr/sbin:/sbin",
        "HOME": "/var/empty", "LC_ALL": "C", "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_CONFIG_GLOBAL": "/dev/null", "GIT_TERMINAL_PROMPT": "0",
    }
    command = [str(GIT_BINARY), "-c", "core.hooksPath=/dev/null", "-c", "core.fsmonitor=false", *args]
    try: return subprocess.run(command, cwd=repo, env=env, check=check, capture_output=True)
    except (OSError, subprocess.CalledProcessError) as exc: raise CollectorError("Git operation failed") from exc


def _validate_fixture(worktree: Path, profile: str, ordinal: int) -> tuple[str, str]:
    expected = {**_expected_fixture_inputs(profile, ordinal), **_expected_fixture_contents(profile, ordinal)}
    fixture = worktree / ".capability-benchmark"
    git_directory = worktree / ".git"
    if fixture.is_symlink() or not fixture.is_dir() or git_directory.is_symlink() or not git_directory.is_dir(): raise CollectorError("invalid fixture tree")
    actual_tree: dict[str, str] = {}; seen_files: set[str] = set(); seen_directories: set[str] = set()
    for directory, directories, files in os.walk(worktree, followlinks=False):
        root = Path(directory)
        if any((root / name).is_symlink() for name in directories): raise CollectorError("invalid fixture tree")
        if root == worktree:
            directories.remove(".git")
        seen_directories.update((root / name).relative_to(worktree).as_posix() for name in directories)
        for name in files:
            path = root / name
            if path.is_symlink() or not path.is_file(): raise CollectorError("invalid fixture tree")
            relative = path.relative_to(worktree).as_posix(); seen_files.add(relative)
            if relative in expected: actual_tree[relative] = path.read_text()
    if seen_directories != {".capability-benchmark", ".codex"} or seen_files != set(expected) | {".codex/hooks.json"} or actual_tree != expected:
        raise CollectorError("invalid fixture tree")
    outputs = _expected_fixture_contents(profile, ordinal)
    scope = [{"path": path, "content_digest": _digest_text(content)} for path, content in outputs.items()]
    return _digest_json(outputs), _digest_json(scope)


def _relative(value: str) -> PurePosixPath:
    path = PurePosixPath(value)
    if not value or path.is_absolute() or ".." in path.parts or path.as_posix() != value: raise CollectorError("unsafe relative path")
    return path


def _safe(root: Path, relative: str) -> Path:
    path, current = _relative(relative), root
    if root.is_symlink(): raise CollectorError("symlink evidence root")
    for part in path.parts:
        current = current / part
        if current.exists() or current.is_symlink():
            if stat.S_ISLNK(current.lstat().st_mode): raise CollectorError("evidence path traverses symlink")
    return root.joinpath(*path.parts)


def _parents(root: Path, parent: Path) -> None:
    root.mkdir(parents=True, exist_ok=True, mode=0o700); current = root
    for part in parent.relative_to(root).parts:
        current /= part
        if current.exists() or current.is_symlink():
            mode = current.lstat().st_mode
            if stat.S_ISLNK(mode) or not stat.S_ISDIR(mode): raise CollectorError("unsafe evidence parent")
        else: current.mkdir(mode=0o700)


def _write(path: Path, value: object, *, exclusive: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True); encoded = _bytes(value) + b"\n"
    if exclusive:
        flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
        try: descriptor = os.open(path, flags, 0o600)
        except OSError as exc: raise CollectorError("exclusive state write failed") from exc
        with os.fdopen(descriptor, "wb") as stream: stream.write(encoded); stream.flush(); os.fsync(stream.fileno())
        return
    if path.is_symlink(): raise CollectorError("refusing symlink replacement")
    temporary = path.with_name(f".{path.name}.{secrets.token_hex(6)}")
    try:
        descriptor = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(descriptor, "wb") as stream: stream.write(encoded); stream.flush(); os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally: temporary.unlink(missing_ok=True)


def _load(path: Path) -> dict[str, object]:
    try: value = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as exc: raise CollectorError("invalid state JSON") from exc
    if not isinstance(value, dict): raise CollectorError("state is not an object")
    return value


def _effect_paths(root: Path, run_id: str) -> tuple[Path, Path]:
    _run_id(run_id)
    return _safe(root, f".capability-state/effects/{run_id}.json"), _safe(root, f".codex/runtime/capability-baseline/{run_id}/marker.json")


def _effect_nonce(run_id: str, request_digest: str) -> str:
    if not DIGEST_RE.fullmatch(request_digest): raise CollectorError("bad effect digest")
    return hashlib.sha256(f"effect\0{run_id}\0{request_digest}".encode()).hexdigest()


def _effect_marker(run_id: str, request_digest: str, nonce: str) -> dict[str, str]:
    return {"schema_version": "capability-baseline-effect-marker/v1", "run_id": run_id, "request_digest": request_digest, "nonce": nonce}


def _write_marker_exclusive(path: Path, payload: dict[str, object]) -> None: _write(path, payload, exclusive=True)


def _execute_marker_effect(*, evidence_root: Path, run_id: str, request_digest: str, profile: str, marker_writer: Callable[[Path, dict[str, object]], None] = _write_marker_exclusive) -> EffectResult:
    if profile not in EFFECT_PROFILES: raise CollectorError(f"marker effect is not authorized for profile {profile}")
    reservation_path, marker_path = _effect_paths(evidence_root, run_id)
    _parents(evidence_root, reservation_path.parent); _parents(evidence_root, marker_path.parent)
    nonce = _effect_nonce(run_id, request_digest)
    fixed = {"schema_version": EFFECT_RESERVATION_SCHEMA, "run_id": run_id, "request_digest": request_digest, "nonce": nonce}
    marker = _effect_marker(run_id, request_digest, nonce)
    if reservation_path.exists() or reservation_path.is_symlink():
        if reservation_path.is_symlink(): raise CollectorError("symlink effect reservation")
        current = _load(reservation_path)
        if any(current.get(key) != value for key, value in fixed.items()): raise ReplayConflict("changed effect replay")
        if current.get("state") == "completed":
            if marker_path.is_symlink() or _load(marker_path) != marker: raise CollectorError("mismatched completed marker")
            return EffectResult(marker_path.relative_to(evidence_root).as_posix(), nonce, False, False)
        if current.get("state") == "attempting":
            if not marker_path.exists(): raise EffectUncertain("effect outcome uncertain; no retry")
            if marker_path.is_symlink() or _load(marker_path) != marker: raise CollectorError("mismatched attempted marker")
            current.update(state="completed", reconciled=True); _write(reservation_path, current)
            return EffectResult(marker_path.relative_to(evidence_root).as_posix(), nonce, False, True)
        raise EffectUncertain("nonterminal effect reservation; no retry")
    reservation = {**fixed, "state": "reserved"}; _write(reservation_path, reservation, exclusive=True)
    reservation["state"] = "attempting"; _write(reservation_path, reservation)
    marker_writer(marker_path, marker)
    reservation.update(state="completed", reconciled=False); _write(reservation_path, reservation)
    return EffectResult(marker_path.relative_to(evidence_root).as_posix(), nonce, True, False)


def _coord(run_id: str) -> str: return f"coordination/capability-baseline/{run_id}/route.json"
def _review(run_id: str) -> str: return f"coordination/verification/capability-baseline/{run_id}/review.json"


def _evidence_write(root: Path, relative: str, value: object) -> None:
    path = _safe(root, relative); _parents(root, path.parent)
    if path.exists():
        if _load(path) != value: raise ReplayConflict("changed parent evidence")
    else: _write(path, value, exclusive=True)


def _derive_profile_evidence(*, profile: str, run_id: str, evidence_root: Path, source_head: str, scope_digest: str, request_digest: str, accepted_route_ns: int | None, monotonic_ns: Callable[[], int]) -> ProfileEvidence:
    if profile not in PROFILES or not SHA_RE.fullmatch(source_head) or not DIGEST_RE.fullmatch(scope_digest) or not DIGEST_RE.fullmatch(request_digest): raise CollectorError("bad evidence identity")
    artifacts: list[dict[str, str]] = []; reviews: list[dict[str, str]] = []; endpoints: dict[str, int] = {}; attempted = False
    if profile in {"coordination_only", "combined"}:
        path = _coord(run_id); _evidence_write(evidence_root, path, {"schema_version": "capability-baseline-route/v1", "run_id": run_id, "source_head": source_head, "scope_digest": scope_digest}); artifacts.append({"path": path, "class": "coordination"})
    if profile in {"verification_only", "combined"}:
        identity = {"base": source_head, "head": source_head, "scope_digest": scope_digest, "question_digest": QUESTION_DIGEST}
        review = {
            "schema_version": "capability-baseline-review/v1", "run_id": run_id,
            "identity": identity, "verdict": "GO",
            "verifier": "deterministic-fixture-verifier/v1",
        }
        path = _review(run_id); _evidence_write(evidence_root, path, review); artifacts.append({"path": path, "class": "verification"}); reviews.append(identity)
    if profile == "combined":
        if type(accepted_route_ns) is not int: raise CollectorError("combined route timestamp absent")
        go = monotonic_ns()
        if go < accepted_route_ns: raise CollectorError("GO precedes route")
        endpoints = {"accepted_route": accepted_route_ns, "published_go": go}
    elif accepted_route_ns is not None: raise CollectorError("route timestamp outside combined")
    if profile in EFFECT_PROFILES:
        effect = _execute_marker_effect(evidence_root=evidence_root, run_id=run_id, request_digest=request_digest, profile=profile); artifacts.append({"path": effect.path, "class": "effect"}); attempted = effect.attempted
    result = ProfileEvidence(tuple(artifacts), tuple(reviews), endpoints, attempted)
    _validate_profile_evidence(profile=profile, run_id=run_id, evidence_root=evidence_root, artifacts=result.artifacts, reviews=result.reviews, source_head=source_head, scope_digest=scope_digest, request_digest=request_digest)
    return result


def _validate_profile_evidence(*, profile: str, run_id: str, evidence_root: Path, artifacts: Sequence[Mapping[str, object]], reviews: Sequence[Mapping[str, object]], source_head: str, scope_digest: str, request_digest: str) -> None:
    if profile not in PROFILES or not SHA_RE.fullmatch(source_head) or not DIGEST_RE.fullmatch(scope_digest) or not DIGEST_RE.fullmatch(request_digest): raise CollectorError("bad profile evidence identity")
    paths: dict[str, str] = {}
    if "coordination" in PROFILE_CLASSES[profile]: paths[_coord(run_id)] = "coordination"
    if "verification" in PROFILE_CLASSES[profile]: paths[_review(run_id)] = "verification"
    if "effect" in PROFILE_CLASSES[profile]: paths[f".codex/runtime/capability-baseline/{run_id}/marker.json"] = "effect"
    if len(artifacts) != len(paths): raise CollectorError("missing or forbidden profile evidence")
    seen = set()
    for artifact in artifacts:
        relative = artifact.get("path")
        if set(artifact) != {"path", "class"} or not isinstance(relative, str) or paths.get(relative) != artifact.get("class"): raise CollectorError("artifact belongs to another run or class")
        path = _safe(evidence_root, relative)
        if path.is_symlink(): raise CollectorError("profile artifact is symlink")
        if not path.is_file(): raise CollectorError("profile artifact absent")
        seen.add(relative)
    if seen != set(paths): raise CollectorError("wrong profile artifact set")
    identity = {"base": source_head, "head": source_head, "scope_digest": scope_digest, "question_digest": QUESTION_DIGEST}
    if profile in {"coordination_only", "combined"}:
        route = {"schema_version": "capability-baseline-route/v1", "run_id": run_id, "source_head": source_head, "scope_digest": scope_digest}
        if _load(_safe(evidence_root, _coord(run_id))) != route: raise CollectorError("route evidence content mismatch")
    if profile in {"verification_only", "combined"}:
        review = {
            "schema_version": "capability-baseline-review/v1", "run_id": run_id,
            "identity": identity, "verdict": "GO",
            "verifier": "deterministic-fixture-verifier/v1",
        }
        if len(reviews) != 1 or dict(reviews[0]) != identity: raise CollectorError("review identity mismatch")
        if _load(_safe(evidence_root, _review(run_id))) != review: raise CollectorError("review evidence content mismatch")
    elif reviews: raise CollectorError("forbidden review evidence")

    reservation_path, marker_path = _effect_paths(evidence_root, run_id)
    if profile in EFFECT_PROFILES:
        nonce = _effect_nonce(run_id, request_digest)
        reservation = {
            "schema_version": EFFECT_RESERVATION_SCHEMA, "state": "completed",
            "run_id": run_id, "request_digest": request_digest, "nonce": nonce,
        }
        if reservation_path.is_symlink() or not reservation_path.is_file(): raise CollectorError("effect reservation evidence absent")
        current = _load(reservation_path)
        if set(current) != set(reservation) | {"reconciled"} or any(current.get(key) != value for key, value in reservation.items()) or type(current.get("reconciled")) is not bool:
            raise CollectorError("effect reservation evidence mismatch")
        if marker_path.is_symlink() or _load(marker_path) != _effect_marker(run_id, request_digest, nonce): raise CollectorError("effect marker evidence mismatch")
    elif any(path.exists() or path.is_symlink() for path in (reservation_path, marker_path)):
        raise CollectorError("forbidden effect evidence")


def _profile_evidence_digest(*, profile: str, run_id: str, evidence_root: Path, artifacts: Sequence[Mapping[str, object]], reviews: Sequence[Mapping[str, object]]) -> str:
    entries = []
    for artifact in artifacts:
        relative = artifact.get("path")
        if not isinstance(relative, str): raise CollectorError("invalid profile evidence path")
        path = _safe(evidence_root, relative)
        if path.is_symlink() or not path.is_file(): raise CollectorError("profile evidence unavailable")
        entries.append({
            "path": relative, "class": artifact.get("class"),
            "content_digest": "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest(),
        })
    entries.sort(key=lambda item: (str(item["class"]), str(item["path"])))
    return _digest_json({
        "schema_version": "capability-baseline-profile-evidence-digest/v1",
        "profile": profile, "run_id": run_id, "artifacts": entries,
        "reviews": [dict(review) for review in reviews],
    })


def _record(
    run_id: str,
    request_digest: str,
    status: str,
    observation: Mapping[str, object] | None,
    error: str | None,
    attempted: bool,
    runtime_evidence_digest: str | None = None,
    profile_evidence_digest: str | None = None,
) -> RunRecord:
    _run_id(run_id)
    if not DIGEST_RE.fullmatch(request_digest) or status not in {"completed", "failed", "uncertain"}: raise CollectorError("invalid run record identity")
    if error is not None and not isinstance(error, str): raise CollectorError("invalid run record error")
    if type(attempted) is not bool: raise CollectorError("invalid effect-attempt flag")
    for digest in (runtime_evidence_digest, profile_evidence_digest):
        if digest is not None and not DIGEST_RE.fullmatch(digest): raise CollectorError("invalid evidence digest")
    obs = dict(observation or {})
    body = {
        "schema_version": RUN_RECORD_SCHEMA, "run_id": run_id,
        "request_digest": request_digest, "status": status,
        "observation": obs, "error": error, "effect_attempted": attempted,
        "runtime_evidence_digest": runtime_evidence_digest,
        "profile_evidence_digest": profile_evidence_digest,
    }
    return RunRecord(
        run_id, request_digest, status, _bytes(obs).decode(), error, attempted,
        runtime_evidence_digest, profile_evidence_digest, _digest_json(body),
    )


def _collector_failure_code(error: CollectorError) -> str:
    message = str(error)
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9 ._-]{0,119}", message):
        return "collector-error"
    return re.sub(r"[^a-z0-9]+", "-", message.lower()).strip("-") or "collector-error"


def _load_record(path: Path) -> RunRecord:
    if path.is_symlink() or not path.is_file(): raise CollectorError("invalid run record path")
    value = _load(path)
    expected = {
        "schema_version", "run_id", "request_digest", "status", "observation",
        "error", "effect_attempted", "runtime_evidence_digest",
        "profile_evidence_digest", "record_digest",
    }
    if set(value) != expected or value.get("schema_version") != RUN_RECORD_SCHEMA: raise CollectorError("invalid run record fields")
    if not isinstance(value.get("run_id"), str) or not isinstance(value.get("request_digest"), str) or not isinstance(value.get("status"), str): raise CollectorError("invalid run record identity")
    if not isinstance(value.get("observation"), dict) or (value.get("error") is not None and not isinstance(value.get("error"), str)) or type(value.get("effect_attempted")) is not bool: raise CollectorError("invalid run record types")
    for key in ("runtime_evidence_digest", "profile_evidence_digest"):
        if value.get(key) is not None and (not isinstance(value[key], str) or not DIGEST_RE.fullmatch(value[key])): raise CollectorError("invalid run record evidence digest")
    record = _record(
        value["run_id"], value["request_digest"], value["status"],
        value["observation"], value["error"], value["effect_attempted"],
        value["runtime_evidence_digest"], value["profile_evidence_digest"],
    )
    if value != record.as_json(): raise CollectorError("invalid run record digest")
    return record


def _signal_process_group(pid: int, signal_number: int) -> bool:
    try: os.killpg(pid, signal_number); return True
    except ProcessLookupError: return False
    except OSError as exc: raise CollectorError("Codex process group cleanup failed") from exc


def _stop_process_group(pid: int) -> None:
    if not _signal_process_group(pid, signal.SIGTERM): return
    time.sleep(0.05)
    _signal_process_group(pid, signal.SIGKILL)


def _confirm_process_group_gone(pid: int) -> None:
    deadline = time.monotonic() + 0.5
    while True:
        if not _signal_process_group(pid, 0): return
        if time.monotonic() >= deadline: raise CollectorError("Codex process group survived cleanup")
        time.sleep(0.02)


def _process(command: Sequence[str], prompt: str, cwd: Path, env: Mapping[str, str], timeout: int) -> ProcessCapture:
    try:
        process = subprocess.Popen(
            list(command), cwd=cwd, env=dict(env), stdin=subprocess.PIPE,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
            start_new_session=True,
        )
    except OSError: return ProcessCapture(127, "", "", False)
    try:
        stdout, stderr = process.communicate(prompt, timeout=timeout)
        _stop_process_group(process.pid); _confirm_process_group_gone(process.pid)
        return ProcessCapture(process.returncode, stdout, stderr, False)
    except subprocess.TimeoutExpired:
        _stop_process_group(process.pid)
        try: stdout, stderr = process.communicate(timeout=2)
        except subprocess.TimeoutExpired as exc: raise CollectorError("Codex process group did not exit after kill") from exc
        _confirm_process_group_gone(process.pid)
        return ProcessCapture(124, stdout, stderr, True)


@contextlib.contextmanager
def _workspace(_config: CollectorConfig, _run_id_value: str):
    base = Path(tempfile.mkdtemp(prefix="cbr-work-", dir="/tmp")); workspace = base / "workspace"; workspace.mkdir()
    try:
        _git(workspace, "init", "-q")
        yield workspace
    finally:
        try: shutil.rmtree(base)
        except OSError as exc: raise CollectorError("disposable workspace cleanup failed") from exc


def _runtime_evidence_digest(run_id: str, request_digest: str, capture: ProcessCapture, hook_records: Sequence[object]) -> str:
    return _digest_json({
        "schema_version": "capability-baseline-runtime-evidence-digest/v1",
        "run_id": run_id, "request_digest": request_digest,
        "stdout_digest": _digest_text(capture.stdout),
        "stderr_digest": _digest_text(capture.stderr),
        "hook_records_digest": _digest_json(list(hook_records)),
        "exit_code": capture.returncode, "timed_out": capture.timed_out,
    })


def _validate_run_reservation(path: Path, *, run_id: str, request_digest: str, identity: Mapping[str, object], state: str | None = None) -> dict[str, object]:
    if path.is_symlink() or not path.is_file(): raise CollectorError("invalid run reservation path")
    value = _load(path)
    expected = {"schema_version", "state", "run_id", "request_digest", "request"}
    if set(value) != expected or value.get("schema_version") != RUN_RESERVATION_SCHEMA:
        raise CollectorError("invalid run reservation fields")
    if value.get("run_id") != run_id or value.get("request_digest") != request_digest or value.get("request") != dict(identity):
        raise ReplayConflict("changed reserved replay")
    if value.get("state") not in {"reserved", "started", "completed", "failed", "uncertain"}:
        raise CollectorError("invalid run reservation state")
    if state is not None and value.get("state") != state: raise CollectorError("run reservation/record state mismatch")
    return value


def _assert_no_run_evidence(evidence_root: Path, run_id: str) -> None:
    reservation_path, marker_path = _effect_paths(evidence_root, run_id)
    paths = (
        _safe(evidence_root, _coord(run_id)), _safe(evidence_root, _review(run_id)),
        reservation_path, marker_path,
    )
    if any(path.exists() or path.is_symlink() for path in paths): raise ReplayConflict("orphan run evidence requires investigation")


def _expected_scope_digest(profile: str, ordinal: int) -> str:
    scope = [
        {"path": path, "content_digest": _digest_text(content)}
        for path, content in _expected_fixture_contents(profile, ordinal).items()
    ]
    return _digest_json(scope)


def _effect_may_have_been_attempted(evidence_root: Path, run_id: str, request_digest: str, profile: str) -> bool:
    if profile not in EFFECT_PROFILES: return False
    try:
        reservation_path, _ = _effect_paths(evidence_root, run_id)
        if reservation_path.is_symlink() or not reservation_path.is_file(): return False
        value = _load(reservation_path)
        nonce = _effect_nonce(run_id, request_digest)
        fixed = {"schema_version": EFFECT_RESERVATION_SCHEMA, "run_id": run_id, "request_digest": request_digest, "nonce": nonce}
        return all(value.get(key) == expected for key, expected in fixed.items()) and value.get("state") in {"attempting", "completed"}
    except CollectorError:
        return False


def _run_identity(config: CollectorConfig, contract: Mapping[str, object], profile: str, ordinal: int) -> dict[str, object]:
    return {
        "cohort_id": config.cohort_id, "profile": profile, "ordinal": ordinal,
        "source_head": config.source_head, "contract_digest": _digest_json(contract),
        "scenario_input_digest": _profile(dict(contract), profile)["scenario_input_digest"],
        "collector_identity": config.collector_identity, "codex_identity": config.codex_identity,
        "model": config.model, "reasoning_effort": config.reasoning_effort,
        "host_identity": config.host_identity,
        "prompt_digest": _digest_text(_prompt(dict(contract), profile, ordinal)),
    }


def _validate_replayed_record(
    config: CollectorConfig,
    contract: Mapping[str, object],
    profile: str,
    ordinal: int,
    identity: Mapping[str, object],
    record: RunRecord,
    reservation_path: Path,
) -> None:
    run_id = f"{config.cohort_id}-{profile}-{ordinal}"
    if record.run_id != run_id or record.request_digest != _digest_json(identity): raise ReplayConflict("changed completed replay")
    _validate_run_reservation(
        reservation_path, run_id=run_id, request_digest=record.request_digest,
        identity=identity, state=record.status,
    )
    if record.status != "completed":
        if record.observation or not isinstance(record.error, str) or not record.error: raise CollectorError("invalid nonterminal run record")
        return
    if record.error is not None or not isinstance(record.runtime_evidence_digest, str) or not DIGEST_RE.fullmatch(record.runtime_evidence_digest):
        raise CollectorError("completed run lacks runtime evidence")
    if not isinstance(record.profile_evidence_digest, str) or not DIGEST_RE.fullmatch(record.profile_evidence_digest):
        raise CollectorError("completed run lacks profile evidence")
    observation = record.observation
    expected_keys = {
        "run_id", "profile", "ordinal", "host_identity", "clock_domain",
        "instrumentation_identity", "scenario_input_digest", "accepted_result_digest",
        "endpoints", "artifacts", "reviews",
    }
    if set(observation) != expected_keys: raise CollectorError("invalid replay observation fields")
    fixed = {
        "run_id": run_id, "profile": profile, "ordinal": ordinal,
        "host_identity": config.host_identity, "clock_domain": CLOCK_DOMAIN,
        "instrumentation_identity": INSTRUMENTATION_IDENTITY,
        "scenario_input_digest": _profile(dict(contract), profile)["scenario_input_digest"],
        "accepted_result_digest": _digest_json(_expected_fixture_contents(profile, ordinal)),
    }
    if any(observation.get(key) != value for key, value in fixed.items()): raise CollectorError("replay observation differs from deterministic fixture")
    endpoints = observation.get("endpoints")
    expected_endpoints = {"accepted_input", "first_tool_callback"}
    if profile == "combined": expected_endpoints |= {"accepted_route", "published_go"}
    if not isinstance(endpoints, dict) or set(endpoints) != expected_endpoints: raise CollectorError("invalid replay endpoint set")
    for endpoint in endpoints.values():
        if not isinstance(endpoint, dict) or set(endpoint) != {"ns", "clock_domain"} or type(endpoint.get("ns")) is not int or endpoint["ns"] < 0 or endpoint.get("clock_domain") != CLOCK_DOMAIN:
            raise CollectorError("invalid replay endpoint")
    if endpoints["first_tool_callback"]["ns"] < endpoints["accepted_input"]["ns"]: raise CollectorError("replay tool endpoint precedes input")
    if profile == "combined" and endpoints["published_go"]["ns"] < endpoints["accepted_route"]["ns"]: raise CollectorError("replay GO precedes route")
    artifacts, reviews = observation.get("artifacts"), observation.get("reviews")
    if not isinstance(artifacts, list) or not isinstance(reviews, list): raise CollectorError("invalid replay profile evidence")
    evidence_root = config.cohort_root / "evidence"
    scope_digest = _expected_scope_digest(profile, ordinal)
    _validate_profile_evidence(
        profile=profile, run_id=run_id, evidence_root=evidence_root,
        artifacts=artifacts, reviews=reviews, source_head=config.source_head,
        scope_digest=scope_digest, request_digest=record.request_digest,
    )
    digest = _profile_evidence_digest(
        profile=profile, run_id=run_id, evidence_root=evidence_root,
        artifacts=artifacts, reviews=reviews,
    )
    if record.profile_evidence_digest != digest: raise CollectorError("profile evidence digest mismatch")
    if record.effect_attempted is not (profile in EFFECT_PROFILES): raise CollectorError("effect-attempt record mismatch")


def run_one(config: CollectorConfig, profile: str, ordinal: int, *, process_runner: ProcessRunner = _process, workspace_factory: WorkspaceFactory = _workspace, monotonic_ns: Callable[[], int] = time.monotonic_ns) -> RunRecord:
    """Reserve and execute one exact profile/ordinal; never retry an identity."""
    if profile not in PROFILES or ordinal not in range(1, 6): raise CollectorError("run outside fixed cohort")
    if profile in EFFECT_PROFILES and not config.local_markers_authorized: raise CollectorError("explicit local marker authorization is required")
    if process_runner is _process:
        _assert_codex_binary_identity(config)
        _assert_committed_runtime(config)
    contract = _load_contract(config.contract_path); run_id = f"{config.cohort_id}-{profile}-{ordinal}"
    identity = _run_identity(config, contract, profile, ordinal)
    request_digest = _digest_json(identity)
    state = _safe(config.cohort_root, f"records/{run_id}")
    reservation_path = _safe(config.cohort_root, f"records/{run_id}/reservation.json")
    record_path = _safe(config.cohort_root, f"records/{run_id}/record.json")
    if record_path.exists() or record_path.is_symlink():
        old = _load_record(record_path)
        if old.request_digest != request_digest: raise ReplayConflict("changed completed replay")
        if not config.resume: raise ReplayConflict("existing run requires explicit resume")
        _validate_replayed_record(config, contract, profile, ordinal, identity, old, reservation_path)
        return old
    if reservation_path.exists() or reservation_path.is_symlink():
        _validate_run_reservation(reservation_path, run_id=run_id, request_digest=request_digest, identity=identity)
        if not config.resume: raise ReplayConflict("existing run requires explicit resume")
        raise CollectorError("reserved/started run is uncertain; no retry")
    _assert_no_run_evidence(config.cohort_root / "evidence", run_id)
    _parents(config.cohort_root, state)
    reservation = {"schema_version": RUN_RESERVATION_SCHEMA, "state": "reserved", "run_id": run_id, "request_digest": request_digest, "request": identity}
    _write(reservation_path, reservation, exclusive=True); accepted_route = monotonic_ns() if profile == "combined" else None
    reservation["state"] = "started"; _write(reservation_path, reservation)
    prompt = _prompt(contract, profile, ordinal)
    runtime_digest: str | None = None
    profile_digest: str | None = None
    try:
        with workspace_factory(config, run_id) as workspace:
            fixture = workspace / ".capability-benchmark"; fixture.mkdir(parents=True, exist_ok=True)
            for relative, content in _expected_fixture_inputs(profile, ordinal).items(): (workspace / relative).write_text(content)
            with _Receiver(monotonic_ns) as receiver:
                _install_hooks(workspace, run_id, receiver.socket_path, config.collector_identity if process_runner is _process else None)
                capture = process_runner(_build_child_command(config.codex_binary, model=config.model, reasoning_effort=config.reasoning_effort, worktree=workspace), prompt, workspace, _scrub_environment(), config.timeout_seconds)
            runtime_digest = _runtime_evidence_digest(run_id, request_digest, capture, receiver.records)
            if capture.timed_out:
                result = _record(run_id, request_digest, "uncertain", None, "codex-timeout-outcome-unknown", False, runtime_digest)
                _write(record_path, result.as_json(), exclusive=True); reservation["state"] = "uncertain"; _write(reservation_path, reservation)
                _validate_replayed_record(config, contract, profile, ordinal, identity, result, reservation_path)
                return result
            endpoints = parse_runtime_trace(
                capture.stdout,
                exit_code=capture.returncode,
                hook_records=receiver.records,
                expected_run_id=run_id,
                expected_prompt_digest=_digest_text(prompt),
            )
            accepted_digest, scope_digest = _validate_fixture(workspace, profile, ordinal)
        evidence = _derive_profile_evidence(profile=profile, run_id=run_id, evidence_root=config.cohort_root / "evidence", source_head=config.source_head, scope_digest=scope_digest, request_digest=request_digest, accepted_route_ns=accepted_route, monotonic_ns=monotonic_ns)
        profile_digest = _profile_evidence_digest(
            profile=profile, run_id=run_id, evidence_root=config.cohort_root / "evidence",
            artifacts=evidence.artifacts, reviews=evidence.reviews,
        )
        endpoint_map = {
            "accepted_input": {"ns": endpoints.accepted_input_ns, "clock_domain": CLOCK_DOMAIN},
            "first_tool_callback": {"ns": endpoints.first_tool_callback_ns, "clock_domain": CLOCK_DOMAIN},
        }
        endpoint_map.update({name: {"ns": ns, "clock_domain": CLOCK_DOMAIN} for name, ns in evidence.route_endpoints.items()})
        observation = {
            "run_id": run_id, "profile": profile, "ordinal": ordinal,
            "host_identity": config.host_identity, "clock_domain": CLOCK_DOMAIN,
            "instrumentation_identity": INSTRUMENTATION_IDENTITY,
            "scenario_input_digest": _profile(contract, profile)["scenario_input_digest"],
            "accepted_result_digest": accepted_digest, "endpoints": endpoint_map,
            "artifacts": [dict(item) for item in evidence.artifacts], "reviews": [dict(item) for item in evidence.reviews],
        }
        result = _record(run_id, request_digest, "completed", observation, None, evidence.effect_attempted, runtime_digest, profile_digest)
    except EffectUncertain:
        result = _record(run_id, request_digest, "uncertain", None, "effect-outcome-unknown", True, runtime_digest, profile_digest)
    except CollectorError as exc:
        attempted = _effect_may_have_been_attempted(config.cohort_root / "evidence", run_id, request_digest, profile)
        result = _record(
            run_id, request_digest, "failed", None,
            f"run-evidence-invalid:{_collector_failure_code(exc)}",
            attempted, runtime_digest, profile_digest,
        )
    except (OSError, ValueError, UnicodeError):
        attempted = _effect_may_have_been_attempted(config.cohort_root / "evidence", run_id, request_digest, profile)
        result = _record(run_id, request_digest, "failed", None, "run-evidence-invalid", attempted, runtime_digest, profile_digest)
    _write(record_path, result.as_json(), exclusive=True); reservation["state"] = result.status; _write(reservation_path, reservation)
    _validate_replayed_record(config, contract, profile, ordinal, identity, result, reservation_path)
    return result


def _reporter() -> object:
    global _REPORTER_MODULE
    if _REPORTER_MODULE is not None: return _REPORTER_MODULE
    path = Path(__file__).resolve().with_name("protocol_effectiveness_report.py"); inserted = str(path.parent) not in sys.path
    if inserted: sys.path.insert(0, str(path.parent))
    try:
        spec = importlib.util.spec_from_file_location("_capability_reporter", path)
        if spec is None or spec.loader is None: raise CollectorError("reporter unavailable")
        module = importlib.util.module_from_spec(spec); sys.modules[spec.name] = module; spec.loader.exec_module(module); _REPORTER_MODULE = module; return module
    finally:
        if inserted: sys.path.remove(str(path.parent))


def run_cohort(config: CollectorConfig, *, process_runner: ProcessRunner = _process, workspace_factory: WorkspaceFactory = _workspace, monotonic_ns: Callable[[], int] = time.monotonic_ns) -> CohortResult:
    """Run ordinal-first/profile-inner, stopping without retry on first invalid run."""
    if config.resume: raise CollectorError("resumed cohort cannot issue operational provenance")
    if not config.resume and (config.cohort_root.exists() or config.cohort_root.is_symlink()):
        if config.cohort_root.is_symlink() or not config.cohort_root.is_dir() or any(config.cohort_root.iterdir()):
            raise ReplayConflict("fresh cohort root is not empty")
    contract, records = _load_contract(config.contract_path), []
    for ordinal in range(1, 6):
        for profile in PROFILES:
            record = run_one(config, profile, ordinal, process_runner=process_runner, workspace_factory=workspace_factory, monotonic_ns=monotonic_ns); records.append(record)
            if record.status != "completed": raise CollectorError(f"cohort stopped at {record.run_id}")
    for record in records:
        profile, ordinal = _profile_ordinal_from_run_id(record.run_id)
        identity = _run_identity(config, contract, profile, ordinal)
        record_path = _safe(config.cohort_root, f"records/{record.run_id}/record.json")
        reservation_path = _safe(config.cohort_root, f"records/{record.run_id}/reservation.json")
        persisted = _load_record(record_path)
        _validate_replayed_record(config, contract, profile, ordinal, identity, persisted, reservation_path)
        if persisted != record: raise CollectorError("run record changed after collection")
    if process_runner is _process:
        _assert_codex_binary_identity(config)
        _assert_committed_runtime(config)
    if len({record.run_id for record in records}) != 25 or sum(record.effect_attempted for record in records) != 10: raise CollectorError("wrong cohort/effect count")
    observations = {
        "schema_version": "capability-first-baseline-observations/v1", "evidence_kind": "runtime_trace",
        "host_identity": config.host_identity, "clock_domain": CLOCK_DOMAIN,
        "instrumentation_identity": INSTRUMENTATION_IDENTITY, "runs": [record.observation for record in records],
    }
    if len({run["accepted_result_digest"] for run in observations["runs"]}) != 25: raise CollectorError("non-unique accepted results")
    reporter = _reporter(); provenance_type = getattr(reporter, "VerifiedBaselineProvenance", None)
    if provenance_type is None: raise CollectorError("reporter lacks verified provenance")
    provenance = provenance_type(
        contract_digest=_digest_json(contract), observations_digest=_digest_json(observations),
        cohort_identity=(("benchmark_id", contract["benchmark_id"]), ("host_identity", config.host_identity), ("clock_domain", CLOCK_DOMAIN), ("instrumentation_identity", INSTRUMENTATION_IDENTITY)),
        collector_identity=config.collector_identity, source_head=config.source_head,
        codex_identity=config.codex_identity, run_record_digests=tuple((record.run_id, record.record_digest) for record in records),
    )
    return CohortResult(observations, tuple(records), provenance, config.cohort_root / "evidence")


def _preflight_committed_paths(repo_root: Path, source_head: str | None, required_paths: Sequence[str]) -> dict[str, object]:
    root = repo_root.resolve()
    try: current = _git(root, "rev-parse", "HEAD").stdout.decode().strip()
    except CollectorError as exc: raise PreflightError("commit-required: repository has no committed HEAD") from exc
    pinned = source_head or current
    if not SHA_RE.fullmatch(pinned) or pinned != current: raise PreflightError("commit-required: pinned and checkout HEAD differ")
    blobs, errors = {}, []
    for value in required_paths:
        try: path = root.joinpath(*_relative(value).parts)
        except CollectorError: errors.append(f"invalid path {value}"); continue
        if path.is_symlink() or not path.is_file(): errors.append(f"{value} is absent/untracked"); continue
        status = _git(root, "status", "--porcelain=v1", "--", value, check=False)
        blob = _git(root, "show", f"{pinned}:{value}", check=False)
        if status.returncode or status.stdout or blob.returncode or path.read_bytes() != blob.stdout: errors.append(f"{value} lacks exact committed bytes"); continue
        blobs[value] = "sha256:" + hashlib.sha256(blob.stdout).hexdigest()
    if errors: raise PreflightError("commit-required: " + "; ".join(errors))
    return {"source_head": pinned, "blobs": blobs}


def _assert_committed_runtime(config: CollectorConfig) -> None:
    blobs = dict(config.runtime_blob_digests)
    if set(blobs) != set(REQUIRED_COMMITTED_PATHS): raise PreflightError("commit-required: runtime seal is absent")
    for relative, expected in blobs.items():
        path = config.repo_root.joinpath(*_relative(relative).parts)
        if path.is_symlink() or not path.is_file() or "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise PreflightError("commit-required: runtime bytes changed")
    expected = config.collector_identity.rsplit("@", 1)[-1]
    if blobs.get(COLLECTOR_RELATIVE_PATH) != expected:
        raise PreflightError("commit-required: collector identity differs from pinned bytes")


def _reject_symlink_components(path: Path) -> None:
    absolute = path if path.is_absolute() else Path.cwd() / path
    current = Path(absolute.anchor)
    for part in absolute.parts[1:]:
        current /= part
        if current.is_symlink(): raise CollectorError("cohort root traverses symlink")


def _validated_output_root(repo_root: Path, cohort_id: str) -> Path:
    _run_id(cohort_id)
    root = repo_root.resolve()
    expected = root / "logs" / "capability-first" / cohort_id
    _reject_symlink_components(expected)
    return expected


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__); modes = parser.add_mutually_exclusive_group(required=True)
    for mode in ("preflight", "canary", "collect"): modes.add_argument(f"--{mode}", action="store_true")
    parser.add_argument("--source-head")
    for name in ("cohort-id", "model", "reasoning-effort"): parser.add_argument(f"--{name}")
    parser.add_argument("--timeout-seconds", type=int, default=300)
    parser.add_argument("--authorize-local-markers", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the hook, committed-byte preflight, canary, or fixed cohort."""
    arguments = list(argv) if argv is not None else sys.argv[1:]
    if arguments and arguments[0] == "hook":
        parser = argparse.ArgumentParser(add_help=False); parser.add_argument("--event-kind", required=True); parser.add_argument("--run-id", required=True); parser.add_argument("--socket-path", type=Path, required=True)
        try: args = parser.parse_args(arguments[1:])
        except SystemExit: return 2
        return hook_main(args.event_kind, args.run_id, args.socket_path)
    args = _parser().parse_args(arguments)
    try:
        preflight = _preflight_committed_paths(REPOSITORY_ROOT, args.source_head, REQUIRED_COMMITTED_PATHS)
        if args.preflight: print(json.dumps(preflight, sort_keys=True)); return 0
        required = (args.cohort_id, args.model, args.reasoning_effort)
        if any(value is None for value in required): raise CollectorError("collection arguments must be explicit")
        if args.collect and not args.authorize_local_markers: raise CollectorError("explicit local marker authorization is required")
        repo_root = REPOSITORY_ROOT.resolve()
        cohort_root = _validated_output_root(repo_root, args.cohort_id)
        contract_path = repo_root / CONTRACT_RELATIVE_PATH
        contract = _load_contract(contract_path)
        codex_binary, codex_identity = _approved_codex_runtime(contract)
        blobs = preflight.get("blobs")
        collector_digest = blobs.get(COLLECTOR_RELATIVE_PATH) if isinstance(blobs, dict) else None
        if not isinstance(collector_digest, str) or not DIGEST_RE.fullmatch(collector_digest): raise CollectorError("committed collector identity is unavailable")
        runtime_blobs = tuple(sorted((str(path), str(digest)) for path, digest in blobs.items())) if isinstance(blobs, dict) else ()
        config = CollectorConfig(
            repo_root=repo_root, source_head=str(preflight["source_head"]),
            contract_path=contract_path,
            cohort_id=args.cohort_id, cohort_root=cohort_root,
            codex_binary=codex_binary, codex_identity=codex_identity,
            collector_identity=f"capability-baseline-runtime@{collector_digest}",
            model=args.model, reasoning_effort=args.reasoning_effort,
            host_identity=_derived_host_identity(), timeout_seconds=args.timeout_seconds,
            resume=False, local_markers_authorized=args.authorize_local_markers,
            runtime_blob_digests=runtime_blobs,
        )
        if args.canary:
            canary_id = _run_id(f"canary-{args.cohort_id}")
            canary_root = repo_root / "logs" / "capability-first" / ".canaries" / args.cohort_id
            _reject_symlink_components(canary_root)
            canary = replace(config, cohort_id=canary_id, cohort_root=canary_root, resume=False, local_markers_authorized=False)
            record = run_one(canary, "none", 1); print(json.dumps({"status": record.status, "record_digest": record.record_digest})); return 0 if record.status == "completed" else 2
        result = run_cohort(config); reporter = _reporter()
        artifact = reporter._aggregate_baseline(_load_contract(config.contract_path), result.observations, kernel_mirror={"epoch": 0, "writer": "v1", "authority": "declarative_only"}, repository_root=result.evidence_root, verified_provenance=result.provenance)
        if not artifact.get("operational_complete"): raise CollectorError("reporter rejected verified cohort")
        _write(config.cohort_root / "observations.json", result.observations); _write(config.cohort_root / "baseline.json", artifact)
        print(json.dumps({"status": "complete", "run_count": 25})); return 0
    except CollectorError as exc:
        print(str(exc), file=sys.stderr); return 2


if __name__ == "__main__": raise SystemExit(main())
