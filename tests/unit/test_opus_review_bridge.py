from __future__ import annotations

import errno
import hashlib
import io
import inspect
import json
import multiprocessing
import os
import signal
import shlex
import shutil
import socket
import stat
import subprocess
import sys
import tarfile
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from dataclasses import dataclass, replace
from pathlib import Path

import pytest

import opus_review_bridge as bridge
import opus_review_receipts as receipts


ROOT = Path(__file__).resolve().parents[2]
EXPECTED_PROVIDER_OUTPUT_LIMIT_BYTES = 131_072
EXISTING_SESSION_TRANSPORT_PROFILE = "anthropic-claude-existing-session-v1"
FORBIDDEN_CLAUDE_ENVIRONMENT = (
    "ANTHROPIC_API_KEY",
    "ANTHROPIC_AUTH_TOKEN",
    "ANTHROPIC_BASE_URL",
    "CLAUDE_CODE_OAUTH_TOKEN",
    "ALL_PROXY",
    "HTTPS_PROXY",
    "HTTP_PROXY",
    "NO_PROXY",
    "all_proxy",
    "https_proxy",
    "http_proxy",
    "no_proxy",
)


def test_provider_only_advisory_prompt_exactly_matches_plan() -> None:
    plan = (
        ROOT
        / "docs"
        / "superpowers"
        / "plans"
        / "2026-07-13-opus-lanev-receipt-hardening.md"
    ).read_text(encoding="utf-8")
    anchor = (
        "After Task 7, the exact body returned by "
        "`_agent_prompt_from_content()` and\n"
        "passed through `--append-system-prompt` must be the following text, byte "
        "for\nbyte after surrounding whitespace is stripped:\n\n"
    )
    _, anchor_found, after_anchor = plan.partition(anchor)
    assert anchor_found == anchor
    _, fence_found, after_fence = after_anchor.partition("```markdown\n")
    assert fence_found == "```markdown\n"
    expected_body, closing_fence_found, _ = after_fence.partition("\n```")
    assert closing_fence_found == "\n```"

    content = (
        ROOT / "scripts" / "prompts" / "opus_lane_v_advisory.md"
    ).read_text(encoding="utf-8")
    actual_body = bridge._agent_prompt_from_content(content)

    assert actual_body == expected_body

    advisory_limitations = (
        "You are a read-only advisory evidence reviewer, not an operator seat or\n"
        "protocol decision-maker.",
        "The Codex operator\nalone decides GO, NITS, FAIL, mailbox actions, lock "
        "actions, and every other\nprotocol or side-effect decision.",
        "Do not issue a protocol verdict.",
        "Do not edit,\nstage, commit, produce a patch, write mail, mutate a lock, or "
        "perform any other\nside effect.",
    )
    old_authority_phrases = (
        "operator-seat verifier",
        "report FAIL with file:line evidence",
        "in-scope (GO + ratify-owed)",
        "**Verdict:** GO / NITS / FAIL",
        "GO authorizes its release",
    )
    assert all(limitation in actual_body for limitation in advisory_limitations)
    assert all(phrase not in actual_body for phrase in old_authority_phrases)


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
        "schema_version": "opus-provider-review/v1",
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
    assert review.to_dict()["schema_version"] == "opus-review/v3"


def test_provider_and_normalized_review_schemas_are_separate() -> None:
    assert bridge.PROVIDER_SCHEMA_VERSION == "opus-provider-review/v1"
    assert bridge.REVIEW_SCHEMA_VERSION == receipts.REVIEW_SCHEMA_VERSION
    assert bridge.RECONCILIATION_SCHEMA_VERSION == (
        receipts.RECONCILIATION_SCHEMA_VERSION
    )
    assert bridge.OPUS_OUTPUT_SCHEMA["properties"]["schema_version"] == {
        "const": "opus-provider-review/v1"
    }


def test_opus_review_v3_round_trip_preserves_bridge_owned_fields() -> None:
    review = bridge.parse_structured_review(
        _structured_payload(),
        expected_head=HEAD,
        expected_base=BASE,
        expected_profile="codex-lane-v",
        effective_model="claude-opus-4-7",
        authorization_source="user-task:verification-1",
    )

    payload = review.to_dict()
    assert payload["schema_version"] == "opus-review/v3"
    assert payload["review_profile"] == "codex-lane-v"
    assert payload["failure_stage"] is None
    assert payload["stdout_truncated"] is False
    assert payload["stderr_truncated"] is False
    assert bridge.OpusReview.from_dict(payload) == review


def test_provider_payload_cannot_assert_bridge_receipt_metadata() -> None:
    payload = _structured_payload()
    payload["receipt_id"] = "opr1:" + "a" * 64

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


def test_opus_review_from_dict_rejects_provider_payload() -> None:
    payload = _structured_payload()

    with pytest.raises(bridge.ReviewContractError) as excinfo:
        bridge.OpusReview.from_dict(payload)

    assert excinfo.value.reason == "invalid_schema"


def test_opus_review_from_dict_rejects_v2_without_profile() -> None:
    payload = _normalized_pass_payload()
    payload["schema_version"] = "opus-review/v2"
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
    return bridge._reconcile_review(
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


@pytest.mark.parametrize(
    ("severity", "codex_verdict"),
    [
        ("minor", "GO"),
        ("important", "GO"),
        ("important", "NITS"),
        ("critical", "GO"),
        ("critical", "NITS"),
    ],
)
def test_reconcile_rejects_verdict_below_confirmed_severity_floor(
    severity: str, codex_verdict: str
) -> None:
    review = bridge.parse_structured_review(
        _structured_payload(
            status="issues", findings=[_finding_payload(severity=severity)]
        ),
        expected_head=HEAD,
        expected_base=BASE,
        expected_profile="codex-lane-v",
        effective_model="claude-opus-4-7",
        authorization_source="user-task:verification-1",
    )

    with pytest.raises(bridge.ReviewContractError) as excinfo:
        _reconcile(
            codex_verdict,
            review,
            [bridge.FindingDisposition("OPUS-1", "confirmed", "")],
        )

    assert excinfo.value.reason == "verdict_severity_mismatch"


@pytest.mark.parametrize(
    ("severity", "codex_verdict", "expected_bucket"),
    [
        ("minor", "NITS", "nits"),
        ("minor", "FAIL", "nits"),
        ("important", "FAIL", "fail"),
        ("critical", "FAIL", "fail"),
    ],
)
def test_reconcile_accepts_verdict_at_or_above_confirmed_severity_floor(
    severity: str, codex_verdict: str, expected_bucket: str
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
        codex_verdict,
        review,
        [bridge.FindingDisposition("OPUS-1", "confirmed", "")],
    )

    assert result.codex_verdict == codex_verdict
    assert not result.go_allowed
    assert result.confirmed_fail_finding_ids == (
        ("OPUS-1",) if expected_bucket == "fail" else ()
    )
    assert result.confirmed_nits_finding_ids == (
        ("OPUS-1",) if expected_bucket == "nits" else ()
    )


def test_reconcile_mixed_confirmed_findings_uses_highest_severity_floor(
) -> None:
    minor = _finding_payload(severity="minor")
    important = _finding_payload(severity="important")
    important["id"] = "OPUS-2"
    review = bridge.parse_structured_review(
        _structured_payload(status="issues", findings=[minor, important]),
        expected_head=HEAD,
        expected_base=BASE,
        expected_profile="codex-lane-v",
        effective_model="claude-opus-4-7",
        authorization_source="user-task:verification-1",
    )
    dispositions = [
        bridge.FindingDisposition("OPUS-1", "confirmed", ""),
        bridge.FindingDisposition("OPUS-2", "confirmed", ""),
    ]

    with pytest.raises(bridge.ReviewContractError) as excinfo:
        _reconcile("NITS", review, dispositions)

    assert excinfo.value.reason == "verdict_severity_mismatch"
    result = _reconcile("FAIL", review, dispositions)
    assert result.confirmed_fail_finding_ids == ("OPUS-2",)
    assert result.confirmed_nits_finding_ids == ("OPUS-1",)


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
    parameters = inspect.signature(bridge._reconcile_review).parameters
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
        bridge._reconcile_review(
            "GO",
            review,
            [],
            expected_head="c" * 40,
            expected_base=BASE,
        )
    assert excinfo.value.reason == "reviewed_scope_mismatch"

    result = bridge._reconcile_review(
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
) -> bridge._ProviderReviewRequest:
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
    return bridge._ProviderReviewRequest(
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


AUTHORITY_TASK_ID = "11111111-2222-4333-8444-555555555555"


@dataclass(frozen=True)
class _AuthorityFixture:
    root: Path
    request: bridge.ReviewRequest
    base: str
    head: str
    descriptor_commit: str
    trigger_commit: str
    descriptor_path: str
    descriptor_digest: str
    event_path: str | None


PROMPT_AUTHORITY_TASK_ID = "22222222-3333-4444-8555-666666666666"
PROMPT_PATH = "scripts/prompts/opus_lane_v_advisory.md"
PROMPT_AUTHORITY_PREFIX = (
    "scripts/prompts/opus_lane_v_advisory.authority."
)


@dataclass(frozen=True)
class _PromptAuthorityFixture:
    root: Path
    request: bridge.ReviewRequest
    base: str
    head: str
    descriptor_path: str
    descriptor_digest: str
    authority_path: str | None
    authority_blob_oid: str | None
    prompt_blob_oid: str
    prompt_bytes: bytes
    prompt_body: str | None


def _hash_git_blob(root: Path, raw: bytes) -> str:
    completed = subprocess.run(
        ["env", "-u", "GIT_INDEX_FILE", "git", "hash-object", "--stdin"],
        cwd=root,
        input=raw,
        check=True,
        capture_output=True,
    )
    return completed.stdout.decode("ascii").strip()


def _prompt_authority_fixture(
    root: Path,
    *,
    include_authority: bool = True,
    extra_authority: bool = False,
    authority_filename_oid: str | None = None,
    authority_overrides: dict[str, object] | None = None,
    authority_raw: bytes | None = None,
    authority_prompt_bytes: bytes | None = None,
    committed_prompt_bytes: bytes | None = None,
) -> _PromptAuthorityFixture:
    root.mkdir()
    (root / "AGENTS.md").write_text("# Pipeline fixture\n", encoding="utf-8")
    scripts = root / "scripts"
    scripts.mkdir()
    (scripts / "codex_protocol_model.py").write_text(
        "# Pipeline marker\n", encoding="utf-8"
    )
    (scripts / "feature.py").write_text("VALUE = 'base'\n", encoding="utf-8")
    requirement = root / "requirements" / "task.md"
    requirement.parent.mkdir()
    requirement.write_text("Review the committed feature.\n", encoding="utf-8")
    old_claude = root / ".claude" / "agents" / "lane-v-verifier.md"
    old_claude.parent.mkdir(parents=True)
    old_claude.write_text(
        "---\nname: lane-v-verifier\n---\n\n"
        "OLD-CLAUDE-AUTHORITY-SENTINEL\n",
        encoding="utf-8",
    )
    codex_mirror = root / ".codex" / "agents" / "lane-v-verifier.toml"
    codex_mirror.parent.mkdir(parents=True)
    codex_mirror.write_text(
        'developer_instructions = "CODEX-MIRROR-AUTHORITY-SENTINEL"\n',
        encoding="utf-8",
    )

    _git(root, "init", "-q")
    _git(root, "config", "user.name", "Prompt Authority Fixture")
    _git(root, "config", "user.email", "prompt-authority@example.invalid")
    _git(root, "add", ".")
    _git(root, "commit", "-q", "-m", "chore: pre-authority base")
    base = _git(root, "rev-parse", "HEAD")

    expected_prompt = (
        (ROOT / PROMPT_PATH).read_bytes()
        if authority_prompt_bytes is None
        else authority_prompt_bytes
    )
    prompt_blob_oid = _hash_git_blob(root, expected_prompt)
    try:
        prompt_body = bridge._agent_prompt_from_content(
            expected_prompt.decode("utf-8")
        )
        body_bytes = prompt_body.encode("utf-8")
    except (UnicodeDecodeError, bridge.ReviewContractError):
        prompt_body = None
        body_bytes = b""
    authority_mapping: dict[str, object] = {
        "schema_version": "opus-provider-prompt-authority/v1",
        "prompt_path": PROMPT_PATH,
        "prompt_blob_oid": prompt_blob_oid,
        "file_sha256": "sha256:" + hashlib.sha256(expected_prompt).hexdigest(),
        "file_size_bytes": len(expected_prompt),
        "body_sha256": "sha256:" + hashlib.sha256(body_bytes).hexdigest(),
        "body_size_bytes": len(body_bytes),
    }
    if authority_overrides:
        authority_mapping.update(authority_overrides)
    manifest_raw = authority_raw or (
        json.dumps(authority_mapping, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")
    authority_blob_oid = _hash_git_blob(root, manifest_raw)
    encoded_oid = authority_filename_oid or authority_blob_oid
    authority_path = f"{PROMPT_AUTHORITY_PREFIX}{encoded_oid}.json"

    requirement_paths = ["requirements/task.md"]
    if include_authority:
        manifest = root / authority_path
        manifest.parent.mkdir(parents=True, exist_ok=True)
        manifest.write_bytes(manifest_raw)
        requirement_paths.append(authority_path)
    if extra_authority:
        extra_raw = manifest_raw + b" "
        extra_oid = _hash_git_blob(root, extra_raw)
        extra_path = f"{PROMPT_AUTHORITY_PREFIX}{extra_oid}.json"
        (root / extra_path).write_bytes(extra_raw)
        requirement_paths.append(extra_path)

    descriptor_path = (
        "coordination/verification/scopes/"
        f"{PROMPT_AUTHORITY_TASK_ID}.json"
    )
    descriptor = {
        "schema_version": "lane-v-scope/v1",
        "task_id": PROMPT_AUTHORITY_TASK_ID,
        "question_id": "descriptor-bound-advisory-prompt",
        "trigger_kind": "shipping-commit",
        "verification_mode": "codex-lane-v",
        "verification_harness": "codex:lane-v-verifier",
        "review_profile": "codex-lane-v",
        "reviewed_base": {"policy": "exact", "commit": base},
        "requirement_paths": requirement_paths,
        "allowed_path_roots": [
            ".claude",
            ".codex",
            "coordination/verification/scopes",
            "requirements",
            "scripts",
        ],
        "verification_commands": [
            "env -u GIT_INDEX_FILE .venv/bin/python -m pytest "
            "tests/unit/test_feature.py -q"
        ],
    }
    descriptor_file = root / descriptor_path
    descriptor_file.parent.mkdir(parents=True)
    descriptor_raw = (
        json.dumps(descriptor, indent=2, ensure_ascii=False) + "\n"
    ).encode("utf-8")
    descriptor_file.write_bytes(descriptor_raw)
    descriptor_digest = "sha256:" + hashlib.sha256(descriptor_raw).hexdigest()
    _git(root, "add", ".")
    _git(root, "commit", "-q", "-m", "docs: bind prompt authority")

    committed_prompt = (
        expected_prompt
        if committed_prompt_bytes is None
        else committed_prompt_bytes
    )
    prompt_file = root / PROMPT_PATH
    prompt_file.parent.mkdir(parents=True, exist_ok=True)
    prompt_file.write_bytes(committed_prompt)
    _git(root, "add", PROMPT_PATH)
    _git(root, "commit", "-q", "-m", "feat: seed advisory provider prompt")

    (scripts / "feature.py").write_text("VALUE = 'reviewed'\n", encoding="utf-8")
    _git(root, "add", "scripts/feature.py")
    _git(
        root,
        "commit",
        "-q",
        "-m",
        "feat: bind reviewed prompt",
        "-m",
        f"Lane-V-Scope: {descriptor_path}@{descriptor_digest}",
    )
    head = _git(root, "rev-parse", "HEAD")

    prompt_file.write_text(
        "---\nname: wip\n---\n\nMUTABLE-WIP-PROMPT-SENTINEL\n",
        encoding="utf-8",
    )
    return _PromptAuthorityFixture(
        root=root,
        request=bridge.ReviewRequest(
            repo_root=root,
            reviewed_head=head,
            reviewed_base=base,
            review_profile="codex-lane-v",
            authorization_source="",
            trigger_kind="shipping-commit",
            trigger_commit=head,
        ),
        base=base,
        head=head,
        descriptor_path=descriptor_path,
        descriptor_digest=descriptor_digest,
        authority_path=authority_path if include_authority else None,
        authority_blob_oid=authority_blob_oid if include_authority else None,
        prompt_blob_oid=prompt_blob_oid,
        prompt_bytes=expected_prompt,
        prompt_body=prompt_body,
    )


def test_review_renders_descriptor_bound_advisory_prompt_separately_from_task_prompt(
    tmp_path: Path,
) -> None:
    fixture = _prompt_authority_fixture(tmp_path / "repo")
    assert fixture.prompt_body is not None
    observed_argv: list[list[str]] = []
    store = receipts.ReceiptStore(tmp_path / "state")

    def fake_runner(argv: list[str], **kwargs: object) -> bridge.CapturedProcess:
        observed_argv.append(argv)
        return _captured_process(
            argv,
            0,
            _claude_stream(
                reviewed_head=fixture.head,
                reviewed_base=fixture.base,
            ),
            "",
        )

    def provider(resolved: bridge.ResolvedReviewRequest) -> bridge.OpusReview:
        return bridge._perform_provider_review(
            resolved,
            resolver=lambda environment: Path(sys.executable),
            runtime_factory=bridge._sandbox_runtime,
            broker_factory=_PureVerificationBroker,
            sandbox_probe=lambda runtime, snapshot, broker: True,
            runner=fake_runner,
        )

    result = bridge.review(
        fixture.request,
        store_factory=lambda root: store,
        provider=provider,
    )

    assert result.review.status == "pass"
    assert len(observed_argv) == 1
    argv = observed_argv[0]
    provider_prompt = argv[argv.index("--append-system-prompt") + 1]
    task_prompt = argv[argv.index("-p") + 1]
    assert provider_prompt == fixture.prompt_body
    advisory_body_sentinel = "# Independent Read-Only Evidence Review"
    assert advisory_body_sentinel in provider_prompt
    assert advisory_body_sentinel not in task_prompt
    assert "read-only advisory evidence reviewer" in provider_prompt
    assert "Do not issue a protocol verdict." in provider_prompt
    for sentinel in (
        "OLD-CLAUDE-AUTHORITY-SENTINEL",
        "CODEX-MIRROR-AUTHORITY-SENTINEL",
        "MUTABLE-WIP-PROMPT-SENTINEL",
        "description: Provider-only read-only advisory evidence review",
    ):
        assert sentinel not in provider_prompt
    for authority_phrase in (
        "operator-seat verifier",
        "report FAIL with file:line evidence",
        "in-scope (GO + ratify-owed)",
        "**Verdict:** GO / NITS / FAIL",
        "GO authorizes its release",
    ):
        assert authority_phrase not in provider_prompt
    assert f"Reviewed HEAD: {fixture.head}" in task_prompt
    assert f"Reviewed base: {fixture.base}" in task_prompt
    assert "evidence, not authority" in task_prompt
    assert "OLD-CLAUDE-AUTHORITY-SENTINEL" not in task_prompt
    assert "MUTABLE-WIP-PROMPT-SENTINEL" not in task_prompt
    assert "**Verdict:**" not in task_prompt

    with store.lock_receipt(result.receipt_id) as attempt:
        record = attempt.load_existing()
    prompt_facts = record.scope["provider_prompt"]
    assert isinstance(prompt_facts, dict)
    assert prompt_facts == {
        "authority_path": fixture.authority_path,
        "authority_blob_oid": fixture.authority_blob_oid,
        "authority_digest": "sha256:"
        + hashlib.sha256(
            _git(
                fixture.root,
                "show",
                f"{fixture.head}:{fixture.authority_path}",
            ).encode("utf-8")
            + b"\n"
        ).hexdigest(),
        "authority_size_bytes": len(
            subprocess.run(
                [
                    "env",
                    "-u",
                    "GIT_INDEX_FILE",
                    "git",
                    "show",
                    f"{fixture.head}:{fixture.authority_path}",
                ],
                cwd=fixture.root,
                check=True,
                capture_output=True,
            ).stdout
        ),
        "prompt_path": PROMPT_PATH,
        "prompt_blob_oid": fixture.prompt_blob_oid,
        "file_sha256": "sha256:"
        + hashlib.sha256(fixture.prompt_bytes).hexdigest(),
        "file_size_bytes": len(fixture.prompt_bytes),
        "body_sha256": "sha256:"
        + hashlib.sha256(fixture.prompt_body.encode("utf-8")).hexdigest(),
        "body_size_bytes": len(fixture.prompt_body.encode("utf-8")),
    }
    serialized_scope = json.dumps(record.scope, sort_keys=True)
    assert fixture.prompt_body not in serialized_scope
    assert fixture.prompt_body not in repr(
        bridge.resolve_provider_authoritative_scope(fixture.request)
    )


@pytest.mark.parametrize(
    ("case", "expected_detail"),
    [
        (
            "missing-authority",
            "Codex review requires exactly one provider prompt authority requirement",
        ),
        (
            "multiple-authority",
            "Codex review requires exactly one provider prompt authority requirement",
        ),
        ("malformed-authority", "schema_version"),
        (
            "filename-oid-mismatch",
            "provider prompt authority filename does not match its Git blob",
        ),
        (
            "wrong-prompt-path",
            f"prompt_path must be {PROMPT_PATH!r}",
        ),
        (
            "wrong-prompt-blob",
            "provider prompt Git blob does not match committed authority",
        ),
        (
            "wrong-file-digest",
            "provider prompt Git blob does not match committed authority",
        ),
        (
            "wrong-file-size",
            "provider prompt Git blob does not match committed authority",
        ),
        (
            "wrong-body-digest",
            "provider prompt body does not match committed authority",
        ),
        (
            "wrong-body-size",
            "provider prompt body does not match committed authority",
        ),
        (
            "unknown-authority-field",
            "provider prompt authority fields must be "
            "['body_sha256', 'body_size_bytes', 'file_sha256', "
            "'file_size_bytes', 'prompt_blob_oid', 'prompt_path', "
            "'schema_version'], got ['body_sha256', 'body_size_bytes', "
            "'file_sha256', 'file_size_bytes', 'prompt_blob_oid', "
            "'prompt_path', 'schema_version', 'unexpected']",
        ),
        (
            "boolean-size",
            "file_size_bytes must be an integer from 1 to 65536",
        ),
        ("invalid-prompt-utf8", "provider prompt must be UTF-8"),
        ("invalid-prompt-frontmatter", "missing opening frontmatter"),
        (
            "reviewed-prompt-drift",
            "provider prompt Git blob does not match committed authority",
        ),
    ],
)
def test_prompt_authority_failure_precedes_store_and_provider_construction(
    tmp_path: Path, case: str, expected_detail: str
) -> None:
    exact_prompt = (ROOT / PROMPT_PATH).read_bytes()
    kwargs: dict[str, object] = {}
    if case == "missing-authority":
        kwargs["include_authority"] = False
    elif case == "multiple-authority":
        kwargs["extra_authority"] = True
    elif case == "malformed-authority":
        kwargs["authority_raw"] = b'{"schema_version":"x","schema_version":"y"}\n'
    elif case == "filename-oid-mismatch":
        kwargs["authority_filename_oid"] = "0" * 40
    elif case == "wrong-prompt-path":
        kwargs["authority_overrides"] = {
            "prompt_path": "scripts/prompts/not_opus_lane_v_advisory.md"
        }
    elif case == "wrong-prompt-blob":
        kwargs["authority_overrides"] = {"prompt_blob_oid": "f" * 40}
    elif case == "wrong-file-digest":
        kwargs["authority_overrides"] = {
            "file_sha256": "sha256:" + "0" * 64
        }
    elif case == "wrong-file-size":
        kwargs["authority_overrides"] = {
            "file_size_bytes": len(exact_prompt) + 1
        }
    elif case == "wrong-body-digest":
        kwargs["authority_overrides"] = {
            "body_sha256": "sha256:" + "0" * 64
        }
    elif case == "wrong-body-size":
        kwargs["authority_overrides"] = {"body_size_bytes": 1}
    elif case == "unknown-authority-field":
        kwargs["authority_overrides"] = {"unexpected": "x"}
    elif case == "boolean-size":
        kwargs["authority_overrides"] = {"file_size_bytes": True}
    elif case == "invalid-prompt-utf8":
        kwargs["authority_prompt_bytes"] = b"\xff"
        kwargs["authority_overrides"] = {
            "body_sha256": "sha256:" + hashlib.sha256(b"x").hexdigest(),
            "body_size_bytes": 1,
        }
    elif case == "invalid-prompt-frontmatter":
        kwargs["authority_prompt_bytes"] = b"# no frontmatter\n"
        kwargs["authority_overrides"] = {
            "body_sha256": "sha256:" + hashlib.sha256(b"x").hexdigest(),
            "body_size_bytes": 1,
        }
    elif case == "reviewed-prompt-drift":
        kwargs["committed_prompt_bytes"] = exact_prompt.replace(
            b"Evidence over prose.", b"DRIFTED PROMPT BODY."
        )
    fixture = _prompt_authority_fixture(tmp_path / case, **kwargs)
    calls = {"store": 0, "provider": 0}

    def forbidden_store(root: Path) -> receipts.ReceiptStore:
        del root
        calls["store"] += 1
        raise AssertionError("store construction must follow prompt validation")

    def forbidden_provider(
        resolved: bridge.ResolvedReviewRequest,
    ) -> bridge.OpusReview:
        del resolved
        calls["provider"] += 1
        raise AssertionError("provider construction must follow prompt validation")

    with pytest.raises(bridge.ReviewContractError) as excinfo:
        bridge.review(
            fixture.request,
            store_factory=forbidden_store,
            provider=forbidden_provider,
        )

    assert excinfo.value.reason == "invalid_provider_prompt"
    assert excinfo.value.detail == expected_detail
    assert calls == {"store": 0, "provider": 0}


def _authority_fixture(
    root: Path,
    *,
    trigger_kind: str = "shipping-commit",
    recipient: str = "operator",
    descriptor_task_id: str = AUTHORITY_TASK_ID,
    descriptor_path_task_id: str = AUTHORITY_TASK_ID,
    descriptor_changes: dict[str, object] | None = None,
    shipping_subject: str = "feat: bind reviewed change",
    shipping_references: tuple[str, ...] | None = None,
    shipping_followup_body: str | None = None,
    trailer_reference_override: str | None = None,
    event_overrides: dict[str, str] | None = None,
) -> _AuthorityFixture:
    root.mkdir()
    (root / "AGENTS.md").write_text("# Pipeline fixture\n", encoding="utf-8")
    scripts = root / "scripts"
    scripts.mkdir()
    (scripts / "codex_protocol_model.py").write_text(
        "# Pipeline marker\n", encoding="utf-8"
    )
    (scripts / "feature.py").write_text("VALUE = 'base'\n", encoding="utf-8")
    agent = root / ".claude" / "agents" / "lane-v-verifier.md"
    agent.parent.mkdir(parents=True)
    agent.write_text(
        "---\nname: lane-v-verifier\n---\n\nPinned verifier.\n",
        encoding="utf-8",
    )
    requirement = root / "requirements" / "task.md"
    requirement.parent.mkdir()
    requirement.write_text("Review the committed feature.\n", encoding="utf-8")
    test_file = root / "tests" / "unit" / "test_feature.py"
    test_file.parent.mkdir(parents=True)
    test_file.write_text("def test_feature():\n    assert True\n", encoding="utf-8")

    _git(root, "init", "-q")
    _git(root, "config", "user.name", "Authority Fixture")
    _git(root, "config", "user.email", "authority@example.invalid")
    _git(root, "add", ".")
    _git(root, "commit", "-q", "-m", "chore: base")
    base = _git(root, "rev-parse", "HEAD")

    provider_prompt = (
        "---\nname: fixture-advisory\n---\n\n"
        "Fixture read-only advisory evidence review.\n"
    ).encode("utf-8")
    provider_body = bridge._agent_prompt_from_content(
        provider_prompt.decode("utf-8")
    ).encode("utf-8")
    provider_prompt_oid = _hash_git_blob(root, provider_prompt)
    prompt_authority = {
        "schema_version": "opus-provider-prompt-authority/v1",
        "prompt_path": PROMPT_PATH,
        "prompt_blob_oid": provider_prompt_oid,
        "file_sha256": "sha256:" + hashlib.sha256(provider_prompt).hexdigest(),
        "file_size_bytes": len(provider_prompt),
        "body_sha256": "sha256:" + hashlib.sha256(provider_body).hexdigest(),
        "body_size_bytes": len(provider_body),
    }
    prompt_authority_raw = (
        json.dumps(prompt_authority, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")
    prompt_authority_oid = _hash_git_blob(root, prompt_authority_raw)
    prompt_authority_path = (
        f"{PROMPT_AUTHORITY_PREFIX}{prompt_authority_oid}.json"
    )
    prompt_authority_file = root / prompt_authority_path
    prompt_authority_file.parent.mkdir(parents=True, exist_ok=True)
    prompt_authority_file.write_bytes(prompt_authority_raw)

    descriptor_path = (
        "coordination/verification/scopes/"
        f"{descriptor_path_task_id}.json"
    )
    descriptor = {
        "schema_version": "lane-v-scope/v1",
        "task_id": descriptor_task_id,
        "question_id": "authority-fixture",
        "trigger_kind": trigger_kind,
        "verification_mode": "codex-lane-v",
        "verification_harness": "codex:lane-v-verifier",
        "review_profile": "codex-lane-v",
        "reviewed_base": {"policy": "exact", "commit": base},
        "requirement_paths": [
            "requirements/task.md",
            prompt_authority_path,
        ],
        "allowed_path_roots": [
            "coordination/mailbox/sent",
            "coordination/verification/scopes",
            "requirements",
            "scripts",
        ],
        "verification_commands": [
            "env -u GIT_INDEX_FILE .venv/bin/python -m pytest "
            "tests/unit/test_feature.py -q"
        ],
    }
    if descriptor_changes:
        descriptor.update(descriptor_changes)
    descriptor_file = root / descriptor_path
    descriptor_file.parent.mkdir(parents=True)
    descriptor_bytes = (
        json.dumps(descriptor, indent=2, ensure_ascii=False) + "\n"
    ).encode("utf-8")
    descriptor_file.write_bytes(descriptor_bytes)
    descriptor_digest = "sha256:" + hashlib.sha256(descriptor_bytes).hexdigest()
    _git(root, "add", descriptor_path)
    _git(root, "add", prompt_authority_path)
    _git(root, "commit", "-q", "-m", "docs: bind review authority")
    descriptor_commit = _git(root, "rev-parse", "HEAD")

    provider_prompt_file = root / PROMPT_PATH
    provider_prompt_file.write_bytes(provider_prompt)
    _git(root, "add", PROMPT_PATH)
    _git(root, "commit", "-q", "-m", "feat: seed fixture advisory prompt")

    (scripts / "feature.py").write_text("VALUE = 'reviewed'\n", encoding="utf-8")
    _git(root, "add", "scripts/feature.py")
    if trigger_kind == "shipping-commit":
        reference = trailer_reference_override or (
            f"{descriptor_path}@{descriptor_digest}"
        )
        references = (
            (reference,) if shipping_references is None else shipping_references
        )
        commit_args = ["commit", "-q", "-m", shipping_subject]
        if references:
            commit_args.extend(
                (
                    "-m",
                    "\n".join(
                        f"Lane-V-Scope: {item}" for item in references
                    ),
                )
            )
        if shipping_followup_body is not None:
            commit_args.extend(("-m", shipping_followup_body))
        _git(root, *commit_args)
    else:
        _git(root, "commit", "-q", "-m", "feat: bind reviewed change")
    head = _git(root, "rev-parse", "HEAD")

    event_path: str | None = None
    trigger_commit = head
    if trigger_kind == "verify-request":
        values = {
            "filename_timestamp": "2026-07-13T00-16-59Z",
            "when": "2026-07-13T00:16:59Z",
            "sender": "director",
            "recipient": recipient,
            "h1_sender": "Director",
            "h1_recipient": recipient.capitalize(),
            "from_sender": "director",
            "event_type": "verify-request",
            "head": head,
            "base": base,
            "scope": f"{descriptor_path}@{descriptor_digest}",
        }
        if event_overrides:
            values.update(event_overrides)
        event_path = (
            "coordination/mailbox/sent/"
            f"{values['filename_timestamp']}-{values['sender']}-to-"
            f"{values['recipient']}-verify-request.md"
        )
        event_file = root / event_path
        event_file.parent.mkdir(parents=True, exist_ok=True)
        event_file.write_text(
            f"# {values['h1_sender']} → {values['h1_recipient']}: "
            "review fixture\n\n"
            f"**When:** {values['when']} · **From:** "
            f"{values['from_sender']} (online)\n\n"
            f"Event type: {values['event_type']}\n"
            f"Reviewed head: {values['head']}\n"
            f"Reviewed base: {values['base']}\n"
            f"Lane-V-Scope: {values['scope']}\n",
            encoding="utf-8",
        )
        _git(root, "add", event_path)
        _git(root, "commit", "-q", "-m", "coord: request verification")
        trigger_commit = _git(root, "rev-parse", "HEAD")

    return _AuthorityFixture(
        root=root,
        request=bridge.ReviewRequest(
            repo_root=root,
            reviewed_head=head,
            reviewed_base=base,
            review_profile="codex-lane-v",
            authorization_source="",
            trigger_kind=trigger_kind,
            trigger_commit=trigger_commit,
            trigger_path=event_path,
        ),
        base=base,
        head=head,
        descriptor_commit=descriptor_commit,
        trigger_commit=trigger_commit,
        descriptor_path=descriptor_path,
        descriptor_digest=descriptor_digest,
        event_path=event_path,
    )


def test_shipping_trigger_resolves_only_committed_authority_and_uppercase_shas(
    tmp_path: Path,
) -> None:
    fixture = _authority_fixture(tmp_path / "repo")
    fixture_path = fixture.root / fixture.descriptor_path
    fixture_path.write_text("mutable descriptor sentinel\n", encoding="utf-8")
    uppercase = replace(
        fixture.request,
        reviewed_head=fixture.head.upper(),
        reviewed_base=fixture.base.upper(),
        trigger_commit=fixture.trigger_commit.upper(),
    )

    resolved = bridge.resolve_authoritative_scope(uppercase)

    assert resolved.request.reviewed_head == fixture.head
    assert resolved.request.reviewed_base == fixture.base
    assert resolved.request.trigger_commit == fixture.trigger_commit
    assert resolved.authority.task_id == AUTHORITY_TASK_ID
    assert resolved.scope.trigger_identity == (
        f"shipping-commit:{fixture.trigger_commit}"
    )
    assert resolved.scope.descriptor_digest == fixture.descriptor_digest


@pytest.mark.parametrize(
    "selector",
    (
        "GIT_DIR",
        "GIT_COMMON_DIR",
        "GIT_OBJECT_DIRECTORY",
        "GIT_ALTERNATE_OBJECT_DIRECTORIES",
    ),
)
def test_authoritative_scope_rejects_foreign_graph_from_ambient_git_selector(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    selector: str,
) -> None:
    target = _authority_fixture(
        tmp_path / "target",
        descriptor_task_id="aaaaaaaa-bbbb-4ccc-8ddd-eeeeeeeeeeee",
        descriptor_path_task_id="aaaaaaaa-bbbb-4ccc-8ddd-eeeeeeeeeeee",
    )
    foreign = _authority_fixture(tmp_path / "foreign")
    assert target.head != foreign.head
    invisible = bridge._git_process(
        target.root, "cat-file", "-e", f"{foreign.head}^{{commit}}"
    )
    assert invisible.returncode != 0
    foreign_git_dir = foreign.root / ".git"
    _git(
        foreign.root,
        "config",
        "core.worktree",
        str(target.root.resolve()),
    )
    selector_value = (
        foreign_git_dir / "objects"
        if selector
        in {"GIT_OBJECT_DIRECTORY", "GIT_ALTERNATE_OBJECT_DIRECTORIES"}
        else foreign_git_dir
    )
    monkeypatch.setenv(selector, str(selector_value))

    with pytest.raises(
        (bridge.ReviewContractError, receipts.ReceiptContractError)
    ):
        bridge.resolve_authoritative_scope(
            replace(foreign.request, repo_root=target.root)
        )


def test_bridge_host_git_launcher_strips_every_git_environment_key(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    fixture = _authority_fixture(tmp_path / "repo")
    hostile_bin = tmp_path / "hostile-bin"
    hostile_bin.mkdir()
    shim_marker = tmp_path / "git-shim-invoked"
    git_shim = hostile_bin / "git"
    git_shim.write_text(
        "#!/bin/sh\n"
        f"printf 'invoked\\n' >> {shlex.quote(str(shim_marker))}\n"
        "exit 97\n",
        encoding="utf-8",
    )
    git_shim.chmod(0o755)
    real_run = subprocess.run
    launches: list[tuple[list[str], dict[str, object]]] = []

    def launch_spy(
        argv: list[str], **kwargs: object
    ) -> subprocess.CompletedProcess[object]:
        launches.append((argv, kwargs))
        return real_run(argv, **kwargs)

    monkeypatch.setenv("PATH", str(hostile_bin))
    monkeypatch.setenv("GIT_FUTURE_AUTHORITY_SELECTOR", "attacker-controlled")
    monkeypatch.setattr(bridge.subprocess, "run", launch_spy)

    resolved = bridge.resolve_authoritative_scope(fixture.request)

    assert resolved.request.reviewed_head == fixture.head
    assert launches
    assert not shim_marker.exists()
    for argv, kwargs in launches:
        assert argv[:2] == ["/usr/bin/git", "--no-replace-objects"]
        assert Path(kwargs["cwd"]) == fixture.root
        environment = kwargs["env"]
        assert isinstance(environment, dict)
        assert environment["PATH"] == str(hostile_bin)
        assert not any(key.startswith("GIT_") for key in environment)


def test_authoritative_scope_ignores_replace_ref_for_reviewed_commit(
    tmp_path: Path,
) -> None:
    fixture = _authority_fixture(tmp_path / "repo")
    feature_path = fixture.root / "scripts" / "feature.py"
    original = _git(
        fixture.root,
        "show",
        f"{fixture.head}:scripts/feature.py",
    )
    feature_path.write_text("VALUE = 'replacement'\n", encoding="utf-8")
    _git(fixture.root, "add", "scripts/feature.py")
    attacker_tree = _git(fixture.root, "write-tree")
    attacker = _git(
        fixture.root,
        "commit-tree",
        attacker_tree,
        "-m",
        "chore: attacker replacement",
    )
    _git(fixture.root, "reset", "-q", "--hard", fixture.head)
    _git(fixture.root, "replace", fixture.head, attacker)
    assert (
        _git(fixture.root, "show", f"{fixture.head}:scripts/feature.py")
        == "VALUE = 'replacement'"
    )

    resolved = bridge.resolve_provider_authoritative_scope(fixture.request)

    assert resolved.request.reviewed_head == fixture.head
    shown = bridge._git_process(
        fixture.root, "show", f"{fixture.head}:scripts/feature.py"
    )
    assert shown.returncode == 0
    assert shown.stdout.strip() == original


def test_shipping_scope_line_in_middle_body_is_not_a_terminal_trailer(
    tmp_path: Path,
) -> None:
    fixture = _authority_fixture(
        tmp_path / "repo",
        shipping_followup_body="Post-trailer prose is not authority.",
    )

    with pytest.raises(bridge.ReviewContractError) as excinfo:
        bridge.resolve_authoritative_scope(fixture.request)

    assert excinfo.value.reason == "invalid_trigger"


def test_shipping_scope_is_unique_across_body_and_terminal_trailer(
    tmp_path: Path,
) -> None:
    fixture = _authority_fixture(tmp_path / "malformed")
    reference = f"{fixture.descriptor_path}@{fixture.descriptor_digest}"
    _git(
        fixture.root,
        "commit",
        "--amend",
        "-q",
        "-m",
        "feat: bind reviewed change",
        "-m",
        f"Authority context\nLane-V-Scope: {reference}",
        "-m",
        f"Lane-V-Scope: {reference}",
    )
    malformed_head = _git(fixture.root, "rev-parse", "HEAD")
    malformed_request = replace(
        fixture.request,
        reviewed_head=malformed_head,
        trigger_commit=malformed_head,
    )

    with pytest.raises(bridge.ReviewContractError) as excinfo:
        bridge.resolve_authoritative_scope(malformed_request)

    assert excinfo.value.reason == "invalid_trigger"

    lawful = _authority_fixture(tmp_path / "lawful")
    resolved = bridge.resolve_authoritative_scope(lawful.request)
    assert resolved.request.trigger_commit == lawful.trigger_commit


@pytest.mark.parametrize(
    ("case", "fixture_kwargs", "request_change"),
    [
        ("missing-trailer", {"shipping_references": ()}, None),
        (
            "duplicate-trailer",
            {
                "shipping_references": (
                    "coordination/verification/scopes/"
                    f"{AUTHORITY_TASK_ID}.json@sha256:" + "a" * 64,
                    "coordination/verification/scopes/"
                    f"{AUTHORITY_TASK_ID}.json@sha256:" + "b" * 64,
                )
            },
            None,
        ),
        (
            "wrong-digest",
            {
                "trailer_reference_override": (
                    "coordination/verification/scopes/"
                    f"{AUTHORITY_TASK_ID}.json@sha256:" + "0" * 64
                )
            },
            None,
        ),
        (
            "descriptor-task-mismatch",
            {"descriptor_task_id": "aaaaaaaa-bbbb-4ccc-8ddd-eeeeeeeeeeee"},
            None,
        ),
        ("non-shipping-subject", {"shipping_subject": "docs: not shipping"}, None),
        ("trigger-not-head", {}, "trigger_not_head"),
        ("wrong-request-base", {}, "wrong_base"),
        ("abbreviated-head", {}, "abbreviated_head"),
        ("moving-trigger", {}, "moving_trigger"),
        (
            "unsupported-harness",
            {"descriptor_changes": {"verification_harness": "invented:harness"}},
            None,
        ),
    ],
)
def test_shipping_trigger_rejects_unbound_or_ambiguous_authority(
    tmp_path: Path,
    case: str,
    fixture_kwargs: dict[str, object],
    request_change: str | None,
) -> None:
    fixture = _authority_fixture(tmp_path / case, **fixture_kwargs)
    request = fixture.request
    if request_change == "trigger_not_head":
        request = replace(request, trigger_commit=fixture.descriptor_commit)
    elif request_change == "wrong_base":
        request = replace(request, reviewed_base=fixture.descriptor_commit)
    elif request_change == "abbreviated_head":
        request = replace(request, reviewed_head=fixture.head[:12])
    elif request_change == "moving_trigger":
        request = replace(request, trigger_commit="HEAD")

    with pytest.raises((bridge.ReviewContractError, receipts.ReceiptContractError)):
        bridge.resolve_authoritative_scope(request)


@pytest.mark.parametrize("recipient", ["operator", "operator2"])
def test_verify_request_resolves_exact_committed_envelope(
    tmp_path: Path, recipient: str
) -> None:
    fixture = _authority_fixture(
        tmp_path / recipient,
        trigger_kind="verify-request",
        recipient=recipient,
    )

    resolved = bridge.resolve_provider_authoritative_scope(fixture.request)

    assert resolved.verify_request == bridge.VerifyRequestEnvelope(
        timestamp="2026-07-13T00:16:59Z",
        sender="director",
        recipient=recipient,
    )
    assert resolved.scope.trigger_identity == (
        f"verify-request:{fixture.trigger_commit}:{fixture.event_path}"
    )


@pytest.mark.parametrize(
    ("case", "overrides"),
    [
        ("when", {"when": "2026-07-13T00:17:00Z"}),
        ("from", {"from_sender": "director2"}),
        ("h1-sender", {"h1_sender": "Coordinator"}),
        ("h1-recipient", {"h1_recipient": "Operator2"}),
        ("kind", {"event_type": "coordination"}),
        ("recipient", {"recipient": "all", "h1_recipient": "All"}),
        ("head", {"head": "a" * 40}),
        ("base", {"base": "b" * 40}),
        (
            "scope",
            {
                "scope": "coordination/verification/scopes/"
                f"{AUTHORITY_TASK_ID}.json@sha256:" + "0" * 64
            },
        ),
    ],
)
def test_verify_request_rejects_envelope_and_scope_mismatches(
    tmp_path: Path, case: str, overrides: dict[str, str]
) -> None:
    fixture = _authority_fixture(
        tmp_path / case,
        trigger_kind="verify-request",
        event_overrides=overrides,
    )

    with pytest.raises((bridge.ReviewContractError, receipts.ReceiptContractError)):
        bridge.resolve_authoritative_scope(fixture.request)


def test_verify_request_rejects_trigger_path_mismatch(tmp_path: Path) -> None:
    fixture = _authority_fixture(
        tmp_path / "repo", trigger_kind="verify-request"
    )
    request = replace(
        fixture.request,
        trigger_path="coordination/mailbox/sent/not-the-event.md",
    )

    with pytest.raises((bridge.ReviewContractError, receipts.ReceiptContractError)):
        bridge.resolve_authoritative_scope(request)


def test_verify_request_rejects_trigger_on_a_fork_of_reviewed_head(
    tmp_path: Path,
) -> None:
    fixture = _authority_fixture(
        tmp_path / "repo", trigger_kind="verify-request"
    )
    assert fixture.event_path is not None
    event_body = _git(
        fixture.root,
        "show",
        f"{fixture.trigger_commit}:{fixture.event_path}",
    )
    _git(fixture.root, "switch", "--detach", fixture.descriptor_commit)
    event_file = fixture.root / fixture.event_path
    event_file.parent.mkdir(parents=True, exist_ok=True)
    event_file.write_text(event_body + "\n", encoding="utf-8")
    _git(fixture.root, "add", fixture.event_path)
    _git(fixture.root, "commit", "-q", "-m", "coord: forked verification request")
    forked_trigger = _git(fixture.root, "rev-parse", "HEAD")

    with pytest.raises(bridge.ReviewContractError) as excinfo:
        bridge.resolve_authoritative_scope(
            replace(fixture.request, trigger_commit=forked_trigger)
        )

    assert excinfo.value.reason == "invalid_verify_request"


def _commit_shipping_fixture_change(
    fixture: _AuthorityFixture, *paths: str, descriptor_digest: str | None = None
) -> str:
    _git(fixture.root, "add", *paths)
    reference = (
        f"{fixture.descriptor_path}@"
        f"{descriptor_digest or fixture.descriptor_digest}"
    )
    _git(
        fixture.root,
        "commit",
        "-q",
        "-m",
        "feat: advance reviewed change",
        "-m",
        f"Lane-V-Scope: {reference}",
    )
    return _git(fixture.root, "rev-parse", "HEAD")


def test_requirement_metadata_is_bound_to_git_bytes_and_changes_with_head(
    tmp_path: Path,
) -> None:
    fixture = _authority_fixture(tmp_path / "repo")
    first = bridge.resolve_authoritative_scope(fixture.request)
    requirement_path = fixture.root / "requirements" / "task.md"
    original = first.review_requirements[0]

    requirement_path.write_text("mutable working-tree sentinel\n", encoding="utf-8")
    unchanged = bridge.resolve_authoritative_scope(fixture.request)
    assert unchanged.review_requirements[0] == original

    new_head = _commit_shipping_fixture_change(
        fixture, "requirements/task.md"
    )
    changed = bridge.resolve_authoritative_scope(
        replace(
            fixture.request,
            reviewed_head=new_head,
            trigger_commit=new_head,
        )
    )

    assert changed.review_requirements[0].digest != original.digest
    assert changed.review_requirements[0].blob_id != original.blob_id
    assert changed.review_requirements[0].size_bytes == len(
        b"mutable working-tree sentinel\n"
    )


def test_prompt_exposes_content_addressed_git_show_without_raw_authority(
    tmp_path: Path,
) -> None:
    fixture = _authority_fixture(
        tmp_path / "repo", trigger_kind="verify-request", recipient="operator2"
    )
    resolved = bridge.resolve_authoritative_scope(fixture.request)
    (fixture.root / fixture.descriptor_path).write_text(
        "RAW-WORKTREE-AUTHORITY-SENTINEL\n", encoding="utf-8"
    )

    prompt = bridge.build_review_prompt(resolved)

    assert "RAW-WORKTREE-AUTHORITY-SENTINEL" not in prompt
    assert str(fixture.root.resolve()) not in prompt
    for blob in (*resolved.review_requirements, *resolved.authority_requirements):
        assert f"git show {blob.commit}:{blob.path}" in prompt
        assert blob.blob_id in prompt
        assert blob.digest in prompt
        assert str(blob.size_bytes) in prompt


@pytest.mark.parametrize(
    "trigger_kind", ["shipping-commit", "verify-request"]
)
def test_every_printed_immutable_blob_command_has_an_exact_allowed_rule(
    tmp_path: Path, trigger_kind: str
) -> None:
    fixture = _authority_fixture(
        tmp_path / "repo", trigger_kind=trigger_kind
    )
    resolved = bridge.resolve_authoritative_scope(fixture.request)
    execution_request = bridge._provider_request_from_resolved(resolved)
    broker_commands = _broker_client_commands(
        tmp_path / "broker", len(resolved.verification_commands)
    )

    argv = bridge.build_claude_command(
        resolved,
        execution_request=execution_request,
        agent_prompt="PINNED-PRE-HEAD-VERIFIER",
        verification_commands=broker_commands,
    )

    prompt = argv[argv.index("-p") + 1]
    printed_commands = tuple(
        line.split(" command=", 1)[1]
        for line in prompt.splitlines()
        if line.startswith("- purpose=")
    )
    allowed_rules = tuple(argv[argv.index("--allowedTools") + 1 :])
    assert len(printed_commands) == len(
        (*resolved.review_requirements, *resolved.authority_requirements)
    )
    for command in printed_commands:
        assert f"Bash({command})" in allowed_rules
    assert all(
        "broker_client.py" not in rule
        for rule in allowed_rules[: -len(broker_commands)]
    )
    assert all(
        "broker_client.py" in rule
        for rule in allowed_rules[-len(broker_commands) :]
    )


def _review_archive(member: tarfile.TarInfo, payload: bytes = b"") -> bytes:
    raw = io.BytesIO()
    with tarfile.open(fileobj=raw, mode="w") as bundle:
        if member.isfile():
            member.size = len(payload)
            bundle.addfile(member, io.BytesIO(payload))
        else:
            bundle.addfile(member)
    return raw.getvalue()


def test_extract_review_archive_passes_exact_data_filter(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    member = tarfile.TarInfo("bin/reviewer")
    member.mode = 0o755
    archive = _review_archive(member, b"reviewer\n")
    destination = tmp_path / "snapshot"
    observed_filters: list[object] = []
    original_extractall = bridge.tarfile.TarFile.extractall

    def capture_extractall(
        bundle,
        path=".",
        members=None,
        *,
        numeric_owner=False,
        filter=None,
    ):
        observed_filters.append(filter)
        return original_extractall(
            bundle,
            path,
            members,
            numeric_owner=numeric_owner,
            filter=filter,
        )

    monkeypatch.setattr(bridge.tarfile.TarFile, "extractall", capture_extractall)
    bridge._extract_review_archive(archive, destination)

    extracted = destination / "bin" / "reviewer"
    assert observed_filters == [bridge.tarfile.data_filter]
    assert extracted.read_bytes() == b"reviewer\n"
    assert extracted.stat().st_mode & stat.S_IXUSR


@pytest.mark.parametrize("condition", ("missing", "not-callable"))
def test_extract_review_archive_fails_closed_without_callable_data_filter(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, condition: str
) -> None:
    member = tarfile.TarInfo("safe.txt")
    archive = _review_archive(member, b"safe\n")
    destination = tmp_path / "snapshot"
    if condition == "missing":
        monkeypatch.delattr(bridge.tarfile, "data_filter")
    else:
        monkeypatch.setattr(bridge.tarfile, "data_filter", None)

    with pytest.raises(bridge.ReviewContractError) as excinfo:
        bridge._extract_review_archive(archive, destination)

    assert excinfo.value.reason == "invalid_scope"
    assert excinfo.value.detail == "safe tar data filter is unavailable"
    assert not destination.exists()


@pytest.mark.parametrize(
    ("name", "member_type", "linkname"),
    [
        ("/absolute", tarfile.REGTYPE, ""),
        ("../escape", tarfile.REGTYPE, ""),
        (".git/config", tarfile.REGTYPE, ""),
        ("symlink", tarfile.SYMTYPE, "target"),
        ("hardlink", tarfile.LNKTYPE, "target"),
        ("fifo", tarfile.FIFOTYPE, ""),
    ],
)
def test_extract_review_archive_rejects_unsafe_members(
    tmp_path: Path, name: str, member_type: bytes, linkname: str
) -> None:
    member = tarfile.TarInfo(name)
    member.type = member_type
    member.linkname = linkname
    payload = b"unsafe\n" if member.isfile() else b""
    destination = tmp_path / "snapshot"

    with pytest.raises(bridge.ReviewContractError) as excinfo:
        bridge._extract_review_archive(_review_archive(member, payload), destination)

    assert excinfo.value.reason == "invalid_scope"
    assert not destination.exists()


def test_extract_review_archive_blocks_preexisting_destination_symlink(
    tmp_path: Path,
) -> None:
    outside = tmp_path / "outside"
    outside.mkdir()
    destination = tmp_path / "snapshot"
    destination.mkdir()
    (destination / "pivot").symlink_to(outside, target_is_directory=True)
    member = tarfile.TarInfo("pivot/escaped.txt")

    with pytest.raises(tarfile.OutsideDestinationError):
        bridge._extract_review_archive(
            _review_archive(member, b"blocked\n"), destination
        )

    assert not (outside / "escaped.txt").exists()


def test_snapshot_fetches_later_trigger_and_reverifies_bound_blobs(
    tmp_path: Path,
) -> None:
    fixture = _authority_fixture(
        tmp_path / "repo", trigger_kind="verify-request"
    )
    assert fixture.trigger_commit != fixture.head
    resolved = bridge.resolve_authoritative_scope(fixture.request)

    with bridge._immutable_review_snapshot(resolved) as snapshot:
        assert _git(snapshot, "rev-parse", "HEAD") == fixture.head
        _git(snapshot, "cat-file", "-e", f"{fixture.trigger_commit}^{{commit}}")
        for blob in resolved.authority_requirements:
            raw = subprocess.run(
                [
                    "env",
                    "-u",
                    "GIT_INDEX_FILE",
                    "git",
                    "show",
                    f"{blob.commit}:{blob.path}",
                ],
                cwd=snapshot,
                check=True,
                capture_output=True,
            ).stdout
            assert "sha256:" + hashlib.sha256(raw).hexdigest() == blob.digest


def test_authority_blob_over_65536_bytes_fails_before_provider_scope(
    tmp_path: Path,
) -> None:
    fixture = _authority_fixture(tmp_path / "repo")
    descriptor_file = fixture.root / fixture.descriptor_path
    oversized = json.dumps({"padding": "x" * 66_000}).encode("utf-8")
    descriptor_file.write_bytes(oversized)
    digest = "sha256:" + hashlib.sha256(oversized).hexdigest()
    new_head = _commit_shipping_fixture_change(
        fixture, fixture.descriptor_path, descriptor_digest=digest
    )

    with pytest.raises(bridge.ReviewContractError) as excinfo:
        bridge.resolve_authoritative_scope(
            replace(
                fixture.request,
                reviewed_head=new_head,
                trigger_commit=new_head,
            )
        )

    assert excinfo.value.reason == "authority_blob_too_large"


def test_scope_resolution_rejects_missing_requirement_and_uncovered_change(
    tmp_path: Path,
) -> None:
    missing = _authority_fixture(tmp_path / "missing")
    (missing.root / "requirements" / "task.md").unlink()
    missing_head = _commit_shipping_fixture_change(
        missing, "requirements/task.md"
    )
    with pytest.raises(bridge.ReviewContractError, match="committed review_requirement"):
        bridge.resolve_authoritative_scope(
            replace(
                missing.request,
                reviewed_head=missing_head,
                trigger_commit=missing_head,
            )
        )

    uncovered = _authority_fixture(tmp_path / "uncovered")
    unbound = uncovered.root / "unbound.txt"
    unbound.write_text("outside scope\n", encoding="utf-8")
    uncovered_head = _commit_shipping_fixture_change(uncovered, "unbound.txt")
    with pytest.raises(bridge.ReviewContractError) as excinfo:
        bridge.resolve_authoritative_scope(
            replace(
                uncovered.request,
                reviewed_head=uncovered_head,
                trigger_commit=uncovered_head,
            )
        )
    assert excinfo.value.reason == "changed_path_not_allowed"


def test_scope_resolution_uses_bounded_nul_delimited_git_diff(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    fixture = _authority_fixture(tmp_path / "repo")
    original = bridge._git_process
    calls: list[tuple[str, ...]] = []

    def tracked(root: Path, *args: str, **kwargs: object) -> object:
        calls.append(args)
        return original(root, *args, **kwargs)

    monkeypatch.setattr(bridge, "_git_process", tracked)
    bridge.resolve_authoritative_scope(fixture.request)

    assert any(
        args[:5]
        == (
            "-c",
            "core.quotepath=false",
            "-c",
            "diff.renames=false",
            "diff",
        )
        and (
            "--name-status",
            "-z",
            "--no-renames",
            "--no-ext-diff",
            "--no-textconv",
        )
        == args[5:10]
        for args in calls
    )


def _normalized_pass_review(
    resolved: bridge.ResolvedReviewRequest,
) -> bridge.OpusReview:
    return bridge.parse_structured_review(
        _structured_payload(
            reviewed_head=resolved.request.reviewed_head,
            reviewed_base=resolved.scope.effective_base,
        ),
        expected_head=resolved.request.reviewed_head,
        expected_base=resolved.scope.effective_base,
        expected_profile=resolved.scope.review_profile,
        effective_model="claude-opus-4-7",
        authorization_source=resolved.scope.authorization_identity,
    )


def _receipt_store_factory(
    state_root: Path,
) -> object:
    return lambda repo_root: receipts.ReceiptStore.for_repo(
        repo_root, state_root=state_root
    )


def _append_fsynced_crash_trace(trace_path: Path, stage: str) -> None:
    descriptor = os.open(
        trace_path,
        os.O_WRONLY | os.O_CREAT | os.O_APPEND | getattr(os, "O_CLOEXEC", 0),
        0o600,
    )
    try:
        raw = (stage + "\n").encode("utf-8")
        assert os.write(descriptor, raw) == len(raw)
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _crash_review_worker(
    request: bridge.ReviewRequest,
    resolved: bridge.ResolvedReviewRequest,
    state_root: Path,
    trace_path: Path,
    seam: str,
    exit_code: int,
) -> None:
    original_reserve = receipts.LockedAttempt.reserve_or_load
    original_validator = bridge._validated_provider_result

    def traced_reserve(
        attempt: receipts.LockedAttempt,
        scope: receipts.ReviewScope,
    ) -> receipts.ReservationDecision:
        decision = original_reserve(attempt, scope)
        if decision.action == "launch":
            _append_fsynced_crash_trace(trace_path, "reserve:launch")
            if seam == "after_reservation":
                os._exit(exit_code)
        return decision

    def provider(
        provider_resolved: bridge.ResolvedReviewRequest,
    ) -> bridge.OpusReview:
        _append_fsynced_crash_trace(trace_path, "provider:entered")
        if seam == "provider_entry":
            os._exit(exit_code)
        return _normalized_pass_review(provider_resolved)

    def traced_validator(
        candidate: object,
        scope: receipts.ReviewScope,
    ) -> bridge.OpusReview:
        normalized = original_validator(candidate, scope)
        _append_fsynced_crash_trace(trace_path, "validator:normalized")
        if seam == "normalized_result":
            os._exit(exit_code)
        return normalized

    def crash_before_replace(*args: object, **kwargs: object) -> None:
        _append_fsynced_crash_trace(trace_path, "replace:before")
        os._exit(exit_code)

    receipts.LockedAttempt.reserve_or_load = traced_reserve
    if seam in {"normalized_result", "before_replace"}:
        bridge._validated_provider_result = traced_validator
    if seam == "before_replace":
        receipts.os.replace = crash_before_replace

    bridge.review(
        request,
        scope_resolver=lambda unused: resolved,
        store_factory=lambda unused: receipts.ReceiptStore.for_repo(
            resolved.request.repo_root, state_root=state_root
        ),
        provider=provider,
    )
    _append_fsynced_crash_trace(trace_path, "review:returned")
    os._exit(98)


@pytest.mark.parametrize(
    ("seam", "exit_code", "expected_trace"),
    (
        ("after_reservation", 71, ("reserve:launch",)),
        (
            "provider_entry",
            72,
            ("reserve:launch", "provider:entered"),
        ),
        (
            "normalized_result",
            73,
            ("reserve:launch", "provider:entered", "validator:normalized"),
        ),
        (
            "before_replace",
            74,
            (
                "reserve:launch",
                "provider:entered",
                "validator:normalized",
                "replace:before",
            ),
        ),
    ),
)
def test_review_process_crashes_at_four_real_persistence_seams(
    tmp_path: Path,
    seam: str,
    exit_code: int,
    expected_trace: tuple[str, ...],
) -> None:
    fixture = _authority_fixture(tmp_path / "repo")
    resolved = bridge.resolve_provider_authoritative_scope(fixture.request)
    state_root = tmp_path / "state" / seam
    trace_path = tmp_path / f"{seam}.trace"
    context = multiprocessing.get_context("fork")
    process = context.Process(
        target=_crash_review_worker,
        args=(
            fixture.request,
            resolved,
            state_root,
            trace_path,
            seam,
            exit_code,
        ),
    )
    try:
        process.start()
        process.join(timeout=15)
        assert process.exitcode == exit_code
    finally:
        if process.is_alive():
            process.terminate()
        process.join(timeout=5)

    store = receipts.ReceiptStore.for_repo(
        fixture.root, state_root=state_root
    )
    with store.lock_attempt(resolved.scope, blocking=False) as attempt:
        reserved = attempt.load_existing()
    assert reserved.state == "reserved"
    assert reserved.generation == 1
    assert reserved.review is None

    trace = tuple(trace_path.read_text(encoding="utf-8").splitlines())
    assert trace == expected_trace
    orphan_temporary_files = tuple(state_root.glob("*.tmp-*"))
    if seam == "before_replace":
        assert len(orphan_temporary_files) == 1
        orphan = json.loads(
            orphan_temporary_files[0].read_text(encoding="utf-8")
        )
        assert orphan["state"] == "reviewed"
        assert orphan["generation"] == 2
    else:
        assert orphan_temporary_files == ()

    provider_calls = 0

    def forbidden_provider(
        unused: bridge.ResolvedReviewRequest,
    ) -> bridge.OpusReview:
        nonlocal provider_calls
        provider_calls += 1
        raise AssertionError("receipt recovery must not re-enter the provider")

    recovered = bridge.review(
        fixture.request,
        scope_resolver=lambda unused: resolved,
        store_factory=lambda unused: store,
        provider=forbidden_provider,
    )
    replayed = bridge.review(
        fixture.request,
        scope_resolver=lambda unused: resolved,
        store_factory=lambda unused: store,
        provider=forbidden_provider,
    )

    assert provider_calls == 0
    assert recovered.to_dict() == replayed.to_dict()
    assert recovered.receipt_state == "reviewed"
    assert recovered.review.status == "unavailable"
    assert recovered.review.failure_stage == "receipt_recovery"
    assert recovered.review.unavailable_reason == "attempt_state_uncertain"


def test_review_receipt_exact_replay_calls_provider_once(tmp_path: Path) -> None:
    fixture = _authority_fixture(tmp_path / "repo")
    state_root = tmp_path / "state"
    calls = 0

    def provider(resolved: bridge.ResolvedReviewRequest) -> bridge.OpusReview:
        nonlocal calls
        calls += 1
        return _normalized_pass_review(resolved)

    first = bridge.review(
        fixture.request,
        provider=provider,
        store_factory=_receipt_store_factory(state_root),
    )
    second = bridge.review(
        fixture.request,
        provider=provider,
        store_factory=_receipt_store_factory(state_root),
    )

    assert calls == 1
    assert first.receipt_id == second.receipt_id
    assert first.scope_digest == second.scope_digest
    assert first.receipt_state == second.receipt_state == "reviewed"
    assert first.review == second.review
    assert first.to_dict()["schema_version"] == "opus-review/v3"


def test_review_receipt_concurrent_calls_launch_one_provider(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    fixture = _authority_fixture(tmp_path / "repo")
    state_root = tmp_path / "state"
    entered = threading.Event()
    release = threading.Event()
    contended = threading.Event()
    condition = threading.Condition()
    contended_operations: list[int] = []
    owner_fd: int | None = None
    waiter_count = 0
    calls = 0

    def deterministic_flock(fd: int, operation: int) -> None:
        nonlocal owner_fd, waiter_count
        with condition:
            if operation == receipts.fcntl.LOCK_UN:
                assert owner_fd == fd
                owner_fd = None
                condition.notify_all()
                return
            assert operation & receipts.fcntl.LOCK_EX
            if owner_fd is None:
                owner_fd = fd
                return
            contended_operations.append(operation)
            waiter_count += 1
            contended.set()
            try:
                if operation & receipts.fcntl.LOCK_NB:
                    raise BlockingIOError(
                        errno.EWOULDBLOCK, "deterministic attempt contention"
                    )
                while owner_fd is not None:
                    condition.wait()
                owner_fd = fd
            finally:
                waiter_count -= 1

    def provider(resolved: bridge.ResolvedReviewRequest) -> bridge.OpusReview:
        nonlocal calls
        calls += 1
        entered.set()
        assert release.wait(timeout=5)
        return _normalized_pass_review(resolved)

    monkeypatch.setattr(receipts.fcntl, "flock", deterministic_flock)
    with ThreadPoolExecutor(max_workers=2) as executor:
        first_future = executor.submit(
            bridge.review,
            fixture.request,
            provider=provider,
            store_factory=_receipt_store_factory(state_root),
        )
        assert entered.wait(timeout=5)
        second_future = executor.submit(
            bridge.review,
            fixture.request,
            provider=provider,
            store_factory=_receipt_store_factory(state_root),
        )
        try:
            assert contended.wait(timeout=5)
            with condition:
                assert contended_operations == [receipts.fcntl.LOCK_EX]
                assert waiter_count == 1
                assert owner_fd is not None
                assert not second_future.done()
        finally:
            release.set()
        first = first_future.result(timeout=5)
        second = second_future.result(timeout=5)

    assert calls == 1
    assert first.to_dict() == second.to_dict()


def test_review_receipt_scope_conflict_does_not_unlock_retry(tmp_path: Path) -> None:
    fixture = _authority_fixture(tmp_path / "repo")
    state_root = tmp_path / "state"
    calls = 0

    def provider(resolved: bridge.ResolvedReviewRequest) -> bridge.OpusReview:
        nonlocal calls
        calls += 1
        return _normalized_pass_review(resolved)

    first_request = replace(
        fixture.request, authorization_source="user-task:authority-first"
    )
    bridge.review(
        first_request,
        provider=provider,
        store_factory=_receipt_store_factory(state_root),
    )
    conflicting = replace(
        fixture.request, authorization_source="user-task:authority-second"
    )

    with pytest.raises(receipts.ReceiptStateError) as excinfo:
        bridge.review(
            conflicting,
            provider=provider,
            store_factory=_receipt_store_factory(state_root),
        )

    assert excinfo.value.reason == "attempt_scope_conflict"
    assert calls == 1


def test_review_receipt_abandoned_reservation_degrades_without_provider(
    tmp_path: Path,
) -> None:
    fixture = _authority_fixture(tmp_path / "repo")
    resolved = bridge.resolve_provider_authoritative_scope(fixture.request)
    store = receipts.ReceiptStore.for_repo(
        fixture.root, state_root=tmp_path / "state"
    )
    with store.lock_attempt(resolved.scope) as attempt:
        assert attempt.reserve_or_load(resolved.scope).action == "launch"
    calls = 0

    def forbidden_provider(
        resolved_request: bridge.ResolvedReviewRequest,
    ) -> bridge.OpusReview:
        nonlocal calls
        calls += 1
        raise AssertionError("abandoned reservation must not launch provider")

    result = bridge.review(
        fixture.request,
        provider=forbidden_provider,
        store_factory=lambda repo_root: store,
    )

    assert calls == 0
    assert result.receipt_state == "reviewed"
    assert result.review.status == "unavailable"
    assert result.review.unavailable_reason == "attempt_state_uncertain"
    assert result.review.failure_stage == "receipt_recovery"


def test_review_receipt_changed_head_gets_distinct_attempt(tmp_path: Path) -> None:
    fixture = _authority_fixture(tmp_path / "repo")
    state_root = tmp_path / "state"
    calls = 0

    def provider(resolved: bridge.ResolvedReviewRequest) -> bridge.OpusReview:
        nonlocal calls
        calls += 1
        return _normalized_pass_review(resolved)

    first = bridge.review(
        fixture.request,
        provider=provider,
        store_factory=_receipt_store_factory(state_root),
    )
    feature = fixture.root / "scripts" / "feature.py"
    feature.write_text("VALUE = 'second-head'\n", encoding="utf-8")
    new_head = _commit_shipping_fixture_change(fixture, "scripts/feature.py")
    second = bridge.review(
        replace(
            fixture.request,
            reviewed_head=new_head,
            trigger_commit=new_head,
        ),
        provider=provider,
        store_factory=_receipt_store_factory(state_root),
    )

    assert calls == 2
    assert first.receipt_id != second.receipt_id


def test_review_scope_failure_precedes_store_creation(tmp_path: Path) -> None:
    fixture = _authority_fixture(tmp_path / "repo")
    store_called = False

    def failing_resolver(
        request: bridge.ReviewRequest,
    ) -> bridge.ResolvedReviewRequest:
        raise bridge.ReviewContractError("invalid_scope", "pre-reservation")

    def store_factory(repo_root: Path) -> receipts.ReceiptStore:
        nonlocal store_called
        store_called = True
        return receipts.ReceiptStore.for_repo(
            repo_root, state_root=tmp_path / "state"
        )

    with pytest.raises(bridge.ReviewContractError, match="pre-reservation"):
        bridge.review(
            fixture.request,
            scope_resolver=failing_resolver,
            store_factory=store_factory,
            provider=lambda resolved: _normalized_pass_review(resolved),
        )

    assert not store_called
    assert not (tmp_path / "state").exists()


def test_review_provider_failure_is_sanitized_and_persisted_once(
    tmp_path: Path,
) -> None:
    fixture = _authority_fixture(tmp_path / "repo")
    state_root = tmp_path / "state"
    calls = 0

    def failing_provider(
        resolved: bridge.ResolvedReviewRequest,
    ) -> bridge.OpusReview:
        nonlocal calls
        calls += 1
        raise OSError("RAW-PROVIDER-HOST-DETAIL")

    first = bridge.review(
        fixture.request,
        provider=failing_provider,
        store_factory=_receipt_store_factory(state_root),
    )
    second = bridge.review(
        fixture.request,
        provider=failing_provider,
        store_factory=_receipt_store_factory(state_root),
    )

    assert calls == 1
    assert first.to_dict() == second.to_dict()
    assert first.review.status == "unavailable"
    assert first.review.unavailable_reason == "process_failed"
    assert "RAW-PROVIDER" not in json.dumps(first.to_dict(), sort_keys=True)


def test_review_receipt_write_failure_leaves_reserved_for_uncertain_recovery(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    fixture = _authority_fixture(tmp_path / "repo")
    resolved = bridge.resolve_provider_authoritative_scope(fixture.request)
    store = receipts.ReceiptStore.for_repo(
        fixture.root, state_root=tmp_path / "state"
    )

    def fail_record_review(
        attempt: object, review: object
    ) -> receipts.ReceiptRecord:
        raise receipts.ReceiptStateError(
            "receipt_replace_failed", "RAW-RECEIPT-WRITE-DETAIL"
        )

    monkeypatch.setattr(receipts.LockedAttempt, "record_review", fail_record_review)
    with pytest.raises(bridge.ReviewContractError) as excinfo:
        bridge.review(
            fixture.request,
            provider=_normalized_pass_review,
            store_factory=lambda repo_root: store,
        )
    assert excinfo.value.reason == "receipt_write"
    assert "RAW-RECEIPT" not in str(excinfo.value)

    monkeypatch.undo()
    with store.lock_attempt(resolved.scope) as attempt:
        decision = attempt.reserve_or_load(resolved.scope)
    assert decision.action == "degrade_uncertain"
    assert decision.record.state == "reserved"


def _normalized_issues_review(
    resolved: bridge.ResolvedReviewRequest,
    *,
    severity: str = "important",
) -> bridge.OpusReview:
    return bridge.parse_structured_review(
        _structured_payload(
            status="issues",
            findings=[_finding_payload(severity=severity)],
            reviewed_head=resolved.request.reviewed_head,
            reviewed_base=resolved.scope.effective_base,
        ),
        expected_head=resolved.request.reviewed_head,
        expected_base=resolved.scope.effective_base,
        expected_profile=resolved.scope.review_profile,
        effective_model="claude-opus-4-7",
        authorization_source=resolved.scope.authorization_identity,
    )


def _reviewed_receipt(
    fixture: _AuthorityFixture,
    state_root: Path,
    provider: object = _normalized_pass_review,
) -> tuple[bridge.ReviewReceiptResult, receipts.ReceiptStore]:
    store = receipts.ReceiptStore.for_repo(
        fixture.root, state_root=state_root
    )
    result = bridge.review(
        fixture.request,
        provider=provider,
        store_factory=lambda repo_root: store,
    )
    return result, store


def _reconcile_stored(
    fixture: _AuthorityFixture,
    result: bridge.ReviewReceiptResult,
    store: receipts.ReceiptStore,
    *,
    verdict: str = "GO",
    dispositions: tuple[bridge.FindingDisposition, ...] = (),
) -> bridge.ReconciliationReceiptResult:
    return bridge.reconcile_receipt(
        repo_root=fixture.root,
        receipt_id=result.receipt_id,
        expected_head=fixture.head,
        expected_base=fixture.base,
        codex_verdict=verdict,
        dispositions=dispositions,
        store_factory=lambda repo_root: store,
    )


def _reconciled_record(
    tmp_path: Path,
    *,
    requested_base: bool = True,
) -> tuple[
    _AuthorityFixture,
    bridge.ReconciliationReceiptResult,
    receipts.ReceiptRecord,
]:
    fixture = _authority_fixture(tmp_path / "repo")
    store = receipts.ReceiptStore.for_repo(
        fixture.root, state_root=tmp_path / "state"
    )
    result = bridge.review(
        fixture.request
        if requested_base
        else replace(fixture.request, reviewed_base=None),
        provider=_normalized_pass_review,
        store_factory=lambda repo_root: store,
    )
    reconciled = bridge.reconcile_receipt(
        repo_root=fixture.root,
        receipt_id=result.receipt_id,
        expected_head=fixture.head,
        expected_base=fixture.base if requested_base else None,
        codex_verdict="GO",
        dispositions=(),
        store_factory=lambda repo_root: store,
    )
    with store.lock_receipt(result.receipt_id) as attempt:
        record = attempt.load_existing()
    return fixture, reconciled, record


@pytest.mark.parametrize(
    ("severity", "invalid_verdict", "corrected_verdict"),
    [
        ("minor", "GO", "NITS"),
        ("important", "NITS", "FAIL"),
    ],
)
def test_reconcile_receipt_rejects_severity_mismatch_before_persistence(
    tmp_path: Path,
    severity: str,
    invalid_verdict: str,
    corrected_verdict: str,
) -> None:
    fixture = _authority_fixture(tmp_path / severity)
    result, store = _reviewed_receipt(
        fixture,
        tmp_path / f"state-{severity}",
        lambda resolved: _normalized_issues_review(
            resolved, severity=severity
        ),
    )
    dispositions = (
        bridge.FindingDisposition("OPUS-1", "confirmed", ""),
    )

    with pytest.raises(bridge.ReviewContractError) as excinfo:
        _reconcile_stored(
            fixture,
            result,
            store,
            verdict=invalid_verdict,
            dispositions=dispositions,
        )

    assert excinfo.value.reason == "verdict_severity_mismatch"
    with store.lock_receipt(result.receipt_id) as attempt:
        unchanged = attempt.load_existing()
    assert unchanged.state == "reviewed"
    assert unchanged.reconciliation is None

    corrected = _reconcile_stored(
        fixture,
        result,
        store,
        verdict=corrected_verdict,
        dispositions=dispositions,
    )
    assert corrected.reconciliation.codex_verdict == corrected_verdict
    assert corrected.receipt_state == "reconciled"


@pytest.mark.parametrize("requested_base", ("explicit", "omitted"))
def test_report_reconciliation_scope_returns_canonical_result(
    tmp_path: Path, requested_base: str
) -> None:
    fixture, reconciled, record = _reconciled_record(
        tmp_path, requested_base=requested_base == "explicit"
    )
    assert record.scope["requested_base"] == (
        fixture.base if requested_base == "explicit" else None
    )

    validated = bridge.validated_report_reconciliation_scope(
        fixture.root,
        record,
        fixture.head,
        fixture.base,
    )

    assert validated.to_dict() == reconciled.to_dict()


@pytest.mark.parametrize(
    ("field", "value_attribute"),
    (
        ("reviewed_head", "descriptor_commit"),
        ("effective_base", "descriptor_commit"),
    ),
)
def test_report_reconciliation_scope_rejects_report_and_receipt_scope_mismatch(
    tmp_path: Path, field: str, value_attribute: str
) -> None:
    fixture, _, record = _reconciled_record(tmp_path)
    report_head = fixture.head
    report_base = fixture.base
    if field == "reviewed_head":
        report_head = getattr(fixture, value_attribute)
    else:
        report_base = getattr(fixture, value_attribute)

    with pytest.raises(bridge.ReviewContractError) as excinfo:
        bridge.validated_report_reconciliation_scope(
            fixture.root,
            record,
            report_head,
            report_base,
        )

    assert excinfo.value.reason == "reviewed_scope_mismatch"


@pytest.mark.parametrize("requested_base", ("mismatch", "missing"))
def test_report_reconciliation_scope_rejects_invalid_requested_base_relation(
    tmp_path: Path, requested_base: str
) -> None:
    fixture, _, record = _reconciled_record(tmp_path)
    scope = dict(record.scope)
    if requested_base == "mismatch":
        scope["requested_base"] = fixture.descriptor_commit
    else:
        del scope["requested_base"]

    with pytest.raises(bridge.ReviewContractError) as excinfo:
        bridge.validated_report_reconciliation_scope(
            fixture.root,
            replace(record, scope=scope),
            fixture.head,
            fixture.base,
        )

    assert excinfo.value.reason == "invalid_receipt_scope"


def test_report_reconciliation_scope_rejects_other_repository(
    tmp_path: Path,
) -> None:
    fixture, _, record = _reconciled_record(tmp_path)
    other = _authority_fixture(
        tmp_path / "other",
        descriptor_task_id="aaaaaaaa-bbbb-4ccc-8ddd-eeeeeeeeeeee",
        descriptor_path_task_id="aaaaaaaa-bbbb-4ccc-8ddd-eeeeeeeeeeee",
    )

    with pytest.raises(bridge.ReviewContractError) as excinfo:
        bridge.validated_report_reconciliation_scope(
            other.root,
            record,
            fixture.head,
            fixture.base,
        )

    assert excinfo.value.reason == "receipt_repository_mismatch"


@pytest.mark.parametrize("missing_field", ("reviewed_head", "effective_base"))
def test_report_reconciliation_scope_requires_stored_commits_to_exist(
    tmp_path: Path, missing_field: str
) -> None:
    fixture, _, record = _reconciled_record(tmp_path)
    missing = "f" * 40
    scope = dict(record.scope)
    scope[missing_field] = missing
    if missing_field == "effective_base":
        scope["requested_base"] = None

    with pytest.raises(bridge.ReviewContractError) as excinfo:
        bridge.validated_report_reconciliation_scope(
            fixture.root,
            replace(record, scope=scope),
            missing if missing_field == "reviewed_head" else fixture.head,
            missing if missing_field == "effective_base" else fixture.base,
        )

    assert excinfo.value.reason == "invalid_scope"


def test_report_reconciliation_scope_requires_base_to_precede_head(
    tmp_path: Path,
) -> None:
    fixture, _, record = _reconciled_record(tmp_path)
    tree = _git(fixture.root, "show", "-s", "--format=%T", fixture.head)
    unrelated = _git(
        fixture.root,
        "commit-tree",
        tree,
        "-m",
        "test: unrelated root",
    )
    scope = dict(record.scope)
    scope["effective_base"] = unrelated
    scope["requested_base"] = None

    with pytest.raises(bridge.ReviewContractError) as excinfo:
        bridge.validated_report_reconciliation_scope(
            fixture.root,
            replace(record, scope=scope),
            fixture.head,
            unrelated,
        )

    assert excinfo.value.reason == "invalid_scope"


@pytest.mark.parametrize(
    ("scope_field", "report_head_attribute", "report_base_attribute"),
    (
        ("reviewed_head", "descriptor_commit", "base"),
        ("effective_base", "head", "descriptor_commit"),
    ),
)
def test_report_reconciliation_scope_rejects_reconciliation_scope_mismatch(
    tmp_path: Path,
    scope_field: str,
    report_head_attribute: str,
    report_base_attribute: str,
) -> None:
    fixture, _, record = _reconciled_record(tmp_path)
    scope = dict(record.scope)
    scope[scope_field] = getattr(
        fixture,
        report_head_attribute
        if scope_field == "reviewed_head"
        else report_base_attribute,
    )
    scope["requested_base"] = None

    with pytest.raises(bridge.ReviewContractError) as excinfo:
        bridge.validated_report_reconciliation_scope(
            fixture.root,
            replace(record, scope=scope),
            getattr(fixture, report_head_attribute),
            getattr(fixture, report_base_attribute),
        )

    assert excinfo.value.reason == "invalid_receipt_reconciliation"


@pytest.mark.parametrize(
    ("section", "field", "value_attribute"),
    (
        ("input", "expected_head", "descriptor_commit"),
        ("input", "expected_base", "descriptor_commit"),
        ("result", "reviewed_head", "descriptor_commit"),
        ("result", "reviewed_base", "descriptor_commit"),
    ),
)
def test_report_reconciliation_scope_rejects_each_input_and_result_commit_mismatch(
    tmp_path: Path,
    section: str,
    field: str,
    value_attribute: str,
) -> None:
    fixture, _, record = _reconciled_record(tmp_path)
    assert record.reconciliation is not None
    wrapper = dict(record.reconciliation)
    changed = dict(wrapper[section])
    changed[field] = getattr(fixture, value_attribute)
    wrapper[section] = changed
    if section == "input":
        wrapper["input_digest"] = "sha256:" + hashlib.sha256(
            receipts.canonical_json_bytes(changed)
        ).hexdigest()

    with pytest.raises(bridge.ReviewContractError) as excinfo:
        bridge.validated_report_reconciliation_scope(
            fixture.root,
            replace(record, reconciliation=wrapper),
            fixture.head,
            fixture.base,
        )

    assert excinfo.value.reason == "invalid_receipt_reconciliation"


def test_report_reconciliation_scope_requires_canonical_reconciliation(
    tmp_path: Path,
) -> None:
    fixture, _, record = _reconciled_record(tmp_path)

    with pytest.raises(bridge.ReviewContractError) as excinfo:
        bridge.validated_report_reconciliation_scope(
            fixture.root,
            replace(record, reconciliation=None),
            fixture.head,
            fixture.base,
        )

    assert excinfo.value.reason == "invalid_receipt_reconciliation"


def test_reconcile_receipt_has_no_fabricated_review_input() -> None:
    parameters = inspect.signature(bridge.reconcile_receipt).parameters
    assert "review" not in parameters
    assert "opus_review_json" not in parameters
    assert "receipt_id" in parameters


def test_reconcile_receipt_rejects_malformed_id_before_store_initialization(
    tmp_path: Path,
) -> None:
    fixture = _authority_fixture(tmp_path / "repo")
    state_root = tmp_path / "receipt-state"
    factory_calls = 0

    def store_factory(repo_root: Path) -> receipts.ReceiptStore:
        nonlocal factory_calls
        factory_calls += 1
        return receipts.ReceiptStore.for_repo(
            repo_root,
            state_root=state_root,
        )

    with pytest.raises(
        (bridge.ReviewContractError, receipts.ReceiptContractError)
    ) as excinfo:
        bridge.reconcile_receipt(
            repo_root=fixture.root,
            receipt_id="opr1:not-canonical",
            expected_head=fixture.head,
            expected_base=fixture.base,
            codex_verdict="GO",
            dispositions=(),
            store_factory=store_factory,
        )

    assert factory_calls == 0
    assert not state_root.exists()
    assert isinstance(excinfo.value, bridge.ReviewContractError)
    assert excinfo.value.reason == "invalid_receipt_id"


def test_reconcile_receipt_rejects_wrong_repo_head_base_and_receipt(
    tmp_path: Path,
) -> None:
    fixture = _authority_fixture(tmp_path / "repo")
    result, store = _reviewed_receipt(fixture, tmp_path / "state")
    other = _authority_fixture(tmp_path / "other")

    cases = (
        {"repo_root": other.root},
        {"expected_head": fixture.base},
        {"expected_base": fixture.head},
        {"receipt_id": "opr1:" + "f" * 64},
    )
    for changes in cases:
        arguments = {
            "repo_root": fixture.root,
            "receipt_id": result.receipt_id,
            "expected_head": fixture.head,
            "expected_base": fixture.base,
            "codex_verdict": "GO",
            "dispositions": (),
            "store_factory": lambda repo_root: store,
        }
        arguments.update(changes)
        with pytest.raises(
            (bridge.ReviewContractError, receipts.ReceiptStateError)
        ):
            bridge.reconcile_receipt(**arguments)


def test_reconcile_requires_originally_explicit_base_and_allows_retry(
    tmp_path: Path,
) -> None:
    fixture = _authority_fixture(tmp_path / "repo")
    result, store = _reviewed_receipt(fixture, tmp_path / "state")

    for supplied_base in (None, fixture.descriptor_commit):
        with pytest.raises(bridge.ReviewContractError) as excinfo:
            bridge.reconcile_receipt(
                repo_root=fixture.root,
                receipt_id=result.receipt_id,
                expected_head=fixture.head,
                expected_base=supplied_base,
                codex_verdict="GO",
                dispositions=(),
                store_factory=lambda repo_root: store,
            )
        assert excinfo.value.reason == "reviewed_scope_mismatch"

    retry = _reconcile_stored(fixture, result, store)
    assert retry.receipt_state == "reconciled"


def test_reconcile_requires_base_omission_when_review_omitted_it(
    tmp_path: Path,
) -> None:
    fixture = _authority_fixture(tmp_path / "repo")
    store = receipts.ReceiptStore.for_repo(
        fixture.root, state_root=tmp_path / "state"
    )
    result = bridge.review(
        replace(fixture.request, reviewed_base=None),
        provider=_normalized_pass_review,
        store_factory=lambda repo_root: store,
    )

    with pytest.raises(bridge.ReviewContractError) as excinfo:
        bridge.reconcile_receipt(
            repo_root=fixture.root,
            receipt_id=result.receipt_id,
            expected_head=fixture.head,
            expected_base=fixture.base,
            codex_verdict="GO",
            dispositions=(),
            store_factory=lambda repo_root: store,
        )
    assert excinfo.value.reason == "reviewed_scope_mismatch"

    reconciled = bridge.reconcile_receipt(
        repo_root=fixture.root,
        receipt_id=result.receipt_id,
        expected_head=fixture.head,
        expected_base=None,
        codex_verdict="GO",
        dispositions=(),
        store_factory=lambda repo_root: store,
    )
    assert reconciled.receipt_state == "reconciled"


def test_reconcile_receipt_exact_replay_and_exact_evidence_hash(
    tmp_path: Path,
) -> None:
    fixture = _authority_fixture(tmp_path / "repo")
    result, store = _reviewed_receipt(
        fixture,
        tmp_path / "state",
        lambda resolved: _normalized_issues_review(resolved),
    )
    evidence = "  focused test exits 0  "
    dispositions = (
        bridge.FindingDisposition("OPUS-1", "disproved", evidence),
    )

    first = _reconcile_stored(
        fixture, result, store, dispositions=dispositions
    )
    second = _reconcile_stored(
        fixture, result, store, dispositions=dispositions
    )

    assert first.to_dict() == second.to_dict()
    assert first.receipt_state == second.receipt_state == "reconciled"
    assert first.reconciliation.go_allowed
    with store.lock_receipt(result.receipt_id) as attempt:
        record = attempt.load_existing()
    assert record.reconciliation is not None
    persisted = record.reconciliation["input"]["dispositions"]["OPUS-1"]
    assert persisted == {
        "disposition": "disproved",
        "evidence": evidence,
        "evidence_digest": "sha256:"
        + hashlib.sha256(evidence.encode("utf-8")).hexdigest(),
    }


def test_reconcile_receipt_empty_evidence_hashes_as_none(tmp_path: Path) -> None:
    fixture = _authority_fixture(tmp_path / "repo")
    result, store = _reviewed_receipt(
        fixture,
        tmp_path / "state",
        lambda resolved: _normalized_issues_review(resolved),
    )

    _reconcile_stored(
        fixture,
        result,
        store,
        dispositions=(
            bridge.FindingDisposition("OPUS-1", "unresolved", ""),
        ),
    )

    with store.lock_receipt(result.receipt_id) as attempt:
        record = attempt.load_existing()
    assert record.reconciliation is not None
    persisted = record.reconciliation["input"]["dispositions"]["OPUS-1"]
    assert persisted["evidence_digest"] == "none"


def _disposition_with_attestation_line_bytes(
    target_bytes: int,
) -> bridge.FindingDisposition:
    def rendered_size(evidence: str) -> int:
        mapping = {
            "OPUS-1": {
                "disposition": "unresolved",
                "evidence": evidence,
                "evidence_digest": "sha256:"
                + hashlib.sha256(evidence.encode("utf-8")).hexdigest(),
            }
        }
        rendered = receipts.canonical_json_bytes(mapping).decode("utf-8")
        return len(f"Opus finding dispositions: {rendered}".encode("utf-8"))

    fixed_bytes = rendered_size("x") - 1
    evidence = "x" * (target_bytes - fixed_bytes)
    assert rendered_size(evidence) == target_bytes
    return bridge.FindingDisposition("OPUS-1", "unresolved", evidence)


def test_reconcile_attestation_line_exact_byte_limit_is_publishable(
    tmp_path: Path,
) -> None:
    fixture = _authority_fixture(tmp_path / "repo")
    result, store = _reviewed_receipt(
        fixture,
        tmp_path / "state",
        lambda resolved: _normalized_issues_review(resolved),
    )

    reconciled = _reconcile_stored(
        fixture,
        result,
        store,
        dispositions=(_disposition_with_attestation_line_bytes(49_152),),
    )

    assert bridge.REPORT_ATTESTATION_LINE_LIMIT_BYTES == 49_152
    assert reconciled.receipt_state == "reconciled"


def test_oversized_attestation_leaves_reviewed_and_allows_smaller_retry(
    tmp_path: Path,
) -> None:
    fixture = _authority_fixture(tmp_path / "repo")
    result, store = _reviewed_receipt(
        fixture,
        tmp_path / "state",
        lambda resolved: _normalized_issues_review(resolved),
    )

    with pytest.raises(bridge.ReviewContractError) as excinfo:
        _reconcile_stored(
            fixture,
            result,
            store,
            dispositions=(_disposition_with_attestation_line_bytes(49_153),),
        )

    assert excinfo.value.reason == "attestation_line_too_large"
    assert "x" * 100 not in str(excinfo.value)
    with store.lock_receipt(result.receipt_id) as attempt:
        assert attempt.load_existing().state == "reviewed"

    retry = _reconcile_stored(
        fixture,
        result,
        store,
        dispositions=(_disposition_with_attestation_line_bytes(49_152),),
    )
    assert retry.receipt_state == "reconciled"


def test_stored_reconciliation_is_recomputed_before_replay(
    tmp_path: Path,
) -> None:
    fixture = _authority_fixture(tmp_path / "repo")
    result, store = _reviewed_receipt(fixture, tmp_path / "state")
    _reconcile_stored(fixture, result, store)
    with store.lock_receipt(result.receipt_id) as attempt:
        record = attempt.load_existing()
    assert record.reconciliation is not None
    tampered_wrapper = dict(record.reconciliation)
    tampered_result = dict(tampered_wrapper["result"])
    tampered_report = dict(tampered_result["report_fields"])
    tampered_report["Degraded reason"] = "fabricated"
    tampered_result["report_fields"] = tampered_report
    tampered_wrapper["result"] = tampered_result

    with pytest.raises(bridge.ReviewContractError) as excinfo:
        bridge.stored_reconciliation_from_record(
            replace(record, reconciliation=tampered_wrapper)
        )

    assert excinfo.value.reason == "invalid_receipt_reconciliation"


def test_reconcile_receipt_conflicting_replays_fail_closed(
    tmp_path: Path,
) -> None:
    fixture = _authority_fixture(tmp_path / "repo")
    result, store = _reviewed_receipt(
        fixture,
        tmp_path / "state",
        lambda resolved: _normalized_issues_review(resolved),
    )
    original = (
        bridge.FindingDisposition("OPUS-1", "unresolved", ""),
    )
    _reconcile_stored(fixture, result, store, dispositions=original)

    conflicts = (
        {
            "verdict": "NITS",
            "dispositions": original,
        },
        {
            "verdict": "FAIL",
            "dispositions": (
                bridge.FindingDisposition("OPUS-1", "confirmed", ""),
            ),
        },
        {
            "dispositions": (
                bridge.FindingDisposition("OPUS-1", "unresolved", "changed"),
            )
        },
    )
    for changes in conflicts:
        with pytest.raises(receipts.ReceiptStateError) as excinfo:
            _reconcile_stored(fixture, result, store, **changes)
        assert excinfo.value.reason == "reconciliation_replay_conflict"

    with pytest.raises(bridge.ReviewContractError):
        bridge.reconcile_receipt(
            repo_root=fixture.root,
            receipt_id=result.receipt_id,
            expected_head=fixture.base,
            expected_base=fixture.base,
            codex_verdict="GO",
            dispositions=original,
            store_factory=lambda repo_root: store,
        )


def test_reconcile_receipt_simultaneous_identical_calls_converge(
    tmp_path: Path,
) -> None:
    fixture = _authority_fixture(tmp_path / "repo")
    result, store = _reviewed_receipt(fixture, tmp_path / "state")

    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = [
            executor.submit(_reconcile_stored, fixture, result, store)
            for _ in range(2)
        ]
        outputs = [future.result(timeout=5).to_dict() for future in futures]

    assert outputs[0] == outputs[1]


def test_reconcile_receipt_simultaneous_conflict_has_one_winner(
    tmp_path: Path,
) -> None:
    fixture = _authority_fixture(tmp_path / "repo")
    result, store = _reviewed_receipt(fixture, tmp_path / "state")
    barrier = threading.Barrier(2)

    def reconcile_with(verdict: str) -> bridge.ReconciliationReceiptResult:
        barrier.wait(timeout=5)
        return _reconcile_stored(
            fixture, result, store, verdict=verdict
        )

    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = [
            executor.submit(reconcile_with, verdict)
            for verdict in ("GO", "NITS")
        ]
        successes = []
        failures = []
        for future in futures:
            try:
                successes.append(future.result(timeout=5))
            except receipts.ReceiptStateError as exc:
                failures.append(exc)

    assert len(successes) == 1
    assert [failure.reason for failure in failures] == [
        "reconciliation_replay_conflict"
    ]


@pytest.mark.parametrize("status", ["pass", "unavailable"])
def test_reconcile_pass_and_unavailable_reject_dispositions(
    tmp_path: Path, status: str
) -> None:
    fixture = _authority_fixture(tmp_path / status)

    def provider(resolved: bridge.ResolvedReviewRequest) -> bridge.OpusReview:
        if status == "pass":
            return _normalized_pass_review(resolved)
        return bridge.OpusReview.unavailable(
            reviewed_head=resolved.scope.reviewed_head,
            reviewed_base=resolved.scope.effective_base,
            review_profile=resolved.scope.review_profile,
            authorization_source=resolved.scope.authorization_identity,
            reason="timeout",
        )

    result, store = _reviewed_receipt(
        fixture, tmp_path / f"state-{status}", provider
    )

    with pytest.raises(bridge.ReviewContractError) as excinfo:
        _reconcile_stored(
            fixture,
            result,
            store,
            dispositions=(
                bridge.FindingDisposition("OPUS-1", "unresolved", ""),
            ),
        )
    assert excinfo.value.reason == "unexpected_dispositions"


def test_reconciliation_report_fields_are_canonical_and_ordered(
    tmp_path: Path,
) -> None:
    fixture = _authority_fixture(tmp_path / "repo")
    result, store = _reviewed_receipt(fixture, tmp_path / "state")

    reconciled = _reconcile_stored(fixture, result, store)

    assert tuple(reconciled.report_fields) == (
        "Review profile",
        "Authorization identity",
        "Opus receipt ID",
        "Opus scope digest",
        "Cross-model review",
        "Effective Opus model",
        "Opus finding dispositions",
        "Reconciliation guard",
        "Degraded reason",
    )
    assert reconciled.report_fields["Review profile"] == "codex-lane-v"
    assert reconciled.report_fields["Opus receipt ID"] == result.receipt_id
    assert reconciled.report_fields["Opus finding dispositions"] == "none"
    assert json.loads(reconciled.report_fields["Reconciliation guard"]) == {
        "digest": reconciled.input_digest,
        "go_allowed": True,
    }


def _committed_request(
    tmp_path: Path,
    *,
    route_test_source: str = "def test_fixture():\n    assert True\n",
) -> bridge._ProviderReviewRequest:
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
) -> bridge._ProviderReviewRequest:
    return replace(
        _committed_request(tmp_path),
        authorization_source=authorization,
    )


def _sandbox_probe_request(
    tmp_path: Path, test_source: str
) -> bridge._ProviderReviewRequest:
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
    request: bridge._ProviderReviewRequest,
    *,
    runner: object,
    resolver: object | None = None,
    sandbox_probe: object | None = None,
    agent_prompt: str = "PINNED-TEST-ADVISORY-PROMPT",
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

    return bridge._perform_provider_review(
        request,
        agent_prompt=agent_prompt,
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


def test_review_runs_in_immutable_head_snapshot_with_preverified_prompt(
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
        assert verifier_prompt == "PINNED-TEST-ADVISORY-PROMPT"
        assert "BASE-TRUSTED-AGENT" not in verifier_prompt
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


def test_low_level_review_requires_an_already_verified_provider_prompt(
    tmp_path: Path,
) -> None:
    request = replace(_committed_request(tmp_path), reviewed_base=None)

    def forbidden_runner(*args: object, **kwargs: object) -> object:
        raise AssertionError("provider must not run without a verified prompt")

    with pytest.raises(bridge.ReviewContractError) as excinfo:
        bridge._perform_provider_review(request, runner=forbidden_runner)

    assert excinfo.value.reason == "invalid_provider_prompt"


def test_review_rejects_explicit_base_that_does_not_precede_head(
    tmp_path: Path,
) -> None:
    fixture = _prompt_authority_fixture(tmp_path / "repo")
    request = replace(fixture.request, reviewed_base=fixture.head)
    calls = 0

    def forbidden_store(root: Path) -> receipts.ReceiptStore:
        del root
        nonlocal calls
        calls += 1
        raise AssertionError("store must not open for a mismatched base")

    with pytest.raises(bridge.ReviewContractError) as excinfo:
        bridge.review(request, store_factory=forbidden_store)

    assert excinfo.value.reason == "reviewed_scope_mismatch"
    assert calls == 0


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
    request: bridge._ProviderReviewRequest,
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

    result = bridge._perform_provider_review(
        request,
        agent_prompt="PINNED-TEST-ADVISORY-PROMPT",
        runner=fake_runner,
    )
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


def test_verification_broker_close_linearizes_with_inflight_spawn(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source = tmp_path / "source"
    snapshot = tmp_path / "snapshot"
    source.mkdir()
    snapshot.mkdir()
    popen_created = threading.Event()
    allow_popen_return = threading.Event()
    close_probed_lock = threading.Event()
    close_observed_active_spawn: list[bool] = []
    child_alive_when_close_returned: list[bool] = []
    spawned: list[subprocess.Popen[bytes]] = []
    responses: list[dict[str, object]] = []
    real_popen = subprocess.Popen

    class ObservedLock:
        def __init__(self) -> None:
            self._lock = threading.Lock()

        def __enter__(self) -> ObservedLock:
            if threading.current_thread().name == "broker-close":
                acquired = self._lock.acquire(blocking=False)
                close_observed_active_spawn.append(not acquired)
                close_probed_lock.set()
                if not acquired:
                    self._lock.acquire()
            else:
                self._lock.acquire()
            return self

        def __exit__(self, *exc_info: object) -> None:
            self._lock.release()

    def held_popen(*args: object, **kwargs: object) -> subprocess.Popen[bytes]:
        process = real_popen(*args, **kwargs)
        spawned.append(process)
        popen_created.set()
        if not allow_popen_return.wait(timeout=5):
            bridge._terminate_process_group(process)
            raise AssertionError("test did not release the Popen return seam")
        return process

    with bridge._sandbox_runtime(source, snapshot) as runtime:
        broker = bridge._VerificationBroker(
            runtime,
            snapshot,
            timeout_seconds=30,
        )
        broker._lock = ObservedLock()
        monkeypatch.setattr(bridge.subprocess, "Popen", held_popen)
        client = broker.register(
            [sys.executable, "-c", "import time; time.sleep(30)"]
        )
        token = client[-2]
        response_thread = threading.Thread(
            target=lambda: responses.append(broker._response_for_token(token)),
            name="broker-response",
        )

        def close_broker() -> None:
            broker.close()
            child_alive_when_close_returned.append(spawned[0].poll() is None)

        close_thread = threading.Thread(target=close_broker, name="broker-close")
        try:
            response_thread.start()
            assert popen_created.wait(timeout=5)
            close_thread.start()
            assert close_probed_lock.wait(timeout=5)
            allow_popen_return.set()
            close_thread.join(timeout=5)
            assert not close_thread.is_alive()
            if spawned[0].poll() is None:
                bridge._terminate_process_group(spawned[0])
            response_thread.join(timeout=5)
            assert not response_thread.is_alive()
        finally:
            allow_popen_return.set()
            if spawned and spawned[0].poll() is None:
                bridge._terminate_process_group(spawned[0])
            response_thread.join(timeout=5)
            close_thread.join(timeout=5)
            broker.close()

    assert close_observed_active_spawn[0] is True
    assert child_alive_when_close_returned == [False]
    assert len(responses) == 1


def test_verification_broker_rejects_registration_after_close(
    tmp_path: Path,
) -> None:
    source = tmp_path / "source"
    snapshot = tmp_path / "snapshot"
    source.mkdir()
    snapshot.mkdir()

    with bridge._sandbox_runtime(source, snapshot) as runtime:
        broker = bridge._VerificationBroker(
            runtime,
            snapshot,
            timeout_seconds=5,
        )
        broker.close()

        with pytest.raises(RuntimeError, match="broker is closed"):
            broker.register([sys.executable, "-c", "pass"])


def test_verification_broker_rejects_registered_token_after_close_without_admission(
    tmp_path: Path,
) -> None:
    source = tmp_path / "source"
    snapshot = tmp_path / "snapshot"
    source.mkdir()
    snapshot.mkdir()

    with bridge._sandbox_runtime(source, snapshot) as runtime:
        broker = bridge._VerificationBroker(
            runtime,
            snapshot,
            timeout_seconds=5,
        )
        client = broker.register([sys.executable, "-c", "pass"])
        token = client[-2]
        broker.close()

        response = broker._response_for_token(token)

    assert response == broker._rejected_payload()
    assert token not in broker._used


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


@pytest.mark.parametrize("forbidden_name", FORBIDDEN_CLAUDE_ENVIRONMENT)
def test_probe_host_capabilities_rejects_overrides_before_any_probe(
    monkeypatch: pytest.MonkeyPatch,
    forbidden_name: str,
) -> None:
    for name in FORBIDDEN_CLAUDE_ENVIRONMENT:
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv(forbidden_name, "")
    calls: list[str] = []

    def forbidden(*args: object, **kwargs: object) -> object:
        calls.append("called")
        raise AssertionError("no capability probe may run")

    with pytest.raises(bridge.ReviewContractError) as excinfo:
        bridge.probe_host_capabilities(
            command_probe=forbidden,
            socket_probe=forbidden,
            claude_resolver=forbidden,
        )

    assert excinfo.value.reason == "forbidden_environment"
    assert forbidden_name in str(excinfo.value)
    assert calls == []


def test_clean_existing_session_environment_is_forwarded_without_overrides() -> None:
    source = {
        "HOME": "/Users/example",
        "PATH": "/usr/bin:/bin",
        "LANG": "en_US.UTF-8",
        "LC_ALL": "en_US.UTF-8",
        "LOGNAME": "example",
        "SHELL": "/bin/zsh",
        "SSL_CERT_DIR": "/etc/ssl/certs",
        "SSL_CERT_FILE": "/etc/ssl/cert.pem",
        "TERM": "xterm-256color",
        "TMPDIR": "/tmp/example",
        "USER": "example",
        "UNRELATED": "must-not-be-forwarded",
    }

    child = bridge.build_claude_environment(source)

    for key, value in source.items():
        if key != "UNRELATED":
            assert child[key] == value
    assert "UNRELATED" not in child
    assert not (set(child) & set(FORBIDDEN_CLAUDE_ENVIRONMENT))


@pytest.mark.parametrize("forbidden_name", FORBIDDEN_CLAUDE_ENVIRONMENT)
def test_forbidden_existing_session_override_blocks_before_any_host_seam(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    forbidden_name: str,
) -> None:
    request = _uncommitted_request(tmp_path)
    for name in FORBIDDEN_CLAUDE_ENVIRONMENT:
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv(forbidden_name, "")
    calls: list[str] = []

    def forbidden(*args: object, **kwargs: object) -> object:
        calls.append("called")
        raise AssertionError("no host seam may run")

    monkeypatch.setattr(bridge, "_require_git_repository", forbidden)

    with pytest.raises(bridge.ReviewContractError) as excinfo:
        bridge._perform_provider_review(
            request,
            agent_prompt="PINNED-TEST-ADVISORY-PROMPT",
            resolver=forbidden,
            runtime_factory=forbidden,
            runner=forbidden,
        )

    assert excinfo.value.reason == "forbidden_environment"
    assert forbidden_name in str(excinfo.value)
    assert calls == []


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

    result = bridge._perform_provider_review(
        request,
        agent_prompt="PINNED-TEST-ADVISORY-PROMPT",
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
    assert result.failure_stage == "provider_exit"
    assert result.stdout_truncated is True
    assert result.stderr_truncated is False
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

    result = bridge._perform_provider_review(
        request,
        agent_prompt="PINNED-TEST-ADVISORY-PROMPT",
        runner=fake_runner,
    )

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

    result = bridge._perform_provider_review(
        request,
        agent_prompt="PINNED-TEST-ADVISORY-PROMPT",
        runner=fake_runner,
    )

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
    result = bridge._perform_provider_review(
        _committed_request(tmp_path),
        agent_prompt="PINNED-TEST-ADVISORY-PROMPT",
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
        bridge._perform_provider_review(request)

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

    result = bridge._perform_provider_review(
        request,
        agent_prompt="PINNED-TEST-ADVISORY-PROMPT",
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
    request = bridge._ProviderReviewRequest(
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
        bridge._perform_provider_review(request)

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


def test_review_cli_rejects_caller_selected_scope_lists() -> None:
    common = [
        "review",
        "--repo-root",
        ".",
        "--head",
        "b" * 40,
        "--review-profile",
        "codex-lane-v",
        "--transport-profile",
        EXISTING_SESSION_TRANSPORT_PROFILE,
    ]
    for old_flag in ("--requirement", "--allow-path", "--verification-command"):
        with pytest.raises(SystemExit):
            bridge._parser().parse_args([*common, old_flag, "x"])


@pytest.mark.parametrize(
    "transport_arguments",
    [
        (),
        ("--transport-profile", "anthropic-api-v1"),
    ],
    ids=["missing", "wrong"],
)
def test_review_cli_rejects_missing_or_wrong_transport_profile_before_reviewer(
    transport_arguments: tuple[str, ...],
) -> None:
    calls = 0

    def forbidden_reviewer(request: bridge.ReviewRequest) -> bridge.ReviewReceiptResult:
        nonlocal calls
        calls += 1
        raise AssertionError("reviewer must not run for an invalid transport profile")

    with pytest.raises(SystemExit):
        bridge.main(
            [
                "review",
                "--repo-root",
                ".",
                "--head",
                HEAD,
                "--shipping-commit",
                HEAD,
                "--review-profile",
                "codex-lane-v",
                *transport_arguments,
            ],
            reviewer=forbidden_reviewer,
        )

    assert calls == 0


def test_reconcile_cli_rejects_caller_json() -> None:
    with pytest.raises(SystemExit):
        bridge._parser().parse_args(
            [
                "reconcile",
                "--repo-root",
                ".",
                "--head",
                "b" * 40,
                "--codex-verdict",
                "GO",
                "--opus-review-json",
                "{}",
            ]
        )


def test_reconcile_cli_requires_receipt_id() -> None:
    receipt_id = "opr1:" + "a" * 64
    args = bridge._parser().parse_args(
        [
            "reconcile",
            "--repo-root",
            ".",
            "--receipt-id",
            receipt_id,
            "--head",
            "b" * 40,
            "--codex-verdict",
            "GO",
        ]
    )

    assert args.receipt_id == receipt_id


def test_review_cli_requires_and_emits_review_profile(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    def fake_reviewer(
        request: bridge.ReviewRequest,
    ) -> bridge.ReviewReceiptResult:
        assert request.reviewed_head == HEAD
        assert request.reviewed_base == BASE
        assert request.review_profile == "codex-lane-v"
        assert request.authorization_source == "user-task:verification-1"
        assert request.trigger_kind == "shipping-commit"
        assert request.trigger_commit == HEAD
        review = bridge.parse_structured_review(
            _structured_payload(),
            expected_head=HEAD,
            expected_base=BASE,
            expected_profile=request.review_profile,
            effective_model="claude-opus-4-7",
            authorization_source=request.authorization_source,
        )
        return bridge.ReviewReceiptResult(
            review=review,
            receipt_id="opr1:" + "a" * 64,
            scope_digest="sha256:" + "b" * 64,
            receipt_state="reviewed",
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
            "--shipping-commit",
            HEAD.upper(),
            "--review-profile",
            "codex-lane-v",
            "--transport-profile",
            EXISTING_SESSION_TRANSPORT_PROFILE,
            "--authorization-source",
            "user-task:verification-1",
        ],
        reviewer=fake_reviewer,
    )

    assert rc == 0
    payload = json.loads(capsys.readouterr().out)
    assert tuple(payload) == tuple(sorted(payload))
    assert payload["schema_version"] == "opus-review/v3"
    assert payload["review_profile"] == "codex-lane-v"
    assert payload["status"] == "pass"
    assert payload["receipt_id"] == "opr1:" + "a" * 64


def test_reconcile_cli_passes_receipt_and_exact_evidence(
    capsys: pytest.CaptureFixture[str],
) -> None:
    finding = _finding_payload()
    finding["id"] = "OPUS.safe_1-2"
    review = bridge.parse_structured_review(
        _structured_payload(status="issues", findings=[finding]),
        expected_head=HEAD,
        expected_base=BASE,
        expected_profile="codex-lane-v",
        effective_model="claude-opus-4-7",
        authorization_source="user-task:verification-1",
    )
    receipt_id = "opr1:" + "a" * 64
    evidence = "  focused round-trip evidence  "
    report_field_names = (
        "Review profile",
        "Authorization identity",
        "Opus receipt ID",
        "Opus scope digest",
        "Cross-model review",
        "Effective Opus model",
        "Opus finding dispositions",
        "Reconciliation guard",
        "Degraded reason",
    )

    def fake_reconciler(**kwargs: object) -> bridge.ReconciliationReceiptResult:
        assert kwargs["receipt_id"] == receipt_id
        dispositions = kwargs["dispositions"]
        assert dispositions == [
            bridge.FindingDisposition("OPUS.safe_1-2", "disproved", evidence)
        ]
        reconciliation = bridge._reconcile_review(
            str(kwargs["codex_verdict"]),
            review,
            dispositions,
            expected_head=str(kwargs["expected_head"]),
            expected_base=str(kwargs["expected_base"]),
        )
        return bridge.ReconciliationReceiptResult(
            reconciliation=reconciliation,
            receipt_id=receipt_id,
            scope_digest="sha256:" + "b" * 64,
            receipt_state="reconciled",
            input_digest="sha256:" + "c" * 64,
            report_fields={name: name for name in report_field_names},
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
            "--receipt-id",
            receipt_id,
            "--disposition",
            "OPUS.safe_1-2=disproved",
            "--evidence",
            "OPUS.safe_1-2=" + evidence,
        ],
        reconciler=fake_reconciler,
    )

    assert rc == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["schema_version"] == "opus-reconciliation/v2"
    assert payload["go_allowed"] is True
    assert payload["disproved_finding_ids"] == ["OPUS.safe_1-2"]
    assert tuple(payload["report_fields"]) == report_field_names


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
    receipt_id = "opr1:" + "a" * 64

    def fake_reconciler(**kwargs: object) -> bridge.ReconciliationReceiptResult:
        bridge._reconcile_review(
            str(kwargs["codex_verdict"]),
            review,
            kwargs["dispositions"],
            expected_head=str(kwargs["expected_head"]),
            expected_base=str(kwargs["expected_base"]),
        )
        raise AssertionError("missing evidence must not reconcile")

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
            "--receipt-id",
            receipt_id,
            "--disposition",
            "OPUS-1=disproved",
        ],
        reconciler=fake_reconciler,
    )

    captured = capsys.readouterr()
    assert rc == 2
    assert "disproof_evidence_missing" in captured.err
