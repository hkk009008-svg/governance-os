"""Focused contract for the supported Codex <-> Claude relay."""

from __future__ import annotations

import asyncio
import json
import math
import re
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pytest

# The connector runtime is OPTIONAL: ARCHITECTURE.md hash-locks it separately in
# requirements-connector.txt, and CI installs only requirements-dev.txt. Without
# this guard the module fails to COLLECT rather than skip, which ends the whole
# run at exit 2 instead of skipping one file.
pytest.importorskip("mcp", reason="optional connector runtime is not installed")

from mcp import types  # noqa: E402

import claude_task_connector as connector  # noqa: E402


class CapturingOptions:
    def __init__(self, **kwargs: Any) -> None:
        self.kwargs = kwargs


@dataclass
class FakeUserMessage:
    content: str
    origin: dict[str, Any] | None = None
    uuid: str | None = None


@dataclass
class FakeResultMessage:
    subtype: str = "success"
    is_error: bool = False
    total_cost_usd: float = 0.01
    errors: list[str] | None = None
    origin: dict[str, Any] | None = None
    uuid: str | None = None


_STOP = object()


class FakeClient:
    def __init__(
        self,
        options: Any,
        *,
        connect_error: str | None = None,
        stall_query: bool = False,
    ) -> None:
        self.options = options
        self.connect_error = connect_error
        self.stall_query = stall_query
        self.queries: list[str] = []
        self.query_started = threading.Event()
        self.connected = False
        self.disconnected = False
        self._loop: asyncio.AbstractEventLoop | None = None
        self._queue: asyncio.Queue[Any] | None = None

    async def connect(self) -> None:
        if self.connect_error:
            raise RuntimeError(self.connect_error)
        self._loop = asyncio.get_running_loop()
        self._queue = asyncio.Queue()
        self.connected = True

    async def receive_messages(self):
        assert self._queue is not None
        while True:
            message = await self._queue.get()
            if message is _STOP:
                return
            yield message

    async def query(self, prompt: str) -> None:
        self.queries.append(prompt)
        self.query_started.set()
        if self.stall_query:
            await asyncio.Future()

    async def disconnect(self) -> None:
        self.disconnected = True
        if self._queue is not None:
            self._queue.put_nowait(_STOP)

    def emit(self, message: Any) -> None:
        assert self._loop is not None and self._queue is not None
        self._loop.call_soon_threadsafe(self._queue.put_nowait, message)


class FakeFactory:
    def __init__(
        self,
        *,
        connect_error: str | None = None,
        stall_query: bool = False,
    ) -> None:
        self.connect_error = connect_error
        self.stall_query = stall_query
        self.clients: list[FakeClient] = []

    def __call__(self, options: Any) -> FakeClient:
        client = FakeClient(
            options,
            connect_error=self.connect_error,
            stall_query=self.stall_query,
        )
        self.clients.append(client)
        return client


def _config(tmp_path: Path, **overrides: Any) -> connector.BridgeConfig:
    values = {
        "cwd": tmp_path,
        "start_timeout_seconds": 1.0,
        "operation_timeout_seconds": 1.0,
    }
    values.update(overrides)
    return connector.BridgeConfig(**values)


def _runtime(tmp_path: Path, factory: FakeFactory | None = None):
    factory = factory or FakeFactory()
    runtime = connector.BridgeRuntime(
        client_factory=factory, options_cls=CapturingOptions
    )
    assert runtime.start(_config(tmp_path))["state"] == "running"
    return runtime, factory.clients[0]


def _until(predicate: Any, timeout: float = 1.0) -> None:
    deadline = time.monotonic() + timeout
    while not predicate():
        if time.monotonic() >= deadline:
            raise AssertionError("condition did not become true")
        time.sleep(0.005)


def _hook(client: FakeClient, phase: str):
    spec = client.options.kwargs["hooks"][phase][0]
    return spec.hooks[0]


def _tool_call(
    server: Any,
    name: str,
    arguments: dict[str, Any] | None = None,
) -> tuple[dict[str, Any], bool]:
    request = types.CallToolRequest(
        params=types.CallToolRequestParams(name=name, arguments=arguments or {})
    )
    result = asyncio.run(server.request_handlers[types.CallToolRequest](request)).root
    if result.isError:
        return {"error": result.content[0].text}, True
    assert result.structuredContent is not None
    return result.structuredContent, False


def _pre(name: str, tool_input: dict[str, Any]) -> dict[str, Any]:
    return {
        "hook_event_name": "PreToolUse",
        "tool_name": name,
        "tool_input": tool_input,
    }


def _post(
    name: str, tool_input: dict[str, Any], response: Any
) -> dict[str, Any]:
    return {
        "hook_event_name": "PostToolUse",
        "tool_name": name,
        "tool_input": tool_input,
        "tool_response": response,
    }


def _allowed(decision: dict[str, Any]) -> bool:
    return (
        decision["hookSpecificOutput"]["permissionDecision"] == "allow"
    )


def test_sdk_options_are_named_isolated_and_transport_only(tmp_path: Path) -> None:
    gate = connector.RelayGate()
    options = connector.build_sdk_options(
        _config(tmp_path),
        options_cls=CapturingOptions,
        gate=gate,
    ).kwargs

    assert options["tools"] == ["ListAgents", "SendMessage"]
    assert options["allowed_tools"] == ["ListAgents", "SendMessage"]
    assert options["mcp_servers"] == {}
    assert options["strict_mcp_config"] is True
    assert options["permission_mode"] == "dontAsk"
    assert options["setting_sources"] == []
    assert options["skills"] == []
    assert options["extra_args"] == {"name": connector.BRIDGE_NAME}
    assert json.loads(options["settings"]) == {
        "crossSessionInbound": "accept",
        "isolatePeerMachines": True,
    }
    assert set(options["hooks"]) == {"PreToolUse", "PostToolUse"}


def test_bridge_prompt_agrees_with_the_unarmed_gate() -> None:
    """The prompt must not direct an action the gate structurally forbids.

    Measured rather than assumed: with no relay armed the gate denies every
    native tool, so telling the bridge to "acknowledge" an inbound peer message
    can only produce denied tool calls, which spend budget against the bridge
    ceiling and achieve nothing. An unsolicited inbound message is already
    recorded in the event buffer for Codex to read, so the correct behaviour is
    to call no tool at all.

    Both halves are pinned together deliberately: if the gate ever starts
    allowing an unarmed tool, the first loop fails and the prompt wording is
    reconsidered as one decision instead of drifting apart again.
    """
    gate = connector.RelayGate()
    for tool in connector.NATIVE_TOOLS:
        decision = asyncio.run(gate.pre_tool_use(_pre(tool, {}), f"u-{tool}", None))
        assert not _allowed(decision), f"unarmed gate allowed {tool}"

    prompt = connector.BRIDGE_SYSTEM_PROMPT
    assert "Call no tool" in prompt
    assert "acknowledgement short" not in prompt


def test_gate_allows_only_one_confirmed_exact_relay() -> None:
    observed: list[dict[str, Any]] = []
    gate = connector.RelayGate(observer=observed.append)
    _prompt, request = connector.build_relay(
        target="pipeline-24 [abc123]",
        target_prefix=None,
        text="hello",
        message_id="m-1",
    )
    expected = {
        "to": request["target"],
        "summary": request["summary"],
        "message": request["message"],
    }

    denied = asyncio.run(gate.pre_tool_use(_pre("ListAgents", {}), "l0", None))
    assert not _allowed(denied)
    gate.arm(request)
    assert _allowed(
        asyncio.run(gate.pre_tool_use(_pre("ListAgents", {}), "l1", None))
    )
    assert not _allowed(
        asyncio.run(gate.pre_tool_use(_pre("ListAgents", {}), "l2", None))
    )
    assert not _allowed(
        asyncio.run(gate.pre_tool_use(_pre("SendMessage", expected), "s0", None))
    )
    assert not _allowed(
        asyncio.run(gate.pre_tool_use(_pre("Bash", {"command": "true"}), "b1", None))
    )

    asyncio.run(
        gate.post_tool_use(
            _post("ListAgents", {}, {"listing": "pipeline-24 [abc123] · idle"}),
            "l1",
            None,
        )
    )
    asyncio.run(
        gate.post_tool_use(
            _post("ListAgents", {}, {"listing": "attacker [bad999] · idle"}),
            "l1",
            None,
        )
    )
    assert gate.snapshot()["resolved_target"] == "pipeline-24 [abc123]"
    altered = dict(expected, message="changed")
    assert not _allowed(
        asyncio.run(gate.pre_tool_use(_pre("SendMessage", altered), "s1", None))
    )
    empty_preview = dict(expected, content="...")
    assert not _allowed(
        asyncio.run(
            gate.pre_tool_use(_pre("SendMessage", empty_preview), "s-empty", None)
        )
    )
    assert _allowed(
        asyncio.run(gate.pre_tool_use(_pre("SendMessage", expected), "s2", None))
    )
    assert not _allowed(
        asyncio.run(gate.pre_tool_use(_pre("SendMessage", expected), "s3", None))
    )
    asyncio.run(
        gate.post_tool_use(
            _post("SendMessage", expected, {"success": True}), "s2", None
        )
    )
    assert [event["name"] for event in observed] == ["ListAgents", "SendMessage"]
    assert observed[0]["resolved_target"] == "pipeline-24 [abc123]"


def test_no_reachable_agents_sentinel_cannot_be_selected_as_an_exact_target() -> None:
    gate = connector.RelayGate()
    _prompt, request = connector.build_relay(
        target="No reachable agents.",
        target_prefix=None,
        text="hello",
        message_id="no-peers-1",
    )
    gate.arm(request)
    asyncio.run(gate.pre_tool_use(_pre("ListAgents", {}), "l1", None))
    asyncio.run(
        gate.post_tool_use(
            _post("ListAgents", {}, {"listing": "No reachable agents."}),
            "l1",
            None,
        )
    )
    send = {
        "to": "No reachable agents.",
        "summary": request["summary"],
        "message": request["message"],
    }
    assert not _allowed(
        asyncio.run(gate.pre_tool_use(_pre("SendMessage", send), "s1", None))
    )


@pytest.mark.parametrize(
    ("first_listing", "second_listing", "retry_allowed", "send_allowed"),
    [
        ("different-peer [z9] · idle", None, False, False),
        ("No reachable agents.", "No reachable agents.", True, False),
        ("No reachable agents.", "pipeline-24 [abc123] · idle", True, True),
    ],
)
def test_registration_retry_is_empty_only_and_bounded(
    first_listing: str,
    second_listing: str | None,
    retry_allowed: bool,
    send_allowed: bool,
) -> None:
    gate = connector.RelayGate()
    _prompt, request = connector.build_relay(
        target="pipeline-24 [abc123]",
        target_prefix=None,
        text="hello",
        message_id=f"retry-{retry_allowed}-{send_allowed}",
    )
    gate.arm(request)
    assert _allowed(asyncio.run(gate.pre_tool_use(_pre("ListAgents", {}), "l1", None)))
    asyncio.run(
        gate.post_tool_use(
            _post("ListAgents", {}, {"listing": first_listing}), "l1", None
        )
    )
    retry = asyncio.run(gate.pre_tool_use(_pre("ListAgents", {}), "l2", None))
    assert _allowed(retry) is retry_allowed
    if not retry_allowed:
        return

    asyncio.run(
        gate.post_tool_use(
            _post("ListAgents", {}, {"listing": second_listing}), "l2", None
        )
    )
    assert not _allowed(
        asyncio.run(gate.pre_tool_use(_pre("ListAgents", {}), "l3", None))
    )
    send = {
        "to": "pipeline-24 [abc123]",
        "summary": request["summary"],
        "message": request["message"],
    }
    assert _allowed(
        asyncio.run(gate.pre_tool_use(_pre("SendMessage", send), "s1", None))
    ) is send_allowed


@pytest.mark.parametrize(
    ("listing", "allowed"),
    [
        ("pipeline-24 [a1] · idle", True),
        ("pipeline-24 [a1] · idle\npipeline-24-copy [b2] · idle", False),
        ("pipeline-24 [a1] · offline", False),
        ("pipeline-codex-bridge [self1] · idle", False),
        ("No reachable agents", False),
    ],
)
def test_prefix_must_resolve_to_one_live_nonself_peer(
    listing: str, allowed: bool
) -> None:
    gate = connector.RelayGate()
    _prompt, request = connector.build_relay(
        target=None,
        target_prefix="pipeline-24",
        text="hello",
        message_id="prefix-1",
    )
    gate.arm(request)
    asyncio.run(gate.pre_tool_use(_pre("ListAgents", {}), "l1", None))
    asyncio.run(
        gate.post_tool_use(
            _post("ListAgents", {}, {"listing": listing}), "l1", None
        )
    )
    target = "pipeline-24 [a1]" if allowed else None
    send = {
        "to": target,
        "summary": request["summary"],
        "message": request["message"],
    }
    assert _allowed(
        asyncio.run(gate.pre_tool_use(_pre("SendMessage", send), "s1", None))
    ) is allowed


@pytest.mark.parametrize("timeout", [0, -1, math.inf, math.nan, True, "1"])
def test_timeouts_are_finite_positive_and_bounded(
    tmp_path: Path, timeout: Any
) -> None:
    with pytest.raises(connector.ConnectorError):
        _config(tmp_path, operation_timeout_seconds=timeout)


def test_event_buffer_is_bounded_and_reports_truncation() -> None:
    store = connector.EventBuffer(2)
    store.append({"kind": "one"})
    store.append({"kind": "two"})
    store.append({"kind": "three"})

    result = store.wait(0, 10, 0)
    assert [event["kind"] for event in result["events"]] == ["two", "three"]
    assert result["truncated"] is True
    assert result["dropped_before_cursor"] == 1
    assert result["timed_out"] is False


def test_read_is_atomic_under_a_forced_interleave(tmp_path: Path) -> None:
    """Force the overlap instead of racing for it.

    Two earlier versions of this control raced a subprocess and were both
    vacuous: one passed when the writer never ran, the next passed when the
    writer wrote once and exited BEFORE any read observed it. Asserting that a
    write happened does not establish that it overlapped a read.

    So the write is injected at the exact point that matters -- between _read's
    cursor lookup and its events SELECT -- from a SECOND connection to the same
    file. Unguarded, the events query then returns a row newer than the cursor
    just read and the result is self-inconsistent, every run. Guarded, the
    deferred snapshot excludes it.
    """
    path = tmp_path / "shared" / "events.sqlite3"
    path.parent.mkdir(parents=True)
    store = connector.EventBuffer(256, path)
    store.append({"kind": "seed"})
    injector = connector.EventBuffer(256, path)

    original = store._meta
    fired = False

    def interleave(key: str) -> str:
        nonlocal fired
        value = original(key)
        if key == "cursor" and not fired:
            fired = True
            injector.append({"kind": "injected"})
        return value

    store._meta = interleave  # type: ignore[method-assign]
    try:
        result = store.wait(0, 50, 0)
        committed = injector.latest_cursor
    finally:
        store._meta = original  # type: ignore[method-assign]
        injector.close()
        store.close()

    # The postcondition is the WRITE, not the hook. An earlier version set a
    # flag BEFORE calling append, so deleting the append left every assertion
    # green -- even against the exact unguarded _read. A committed cursor of 2
    # (seed plus injection) cannot be produced by a hook that wrote nothing.
    assert committed == 2, (
        f"injected write did not commit (cursor {committed}); run proves nothing"
    )
    assert fired, "the interleave never fired; run proves nothing"
    assert result["cursor"] <= result["latest_cursor"], (
        f"read saw cursor {result['cursor']} past "
        f"latest_cursor {result['latest_cursor']}"
    )


def test_stopping_the_bridge_discards_the_shared_store(tmp_path: Path) -> None:
    """ARCHITECTURE.md calls the bridge transient; its store must be too."""
    runtime, _client = _runtime(tmp_path)
    path = connector.shared_buffer_path(Path(tmp_path).resolve())
    assert path.exists(), "starting a bridge should create the shared store"

    runtime.stop()
    assert not path.exists(), "stopping a bridge must not leave durable state"


def test_discard_surfaces_a_real_unlink_failure(tmp_path: Path) -> None:
    """The happy path above is not enough, and once said so falsely.

    discard caught bare OSError, so a store that could NOT be removed was
    reported as removed: stop() returned `stopped`, the files survived, and the
    next start resumed that generation and its stale cursor. Only a failing
    unlink separates the two behaviours, so this forces one.
    """
    directory = tmp_path / "store"
    directory.mkdir()
    store = connector.EventBuffer(4, directory / "events.sqlite3")
    store.append({"kind": "one"})
    directory.chmod(0o500)  # unlink now fails with EACCES
    try:
        with pytest.raises(OSError):
            store.discard()
    finally:
        directory.chmod(0o700)


def test_start_refuses_a_shared_namespace_before_it_destroys(tmp_path, monkeypatch, request):
    """A sentinel pins the ORDER, which calling the guard directly could not:
    cleanup runs after validation, so moving or deleting the guard eats it."""
    home = tmp_path / "home"
    home.mkdir(mode=0o750)
    monkeypatch.setenv("HOME", str(home))
    previous = connector.os.umask(0)
    request.addfinalizer(lambda: connector.os.umask(previous))
    store = connector.shared_buffer_path(tmp_path)
    _runtime(tmp_path)
    assert store.parent == home / ".pipeline-codex-bridge", "one level under home"
    assert not store.parent.stat().st_mode & 0o077, "and private under umask 000"
    store.write_bytes(b"sentinel")
    home.parent.chmod(0o777)
    with pytest.raises(connector.ConnectorError, match="writable beyond"):
        _runtime(tmp_path)
    assert store.read_bytes() == b"sentinel", "refusal must precede cleanup"


def test_runtime_relay_lifecycle_and_idempotency(tmp_path: Path) -> None:
    runtime, client = _runtime(tmp_path)
    prompt, request = connector.build_relay(
        target="pipeline-24 [abc123]",
        target_prefix=None,
        text="hello",
        message_id="relay-1",
    )
    submitted = runtime.send(prompt, request)
    assert submitted["status"] == "queued"
    assert submitted["delivery_ack"] is False
    assert client.query_started.wait(1)
    request = json.loads(client.queries[0].split("\n", 1)[1])
    send_input = {
        "to": request["target"],
        "summary": request["summary"],
        "message": request["message"],
    }

    pre, post = _hook(client, "PreToolUse"), _hook(client, "PostToolUse")
    assert _allowed(asyncio.run(pre(_pre("ListAgents", {}), "l1", None)))
    asyncio.run(
        post(
            _post("ListAgents", {}, {"listing": "pipeline-24 [abc123] · idle"}),
            "l1",
            None,
        )
    )
    assert _allowed(asyncio.run(pre(_pre("SendMessage", send_input), "s1", None)))
    asyncio.run(
        post(
            _post("SendMessage", send_input, {"success": True}),
            "s1",
            None,
        )
    )
    client.emit(FakeResultMessage())
    _until(lambda: runtime.status("relay-1")["operation"]["state"] == "terminal")

    receipt = runtime.status("relay-1")["operation"]
    assert receipt["outcome"] == "native_send_observed_no_end_to_end_ack"
    assert receipt["resolved_target"] == "pipeline-24 [abc123]"
    events = runtime.wait(
        generation=submitted["generation"],
        after=submitted["after_cursor"],
        timeout_seconds=0,
        operation_id="relay-1",
    )
    assert {"tool", "result"} <= {event["kind"] for event in events["events"]}
    duplicate = runtime.send(
        *connector.build_relay(
            target="pipeline-24 [abc123]",
            target_prefix=None,
            text="hello",
            message_id="relay-1",
        )
    )
    assert duplicate["status"] == "duplicate"
    with pytest.raises(connector.ConnectorError, match="different content"):
        runtime.send(
            *connector.build_relay(
                target="pipeline-24 [abc123]",
                target_prefix=None,
                text="changed",
                message_id="relay-1",
            )
        )
    assert runtime.stop()["state"] == "stopped"


def test_terminal_without_send_is_not_reported_as_delivery(tmp_path: Path) -> None:
    runtime, client = _runtime(tmp_path)
    runtime.send(
        *connector.build_relay(
            target="missing [none]",
            target_prefix=None,
            text="hello",
            message_id="relay-no-send",
        )
    )
    assert client.query_started.wait(1)
    client.emit(FakeResultMessage())
    _until(
        lambda: runtime.status("relay-no-send")["operation"]["state"] == "terminal"
    )
    receipt = runtime.status("relay-no-send")["operation"]
    assert receipt["outcome"] == "terminal_without_native_send"
    assert receipt["native_send_observed"] is False
    assert receipt["delivery_ack"] is False
    runtime.stop()


def test_in_flight_rejection_does_not_leak_or_poison_receipt(tmp_path: Path) -> None:
    runtime, client = _runtime(tmp_path)
    runtime.send(
        *connector.build_relay(
            target="pipeline-24 [abc123]",
            target_prefix=None,
            text="first",
            message_id="relay-live",
        )
    )
    assert client.query_started.wait(1)
    retry = connector.build_relay(
        target="pipeline-24 [abc123]",
        target_prefix=None,
        text="retry",
        message_id="relay-retry",
    )
    with pytest.raises(connector.ConnectorError, match="still in flight"):
        runtime.send(*retry)
    with pytest.raises(connector.ConnectorError, match="unknown relay"):
        runtime.status("relay-retry")

    client.emit(FakeResultMessage())
    _until(lambda: runtime.status("relay-live")["operation"]["state"] == "terminal")
    assert runtime.send(*retry)["status"] == "queued"
    runtime.stop()


def test_stalled_query_does_not_block_status_and_quarantines_on_timeout(
    tmp_path: Path,
) -> None:
    factory = FakeFactory(stall_query=True)
    runtime = connector.BridgeRuntime(
        client_factory=factory, options_cls=CapturingOptions
    )
    runtime.start(_config(tmp_path, operation_timeout_seconds=0.05))
    started = time.monotonic()
    runtime.send(
        *connector.build_relay(
            target="pipeline-24 [abc123]",
            target_prefix=None,
            text="hello",
            message_id="stall-1",
        )
    )
    assert time.monotonic() - started < 0.05
    assert runtime.status()["state"] == "running"
    _until(lambda: runtime.status()["state"] == "error")
    receipt = runtime.status("stall-1")["operation"]
    assert receipt["state"] == "timed_out"
    assert receipt["outcome"] == "timed_out_without_native_send"
    runtime.stop()


def test_peer_messages_are_attributed_deduplicated_and_conflicts_fail(
    tmp_path: Path,
) -> None:
    runtime, client = _runtime(tmp_path)
    origin = {
        "kind": "peer",
        "from": "uds:peer",
        "name": "pipeline-24",
        "fromSession": "session-1",
        "msg_id": "peer-message-1",
        "body": "from Claude",
    }
    client.emit(FakeUserMessage("fallback", origin=origin, uuid="u1"))
    client.emit(FakeUserMessage("fallback", origin=origin, uuid="u2"))
    _until(lambda: runtime.status()["latest_cursor"] == 1)
    events = runtime.wait(
        generation=runtime.status()["generation"], after=0, timeout_seconds=0
    )
    assert len(events["events"]) == 1
    assert events["events"][0]["sender"]["identity_scope"] == "routing_only"
    client.emit(
        FakeUserMessage(
            "fallback",
            origin=dict(origin, body="conflict"),
            uuid="u3",
        )
    )
    _until(lambda: runtime.status()["state"] == "error")
    assert "reused" in runtime.status()["last_error"]
    runtime.stop()


@pytest.mark.parametrize(
    ("content", "body", "kind", "error"),
    [
        ("fallback", "hello\x1b[31m", "peer_message_rejected", "control character"),
        (
            "x" * (connector.MAX_MESSAGE_BYTES + 1),
            "ignored",
            "message_rejected",
            "exceeds",
        ),
    ],
)
def test_malformed_inbound_message_is_rejected_without_stopping_bridge(
    tmp_path: Path, content: str, body: str, kind: str, error: str
) -> None:
    runtime, client = _runtime(tmp_path)
    client.emit(
        FakeUserMessage(
            content,
            origin={
                "kind": "peer",
                "from": "uds:peer",
                "name": "pipeline-24",
                "msg_id": "bad-peer-message",
                "body": body,
            },
        )
    )
    _until(lambda: runtime.status()["latest_cursor"] == 1)
    assert runtime.status()["state"] == "running"
    event = runtime.wait(
        generation=runtime.status()["generation"], after=0, timeout_seconds=0
    )["events"][0]
    assert event["kind"] == kind
    assert error in event["error"]
    runtime.stop()


def test_connect_error_never_reports_running(tmp_path: Path) -> None:
    factory = FakeFactory(connect_error="boom")
    runtime = connector.BridgeRuntime(
        client_factory=factory, options_cls=CapturingOptions
    )
    with pytest.raises(connector.ConnectorError, match="boom"):
        runtime.start(_config(tmp_path))
    assert runtime.status()["state"] == "error"


def test_mcp_surface_is_five_tools_and_send_lazily_starts(tmp_path: Path) -> None:
    factory = FakeFactory()
    runtime = connector.BridgeRuntime(
        client_factory=factory, options_cls=CapturingOptions
    )
    tools_api = connector.ConnectorTools(runtime=runtime, default_cwd=tmp_path)
    server = connector.build_mcp_server(tools_api)
    assert server.name == "pipeline-claude-task-connector"
    assert server.version == connector.SERVER_VERSION
    assert factory.clients == []

    listed = asyncio.run(
        server.request_handlers[types.ListToolsRequest](types.ListToolsRequest())
    )
    tools = {tool.name: tool for tool in listed.root.tools}
    assert set(tools) == {
        "claude_bridge_start",
        "claude_bridge_status",
        "claude_bridge_send",
        "claude_bridge_wait",
        "claude_bridge_stop",
    }
    assert tools["claude_bridge_start"].inputSchema["properties"] == {}
    assert factory.clients == []

    invalid, is_error = _tool_call(
        server,
        "claude_bridge_send",
        {"target_prefix": "bad prefix", "text": "hello", "message_id": "bad-1"},
    )
    assert is_error is True
    assert "target_prefix" in invalid["error"]
    assert factory.clients == []

    sent, is_error = _tool_call(
        server,
        "claude_bridge_send",
        {
            "target_prefix": "pipeline-24",
            "text": "hello",
            "message_id": "lazy-1",
        },
    )
    assert is_error is False
    assert sent["status"] == "queued"
    assert len(factory.clients) == 1
    assert factory.clients[0].options.kwargs["max_budget_usd"] == 1.0
    runtime.stop()


def test_mcp_start_rejects_caller_tuning_without_launch(
    tmp_path: Path,
) -> None:
    factory = FakeFactory()
    tools_api = connector.ConnectorTools(
        runtime=connector.BridgeRuntime(
            client_factory=factory, options_cls=CapturingOptions
        ),
        default_cwd=tmp_path,
    )
    server = connector.build_mcp_server(tools_api)
    result, is_error = _tool_call(
        server, "claude_bridge_start", {"max_budget_usd": 1.01}
    )
    assert is_error is True
    assert "Additional properties" in result["error"]
    assert factory.clients == []


def test_wait_rejects_stale_generation(tmp_path: Path) -> None:
    runtime, _client = _runtime(tmp_path)
    with pytest.raises(connector.ConnectorError, match="generation"):
        runtime.wait(generation="stale", timeout_seconds=0)
    runtime.stop()


def test_capabilities_describe_only_the_supported_boundary() -> None:
    report = connector.capability_report()
    assert report["transport"] == "supported_claude_agent_sdk_native_peer"
    assert report["bridge_name"] == "pipeline-codex-bridge"
    assert report["standing_budget_usd"] == 1.0
    assert report["native_tools"] == ["ListAgents", "SendMessage"]
    assert report["delivery_ack"] is False
    assert report["governance_authority"] == "none"


def test_project_wrapper_config_and_dependency_pin_remain_present() -> None:
    root = Path(__file__).resolve().parents[2]
    config = (root / ".codex/config.toml").read_text(encoding="utf-8")
    wrapper = root / "coordination/bin/claude-task-connector"
    requirement = (root / "requirements-connector.in").read_text(encoding="utf-8")
    connector_lock = (root / "requirements-connector.txt").read_text(encoding="utf-8")
    governance_lock = (root / "requirements-governance.txt").read_text(encoding="utf-8")

    assert "[mcp_servers.claude_task_connector]" in config
    assert "coordination/bin/claude-task-connector" in config
    assert wrapper.stat().st_mode & 0o111
    assert "claude-agent-sdk==0.2.137" in requirement
    assert "mcp==1.29.0" in requirement
    assert "--constraint requirements-governance.txt" in connector_lock.splitlines()[1]
    for package in ("cffi", "cryptography"):
        pattern = re.compile(rf"^{package}==([^ \\\n]+)", re.MULTILINE)
        assert pattern.search(connector_lock).group(1) == pattern.search(
            governance_lock
        ).group(1)
