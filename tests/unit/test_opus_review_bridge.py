from __future__ import annotations

import errno
import inspect
import json
import os
import signal
import shlex
import shutil
import socket
import stat
import subprocess
import sys
import threading
import time
from contextlib import contextmanager
from dataclasses import replace
from pathlib import Path

import pytest

import opus_review_bridge as bridge


ROOT = Path(__file__).resolve().parents[2]
EXPECTED_PROVIDER_OUTPUT_LIMIT_BYTES = 131_072


@pytest.fixture(scope="module")
def host_capabilities() -> bridge.HostCapabilities:
    return bridge.probe_host_capabilities()


def _require_host_capabilities(
    capabilities: bridge.HostCapabilities,
    *required: str,
) -> None:
    missing = tuple(
        name for name in required if not getattr(capabilities, name)
    )
    if missing:
        pytest.skip(f"host capability unavailable: {', '.join(missing)}")


def _root_revision(revision: str) -> str:
    completed = subprocess.run(
        ["env", "-u", "GIT_INDEX_FILE", "git", "rev-parse", revision],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


HEAD = _root_revision("HEAD")
BASE = _root_revision("HEAD^1")


def _finding_payload(*, severity: str = "important") -> dict[str, object]:
    return {
        "id": "OPUS-1",
        "severity": severity,
        "claim": "the guard accepts a stale parent",
        "location": "scripts/route_lineage.py:120",
        "evidence": "the stale-parent branch returns success",
        "reproduction": "run the stale-parent focused test",
    }


def _structured_payload(
    *,
    status: str = "pass",
    findings: list[dict[str, object]] | None = None,
    reviewed_head: str = HEAD,
    reviewed_base: str | None = BASE,
) -> dict[str, object]:
    return {
        "schema_version": "opus-review/v2",
        "review_profile": "codex-lane-v",
        "reviewed_head": reviewed_head,
        "reviewed_base": reviewed_base,
        "status": status,
        "findings": [] if findings is None else findings,
    }


def test_parse_structured_review_accepts_clean_opus_pass() -> None:
    review = bridge.parse_structured_review(
        _structured_payload(),
        expected_head=HEAD,
        expected_base=BASE,
        expected_profile="codex-lane-v",
        effective_model="claude-opus-4-7",
        authorization_source="user-task:verification-1",
    )

    assert review.status == "pass"
    assert review.findings == ()
    assert review.effective_model == "claude-opus-4-7"
    assert review.to_dict()["schema_version"] == "opus-review/v2"


def test_opus_review_v2_round_trip_preserves_codex_lane_v_profile() -> None:
    review = bridge.parse_structured_review(
        _structured_payload(),
        expected_head=HEAD,
        expected_base=BASE,
        expected_profile="codex-lane-v",
        effective_model="claude-opus-4-7",
        authorization_source="user-task:verification-1",
    )

    payload = review.to_dict()
    assert payload["schema_version"] == "opus-review/v2"
    assert payload["review_profile"] == "codex-lane-v"
    assert bridge.OpusReview.from_dict(payload) == review


def test_opus_review_from_dict_rejects_v1_without_profile() -> None:
    payload = _normalized_pass_payload()
    payload["schema_version"] = "opus-review/v1"
    payload.pop("review_profile", None)

    with pytest.raises(bridge.ReviewContractError) as excinfo:
        bridge.OpusReview.from_dict(payload)

    assert excinfo.value.reason == "invalid_schema"


def test_parse_structured_review_rejects_wrong_profile() -> None:
    payload = _structured_payload()
    payload["review_profile"] = "money-gate"

    with pytest.raises(bridge.ReviewContractError) as excinfo:
        bridge.parse_structured_review(
            payload,
            expected_head=HEAD,
            expected_base=BASE,
            expected_profile="codex-lane-v",
            effective_model="claude-opus-4-7",
            authorization_source="user-task:verification-1",
        )

    assert excinfo.value.reason == "invalid_schema"


def test_parse_structured_review_rejects_scope_mismatch() -> None:
    payload = _structured_payload()
    payload["reviewed_head"] = "c" * 40

    with pytest.raises(bridge.ReviewContractError) as excinfo:
        bridge.parse_structured_review(
            payload,
            expected_head=HEAD,
            expected_base=BASE,
            expected_profile="codex-lane-v",
            effective_model="claude-opus-4-7",
            authorization_source="user-task:verification-1",
        )

    assert excinfo.value.reason == "reviewed_scope_mismatch"


@pytest.mark.parametrize(
    "finding_id",
    ["", " OPUS-1", "OPUS-1 ", "OPUS=1", "OPUS/1", "A" * 65],
    ids=["empty", "leading-space", "trailing-space", "equals", "slash", "too-long"],
)
def test_finding_id_parser_matches_bounded_delimiter_safe_schema(
    finding_id: str,
) -> None:
    finding = _finding_payload()
    finding["id"] = finding_id

    with pytest.raises(bridge.ReviewContractError) as excinfo:
        bridge.parse_structured_review(
            _structured_payload(status="issues", findings=[finding]),
            expected_head=HEAD,
            expected_base=BASE,
            expected_profile="codex-lane-v",
            effective_model="claude-opus-4-7",
            authorization_source="user-task:verification-1",
        )

    assert excinfo.value.reason == "invalid_schema"
    schema = bridge.OPUS_OUTPUT_SCHEMA["properties"]["findings"]["items"][
        "properties"
    ]["id"]
    assert schema == {
        "type": "string",
        "pattern": bridge.FINDING_ID_PATTERN,
        "minLength": 1,
        "maxLength": bridge.FINDING_ID_MAX_LENGTH,
    }


def _normalized_pass_payload() -> dict[str, object]:
    return bridge.parse_structured_review(
        _structured_payload(),
        expected_head=HEAD,
        expected_base=BASE,
        expected_profile="codex-lane-v",
        effective_model="claude-opus-4-7",
        authorization_source="user-task:verification-1",
    ).to_dict()


def _reconcile(
    codex_verdict: str,
    review: bridge.OpusReview,
    dispositions: list[bridge.FindingDisposition],
) -> bridge.Reconciliation:
    return bridge.reconcile(
        codex_verdict,
        review,
        dispositions,
        repo_root=ROOT,
        expected_head=review.reviewed_head,
        expected_base=review.reviewed_base,
    )


def test_opus_review_from_dict_rejects_extra_top_level_fields() -> None:
    payload = _normalized_pass_payload()
    payload["ignored"] = "must not be silently accepted"

    with pytest.raises(bridge.ReviewContractError) as excinfo:
        bridge.OpusReview.from_dict(payload)

    assert excinfo.value.reason == "invalid_schema"


def test_opus_review_from_dict_never_discards_unavailable_evidence() -> None:
    payload = bridge.OpusReview.unavailable(
        reviewed_head=HEAD,
        reviewed_base=BASE,
        review_profile=bridge.CODEX_LANE_V_REVIEW_PROFILE,
        authorization_source="user-task:verification-1",
        reason="timeout",
    ).to_dict()
    payload["effective_model"] = "claude-opus-4-7"
    payload["findings"] = [_finding_payload()]

    with pytest.raises(bridge.ReviewContractError) as excinfo:
        bridge.OpusReview.from_dict(payload)

    assert excinfo.value.reason == "invalid_schema"


@pytest.mark.parametrize(
    ("changes", "case"),
    [
        ({"authorization_source": "invented-consent"}, "invalid authorization"),
        ({"unavailable_reason": "timeout"}, "pass with unavailable reason"),
    ],
)
def test_opus_review_from_dict_enforces_status_and_authorization_invariants(
    changes: dict[str, object], case: str
) -> None:
    payload = _normalized_pass_payload()
    payload.update(changes)

    with pytest.raises(bridge.ReviewContractError) as excinfo:
        bridge.OpusReview.from_dict(payload)

    assert excinfo.value.reason == "invalid_schema", case


def test_opus_review_from_dict_accepts_only_missing_authorization_sentinel(
) -> None:
    payload = bridge.OpusReview.unavailable(
        reviewed_head=HEAD,
        reviewed_base=BASE,
        review_profile=bridge.CODEX_LANE_V_REVIEW_PROFILE,
        authorization_source="missing",
        reason="authorization_missing",
    ).to_dict()

    review = bridge.OpusReview.from_dict(payload)

    assert review.status == "unavailable"
    assert review.authorization_source == "missing"


def test_reconcile_blocks_unresolved_finding() -> None:
    review = bridge.parse_structured_review(
        _structured_payload(status="issues", findings=[_finding_payload()]),
        expected_head=HEAD,
        expected_base=BASE,
        expected_profile="codex-lane-v",
        effective_model="claude-opus-4-7",
        authorization_source="user-task:verification-1",
    )

    result = _reconcile(
        "GO",
        review,
        [bridge.FindingDisposition("OPUS-1", "unresolved", "")],
    )

    assert not result.go_allowed
    assert result.unresolved_finding_ids == ("OPUS-1",)
    assert result.blocking_finding_ids == ("OPUS-1",)


def test_reconcile_requires_evidence_to_disprove() -> None:
    review = bridge.parse_structured_review(
        _structured_payload(status="issues", findings=[_finding_payload()]),
        expected_head=HEAD,
        expected_base=BASE,
        expected_profile="codex-lane-v",
        effective_model="claude-opus-4-7",
        authorization_source="user-task:verification-1",
    )

    with pytest.raises(bridge.ReviewContractError) as excinfo:
        _reconcile(
            "GO",
            review,
            [bridge.FindingDisposition("OPUS-1", "disproved", "")],
        )

    assert excinfo.value.reason == "disproof_evidence_missing"


@pytest.mark.parametrize(
    ("codex_verdict", "go_allowed"),
    [("GO", True), ("NITS", False), ("FAIL", False)],
)
def test_reconcile_unavailable_preserves_degraded_codex_verdict(
    codex_verdict: str, go_allowed: bool
) -> None:
    review = bridge.OpusReview.unavailable(
        reviewed_head=HEAD,
        reviewed_base=BASE,
        review_profile=bridge.CODEX_LANE_V_REVIEW_PROFILE,
        authorization_source="user-task:verification-1",
        reason="timeout",
    )

    result = _reconcile(codex_verdict, review, [])

    assert result.codex_verdict == codex_verdict
    assert result.go_allowed is go_allowed
    assert result.degraded_cross_model_review
    assert result.degraded_reason == "timeout"


def test_reconcile_confirmed_minor_requires_nits() -> None:
    review = bridge.parse_structured_review(
        _structured_payload(
            status="issues", findings=[_finding_payload(severity="minor")]
        ),
        expected_head=HEAD,
        expected_base=BASE,
        expected_profile="codex-lane-v",
        effective_model="claude-opus-4-7",
        authorization_source="user-task:verification-1",
    )

    result = _reconcile(
        "GO", review, [bridge.FindingDisposition("OPUS-1", "confirmed", "")]
    )

    assert not result.go_allowed
    assert result.confirmed_nits_finding_ids == ("OPUS-1",)
    assert result.confirmed_fail_finding_ids == ()


@pytest.mark.parametrize("severity", ["important", "critical"])
def test_reconcile_confirmed_important_or_critical_requires_fail(
    severity: str,
) -> None:
    review = bridge.parse_structured_review(
        _structured_payload(status="issues", findings=[_finding_payload(severity=severity)]),
        expected_head=HEAD,
        expected_base=BASE,
        expected_profile="codex-lane-v",
        effective_model="claude-opus-4-7",
        authorization_source="user-task:verification-1",
    )

    result = _reconcile(
        "GO", review, [bridge.FindingDisposition("OPUS-1", "confirmed", "")]
    )

    assert not result.go_allowed
    assert result.confirmed_fail_finding_ids == ("OPUS-1",)
    assert result.confirmed_nits_finding_ids == ()


def test_reconcile_all_evidence_backed_disproofs_allow_codex_go() -> None:
    review = bridge.parse_structured_review(
        _structured_payload(status="issues", findings=[_finding_payload()]),
        expected_head=HEAD,
        expected_base=BASE,
        expected_profile="codex-lane-v",
        effective_model="claude-opus-4-7",
        authorization_source="user-task:verification-1",
    )

    result = _reconcile(
        "GO",
        review,
        [
            bridge.FindingDisposition(
                "OPUS-1", "disproved", "focused stale-parent test exits 0"
            )
        ],
    )

    assert result.go_allowed
    assert result.disproved_finding_ids == ("OPUS-1",)
    assert result.blocking_finding_ids == ()


@pytest.mark.parametrize("codex_verdict", ["NITS", "FAIL"])
def test_reconcile_never_upgrades_non_go_codex_verdict(codex_verdict: str) -> None:
    review = bridge.parse_structured_review(
        _structured_payload(),
        expected_head=HEAD,
        expected_base=BASE,
        expected_profile="codex-lane-v",
        effective_model="claude-opus-4-7",
        authorization_source="user-task:verification-1",
    )

    result = _reconcile(codex_verdict, review, [])

    assert result.codex_verdict == codex_verdict
    assert not result.go_allowed


def test_reconcile_requires_exact_finding_disposition_set() -> None:
    review = bridge.parse_structured_review(
        _structured_payload(status="issues", findings=[_finding_payload()]),
        expected_head=HEAD,
        expected_base=BASE,
        expected_profile="codex-lane-v",
        effective_model="claude-opus-4-7",
        authorization_source="user-task:verification-1",
    )

    with pytest.raises(bridge.ReviewContractError) as excinfo:
        _reconcile("GO", review, [])

    assert excinfo.value.reason == "disposition_mismatch"


def test_reconcile_binds_expected_scope_and_preserves_it_in_output() -> None:
    parameters = inspect.signature(bridge.reconcile).parameters
    assert "expected_head" in parameters
    assert "expected_base" in parameters

    review = bridge.parse_structured_review(
        _structured_payload(),
        expected_head=HEAD,
        expected_base=BASE,
        expected_profile="codex-lane-v",
        effective_model="claude-opus-4-7",
        authorization_source="user-task:verification-1",
    )
    with pytest.raises(bridge.ReviewContractError) as excinfo:
        bridge.reconcile(
            "GO",
            review,
            [],
            repo_root=ROOT,
            expected_head="c" * 40,
            expected_base=BASE,
        )
    assert excinfo.value.reason == "reviewed_scope_mismatch"

    result = bridge.reconcile(
        "GO",
        review,
        [],
        repo_root=ROOT,
        expected_head=HEAD,
        expected_base=BASE,
    )
    assert result.reviewed_head == HEAD
    assert result.reviewed_base == BASE
    assert result.to_dict()["reviewed_head"] == HEAD
    assert result.to_dict()["reviewed_base"] == BASE


def test_reconcile_rejects_nonexistent_commits_in_explicit_pipeline_root() -> None:
    missing_head = "f" * 40
    review = bridge.OpusReview.unavailable(
        reviewed_head=missing_head,
        reviewed_base=BASE,
        review_profile=bridge.CODEX_LANE_V_REVIEW_PROFILE,
        authorization_source="user-task:verification-1",
        reason="timeout",
    )

    try:
        bridge.reconcile(
            "GO",
            review,
            [],
            repo_root=ROOT,
            expected_head=missing_head,
            expected_base=BASE,
        )
    except TypeError as exc:
        pytest.fail(f"reconcile must require an explicit repo_root: {exc}")
    except bridge.ReviewContractError as exc:
        assert exc.reason == "invalid_scope"
    else:
        pytest.fail("a syntactically valid nonexistent commit must not allow GO")


def _uncommitted_request(
    tmp_path: Path, *, authorization: str = "user-task:verification-1"
) -> bridge.ReviewRequest:
    (tmp_path / "AGENTS.md").write_text("# Pipeline fixture\n", encoding="utf-8")
    (tmp_path / "scripts").mkdir(exist_ok=True)
    (tmp_path / "scripts" / "codex_protocol_model.py").write_text(
        "# Pipeline marker\n", encoding="utf-8"
    )
    agent = tmp_path / ".claude" / "agents" / "lane-v-verifier.md"
    agent.parent.mkdir(parents=True, exist_ok=True)
    agent.write_text(
        "---\n"
        "name: lane-v-verifier\n"
        "description: Fixture independent verifier\n"
        "tools: Read, Grep, Glob, Bash\n"
        "model: sonnet\n"
        "---\n\n"
        "# Fixture Lane V\n\nROLE-CONTENT-FROM-EXISTING-AGENT\n",
        encoding="utf-8",
    )
    requirement = tmp_path / "brief.md"
    requirement.write_text("Verify the stale-parent guard.\n", encoding="utf-8")
    return bridge.ReviewRequest(
        repo_root=tmp_path,
        reviewed_head=HEAD,
        reviewed_base=BASE,
        requirement_paths=(requirement,),
        allowed_paths=("scripts/route_lineage.py", "tests/unit/test_route_lineage.py"),
        verification_commands=(
            "env -u GIT_INDEX_FILE .venv/bin/python -m pytest "
            "tests/unit/test_route_lineage.py -q",
        ),
        review_profile=bridge.CODEX_LANE_V_REVIEW_PROFILE,
        authorization_source=authorization,
    )


def _git(root: Path, *args: str) -> str:
    completed = subprocess.run(
        ["env", "-u", "GIT_INDEX_FILE", "git", *args],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def _committed_request(
    tmp_path: Path,
    *,
    route_test_source: str = "def test_fixture():\n    assert True\n",
) -> bridge.ReviewRequest:
    request = _uncommitted_request(tmp_path)
    route = tmp_path / "scripts" / "route_lineage.py"
    route.write_text("STATE = 'base'\n", encoding="utf-8")
    route_test = tmp_path / "tests" / "unit" / "test_route_lineage.py"
    route_test.parent.mkdir(parents=True)
    route_test.write_text(route_test_source, encoding="utf-8")
    agent = tmp_path / ".claude" / "agents" / "lane-v-verifier.md"
    agent.write_text(
        "---\nname: lane-v-verifier\n---\n\n"
        "ROLE-CONTENT-FROM-EXISTING-AGENT\nBASE-TRUSTED-AGENT\n",
        encoding="utf-8",
    )
    (tmp_path / "brief.md").write_text("base requirement\n", encoding="utf-8")

    _git(tmp_path, "init", "-q")
    _git(tmp_path, "config", "user.name", "Opus Bridge Test")
    _git(tmp_path, "config", "user.email", "opus-bridge@example.invalid")
    _git(tmp_path, "add", ".")
    _git(tmp_path, "commit", "-q", "-m", "base")
    reviewed_base = _git(tmp_path, "rev-parse", "HEAD")

    agent.write_text(
        "---\nname: lane-v-verifier\n---\n\n"
        "ROLE-CONTENT-FROM-EXISTING-AGENT\nHEAD-UNTRUSTED-AGENT\n",
        encoding="utf-8",
    )
    (tmp_path / "brief.md").write_text("head requirement\n", encoding="utf-8")
    route.write_text("STATE = 'reviewed-head'\n", encoding="utf-8")
    _git(tmp_path, "add", ".")
    _git(tmp_path, "commit", "-q", "-m", "head")
    reviewed_head = _git(tmp_path, "rev-parse", "HEAD")

    agent.write_text(
        "---\nname: lane-v-verifier\n---\n\n"
        "ROLE-CONTENT-FROM-EXISTING-AGENT\nMUTABLE-WIP-AGENT\n",
        encoding="utf-8",
    )
    (tmp_path / "brief.md").write_text("mutable WIP requirement\n", encoding="utf-8")
    route.write_text("STATE = 'mutable-wip'\n", encoding="utf-8")
    return replace(
        request,
        reviewed_head=reviewed_head,
        reviewed_base=reviewed_base,
    )


def _request(
    tmp_path: Path, *, authorization: str = "user-task:verification-1"
) -> bridge.ReviewRequest:
    return replace(
        _committed_request(tmp_path),
        authorization_source=authorization,
    )


def _sandbox_probe_request(tmp_path: Path, test_source: str) -> bridge.ReviewRequest:
    request = _committed_request(tmp_path, route_test_source=test_source)
    return replace(
        request,
        verification_commands=(
            f"env -u GIT_INDEX_FILE {shlex.quote(sys.executable)} -m pytest "
            "tests/unit/test_route_lineage.py -q",
        ),
    )


def _verification_command_from_provider_argv(argv: list[str]) -> list[str]:
    rules = argv[argv.index("--allowedTools") + 1 :]
    rule = next(
        item
        for item in rules
        if "broker_client.py" in item or "-m pytest" in item
    )
    assert rule.startswith("Bash(") and rule.endswith(")")
    return shlex.split(rule[len("Bash(") : -1])


def _assert_broker_client_command(
    argv: list[str], *, expected_command_timeout: int
) -> None:
    assert len(argv) == 5
    assert Path(argv[0]).resolve() == Path(sys.executable).resolve()
    assert Path(argv[1]).name == "broker_client.py"
    assert Path(argv[2]).is_absolute()
    assert stat.S_ISSOCK(Path(argv[2]).stat().st_mode)
    assert stat.S_IMODE(Path(argv[2]).stat().st_mode) == 0o600
    assert len(argv[3]) == 64
    assert all(character in "0123456789abcdef" for character in argv[3])
    assert argv[4] == str(expected_command_timeout + 5)


def _broker_client_commands(tmp_path: Path, count: int) -> tuple[str, ...]:
    root = tmp_path / "opus-sandbox-test"
    control = root / "control"
    broker_dir = root / "broker"
    control.mkdir(parents=True, exist_ok=True)
    broker_dir.mkdir(exist_ok=True)
    root.chmod(0o700)
    control.chmod(0o700)
    broker_dir.chmod(0o700)
    client = control / "broker_client.py"
    client.write_text("# bridge-owned fixture\n", encoding="utf-8")
    client.chmod(0o500)
    socket_path = broker_dir / "verification.sock"
    return tuple(
        shlex.join(
            [
                sys.executable,
                str(client),
                str(socket_path),
                f"{index + 1:064x}",
                "905",
            ]
        )
        for index in range(count)
    )


def _process_tree_command(pid_path: Path, *, parent_waits: bool) -> list[str]:
    descendant_source = "import time; time.sleep(60)"
    parent_source = "\n".join(
        (
            "from pathlib import Path",
            "import subprocess",
            "import sys",
            "import time",
            "descendant = subprocess.Popen([sys.executable, '-c', sys.argv[2]])",
            "Path(sys.argv[1]).write_text(str(descendant.pid), encoding='utf-8')",
            *(('time.sleep(60)',) if parent_waits else ()),
        )
    )
    return [sys.executable, "-c", parent_source, str(pid_path), descendant_source]


def _pid_exists(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    return True


def _wait_for_pid_file(pid_path: Path, *, timeout: float = 5.0) -> int:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if pid_path.is_file() and pid_path.read_text(encoding="utf-8").strip():
            return int(pid_path.read_text(encoding="utf-8"))
        time.sleep(0.02)
    raise AssertionError("descendant pid was not recorded")


def _wait_for_pid_exit(pid: int, *, timeout: float = 5.0) -> bool:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if not _pid_exists(pid):
            return True
        time.sleep(0.02)
    return not _pid_exists(pid)


def _kill_pid_if_alive(pid: int | None) -> None:
    if pid is None or not _pid_exists(pid):
        return
    try:
        os.kill(pid, signal.SIGKILL)
    except ProcessLookupError:
        pass


def _claude_stream(
    *,
    model: str = "claude-opus-4-7",
    structured: dict[str, object] | None = None,
    reviewed_head: str = HEAD,
    reviewed_base: str | None = BASE,
) -> str:
    payload = (
        _structured_payload(
            reviewed_head=reviewed_head,
            reviewed_base=reviewed_base,
        )
        if structured is None
        else structured
    )
    return "\n".join(
        [
            json.dumps({"type": "system", "subtype": "init", "model": model}),
            json.dumps(
                {
                    "type": "result",
                    "subtype": "success",
                    "structured_output": payload,
                }
            ),
        ]
    )


def _captured_process(
    argv: list[str],
    returncode: int,
    stdout: str | bytes,
    stderr: str | bytes,
    *,
    stdout_truncated: bool = False,
    stderr_truncated: bool = False,
) -> bridge.CapturedProcess:
    return bridge.CapturedProcess(
        args=tuple(argv),
        returncode=returncode,
        stdout=stdout.encode("utf-8") if isinstance(stdout, str) else stdout,
        stderr=stderr.encode("utf-8") if isinstance(stderr, str) else stderr,
        stdout_truncated=stdout_truncated,
        stderr_truncated=stderr_truncated,
    )


class _PureVerificationBroker:
    def __init__(
        self,
        runtime: bridge.SandboxRuntime,
        snapshot: Path,
        *,
        timeout_seconds: int,
    ) -> None:
        self.runtime = runtime
        self.snapshot = snapshot
        self.timeout_seconds = timeout_seconds
        self.socket_path = runtime.broker_dir / "verification.sock"
        self._counter = 0
        self.closed = False

    def register_verification(self, command: str) -> str:
        del command
        self._counter += 1
        return shlex.join(
            [
                sys.executable,
                str(self.runtime.broker_client),
                str(self.socket_path),
                f"{self._counter:064x}",
                str(self.timeout_seconds + 5),
            ]
        )

    def close(self) -> None:
        self.closed = True

    def __enter__(self) -> _PureVerificationBroker:
        return self

    def __exit__(self, *exc_info: object) -> None:
        self.close()


def _pure_review(
    request: bridge.ReviewRequest,
    *,
    runner: object,
    resolver: object | None = None,
    sandbox_probe: object | None = None,
) -> bridge.OpusReview:
    def captured_runner(
        argv: list[str], **kwargs: object
    ) -> bridge.CapturedProcess:
        completed = runner(argv, **kwargs)
        if isinstance(completed, bridge.CapturedProcess):
            return completed
        assert isinstance(completed, subprocess.CompletedProcess)
        return _captured_process(
            argv,
            completed.returncode,
            completed.stdout,
            completed.stderr,
        )

    return bridge.review(
        request,
        resolver=(
            (lambda environment: Path(sys.executable))
            if resolver is None
            else resolver
        ),
        runtime_factory=bridge._sandbox_runtime,
        broker_factory=_PureVerificationBroker,
        sandbox_probe=(
            (lambda runtime, snapshot, broker: True)
            if sandbox_probe is None
            else sandbox_probe
        ),
        runner=captured_runner,
    )


def test_review_request_has_no_codex_result_channel(tmp_path: Path) -> None:
    request = _request(tmp_path)
    prompt = bridge.build_review_prompt(request)

    assert "codex_verdict" not in inspect.signature(bridge.ReviewRequest).parameters
    assert "codex_report" not in inspect.signature(bridge.ReviewRequest).parameters
    assert "codex_findings" not in inspect.signature(bridge.ReviewRequest).parameters
    assert "codex_conclusion" not in inspect.signature(bridge.ReviewRequest).parameters
    assert "Do not ask for or infer the Codex verifier's verdict" in prompt
    assert "Authorization source: user-task:verification-1" in prompt
    assert (
        "Review profile: codex-lane-v\n"
        "Authorization source: user-task:verification-1"
    ) in prompt
    assert "Verify the stale-parent guard" not in prompt
    assert "brief.md" in prompt


def test_build_review_prompt_rejects_invalid_authorization_source(
    tmp_path: Path,
) -> None:
    with pytest.raises(bridge.ReviewContractError) as excinfo:
        bridge.build_review_prompt(_request(tmp_path, authorization="yes"))

    assert excinfo.value.reason == "invalid_authorization"


def test_build_claude_command_is_bounded_and_read_only(tmp_path: Path) -> None:
    request = _request(tmp_path)
    argv = bridge.build_claude_command(
        request,
        agent_prompt="PINNED-PRE-HEAD-VERIFIER",
        verification_commands=_broker_client_commands(tmp_path, 1),
    )
    rendered = " ".join(argv)
    allowed_rules = argv[argv.index("--allowedTools") + 1 :]

    assert argv[:2] == ["claude", "-p"]
    assert "--safe-mode" in argv
    assert "--disable-slash-commands" in argv
    assert "--bare" not in argv
    assert "--agents" not in argv
    assert "--agent" not in argv
    assert argv[argv.index("--append-system-prompt") + 1] == (
        "PINNED-PRE-HEAD-VERIFIER"
    )
    assert argv[argv.index("--max-turns") + 1] == "12"
    assert "--model opus" in rendered
    assert "--output-format stream-json" in rendered
    assert "--verbose" in argv
    assert "--no-session-persistence" in argv
    assert argv[argv.index("--setting-sources") + 1] == ""
    assert "--strict-mcp-config" in argv
    assert json.loads(argv[argv.index("--mcp-config") + 1]) == {"mcpServers": {}}
    assert "--permission-mode dontAsk" in rendered
    assert "Edit,Write,NotebookEdit,Agent,Skill,WebFetch,WebSearch" in argv
    assert any(
        f"{request.reviewed_base}..{request.reviewed_head}" in rule
        for rule in allowed_rules
    )
    assert all("*" not in rule for rule in allowed_rules)
    assert any("broker_client.py" in rule for rule in allowed_rules)
    assert not any("-m pytest" in rule for rule in allowed_rules)


@pytest.mark.parametrize("reviewed_base", [BASE, None], ids=["range", "single-commit"])
def test_review_patch_commands_disable_external_diff_and_textconv(
    tmp_path: Path,
    reviewed_base: str | None,
) -> None:
    request = replace(_request(tmp_path), reviewed_base=reviewed_base)
    patch_commands = []
    for command in bridge._review_git_commands(request):
        argv = shlex.split(command)
        git_subcommand = argv[argv.index("git") + 1]
        if git_subcommand in {"diff", "show"} and "--" in argv:
            patch_commands.append(argv)

    assert patch_commands
    for argv in patch_commands:
        assert "--no-ext-diff" in argv
        assert "--no-textconv" in argv


def test_build_claude_command_requires_brokered_verification_rules(
    tmp_path: Path,
) -> None:
    request = _request(tmp_path)

    with pytest.raises(TypeError):
        bridge.build_claude_command(request, agent_prompt="PINNED")

    with pytest.raises(bridge.ReviewContractError) as excinfo:
        bridge.build_claude_command(
            request,
            agent_prompt="PINNED",
            verification_commands=request.verification_commands,
        )

    assert excinfo.value.reason == "invalid_command"


@pytest.mark.parametrize(
    "receive_timeout",
    ["", "5", "05", "5.0", "+6", "906"],
    ids=["empty", "below-minimum", "leading-zero", "decimal", "sign", "too-large"],
)
def test_build_claude_command_rejects_invalid_broker_receive_timeout(
    tmp_path: Path,
    receive_timeout: str,
) -> None:
    request = _request(tmp_path)
    command = shlex.split(_broker_client_commands(tmp_path, 1)[0])
    command[-1] = receive_timeout

    with pytest.raises(bridge.ReviewContractError) as excinfo:
        bridge.build_claude_command(
            request,
            agent_prompt="PINNED",
            verification_commands=(shlex.join(command),),
        )

    assert excinfo.value.reason == "invalid_command"


@pytest.mark.parametrize(
    "command",
    [
        "rm -rf scratch",
        "env -u GIT_INDEX_FILE git reset --hard HEAD",
        "curl https://example.com/review",
        "claude -p run-another-provider",
        "sh verify.sh",
        "env -u GIT_INDEX_FILE .venv/bin/python scripts/send_event.py",
        "env -u GIT_INDEX_FILE arbitrary-verifier --check",
        "env -u GIT_INDEX_FILE .venv/bin/python -m pytest /tmp/evil_test.py -q",
        "env -u GIT_INDEX_FILE .venv/bin/python -m pytest -p evil_plugin tests/unit/test_route_lineage.py",
        "env -u GIT_INDEX_FILE .venv/bin/python -m pytest -c /tmp/pytest.ini tests/unit/test_route_lineage.py",
        "env -u GIT_INDEX_FILE .venv/bin/python -m pytest",
    ],
)
def test_review_rejects_mutating_network_provider_or_arbitrary_commands(
    tmp_path: Path, command: str
) -> None:
    request = replace(_request(tmp_path), verification_commands=(command,))

    with pytest.raises(bridge.ReviewContractError) as excinfo:
        bridge.build_claude_command(
            request,
            agent_prompt="PINNED",
            verification_commands=_broker_client_commands(tmp_path, 1),
        )

    assert excinfo.value.reason == "invalid_command"


def test_review_accepts_only_narrow_pipeline_verification_shapes(
    tmp_path: Path,
) -> None:
    request = replace(
        _request(tmp_path),
        verification_commands=(
            "env -u GIT_INDEX_FILE .venv/bin/python -m pytest "
            "tests/unit/test_route_lineage.py -q",
            "env -u GIT_INDEX_FILE .venv/bin/python scripts/ci_smoke.py",
        ),
    )

    argv = bridge.build_claude_command(
        request,
        agent_prompt="PINNED",
        verification_commands=_broker_client_commands(tmp_path, 2),
    )
    allowed_rules = argv[argv.index("--allowedTools") + 1 :]

    assert sum("broker_client.py" in rule for rule in allowed_rules) == 2


def test_review_runs_in_immutable_head_snapshot_with_trusted_base_agent(
    tmp_path: Path,
) -> None:
    request = _committed_request(tmp_path)
    snapshot_paths: list[Path] = []

    def fake_runner(argv: list[str], **kwargs: object) -> bridge.CapturedProcess:
        snapshot = Path(str(kwargs["cwd"]))
        snapshot_paths.append(snapshot)
        assert argv[0] == "/usr/bin/sandbox-exec"
        assert snapshot != tmp_path.resolve()
        assert _git(snapshot, "rev-parse", "HEAD") == request.reviewed_head
        assert (snapshot / "brief.md").read_text(encoding="utf-8") == "head requirement\n"
        assert (
            snapshot / "scripts" / "route_lineage.py"
        ).read_text(encoding="utf-8") == "STATE = 'reviewed-head'\n"
        assert not (
            (snapshot / "scripts" / "route_lineage.py").stat().st_mode
            & stat.S_IWUSR
        )
        assert (snapshot / ".venv" / "bin" / "python").resolve() == Path(
            sys.executable
        ).resolve()
        verifier_prompt = argv[argv.index("--append-system-prompt") + 1]
        assert "BASE-TRUSTED-AGENT" in verifier_prompt
        assert "HEAD-UNTRUSTED-AGENT" not in verifier_prompt
        assert "MUTABLE-WIP-AGENT" not in verifier_prompt
        return _captured_process(
            argv,
            0,
            _claude_stream(
                reviewed_head=request.reviewed_head,
                reviewed_base=request.reviewed_base,
            ),
            "",
        )

    result = _pure_review(request, runner=fake_runner)

    assert result.status == "pass"
    assert snapshot_paths and not snapshot_paths[0].exists()
    assert (tmp_path / "brief.md").read_text(encoding="utf-8") == "mutable WIP requirement\n"


def test_review_without_explicit_base_uses_first_parent_verifier_prompt(
    tmp_path: Path,
) -> None:
    request = replace(_committed_request(tmp_path), reviewed_base=None)

    def fake_runner(argv: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        if "--append-system-prompt" in argv:
            verifier_prompt = argv[argv.index("--append-system-prompt") + 1]
        else:
            agents = json.loads(argv[argv.index("--agents") + 1])
            verifier_prompt = agents["lane-v-verifier"]["prompt"]
        assert "BASE-TRUSTED-AGENT" in verifier_prompt
        assert "HEAD-UNTRUSTED-AGENT" not in verifier_prompt
        return subprocess.CompletedProcess(
            argv,
            0,
            _claude_stream(
                reviewed_head=request.reviewed_head,
                reviewed_base=None,
            ),
            "",
        )

    result = _pure_review(request, runner=fake_runner)

    assert result.status == "pass"


def test_review_rejects_explicit_base_that_does_not_precede_head(
    tmp_path: Path,
) -> None:
    request = replace(_committed_request(tmp_path), authorization_source="")
    request = replace(request, reviewed_base=request.reviewed_head)

    def forbidden_runner(*args: object, **kwargs: object) -> subprocess.CompletedProcess[str]:
        raise AssertionError("provider must not run with a non-preceding prompt base")

    with pytest.raises(bridge.ReviewContractError) as excinfo:
        _pure_review(request, runner=forbidden_runner)

    assert excinfo.value.reason == "invalid_scope"


@pytest.mark.parametrize("field", ["reviewed_head", "reviewed_base"])
def test_review_proves_revisions_exist_before_provider_call(
    tmp_path: Path, field: str
) -> None:
    request = replace(_committed_request(tmp_path), **{field: "f" * 40})

    def forbidden_runner(*args: object, **kwargs: object) -> subprocess.CompletedProcess[str]:
        raise AssertionError("Claude must not run for a missing reviewed commit")

    with pytest.raises(bridge.ReviewContractError) as excinfo:
        _pure_review(request, runner=forbidden_runner)

    assert excinfo.value.reason == "invalid_scope"


def test_standing_authorization_requires_existing_reviewed_commits(
    tmp_path: Path,
) -> None:
    request = replace(
        _committed_request(tmp_path),
        authorization_source="",
        reviewed_head="f" * 40,
    )

    calls = 0

    def forbidden_runner(*args: object, **kwargs: object) -> object:
        nonlocal calls
        calls += 1
        raise AssertionError("provider must not run before commit scope proof")

    with pytest.raises(bridge.ReviewContractError) as excinfo:
        _pure_review(request, runner=forbidden_runner)

    assert excinfo.value.reason == "invalid_scope"
    assert calls == 0


def test_standing_authorization_requires_pipeline_identity(
    tmp_path: Path,
) -> None:
    request = replace(_committed_request(tmp_path), authorization_source="")
    (tmp_path / "AGENTS.md").unlink()

    calls = 0

    def forbidden_runner(*args: object, **kwargs: object) -> object:
        nonlocal calls
        calls += 1
        raise AssertionError("provider must not run before Pipeline identity proof")

    with pytest.raises(bridge.ReviewContractError) as excinfo:
        _pure_review(request, runner=forbidden_runner)

    assert excinfo.value.reason == "not_pipeline_repo"
    assert calls == 0


def test_standing_authorization_requires_requirement_at_reviewed_head(
    tmp_path: Path,
) -> None:
    request = _committed_request(tmp_path)
    late_requirement = tmp_path / "late-requirement.md"
    late_requirement.write_text("mutable only\n", encoding="utf-8")
    request = replace(
        request,
        requirement_paths=(late_requirement,),
        authorization_source="",
    )
    calls = 0

    def forbidden_runner(*args: object, **kwargs: object) -> object:
        nonlocal calls
        calls += 1
        raise AssertionError("provider must not run before snapshot scope proof")

    with pytest.raises(bridge.ReviewContractError) as excinfo:
        _pure_review(request, runner=forbidden_runner)

    assert excinfo.value.reason == "invalid_scope"
    assert calls == 0


def _run_sandbox_probe(
    request: bridge.ReviewRequest,
    *,
    expect_success: bool,
) -> subprocess.CompletedProcess[str]:
    observed: list[subprocess.CompletedProcess[str]] = []

    def fake_runner(argv: list[str], **kwargs: object) -> bridge.CapturedProcess:
        verification_argv = _verification_command_from_provider_argv(argv)
        _assert_broker_client_command(
            verification_argv, expected_command_timeout=request.timeout_seconds
        )
        completed = subprocess.run(
            verification_argv,
            cwd=str(kwargs["cwd"]),
            env=kwargs["env"],
            capture_output=True,
            text=True,
            check=False,
        )
        observed.append(completed)
        if expect_success:
            assert completed.returncode == 0, completed.stdout + completed.stderr
        else:
            assert completed.returncode != 0
            assert "Operation not permitted" in completed.stdout + completed.stderr
        return _captured_process(
            argv,
            0,
            _claude_stream(
                reviewed_head=request.reviewed_head,
                reviewed_base=request.reviewed_base,
            ),
            "",
        )

    result = bridge.review(request, runner=fake_runner)
    assert result.status == "pass"
    assert len(observed) == 1
    return observed[0]


@pytest.mark.parametrize("layout", ["normal-checkout", "linked-worktree"])
def test_sandbox_probe_allows_trusted_venv_inside_source_but_denies_source_reads(
    tmp_path: Path,
    layout: str,
    host_capabilities: bridge.HostCapabilities,
) -> None:
    _require_host_capabilities(host_capabilities, "seatbelt", "af_unix")
    trusted_venv = Path(sys.executable).parent.parent.resolve()
    if layout == "normal-checkout":
        source = Path(sys.executable).parent.parent.parent.resolve()
        source_marker = source / "AGENTS.md"
        assert trusted_venv.is_relative_to(source)
    else:
        source = tmp_path / "linked-source"
        source.mkdir()
        source_marker = source / "mutable-source.txt"
        source_marker.write_text("mutable\n", encoding="utf-8")
        assert not trusted_venv.is_relative_to(source)

    snapshot = tmp_path / "snapshot"
    snapshot.mkdir()
    (snapshot / ".venv").symlink_to(trusted_venv, target_is_directory=True)
    read_source = (
        "from pathlib import Path; "
        f"Path({str(source_marker)!r}).read_text(encoding='utf-8')"
    )

    with bridge._sandbox_runtime(source, snapshot) as runtime:
        with bridge._VerificationBroker(
            runtime, snapshot, timeout_seconds=10
        ) as broker:
            assert bridge._probe_sandbox_profiles(runtime, snapshot, broker)

            broker_client = broker.register(
                bridge._sandboxed_verification_argv(
                    "env -u GIT_INDEX_FILE "
                    f"{shlex.quote(sys.executable)} -c {shlex.quote(read_source)}",
                    runtime,
                )
            )
            inner_read = subprocess.run(
                broker_client,
                cwd=snapshot,
                env={
                    **bridge.build_claude_environment(),
                    "TMPDIR": str(runtime.provider_scratch),
                },
                capture_output=True,
                text=True,
                check=False,
            )
            outer_read = subprocess.run(
                [
                    str(bridge.SANDBOX_EXECUTABLE),
                    "-f",
                    str(runtime.outer_profile),
                    sys.executable,
                    "-c",
                    read_source,
                ],
                cwd=snapshot,
                env=bridge.build_claude_environment(),
                capture_output=True,
                text=True,
                check=False,
            )

    for completed in (inner_read, outer_read):
        assert completed.returncode != 0
        assert "Operation not permitted" in completed.stdout + completed.stderr


@pytest.mark.parametrize(
    ("parent_waits", "expected_returncode"),
    [(False, 0), (True, 124)],
    ids=["normal-parent-exit", "timeout"],
)
def test_verification_broker_reaps_entire_process_group(
    tmp_path: Path,
    parent_waits: bool,
    expected_returncode: int,
    host_capabilities: bridge.HostCapabilities,
) -> None:
    _require_host_capabilities(host_capabilities, "af_unix")
    source = tmp_path / "source"
    snapshot = tmp_path / "snapshot"
    source.mkdir()
    snapshot.mkdir()
    pid_path = tmp_path / "descendant.pid"
    descendant_pid: int | None = None

    try:
        with bridge._sandbox_runtime(source, snapshot) as runtime:
            with bridge._VerificationBroker(
                runtime, snapshot, timeout_seconds=1
            ) as broker:
                client = broker.register(
                    _process_tree_command(pid_path, parent_waits=parent_waits)
                )
                completed = subprocess.run(
                    client,
                    cwd=snapshot,
                    capture_output=True,
                    text=True,
                    check=False,
                    timeout=5,
                )
            descendant_pid = _wait_for_pid_file(pid_path)

        assert completed.returncode == expected_returncode
        assert _wait_for_pid_exit(descendant_pid)
    finally:
        _kill_pid_if_alive(descendant_pid)


def test_verification_broker_context_shutdown_reaps_active_process_group(
    tmp_path: Path,
    host_capabilities: bridge.HostCapabilities,
) -> None:
    _require_host_capabilities(host_capabilities, "af_unix")
    source = tmp_path / "source"
    snapshot = tmp_path / "snapshot"
    source.mkdir()
    snapshot.mkdir()
    pid_path = tmp_path / "descendant.pid"
    descendant_pid: int | None = None
    completed: list[subprocess.CompletedProcess[str]] = []

    try:
        with bridge._sandbox_runtime(source, snapshot) as runtime:
            broker = bridge._VerificationBroker(
                runtime, snapshot, timeout_seconds=30
            )
            closed = False
            try:
                client = broker.register(
                    _process_tree_command(pid_path, parent_waits=True)
                )
                client_thread = threading.Thread(
                    target=lambda: completed.append(
                        subprocess.run(
                            client,
                            cwd=snapshot,
                            capture_output=True,
                            text=True,
                            check=False,
                            timeout=10,
                        )
                    )
                )
                client_thread.start()
                descendant_pid = _wait_for_pid_file(pid_path)
                broker.close()
                closed = True
                client_thread.join(timeout=5)
                assert not client_thread.is_alive()
            finally:
                if not closed:
                    broker.close()

        assert completed
        assert _wait_for_pid_exit(descendant_pid)
    finally:
        _kill_pid_if_alive(descendant_pid)


@pytest.mark.parametrize(
    "parent_waits", [False, True], ids=["normal-parent-exit", "timeout"]
)
def test_provider_process_group_runner_reaps_descendants(
    tmp_path: Path,
    parent_waits: bool,
) -> None:
    pid_path = tmp_path / "descendant.pid"
    command = _process_tree_command(pid_path, parent_waits=parent_waits)
    descendant_pid: int | None = None

    try:
        if parent_waits:
            with pytest.raises(subprocess.TimeoutExpired):
                bridge._run_process_group(
                    command,
                    cwd=str(tmp_path),
                    env=os.environ.copy(),
                    capture_output=True,
                    text=True,
                    check=False,
                    timeout=1,
                )
        else:
            completed = bridge._run_process_group(
                command,
                cwd=str(tmp_path),
                env=os.environ.copy(),
                capture_output=True,
                text=True,
                check=False,
                timeout=5,
            )
            assert completed.returncode == 0
        assert not any(
            thread.name.startswith("opus-provider-drain-") and thread.is_alive()
            for thread in threading.enumerate()
        )
        descendant_pid = _wait_for_pid_file(pid_path)
        assert _wait_for_pid_exit(descendant_pid)
    finally:
        _kill_pid_if_alive(descendant_pid)


def _simultaneous_stream_command(
    *, stdout_size: int, stderr_size: int, returncode: int = 0
) -> list[str]:
    source = "\n".join(
        (
            "import os",
            "import sys",
            "import threading",
            "barrier = threading.Barrier(3)",
            "def emit(fd, byte, size):",
            "    barrier.wait()",
            "    remaining = size",
            "    chunk = byte * 8192",
            "    while remaining:",
            "        written = os.write(fd, chunk[:remaining])",
            "        remaining -= written",
            "threads = [",
            "    threading.Thread(target=emit, args=(1, b'O', int(sys.argv[1]))),",
            "    threading.Thread(target=emit, args=(2, b'E', int(sys.argv[2]))),",
            "]",
            "for thread in threads: thread.start()",
            "barrier.wait()",
            "for thread in threads: thread.join()",
            "raise SystemExit(int(sys.argv[3]))",
        )
    )
    return [
        sys.executable,
        "-c",
        source,
        str(stdout_size),
        str(stderr_size),
        str(returncode),
    ]


@pytest.mark.parametrize(
    ("stdout_size", "stderr_size", "stdout_truncated", "stderr_truncated"),
    [
        (EXPECTED_PROVIDER_OUTPUT_LIMIT_BYTES + 4096, 17, True, False),
        (19, EXPECTED_PROVIDER_OUTPUT_LIMIT_BYTES + 4096, False, True),
        (
            EXPECTED_PROVIDER_OUTPUT_LIMIT_BYTES + 4096,
            EXPECTED_PROVIDER_OUTPUT_LIMIT_BYTES + 8192,
            True,
            True,
        ),
    ],
    ids=["stdout", "stderr", "both"],
)
def test_provider_process_group_runner_bounds_and_drains_concurrent_streams(
    tmp_path: Path,
    stdout_size: int,
    stderr_size: int,
    stdout_truncated: bool,
    stderr_truncated: bool,
) -> None:
    assert getattr(bridge, "PROVIDER_OUTPUT_LIMIT_BYTES", None) == (
        EXPECTED_PROVIDER_OUTPUT_LIMIT_BYTES
    )
    command = _simultaneous_stream_command(
        stdout_size=stdout_size,
        stderr_size=stderr_size,
    )

    completed = bridge._run_process_group(
        command,
        cwd=str(tmp_path),
        env=os.environ.copy(),
        capture_output=True,
        text=True,
        check=False,
        timeout=5,
    )

    assert isinstance(completed, bridge.CapturedProcess)
    assert completed.args == tuple(command)
    assert completed.returncode == 0
    assert completed.stdout == b"O" * min(
        stdout_size, EXPECTED_PROVIDER_OUTPUT_LIMIT_BYTES
    )
    assert completed.stderr == b"E" * min(
        stderr_size, EXPECTED_PROVIDER_OUTPUT_LIMIT_BYTES
    )
    assert completed.stdout_truncated is stdout_truncated
    assert completed.stderr_truncated is stderr_truncated
    assert not any(
        thread.name.startswith("opus-provider-drain-") and thread.is_alive()
        for thread in threading.enumerate()
    )


def test_provider_process_group_runner_preserves_nonzero_exit_after_drain(
    tmp_path: Path,
) -> None:
    command = _simultaneous_stream_command(
        stdout_size=65_537,
        stderr_size=65_539,
        returncode=7,
    )

    completed = bridge._run_process_group(
        command,
        cwd=str(tmp_path),
        env=os.environ.copy(),
        capture_output=True,
        text=True,
        check=False,
        timeout=5,
    )

    assert completed.returncode == 7
    assert completed.stdout == b"O" * 65_537
    assert completed.stderr == b"E" * 65_539
    assert not completed.stdout_truncated
    assert not completed.stderr_truncated


def test_provider_reader_failure_kills_group_and_joins_other_reader(
    tmp_path: Path,
) -> None:
    pid_path = tmp_path / "reader-failure-descendant.pid"
    command = _process_tree_command(pid_path, parent_waits=True)
    call_lock = threading.Lock()
    calls = 0
    descendant_pid: int | None = None

    def injected_reader(stream: object, limit: int) -> tuple[bytes, bool]:
        nonlocal calls
        assert limit == EXPECTED_PROVIDER_OUTPUT_LIMIT_BYTES
        with call_lock:
            calls += 1
            call_number = calls
        if call_number == 1:
            _wait_for_pid_file(pid_path)
            raise RuntimeError("raw reader detail must stay private")
        while stream.read(8192):
            pass
        return b"", False

    try:
        with pytest.raises(OSError, match="provider output capture failed") as excinfo:
            bridge._run_process_group(
                command,
                cwd=str(tmp_path),
                env=os.environ.copy(),
                capture_output=True,
                text=True,
                check=False,
                timeout=10,
                stream_reader=injected_reader,
            )
        assert "raw reader detail" not in str(excinfo.value)
        descendant_pid = _wait_for_pid_file(pid_path)
        assert _wait_for_pid_exit(descendant_pid)
        assert calls == 2
        assert not any(
            thread.name.startswith("opus-provider-drain-") and thread.is_alive()
            for thread in threading.enumerate()
        )
    finally:
        _kill_pid_if_alive(descendant_pid)


class _InjectedDrainThread:
    def __init__(
        self,
        *,
        target: object,
        args: tuple[str, object],
        name: str,
        fail_start: bool,
        pid_path: Path,
    ) -> None:
        self.stream = args[1]
        self.start_called = False
        self.started = False
        self.joined = False
        self._fail_start = fail_start
        self._pid_path = pid_path
        self._thread = threading.Thread(target=target, args=args, name=name)

    def start(self) -> None:
        self.start_called = True
        if self._fail_start:
            _wait_for_pid_file(self._pid_path)
            raise RuntimeError("raw thread start detail must stay private")
        self._thread.start()
        self.started = True

    def join(self) -> None:
        assert self.started
        self.joined = True
        self._thread.join()

    def is_alive(self) -> bool:
        return self._thread.is_alive()


@pytest.mark.parametrize(
    ("failure_index", "expected_joined"),
    [(0, (False, False)), (1, (True, False))],
    ids=["first-start", "second-start"],
)
def test_provider_reader_start_failure_owns_all_partial_cleanup(
    tmp_path: Path,
    failure_index: int,
    expected_joined: tuple[bool, bool],
) -> None:
    pid_path = tmp_path / f"reader-start-{failure_index}-descendant.pid"
    command = _process_tree_command(pid_path, parent_waits=True)
    created: list[_InjectedDrainThread] = []
    descendant_pid: int | None = None

    def thread_factory(**kwargs: object) -> _InjectedDrainThread:
        args = kwargs["args"]
        assert isinstance(args, tuple)
        reader = _InjectedDrainThread(
            target=kwargs["target"],
            args=args,
            name=str(kwargs["name"]),
            fail_start=len(created) == failure_index,
            pid_path=pid_path,
        )
        created.append(reader)
        return reader

    try:
        with pytest.raises(
            OSError, match=r"^provider output capture failed$"
        ) as excinfo:
            bridge._run_process_group(
                command,
                cwd=str(tmp_path),
                env=os.environ.copy(),
                capture_output=True,
                text=True,
                check=False,
                timeout=10,
                thread_factory=thread_factory,
            )

        assert excinfo.value.args == ("provider output capture failed",)
        assert "raw thread start detail" not in str(excinfo.value)
        assert len(created) == 2
        assert tuple(reader.joined for reader in created) == expected_joined
        assert all(reader.start_called for reader in created[: failure_index + 1])
        assert all(
            not reader.start_called for reader in created[failure_index + 1 :]
        )
        assert len({id(reader.stream) for reader in created}) == 2
        assert all(getattr(reader.stream, "closed") for reader in created)
        assert not any(reader.is_alive() for reader in created)
        assert not any(
            thread.name.startswith("opus-provider-drain-") and thread.is_alive()
            for thread in threading.enumerate()
        )
        descendant_pid = _wait_for_pid_file(pid_path)
        assert _wait_for_pid_exit(descendant_pid)
    finally:
        _kill_pid_if_alive(descendant_pid)


class _CleanupSocket:
    def __init__(self, stage: str) -> None:
        self.stage = stage
        self.closed = False

    def bind(self, path: str) -> None:
        Path(path).write_bytes(b"partial broker socket")
        if self.stage == "bind":
            raise OSError("raw bind detail")

    def listen(self, backlog: int) -> None:
        assert backlog == 4
        if self.stage == "listen":
            raise OSError("raw listen detail")

    def settimeout(self, timeout: float) -> None:
        assert timeout == 0.1

    def close(self) -> None:
        self.closed = True


class _CleanupThread:
    def __init__(self, *, fail_start: bool) -> None:
        self.fail_start = fail_start
        self.started = False
        self.joined = False
        self.alive = False

    def start(self) -> None:
        self.started = True
        self.alive = True
        if self.fail_start:
            raise RuntimeError("raw thread start detail")

    def join(self, timeout: float | None = None) -> None:
        assert timeout in {None, 5}
        self.joined = True
        self.alive = False

    def is_alive(self) -> bool:
        return self.alive


@pytest.mark.parametrize("stage", ["bind", "listen", "thread_start"])
def test_verification_broker_constructor_cleans_every_partial_stage(
    tmp_path: Path,
    stage: str,
) -> None:
    source = tmp_path / "source"
    snapshot = tmp_path / "snapshot"
    source.mkdir()
    snapshot.mkdir()
    listener = _CleanupSocket(stage)
    created_threads: list[_CleanupThread] = []

    def socket_factory(*args: object) -> _CleanupSocket:
        assert args == (socket.AF_UNIX, socket.SOCK_STREAM)
        return listener

    def thread_factory(**kwargs: object) -> _CleanupThread:
        assert kwargs["name"] == "opus-verification-broker"
        assert kwargs["daemon"] is True
        thread = _CleanupThread(fail_start=stage == "thread_start")
        created_threads.append(thread)
        return thread

    with bridge._sandbox_runtime(source, snapshot) as runtime:
        broker = bridge._VerificationBroker.__new__(bridge._VerificationBroker)
        with pytest.raises((OSError, RuntimeError)):
            broker.__init__(
                runtime,
                snapshot,
                timeout_seconds=5,
                socket_factory=socket_factory,
                thread_factory=thread_factory,
            )

        assert listener.closed
        assert not broker.socket_path.exists()
        assert broker._stop.is_set()
        if stage == "thread_start":
            assert created_threads[0].started
            assert created_threads[0].joined
            assert not created_threads[0].is_alive()
        else:
            assert created_threads == []
        broker.close()
        broker.close()


@pytest.mark.parametrize(
    ("seatbelt", "af_unix", "claude_cli", "missing"),
    [
        (True, True, True, ()),
        (False, True, True, ("seatbelt",)),
        (True, False, True, ("af_unix",)),
        (True, True, False, ("claude_cli",)),
        (
            False,
            False,
            False,
            ("seatbelt", "af_unix", "claude_cli"),
        ),
    ],
)
def test_probe_host_capabilities_classifies_exact_missing_names(
    seatbelt: bool,
    af_unix: bool,
    claude_cli: bool,
    missing: tuple[str, ...],
) -> None:
    commands: list[tuple[str, ...]] = []

    def command_probe(argv: tuple[str, ...]) -> bool:
        commands.append(argv)
        return seatbelt

    capabilities = bridge.probe_host_capabilities(
        command_probe=command_probe,
        socket_probe=lambda: af_unix,
        claude_resolver=(
            (lambda environment: Path("/fake/claude"))
            if claude_cli
            else (lambda environment: None)
        ),
    )

    assert capabilities == bridge.HostCapabilities(
        seatbelt=seatbelt,
        af_unix=af_unix,
        claude_cli=claude_cli,
        missing=missing,
    )
    assert commands == [
        (
            "/usr/bin/sandbox-exec",
            "-p",
            "(version 1) (allow default)",
            "/usr/bin/true",
        )
    ]


def test_probe_host_capabilities_fails_closed_without_leaking_probe_errors() -> None:
    def unavailable(*args: object) -> bool:
        raise OSError("raw host probe detail")

    def missing_claude(environment: object) -> Path | None:
        raise OSError("raw resolver detail")

    capabilities = bridge.probe_host_capabilities(
        command_probe=unavailable,
        socket_probe=unavailable,
        claude_resolver=missing_claude,
    )

    assert capabilities.missing == ("seatbelt", "af_unix", "claude_cli")


def test_review_uses_complete_injected_host_seam(tmp_path: Path) -> None:
    request = _request(tmp_path)
    calls: list[str] = []

    def resolver(environment: object) -> Path:
        calls.append("resolver")
        return Path(sys.executable)

    @contextmanager
    def runtime_factory(source: Path, snapshot: Path) -> object:
        calls.append("runtime")
        with bridge._sandbox_runtime(source, snapshot) as runtime:
            yield runtime

    def broker_factory(
        runtime: bridge.SandboxRuntime,
        snapshot: Path,
        *,
        timeout_seconds: int,
    ) -> _PureVerificationBroker:
        calls.append("broker")
        return _PureVerificationBroker(
            runtime,
            snapshot,
            timeout_seconds=timeout_seconds,
        )

    def sandbox_probe(
        runtime: bridge.SandboxRuntime,
        snapshot: Path,
        broker: _PureVerificationBroker,
    ) -> bool:
        calls.append("sandbox_probe")
        return True

    def runner(argv: list[str], **kwargs: object) -> bridge.CapturedProcess:
        calls.append("runner")
        return _captured_process(
            argv,
            0,
            _claude_stream(
                reviewed_head=request.reviewed_head,
                reviewed_base=request.reviewed_base,
            ),
            "",
        )

    result = bridge.review(
        request,
        resolver=resolver,
        runtime_factory=runtime_factory,
        broker_factory=broker_factory,
        sandbox_probe=sandbox_probe,
        runner=runner,
    )

    assert result.status == "pass"
    assert calls == ["resolver", "runtime", "broker", "sandbox_probe", "runner"]


def test_review_gives_truncation_precedence_over_parseable_provider_output(
    tmp_path: Path,
) -> None:
    request = _request(tmp_path)

    def runner(argv: list[str], **kwargs: object) -> bridge.CapturedProcess:
        return _captured_process(
            argv,
            0,
            _claude_stream(
                reviewed_head=request.reviewed_head,
                reviewed_base=request.reviewed_base,
            ),
            b"provider stderr must not escape",
            stdout_truncated=True,
            stderr_truncated=False,
        )

    result = _pure_review(request, runner=runner)

    assert result.status == "unavailable"
    assert result.unavailable_reason == "output_limit"
    serialized = json.dumps(result.to_dict(), sort_keys=True)
    assert "provider stderr" not in serialized


def test_provider_failure_stages_are_exact() -> None:
    assert bridge.PROVIDER_FAILURE_STAGES == frozenset(
        {
            "broker_start",
            "sandbox_probe",
            "provider_spawn",
            "provider_timeout",
            "provider_exit",
            "response_parse",
            "contract_validation",
            "model_validation",
            "receipt_recovery",
        }
    )


def test_verification_broker_silent_peer_cannot_block_shutdown(
    tmp_path: Path,
    host_capabilities: bridge.HostCapabilities,
) -> None:
    _require_host_capabilities(host_capabilities, "af_unix")
    source = tmp_path / "source"
    snapshot = tmp_path / "snapshot"
    source.mkdir()
    snapshot.mkdir()

    with bridge._sandbox_runtime(source, snapshot) as runtime:
        broker = bridge._VerificationBroker(runtime, snapshot, timeout_seconds=5)
        peer = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        peer.connect(str(broker.socket_path))
        time.sleep(0.2)
        closed = False
        started = time.monotonic()
        try:
            broker.close()
            closed = True
        finally:
            peer.close()
            if not closed:
                broker.close()

    assert time.monotonic() - started < 2
    assert bridge.BROKER_SOCKET_TIMEOUT_SECONDS == 0.5
    assert "sock.settimeout(" in bridge.BROKER_CLIENT_SOURCE


def test_verification_broker_client_waits_for_admitted_long_command(
    tmp_path: Path,
    host_capabilities: bridge.HostCapabilities,
) -> None:
    _require_host_capabilities(host_capabilities, "af_unix")
    source = tmp_path / "source"
    snapshot = tmp_path / "snapshot"
    source.mkdir()
    snapshot.mkdir()

    with bridge._sandbox_runtime(source, snapshot) as runtime:
        with bridge._VerificationBroker(
            runtime, snapshot, timeout_seconds=7
        ) as broker:
            client = broker.register(
                [
                    sys.executable,
                    "-c",
                    "import time; time.sleep(5.25); print('completed')",
                ]
            )
            completed = subprocess.run(
                client,
                cwd=snapshot,
                capture_output=True,
                text=True,
                check=False,
                timeout=10,
            )
            assert completed.returncode == 0, completed.stdout + completed.stderr
            _assert_broker_client_command(
                client, expected_command_timeout=broker.timeout_seconds
            )

    assert completed.stdout.strip() == "completed"


@pytest.mark.parametrize(
    "receive_timeout",
    ["", "5", "05", "5.0", "+6", "906"],
    ids=["empty", "below-minimum", "leading-zero", "decimal", "sign", "too-large"],
)
def test_generated_broker_client_rejects_noncanonical_receive_timeout(
    tmp_path: Path,
    receive_timeout: str,
) -> None:
    source = tmp_path / "source"
    snapshot = tmp_path / "snapshot"
    source.mkdir()
    snapshot.mkdir()

    with bridge._sandbox_runtime(source, snapshot) as runtime:
        completed = subprocess.run(
            [
                sys.executable,
                str(runtime.broker_client),
                str(runtime.broker_dir / "missing.sock"),
                "0" * 64,
                receive_timeout,
            ],
            capture_output=True,
            text=True,
            check=False,
            timeout=2,
        )

    assert completed.returncode == 125
    assert completed.stderr.strip() == "broker request rejected"


def test_nested_sandbox_runs_admitted_safe_verification(
    tmp_path: Path,
    host_capabilities: bridge.HostCapabilities,
) -> None:
    _require_host_capabilities(host_capabilities, "seatbelt", "af_unix")
    request = _sandbox_probe_request(
        tmp_path,
        "def test_safe_verifier(tmp_path):\n"
        "    artifact = tmp_path / 'proof.txt'\n"
        "    artifact.write_text('safe', encoding='utf-8')\n"
        "    assert artifact.read_text(encoding='utf-8') == 'safe'\n",
    )

    completed = _run_sandbox_probe(request, expect_success=True)

    assert "1 passed" in completed.stdout


@pytest.mark.parametrize(
    ("test_source", "required_capabilities"),
    [
        pytest.param(
            "from pathlib import Path\n"
            "def test_source_write_is_denied():\n"
            "    Path(%r).write_text('escaped', encoding='utf-8')\n"
            % str(Path("SOURCE_TARGET")),
            ("seatbelt", "af_unix"),
            id="source-write",
        ),
        pytest.param(
            "import os\n"
            "def test_snapshot_chmod_is_denied():\n"
            "    os.chmod('scripts/route_lineage.py', 0o777)\n",
            ("seatbelt", "af_unix"),
            id="snapshot-chmod",
        ),
        pytest.param(
            "import socket\n"
            "def test_socket_connect_is_denied():\n"
            "    socket.create_connection(('127.0.0.1', 9), timeout=0.1)\n",
            ("seatbelt", "af_unix"),
            id="socket",
        ),
        pytest.param(
            "from pathlib import Path\n"
            "def test_source_read_is_denied():\n"
            "    Path(%r).read_text(encoding='utf-8')\n"
            % str(Path("SOURCE_READ_TARGET")),
            ("seatbelt", "af_unix"),
            id="source-read",
        ),
        pytest.param(
            "from pathlib import Path\n"
            "def test_sensitive_read_is_denied():\n"
            "    Path(%r).read_text(encoding='utf-8')\n"
            % str(Path.home() / ".claude" / "settings.json"),
            ("seatbelt", "af_unix"),
            id="sensitive-read",
        ),
        pytest.param(
            "import subprocess\n"
            "def test_claude_launch_is_denied():\n"
            "    subprocess.run([CLAUDE_EXECUTABLE, '--version'], check=True)\n",
            ("seatbelt", "af_unix", "claude_cli"),
            id="claude-launch",
        ),
    ],
)
def test_nested_sandbox_denies_adversarial_verifier_actions(
    tmp_path: Path,
    test_source: str,
    required_capabilities: tuple[str, ...],
    host_capabilities: bridge.HostCapabilities,
) -> None:
    _require_host_capabilities(host_capabilities, *required_capabilities)
    if "CLAUDE_EXECUTABLE" in test_source:
        claude_executable = bridge._resolve_claude_executable(
            bridge.build_claude_environment()
        )
        assert claude_executable is not None
        test_source = test_source.replace(
            "CLAUDE_EXECUTABLE", repr(str(claude_executable))
        )
    source_target = tmp_path / "scripts" / "route_lineage.py"
    source_read_target = tmp_path / "AGENTS.md"
    test_source = test_source.replace("SOURCE_TARGET", str(source_target)).replace(
        "SOURCE_READ_TARGET", str(source_read_target)
    )
    request = _sandbox_probe_request(tmp_path, test_source)
    before = source_target.read_text(encoding="utf-8")

    _run_sandbox_probe(request, expect_success=False)

    assert source_target.read_text(encoding="utf-8") == before


@pytest.mark.parametrize("attack", ["replay", "forged-token"])
def test_verification_broker_rejects_replay_and_forged_tokens(
    tmp_path: Path,
    attack: str,
    host_capabilities: bridge.HostCapabilities,
) -> None:
    _require_host_capabilities(host_capabilities, "seatbelt", "af_unix")
    request = _sandbox_probe_request(
        tmp_path,
        "def test_safe_verifier():\n    assert True\n",
    )

    def fake_runner(argv: list[str], **kwargs: object) -> bridge.CapturedProcess:
        verification_argv = _verification_command_from_provider_argv(argv)
        _assert_broker_client_command(
            verification_argv, expected_command_timeout=request.timeout_seconds
        )
        first = subprocess.run(
            verification_argv,
            cwd=str(kwargs["cwd"]),
            env=kwargs["env"],
            capture_output=True,
            text=True,
            check=False,
        )
        assert first.returncode == 0, first.stdout + first.stderr
        attacked_argv = list(verification_argv)
        if attack == "forged-token":
            attacked_argv[-2] = "0" * 64
        rejected = subprocess.run(
            attacked_argv,
            cwd=str(kwargs["cwd"]),
            env=kwargs["env"],
            capture_output=True,
            text=True,
            check=False,
        )
        assert rejected.returncode != 0
        assert "rejected" in (rejected.stdout + rejected.stderr).lower()
        return _captured_process(
            argv,
            0,
            _claude_stream(
                reviewed_head=request.reviewed_head,
                reviewed_base=request.reviewed_base,
            ),
            "",
        )

    result = bridge.review(request, runner=fake_runner)

    assert result.status == "pass"


@pytest.mark.parametrize(
    ("test_source", "timeout_seconds", "diagnostic"),
    [
        (
            "def test_output_is_bounded():\n"
            "    print('x' * 1000000)\n"
            "    assert False\n",
            10,
            "output limit",
        ),
        (
            "import time\ndef test_timeout_is_bounded():\n    time.sleep(5)\n",
            1,
            "timed out",
        ),
    ],
    ids=["output", "timeout"],
)
def test_verification_broker_bounds_output_and_runtime(
    tmp_path: Path,
    test_source: str,
    timeout_seconds: int,
    diagnostic: str,
    host_capabilities: bridge.HostCapabilities,
) -> None:
    _require_host_capabilities(host_capabilities, "seatbelt", "af_unix")
    request = replace(
        _sandbox_probe_request(tmp_path, test_source),
        timeout_seconds=timeout_seconds,
    )

    def fake_runner(argv: list[str], **kwargs: object) -> bridge.CapturedProcess:
        verification_argv = _verification_command_from_provider_argv(argv)
        _assert_broker_client_command(
            verification_argv, expected_command_timeout=timeout_seconds
        )
        completed = subprocess.run(
            verification_argv,
            cwd=str(kwargs["cwd"]),
            env=kwargs["env"],
            capture_output=True,
            text=True,
            check=False,
            timeout=timeout_seconds + 5,
        )
        output = completed.stdout + completed.stderr
        assert completed.returncode != 0
        assert diagnostic in output.lower()
        assert len(output) < 300000
        return _captured_process(
            argv,
            0,
            _claude_stream(
                reviewed_head=request.reviewed_head,
                reviewed_base=request.reviewed_base,
            ),
            "",
        )

    result = bridge.review(request, runner=fake_runner)

    assert result.status == "pass"


def test_review_normalizes_missing_sandbox_without_provider_call(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def forbidden_runner(*args: object, **kwargs: object) -> subprocess.CompletedProcess[str]:
        raise AssertionError("provider must not run without the required sandbox")

    monkeypatch.setattr(
        bridge, "SANDBOX_EXECUTABLE", tmp_path / "missing-sandbox-exec"
    )
    result = bridge.review(
        _committed_request(tmp_path),
        resolver=lambda environment: Path(sys.executable),
        runtime_factory=bridge._sandbox_runtime,
        broker_factory=_PureVerificationBroker,
        runner=forbidden_runner,
    )

    assert result.status == "unavailable"
    assert result.unavailable_reason == "sandbox_unavailable"


def test_review_normalizes_sandbox_profile_failure_without_provider_call(
    tmp_path: Path,
) -> None:
    def forbidden_runner(*args: object, **kwargs: object) -> subprocess.CompletedProcess[str]:
        raise AssertionError("provider must not run after sandbox profile failure")

    result = _pure_review(
        _committed_request(tmp_path),
        runner=forbidden_runner,
        sandbox_probe=lambda runtime, snapshot, broker: False,
    )

    assert result.status == "unavailable"
    assert result.unavailable_reason == "sandbox_unavailable"


def test_review_invokes_claude_once_and_uses_init_model(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    calls: list[tuple[list[str], dict[str, object]]] = []
    monkeypatch.setenv("PIPELINE_SECRET_SHOULD_NOT_LEAK", "secret")
    request = _request(tmp_path)

    def fake_runner(argv: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        calls.append((argv, kwargs))
        return subprocess.CompletedProcess(
            argv,
            0,
            _claude_stream(
                reviewed_head=request.reviewed_head,
                reviewed_base=request.reviewed_base,
            ),
            "",
        )

    result = _pure_review(request, runner=fake_runner)

    assert result.status == "pass"
    assert result.effective_model == "claude-opus-4-7"
    assert len(calls) == 1
    assert calls[0][1]["timeout"] == 900
    assert calls[0][1]["cwd"] != str(tmp_path.resolve())
    child_env = calls[0][1]["env"]
    assert isinstance(child_env, dict)
    assert "PIPELINE_SECRET_SHOULD_NOT_LEAK" not in child_env
    assert child_env["CLAUDE_CODE_DISABLE_AUTO_MEMORY"] == "1"
    assert child_env["CLAUDE_CODE_DISABLE_BACKGROUND_TASKS"] == "1"
    assert child_env["CLAUDE_CODE_MAX_RETRIES"] == "0"
    assert child_env["CLAUDE_CODE_SUBPROCESS_ENV_SCRUB"] == "1"
    assert child_env["CLAUDE_CODE_SKIP_PROMPT_HISTORY"] == "1"
    assert child_env["MAX_STRUCTURED_OUTPUT_RETRIES"] == "0"


def test_review_canonicalizes_uppercase_scope_before_provider_call(
    tmp_path: Path,
) -> None:
    original = _request(tmp_path)
    request = replace(
        original,
        reviewed_head=original.reviewed_head.upper(),
        reviewed_base=original.reviewed_base.upper() if original.reviewed_base else None,
    )
    calls = 0

    def fake_runner(argv: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        nonlocal calls
        calls += 1
        prompt = argv[argv.index("-p") + 1]
        assert f"Reviewed HEAD: {original.reviewed_head}" in prompt
        assert f"Reviewed base: {original.reviewed_base}" in prompt
        assert original.reviewed_head.upper() not in prompt
        return subprocess.CompletedProcess(
            argv,
            0,
            _claude_stream(
                reviewed_head=original.reviewed_head,
                reviewed_base=original.reviewed_base,
            ),
            "",
        )

    result = _pure_review(request, runner=fake_runner)

    assert calls == 1
    assert result.status == "pass"
    assert result.reviewed_head == original.reviewed_head
    assert result.reviewed_base == original.reviewed_base


def test_missing_authorization_uses_standing_policy_and_invokes_once(
    tmp_path: Path,
) -> None:
    request = _request(tmp_path, authorization="")
    calls = 0

    def fake_runner(
        argv: list[str], **kwargs: object
    ) -> subprocess.CompletedProcess[str]:
        nonlocal calls
        calls += 1
        return subprocess.CompletedProcess(
            argv,
            0,
            _claude_stream(
                reviewed_head=request.reviewed_head,
                reviewed_base=request.reviewed_base,
            ),
            "",
        )

    result = _pure_review(request, runner=fake_runner)

    assert calls == 1
    assert result.status == "pass"
    assert result.review_profile == "codex-lane-v"
    assert result.authorization_source == (
        "standing-policy:codex-lane-v-opus-v1"
    )


def test_whitespace_authorization_uses_standing_policy(
    tmp_path: Path,
) -> None:
    request = _request(tmp_path, authorization=" \t ")
    calls = 0

    def fake_runner(
        argv: list[str], **kwargs: object
    ) -> subprocess.CompletedProcess[str]:
        nonlocal calls
        calls += 1
        return subprocess.CompletedProcess(
            argv,
            0,
            _claude_stream(
                reviewed_head=request.reviewed_head,
                reviewed_base=request.reviewed_base,
            ),
            "",
        )

    result = _pure_review(request, runner=fake_runner)
    assert calls == 1
    assert result.authorization_source == (
        "standing-policy:codex-lane-v-opus-v1"
    )


def test_standing_authorization_requires_exact_review_profile(
    tmp_path: Path,
) -> None:
    request = replace(
        _request(tmp_path, authorization=""),
        review_profile="money-gate",
    )
    calls = 0

    def forbidden_runner(*args: object, **kwargs: object) -> object:
        nonlocal calls
        calls += 1
        raise AssertionError("provider must not run for a wrong profile")

    with pytest.raises(bridge.ReviewContractError) as excinfo:
        _pure_review(request, runner=forbidden_runner)

    assert excinfo.value.reason == "invalid_profile"
    assert calls == 0


@pytest.mark.parametrize(
    "authorization",
    ["user-task:verification-1", "verify-request:route-22"],
)
def test_explicit_authorization_sources_are_preserved(
    tmp_path: Path, authorization: str
) -> None:
    request = _request(tmp_path, authorization=authorization)

    def fake_runner(
        argv: list[str], **kwargs: object
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(
            argv,
            0,
            _claude_stream(
                reviewed_head=request.reviewed_head,
                reviewed_base=request.reviewed_base,
            ),
            "",
        )

    result = _pure_review(request, runner=fake_runner)
    assert result.authorization_source == authorization


def test_explicit_standing_policy_source_is_rejected(
    tmp_path: Path,
) -> None:
    request = _request(
        tmp_path,
        authorization="standing-policy:codex-lane-v-opus-v1",
    )

    with pytest.raises(bridge.ReviewContractError) as excinfo:
        bridge.review(request)

    assert excinfo.value.reason == "invalid_authorization"


def test_review_rejects_unstructured_authorization_source(tmp_path: Path) -> None:
    def forbidden_runner(*args: object, **kwargs: object) -> subprocess.CompletedProcess[str]:
        raise AssertionError("Claude must not run with an invalid authorization source")

    with pytest.raises(bridge.ReviewContractError) as excinfo:
        _pure_review(_request(tmp_path, authorization="yes"), runner=forbidden_runner)

    assert excinfo.value.reason == "invalid_authorization"


def test_review_rejects_non_opus_effective_model(tmp_path: Path) -> None:
    request = _request(tmp_path)

    def fake_runner(argv: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(
            argv,
            0,
            _claude_stream(
                model="claude-sonnet-4-6",
                reviewed_head=request.reviewed_head,
                reviewed_base=request.reviewed_base,
            ),
            "",
        )

    result = _pure_review(request, runner=fake_runner)

    assert result.status == "unavailable"
    assert result.unavailable_reason == "effective_model_not_opus"


def test_review_normalizes_timeout_without_retry(tmp_path: Path) -> None:
    calls = 0
    sandbox_roots: list[Path] = []
    request = _request(tmp_path, authorization="")

    def fake_runner(argv: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        nonlocal calls
        calls += 1
        sandbox_roots.append(Path(argv[2]).parent.parent)
        raise subprocess.TimeoutExpired(argv, 900)

    result = _pure_review(request, runner=fake_runner)

    assert calls == 1
    assert result.status == "unavailable"
    assert result.unavailable_reason == "timeout"
    assert result.review_profile == "codex-lane-v"
    assert result.authorization_source == (
        "standing-policy:codex-lane-v-opus-v1"
    )
    assert sandbox_roots and not sandbox_roots[0].exists()
    assert not any(
        thread.name == "opus-verification-broker" and thread.is_alive()
        for thread in threading.enumerate()
    )


def test_review_normalizes_missing_claude_binary(tmp_path: Path) -> None:
    def fake_runner(argv: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        raise FileNotFoundError("claude")

    result = _pure_review(_request(tmp_path), runner=fake_runner)

    assert result.status == "unavailable"
    assert result.unavailable_reason == "claude_not_found"


def test_review_resolves_claude_before_default_process_group_launch(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    request = _request(tmp_path)
    fake_bin = tmp_path.parent / f"{tmp_path.name}-provider-bin"
    fake_bin.mkdir()
    fake_claude = fake_bin / "claude"
    fake_claude.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
    fake_claude.chmod(0o755)
    monkeypatch.setattr(shutil, "which", lambda *args, **kwargs: str(fake_claude))
    calls = 0

    def fake_process_group_runner(
        argv: list[str], **kwargs: object
    ) -> bridge.CapturedProcess:
        nonlocal calls
        calls += 1
        assert Path(argv[3]) == fake_claude.resolve()
        return _captured_process(
            argv,
            0,
            _claude_stream(
                reviewed_head=request.reviewed_head,
                reviewed_base=request.reviewed_base,
            ),
            "",
        )

    monkeypatch.setattr(bridge, "_run_process_group", fake_process_group_runner)

    result = bridge.review(
        request,
        runtime_factory=bridge._sandbox_runtime,
        broker_factory=_PureVerificationBroker,
        sandbox_probe=lambda runtime, snapshot, broker: True,
    )

    assert calls == 1
    assert result.status == "pass"


def test_review_missing_claude_is_unavailable_before_sandbox_launch(
    tmp_path: Path,
) -> None:
    request = _request(tmp_path)

    def forbidden_runner(
        *args: object, **kwargs: object
    ) -> subprocess.CompletedProcess[str]:
        raise AssertionError("provider must not run without a resolved Claude binary")

    result = _pure_review(
        request,
        runner=forbidden_runner,
        resolver=lambda environment: None,
    )

    assert result.status == "unavailable"
    assert result.unavailable_reason == "claude_not_found"


@pytest.mark.parametrize(
    "error",
    [
        PermissionError("permission denied"),
        OSError(errno.ENOEXEC, "executable format error"),
        OSError(errno.EIO, "provider spawn I/O error"),
        OSError("provider output capture failed"),
    ],
    ids=[
        "permission",
        "executable-format",
        "other-oserror",
        "reader-thread-start",
    ],
)
def test_review_normalizes_provider_spawn_oserror(
    tmp_path: Path, error: OSError
) -> None:
    def fake_runner(argv: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        raise error

    result = _pure_review(_request(tmp_path), runner=fake_runner)

    assert result.status == "unavailable"
    assert result.unavailable_reason == "process_failed"


def test_review_normalizes_invalid_stream_json(tmp_path: Path) -> None:
    def fake_runner(argv: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(argv, 0, "not-json\n", "")

    result = _pure_review(_request(tmp_path), runner=fake_runner)

    assert result.status == "unavailable"
    assert result.unavailable_reason == "invalid_json"


def test_review_rejects_invalid_utf8_before_stream_parsing(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def forbidden_parser(stdout: str) -> object:
        raise AssertionError("invalid UTF-8 must fail before provider parsing")

    monkeypatch.setattr(bridge, "parse_claude_stream", forbidden_parser)

    def fake_runner(argv: list[str], **kwargs: object) -> bridge.CapturedProcess:
        return _captured_process(argv, 0, b"\xff", b"")

    result = _pure_review(_request(tmp_path), runner=fake_runner)

    assert result.status == "unavailable"
    assert result.unavailable_reason == "invalid_json"


def test_review_rejects_stream_events_after_result(tmp_path: Path) -> None:
    request = _request(tmp_path)
    stdout = "\n".join(
        (
            _claude_stream(
                reviewed_head=request.reviewed_head,
                reviewed_base=request.reviewed_base,
            ),
            json.dumps({"type": "assistant", "message": "trailing"}),
        )
    )

    def fake_runner(argv: list[str], **kwargs: object) -> bridge.CapturedProcess:
        return _captured_process(argv, 0, stdout, b"")

    result = _pure_review(request, runner=fake_runner)

    assert result.status == "unavailable"
    assert result.unavailable_reason == "invalid_schema"


def test_review_rejects_duplicate_init_events(tmp_path: Path) -> None:
    request = _request(tmp_path)
    stdout = "\n".join(
        [
            json.dumps(
                {
                    "type": "system",
                    "subtype": "init",
                    "model": "claude-opus-4-7",
                }
            ),
            _claude_stream(
                reviewed_head=request.reviewed_head,
                reviewed_base=request.reviewed_base,
            ),
        ]
    )

    def fake_runner(argv: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(argv, 0, stdout, "")

    result = _pure_review(request, runner=fake_runner)

    assert result.status == "unavailable"
    assert result.unavailable_reason == "invalid_schema"


def test_review_rejects_conflicting_init_events(tmp_path: Path) -> None:
    request = _request(tmp_path)
    stdout = "\n".join(
        [
            json.dumps(
                {
                    "type": "system",
                    "subtype": "init",
                    "model": "claude-opus-4-7",
                }
            ),
            _claude_stream(
                model="claude-sonnet-4-6",
                reviewed_head=request.reviewed_head,
                reviewed_base=request.reviewed_base,
            ),
        ]
    )

    def fake_runner(argv: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(argv, 0, stdout, "")

    result = _pure_review(request, runner=fake_runner)

    assert result.status == "unavailable"
    assert result.unavailable_reason == "invalid_schema"


def test_review_rejects_duplicate_result_events(tmp_path: Path) -> None:
    request = _request(tmp_path)
    structured = _structured_payload(
        reviewed_head=request.reviewed_head,
        reviewed_base=request.reviewed_base,
    )
    stdout = "\n".join(
        [
            _claude_stream(
                reviewed_head=request.reviewed_head,
                reviewed_base=request.reviewed_base,
            ),
            json.dumps(
                {
                    "type": "result",
                    "subtype": "success",
                    "structured_output": structured,
                }
            ),
        ]
    )

    def fake_runner(argv: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(argv, 0, stdout, "")

    result = _pure_review(request, runner=fake_runner)

    assert result.status == "unavailable"
    assert result.unavailable_reason == "invalid_schema"


def test_review_accepts_opus_issues_result(tmp_path: Path) -> None:
    request = _request(tmp_path)

    def fake_runner(argv: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(
            argv,
            0,
            _claude_stream(
                structured=_structured_payload(
                    status="issues",
                    findings=[_finding_payload()],
                    reviewed_head=request.reviewed_head,
                    reviewed_base=request.reviewed_base,
                ),
            ),
            "",
        )

    result = _pure_review(request, runner=fake_runner)

    assert result.status == "issues"
    assert tuple(finding.id for finding in result.findings) == ("OPUS-1",)


def test_review_rejects_missing_effective_model(tmp_path: Path) -> None:
    request = _request(tmp_path)
    stdout = json.dumps(
        {
            "type": "result",
            "subtype": "success",
            "structured_output": _structured_payload(
                reviewed_head=request.reviewed_head,
                reviewed_base=request.reviewed_base,
            ),
        }
    )

    def fake_runner(argv: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(argv, 0, stdout, "")

    result = _pure_review(request, runner=fake_runner)

    assert result.status == "unavailable"
    assert result.unavailable_reason == "effective_model_missing"


def test_review_normalizes_scope_mismatch(tmp_path: Path) -> None:
    request = _request(tmp_path)
    payload = _structured_payload(
        reviewed_head=request.reviewed_head,
        reviewed_base=request.reviewed_base,
    )
    payload["reviewed_head"] = "c" * 40

    def fake_runner(argv: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(
            argv, 0, _claude_stream(structured=payload), ""
        )

    result = _pure_review(request, runner=fake_runner)

    assert result.status == "unavailable"
    assert result.unavailable_reason == "reviewed_scope_mismatch"


def test_review_normalizes_invalid_structured_schema(tmp_path: Path) -> None:
    request = _request(tmp_path)
    payload = _structured_payload(
        reviewed_head=request.reviewed_head,
        reviewed_base=request.reviewed_base,
    )
    payload["findings"] = [_finding_payload()]

    def fake_runner(argv: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(
            argv, 0, _claude_stream(structured=payload), ""
        )

    result = _pure_review(request, runner=fake_runner)

    assert result.status == "unavailable"
    assert result.unavailable_reason == "invalid_schema"


@pytest.mark.parametrize(
    ("diagnostic", "reason"),
    [
        ("OAuth token expired; please run /login", "authentication_failed"),
        ("unexpected process exit", "process_failed"),
    ],
)
def test_review_normalizes_nonzero_process_failures(
    tmp_path: Path, diagnostic: str, reason: str
) -> None:
    def fake_runner(argv: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(argv, 1, "", diagnostic)

    result = _pure_review(_request(tmp_path), runner=fake_runner)

    assert result.status == "unavailable"
    assert result.unavailable_reason == reason


def test_review_rejects_non_pipeline_root(tmp_path: Path) -> None:
    request = bridge.ReviewRequest(
        repo_root=tmp_path,
        reviewed_head=HEAD,
        reviewed_base=BASE,
        requirement_paths=(),
        allowed_paths=(),
        verification_commands=(),
        review_profile=bridge.CODEX_LANE_V_REVIEW_PROFILE,
        authorization_source="user-task:verification-1",
    )

    with pytest.raises(bridge.ReviewContractError) as excinfo:
        bridge.review(request)

    assert excinfo.value.reason == "not_pipeline_repo"


@pytest.mark.parametrize(
    ("changes", "reason"),
    [
        ({"allowed_paths": ("../outside",)}, "invalid_scope"),
        (
            {
                "verification_commands": (
                    "env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/* -q",
                )
            },
            "invalid_command",
        ),
        ({"max_turns": 13}, "invalid_limits"),
        ({"timeout_seconds": 901}, "invalid_limits"),
    ],
)
def test_review_rejects_scope_command_or_limit_widening(
    tmp_path: Path, changes: dict[str, object], reason: str
) -> None:
    request = replace(_request(tmp_path, authorization=""), **changes)

    def forbidden_runner(*args: object, **kwargs: object) -> subprocess.CompletedProcess[str]:
        raise AssertionError("invalid requests must fail before Claude runs")

    with pytest.raises(bridge.ReviewContractError) as excinfo:
        _pure_review(request, runner=forbidden_runner)

    assert excinfo.value.reason == reason


def test_review_bridge_does_not_write_repository_files(tmp_path: Path) -> None:
    request = _request(tmp_path)
    before = {
        path.relative_to(tmp_path).as_posix(): path.read_bytes()
        for path in tmp_path.rglob("*")
        if path.is_file()
    }

    def fake_runner(argv: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(
            argv,
            0,
            _claude_stream(
                reviewed_head=request.reviewed_head,
                reviewed_base=request.reviewed_base,
            ),
            "",
        )

    result = _pure_review(request, runner=fake_runner)
    after = {
        path.relative_to(tmp_path).as_posix(): path.read_bytes()
        for path in tmp_path.rglob("*")
        if path.is_file()
    }

    assert result.status == "pass"
    assert after == before


def test_review_cli_requires_and_emits_review_profile(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    requirement = tmp_path / "brief.md"
    requirement.write_text("Verify the route guard.\n", encoding="utf-8")

    def fake_reviewer(request: bridge.ReviewRequest) -> bridge.OpusReview:
        assert request.reviewed_head == HEAD
        assert request.reviewed_base == BASE
        assert request.review_profile == "codex-lane-v"
        assert request.authorization_source == "user-task:verification-1"
        return bridge.parse_structured_review(
            _structured_payload(),
            expected_head=HEAD,
            expected_base=BASE,
            expected_profile=request.review_profile,
            effective_model="claude-opus-4-7",
            authorization_source=request.authorization_source,
        )

    rc = bridge.main(
        [
            "review",
            "--repo-root",
            str(tmp_path),
            "--head",
            HEAD.upper(),
            "--base",
            BASE.upper(),
            "--requirement",
            str(requirement),
            "--allow-path",
            "scripts/route_lineage.py",
            "--verification-command",
            "env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_route_lineage.py -q",
            "--review-profile",
            "codex-lane-v",
            "--authorization-source",
            "user-task:verification-1",
        ],
        reviewer=fake_reviewer,
    )

    assert rc == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["schema_version"] == "opus-review/v2"
    assert payload["review_profile"] == "codex-lane-v"
    assert payload["status"] == "pass"


def test_reconcile_cli_allows_evidence_backed_disproof(
    capsys: pytest.CaptureFixture[str],
) -> None:
    review = bridge.parse_structured_review(
        _structured_payload(status="issues", findings=[_finding_payload()]),
        expected_head=HEAD,
        expected_base=BASE,
        expected_profile="codex-lane-v",
        effective_model="claude-opus-4-7",
        authorization_source="user-task:verification-1",
    )

    rc = bridge.main(
        [
            "reconcile",
            "--repo-root",
            str(ROOT),
            "--codex-verdict",
            "GO",
            "--head",
            HEAD,
            "--base",
            BASE,
            "--opus-review-json",
            json.dumps(review.to_dict()),
            "--disposition",
            "OPUS-1=disproved",
            "--evidence",
            "OPUS-1=focused stale-parent test exits 0 and the branch rejects the stale value",
        ]
    )

    assert rc == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["schema_version"] == "opus-reconciliation/v1"
    assert payload["go_allowed"] is True
    assert payload["disproved_finding_ids"] == ["OPUS-1"]


def test_finding_id_round_trips_structured_json_through_reconcile_cli(
    capsys: pytest.CaptureFixture[str],
) -> None:
    finding = _finding_payload()
    finding["id"] = "OPUS.safe_1-2"
    normalized = bridge.parse_structured_review(
        _structured_payload(status="issues", findings=[finding]),
        expected_head=HEAD,
        expected_base=BASE,
        expected_profile="codex-lane-v",
        effective_model="claude-opus-4-7",
        authorization_source="user-task:verification-1",
    )

    rc = bridge.main(
        [
            "reconcile",
            "--repo-root",
            str(ROOT),
            "--codex-verdict",
            "GO",
            "--head",
            HEAD.upper(),
            "--base",
            BASE.upper(),
            "--opus-review-json",
            json.dumps(normalized.to_dict()),
            "--disposition",
            "OPUS.safe_1-2=disproved",
            "--evidence",
            "OPUS.safe_1-2=focused round-trip evidence",
        ]
    )

    assert rc == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["reviewed_head"] == HEAD
    assert payload["reviewed_base"] == BASE
    assert payload["disproved_finding_ids"] == ["OPUS.safe_1-2"]


def test_reconcile_cli_rejects_missing_disproof_evidence(
    capsys: pytest.CaptureFixture[str],
) -> None:
    review = bridge.parse_structured_review(
        _structured_payload(status="issues", findings=[_finding_payload()]),
        expected_head=HEAD,
        expected_base=BASE,
        expected_profile="codex-lane-v",
        effective_model="claude-opus-4-7",
        authorization_source="user-task:verification-1",
    )

    rc = bridge.main(
        [
            "reconcile",
            "--repo-root",
            str(ROOT),
            "--codex-verdict",
            "GO",
            "--head",
            HEAD,
            "--base",
            BASE,
            "--opus-review-json",
            json.dumps(review.to_dict()),
            "--disposition",
            "OPUS-1=disproved",
        ]
    )

    captured = capsys.readouterr()
    assert rc == 2
    assert "disproof_evidence_missing" in captured.err
