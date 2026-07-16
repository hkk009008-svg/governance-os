#!/usr/bin/env python3
"""Strict read-only boundary for host-normalized v1 observations."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import asdict, dataclass, replace
from hashlib import sha256
import json
from pathlib import Path
from re import fullmatch
import sys

# A direct `python scripts/capability_v1_adapter.py` launch otherwise exposes
# only `scripts/` on sys.path.  Add the repository root for the shared
# canonicalizer, matching the existing route-manifest CLI bootstrap.
_ADAPTER_ROOT = Path(__file__).resolve().parents[1]
if str(_ADAPTER_ROOT) not in sys.path:
    sys.path.insert(0, str(_ADAPTER_ROOT))

from threeway.canon import canonicalize  # noqa: E402

if __package__:
    from scripts import capability_reducer, compact_state_mapping
else:
    import capability_reducer
    import compact_state_mapping


__all__ = ("LegacyAdapterError", "adapt_v1_history", "main")

_LEGACY_SCHEMA = "compact-kernel-legacy-observation/v1"
_FUTURE_LEGACY_SCHEMA = "compact-kernel-legacy-observation/v9"
_CORPUS_SCHEMA = "compact-kernel-v1-shadow-replay/v1"
_REPORT_SCHEMA = "compact-kernel-v1-shadow-parity-report/v1"
_LEGACY_RECORD_FIELDS = (
    "schema",
    "source_id",
    "source_digest",
    "work_id",
    "route_id",
    "work_revision",
    "unit_id",
    "actor_binding_digest",
    "domain",
    "value",
    "context",
    "mutable_scope_ref",
    "mutable_scope_digest",
    "content_digest",
    "dependency_digest",
    "acceptance_digest",
    "evidence_refs",
    "verification_ref",
    "effect_reservation_refs",
)
_LEGACY_ERROR_CODES = frozenset(
    {
        "legacy_invalid",
        "legacy_version",
        "legacy_unmapped",
        "legacy_ambiguous",
        "legacy_nondeterministic",
        "parity_divergence",
    }
)
_PARITY_KINDS = frozenset(
    {
        "match",
        "compact_more_permissive",
        "compact_more_restrictive",
        "authority_semantic_mismatch",
        "non_authority_only",
        "adapter_error",
    }
)
_BLOCKING_PARITY_KINDS = _PARITY_KINDS - {"match", "non_authority_only"}
_EFFECT_ORDER = {
    "never": 0,
    "separate_current_grant": 1,
    "all_other_gates": 2,
}
_CORPUS_FIELDS = frozenset(
    {
        "schema_version",
        "sources",
        "actors",
        "scopes",
        "case_manifest",
        "cases",
        "phase2_misuse_bindings",
        "deferred_phase3_misuse_ids",
        "reducer_replay_ids",
    }
)
_CASE_FIELDS = frozenset(
    {
        "id",
        "case_kind",
        "mapping_row_id",
        "misuse_vector_id",
        "disposition",
        "source_records",
        "record_orders",
        "resolver_mode",
        "expected",
    }
)
_EXPECTED_FIELDS = frozenset(
    {"projections", "envelope_count", "requested_transitions", "error_code"}
)
_PROJECTION_FIELDS = frozenset(
    {
        "disposition",
        "compact",
        "terminal_scope",
        "next_action",
        "effect_eligibility",
        "advisory_only",
    }
)
_SOURCE_PATHS = (
    "tests/fixtures/compact_state_mapping/v1.json",
    "tests/fixtures/compact_kernel/v1_misuse_vectors.json",
    "tests/fixtures/compact_kernel/v2_replay_vectors.json",
)
_MISUSE_SCHEMA = "compact-kernel-misuse-vectors/v1"
_MISUSE_VECTOR_FIELDS = frozenset(
    {
        "id",
        "enforcing_phase",
        "expected_invariant",
        "phase_1_non_enforcement_reason",
        "stimulus",
        "expected_future_outcome",
    }
)
_CASE_BOUND_MISUSE_DELTA_ORACLE = (
    (
        "relevant_dependency_change",
        "misuse:dependency-change",
        "dependency_digest",
    ),
    (
        "relevant_acceptance_change",
        "misuse:acceptance-change",
        "acceptance_digest",
    ),
    (
        "relevant_evidence_change",
        "misuse:evidence-change",
        "evidence_refs",
    ),
)
_EXACT_DUPLICATE_DELIVERY_CASE_ID = "history:exact-duplicate-source"
_MIXED_VERSION_CASE_ID = "history:mixed-v1-v2"


class LegacyAdapterError(ValueError):
    """A stable, sanitized v1 adapter-boundary failure."""

    code: str

    def __init__(self, code: str) -> None:
        safe_code = code if code in _LEGACY_ERROR_CODES else "legacy_invalid"
        self.code = safe_code
        ValueError.__init__(self, safe_code)


@dataclass(frozen=True)
class _LegacyRecord:
    schema: str
    source_id: str
    source_digest: str
    work_id: str
    route_id: str | None
    work_revision: int
    unit_id: str | None
    actor_binding_digest: str
    domain: str
    value: str
    context: tuple[tuple[str, bool | str], ...]
    mutable_scope_ref: str
    mutable_scope_digest: str
    content_digest: str
    dependency_digest: str
    acceptance_digest: str
    evidence_refs: tuple[str, ...]
    verification_ref: str | None
    effect_reservation_refs: tuple[str, ...]


@dataclass(frozen=True)
class _AdapterRule:
    requested_transition: str | None
    compact: str
    terminal_scope: str
    next_action: str
    effect_eligibility: str
    advisory_only: bool


def _chatgpt_failure_rules() -> tuple[
    tuple[
        tuple[str, str, tuple[tuple[str, bool | str], ...]],
        _AdapterRule,
    ],
    ...,
]:
    rules: list[
        tuple[
            tuple[str, str, tuple[tuple[str, bool | str], ...]],
            _AdapterRule,
        ]
    ] = []
    producer = compact_state_mapping.chatgpt_pro_consult
    for failure_class in sorted(producer.FAILURE_CLASSES):
        for transport in sorted(producer.TRANSPORTS):
            for resume_authorized in (False, True):
                if failure_class == "partial_send":
                    if resume_authorized:
                        continue
                    compact = "OUTCOME_UNKNOWN"
                    terminal_scope = "consultation"
                    next_action = "reconcile_only"
                elif resume_authorized:
                    if transport != "manual":
                        continue
                    compact = "FAILED"
                    terminal_scope = "nonterminal"
                    next_action = "resume_manual"
                else:
                    compact = "FAILED"
                    terminal_scope = "consultation"
                    next_action = "no_retry"
                context = {
                    "failure_class": failure_class,
                    "transport": transport,
                    "manual_resume_authorized": resume_authorized,
                }
                rules.append(
                    (
                        ("chatgpt", "failed", tuple(sorted(context.items()))),
                        _AdapterRule(
                            None,
                            compact,
                            terminal_scope,
                            next_action,
                            "never",
                            True,
                        ),
                    )
                )
    return tuple(rules)


@dataclass(frozen=True)
class _Divergence:
    case_id: str
    kind: str


@dataclass(frozen=True)
class _CorpusReport:
    source_digests: tuple[tuple[str, str], ...]
    set_counts: tuple[tuple[str, int], ...]
    corpus_digest: str
    divergences: tuple[_Divergence, ...]
    specialized_event_ids: tuple[str, ...]
    deferred_phase3_misuse_ids: tuple[str, ...]
    executed_case_ids: tuple[str, ...]


@dataclass(frozen=True)
class _HistoryCaseOracle:
    mapping_row_id: str
    record_count: int
    schemas: tuple[str, ...]
    orders: tuple[tuple[int, ...], ...]
    resolver_mode: str
    disposition: str
    expected_error: str | None
    envelope_count: int
    requested_transitions: tuple[str, ...]
    accepted_prefix_transitions: tuple[str, ...] = ()


_HISTORY_CASE_ORACLE: dict[str, _HistoryCaseOracle] = {
    "history:sequential-update": _HistoryCaseOracle(
        "capacity-active", 2, (_LEGACY_SCHEMA, _LEGACY_SCHEMA), ((0, 1),),
        "stable", "route_event", None, 2, ("START", "UPDATE"),
    ),
    "history:exact-duplicate-source": _HistoryCaseOracle(
        "capacity-ready", 1, (_LEGACY_SCHEMA,), ((0, 0),), "stable",
        "route_event", None, 2, ("START", "START"),
    ),
    "history:changed-duplicate-source": _HistoryCaseOracle(
        "capacity-ready", 2, (_LEGACY_SCHEMA, _LEGACY_SCHEMA), ((0, 1),),
        "stable", "legacy_ambiguous", "legacy_ambiguous", 0, (), ("START",),
    ),
    "history:disjoint-order-permutations": _HistoryCaseOracle(
        "capacity-ready", 2, (_LEGACY_SCHEMA, _LEGACY_SCHEMA),
        ((0, 1), (1, 0)), "stable", "route_event", None, 2,
        ("START", "START"),
    ),
    "history:stale-work-revision": _HistoryCaseOracle(
        "capacity-active", 2, (_LEGACY_SCHEMA, _LEGACY_SCHEMA), ((0, 1),),
        "stable", "legacy_ambiguous", "legacy_ambiguous", 0, (), ("START",),
    ),
    "history:gapped-work-revision": _HistoryCaseOracle(
        "capacity-active", 2, (_LEGACY_SCHEMA, _LEGACY_SCHEMA), ((0, 1),),
        "stable", "legacy_ambiguous", "legacy_ambiguous", 0, (), ("START",),
    ),
    "history:actor-resolver-drift": _HistoryCaseOracle(
        "capacity-ready", 1, (_LEGACY_SCHEMA,), ((0,),), "actor_drift",
        "legacy_nondeterministic", "legacy_nondeterministic", 0, (),
    ),
    "history:scope-resolver-drift": _HistoryCaseOracle(
        "capacity-ready", 1, (_LEGACY_SCHEMA,), ((0,),), "scope_drift",
        "legacy_nondeterministic", "legacy_nondeterministic", 0, (),
    ),
    "history:route-ambiguity": _HistoryCaseOracle(
        "capacity-active", 2, (_LEGACY_SCHEMA, _LEGACY_SCHEMA), ((0, 1),),
        "stable", "legacy_ambiguous", "legacy_ambiguous", 0, (), ("START",),
    ),
    "history:scope-ambiguity": _HistoryCaseOracle(
        "capacity-active", 2, (_LEGACY_SCHEMA, _LEGACY_SCHEMA), ((0, 1),),
        "stable", "legacy_ambiguous", "legacy_ambiguous", 0, (), ("START",),
    ),
    "history:overlapping-unit-scopes": _HistoryCaseOracle(
        "capacity-active", 2, (_LEGACY_SCHEMA, _LEGACY_SCHEMA), ((0, 1),),
        "stable", "legacy_ambiguous", "legacy_ambiguous", 0, (), ("START",),
    ),
    "history:content-change": _HistoryCaseOracle(
        "capacity-active", 2, (_LEGACY_SCHEMA, _LEGACY_SCHEMA), ((0, 1),),
        "stable", "route_event", None, 2, ("START", "UPDATE"),
    ),
    "history:absolute-resolved-path": _HistoryCaseOracle(
        "capacity-ready", 1, (_LEGACY_SCHEMA,), ((0,),), "stable",
        "legacy_ambiguous", "legacy_ambiguous", 0, (),
    ),
    "history:redundant-resolved-scope": _HistoryCaseOracle(
        "capacity-ready", 1, (_LEGACY_SCHEMA,), ((0,),), "stable",
        "legacy_ambiguous", "legacy_ambiguous", 0, (),
    ),
    "history:mixed-v1-v2": _HistoryCaseOracle(
        "capacity-active", 2, (_LEGACY_SCHEMA, capability_reducer.SCHEMA_ID),
        ((0, 1),), "stable", "legacy_version", "legacy_version", 0, (),
    ),
    "history:future-v1-schema": _HistoryCaseOracle(
        "capacity-ready", 1, (_FUTURE_LEGACY_SCHEMA,), ((0,),), "stable",
        "legacy_version", "legacy_version", 0, (),
    ),
    "history:nonzero-epoch-material": _HistoryCaseOracle(
        "capacity-ready", 1, (_LEGACY_SCHEMA,), ((0,),), "stable",
        "legacy_invalid", "legacy_invalid", 0, (),
    ),
}


_ADAPTER_RULES: tuple[
    tuple[
        tuple[str, str, tuple[tuple[str, bool | str], ...]],
        _AdapterRule,
    ],
    ...,
] = (
    (
        ("capacity", "ready", ()),
        _AdapterRule(
            "START",
            "RUN",
            "nonterminal",
            "continue",
            "never",
            False,
        ),
    ),
    (
        ("capacity", "active", ()),
        _AdapterRule(
            "START",
            "RUN",
            "nonterminal",
            "continue",
            "never",
            False,
        ),
    ),
    (
        (
            "capacity",
            "blocked",
            (
                ("completion_evidence", False),
                ("verification_required", False),
            ),
        ),
        _AdapterRule(
            "BLOCK",
            "WAIT",
            "nonterminal",
            "wait_for_named_condition",
            "never",
            False,
        ),
    ),
    (
        (
            "capacity",
            "blocked",
            (
                ("completion_evidence", False),
                ("verification_required", True),
            ),
        ),
        _AdapterRule(
            "BLOCK",
            "WAIT",
            "nonterminal",
            "wait_for_named_condition",
            "never",
            False,
        ),
    ),
    (
        ("capacity", "blocked", (("completion_evidence", True), ("verification_required", True))),
        _AdapterRule(
            "REQUEST_REVIEW",
            "REVIEW",
            "nonterminal",
            "obtain_review",
            "never",
            False,
        ),
    ),
    (
        ("capacity", "blocked", (("completion_evidence", True), ("verification_required", False))),
        _AdapterRule(
            "REQUEST_CLOSE",
            "DONE",
            "unit_version",
            "none",
            "separate_current_grant",
            False,
        ),
    ),
    (
        (
            "capacity",
            "done",
            (
                ("all_triggered_gates_met", False),
                ("verification_required", True),
                ("verification_satisfied", False),
            ),
        ),
        _AdapterRule(
            "REQUEST_REVIEW",
            "REVIEW",
            "nonterminal",
            "obtain_review",
            "never",
            False,
        ),
    ),
    (
        (
            "capacity",
            "done",
            (
                ("all_triggered_gates_met", True),
                ("verification_required", True),
                ("verification_satisfied", True),
            ),
        ),
        _AdapterRule(
            "REQUEST_CLOSE",
            "DONE",
            "unit_version",
            "none",
            "separate_current_grant",
            False,
        ),
    ),
    (
        (
            "capacity",
            "done",
            (
                ("all_triggered_gates_met", True),
                ("verification_required", False),
                ("verification_satisfied", False),
            ),
        ),
        _AdapterRule(
            "REQUEST_CLOSE",
            "DONE",
            "unit_version",
            "none",
            "separate_current_grant",
            False,
        ),
    ),
    (
        ("capacity", "excepted", ()),
        _AdapterRule(
            "REQUEST_CLOSE",
            "DONE",
            "unit_version",
            "new_unit_version",
            "separate_current_grant",
            False,
        ),
    ),
    (
        ("capability", "issued", ()),
        _AdapterRule(
            None,
            "GRANT_AVAILABLE",
            "nonterminal",
            "attempt_if_other_gates_pass",
            "all_other_gates",
            False,
        ),
    ),
    (
        ("capability", "activated", ()),
        _AdapterRule(
            None,
            "GRANT_AVAILABLE",
            "nonterminal",
            "attempt_if_other_gates_pass",
            "all_other_gates",
            False,
        ),
    ),
    (
        ("capability", "consumed", (("receipt_outcome", "ok"),)),
        _AdapterRule(
            None,
            "SUCCEEDED",
            "capability",
            "none",
            "never",
            False,
        ),
    ),
    (
        ("capability", "consumed", (("receipt_outcome", "failed"),)),
        _AdapterRule(
            None,
            "FAILED",
            "capability",
            "no_new_attempt",
            "never",
            False,
        ),
    ),
    (
        ("capability", "consumed", (("receipt_outcome", "absent"),)),
        _AdapterRule(
            None,
            "OUTCOME_UNKNOWN",
            "capability",
            "reconcile_only",
            "never",
            False,
        ),
    ),
    (
        ("capability", "revoked", ()),
        _AdapterRule(
            None,
            "REVOKED",
            "capability",
            "no_new_attempt",
            "never",
            False,
        ),
    ),
    (
        ("capability", "expired", ()),
        _AdapterRule(
            None,
            "EXPIRED",
            "capability",
            "no_new_attempt",
            "never",
            False,
        ),
    ),
    (
        ("capability", "failed", ()),
        _AdapterRule(
            None,
            "FAILED",
            "capability",
            "no_new_attempt",
            "never",
            False,
        ),
    ),
    (
        ("chatgpt", "prepared", ()),
        _AdapterRule(
            None,
            "RESERVED",
            "nonterminal",
            "send_once",
            "never",
            True,
        ),
    ),
    (
        ("chatgpt", "sending", ()),
        _AdapterRule(
            None,
            "ATTEMPTING",
            "nonterminal",
            "complete_send_or_reconcile",
            "never",
            True,
        ),
    ),
    (
        ("chatgpt", "sent", ()),
        _AdapterRule(
            None,
            "AWAITING_RESPONSE",
            "nonterminal",
            "accept_response_or_mark_stale",
            "never",
            True,
        ),
    ),
    (
        ("chatgpt", "received", ()),
        _AdapterRule(
            None,
            "RESPONSE_RECEIVED",
            "nonterminal",
            "reconcile_locally",
            "never",
            True,
        ),
    ),
    (
        ("chatgpt", "reconciled", ()),
        _AdapterRule(
            None,
            "RECONCILED",
            "consultation",
            "none",
            "never",
            True,
        ),
    ),
    *_chatgpt_failure_rules(),
    (
        ("chatgpt", "stale", ()),
        _AdapterRule(
            None,
            "STALE",
            "consultation",
            "no_retry",
            "never",
            True,
        ),
    ),
    (
        ("opus_receipt", "reserved", (("reservation_action", "launch"),)),
        _AdapterRule(
            None,
            "RESERVED",
            "nonterminal",
            "launch_once",
            "never",
            True,
        ),
    ),
    (
        ("opus_receipt", "reserved", (("reservation_action", "return"),)),
        _AdapterRule(
            None,
            "RESERVED",
            "nonterminal",
            "return_without_launch",
            "never",
            True,
        ),
    ),
    (
        ("opus_receipt", "reserved", (("reservation_action", "degrade_uncertain"),)),
        _AdapterRule(
            None,
            "OUTCOME_UNKNOWN",
            "attempt",
            "reconcile_only",
            "never",
            True,
        ),
    ),
    (
        ("opus_receipt", "reviewed", (("provider_status", "pass"),)),
        _AdapterRule(
            None,
            "REVIEWED_PASS",
            "nonterminal",
            "local_reconcile",
            "never",
            True,
        ),
    ),
    (
        ("opus_receipt", "reviewed", (("provider_status", "issues"),)),
        _AdapterRule(
            None,
            "REVIEWED_ISSUES",
            "nonterminal",
            "local_reconcile",
            "never",
            True,
        ),
    ),
    (
        ("opus_receipt", "reviewed", (("provider_status", "unavailable"),)),
        _AdapterRule(
            None,
            "REVIEWED_UNAVAILABLE",
            "nonterminal",
            "local_reconcile",
            "never",
            True,
        ),
    ),
    (
        ("opus_receipt", "reconciled", (("disposition", "GO"),)),
        _AdapterRule(
            None,
            "RECONCILED_GO",
            "provider_review",
            "consult_local_verdict",
            "never",
            True,
        ),
    ),
    (
        ("opus_receipt", "reconciled", (("disposition", "NITS"),)),
        _AdapterRule(
            None,
            "RECONCILED_NITS",
            "provider_review",
            "consult_local_verdict",
            "never",
            True,
        ),
    ),
    (
        ("opus_receipt", "reconciled", (("disposition", "FAIL"),)),
        _AdapterRule(
            None,
            "RECONCILED_FAIL",
            "provider_review",
            "consult_local_verdict",
            "never",
            True,
        ),
    ),
    (
        ("opus_receipt", "publishing", ()),
        _AdapterRule(
            None,
            "PUBLISHING",
            "nonterminal",
            "recover_publication",
            "never",
            True,
        ),
    ),
    (
        ("opus_receipt", "published", ()),
        _AdapterRule(
            None,
            "PUBLISHED",
            "publication_phase",
            "none",
            "never",
            True,
        ),
    ),
    (
        ("provider_result", "pass", ()),
        _AdapterRule(
            None,
            "PROVIDER_PASS",
            "none",
            "local_reconcile",
            "never",
            True,
        ),
    ),
    (
        ("provider_result", "issues", ()),
        _AdapterRule(
            None,
            "PROVIDER_ISSUES",
            "none",
            "local_reconcile",
            "never",
            True,
        ),
    ),
    (
        ("provider_result", "unavailable", ()),
        _AdapterRule(
            None,
            "PROVIDER_UNAVAILABLE",
            "none",
            "continue_without_provider",
            "never",
            True,
        ),
    ),
    (
        ("local_verdict", "GO", (("verification_key_matches", True),)),
        _AdapterRule(
            None,
            "GO",
            "review",
            "continue_effect_gates",
            "all_other_gates",
            False,
        ),
    ),
    (
        ("local_verdict", "NITS", ()),
        _AdapterRule(
            None,
            "NITS",
            "review",
            "new_scoped_version",
            "never",
            False,
        ),
    ),
    (
        ("local_verdict", "FAIL", ()),
        _AdapterRule(
            None,
            "FAIL",
            "review",
            "new_scoped_version",
            "never",
            False,
        ),
    ),
    (
        ("local_verdict", "unable_to_verify", ()),
        _AdapterRule(
            None,
            "UNABLE_TO_VERIFY",
            "nonterminal",
            "redispatch_or_escalate",
            "never",
            False,
        ),
    ),
    (
        ("work_result", "cancelled", ()),
        _AdapterRule(
            "CANCEL",
            "CANCELLED",
            "work",
            "new_work_id",
            "never",
            False,
        ),
    ),
    (
        ("work_result", "failed", ()),
        _AdapterRule(
            None,
            "FAILED",
            "attempt",
            "new_transition_if_policy_allows",
            "never",
            False,
        ),
    ),
    (
        ("work_result", "superseded", ()),
        _AdapterRule(
            "SUPERSEDE",
            "SUPERSEDED",
            "version",
            "follow_successor",
            "never",
            False,
        ),
    ),
    (
        ("work_result", "outcome_unknown", ()),
        _AdapterRule(
            None,
            "OUTCOME_UNKNOWN",
            "nonterminal",
            "reconcile_only",
            "never",
            False,
        ),
    ),
)
def _legacy_invalid() -> LegacyAdapterError:
    return LegacyAdapterError("legacy_invalid")


def _require_string(value: object, pattern: str) -> str:
    if type(value) is not str or fullmatch(pattern, value) is None:
        raise _legacy_invalid()
    return value


def _require_nullable_string(value: object, pattern: str) -> str | None:
    if value is None:
        return None
    return _require_string(value, pattern)


def _require_integer(value: object, minimum: int) -> int:
    if (
        type(value) is not int
        or not minimum <= value <= capability_reducer.MAX_INT
    ):
        raise _legacy_invalid()
    return value


def _require_refs(value: object) -> tuple[str, ...]:
    if (
        type(value) is not list
        or len(value) > capability_reducer.MAX_COLLECTION_ITEMS
    ):
        raise _legacy_invalid()
    refs = tuple(
        _require_string(item, capability_reducer.REF_PATTERN) for item in value
    )
    if len(set(refs)) != len(refs):
        raise _legacy_invalid()
    return tuple(sorted(refs))


def _strict_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    value: dict[str, object] = {}
    for key, item in pairs:
        if key in value:
            raise _legacy_invalid()
        value[key] = item
    return value


def _reject_json_constant(_value: str) -> object:
    raise _legacy_invalid()


def _strict_json_loads(value: object) -> object:
    """Parse JSON while rejecting duplicate keys and non-standard constants."""

    if type(value) is not str:
        raise _legacy_invalid()
    try:
        return json.loads(
            value,
            object_pairs_hook=_strict_object,
            parse_constant=_reject_json_constant,
        )
    except LegacyAdapterError:
        raise
    except Exception:
        raise _legacy_invalid() from None


def _source_digest(value: dict[str, object]) -> str:
    expected_fields = set(_LEGACY_RECORD_FIELDS) - {"source_digest"}
    if set(value) != expected_fields:
        raise _legacy_invalid()
    try:
        return "sha256:" + sha256(canonicalize(value)).hexdigest()
    except Exception:
        raise _legacy_invalid() from None


def _parse_legacy_record(value: object) -> _LegacyRecord:
    if type(value) is not dict or any(type(key) is not str for key in value):
        raise _legacy_invalid()

    schema = value.get("schema")
    if type(schema) is not str:
        raise _legacy_invalid()
    if schema != _LEGACY_SCHEMA:
        raise LegacyAdapterError("legacy_version")
    if set(value) != set(_LEGACY_RECORD_FIELDS):
        raise _legacy_invalid()

    source_id = _require_string(value["source_id"], capability_reducer.ID_PATTERN)
    source_digest = _require_string(
        value["source_digest"], capability_reducer.DIGEST_PATTERN
    )
    work_id = _require_string(value["work_id"], capability_reducer.ID_PATTERN)
    route_id = _require_nullable_string(
        value["route_id"], capability_reducer.ID_PATTERN
    )
    work_revision = _require_integer(value["work_revision"], 1)
    unit_id = _require_nullable_string(
        value["unit_id"], capability_reducer.ID_PATTERN
    )
    actor_binding_digest = _require_string(
        value["actor_binding_digest"], capability_reducer.DIGEST_PATTERN
    )
    domain = _require_string(value["domain"], capability_reducer.ID_PATTERN)
    state_value = _require_string(value["value"], capability_reducer.ID_PATTERN)

    context = value["context"]
    if type(context) is not dict or any(type(key) is not str for key in context):
        raise _legacy_invalid()
    if any(type(item) not in (bool, str) for item in context.values()):
        raise _legacy_invalid()

    mutable_scope_ref = _require_string(
        value["mutable_scope_ref"], capability_reducer.REF_PATTERN
    )
    mutable_scope_digest = _require_string(
        value["mutable_scope_digest"], capability_reducer.DIGEST_PATTERN
    )
    content_digest = _require_string(
        value["content_digest"], capability_reducer.DIGEST_PATTERN
    )
    dependency_digest = _require_string(
        value["dependency_digest"], capability_reducer.DIGEST_PATTERN
    )
    acceptance_digest = _require_string(
        value["acceptance_digest"], capability_reducer.DIGEST_PATTERN
    )
    evidence_refs = _require_refs(value["evidence_refs"])
    verification_ref = _require_nullable_string(
        value["verification_ref"], capability_reducer.REF_PATTERN
    )
    effect_reservation_refs = _require_refs(value["effect_reservation_refs"])

    normalized_without_digest: dict[str, object] = {
        "schema": schema,
        "source_id": source_id,
        "work_id": work_id,
        "route_id": route_id,
        "work_revision": work_revision,
        "unit_id": unit_id,
        "actor_binding_digest": actor_binding_digest,
        "domain": domain,
        "value": state_value,
        "context": {key: item for key, item in sorted(context.items())},
        "mutable_scope_ref": mutable_scope_ref,
        "mutable_scope_digest": mutable_scope_digest,
        "content_digest": content_digest,
        "dependency_digest": dependency_digest,
        "acceptance_digest": acceptance_digest,
        "evidence_refs": list(evidence_refs),
        "verification_ref": verification_ref,
        "effect_reservation_refs": list(effect_reservation_refs),
    }
    if source_digest != _source_digest(normalized_without_digest):
        raise _legacy_invalid()

    try:
        compact_state_mapping.meaning_for(domain, state_value, context=context)
    except compact_state_mapping.StateMappingError:
        raise LegacyAdapterError("legacy_unmapped") from None
    except Exception:
        raise _legacy_invalid() from None

    return _LegacyRecord(
        schema=schema,
        source_id=source_id,
        source_digest=source_digest,
        work_id=work_id,
        route_id=route_id,
        work_revision=work_revision,
        unit_id=unit_id,
        actor_binding_digest=actor_binding_digest,
        domain=domain,
        value=state_value,
        context=tuple(sorted(context.items())),
        mutable_scope_ref=mutable_scope_ref,
        mutable_scope_digest=mutable_scope_digest,
        content_digest=content_digest,
        dependency_digest=dependency_digest,
        acceptance_digest=acceptance_digest,
        evidence_refs=evidence_refs,
        verification_ref=verification_ref,
        effect_reservation_refs=effect_reservation_refs,
    )


def _canonical_digest(value: object) -> str:
    try:
        return "sha256:" + sha256(canonicalize(value)).hexdigest()
    except Exception:
        raise _legacy_invalid() from None


def _rule_key(
    domain: str,
    value: str,
    context: tuple[tuple[str, bool | str], ...],
) -> tuple[str, str, tuple[tuple[str, bool | str], ...]]:
    return (domain, value, context)


def _rule_for_key(
    key: tuple[str, str, tuple[tuple[str, bool | str], ...]],
) -> _AdapterRule:
    matches = tuple(rule for candidate, rule in _ADAPTER_RULES if candidate == key)
    if len(matches) != 1:
        raise LegacyAdapterError("legacy_unmapped")
    return matches[0]


def _record_rule(record: _LegacyRecord) -> _AdapterRule:
    return _rule_for_key(_rule_key(record.domain, record.value, record.context))


def _selected_rule(
    record: _LegacyRecord,
    rule: _AdapterRule,
    *,
    expected_unit_version: int,
) -> _AdapterRule:
    if (
        record.domain == "capacity"
        and record.value in {"ready", "active"}
        and rule.requested_transition == "START"
        and expected_unit_version > 0
    ):
        return replace(rule, requested_transition="UPDATE")
    return rule


def _compact_projection(
    rule: _AdapterRule,
    emitted: object | None,
) -> dict[str, object]:
    """Project gate-only meaning from the selected rule and event disposition."""

    return {
        "disposition": (
            "route_event" if emitted is not None else "no_route_event"
        ),
        "compact": rule.compact,
        "terminal_scope": rule.terminal_scope,
        "next_action": rule.next_action,
        "effect_eligibility": rule.effect_eligibility,
        "advisory_only": rule.advisory_only,
    }


def _transition_id(source_id: str) -> str:
    return "legacy-" + sha256(source_id.encode("utf-8")).hexdigest()


def _envelope_key(
    event: capability_reducer.TransitionEnvelope,
) -> tuple[str, int, str, int, str]:
    work_id, unit_tag, unit_id = capability_reducer.unit_key(
        event.work_id, event.unit_id
    )
    return (
        work_id,
        unit_tag,
        unit_id,
        event.work_revision,
        event.transition_id,
    )


def _mapped_reducer_error(error: capability_reducer.ReducerError) -> LegacyAdapterError:
    if error.code in {"actor_nondeterministic", "scope_nondeterministic"}:
        return LegacyAdapterError("legacy_nondeterministic")
    if error.code in {
        "actor_binding",
        "actor_ineligible",
        "activation_epoch",
        "expected_version",
        "precondition",
        "work_revision",
        "route_ambiguity",
        "scope_invalid",
        "scope_digest",
        "scope_overlap",
        "transition_id_reuse",
        "state_invalid",
    }:
        return LegacyAdapterError("legacy_ambiguous")
    return _legacy_invalid()


def _adapt_parsed_history(
    records: tuple[_LegacyRecord, ...],
    *,
    resolve_actor: capability_reducer.ActorBindingResolver,
    resolve_scope: capability_reducer.ScopeResolver,
) -> tuple[capability_reducer.TransitionEnvelope, ...]:
    state = capability_reducer.KernelState()
    source_events: dict[
        str, tuple[str, capability_reducer.TransitionEnvelope]
    ] = {}
    accepted: list[capability_reducer.TransitionEnvelope] = []

    for record in records:
        prior = source_events.get(record.source_id)
        if prior is not None:
            prior_digest, prior_event = prior
            if prior_digest != record.source_digest:
                raise LegacyAdapterError("legacy_ambiguous")
            accepted.append(prior_event)
            continue

        rule = _record_rule(record)
        if rule.requested_transition is None:
            raise LegacyAdapterError("legacy_unmapped")
        try:
            next_revision, expected_version, precondition = (
                capability_reducer.transition_cursor(
                    state,
                    work_id=record.work_id,
                    unit_id=record.unit_id,
                )
            )
        except capability_reducer.ReducerError as error:
            raise _mapped_reducer_error(error) from None
        except Exception:
            raise _legacy_invalid() from None
        if record.work_revision != next_revision:
            raise LegacyAdapterError("legacy_ambiguous")

        selected = _selected_rule(
            record,
            rule,
            expected_unit_version=expected_version,
        )
        requested_transition = selected.requested_transition
        if requested_transition is None:
            raise LegacyAdapterError("legacy_unmapped")
        event = capability_reducer.TransitionEnvelope(
            schema=capability_reducer.SCHEMA_ID,
            work_id=record.work_id,
            transition_id=_transition_id(record.source_id),
            route_id=record.route_id,
            work_revision=record.work_revision,
            unit_id=record.unit_id,
            actor_binding_digest=record.actor_binding_digest,
            requested_transition=requested_transition,
            expected_unit_version=expected_version,
            precondition_digest=precondition,
            mutable_scope_ref=record.mutable_scope_ref,
            mutable_scope_digest=record.mutable_scope_digest,
            content_digest=record.content_digest,
            dependency_digest=record.dependency_digest,
            acceptance_digest=record.acceptance_digest,
            evidence_refs=record.evidence_refs,
            verification_ref=record.verification_ref,
            effect_reservation_refs=record.effect_reservation_refs,
            activation_epoch=0,
        )

        try:
            first_actor_value = resolve_actor(record.actor_binding_digest)
            first_actor, first_actor_bytes = capability_reducer._validate_actor(
                first_actor_value
            )
            second_actor_value = resolve_actor(record.actor_binding_digest)
            _second_actor, second_actor_bytes = capability_reducer._validate_actor(
                second_actor_value
            )
        except Exception:
            raise _legacy_invalid() from None
        if first_actor_bytes != second_actor_bytes:
            raise LegacyAdapterError("legacy_nondeterministic")
        try:
            state = capability_reducer.apply_transition(
                state,
                event,
                actor=first_actor,
                activation=capability_reducer.ActivationState(epoch=0),
                resolve_scope=resolve_scope,
            )
        except capability_reducer.ReducerError as error:
            raise _mapped_reducer_error(error) from None
        except Exception:
            raise _legacy_invalid() from None

        source_events[record.source_id] = (record.source_digest, event)
        accepted.append(event)

    return tuple(sorted(accepted, key=_envelope_key))


def _require_exact_object(
    value: object,
    fields: frozenset[str],
) -> dict[str, object]:
    if (
        type(value) is not dict
        or any(type(key) is not str for key in value)
        or set(value) != fields
    ):
        raise _legacy_invalid()
    return value


def _require_string_list(value: object) -> list[str]:
    if (
        type(value) is not list
        or any(type(item) is not str or not item for item in value)
        or len(value) != len(set(value))
    ):
        raise _legacy_invalid()
    return value


def _load_json_path(path: Path) -> dict[str, object]:
    try:
        parsed = _strict_json_loads(path.read_text(encoding="utf-8"))
    except LegacyAdapterError:
        raise
    except Exception:
        raise _legacy_invalid() from None
    if type(parsed) is not dict:
        raise _legacy_invalid()
    return parsed


def _bound_sources(
    corpus: dict[str, object],
) -> tuple[
    tuple[tuple[str, str], ...],
    dict[str, dict[str, object]],
]:
    sources = corpus["sources"]
    if (
        type(sources) is not dict
        or any(type(key) is not str for key in sources)
        or set(sources) != set(_SOURCE_PATHS)
    ):
        raise _legacy_invalid()

    bound: dict[str, dict[str, object]] = {}
    digests: list[tuple[str, str]] = []
    for relative_path in _SOURCE_PATHS:
        expected = sources[relative_path]
        if type(expected) is not str or fullmatch(
            capability_reducer.DIGEST_PATTERN, expected
        ) is None:
            raise _legacy_invalid()
        path = _ADAPTER_ROOT / relative_path
        try:
            raw = path.read_bytes()
        except Exception:
            raise _legacy_invalid() from None
        actual = "sha256:" + sha256(raw).hexdigest()
        if actual != expected:
            raise _legacy_invalid()
        bound[relative_path] = _load_json_path(path)
        digests.append((relative_path, actual))
    return tuple(digests), bound


def _actor_from_fixture(value: object) -> capability_reducer.ActorContext:
    fields = frozenset(
        {
            "binding_id",
            "binding_digest",
            "repository",
            "principal",
            "allowed_actions",
            "user_authorized_actions",
            "parent_binding_id",
            "parent_allowed_actions",
            "attested",
            "expired",
            "revoked",
        }
    )
    raw = _require_exact_object(value, fields)
    allowed = _require_string_list(raw["allowed_actions"])
    authorized = _require_string_list(raw["user_authorized_actions"])
    parent_raw = raw["parent_allowed_actions"]
    parent = None if parent_raw is None else _require_string_list(parent_raw)
    actor = capability_reducer.ActorContext(
        binding_id=raw["binding_id"],
        binding_digest=raw["binding_digest"],
        repository=raw["repository"],
        principal=raw["principal"],
        allowed_actions=frozenset(allowed),
        user_authorized_actions=frozenset(authorized),
        parent_binding_id=raw["parent_binding_id"],
        parent_allowed_actions=None if parent is None else frozenset(parent),
        attested=raw["attested"],
        expired=raw["expired"],
        revoked=raw["revoked"],
    )
    actor_without_digest = {
        "binding_id": actor.binding_id,
        "repository": actor.repository,
        "principal": actor.principal,
        "allowed_actions": sorted(actor.allowed_actions),
        "user_authorized_actions": sorted(actor.user_authorized_actions),
        "parent_binding_id": actor.parent_binding_id,
        "parent_allowed_actions": (
            None
            if actor.parent_allowed_actions is None
            else sorted(actor.parent_allowed_actions)
        ),
        "attested": actor.attested,
        "expired": actor.expired,
        "revoked": actor.revoked,
    }
    if actor.binding_digest != _canonical_digest(actor_without_digest):
        raise _legacy_invalid()
    return actor


def _scope_from_fixture(value: object) -> capability_reducer.ResolvedScope:
    raw = _require_exact_object(
        value, frozenset({"repository", "paths", "lock_domains"})
    )
    paths = _require_string_list(raw["paths"])
    locks = _require_string_list(raw["lock_domains"])
    if type(raw["repository"]) is not str:
        raise _legacy_invalid()
    return capability_reducer.ResolvedScope(
        repository=raw["repository"],
        paths=tuple(paths),
        lock_domains=tuple(locks),
    )


def _fixture_runtime(
    corpus: dict[str, object],
) -> tuple[
    dict[str, capability_reducer.ActorContext],
    dict[str, capability_reducer.ResolvedScope],
]:
    actor_values = corpus["actors"]
    scope_values = corpus["scopes"]
    if (
        type(actor_values) is not dict
        or not actor_values
        or type(scope_values) is not dict
        or not scope_values
    ):
        raise _legacy_invalid()
    actors: dict[str, capability_reducer.ActorContext] = {}
    for lookup, value in actor_values.items():
        if type(lookup) is not str:
            raise _legacy_invalid()
        actor = _actor_from_fixture(value)
        if lookup != actor.binding_digest:
            raise _legacy_invalid()
        actors[lookup] = actor
    scopes: dict[str, capability_reducer.ResolvedScope] = {}
    for ref, value in scope_values.items():
        if type(ref) is not str:
            raise _legacy_invalid()
        scopes[ref] = _scope_from_fixture(value)
    return actors, scopes


def _v1_disposition(row: dict[str, object]) -> str:
    domain = row["domain"]
    value = row["value"]
    expected = row["expected"]
    if type(expected) is not dict:
        raise _legacy_invalid()
    compact = expected["compact"]
    if domain == "capacity":
        if value in {"ready", "active"}:
            return "route_event"
        if value == "blocked" and compact in {"WAIT", "REVIEW", "DONE"}:
            return "route_event"
        if value == "done" and compact in {"REVIEW", "DONE"}:
            return "route_event"
        if value == "excepted" and compact == "DONE":
            return "route_event"
    if domain == "work_result" and value in {"cancelled", "superseded"}:
        return "route_event"
    return "no_route_event"


def _projection_from_meaning(
    disposition: str,
    meaning: compact_state_mapping.StateMeaning,
) -> dict[str, object]:
    return {"disposition": disposition, **asdict(meaning)}


def _golden_projection(row: dict[str, object]) -> dict[str, object]:
    expected = row["expected"]
    if type(expected) is not dict or set(expected) != (
        _PROJECTION_FIELDS - {"disposition"}
    ):
        raise _legacy_invalid()
    return {"disposition": _v1_disposition(row), **expected}


def _projection_is_valid(value: object) -> bool:
    if type(value) is not dict or set(value) != _PROJECTION_FIELDS:
        return False
    string_fields = (
        "disposition",
        "compact",
        "terminal_scope",
        "next_action",
        "effect_eligibility",
    )
    return (
        all(type(value[field]) is str for field in string_fields)
        and value["disposition"] in {"route_event", "no_route_event"}
        and value["effect_eligibility"] in _EFFECT_ORDER
        and type(value["advisory_only"]) is bool
    )


def _projection_kind(
    candidate: dict[str, object],
    golden: dict[str, object],
) -> str:
    if not _projection_is_valid(candidate) or not _projection_is_valid(golden):
        return "adapter_error"
    if candidate == golden:
        return "match"
    if candidate["disposition"] != golden["disposition"]:
        return (
            "compact_more_permissive"
            if candidate["disposition"] == "route_event"
            else "compact_more_restrictive"
        )
    candidate_effect = candidate["effect_eligibility"]
    golden_effect = golden["effect_eligibility"]
    if (
        candidate_effect not in _EFFECT_ORDER
        or golden_effect not in _EFFECT_ORDER
    ):
        return "adapter_error"
    if _EFFECT_ORDER[candidate_effect] != _EFFECT_ORDER[golden_effect]:
        return (
            "compact_more_permissive"
            if _EFFECT_ORDER[candidate_effect] > _EFFECT_ORDER[golden_effect]
            else "compact_more_restrictive"
        )
    if any(
        candidate[field] != golden[field]
        for field in ("terminal_scope", "next_action", "advisory_only")
    ):
        return "authority_semantic_mismatch"
    if candidate["compact"] != golden["compact"]:
        return "non_authority_only"
    return "authority_semantic_mismatch"


def _case_resolvers(
    mode: str,
    actors: dict[str, capability_reducer.ActorContext],
    scopes: dict[str, capability_reducer.ResolvedScope],
) -> tuple[
    capability_reducer.ActorBindingResolver,
    capability_reducer.ScopeResolver,
]:
    actor_calls = 0
    scope_calls = 0

    def resolve_actor(digest: str) -> capability_reducer.ActorContext:
        nonlocal actor_calls
        actor_calls += 1
        actor = actors[digest]
        if mode == "actor_drift" and actor_calls % 2 == 0:
            drifted = replace(actor, principal="user:drift")
            return replace(
                drifted,
                binding_digest=_canonical_digest(
                    capability_reducer._actor_mapping(drifted)
                ),
            )
        return actor

    def resolve_scope(ref: str) -> capability_reducer.ResolvedScope:
        nonlocal scope_calls
        scope_calls += 1
        if mode == "scope_drift" and scope_calls % 2 == 0:
            alternatives = tuple(
                value for key, value in scopes.items() if key != ref
            )
            if not alternatives:
                raise KeyError(ref)
            return alternatives[0]
        return scopes[ref]

    return resolve_actor, resolve_scope


def _specialized_probe_record(
    template: dict[str, object],
    row: dict[str, object],
    *,
    route_id: str | None,
    unit_id: str | None,
) -> dict[str, object]:
    axis_id = (
        f"route-{'null' if route_id is None else 'named'}-"
        f"unit-{'null' if unit_id is None else 'named'}"
    )
    probe = dict(template)
    probe.update(
        {
            "source_id": f"specialized-probe:{row['id']}:{axis_id}",
            "work_id": f"work-specialized-probe-{row['id']}-{axis_id}",
            "route_id": route_id,
            "unit_id": unit_id,
            "domain": row["domain"],
            "value": row["value"],
            "context": {
                key: item for key, item in sorted(row["context"].items())
            },
        }
    )
    probe["source_digest"] = _source_digest(
        {key: value for key, value in probe.items() if key != "source_digest"}
    )
    return probe


def _append_kind(
    findings: set[tuple[str, str]],
    case_id: str,
    kind: str,
) -> None:
    if kind not in _PARITY_KINDS:
        kind = "adapter_error"
    if kind != "match":
        findings.add((case_id, kind))


def _validate_case_bound_misuse_deltas(
    case_by_id: dict[str, dict[str, object]],
    bindings: dict[str, object],
) -> None:
    stable_fields = (
        "schema",
        "work_id",
        "route_id",
        "unit_id",
        "actor_binding_digest",
        "domain",
        "context",
        "mutable_scope_ref",
        "mutable_scope_digest",
        "content_digest",
        "verification_ref",
        "effect_reservation_refs",
    )
    delta_fields = (
        "dependency_digest",
        "acceptance_digest",
        "evidence_refs",
    )
    for misuse_id, case_id, required_delta in _CASE_BOUND_MISUSE_DELTA_ORACLE:
        if bindings.get(misuse_id) != {
            "target_kind": "case",
            "target_id": case_id,
        }:
            raise _legacy_invalid()
        case = case_by_id.get(case_id)
        if type(case) is not dict:
            raise _legacy_invalid()
        records = case.get("source_records")
        expected = case.get("expected")
        if (
            case.get("case_kind") != "misuse"
            or case.get("disposition") != "route_event"
            or case.get("resolver_mode") != "stable"
            or case.get("record_orders") != [[0, 1]]
            or type(expected) is not dict
            or expected.get("error_code") is not None
            or expected.get("envelope_count") != 2
            or expected.get("requested_transitions") != ["START", "UPDATE"]
            or type(records) is not list
            or len(records) != 2
        ):
            raise _legacy_invalid()
        try:
            first, second = tuple(_parse_legacy_record(item) for item in records)
        except Exception:
            raise _legacy_invalid() from None
        if (
            first.source_id == second.source_id
            or (first.work_revision, second.work_revision) != (1, 2)
        ):
            raise _legacy_invalid()
        if any(
            getattr(first, field) != getattr(second, field)
            for field in stable_fields
        ):
            raise _legacy_invalid()
        changed_fields = {
            field
            for field in delta_fields
            if getattr(first, field) != getattr(second, field)
        }
        if changed_fields != {required_delta}:
            raise _legacy_invalid()


_HISTORY_CAUSAL_IDENTITY_FIELDS = (
    "work_id",
    "route_id",
    "unit_id",
    "mutable_scope_ref",
    "mutable_scope_digest",
)
_HISTORY_VERIFICATION_KEY_FIELDS = (
    "content_digest",
    "dependency_digest",
    "acceptance_digest",
    "evidence_refs",
)


def _oracle_rebased_record(raw: dict[str, object]) -> _LegacyRecord:
    candidate = dict(raw)
    candidate["schema"] = _LEGACY_SCHEMA
    candidate["source_digest"] = _source_digest(
        {
            key: value
            for key, value in candidate.items()
            if key != "source_digest"
        }
    )
    return _parse_legacy_record(candidate)


def _oracle_parsed_history(
    case_id: str,
    records: list[dict[str, object]],
) -> tuple[_LegacyRecord, ...]:
    record_fields = set(_LEGACY_RECORD_FIELDS)
    try:
        if case_id == "history:future-v1-schema":
            raw = records[0]
            if set(raw) != record_fields or raw["schema"] != _FUTURE_LEGACY_SCHEMA:
                raise _legacy_invalid()
            return (_oracle_rebased_record(raw),)
        if case_id == "history:nonzero-epoch-material":
            raw = records[0]
            if (
                set(raw) != record_fields | {"activation_epoch"}
                or type(raw["activation_epoch"]) is not int
                or raw["activation_epoch"] != 1
            ):
                raise _legacy_invalid()
            without_epoch = dict(raw)
            del without_epoch["activation_epoch"]
            return (_oracle_rebased_record(without_epoch),)
        if case_id == _MIXED_VERSION_CASE_ID:
            first, second = records
            if set(first) != record_fields or set(second) != record_fields:
                raise _legacy_invalid()
            return (_parse_legacy_record(first), _oracle_rebased_record(second))
        return tuple(_parse_legacy_record(record) for record in records)
    except Exception:
        raise _legacy_invalid() from None


def _oracle_fields_are_equal(
    records: tuple[_LegacyRecord, ...],
    fields: tuple[str, ...],
) -> bool:
    return all(
        all(getattr(record, field) == getattr(records[0], field) for field in fields)
        for record in records[1:]
    )


def _oracle_scopes_overlap(
    left: capability_reducer.ResolvedScope,
    right: capability_reducer.ResolvedScope,
) -> bool:
    if left.repository != right.repository:
        return False
    if set(left.lock_domains) & set(right.lock_domains):
        return True
    return any(
        capability_reducer._path_overlap(left_path, right_path)
        for left_path in left.paths
        for right_path in right.paths
    )


def _oracle_record_scope_is_exact(
    record: _LegacyRecord,
    actors: dict[str, capability_reducer.ActorContext],
    scopes: dict[str, capability_reducer.ResolvedScope],
) -> bool:
    actor = actors.get(record.actor_binding_digest)
    scope = scopes.get(record.mutable_scope_ref)
    if actor is None or scope is None:
        return False
    try:
        normalized = capability_reducer._normalize_scope(scope)
        digest = capability_reducer._scope_digest(normalized)
    except capability_reducer.ReducerError:
        return False
    return (
        record.mutable_scope_digest == digest
        and normalized.repository == actor.repository
    )


def _validate_history_relationship(
    case_id: str,
    records: tuple[_LegacyRecord, ...],
    actors: dict[str, capability_reducer.ActorContext],
    scopes: dict[str, capability_reducer.ResolvedScope],
) -> None:
    revisions = tuple(record.work_revision for record in records)
    values = tuple(record.value for record in records)
    source_ids = tuple(record.source_id for record in records)
    first = records[0]

    if case_id == "history:sequential-update":
        valid = (
            len(set(source_ids)) == 2
            and _oracle_fields_are_equal(records, _HISTORY_CAUSAL_IDENTITY_FIELDS)
            and revisions == (1, 2)
            and values == ("ready", "active")
        )
    elif case_id == "history:exact-duplicate-source":
        valid = True
    elif case_id == "history:changed-duplicate-source":
        second = records[1]
        changed_fields = {
            field
            for field in _LegacyRecord.__dataclass_fields__
            if getattr(first, field) != getattr(second, field)
        }
        valid = (
            source_ids[0] == source_ids[1]
            and revisions == (1, 1)
            and changed_fields == {"source_digest", "content_digest"}
        )
    elif case_id == "history:disjoint-order-permutations":
        distinct_fields = (
            "source_id",
            "work_id",
            "route_id",
            "unit_id",
            "mutable_scope_ref",
            "mutable_scope_digest",
        )
        valid = revisions == (1, 1) and all(
            getattr(records[0], field) != getattr(records[1], field)
            for field in distinct_fields
        )
    elif case_id in {
        "history:stale-work-revision",
        "history:gapped-work-revision",
    }:
        expected_revisions = (
            (1, 1)
            if case_id == "history:stale-work-revision"
            else (1, 3)
        )
        valid = (
            len(set(source_ids)) == 2
            and _oracle_fields_are_equal(records, _HISTORY_CAUSAL_IDENTITY_FIELDS)
            and revisions == expected_revisions
            and values == ("ready", "active")
        )
    elif case_id in {
        "history:actor-resolver-drift",
        "history:scope-resolver-drift",
    }:
        valid = True
    elif case_id == "history:route-ambiguity":
        second = records[1]
        valid = (
            len(set(source_ids)) == 2
            and revisions == (1, 2)
            and first.work_id == second.work_id
            and first.unit_id == second.unit_id
            and first.actor_binding_digest == second.actor_binding_digest
            and first.mutable_scope_ref == second.mutable_scope_ref
            and first.mutable_scope_digest == second.mutable_scope_digest
            and all(
                _oracle_record_scope_is_exact(record, actors, scopes)
                for record in records
            )
            and first.route_id is None
            and second.route_id is not None
        )
    elif case_id == "history:scope-ambiguity":
        second = records[1]
        valid = (
            len(set(source_ids)) == 2
            and revisions == (1, 2)
            and first.work_id == second.work_id
            and first.route_id == second.route_id
            and first.unit_id == second.unit_id
            and first.actor_binding_digest == second.actor_binding_digest
            and first.mutable_scope_ref != second.mutable_scope_ref
            and first.mutable_scope_digest != second.mutable_scope_digest
            and all(
                _oracle_record_scope_is_exact(record, actors, scopes)
                for record in records
            )
        )
    elif case_id == "history:overlapping-unit-scopes":
        second = records[1]
        left_scope = scopes.get(first.mutable_scope_ref)
        right_scope = scopes.get(second.mutable_scope_ref)
        valid = (
            len(set(source_ids)) == 2
            and revisions == (1, 2)
            and first.work_id == second.work_id
            and first.route_id == second.route_id
            and first.unit_id != second.unit_id
            and first.actor_binding_digest == second.actor_binding_digest
            and left_scope is not None
            and right_scope is not None
            and all(
                _oracle_record_scope_is_exact(record, actors, scopes)
                for record in records
            )
            and _oracle_scopes_overlap(left_scope, right_scope)
        )
    elif case_id == "history:content-change":
        second = records[1]
        changed_verification_fields = {
            field
            for field in _HISTORY_VERIFICATION_KEY_FIELDS
            if getattr(first, field) != getattr(second, field)
        }
        valid = (
            len(set(source_ids)) == 2
            and _oracle_fields_are_equal(records, _HISTORY_CAUSAL_IDENTITY_FIELDS)
            and revisions == (1, 2)
            and changed_verification_fields == {"content_digest"}
        )
    elif case_id == "history:absolute-resolved-path":
        scope = scopes.get(first.mutable_scope_ref)
        valid = (
            first.mutable_scope_ref == "scope:absolute"
            and scope is not None
            and len(scope.paths) == 1
            and scope.paths[0].startswith("/")
        )
    elif case_id == "history:redundant-resolved-scope":
        scope = scopes.get(first.mutable_scope_ref)
        valid = (
            first.mutable_scope_ref == "scope:redundant"
            and scope is not None
            and any(
                capability_reducer._path_overlap(path, other)
                for index, path in enumerate(scope.paths)
                for other in scope.paths[index + 1 :]
            )
        )
    elif case_id == _MIXED_VERSION_CASE_ID:
        valid = source_ids[0] == source_ids[1]
    elif case_id in {
        "history:future-v1-schema",
        "history:nonzero-epoch-material",
    }:
        valid = True
    else:
        valid = False
    if not valid:
        raise _legacy_invalid()


def _validate_history_case_oracle(
    case: dict[str, object],
    records: list[dict[str, object]],
    normalized_orders: list[tuple[int, ...]],
    expected: dict[str, object],
    actors: dict[str, capability_reducer.ActorContext],
    scopes: dict[str, capability_reducer.ResolvedScope],
) -> None:
    case_id = case["id"]
    oracle = _HISTORY_CASE_ORACLE.get(case_id)
    if oracle is None or (
        case["mapping_row_id"] != oracle.mapping_row_id
        or len(records) != oracle.record_count
        or tuple(record.get("schema") for record in records) != oracle.schemas
        or tuple(normalized_orders) != oracle.orders
        or case["resolver_mode"] != oracle.resolver_mode
        or case["disposition"] != oracle.disposition
        or expected["error_code"] != oracle.expected_error
        or expected["envelope_count"] != oracle.envelope_count
        or tuple(expected["requested_transitions"])
        != oracle.requested_transitions
    ):
        raise _legacy_invalid()
    parsed = _oracle_parsed_history(case_id, records)
    _validate_history_relationship(case_id, parsed, actors, scopes)


def _check_corpus_impl(corpus: dict[str, object]) -> _CorpusReport:
    if set(corpus) != _CORPUS_FIELDS or corpus["schema_version"] != _CORPUS_SCHEMA:
        raise _legacy_invalid()
    source_digests, sources = _bound_sources(corpus)
    mapping_fixture = sources[_SOURCE_PATHS[0]]
    misuse_fixture = sources[_SOURCE_PATHS[1]]
    replay_fixture = sources[_SOURCE_PATHS[2]]

    if set(mapping_fixture) != {"schema_version", "source_values", "rows"}:
        raise _legacy_invalid()
    mapping_rows = mapping_fixture["rows"]
    if type(mapping_rows) is not list or not mapping_rows:
        raise _legacy_invalid()
    mapping_ids = [row["id"] for row in mapping_rows]
    if (
        any(type(row) is not dict for row in mapping_rows)
        or len(mapping_ids) != len(set(mapping_ids))
    ):
        raise _legacy_invalid()
    mapping_by_id = {row["id"]: row for row in mapping_rows}
    mapping_by_key = {
        (
            row["domain"],
            row["value"],
            tuple(sorted(row["context"].items())),
        ): row
        for row in mapping_rows
    }
    accepted_context_keys = set(compact_state_mapping._accepted_context_keys())
    adapter_rule_keys = [key for key, _rule in _ADAPTER_RULES]
    if (
        len(mapping_by_key) != len(mapping_rows)
        or len(adapter_rule_keys) != len(set(adapter_rule_keys))
        or set(mapping_by_key) != accepted_context_keys
        or set(adapter_rule_keys) != accepted_context_keys
    ):
        raise _legacy_invalid()

    if (
        set(misuse_fixture) != {"schema_version", "vectors"}
        or misuse_fixture["schema_version"] != _MISUSE_SCHEMA
    ):
        raise _legacy_invalid()
    misuse_vectors = misuse_fixture["vectors"]
    replay_vectors = replay_fixture.get("vectors")
    if (
        type(misuse_vectors) is not list
        or not misuse_vectors
        or any(
            type(vector) is not dict
            or set(vector) != _MISUSE_VECTOR_FIELDS
            for vector in misuse_vectors
        )
        or type(replay_vectors) is not list
        or any(type(vector) is not dict for vector in replay_vectors)
    ):
        raise _legacy_invalid()
    misuse_ids = [vector["id"] for vector in misuse_vectors]
    if (
        any(type(misuse_id) is not str or not misuse_id for misuse_id in misuse_ids)
        or len(misuse_ids) != len(set(misuse_ids))
        or any(
            type(vector["enforcing_phase"]) is not int
            or vector["enforcing_phase"] not in {2, 3}
            for vector in misuse_vectors
        )
    ):
        raise _legacy_invalid()
    phase2_ids = {
        vector["id"]
        for vector in misuse_vectors
        if vector["enforcing_phase"] == 2
    }
    phase3_ids = {
        vector["id"]
        for vector in misuse_vectors
        if vector["enforcing_phase"] == 3
    }
    replay_ids = [vector.get("id") for vector in replay_vectors]
    replay_misuse_ids = [
        vector.get("misuse_vector_id") for vector in replay_vectors
    ]
    declared_replay_misuse_ids = [
        misuse_id for misuse_id in replay_misuse_ids if misuse_id is not None
    ]
    if (
        any(type(replay_id) is not str or not replay_id for replay_id in replay_ids)
        or len(replay_ids) != len(set(replay_ids))
        or any(
            misuse_id is not None
            and (type(misuse_id) is not str or not misuse_id)
            for misuse_id in replay_misuse_ids
        )
        or len(declared_replay_misuse_ids)
        != len(set(declared_replay_misuse_ids))
        or not set(declared_replay_misuse_ids) <= phase2_ids
        or set(declared_replay_misuse_ids) & phase3_ids
    ):
        raise _legacy_invalid()
    replay_by_id = dict(zip(replay_ids, replay_vectors, strict=True))

    cases = corpus["cases"]
    manifest = corpus["case_manifest"]
    if type(cases) is not list or not cases or type(manifest) is not list:
        raise _legacy_invalid()
    if any(type(item) is not dict or set(item) != _CASE_FIELDS for item in cases):
        raise _legacy_invalid()
    case_ids = [item["id"] for item in cases]
    if (
        any(type(case_id) is not str or not case_id for case_id in case_ids)
        or len(case_ids) != len(set(case_ids))
        or manifest != case_ids
    ):
        raise _legacy_invalid()
    case_by_id = dict(zip(case_ids, cases, strict=True))
    history_case_ids = {
        item["id"] for item in cases if item["case_kind"] == "history"
    }
    if history_case_ids != set(_HISTORY_CASE_ORACLE):
        raise _legacy_invalid()
    mapping_cases = [item for item in cases if item["case_kind"] == "mapping"]
    if [item["mapping_row_id"] for item in mapping_cases] != mapping_ids:
        raise _legacy_invalid()
    mapping_case_keys = {
        (
            mapping_by_id[item["mapping_row_id"]]["domain"],
            mapping_by_id[item["mapping_row_id"]]["value"],
            tuple(
                sorted(
                    mapping_by_id[item["mapping_row_id"]]["context"].items()
                )
            ),
        )
        for item in mapping_cases
    }
    if mapping_case_keys != accepted_context_keys:
        raise _legacy_invalid()
    template_case = case_by_id.get("mapping:capacity-ready")
    if type(template_case) is not dict:
        raise _legacy_invalid()
    template_records = template_case["source_records"]
    if (
        type(template_records) is not list
        or len(template_records) != 1
        or type(template_records[0]) is not dict
    ):
        raise _legacy_invalid()
    specialized_probe_template = template_records[0]
    named_route_ids: set[str] = set()
    named_unit_ids: set[str] = set()
    for item in cases:
        source_records = item["source_records"]
        if type(source_records) is not list:
            raise _legacy_invalid()
        for source_record in source_records:
            if type(source_record) is not dict:
                raise _legacy_invalid()
            route_id = source_record.get("route_id")
            unit_id = source_record.get("unit_id")
            if route_id is not None:
                named_route_ids.add(
                    _require_string(route_id, capability_reducer.ID_PATTERN)
                )
            if unit_id is not None:
                named_unit_ids.add(
                    _require_string(unit_id, capability_reducer.ID_PATTERN)
                )
    if not named_route_ids or not named_unit_ids:
        raise _legacy_invalid()
    named_route_id = min(named_route_ids)
    named_unit_id = min(named_unit_ids)
    specialized_probe_axes = (
        (None, None),
        (None, named_unit_id),
        (named_route_id, None),
        (named_route_id, named_unit_id),
    )

    bindings = corpus["phase2_misuse_bindings"]
    deferred = corpus["deferred_phase3_misuse_ids"]
    corpus_replays = corpus["reducer_replay_ids"]
    if (
        type(bindings) is not dict
        or set(bindings) != phase2_ids
        or type(deferred) is not list
        or len(deferred) != len(set(deferred))
        or set(deferred) != phase3_ids
        or set(bindings) & set(deferred)
        or corpus_replays != replay_ids
    ):
        raise _legacy_invalid()
    bound_targets: set[tuple[str, str]] = set()
    replay_bound_misuse_ids: set[str] = set()
    for misuse_id, value in bindings.items():
        binding = _require_exact_object(
            value, frozenset({"target_kind", "target_id"})
        )
        target = (binding["target_kind"], binding["target_id"])
        if (
            type(target[0]) is not str
            or type(target[1]) is not str
            or target in bound_targets
        ):
            raise _legacy_invalid()
        bound_targets.add(target)
        if target[0] == "case":
            if target[1] not in case_by_id:
                raise _legacy_invalid()
            target_case = case_by_id[target[1]]
            if (
                target_case["case_kind"] not in {"history", "misuse"}
                or target_case["misuse_vector_id"] != misuse_id
                or not target_case["source_records"]
            ):
                raise _legacy_invalid()
        elif target[0] == "reducer_replay":
            if (
                target[1] not in replay_by_id
                or replay_by_id[target[1]]["misuse_vector_id"] != misuse_id
            ):
                raise _legacy_invalid()
            replay_bound_misuse_ids.add(misuse_id)
        else:
            raise _legacy_invalid()
    if replay_bound_misuse_ids != set(declared_replay_misuse_ids):
        raise _legacy_invalid()
    _validate_case_bound_misuse_deltas(case_by_id, bindings)

    actors, scopes = _fixture_runtime(corpus)
    findings: set[tuple[str, str]] = set()
    specialized_event_ids: set[str] = set()
    executed_case_ids: list[str] = []

    for case in cases:
        case_id = case["id"]
        kind = case["case_kind"]
        mapping_id = case["mapping_row_id"]
        misuse_id = case["misuse_vector_id"]
        if kind not in {"mapping", "history", "misuse"}:
            raise _legacy_invalid()
        if (mapping_id is None) == (misuse_id is None):
            raise _legacy_invalid()
        if kind == "mapping":
            if mapping_id not in mapping_by_id or misuse_id is not None:
                raise _legacy_invalid()
        elif kind == "history":
            if mapping_id not in mapping_by_id or misuse_id is not None:
                raise _legacy_invalid()
        elif misuse_id not in phase2_ids or mapping_id is not None:
            raise _legacy_invalid()

        records = case["source_records"]
        orders = case["record_orders"]
        resolver_mode = case["resolver_mode"]
        expected = _require_exact_object(case["expected"], _EXPECTED_FIELDS)
        if (
            type(records) is not list
            or type(orders) is not list
            or not orders
            or resolver_mode
            not in {"stable", "actor_drift", "scope_drift"}
        ):
            raise _legacy_invalid()
        if kind == "mapping" and len(records) > 1:
            raise _legacy_invalid()
        for record in records:
            if type(record) is not dict or "source_digest" not in record:
                raise _legacy_invalid()
            source_digest = record["source_digest"]
            if (
                type(source_digest) is not str
                or fullmatch(capability_reducer.DIGEST_PATTERN, source_digest)
                is None
                or source_digest
                != _canonical_digest(
                    {
                        key: value
                        for key, value in record.items()
                        if key != "source_digest"
                    }
                )
            ):
                raise _legacy_invalid()
        declared_indexes = set(range(len(records)))
        duplicate_delivery = (
            case_id == _EXACT_DUPLICATE_DELIVERY_CASE_ID
            and orders == [[0, 0]]
        )
        if (
            case_id == _EXACT_DUPLICATE_DELIVERY_CASE_ID
            and not duplicate_delivery
        ):
            raise _legacy_invalid()
        normalized_orders: list[tuple[int, ...]] = []
        for order in orders:
            if type(order) is not list:
                raise _legacy_invalid()
            if any(
                type(index) is not int
                or not 0 <= index < len(records)
                for index in order
            ):
                raise _legacy_invalid()
            if (
                set(order) != declared_indexes
                or (len(order) != len(records) and not duplicate_delivery)
            ):
                raise _legacy_invalid()
            normalized_orders.append(tuple(order))

        projections = expected["projections"]
        expected_count = expected["envelope_count"]
        expected_transitions = expected["requested_transitions"]
        expected_error = expected["error_code"]
        if (
            type(projections) is not list
            or not projections
            or type(expected_count) is not int
            or expected_count < 0
            or type(expected_transitions) is not list
            or any(type(item) is not str for item in expected_transitions)
            or (
                expected_error is not None
                and expected_error not in _LEGACY_ERROR_CODES
            )
        ):
            raise _legacy_invalid()
        committed_projections = tuple(
            _require_exact_object(projected, _PROJECTION_FIELDS)
            for projected in projections
        )
        if expected_error is None:
            expected_disposition = (
                "route_event" if expected_count > 0 else "no_route_event"
            )
            if (
                case["disposition"]
                not in {"route_event", "no_route_event"}
                or case["disposition"] != expected_disposition
                or len(expected_transitions) != expected_count
                or any(
                    projected["disposition"] != case["disposition"]
                    for projected in committed_projections
                )
            ):
                raise _legacy_invalid()
        elif (
            case["disposition"] != expected_error
            or expected_count != 0
            or expected_transitions
        ):
            raise _legacy_invalid()

        if kind == "history":
            _validate_history_case_oracle(
                case,
                records,
                normalized_orders,
                expected,
                actors,
                scopes,
            )

        if case_id == _MIXED_VERSION_CASE_ID and (
            kind != "history"
            or len(records) != 2
            or tuple(record.get("schema") for record in records)
            != (_LEGACY_SCHEMA, capability_reducer.SCHEMA_ID)
            or normalized_orders != [(0, 1)]
            or expected_error != "legacy_version"
        ):
            raise _legacy_invalid()

        parser_error_codes: list[str] = []
        for record in records:
            try:
                _parse_legacy_record(record)
            except LegacyAdapterError as error:
                parser_error_codes.append(error.code)
            except Exception:
                raise _legacy_invalid() from None
        if parser_error_codes and (
            len(parser_error_codes) != 1
            or parser_error_codes[0] != expected_error
        ):
            raise _legacy_invalid()

        if records:
            observation_rows: list[dict[str, object]] = []
            observation_keys: list[
                tuple[str, str, tuple[tuple[str, bool | str], ...]]
            ] = []
            for record in records:
                context = record.get("context")
                if type(context) is not dict:
                    raise _legacy_invalid()
                key = (
                    record.get("domain"),
                    record.get("value"),
                    tuple(sorted(context.items())),
                )
                if key not in mapping_by_key:
                    raise _legacy_invalid()
                observation_keys.append(key)
                observation_rows.append(mapping_by_key[key])
        else:
            if kind != "mapping":
                raise _legacy_invalid()
            row = mapping_by_id[mapping_id]
            observation_rows = [row]
            observation_keys = [
                (
                    row["domain"],
                    row["value"],
                    tuple(sorted(row["context"].items())),
                )
            ]
        if kind == "mapping":
            declared = mapping_by_id[mapping_id]
            declared_key = (
                declared["domain"],
                declared["value"],
                tuple(sorted(declared["context"].items())),
            )
            if records and observation_keys != [declared_key]:
                raise _legacy_invalid()
        elif kind == "history":
            declared = mapping_by_id[mapping_id]
            declared_key = (
                declared["domain"],
                declared["value"],
                tuple(sorted(declared["context"].items())),
            )
            if any(
                not order
                or observation_keys[order[-1]] != declared_key
                for order in normalized_orders
            ):
                raise _legacy_invalid()
        if len(projections) != len(observation_rows):
            raise _legacy_invalid()

        for projected, row, key in zip(
            committed_projections,
            observation_rows,
            observation_keys,
            strict=True,
        ):
            committed = projected
            if (
                committed["disposition"]
                not in {"route_event", "no_route_event"}
                or committed["effect_eligibility"] not in _EFFECT_ORDER
                or type(committed["advisory_only"]) is not bool
            ):
                raise _legacy_invalid()
            golden = _golden_projection(row)
            _append_kind(
                findings,
                case_id,
                _projection_kind(committed, golden),
            )
            try:
                current = _projection_from_meaning(
                    _v1_disposition(row),
                    compact_state_mapping.meaning_for(
                        row["domain"],
                        row["value"],
                        context=row["context"],
                    ),
                )
                _append_kind(
                    findings,
                    case_id,
                    _projection_kind(current, golden),
                )
            except Exception:
                _append_kind(findings, case_id, "adapter_error")
            try:
                rule = _rule_for_key(key)
                emitted = object() if rule.requested_transition is not None else None
                actual = _compact_projection(rule, emitted)
                _append_kind(
                    findings,
                    case_id,
                    _projection_kind(actual, golden),
                )
                if (
                    kind == "mapping"
                    and golden["disposition"] == "no_route_event"
                    and actual["disposition"] == "route_event"
                ):
                    specialized_event_ids.add(case_id)
            except LegacyAdapterError:
                _append_kind(findings, case_id, "adapter_error")

        first_success: tuple[
            capability_reducer.TransitionEnvelope, ...
        ] | None = None
        if not records:
            if expected_count != 0 or expected_transitions or expected_error:
                _append_kind(findings, case_id, "adapter_error")
            probe_rule = _rule_for_key(observation_keys[0])
            if kind == "mapping" and probe_rule.requested_transition is None:
                for probe_route_id, probe_unit_id in specialized_probe_axes:
                    resolver_used = False

                    def reject_resolver(_value: str) -> object:
                        nonlocal resolver_used
                        resolver_used = True
                        raise RuntimeError

                    probe = _specialized_probe_record(
                        specialized_probe_template,
                        mapping_by_id[mapping_id],
                        route_id=probe_route_id,
                        unit_id=probe_unit_id,
                    )
                    try:
                        result = adapt_v1_history(
                            (probe,),
                            resolve_actor=reject_resolver,
                            resolve_scope=reject_resolver,
                        )
                    except LegacyAdapterError as error:
                        if error.code != "legacy_unmapped":
                            _append_kind(findings, case_id, "adapter_error")
                    except Exception:
                        _append_kind(findings, case_id, "adapter_error")
                    else:
                        _append_kind(findings, case_id, "adapter_error")
                        if result:
                            specialized_event_ids.add(case_id)
                    if resolver_used:
                        _append_kind(findings, case_id, "adapter_error")
        else:
            accepted_prefix = (
                _HISTORY_CASE_ORACLE[case_id].accepted_prefix_transitions
                if kind == "history"
                else ()
            )
            if accepted_prefix:
                resolve_actor, resolve_scope = _case_resolvers(
                    resolver_mode, actors, scopes
                )
                try:
                    prefix_result = adapt_v1_history(
                        tuple(records[: len(accepted_prefix)]),
                        resolve_actor=resolve_actor,
                        resolve_scope=resolve_scope,
                    )
                except Exception:
                    _append_kind(findings, case_id, "adapter_error")
                else:
                    if (
                        len(prefix_result) != len(accepted_prefix)
                        or tuple(
                            event.requested_transition for event in prefix_result
                        )
                        != accepted_prefix
                    ):
                        _append_kind(
                            findings, case_id, "authority_semantic_mismatch"
                        )
            for order in normalized_orders:
                raw_history = tuple(records[index] for index in order)
                resolve_actor, resolve_scope = _case_resolvers(
                    resolver_mode, actors, scopes
                )
                try:
                    result = adapt_v1_history(
                        raw_history,
                        resolve_actor=resolve_actor,
                        resolve_scope=resolve_scope,
                    )
                except LegacyAdapterError as error:
                    if expected_error != error.code:
                        _append_kind(findings, case_id, "adapter_error")
                    continue
                if expected_error is not None:
                    _append_kind(findings, case_id, "adapter_error")
                    continue
                if (
                    len(result) != expected_count
                    or [event.requested_transition for event in result]
                    != expected_transitions
                ):
                    _append_kind(
                        findings, case_id, "authority_semantic_mismatch"
                    )
                if first_success is None:
                    first_success = result
                elif result != first_success:
                    _append_kind(findings, case_id, "adapter_error")

        executed_case_ids.append(case_id)
        if not any(item[0] == case_id for item in findings):
            findings.add((case_id, "match"))

    permutation_count = sum(
        len(vector["permutations"]) for vector in replay_vectors
    )
    set_counts = (
        ("mapping_rows", len(mapping_rows)),
        ("mapping_domains", len({row["domain"] for row in mapping_rows})),
        ("phase2_misuse_vectors", len(phase2_ids)),
        ("deferred_phase3_misuse_vectors", len(phase3_ids)),
        ("reducer_replay_vectors", len(replay_ids)),
        ("reducer_replay_permutations", permutation_count),
        ("corpus_cases", len(cases)),
    )
    return _CorpusReport(
        source_digests=source_digests,
        set_counts=set_counts,
        corpus_digest=_canonical_digest(corpus),
        divergences=tuple(
            _Divergence(case_id, kind)
            for case_id, kind in sorted(findings)
        ),
        specialized_event_ids=tuple(sorted(specialized_event_ids)),
        deferred_phase3_misuse_ids=tuple(sorted(phase3_ids)),
        executed_case_ids=tuple(executed_case_ids),
    )


def _check_corpus(value: object) -> _CorpusReport:
    try:
        if type(value) is not dict:
            raise _legacy_invalid()
        return _check_corpus_impl(value)
    except LegacyAdapterError:
        raise
    except Exception:
        raise _legacy_invalid() from None


def _report_is_gate_clean(report: _CorpusReport) -> bool:
    return not any(
        item.kind in _BLOCKING_PARITY_KINDS for item in report.divergences
    )


def _report_mapping(report: _CorpusReport) -> dict[str, object]:
    by_kind = {
        kind: sorted(
            {
                item.case_id
                for item in report.divergences
                if item.kind == kind
            }
        )
        for kind in sorted(_PARITY_KINDS)
    }
    body: dict[str, object] = {
        "schema": _REPORT_SCHEMA,
        "mode": "shadow",
        "source_digests": dict(report.source_digests),
        "set_counts": dict(report.set_counts),
        "corpus_digest": report.corpus_digest,
        "case_ids_by_divergence_class": by_kind,
        "specialized_event_ids": list(report.specialized_event_ids),
        "deferred_phase3_misuse_ids": list(
            report.deferred_phase3_misuse_ids
        ),
    }
    return {**body, "report_digest": _canonical_digest(body)}


def adapt_v1_history(
    records: Iterable[object],
    *,
    resolve_actor: capability_reducer.ActorBindingResolver,
    resolve_scope: capability_reducer.ScopeResolver,
) -> tuple[capability_reducer.TransitionEnvelope, ...]:
    """Return only fully validated, reducer-accepted shadow envelopes."""

    try:
        raw_records = tuple(records)
    except Exception:
        raise _legacy_invalid() from None
    if not raw_records:
        return ()

    parsed = tuple(_parse_legacy_record(record) for record in raw_records)
    return _adapt_parsed_history(
        parsed,
        resolve_actor=resolve_actor,
        resolve_scope=resolve_scope,
    )


def main(argv: list[str] | None = None) -> int:
    """Check one committed corpus and print its sanitized canonical report."""

    try:
        arguments = tuple(sys.argv[1:] if argv is None else argv)
    except Exception:
        return 1
    if (
        len(arguments) != 2
        or arguments[0] != "--check-corpus"
        or type(arguments[1]) is not str
        or not arguments[1]
    ):
        return 1
    try:
        corpus = _strict_json_loads(
            Path(arguments[1]).read_text(encoding="utf-8")
        )
        report = _check_corpus(corpus)
        rendered = canonicalize(_report_mapping(report)).decode("utf-8")
        sys.stdout.write(rendered + "\n")
    except Exception:
        return 1
    return 0 if _report_is_gate_clean(report) else 1


if __name__ == "__main__":
    raise SystemExit(main())
