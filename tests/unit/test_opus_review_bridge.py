from __future__ import annotations

import errno
import inspect
import json
import stat
import subprocess
import sys
from dataclasses import replace
from pathlib import Path

import pytest

import opus_review_bridge as bridge


HEAD = "a" * 40
BASE = "b" * 40


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
        "schema_version": "opus-review/v1",
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
        effective_model="claude-opus-4-7",
        authorization_source="user-task:verification-1",
    )

    assert review.status == "pass"
    assert review.findings == ()
    assert review.effective_model == "claude-opus-4-7"
    assert review.to_dict()["schema_version"] == "opus-review/v1"


def test_parse_structured_review_rejects_scope_mismatch() -> None:
    payload = _structured_payload()
    payload["reviewed_head"] = "c" * 40

    with pytest.raises(bridge.ReviewContractError) as excinfo:
        bridge.parse_structured_review(
            payload,
            expected_head=HEAD,
            expected_base=BASE,
            effective_model="claude-opus-4-7",
            authorization_source="user-task:verification-1",
        )

    assert excinfo.value.reason == "reviewed_scope_mismatch"


def _normalized_pass_payload() -> dict[str, object]:
    return bridge.parse_structured_review(
        _structured_payload(),
        expected_head=HEAD,
        expected_base=BASE,
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
        effective_model="claude-opus-4-7",
        authorization_source="user-task:verification-1",
    )
    with pytest.raises(bridge.ReviewContractError) as excinfo:
        bridge.reconcile(
            "GO",
            review,
            [],
            expected_head="c" * 40,
            expected_base=BASE,
        )
    assert excinfo.value.reason == "reviewed_scope_mismatch"

    result = bridge.reconcile(
        "GO",
        review,
        [],
        expected_head=HEAD,
        expected_base=BASE,
    )
    assert result.reviewed_head == HEAD
    assert result.reviewed_base == BASE
    assert result.to_dict()["reviewed_head"] == HEAD
    assert result.to_dict()["reviewed_base"] == BASE


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


def _committed_request(tmp_path: Path) -> bridge.ReviewRequest:
    request = _uncommitted_request(tmp_path)
    route = tmp_path / "scripts" / "route_lineage.py"
    route.write_text("STATE = 'base'\n", encoding="utf-8")
    route_test = tmp_path / "tests" / "unit" / "test_route_lineage.py"
    route_test.parent.mkdir(parents=True)
    route_test.write_text("def test_fixture():\n    assert True\n", encoding="utf-8")
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


def test_review_request_has_no_codex_result_channel(tmp_path: Path) -> None:
    request = _request(tmp_path)
    prompt = bridge.build_review_prompt(request)

    assert "codex_verdict" not in inspect.signature(bridge.ReviewRequest).parameters
    assert "codex_report" not in inspect.signature(bridge.ReviewRequest).parameters
    assert "codex_findings" not in inspect.signature(bridge.ReviewRequest).parameters
    assert "codex_conclusion" not in inspect.signature(bridge.ReviewRequest).parameters
    assert "Do not ask for or infer the Codex verifier's verdict" in prompt
    assert "Authorization source: user-task:verification-1" in prompt
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
    argv = bridge.build_claude_command(request)
    rendered = " ".join(argv)
    dynamic_agents = json.loads(argv[argv.index("--agents") + 1])
    verifier = dynamic_agents["lane-v-verifier"]
    allowed_rules = argv[argv.index("--allowedTools") + 1 :]

    assert argv[:2] == ["claude", "-p"]
    assert "--agent lane-v-verifier" in rendered
    assert "--model opus" in rendered
    assert verifier["model"] == "opus"
    assert verifier["maxTurns"] == 12
    assert "ROLE-CONTENT-FROM-EXISTING-AGENT" in verifier["prompt"]
    assert "hooks" not in verifier
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
        bridge.build_claude_command(request)

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

    argv = bridge.build_claude_command(request)
    allowed_rules = argv[argv.index("--allowedTools") + 1 :]

    assert any("-m pytest" in rule for rule in allowed_rules)
    assert any("scripts/ci_smoke.py" in rule for rule in allowed_rules)


def test_review_runs_in_immutable_head_snapshot_with_trusted_base_agent(
    tmp_path: Path,
) -> None:
    request = _committed_request(tmp_path)
    snapshot_paths: list[Path] = []

    def fake_runner(argv: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        snapshot = Path(str(kwargs["cwd"]))
        snapshot_paths.append(snapshot)
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
        agents = json.loads(argv[argv.index("--agents") + 1])
        verifier_prompt = agents["lane-v-verifier"]["prompt"]
        assert "BASE-TRUSTED-AGENT" in verifier_prompt
        assert "HEAD-UNTRUSTED-AGENT" not in verifier_prompt
        assert "MUTABLE-WIP-AGENT" not in verifier_prompt
        return subprocess.CompletedProcess(
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
    assert snapshot_paths and not snapshot_paths[0].exists()
    assert (tmp_path / "brief.md").read_text(encoding="utf-8") == "mutable WIP requirement\n"


@pytest.mark.parametrize("field", ["reviewed_head", "reviewed_base"])
def test_review_proves_revisions_exist_before_provider_call(
    tmp_path: Path, field: str
) -> None:
    request = replace(_committed_request(tmp_path), **{field: "f" * 40})

    def forbidden_runner(*args: object, **kwargs: object) -> subprocess.CompletedProcess[str]:
        raise AssertionError("Claude must not run for a missing reviewed commit")

    with pytest.raises(bridge.ReviewContractError) as excinfo:
        bridge.review(request, runner=forbidden_runner)

    assert excinfo.value.reason == "invalid_scope"


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

    result = bridge.review(request, runner=fake_runner)

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


def test_review_missing_authorization_does_not_invoke_claude(tmp_path: Path) -> None:
    def forbidden_runner(*args: object, **kwargs: object) -> subprocess.CompletedProcess[str]:
        raise AssertionError("Claude must not run without authorization")

    result = bridge.review(_request(tmp_path, authorization=""), runner=forbidden_runner)

    assert result.status == "unavailable"
    assert result.unavailable_reason == "authorization_missing"


def test_review_whitespace_authorization_records_missing_source(tmp_path: Path) -> None:
    def forbidden_runner(*args: object, **kwargs: object) -> subprocess.CompletedProcess[str]:
        raise AssertionError("Claude must not run without authorization")

    result = bridge.review(
        _request(tmp_path, authorization=" \t "), runner=forbidden_runner
    )

    assert result.status == "unavailable"
    assert result.unavailable_reason == "authorization_missing"
    assert result.authorization_source == "missing"


def test_review_rejects_unstructured_authorization_source(tmp_path: Path) -> None:
    def forbidden_runner(*args: object, **kwargs: object) -> subprocess.CompletedProcess[str]:
        raise AssertionError("Claude must not run with an invalid authorization source")

    with pytest.raises(bridge.ReviewContractError) as excinfo:
        bridge.review(_request(tmp_path, authorization="yes"), runner=forbidden_runner)

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

    result = bridge.review(request, runner=fake_runner)

    assert result.status == "unavailable"
    assert result.unavailable_reason == "effective_model_not_opus"


def test_review_normalizes_timeout_without_retry(tmp_path: Path) -> None:
    calls = 0

    def fake_runner(argv: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        nonlocal calls
        calls += 1
        raise subprocess.TimeoutExpired(argv, 900)

    result = bridge.review(_request(tmp_path), runner=fake_runner)

    assert calls == 1
    assert result.status == "unavailable"
    assert result.unavailable_reason == "timeout"


def test_review_normalizes_missing_claude_binary(tmp_path: Path) -> None:
    def fake_runner(argv: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        raise FileNotFoundError("claude")

    result = bridge.review(_request(tmp_path), runner=fake_runner)

    assert result.status == "unavailable"
    assert result.unavailable_reason == "claude_not_found"


@pytest.mark.parametrize(
    "error",
    [
        PermissionError("permission denied"),
        OSError(errno.ENOEXEC, "executable format error"),
        OSError(errno.EIO, "provider spawn I/O error"),
    ],
    ids=["permission", "executable-format", "other-oserror"],
)
def test_review_normalizes_provider_spawn_oserror(
    tmp_path: Path, error: OSError
) -> None:
    def fake_runner(argv: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        raise error

    result = bridge.review(_request(tmp_path), runner=fake_runner)

    assert result.status == "unavailable"
    assert result.unavailable_reason == "process_failed"


def test_review_normalizes_invalid_stream_json(tmp_path: Path) -> None:
    def fake_runner(argv: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(argv, 0, "not-json\n", "")

    result = bridge.review(_request(tmp_path), runner=fake_runner)

    assert result.status == "unavailable"
    assert result.unavailable_reason == "invalid_json"


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

    result = bridge.review(request, runner=fake_runner)

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

    result = bridge.review(request, runner=fake_runner)

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

    result = bridge.review(request, runner=fake_runner)

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

    result = bridge.review(request, runner=fake_runner)

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

    result = bridge.review(request, runner=fake_runner)

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

    result = bridge.review(request, runner=fake_runner)

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

    result = bridge.review(request, runner=fake_runner)

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

    result = bridge.review(_request(tmp_path), runner=fake_runner)

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
    request = replace(_request(tmp_path), **changes)

    def forbidden_runner(*args: object, **kwargs: object) -> subprocess.CompletedProcess[str]:
        raise AssertionError("invalid requests must fail before Claude runs")

    with pytest.raises(bridge.ReviewContractError) as excinfo:
        bridge.review(request, runner=forbidden_runner)

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

    result = bridge.review(request, runner=fake_runner)
    after = {
        path.relative_to(tmp_path).as_posix(): path.read_bytes()
        for path in tmp_path.rglob("*")
        if path.is_file()
    }

    assert result.status == "pass"
    assert after == before


def test_review_cli_prints_normalized_result(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    requirement = tmp_path / "brief.md"
    requirement.write_text("Verify the route guard.\n", encoding="utf-8")

    def fake_reviewer(request: bridge.ReviewRequest) -> bridge.OpusReview:
        assert request.reviewed_head == HEAD
        assert request.authorization_source == "user-task:verification-1"
        return bridge.parse_structured_review(
            _structured_payload(),
            expected_head=HEAD,
            expected_base=BASE,
            effective_model="claude-opus-4-7",
            authorization_source=request.authorization_source,
        )

    rc = bridge.main(
        [
            "review",
            "--repo-root",
            str(tmp_path),
            "--head",
            HEAD,
            "--base",
            BASE,
            "--requirement",
            str(requirement),
            "--allow-path",
            "scripts/route_lineage.py",
            "--verification-command",
            "env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_route_lineage.py -q",
            "--authorization-source",
            "user-task:verification-1",
        ],
        reviewer=fake_reviewer,
    )

    assert rc == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["schema_version"] == "opus-review/v1"
    assert payload["status"] == "pass"


def test_reconcile_cli_allows_evidence_backed_disproof(
    capsys: pytest.CaptureFixture[str],
) -> None:
    review = bridge.parse_structured_review(
        _structured_payload(status="issues", findings=[_finding_payload()]),
        expected_head=HEAD,
        expected_base=BASE,
        effective_model="claude-opus-4-7",
        authorization_source="user-task:verification-1",
    )

    rc = bridge.main(
        [
            "reconcile",
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


def test_reconcile_cli_rejects_missing_disproof_evidence(
    capsys: pytest.CaptureFixture[str],
) -> None:
    review = bridge.parse_structured_review(
        _structured_payload(status="issues", findings=[_finding_payload()]),
        expected_head=HEAD,
        expected_base=BASE,
        effective_model="claude-opus-4-7",
        authorization_source="user-task:verification-1",
    )

    rc = bridge.main(
        [
            "reconcile",
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
