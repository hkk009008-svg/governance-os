"""Focused contract for the supported Codex <-> Claude relay."""

from __future__ import annotations

import asyncio
import io
import json
import math
import re
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pytest

import claude_task_connector as connector


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
        "max_budget_usd": 0.25,
        "queue_limit": 16,
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
    server: connector.ConnectorMcpServer,
    name: str,
    arguments: dict[str, Any] | None = None,
) -> tuple[dict[str, Any], bool]:
    response = server.handle_request(
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {"name": name, "arguments": arguments or {}},
        }
    )
    result = response["result"]
    return json.loads(result["content"][0]["text"]), result["isError"]


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


@pytest.mark.parametrize(
    "budget",
    [0, -1, 1.01, math.inf, math.nan, True, "1"],
)
def test_budget_is_finite_positive_and_hard_capped(
    tmp_path: Path, budget: Any
) -> None:
    with pytest.raises(connector.ConnectorError):
        _config(tmp_path, max_budget_usd=budget)


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
    server = connector.ConnectorMcpServer(runtime=runtime, default_cwd=tmp_path)
    initialized = server.handle_request(
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {"protocolVersion": "2025-06-18"},
        }
    )
    assert initialized["result"]["capabilities"]["tools"] == {"listChanged": False}
    assert factory.clients == []

    listed = server.handle_request(
        {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}
    )
    tools = {tool["name"]: tool for tool in listed["result"]["tools"]}
    assert set(tools) == {
        "claude_bridge_start",
        "claude_bridge_status",
        "claude_bridge_send",
        "claude_bridge_wait",
        "claude_bridge_stop",
    }
    assert "launch_authorized" not in tools["claude_bridge_start"]["inputSchema"]["properties"]
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


def test_mcp_rejects_budget_above_standing_ceiling_without_launch(
    tmp_path: Path,
) -> None:
    factory = FakeFactory()
    server = connector.ConnectorMcpServer(
        runtime=connector.BridgeRuntime(
            client_factory=factory, options_cls=CapturingOptions
        ),
        default_cwd=tmp_path,
    )
    result, is_error = _tool_call(
        server, "claude_bridge_start", {"max_budget_usd": 1.01}
    )
    assert is_error is True
    assert "at most 1" in result["error"]
    assert factory.clients == []


def test_wait_rejects_stale_generation(tmp_path: Path) -> None:
    runtime, _client = _runtime(tmp_path)
    with pytest.raises(connector.ConnectorError, match="generation"):
        runtime.wait(generation="stale", timeout_seconds=0)
    runtime.stop()


def test_stdio_survives_bad_json_and_lists_tools(tmp_path: Path) -> None:
    runtime = connector.BridgeRuntime(
        client_factory=FakeFactory(), options_cls=CapturingOptions
    )
    server = connector.ConnectorMcpServer(runtime=runtime, default_cwd=tmp_path)
    stdin = io.StringIO(
        "not-json\n"
        + json.dumps(
            {"jsonrpc": "2.0", "id": 7, "method": "tools/list", "params": {}}
        )
        + "\n"
    )
    stdout = io.StringIO()
    connector.serve_stdio(server, stdin=stdin, stdout=stdout)
    replies = [json.loads(line) for line in stdout.getvalue().splitlines()]
    assert replies[0]["error"]["code"] == -32700
    assert len(replies[1]["result"]["tools"]) == 5


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
    assert "--constraint requirements-governance.txt" in connector_lock.splitlines()[1]
    for package in ("cffi", "cryptography"):
        pattern = re.compile(rf"^{package}==([^ \\\n]+)", re.MULTILINE)
        assert pattern.search(connector_lock).group(1) == pattern.search(
            governance_lock
        ).group(1)
