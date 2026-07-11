from __future__ import annotations

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
    *, status: str = "pass", findings: list[dict[str, object]] | None = None
) -> dict[str, object]:
    return {
        "schema_version": "opus-review/v1",
        "reviewed_head": HEAD,
        "reviewed_base": BASE,
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


def test_reconcile_blocks_unresolved_finding() -> None:
    review = bridge.parse_structured_review(
        _structured_payload(status="issues", findings=[_finding_payload()]),
        expected_head=HEAD,
        expected_base=BASE,
        effective_model="claude-opus-4-7",
        authorization_source="user-task:verification-1",
    )

    result = bridge.reconcile(
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
        bridge.reconcile(
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

    result = bridge.reconcile(codex_verdict, review, [])

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

    result = bridge.reconcile(
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

    result = bridge.reconcile(
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

    result = bridge.reconcile(
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

    result = bridge.reconcile(codex_verdict, review, [])

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
        bridge.reconcile("GO", review, [])

    assert excinfo.value.reason == "disposition_mismatch"
