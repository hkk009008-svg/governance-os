from __future__ import annotations

import contextlib
import hashlib
import importlib.util
import io
import json
import os
import shlex
import socket
import subprocess
import sys
import threading
import time
import types
from dataclasses import replace
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO_ROOT / "scripts/capability_baseline_runtime.py"
REPORTER_PATH = REPO_ROOT / "scripts/protocol_effectiveness_report.py"
MANIFEST_PATH = REPO_ROOT / "scripts/baselines/capability_first_five_profile_v1.json"
PROMPT_TEXT = "sensitive prompt"

spec = importlib.util.spec_from_file_location("capability_baseline_runtime", MODULE_PATH)
assert spec is not None and spec.loader is not None
runtime = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = runtime
spec.loader.exec_module(runtime)


def _jsonl(*events: dict[str, object]) -> str:
    return "".join(json.dumps(event) + "\n" for event in events)


def _valid_trace(*, thread_id: str = "session-1") -> str:
    return _jsonl(
        {"type": "thread.started", "thread_id": thread_id},
        {"type": "turn.started"},
        {
            "type": "item.completed",
            "item": {"type": "agent_message", "text": "using a local tool"},
        },
        {
            "type": "item.started",
            "item": {"id": "item-1", "type": "command_execution", "command": "hidden"},
        },
        {
            "type": "item.completed",
            "item": {
                "id": "item-1",
                "type": "command_execution",
                "aggregated_output": "ok",
                "exit_code": 0,
            },
        },
        {"type": "turn.completed", "usage": {}},
    )


def _hook_records(
    *,
    session_id: str = "session-1",
    turn_id: str = "turn-1",
) -> list[dict[str, object]]:
    return [
        {
            "schema_version": runtime.HOOK_RECORD_SCHEMA,
            "event_kind": "UserPromptSubmit",
            "run_id": "cohort-a-none-1",
            "session_id": session_id,
            "turn_id": turn_id,
            "agent_id": None,
            "prompt_digest": runtime._digest_text(PROMPT_TEXT),
            "received_ns": 100,
        },
        {
            "schema_version": runtime.HOOK_RECORD_SCHEMA,
            "event_kind": "PreToolUse",
            "run_id": "cohort-a-none-1",
            "session_id": session_id,
            "turn_id": turn_id,
            "agent_id": None,
            "tool_name": "Bash",
            "tool_use_id_digest": "sha256:" + "2" * 64,
            "received_ns": 140,
        },
    ]


def _hook_payload(
    kind: str,
    *,
    prompt: str = PROMPT_TEXT,
    agent_id: str | None = None,
) -> dict[str, object]:
    common: dict[str, object] = {
        "hook_event_name": kind,
        "session_id": "session-1",
        "turn_id": "turn-1",
        "cwd": "/disposable/worktree",
    }
    if agent_id is not None:
        common["agent_id"] = agent_id
    if kind == "UserPromptSubmit":
        common["prompt"] = prompt
    else:
        common.update(
            {
                "tool_name": "Bash",
                "tool_use_id": "tool-secret-id",
                "tool_input": {"cmd": "do not persist this"},
            }
        )
    return common


def _capture_one_socket_message(socket_path: Path):
    captured: list[bytes] = []
    ready = threading.Event()

    def receive() -> None:
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as listener:
            listener.bind(str(socket_path))
            os.chmod(socket_path, 0o600)
            listener.listen(1)
            ready.set()
            connection, _ = listener.accept()
            with connection:
                captured.append(connection.recv(runtime.MAX_HOOK_RECORD_BYTES + 1))

    thread = threading.Thread(target=receive, daemon=True)
    thread.start()
    assert ready.wait(2)
    return captured, thread


@pytest.mark.parametrize("kind", ["UserPromptSubmit", "PreToolUse"])
def test_hook_main_sends_only_bounded_identity_metadata(
    tmp_path: Path,
    kind: str,
) -> None:
    del tmp_path
    assert hasattr(runtime, "hook_main"), "hook observer is not implemented"
    socket_path = Path("/tmp") / f"cbr-{os.getpid()}-{kind}.sock"
    socket_path.unlink(missing_ok=True)
    captured, thread = _capture_one_socket_message(socket_path)
    payload = _hook_payload(kind)

    code = runtime.hook_main(
        kind,
        "cohort-a-none-1",
        socket_path,
        stdin=io.StringIO(json.dumps(payload)),
    )

    thread.join(2)
    assert code == 0
    assert not thread.is_alive()
    record = json.loads(captured[0])
    assert record["event_kind"] == kind
    assert record["session_id"] == "session-1"
    assert record["turn_id"] == "turn-1"
    assert "prompt" not in record
    assert "tool_input" not in record
    assert "tool_use_id" not in record
    if kind == "UserPromptSubmit":
        assert record["prompt_digest"].startswith("sha256:")
    else:
        assert record["tool_use_id_digest"].startswith("sha256:")


def test_hook_receiver_accepts_fragmented_local_socket_delivery() -> None:
    record = {
        "schema_version": runtime.HOOK_RECORD_SCHEMA,
        "event_kind": "UserPromptSubmit",
        "run_id": "cohort-a-none-1",
        "session_id": "session-1",
        "turn_id": "turn-1",
        "agent_id": None,
        "prompt_digest": runtime._digest_text(PROMPT_TEXT),
    }
    encoded = json.dumps(record).encode()

    with runtime._Receiver(lambda: 123) as receiver:
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as client:
            client.connect(str(receiver.socket_path))
            midpoint = len(encoded) // 2
            client.sendall(encoded[:midpoint])
            time.sleep(0.02)
            client.sendall(encoded[midpoint:])

    assert receiver.records == [{**record, "received_ns": 123}]


def test_installed_hook_executes_parent_collector_outside_child_worktree(tmp_path: Path) -> None:
    worktree = tmp_path / "worktree"
    worktree.mkdir()

    runtime._install_hooks(worktree, "cohort-a-none-1", Path("/tmp/parent.sock"))

    hooks = json.loads((worktree / ".codex/hooks.json").read_text())
    command = hooks["hooks"]["PreToolUse"][0]["hooks"][0]["command"]
    script = Path(shlex.split(command)[1])
    assert script == MODULE_PATH.resolve()
    assert worktree.resolve() not in script.parents


@pytest.mark.parametrize(
    ("kind", "payload"),
    [
        ("UserPromptSubmit", {}),
        ("UserPromptSubmit", {"hook_event_name": "PreToolUse"}),
        ("PreToolUse", {"hook_event_name": "PreToolUse", "session_id": "x"}),
    ],
)
def test_hook_main_fails_closed_on_invalid_or_incomplete_payload(
    tmp_path: Path,
    kind: str,
    payload: dict[str, object],
) -> None:
    assert (
        runtime.hook_main(
            kind,
            "cohort-a-none-1",
            tmp_path / "absent.sock",
            stdin=io.StringIO(json.dumps(payload)),
        )
        != 0
    )


def test_parse_runtime_trace_uses_hook_observations_as_endpoint_authority() -> None:
    parsed = runtime.parse_runtime_trace(
        _valid_trace(),
        exit_code=0,
        hook_records=_hook_records(),
        expected_run_id="cohort-a-none-1",
        expected_prompt_digest=runtime._digest_text(PROMPT_TEXT),
    )

    assert parsed.session_id == "session-1"
    assert parsed.turn_id == "turn-1"
    assert parsed.accepted_input_ns == 100
    assert parsed.first_tool_callback_ns == 140
    assert parsed.first_tool_name == "Bash"


@pytest.mark.parametrize(
    ("trace", "exit_code", "records_factory", "match"),
    [
        (_valid_trace(), 1, lambda: _hook_records(), "nonzero"),
        (_valid_trace(thread_id="other"), 0, lambda: _hook_records(), "session"),
        (_valid_trace(), 0, lambda: _hook_records()[1:], "accepted-input"),
        (_valid_trace(), 0, lambda: _hook_records()[:1], "first-tool"),
        (_valid_trace(), 0, lambda: list(reversed(_hook_records())), "precedes"),
        (_valid_trace(), 0, lambda: _hook_records() + [_hook_records()[0]], "exactly one"),
        (
            _valid_trace(),
            0,
            lambda: [_hook_records()[0], {**_hook_records()[1], "turn_id": "other"}],
            "turn",
        ),
        (
            _jsonl(
                {"type": "thread.started", "thread_id": "session-1"},
                {"type": "turn.started"},
                {"type": "item.started", "item": {"type": "command_execution"}},
            ),
            0,
            lambda: _hook_records(),
            "turn.completed",
        ),
        (_valid_trace() + _jsonl({"type": "mystery.event"}), 0, lambda: _hook_records(), "unknown"),
        (_valid_trace() + "{not-json}\n", 0, lambda: _hook_records(), "malformed"),
        (
            _valid_trace().replace(
                '{"type": "turn.completed", "usage": {}}',
                '{"type": "turn.failed", "error": "bad"}',
            ),
            0,
            lambda: _hook_records(),
            "runtime-failed-after-input-hook",
        ),
    ],
)
def test_parse_runtime_trace_rejects_untrusted_or_incomplete_evidence(
    trace: str,
    exit_code: int,
    records_factory,
    match: str,
) -> None:
    with pytest.raises(runtime.CollectorError, match=match):
        runtime.parse_runtime_trace(
            trace,
            exit_code=exit_code,
            hook_records=records_factory(),
            expected_run_id="cohort-a-none-1",
            expected_prompt_digest=runtime._digest_text(PROMPT_TEXT),
        )


def test_terminal_failure_is_classified_only_by_valid_input_hook_phase() -> None:
    failed_trace = _jsonl(
        {"type": "thread.started", "thread_id": "session-1"},
        {"type": "turn.started"},
        {"type": "turn.failed", "error": {"message": "do-not-persist-this-secret"}},
    )

    with pytest.raises(runtime.TraceFailure) as after_input:
        runtime.parse_runtime_trace(
            failed_trace,
            exit_code=0,
            hook_records=_hook_records()[:1],
            expected_run_id="cohort-a-none-1",
            expected_prompt_digest=runtime._digest_text(PROMPT_TEXT),
        )
    with pytest.raises(runtime.TraceFailure) as before_input:
        runtime.parse_runtime_trace(
            failed_trace,
            exit_code=0,
            hook_records=[],
            expected_run_id="cohort-a-none-1",
            expected_prompt_digest=runtime._digest_text(PROMPT_TEXT),
        )

    assert after_input.value.code == "runtime-failed-after-input-hook"
    assert before_input.value.code == "input-hook-unobserved"
    assert "do-not-persist-this-secret" not in str(after_input.value)
    assert "do-not-persist-this-secret" not in str(before_input.value)


def test_terminal_failure_does_not_accept_wrong_input_hook_binding() -> None:
    failed_trace = _jsonl(
        {"type": "thread.started", "thread_id": "session-1"},
        {"type": "turn.started"},
        {"type": "turn.failed", "error": {"message": "opaque"}},
    )
    wrong = [{**_hook_records()[0], "prompt_digest": "sha256:" + "0" * 64}]

    with pytest.raises(runtime.CollectorError, match="prompt digest") as failure:
        runtime.parse_runtime_trace(
            failed_trace,
            exit_code=0,
            hook_records=wrong,
            expected_run_id="cohort-a-none-1",
            expected_prompt_digest=runtime._digest_text(PROMPT_TEXT),
        )

    assert not isinstance(failure.value, getattr(runtime, "TraceFailure", ()))


def test_nested_fake_json_is_not_parsed_as_a_top_level_event() -> None:
    nested = '{"type":"mystery.event"}'
    events = [json.loads(line) for line in _valid_trace().splitlines()]
    events[-2]["item"]["aggregated_output"] = nested
    trace = _jsonl(*events)

    parsed = runtime.parse_runtime_trace(
        trace,
        exit_code=0,
        hook_records=_hook_records(),
        expected_run_id="cohort-a-none-1",
        expected_prompt_digest=runtime._digest_text(PROMPT_TEXT),
    )

    assert parsed.first_tool_callback_ns == 140


def test_trace_accepts_hook_only_tool_mapping_and_ignores_subagent_hooks() -> None:
    records = _hook_records()
    records.extend(
        [
            {
                **records[0],
                "session_id": "subagent-session",
                "turn_id": "subagent-turn",
                "agent_id": "agent-reviewer",
                "received_ns": 160,
            },
            {
                **records[1],
                "session_id": "subagent-session",
                "turn_id": "subagent-turn",
                "agent_id": "agent-reviewer",
                "received_ns": 170,
            },
        ]
    )
    lifecycle_only = _jsonl(
        {"type": "thread.started", "thread_id": "session-1"},
        {"type": "turn.started"},
        {"type": "item.completed", "item": {"type": "agent_message", "text": "done"}},
        {"type": "turn.completed", "usage": {}},
    )

    parsed = runtime.parse_runtime_trace(
        lifecycle_only,
        exit_code=0,
        hook_records=records,
        expected_run_id="cohort-a-none-1",
        expected_prompt_digest=runtime._digest_text(PROMPT_TEXT),
    )

    assert parsed.first_tool_name == "Bash"
    assert parsed.first_tool_callback_ns == 140


def test_trace_rejects_a_prompt_digest_not_bound_to_the_parent_prompt() -> None:
    with pytest.raises(runtime.CollectorError, match="prompt digest"):
        runtime.parse_runtime_trace(
            _valid_trace(),
            exit_code=0,
            hook_records=_hook_records(),
            expected_run_id="cohort-a-none-1",
            expected_prompt_digest=runtime._digest_text("different prompt"),
        )


def test_child_command_and_environment_are_fixed_and_scrubbed(tmp_path: Path) -> None:
    command = runtime._build_child_command(
        Path("/opt/codex"),
        model="gpt-test",
        reasoning_effort="low",
        worktree=tmp_path,
    )
    env = runtime._scrub_environment(
        {
            "HOME": "/home/test",
            "PATH": "/bin",
            "CODEX_HOME": "/auth-only",
            "GIT_INDEX_FILE": "/bad-index",
            "CODEX_SEAT": "director",
            "PIPELINE_PROTOCOL_MODE": "live",
            "OPENAI_API_KEY": "secret",
            "ANTHROPIC_TOKEN": "secret",
            "GITHUB_TOKEN": "secret",
            "AWS_ACCESS_KEY_ID": "secret",
            "AWS_SESSION_TOKEN": "secret",
            "SSH_AUTH_SOCK": "/private/agent.sock",
            "UNRELATED_RUNTIME_FLAG": "must-not-leak",
            "PYTHONPATH": "/inject",
            "LD_PRELOAD": "/inject.so",
            "NODE_OPTIONS": "--require inject",
        }
    )

    assert command[0] == "/opt/codex"
    assert command[1] == "exec"
    for flag in (
        "--json",
        "--ephemeral",
        "--ignore-user-config",
        "--ignore-rules",
        "--strict-config",
        "--dangerously-bypass-hook-trust",
    ):
        assert flag in command
    assert command[-1] == "-"
    assert "workspace-write" in command
    assert "read-only" not in command
    assert "--skip-git-repo-check" in command
    assert "--add-dir" not in command
    assert command[command.index("-C") + 1] == str(tmp_path / ".capability-benchmark")
    config_values = [
        command[index + 1]
        for index, value in enumerate(command[:-1])
        if value == "-c"
    ]
    assert "sandbox_workspace_write.network_access=false" in config_values
    assert "sandbox_workspace_write.exclude_slash_tmp=true" in config_values
    assert "sandbox_workspace_write.exclude_tmpdir_env_var=true" in config_values
    project_overrides = [
        command[index + 1]
        for index, value in enumerate(command[:-1])
        if value == "-c" and command[index + 1].startswith("projects=")
    ]
    assert project_overrides == [
        f'projects={{{json.dumps(str(tmp_path.resolve()))}={{trust_level="trusted"}}}}'
    ]
    disabled = {command[index + 1] for index, value in enumerate(command[:-1]) if value == "--disable"}
    assert {
        "apps", "auth_elicitation", "browser_use", "browser_use_external",
        "browser_use_full_cdp_access", "computer_use", "enable_fanout",
        "image_generation", "in_app_browser", "memories", "multi_agent",
        "plugin_sharing", "remote_plugin", "skill_mcp_dependency_install",
        "standalone_web_search", "tool_call_mcp_elicitation", "workspace_dependencies",
    } <= disabled
    assert env == {
        "HOME": "/home/test",
        "PATH": "/bin",
        "CODEX_HOME": "/auth-only",
    }


def test_prompt_names_results_relative_to_the_only_writable_directory() -> None:
    contract = runtime._load_contract(MANIFEST_PATH)

    prompt = runtime._prompt(contract, "combined", 1)

    assert "Work only in the current directory." in prompt
    assert "- result-a.txt: accepted:combined:1:a" in prompt
    assert "- result-b.txt: accepted:combined:1:b" in prompt
    assert ".capability-benchmark/result" not in prompt


def test_process_timeout_terminates_the_entire_process_group(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    created: dict[str, object] = {}
    signals: list[tuple[int, int]] = []

    class FakeProcess:
        pid = 4321
        returncode = None
        calls = 0

        def communicate(self, input=None, timeout=None):
            self.calls += 1
            if self.calls == 1:
                raise subprocess.TimeoutExpired("codex", timeout, output="partial", stderr="")
            self.returncode = -15
            return "partial", ""

    def fake_popen(command, **kwargs):
        created.update(command=command, kwargs=kwargs)
        return FakeProcess()

    monkeypatch.setattr(runtime.subprocess, "Popen", fake_popen)
    alive = {"value": True}

    def fake_killpg(pid, sig):
        signals.append((pid, sig))
        if sig == runtime.signal.SIGKILL:
            alive["value"] = False
        if sig == 0 and not alive["value"]:
            raise ProcessLookupError

    monkeypatch.setattr(runtime.os, "killpg", fake_killpg)

    capture = runtime._process(["codex"], "prompt", tmp_path, {}, 1)

    assert capture.timed_out is True
    assert capture.returncode == 124
    assert created["kwargs"]["start_new_session"] is True
    assert signals == [
        (4321, runtime.signal.SIGTERM),
        (4321, runtime.signal.SIGKILL),
        (4321, 0),
    ]


def test_normal_process_exit_also_cleans_surviving_group(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    signals: list[int] = []
    alive = {"value": True}

    class FakeProcess:
        pid = 5432
        returncode = 0

        def communicate(self, input=None, timeout=None):
            return "done", ""

    monkeypatch.setattr(runtime.subprocess, "Popen", lambda *_args, **_kwargs: FakeProcess())

    def fake_killpg(_pid, sig):
        signals.append(sig)
        if sig == runtime.signal.SIGKILL:
            alive["value"] = False
        if sig == 0 and not alive["value"]:
            raise ProcessLookupError

    monkeypatch.setattr(runtime.os, "killpg", fake_killpg)

    capture = runtime._process(["codex"], "prompt", tmp_path, {}, 1)

    assert capture.returncode == 0
    assert signals == [runtime.signal.SIGTERM, runtime.signal.SIGKILL, 0]


def test_workspace_cleanup_failure_is_not_silently_ignored(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    del tmp_path
    monkeypatch.setattr(
        runtime.shutil,
        "rmtree",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(OSError("cleanup failed")),
    )
    with pytest.raises(runtime.CollectorError, match="cleanup"):
        with runtime._workspace(_config(Path("/tmp")), "cohort-a-none-1"):
            pass


def test_workspace_is_an_isolated_git_project_for_hook_discovery() -> None:
    with runtime._workspace(_config(Path("/tmp")), "cohort-a-none-1") as workspace:
        assert (workspace / ".git").is_dir()
        git_root = Path(
            runtime._git(workspace, "rev-parse", "--show-toplevel").stdout.decode().strip()
        )
        assert git_root.resolve() == workspace.resolve()


def test_fixture_validation_rejects_ignored_or_hidden_extra_files(tmp_path: Path) -> None:
    hooks = tmp_path / ".codex/hooks.json"
    hooks.parent.mkdir()
    hooks.write_text("{}")
    fixture = tmp_path / ".capability-benchmark"
    fixture.mkdir()
    (fixture / "input-a.txt").write_text("profile=none\nordinal=1\nfixture=a\n")
    (fixture / "result-a.txt").write_text("accepted:none:1:a\n")
    (fixture / "ignored.txt").write_text("forbidden\n")

    with pytest.raises(runtime.CollectorError, match="fixture tree"):
        runtime._validate_fixture(tmp_path, "none", 1)


def _scope_digest(run_id: str) -> str:
    return runtime._digest_json({"run_id": run_id, "scope": "fixture"})


@pytest.mark.parametrize(
    ("profile", "classes", "review_count", "effect_attempted"),
    [
        ("none", set(), 0, False),
        ("verification_only", {"verification"}, 1, False),
        ("coordination_only", {"coordination"}, 0, False),
        ("effect_only", {"effect"}, 0, True),
        ("combined", {"coordination", "verification", "effect"}, 1, True),
    ],
)
def test_parent_derives_exact_profile_evidence(
    tmp_path: Path,
    profile: str,
    classes: set[str],
    review_count: int,
    effect_attempted: bool,
) -> None:
    run_id = f"cohort-a-{profile}-1"
    evidence = runtime._derive_profile_evidence(
        profile=profile,
        run_id=run_id,
        evidence_root=tmp_path,
        source_head="a" * 40,
        scope_digest=_scope_digest(run_id),
        request_digest=runtime._digest_text(run_id),
        accepted_route_ns=200 if profile == "combined" else None,
        monotonic_ns=lambda: 300,
    )

    assert {item["class"] for item in evidence.artifacts} == classes
    assert len(evidence.reviews) == review_count
    assert evidence.effect_attempted is effect_attempted
    assert evidence.route_endpoints == (
        {"accepted_route": 200, "published_go": 300}
        if profile == "combined"
        else {}
    )
    runtime._validate_profile_evidence(
        profile=profile,
        run_id=run_id,
        evidence_root=tmp_path,
        artifacts=evidence.artifacts,
        reviews=evidence.reviews,
        source_head="a" * 40,
        scope_digest=_scope_digest(run_id),
        request_digest=runtime._digest_text(run_id),
    )
    if profile in {"verification_only", "combined"}:
        review_path = tmp_path / evidence.artifacts[
            next(i for i, item in enumerate(evidence.artifacts) if item["class"] == "verification")
        ]["path"]
        review_record = json.loads(review_path.read_text())
        assert review_record["verdict"] == "GO"
        assert review_record["verifier"] == "deterministic-fixture-verifier/v1"


def test_profile_evidence_rejects_nonexistent_cross_run_and_symlink_paths(
    tmp_path: Path,
) -> None:
    run_id = "cohort-a-coordination_only-1"
    evidence = runtime._derive_profile_evidence(
        profile="coordination_only",
        run_id=run_id,
        evidence_root=tmp_path,
        source_head="a" * 40,
        scope_digest=_scope_digest(run_id),
        request_digest=runtime._digest_text(run_id),
        accepted_route_ns=None,
        monotonic_ns=lambda: 300,
    )
    original = evidence.artifacts[0]

    for bad_path in (
        "coordination/capability-baseline/missing/route.json",
        "coordination/capability-baseline/other-run/route.json",
    ):
        with pytest.raises(runtime.CollectorError):
            runtime._validate_profile_evidence(
                profile="coordination_only",
                run_id=run_id,
                evidence_root=tmp_path,
                artifacts=({**original, "path": bad_path},),
                reviews=(),
                source_head="a" * 40,
                scope_digest=_scope_digest(run_id),
                request_digest=runtime._digest_text(run_id),
            )

    target = tmp_path / original["path"]
    target.unlink()
    target.symlink_to(tmp_path / "elsewhere")
    with pytest.raises(runtime.CollectorError, match="symlink"):
        runtime._validate_profile_evidence(
            profile="coordination_only",
            run_id=run_id,
            evidence_root=tmp_path,
            artifacts=evidence.artifacts,
            reviews=(),
            source_head="a" * 40,
            scope_digest=_scope_digest(run_id),
            request_digest=runtime._digest_text(run_id),
        )


def test_profile_evidence_rejects_mismatched_review_identity(tmp_path: Path) -> None:
    run_id = "cohort-a-verification_only-1"
    evidence = runtime._derive_profile_evidence(
        profile="verification_only",
        run_id=run_id,
        evidence_root=tmp_path,
        source_head="a" * 40,
        scope_digest=_scope_digest(run_id),
        request_digest=runtime._digest_text(run_id),
        accepted_route_ns=None,
        monotonic_ns=lambda: 300,
    )
    changed = ({**evidence.reviews[0], "scope_digest": "sha256:" + "f" * 64},)

    with pytest.raises(runtime.CollectorError, match="review identity"):
        runtime._validate_profile_evidence(
            profile="verification_only",
            run_id=run_id,
            evidence_root=tmp_path,
            artifacts=evidence.artifacts,
            reviews=changed,
            source_head="a" * 40,
            scope_digest=_scope_digest(run_id),
            request_digest=runtime._digest_text(run_id),
        )


def test_marker_effect_is_reserved_before_one_attempt_and_replays_without_attempt(
    tmp_path: Path,
) -> None:
    seen_reservation: list[dict[str, object]] = []

    def marker_writer(path: Path, payload: dict[str, object]) -> None:
        reservation_path, _ = runtime._effect_paths(
            tmp_path, "cohort-a-effect_only-1"
        )
        seen_reservation.append(json.loads(reservation_path.read_text()))
        runtime._write_marker_exclusive(path, payload)

    first = runtime._execute_marker_effect(
        evidence_root=tmp_path,
        run_id="cohort-a-effect_only-1",
        request_digest=runtime._digest_text("request"),
        profile="effect_only",
        marker_writer=marker_writer,
    )
    second = runtime._execute_marker_effect(
        evidence_root=tmp_path,
        run_id="cohort-a-effect_only-1",
        request_digest=runtime._digest_text("request"),
        profile="effect_only",
        marker_writer=lambda *_: pytest.fail("completed replay attempted the effect"),
    )

    assert seen_reservation[0]["state"] == "attempting"
    assert first.attempted is True
    assert second.attempted is False
    assert second.reconciled is False


def test_marker_effect_reconciles_post_attempt_crash_without_retry(tmp_path: Path) -> None:
    run_id = "cohort-a-combined-1"
    request_digest = runtime._digest_text("request")
    reservation_path, marker_path = runtime._effect_paths(tmp_path, run_id)
    nonce = runtime._effect_nonce(run_id, request_digest)
    reservation_path.parent.mkdir(parents=True)
    reservation_path.write_text(
        json.dumps(
            {
                "schema_version": runtime.EFFECT_RESERVATION_SCHEMA,
                "state": "attempting",
                "run_id": run_id,
                "request_digest": request_digest,
                "nonce": nonce,
            }
        )
    )
    marker_path.parent.mkdir(parents=True)
    marker_path.write_text(json.dumps(runtime._effect_marker(run_id, request_digest, nonce)))

    result = runtime._execute_marker_effect(
        evidence_root=tmp_path,
        run_id=run_id,
        request_digest=request_digest,
        profile="combined",
        marker_writer=lambda *_: pytest.fail("reconciliation retried the effect"),
    )

    assert result.attempted is False
    assert result.reconciled is True
    assert json.loads(reservation_path.read_text())["state"] == "completed"


@pytest.mark.parametrize("profile", ["none", "verification_only", "coordination_only"])
def test_marker_effect_rejects_unauthorized_profiles(tmp_path: Path, profile: str) -> None:
    with pytest.raises(runtime.CollectorError, match="not authorized"):
        runtime._execute_marker_effect(
            evidence_root=tmp_path,
            run_id=f"cohort-a-{profile}-1",
            request_digest=runtime._digest_text("request"),
            profile=profile,
        )


def test_marker_effect_rejects_traversal_symlink_mismatch_and_uncertainty(
    tmp_path: Path,
) -> None:
    with pytest.raises(runtime.CollectorError):
        runtime._effect_paths(tmp_path, "../escape")

    symlink_root = tmp_path / "symlink-case"
    (symlink_root / ".capability-state").mkdir(parents=True)
    (symlink_root / ".codex").symlink_to(tmp_path / "outside", target_is_directory=True)
    with pytest.raises(runtime.CollectorError, match="symlink"):
        runtime._execute_marker_effect(
            evidence_root=symlink_root,
            run_id="cohort-a-effect_only-2",
            request_digest=runtime._digest_text("request"),
            profile="effect_only",
        )

    uncertain_root = tmp_path / "uncertain"
    reservation_path, _ = runtime._effect_paths(
        uncertain_root, "cohort-a-effect_only-3"
    )
    reservation_path.parent.mkdir(parents=True)
    reservation_path.write_text(
        json.dumps(
            {
                "schema_version": runtime.EFFECT_RESERVATION_SCHEMA,
                "state": "attempting",
                "run_id": "cohort-a-effect_only-3",
                "request_digest": runtime._digest_text("request"),
                "nonce": runtime._effect_nonce(
                    "cohort-a-effect_only-3", runtime._digest_text("request")
                ),
            }
        )
    )
    with pytest.raises(runtime.EffectUncertain):
        runtime._execute_marker_effect(
            evidence_root=uncertain_root,
            run_id="cohort-a-effect_only-3",
            request_digest=runtime._digest_text("request"),
            profile="effect_only",
        )


def _config(tmp_path: Path, **changes: object):
    values: dict[str, object] = {
        "repo_root": REPO_ROOT,
        "source_head": "a" * 40,
        "contract_path": MANIFEST_PATH,
        "cohort_id": "cohort-a",
        "cohort_root": tmp_path / "cohort",
        "codex_binary": Path("/opt/codex"),
        "codex_identity": "codex-cli/0.144.4@sha256:" + "b" * 64,
        "collector_identity": "capability-baseline-runtime@sha256:" + "c" * 64,
        "model": "gpt-test",
        "reasoning_effort": "low",
        "host_identity": "opaque-host-a",
        "timeout_seconds": 5,
        "local_markers_authorized": True,
    }
    values.update(changes)
    return runtime.CollectorConfig(**values)


def test_pinned_runtime_accepts_max_reasoning_effort(tmp_path: Path) -> None:
    config = _config(tmp_path, reasoning_effort="max")

    command = runtime._build_child_command(
        config.codex_binary,
        model=config.model,
        reasoning_effort=config.reasoning_effort,
        worktree=tmp_path,
    )

    assert 'model_reasoning_effort="max"' in command


def _fake_workspace_factory(root: Path):
    @contextlib.contextmanager
    def factory(_config, run_id: str):
        workspace = root / run_id
        workspace.mkdir(parents=True, exist_ok=False)
        runtime._git(workspace, "init", "-q")
        yield workspace

    return factory


def _fake_runner(order: list[str], *, returncode: int = 0, timed_out: bool = False):
    def runner(command, prompt: str, cwd: Path, env, timeout: int):
        del env, timeout
        hooks = json.loads((cwd / ".codex/hooks.json").read_text())
        prompt_command = hooks["hooks"]["UserPromptSubmit"][0]["hooks"][0]["command"]
        args = shlex.split(prompt_command)
        run_id = args[args.index("--run-id") + 1]
        socket_path = Path(args[args.index("--socket-path") + 1])
        order.append(run_id)
        assert prompt not in command
        assert runtime.hook_main(
            "UserPromptSubmit",
            run_id,
            socket_path,
            stdin=io.StringIO(json.dumps(_hook_payload("UserPromptSubmit", prompt=prompt))),
        ) == 0
        assert runtime.hook_main(
            "PreToolUse",
            run_id,
            socket_path,
            stdin=io.StringIO(json.dumps(_hook_payload("PreToolUse"))),
        ) == 0
        profile, ordinal = runtime._profile_ordinal_from_run_id(run_id)
        for relative, content in runtime._expected_fixture_contents(profile, ordinal).items():
            path = cwd / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content)
        return runtime.ProcessCapture(
            returncode=returncode,
            stdout=_valid_trace(),
            stderr="",
            timed_out=timed_out,
        )

    return runner


def test_run_one_validates_fixture_and_exact_resume_then_rejects_changed_replay(
    tmp_path: Path,
) -> None:
    config = _config(tmp_path)
    order: list[str] = []
    workspace_factory = _fake_workspace_factory(tmp_path / "workspaces")
    record = runtime.run_one(
        config,
        "none",
        1,
        process_runner=_fake_runner(order),
        workspace_factory=workspace_factory,
    )
    replay = runtime.run_one(
        replace(config, resume=True),
        "none",
        1,
        process_runner=lambda *_: pytest.fail("completed run was spawned again"),
        workspace_factory=workspace_factory,
    )

    assert record.status == "completed"
    assert replay == record
    assert record.observation["accepted_result_digest"].startswith("sha256:")
    assert record.runtime_evidence_digest.startswith("sha256:")
    assert record.profile_evidence_digest.startswith("sha256:")
    assert len(order) == 1

    with pytest.raises(runtime.ReplayConflict, match="resume"):
        runtime.run_one(
            config,
            "none",
            1,
            process_runner=lambda *_: pytest.fail("fresh collection reused state"),
            workspace_factory=workspace_factory,
        )

    with pytest.raises(runtime.ReplayConflict):
        runtime.run_one(
            replace(config, model="changed-model"),
            "none",
            1,
            process_runner=lambda *_: pytest.fail("changed replay was spawned"),
            workspace_factory=workspace_factory,
        )


def test_run_one_seals_timeout_as_uncertain_and_never_retries(tmp_path: Path) -> None:
    config = _config(tmp_path)
    workspace_factory = _fake_workspace_factory(tmp_path / "workspaces")
    first = runtime.run_one(
        config,
        "none",
        1,
        process_runner=_fake_runner([], timed_out=True),
        workspace_factory=workspace_factory,
    )
    replay = runtime.run_one(
        replace(config, resume=True),
        "none",
        1,
        process_runner=lambda *_: pytest.fail("uncertain run was retried"),
        workspace_factory=workspace_factory,
    )

    assert first.status == "uncertain"
    assert replay == first


def test_run_one_records_a_safe_collector_failure_reason(tmp_path: Path) -> None:
    record = runtime.run_one(
        _config(tmp_path),
        "none",
        1,
        process_runner=_fake_runner([], returncode=1),
        workspace_factory=_fake_workspace_factory(tmp_path / "workspaces"),
    )

    assert record.status == "failed"
    assert record.error == "run-evidence-invalid:codex-process-exited-nonzero"


def test_run_one_persists_only_closed_runtime_failure_code(tmp_path: Path) -> None:
    secrets = ("turn-secret-7f82", "item-secret-91ab", "stderr-secret-44cd")

    def failing_runner(command, prompt: str, cwd: Path, env, timeout: int):
        del command, env, timeout
        hooks = json.loads((cwd / ".codex/hooks.json").read_text())
        prompt_command = hooks["hooks"]["UserPromptSubmit"][0]["hooks"][0]["command"]
        args = shlex.split(prompt_command)
        run_id = args[args.index("--run-id") + 1]
        socket_path = Path(args[args.index("--socket-path") + 1])
        assert runtime.hook_main(
            "UserPromptSubmit",
            run_id,
            socket_path,
            stdin=io.StringIO(json.dumps(_hook_payload("UserPromptSubmit", prompt=prompt))),
        ) == 0
        return runtime.ProcessCapture(
            returncode=0,
            stdout=_jsonl(
                {"type": "thread.started", "thread_id": "session-1"},
                {"type": "turn.started"},
                {"type": "item.completed", "item": {"type": "agent_message", "text": secrets[1]}},
                {"type": "turn.failed", "error": {"message": secrets[0]}},
            ),
            stderr=secrets[2],
            timed_out=False,
        )

    config = _config(tmp_path)
    record = runtime.run_one(
        config,
        "none",
        1,
        process_runner=failing_runner,
        workspace_factory=_fake_workspace_factory(tmp_path / "workspaces"),
    )
    persisted = (
        config.cohort_root
        / "records"
        / f"{config.cohort_id}-none-1"
        / "record.json"
    ).read_text()

    assert record.status == "failed"
    assert record.error == "run-evidence-invalid:runtime-failed-after-input-hook"
    assert all(secret not in persisted for secret in secrets)


def test_resume_revalidates_parent_profile_evidence_before_reuse(tmp_path: Path) -> None:
    config = _config(tmp_path)
    workspace_factory = _fake_workspace_factory(tmp_path / "workspaces")
    record = runtime.run_one(
        config,
        "verification_only",
        1,
        process_runner=_fake_runner([]),
        workspace_factory=workspace_factory,
    )
    review = next(
        item for item in record.observation["artifacts"] if item["class"] == "verification"
    )
    review_path = config.cohort_root / "evidence" / review["path"]
    review_path.write_text(json.dumps({"verdict": "forged"}))

    with pytest.raises(runtime.CollectorError, match="evidence"):
        runtime.run_one(
            replace(config, resume=True),
            "verification_only",
            1,
            process_runner=lambda *_: pytest.fail("invalid replay spawned"),
            workspace_factory=workspace_factory,
        )


def test_run_cohort_is_interleaved_and_issues_verified_provenance(tmp_path: Path) -> None:
    config = _config(tmp_path)
    order: list[str] = []
    result = runtime.run_cohort(
        config,
        process_runner=_fake_runner(order),
        workspace_factory=_fake_workspace_factory(tmp_path / "workspaces"),
    )

    expected = [
        f"cohort-a-{profile}-{ordinal}"
        for ordinal in range(1, 6)
        for profile in runtime.PROFILES
    ]
    assert order == expected
    assert [run["run_id"] for run in result.observations["runs"]] == expected
    assert len(result.records) == 25
    assert result.provenance is not None
    assert len(result.provenance.run_record_digests) == 25
    marker_paths = list((config.cohort_root / "evidence").glob(".codex/runtime/**/marker.json"))
    assert len(marker_paths) == 10
    reporter = runtime._reporter()
    assert reporter.VerifiedBaselineProvenance is runtime._reporter().VerifiedBaselineProvenance
    artifact = reporter._aggregate_baseline(
        json.loads(MANIFEST_PATH.read_text()),
        result.observations,
        kernel_mirror={"epoch": 0, "writer": "v1", "authority": "declarative_only"},
        repository_root=result.evidence_root,
        verified_provenance=result.provenance,
    )
    assert artifact["operational_complete"] is True, artifact


def test_run_cohort_revalidates_earlier_records_before_provenance(tmp_path: Path) -> None:
    config = _config(tmp_path)
    order: list[str] = []
    base_runner = _fake_runner(order)

    def tampering_runner(*args, **kwargs):
        if order:
            path = config.cohort_root / "records/cohort-a-none-1/record.json"
            value = json.loads(path.read_text())
            value["observation"]["accepted_result_digest"] = "sha256:" + "f" * 64
            forged = runtime._record(
                value["run_id"], value["request_digest"], value["status"],
                value["observation"], value["error"], value["effect_attempted"],
                value["runtime_evidence_digest"], value["profile_evidence_digest"],
            )
            path.write_text(json.dumps(forged.as_json()))
        return base_runner(*args, **kwargs)

    with pytest.raises(runtime.CollectorError, match="deterministic fixture"):
        runtime.run_cohort(
            config,
            process_runner=tampering_runner,
            workspace_factory=_fake_workspace_factory(tmp_path / "workspaces"),
        )


def test_fresh_cohort_rejects_any_preexisting_root_before_first_spawn(tmp_path: Path) -> None:
    config = _config(tmp_path)
    config.cohort_root.mkdir(parents=True)
    (config.cohort_root / "preseeded.json").write_text("{}")

    with pytest.raises(runtime.ReplayConflict, match="fresh cohort"):
        runtime.run_cohort(
            config,
            process_runner=lambda *_: pytest.fail("preseeded cohort spawned Codex"),
            workspace_factory=_fake_workspace_factory(tmp_path / "workspaces"),
        )


def test_resumed_cohort_cannot_issue_operational_provenance(tmp_path: Path) -> None:
    config = replace(_config(tmp_path), resume=True)

    with pytest.raises(runtime.CollectorError, match="resumed cohort.*operational"):
        runtime.run_cohort(
            config,
            process_runner=lambda *_: pytest.fail("resume spawned Codex"),
            workspace_factory=_fake_workspace_factory(tmp_path / "workspaces"),
        )


def _git(repo: Path, *args: str) -> str:
    env = os.environ.copy()
    env.pop("GIT_INDEX_FILE", None)
    completed = subprocess.run(
        ["git", *args],
        cwd=repo,
        env=env,
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def _sealed_reporter_fixture(
    tmp_path: Path,
    reporter_source: str,
    *,
    helper_source: str | None = None,
    extra_sources: dict[str, str] | None = None,
) -> tuple[Path, runtime.CollectorConfig]:
    repo = tmp_path / "sealed-reporter-repo"
    repo.mkdir()
    _git(repo, "init", "-q")
    _git(repo, "config", "user.email", "test@example.invalid")
    _git(repo, "config", "user.name", "Test")
    sources = {
        runtime.COLLECTOR_RELATIVE_PATH: "# sealed collector\n",
        runtime.REPORTER_RELATIVE_PATH: reporter_source,
        runtime.CONTRACT_RELATIVE_PATH: "{}\n",
    }
    if helper_source is not None:
        sources["scripts/reporter_helper.py"] = helper_source
    if extra_sources is not None:
        sources.update(extra_sources)
    for relative, source in sources.items():
        path = repo / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(source, encoding="utf-8")
    _git(repo, "add", ".")
    _git(repo, "commit", "-qm", "sealed reporter fixture")
    head = _git(repo, "rev-parse", "HEAD")
    digests = tuple(
        sorted(
            (
                relative,
                "sha256:" + hashlib.sha256((repo / relative).read_bytes()).hexdigest(),
            )
            for relative in runtime.REQUIRED_COMMITTED_PATHS
        )
    )
    config = _config(
        tmp_path / "config",
        repo_root=repo,
        source_head=head,
        contract_path=repo / runtime.CONTRACT_RELATIVE_PATH,
        collector_identity=(
            "capability-baseline-runtime@"
            + dict(digests)[runtime.COLLECTOR_RELATIVE_PATH]
        ),
        runtime_blob_digests=digests,
    )
    cache = getattr(runtime, "_REPORTER_MODULES", None)
    if isinstance(cache, dict):
        for module in cache.values():
            name = getattr(module, "__name__", None)
            if isinstance(name, str) and sys.modules.get(name) is module:
                sys.modules.pop(name, None)
        cache.clear()
    return repo, config


_MINIMAL_REPORTER = """
from dataclasses import dataclass

@dataclass(frozen=True)
class VerifiedBaselineProvenance:
    source_head: str

def _aggregate_baseline(*, verified_provenance):
    return {"same_type": type(verified_provenance) is VerifiedBaselineProvenance}
"""


def test_repository_path_requires_absolute_origin(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    repo = tmp_path / "repo"
    origin = repo / "scripts/reporter_helper.py"
    origin.parent.mkdir(parents=True)
    origin.write_text("VALUE = 'repo-local'\n", encoding="utf-8")
    monkeypatch.chdir(repo)

    for sentinel in ("built-in", "frozen", "relative.py"):
        assert not runtime._path_within_repository(sentinel, repo)
    assert runtime._path_within_repository(origin, repo)


def test_repository_import_matching_uses_only_first_component(tmp_path: Path) -> None:
    repo, config = _sealed_reporter_fixture(
        tmp_path,
        _MINIMAL_REPORTER,
        helper_source="VALUE = 'script helper'\n",
        extra_sources={
            "packages/deep/nested_helper.py": "VALUE = 'nested helper'\n",
            "packages/utils.py": "VALUE = 'local basename'\n",
        },
    )
    roots = runtime._repository_import_roots(repo, config.source_head)

    assert not runtime._local_import_name("email.utils", roots)
    for name in (
        "nested_helper",
        "deep.nested_helper",
        "scripts.reporter_helper",
    ):
        assert runtime._local_import_name(name, roots)


def test_sealed_reporter_rejects_exact_blob_digest_mismatch(tmp_path: Path) -> None:
    _, config = _sealed_reporter_fixture(tmp_path, _MINIMAL_REPORTER)
    mismatched = tuple(
        (
            relative,
            "sha256:" + "f" * 64
            if relative == runtime.REPORTER_RELATIVE_PATH
            else digest,
        )
        for relative, digest in config.runtime_blob_digests
    )

    with pytest.raises(runtime.PreflightError, match="sealed reporter blob"):
        runtime._reporter(replace(config, runtime_blob_digests=mismatched))


def test_sealed_reporter_rejects_repository_import_during_module_load(
    tmp_path: Path,
) -> None:
    source = "import reporter_helper\n" + _MINIMAL_REPORTER
    _, config = _sealed_reporter_fixture(
        tmp_path,
        source,
        helper_source="VALUE = 'ambient must not load'\n",
    )

    with pytest.raises(runtime.PreflightError, match="repository-local import"):
        runtime._reporter(config)


def test_sealed_reporter_rejects_importlib_repository_import_during_module_load(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source = (
        "import importlib\n"
        "importlib.import_module('scripts.reporter_helper')\n"
        + _MINIMAL_REPORTER
    )
    repo, config = _sealed_reporter_fixture(
        tmp_path,
        source,
        helper_source="VALUE = 'ambient must not load'\n",
    )
    monkeypatch.syspath_prepend(str(repo))

    with pytest.raises(runtime.PreflightError, match="repository-local import"):
        runtime._reporter(config)


def test_sealed_reporter_rejects_nested_local_basename_via_importlib(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source = (
        "import importlib\n"
        "importlib.import_module('nested_helper')\n"
        + _MINIMAL_REPORTER
    )
    _, config = _sealed_reporter_fixture(
        tmp_path,
        source,
        extra_sources={"packages/deep/nested_helper.py": "VALUE = 'committed'\n"},
    )
    poisoned = types.ModuleType("nested_helper")
    poisoned.VALUE = "prepoisoned"
    monkeypatch.setitem(sys.modules, "nested_helper", poisoned)

    with pytest.raises(runtime.PreflightError, match="repository-local import"):
        runtime._reporter(config)


def test_sealed_reporter_rejects_importlib_repository_import_during_aggregation(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source = _MINIMAL_REPORTER.replace(
        'return {"same_type": type(verified_provenance) is VerifiedBaselineProvenance}',
        "import importlib\n"
        "    helper = importlib.import_module('reporter_helper')\n"
        "    return {'loaded': helper.VALUE}",
    )
    _, config = _sealed_reporter_fixture(
        tmp_path,
        source,
        helper_source="VALUE = 'committed'\n",
    )
    poisoned = types.ModuleType("reporter_helper")
    poisoned.VALUE = "prepoisoned"
    monkeypatch.setitem(sys.modules, "reporter_helper", poisoned)

    reporter = runtime._reporter(config)
    provenance = reporter.VerifiedBaselineProvenance(config.source_head)
    with pytest.raises(runtime.PreflightError, match="repository-local import"):
        reporter._aggregate_baseline(verified_provenance=provenance)


def test_sealed_reporter_quarantines_repo_origin_under_allowed_sys_modules_name(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source = _MINIMAL_REPORTER.replace(
        'return {"same_type": type(verified_provenance) is VerifiedBaselineProvenance}',
        "import sys\n"
        "    return {'loaded': sys.modules['allowed_alias'].VALUE}",
    )
    repo, config = _sealed_reporter_fixture(
        tmp_path,
        source,
        helper_source="VALUE = 'committed'\n",
    )
    poisoned = types.ModuleType("allowed_alias")
    poisoned.__file__ = str(repo / "scripts/reporter_helper.py")
    poisoned.VALUE = "prepoisoned"
    monkeypatch.setitem(sys.modules, "allowed_alias", poisoned)

    reporter = runtime._reporter(config)
    provenance = reporter.VerifiedBaselineProvenance(config.source_head)
    with pytest.raises(KeyError, match="allowed_alias"):
        reporter._aggregate_baseline(verified_provenance=provenance)

    key = (config.source_head, dict(config.runtime_blob_digests)[runtime.REPORTER_RELATIVE_PATH])
    assert key not in runtime._REPORTER_MODULES
    assert reporter.__name__ not in sys.modules
    assert sys.modules["allowed_alias"] is poisoned


def test_sealed_reporter_rejects_prepoisoned_repository_import_during_aggregation(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source = _MINIMAL_REPORTER.replace(
        'return {"same_type": type(verified_provenance) is VerifiedBaselineProvenance}',
        "import reporter_helper\n    return {'loaded': reporter_helper.VALUE}",
    )
    repo, config = _sealed_reporter_fixture(
        tmp_path,
        source,
        helper_source="VALUE = 'committed'\n",
    )
    (repo / "scripts/reporter_helper.py").unlink()
    poisoned = types.ModuleType("reporter_helper")
    poisoned.VALUE = "prepoisoned"
    monkeypatch.setitem(sys.modules, "reporter_helper", poisoned)

    reporter = runtime._reporter(config)
    provenance = reporter.VerifiedBaselineProvenance(config.source_head)
    with pytest.raises(runtime.PreflightError, match="repository-local import"):
        reporter._aggregate_baseline(verified_provenance=provenance)


def test_sealed_reporter_cache_is_keyed_by_source_head_and_digest(tmp_path: Path) -> None:
    repo, first_config = _sealed_reporter_fixture(
        tmp_path,
        "TOKEN = 'first'\n" + _MINIMAL_REPORTER,
    )
    first = runtime._reporter(first_config)

    reporter_path = repo / runtime.REPORTER_RELATIVE_PATH
    reporter_path.write_text("TOKEN = 'second'\n" + _MINIMAL_REPORTER, encoding="utf-8")
    _git(repo, "add", runtime.REPORTER_RELATIVE_PATH)
    _git(repo, "commit", "-qm", "second reporter")
    second_head = _git(repo, "rev-parse", "HEAD")
    second_digests = tuple(
        (
            relative,
            "sha256:" + hashlib.sha256((repo / relative).read_bytes()).hexdigest(),
        )
        for relative, _ in first_config.runtime_blob_digests
    )
    second_config = replace(
        first_config,
        source_head=second_head,
        runtime_blob_digests=second_digests,
    )

    second = runtime._reporter(second_config)

    assert first is runtime._reporter(first_config)
    assert second is runtime._reporter(second_config)
    assert first is not second
    assert first.TOKEN == "first"
    assert second.TOKEN == "second"


def test_sealed_reporter_cache_hit_performs_zero_git_work(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _, config = _sealed_reporter_fixture(tmp_path, _MINIMAL_REPORTER)
    calls: list[tuple[tuple[object, ...], dict[str, object]]] = []
    original_git = runtime._git

    def counting_git(*args: object, **kwargs: object):
        calls.append((args, kwargs))
        return original_git(*args, **kwargs)

    monkeypatch.setattr(runtime, "_git", counting_git)
    reporter = runtime._reporter(config)
    first_load_calls = list(calls)

    assert runtime._reporter(config) is reporter
    assert calls == first_load_calls
    assert len(first_load_calls) == 2


def test_sealed_reporter_concurrent_callers_share_one_serialized_load(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _, config = _sealed_reporter_fixture(tmp_path, _MINIMAL_REPORTER)
    calls: list[str] = []
    calls_lock = threading.Lock()
    first_show_started = threading.Event()
    second_show_seen = threading.Event()
    original_git = runtime._git

    def coordinated_git(*args: object, **kwargs: object):
        command = str(args[1])
        with calls_lock:
            calls.append(command)
            show_number = calls.count("show")
        if command == "show" and show_number == 1:
            first_show_started.set()
            second_show_seen.wait(0.5)
        elif command == "show":
            second_show_seen.set()
        return original_git(*args, **kwargs)

    monkeypatch.setattr(runtime, "_git", coordinated_git)
    modules: list[object] = []
    errors: list[BaseException] = []

    def load() -> None:
        try:
            modules.append(runtime._reporter(config))
        except BaseException as exc:
            errors.append(exc)

    first = threading.Thread(target=load)
    second = threading.Thread(target=load)
    first.start()
    assert first_show_started.wait(2)
    second.start()
    first.join(3)
    second.join(3)

    assert not first.is_alive() and not second.is_alive()
    assert errors == []
    assert len(modules) == 2
    assert modules[0] is modules[1]
    assert calls.count("show") == 1
    assert calls.count("ls-tree") == 1


def test_sealed_reporter_system_exit_cleans_module_state(tmp_path: Path) -> None:
    _, config = _sealed_reporter_fixture(tmp_path, "raise SystemExit(7)\n")
    expected = dict(config.runtime_blob_digests)[runtime.REPORTER_RELATIVE_PATH]
    key = (config.source_head, expected)
    module_name = (
        f"_capability_reporter_{config.source_head}_{expected.removeprefix('sha256:')}"
    )

    with pytest.raises(SystemExit) as raised:
        runtime._reporter(config)

    assert raised.value.code == 7
    assert key not in runtime._REPORTER_MODULES
    assert module_name not in sys.modules


def test_sealed_reporter_rejects_deterministic_module_name_collision(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _, config = _sealed_reporter_fixture(tmp_path, _MINIMAL_REPORTER)
    expected = dict(config.runtime_blob_digests)[runtime.REPORTER_RELATIVE_PATH]
    module_name = (
        f"_capability_reporter_{config.source_head}_{expected.removeprefix('sha256:')}"
    )
    collision = types.ModuleType(module_name)
    monkeypatch.setitem(sys.modules, module_name, collision)

    with pytest.raises(runtime.PreflightError, match="module name collision"):
        runtime._reporter(config)

    assert sys.modules[module_name] is collision


def test_sealed_reporter_aggregation_failure_evicts_and_reloads(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source = _MINIMAL_REPORTER.replace(
        "from dataclasses import dataclass",
        "from dataclasses import dataclass\nimport os",
    ).replace(
        'return {"same_type": type(verified_provenance) is VerifiedBaselineProvenance}',
        "if os.environ.pop('CAPABILITY_REPORTER_FAIL_ONCE', None):\n"
        "        raise RuntimeError('transient aggregation failure')\n"
        "    return {'same_type': type(verified_provenance) is VerifiedBaselineProvenance}",
    )
    _, config = _sealed_reporter_fixture(tmp_path, source)
    monkeypatch.setenv("CAPABILITY_REPORTER_FAIL_ONCE", "1")
    key = (config.source_head, dict(config.runtime_blob_digests)[runtime.REPORTER_RELATIVE_PATH])

    first = runtime._reporter(config)
    first_provenance = first.VerifiedBaselineProvenance(config.source_head)
    with pytest.raises(RuntimeError, match="transient aggregation failure"):
        first._aggregate_baseline(verified_provenance=first_provenance)

    assert key not in runtime._REPORTER_MODULES
    assert first.__name__ not in sys.modules
    second = runtime._reporter(config)
    second_provenance = second.VerifiedBaselineProvenance(config.source_head)
    assert second is not first
    assert second._aggregate_baseline(verified_provenance=second_provenance) == {
        "same_type": True
    }


def test_sealed_reporter_creates_and_consumes_one_provenance_type(tmp_path: Path) -> None:
    _, config = _sealed_reporter_fixture(tmp_path, _MINIMAL_REPORTER)

    reporter = runtime._reporter(config)
    provenance = reporter.VerifiedBaselineProvenance(config.source_head)
    artifact = reporter._aggregate_baseline(verified_provenance=provenance)

    assert artifact == {"same_type": True}


def test_production_reporter_has_no_repository_import_on_sealed_load(
    tmp_path: Path,
) -> None:
    _, config = _sealed_reporter_fixture(tmp_path, REPORTER_PATH.read_text(encoding="utf-8"))

    reporter = runtime._reporter(config)

    assert reporter.VerifiedBaselineProvenance.__module__.startswith("_capability_reporter_")


def test_committed_instrument_preflight_accepts_exact_blob_then_refuses_dirty_bytes(
    tmp_path: Path,
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q")
    _git(repo, "config", "user.email", "test@example.invalid")
    _git(repo, "config", "user.name", "Test")
    path = repo / "instrument.py"
    path.write_text("print('v1')\n")
    _git(repo, "add", "instrument.py")
    _git(repo, "commit", "-qm", "instrument")
    head = _git(repo, "rev-parse", "HEAD")

    evidence = runtime._preflight_committed_paths(repo, head, ("instrument.py",))
    assert evidence["source_head"] == head
    assert evidence["blobs"]["instrument.py"].startswith("sha256:")

    path.write_text("print('dirty')\n")
    with pytest.raises(runtime.PreflightError, match="commit-required"):
        runtime._preflight_committed_paths(repo, head, ("instrument.py",))


def test_internal_git_clears_control_environment_and_disables_hooks(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, object] = {}

    def fake_run(command, *, cwd, env, check, capture_output):
        captured.update(command=command, cwd=cwd, env=env, check=check, capture_output=capture_output)
        return subprocess.CompletedProcess(command, 0, b"", b"")

    for key in ("GIT_DIR", "GIT_WORK_TREE", "GIT_OBJECT_DIRECTORY", "GIT_INDEX_FILE", "GIT_CONFIG_GLOBAL"):
        monkeypatch.setenv(key, "/attacker-controlled")
    monkeypatch.setattr(runtime.subprocess, "run", fake_run)

    runtime._git(tmp_path, "status")

    command = captured["command"]
    environment = captured["env"]
    assert command[:5] == ["/usr/bin/git", "-c", "core.hooksPath=/dev/null", "-c", "core.fsmonitor=false"]
    assert not ({"GIT_DIR", "GIT_WORK_TREE", "GIT_OBJECT_DIRECTORY", "GIT_INDEX_FILE"} & set(environment))
    assert environment["GIT_CONFIG_NOSYSTEM"] == "1"
    assert environment["GIT_CONFIG_GLOBAL"] == "/dev/null"
    assert environment["PATH"] == "/usr/bin:/bin:/usr/sbin:/sbin"


def test_runtime_seal_rechecks_only_pinned_instrument_bytes(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    paths = ("instrument.py", "reporter.py", "contract.json")
    for index, relative in enumerate(paths):
        (repo / relative).write_text(f"v{index}\n")
    digests = tuple(
        (relative, "sha256:" + hashlib.sha256((repo / relative).read_bytes()).hexdigest())
        for relative in paths
    )
    monkeypatch.setattr(runtime, "REQUIRED_COMMITTED_PATHS", paths)
    monkeypatch.setattr(runtime, "COLLECTOR_RELATIVE_PATH", "instrument.py")
    config = _config(
        tmp_path,
        repo_root=repo,
        collector_identity=f"collector@{dict(digests)['instrument.py']}",
        runtime_blob_digests=digests,
    )

    runtime._assert_committed_runtime(config)

    (repo / "reporter.py").write_text("changed\n")
    with pytest.raises(runtime.PreflightError, match="runtime bytes changed"):
        runtime._assert_committed_runtime(config)


def test_preflight_cli_performs_no_collection_and_reports_commit_requirement(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q")
    _git(repo, "config", "user.email", "test@example.invalid")
    _git(repo, "config", "user.name", "Test")
    (repo / "instrument.py").write_text("dirty\n")
    monkeypatch.setattr(runtime, "REQUIRED_COMMITTED_PATHS", ("instrument.py",))
    monkeypatch.setattr(runtime, "REPOSITORY_ROOT", repo, raising=False)

    code = runtime.main(["--preflight"])

    assert code == 2
    assert "commit-required" in capsys.readouterr().err


def test_codex_identity_is_derived_from_executable_bytes_and_detects_drift(tmp_path: Path) -> None:
    binary = tmp_path / "codex"
    binary.write_text("#!/bin/sh\nprintf 'codex-cli 9.9.9\\n'\n")
    binary.chmod(0o700)

    resolved, identity = runtime._codex_binary_identity(binary)

    assert resolved == binary.resolve()
    assert identity == "codex-cli/9.9.9@sha256:" + hashlib.sha256(binary.read_bytes()).hexdigest()
    runtime._assert_codex_binary_identity(_config(tmp_path, codex_binary=resolved, codex_identity=identity))

    binary.write_text("#!/bin/sh\nprintf 'codex-cli 10.0.0\\n'\n")
    binary.chmod(0o700)
    with pytest.raises(runtime.CollectorError, match="changed"):
        runtime._assert_codex_binary_identity(_config(tmp_path, codex_binary=resolved, codex_identity=identity))


def test_operational_codex_runtime_requires_contract_pinned_path_and_digest(tmp_path: Path) -> None:
    relative = Path(".codex/packages/standalone/current/bin/codex")
    binary = tmp_path / relative
    binary.parent.mkdir(parents=True)
    binary.write_text("#!/bin/sh\nprintf 'codex-cli 9.9.9\\n'\n")
    binary.chmod(0o700)
    identity = "codex-cli/9.9.9@sha256:" + hashlib.sha256(binary.read_bytes()).hexdigest()
    contract = {"codex_runtime": {"home_relative_path": relative.as_posix(), "identity": identity}}

    assert runtime._approved_codex_runtime(contract, home=tmp_path) == (binary.resolve(), identity)

    contract["codex_runtime"]["identity"] = "codex-cli/9.9.9@sha256:" + "f" * 64
    with pytest.raises(runtime.CollectorError, match="approved Codex"):
        runtime._approved_codex_runtime(contract, home=tmp_path)


def test_host_identity_is_runtime_derived_opaque_and_stable() -> None:
    first = runtime._derived_host_identity()
    second = runtime._derived_host_identity()

    assert first == second
    assert first.startswith("host@sha256:")
    assert len(first) == len("host@sha256:") + 64


def test_output_root_is_derived_and_rejects_symlinked_path(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    expected = repo / "logs/capability-first/cohort-a"

    assert runtime._validated_output_root(repo, "cohort-a") == expected

    expected.parent.mkdir(parents=True)
    expected.symlink_to(tmp_path / "outside", target_is_directory=True)
    with pytest.raises(runtime.CollectorError, match="symlink"):
        runtime._validated_output_root(repo, "cohort-a")


def test_effect_profile_requires_explicit_local_marker_authorization(tmp_path: Path) -> None:
    config = _config(tmp_path, local_markers_authorized=False)

    with pytest.raises(runtime.CollectorError, match="marker authorization"):
        runtime.run_one(
            config,
            "effect_only",
            1,
            process_runner=lambda *_: pytest.fail("unauthorized effect spawned Codex"),
            workspace_factory=_fake_workspace_factory(tmp_path / "workspaces"),
        )

    assert not config.cohort_root.exists()


def test_cli_derives_fixed_contract_identities_and_isolates_canary(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    captured = []
    order: list[str] = []
    monkeypatch.setattr(runtime, "REPOSITORY_ROOT", repo, raising=False)
    monkeypatch.setattr(
        runtime,
        "_preflight_committed_paths",
        lambda *_: {
            "source_head": "a" * 40,
            "blobs": {path: "sha256:" + "c" * 64 for path in runtime.REQUIRED_COMMITTED_PATHS},
        },
    )
    monkeypatch.setattr(
        runtime,
        "_approved_codex_runtime",
        lambda _contract: (Path("/real/codex"), "codex-cli/9.9.9@sha256:" + "b" * 64),
        raising=False,
    )
    monkeypatch.setattr(runtime, "_load_contract", lambda _path: json.loads(MANIFEST_PATH.read_text()))
    monkeypatch.setattr(runtime, "_derived_host_identity", lambda: "host@sha256:" + "f" * 64, raising=False)
    monkeypatch.setattr(
        runtime,
        "_reporter",
        lambda *_: order.append("reporter") or types.SimpleNamespace(),
    )

    def fake_run_one(config, profile, ordinal):
        order.append("spawn")
        captured.append((config, profile, ordinal))
        return runtime._record(
            f"{config.cohort_id}-{profile}-{ordinal}", runtime._digest_text("request"),
            "completed", {}, None, False,
            "sha256:" + "d" * 64, "sha256:" + "e" * 64,
        )

    monkeypatch.setattr(runtime, "run_one", fake_run_one)
    code = runtime.main([
        "--canary", "--cohort-id", "cohort-a",
        "--model", "gpt-test", "--reasoning-effort", "low",
    ])

    assert code == 0
    assert order[0] == "reporter"
    config, profile, ordinal = captured[0]
    assert (profile, ordinal) == ("none", 1)
    assert config.contract_path == repo / "scripts/baselines/capability_first_five_profile_v1.json"
    assert config.collector_identity == "capability-baseline-runtime@sha256:" + "c" * 64
    assert config.codex_identity == "codex-cli/9.9.9@sha256:" + "b" * 64
    assert config.cohort_id == "canary-cohort-a"
    assert config.cohort_root == repo / "logs/capability-first/.canaries/cohort-a"
    assert config.host_identity == "host@sha256:" + "f" * 64
    assert not (repo / "logs/capability-first/cohort-a").exists()


def test_collect_requires_marker_authorization_before_cohort(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    monkeypatch.setattr(runtime, "REPOSITORY_ROOT", repo, raising=False)
    monkeypatch.setattr(
        runtime,
        "_preflight_committed_paths",
        lambda *_: {
            "source_head": "a" * 40,
            "blobs": {path: "sha256:" + "c" * 64 for path in runtime.REQUIRED_COMMITTED_PATHS},
        },
    )
    monkeypatch.setattr(
        runtime,
        "_approved_codex_runtime",
        lambda _contract: (Path("/real/codex"), "codex-cli/9.9.9@sha256:" + "b" * 64),
        raising=False,
    )
    monkeypatch.setattr(runtime, "_derived_host_identity", lambda: "host@sha256:" + "f" * 64, raising=False)
    monkeypatch.setattr(runtime, "run_cohort", lambda *_: pytest.fail("unauthorized cohort started"))

    code = runtime.main([
        "--collect", "--cohort-id", "cohort-a",
        "--model", "gpt-test", "--reasoning-effort", "low",
    ])

    assert code == 2
    assert "marker authorization" in capsys.readouterr().err


def test_collect_rechecks_runtime_bytes_after_aggregation_before_write(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    monkeypatch.setattr(runtime, "REPOSITORY_ROOT", repo, raising=False)
    monkeypatch.setattr(
        runtime,
        "_preflight_committed_paths",
        lambda *_: {
            "source_head": "a" * 40,
            "blobs": {
                path: "sha256:" + "c" * 64
                for path in runtime.REQUIRED_COMMITTED_PATHS
            },
        },
    )
    monkeypatch.setattr(
        runtime,
        "_approved_codex_runtime",
        lambda _contract: (
            Path("/real/codex"),
            "codex-cli/9.9.9@sha256:" + "b" * 64,
        ),
    )
    monkeypatch.setattr(
        runtime,
        "_load_contract",
        lambda _path: json.loads(MANIFEST_PATH.read_text()),
    )
    monkeypatch.setattr(
        runtime,
        "_derived_host_identity",
        lambda: "host@sha256:" + "f" * 64,
    )
    reporter = types.SimpleNamespace(
        _aggregate_baseline=lambda *_args, **_kwargs: {"operational_complete": True},
    )
    monkeypatch.setattr(runtime, "_reporter", lambda *_: reporter)
    monkeypatch.setattr(
        runtime,
        "run_cohort",
        lambda *_args, **_kwargs: runtime.CohortResult(
            {}, (), object(), repo / "evidence"
        ),
    )
    monkeypatch.setattr(
        runtime,
        "_assert_committed_runtime",
        lambda _config: (_ for _ in ()).throw(
            runtime.PreflightError("commit-required: runtime bytes changed")
        ),
    )

    code = runtime.main(
        [
            "--collect",
            "--cohort-id",
            "cohort-a",
            "--model",
            "gpt-test",
            "--reasoning-effort",
            "low",
            "--authorize-local-markers",
        ]
    )

    assert code == 2
    assert not (repo / "logs/capability-first/cohort-a/baseline.json").exists()


def test_cli_rejects_caller_controlled_manifest_and_identity_options() -> None:
    for option in (
        "--repo", "--resume", "--manifest", "--collector-identity",
        "--codex-identity", "--codex-binary", "--host-identity", "--cohort-root",
    ):
        with pytest.raises(SystemExit):
            runtime._parser().parse_args(["--preflight", option, "forged"])
