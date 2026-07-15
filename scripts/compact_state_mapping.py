#!/usr/bin/env python3
"""Pure Phase-1 meanings for current protocol lifecycle values.

This module is observational only.  It does not read or write protocol state,
grant authority, execute an effect, or change any live producer.  The fixture
checker exists solely to freeze the v1 compatibility contract before the
compact reducer is introduced.
"""

from __future__ import annotations

import argparse
from collections.abc import Mapping
from dataclasses import asdict, dataclass
import json
from pathlib import Path
import sys
from typing import Any

import chatgpt_pro_consult
import consume_reviewer_result
import opus_review_bridge
import opus_review_receipts
import protocol_capacity
import route_capability


class StateMappingError(ValueError):
    """The requested observational meaning is unknown or internally invalid."""


_FIXTURE_SCHEMA = "compact-state-mapping/v1"
_WORK_RESULTS = frozenset(
    {"cancelled", "failed", "outcome_unknown", "superseded"}
)
_EFFECT_ELIGIBILITY = frozenset(
    {"never", "separate_current_grant", "all_other_gates"}
)
_UNCONCLUDED_LOCAL_VERDICTS = (
    frozenset(consume_reviewer_result.VERDICTS)
    - frozenset(opus_review_bridge.VALID_STATUSES)
)
if len(_UNCONCLUDED_LOCAL_VERDICTS) != 1:
    raise StateMappingError(
        "expected exactly one producer-backed unconcluded local verdict"
    )
_UNCONCLUDED_LOCAL_VERDICT = next(iter(_UNCONCLUDED_LOCAL_VERDICTS))
_LOCAL_VERDICTS = frozenset(opus_review_bridge.VALID_CODEX_VERDICTS) | {
    _UNCONCLUDED_LOCAL_VERDICT
}


@dataclass(frozen=True)
class StateMeaning:
    compact: str
    terminal_scope: str
    next_action: str
    effect_eligibility: str
    advisory_only: bool


def _meaning(
    compact: str,
    terminal_scope: str,
    next_action: str,
    effect_eligibility: str,
    advisory_only: bool,
) -> StateMeaning:
    if effect_eligibility not in _EFFECT_ELIGIBILITY:
        raise StateMappingError(
            f"unsupported effect eligibility {effect_eligibility!r}"
        )
    return StateMeaning(
        compact,
        terminal_scope,
        next_action,
        effect_eligibility,
        advisory_only,
    )


_RUN = _meaning("RUN", "nonterminal", "continue", "never", False)
_DONE = _meaning(
    "DONE", "unit_version", "none", "separate_current_grant", False
)
_REVIEW = _meaning("REVIEW", "nonterminal", "obtain_review", "never", False)


def _source_values() -> dict[str, list[str]]:
    """Return exact sorted values from the current v1 producers."""

    return {
        "capacity": sorted(protocol_capacity.STATUSES),
        "capability": sorted(route_capability.LIFECYCLE_STATES),
        "chatgpt": sorted(chatgpt_pro_consult.ALLOWED_TRANSITIONS),
        "opus_receipt": sorted(opus_review_receipts.RECEIPT_STATES),
        "provider_result": sorted(opus_review_bridge.VALID_STATUSES),
        "local_verdict": sorted(_LOCAL_VERDICTS),
        "work_result": sorted(_WORK_RESULTS),
    }


_ContextKey = tuple[
    str,
    str,
    tuple[tuple[str, bool | str], ...],
]


def _accepted_context_keys() -> tuple[_ContextKey, ...]:
    """Return every finite producer-backed context accepted by current v1."""

    sources = _source_values()
    keys: set[_ContextKey] = set()

    def add(
        domain: str,
        value: str,
        context: Mapping[str, bool | str],
    ) -> None:
        keys.add((domain, value, tuple(sorted(context.items()))))

    capacity_values = set(sources["capacity"])
    if capacity_values != {"ready", "active", "blocked", "done", "excepted"}:
        raise StateMappingError("capacity producer vocabulary is not classified")
    for value in ("ready", "active", "excepted"):
        add("capacity", value, {})
    for completion_evidence in (False, True):
        for verification_required in (False, True):
            add(
                "capacity",
                "blocked",
                {
                    "completion_evidence": completion_evidence,
                    "verification_required": verification_required,
                },
            )
    for required, satisfied, gates_met in (
        (True, False, False),
        (True, True, True),
        (False, False, True),
    ):
        add(
            "capacity",
            "done",
            {
                "verification_required": required,
                "verification_satisfied": satisfied,
                "all_triggered_gates_met": gates_met,
            },
        )

    capability_values = set(sources["capability"])
    if capability_values != {
        "issued",
        "activated",
        "consumed",
        "revoked",
        "expired",
        "failed",
    }:
        raise StateMappingError("capability producer vocabulary is not classified")
    for value in capability_values - {"consumed"}:
        add("capability", value, {})
    for outcome in ("ok", "failed", "absent"):
        add("capability", "consumed", {"receipt_outcome": outcome})

    chatgpt_values = set(sources["chatgpt"])
    if "failed" not in chatgpt_values:
        raise StateMappingError("ChatGPT producer vocabulary lacks failed")
    for value in chatgpt_values - {"failed"}:
        add("chatgpt", value, {})
    for failure_class in sorted(chatgpt_pro_consult.FAILURE_CLASSES):
        for transport in sorted(chatgpt_pro_consult.TRANSPORTS):
            for resume_authorized in (False, True):
                if failure_class == "partial_send" and resume_authorized:
                    continue
                if resume_authorized and transport != "manual":
                    continue
                add(
                    "chatgpt",
                    "failed",
                    {
                        "failure_class": failure_class,
                        "transport": transport,
                        "manual_resume_authorized": resume_authorized,
                    },
                )

    receipt_values = set(sources["opus_receipt"])
    if receipt_values != {
        "reserved",
        "reviewed",
        "reconciled",
        "publishing",
        "published",
    }:
        raise StateMappingError("Opus receipt producer vocabulary is not classified")
    for action in opus_review_receipts.RESERVATION_ACTIONS:
        add("opus_receipt", "reserved", {"reservation_action": action})
    for status in sorted(opus_review_bridge.VALID_STATUSES):
        add("opus_receipt", "reviewed", {"provider_status": status})
    for disposition in sorted(opus_review_bridge.VALID_CODEX_VERDICTS):
        add("opus_receipt", "reconciled", {"disposition": disposition})
    for value in ("publishing", "published"):
        add("opus_receipt", value, {})

    for value in sources["provider_result"]:
        add("provider_result", value, {})
    for value in sources["local_verdict"]:
        context = {"verification_key_matches": True} if value == "GO" else {}
        add("local_verdict", value, context)
    for value in sources["work_result"]:
        add("work_result", value, {})

    return tuple(sorted(keys, key=repr))


def _strict_context(
    context: Mapping[str, object], required: frozenset[str]
) -> Mapping[str, object]:
    if set(context) != required:
        expected = ", ".join(sorted(required)) or "none"
        actual = ", ".join(sorted((repr(key) for key in context))) or "none"
        raise StateMappingError(
            f"context fields do not match: expected {expected}; got {actual}"
        )
    return context


def _bool(context: Mapping[str, object], field: str) -> bool:
    value = context[field]
    if type(value) is not bool:
        raise StateMappingError(f"context.{field} must be a boolean")
    return value


def _enum(
    context: Mapping[str, object], field: str, allowed: frozenset[str]
) -> str:
    value = context[field]
    if not isinstance(value, str) or value not in allowed:
        raise StateMappingError(
            f"context.{field} must be one of: {', '.join(sorted(allowed))}"
        )
    return value


def _capacity_meaning(value: str, context: Mapping[str, object]) -> StateMeaning:
    if value in {"ready", "active"}:
        _strict_context(context, frozenset())
        return _RUN
    if value == "blocked":
        _strict_context(
            context, frozenset({"completion_evidence", "verification_required"})
        )
        completion_evidence = _bool(context, "completion_evidence")
        verification_required = _bool(context, "verification_required")
        if not completion_evidence:
            return _meaning(
                "WAIT", "nonterminal", "wait_for_named_condition", "never", False
            )
        if verification_required:
            return _REVIEW
        return _DONE
    if value == "done":
        _strict_context(
            context,
            frozenset(
                {
                    "verification_required",
                    "verification_satisfied",
                    "all_triggered_gates_met",
                }
            ),
        )
        required = _bool(context, "verification_required")
        satisfied = _bool(context, "verification_satisfied")
        gates_met = _bool(context, "all_triggered_gates_met")
        if required and not satisfied and not gates_met:
            return _REVIEW
        if required and satisfied and gates_met:
            return _DONE
        if not required and not satisfied and gates_met:
            return _DONE
        raise StateMappingError("contradictory or incomplete done-state context")
    if value == "excepted":
        _strict_context(context, frozenset())
        return _meaning(
            "DONE",
            "unit_version",
            "new_unit_version",
            "separate_current_grant",
            False,
        )
    raise StateMappingError(f"unsupported capacity value {value!r}")


def _capability_meaning(
    value: str, context: Mapping[str, object]
) -> StateMeaning:
    if value in {"issued", "activated"}:
        _strict_context(context, frozenset())
        return _meaning(
            "GRANT_AVAILABLE",
            "nonterminal",
            "attempt_if_other_gates_pass",
            "all_other_gates",
            False,
        )
    if value == "consumed":
        _strict_context(context, frozenset({"receipt_outcome"}))
        outcome = _enum(
            context, "receipt_outcome", frozenset({"ok", "failed", "absent"})
        )
        if outcome == "ok":
            return _meaning(
                "SUCCEEDED", "capability", "none", "never", False
            )
        if outcome == "failed":
            return _meaning(
                "FAILED", "capability", "no_new_attempt", "never", False
            )
        return _meaning(
            "OUTCOME_UNKNOWN", "capability", "reconcile_only", "never", False
        )
    if value in {"revoked", "expired", "failed"}:
        _strict_context(context, frozenset())
        compact = {
            "revoked": "REVOKED",
            "expired": "EXPIRED",
            "failed": "FAILED",
        }[value]
        return _meaning(
            compact, "capability", "no_new_attempt", "never", False
        )
    raise StateMappingError(f"unsupported capability value {value!r}")


_CHATGPT_SIMPLE = {
    "prepared": _meaning(
        "RESERVED", "nonterminal", "send_once", "never", True
    ),
    "sending": _meaning(
        "ATTEMPTING", "nonterminal", "complete_send_or_reconcile", "never", True
    ),
    "sent": _meaning(
        "AWAITING_RESPONSE",
        "nonterminal",
        "accept_response_or_mark_stale",
        "never",
        True,
    ),
    "received": _meaning(
        "RESPONSE_RECEIVED", "nonterminal", "reconcile_locally", "never", True
    ),
    "reconciled": _meaning(
        "RECONCILED", "consultation", "none", "never", True
    ),
    "stale": _meaning(
        "STALE", "consultation", "no_retry", "never", True
    ),
}


def _chatgpt_meaning(value: str, context: Mapping[str, object]) -> StateMeaning:
    if value in _CHATGPT_SIMPLE:
        _strict_context(context, frozenset())
        return _CHATGPT_SIMPLE[value]
    if value != "failed":
        raise StateMappingError(f"unsupported ChatGPT value {value!r}")

    _strict_context(
        context,
        frozenset({"failure_class", "transport", "manual_resume_authorized"}),
    )
    failure_class = _enum(
        context, "failure_class", chatgpt_pro_consult.FAILURE_CLASSES
    )
    transport = _enum(context, "transport", chatgpt_pro_consult.TRANSPORTS)
    resume_authorized = _bool(context, "manual_resume_authorized")
    if failure_class == "partial_send":
        if resume_authorized:
            raise StateMappingError(
                "ambiguous partial_send cannot authorize resume or retry"
            )
        return _meaning(
            "OUTCOME_UNKNOWN", "consultation", "reconcile_only", "never", True
        )
    if resume_authorized:
        if transport != "manual":
            raise StateMappingError(
                "manual resume authority requires manual-origin transport"
            )
        return _meaning(
            "FAILED", "nonterminal", "resume_manual", "never", True
        )
    return _meaning(
        "FAILED", "consultation", "no_retry", "never", True
    )


def _opus_receipt_meaning(
    value: str, context: Mapping[str, object]
) -> StateMeaning:
    if value == "reserved":
        _strict_context(context, frozenset({"reservation_action"}))
        action = _enum(
            context,
            "reservation_action",
            frozenset(opus_review_receipts.RESERVATION_ACTIONS),
        )
        if action == "launch":
            return _meaning(
                "RESERVED", "nonterminal", "launch_once", "never", True
            )
        if action == "return":
            return _meaning(
                "RESERVED",
                "nonterminal",
                "return_without_launch",
                "never",
                True,
            )
        return _meaning(
            "OUTCOME_UNKNOWN", "attempt", "reconcile_only", "never", True
        )
    if value == "reviewed":
        _strict_context(context, frozenset({"provider_status"}))
        status = _enum(
            context, "provider_status", opus_review_bridge.VALID_STATUSES
        )
        return _meaning(
            f"REVIEWED_{status.upper()}",
            "nonterminal",
            "local_reconcile",
            "never",
            True,
        )
    if value == "reconciled":
        _strict_context(context, frozenset({"disposition"}))
        disposition = _enum(
            context, "disposition", opus_review_bridge.VALID_CODEX_VERDICTS
        )
        return _meaning(
            f"RECONCILED_{disposition}",
            "provider_review",
            "consult_local_verdict",
            "never",
            True,
        )
    if value == "publishing":
        _strict_context(context, frozenset())
        return _meaning(
            "PUBLISHING",
            "nonterminal",
            "recover_publication",
            "never",
            True,
        )
    if value == "published":
        _strict_context(context, frozenset())
        return _meaning(
            "PUBLISHED", "publication_phase", "none", "never", True
        )
    raise StateMappingError(f"unsupported Opus receipt value {value!r}")


def _provider_result_meaning(
    value: str, context: Mapping[str, object]
) -> StateMeaning:
    _strict_context(context, frozenset())
    next_action = (
        "continue_without_provider" if value == "unavailable" else "local_reconcile"
    )
    return _meaning(
        f"PROVIDER_{value.upper()}", "none", next_action, "never", True
    )


def _local_verdict_meaning(
    value: str, context: Mapping[str, object]
) -> StateMeaning:
    if value == _UNCONCLUDED_LOCAL_VERDICT:
        _strict_context(context, frozenset())
        return _meaning(
            "UNABLE_TO_VERIFY",
            "nonterminal",
            "redispatch_or_escalate",
            "never",
            False,
        )
    if value == "GO":
        _strict_context(context, frozenset({"verification_key_matches"}))
        if not _bool(context, "verification_key_matches"):
            raise StateMappingError("GO requires its exact verification key")
        return _meaning(
            "GO", "review", "continue_effect_gates", "all_other_gates", False
        )
    _strict_context(context, frozenset())
    return _meaning(
        value, "review", "new_scoped_version", "never", False
    )


_WORK_MEANINGS = {
    "cancelled": _meaning(
        "CANCELLED", "work", "new_work_id", "never", False
    ),
    "failed": _meaning(
        "FAILED",
        "attempt",
        "new_transition_if_policy_allows",
        "never",
        False,
    ),
    "superseded": _meaning(
        "SUPERSEDED", "version", "follow_successor", "never", False
    ),
    "outcome_unknown": _meaning(
        "OUTCOME_UNKNOWN", "nonterminal", "reconcile_only", "never", False
    ),
}


def meaning_for(
    domain: str, value: str, *, context: Mapping[str, object]
) -> StateMeaning:
    """Return the fail-closed observational meaning for one current v1 value."""

    if not isinstance(domain, str):
        raise StateMappingError("domain must be a string")
    if not isinstance(value, str):
        raise StateMappingError("value must be a string")
    if not isinstance(context, Mapping):
        raise StateMappingError("context must be a mapping")

    sources = _source_values()
    if domain not in sources:
        raise StateMappingError(f"unknown state domain {domain!r}")
    if value not in sources[domain]:
        raise StateMappingError(
            f"unknown value {value!r} for state domain {domain!r}"
        )

    if domain == "capacity":
        return _capacity_meaning(value, context)
    if domain == "capability":
        return _capability_meaning(value, context)
    if domain == "chatgpt":
        return _chatgpt_meaning(value, context)
    if domain == "opus_receipt":
        return _opus_receipt_meaning(value, context)
    if domain == "provider_result":
        return _provider_result_meaning(value, context)
    if domain == "local_verdict":
        return _local_verdict_meaning(value, context)
    if domain == "work_result":
        _strict_context(context, frozenset())
        return _WORK_MEANINGS[value]
    raise StateMappingError(f"unknown state domain {domain!r}")


def _fixture_result(value: object) -> tuple[int, int]:
    if not isinstance(value, Mapping) or set(value) != {
        "schema_version",
        "source_values",
        "rows",
    }:
        raise StateMappingError("fixture fields do not match the v1 contract")
    if value["schema_version"] != _FIXTURE_SCHEMA:
        raise StateMappingError("unsupported fixture schema version")

    source_values = value["source_values"]
    expected_sources = _source_values()
    if source_values != expected_sources:
        raise StateMappingError(
            "source-set parity mismatch between fixture and current producers"
        )

    rows = value["rows"]
    if not isinstance(rows, list) or not rows:
        raise StateMappingError("fixture rows must be a non-empty array")
    seen: set[str] = set()
    covered = {domain: set() for domain in expected_sources}
    row_keys: list[_ContextKey] = []
    expected_fields = {
        "compact",
        "terminal_scope",
        "next_action",
        "effect_eligibility",
        "advisory_only",
    }
    for index, row in enumerate(rows):
        if not isinstance(row, Mapping) or set(row) != {
            "id",
            "domain",
            "value",
            "context",
            "expected",
        }:
            raise StateMappingError(f"fixture row {index} fields do not match")
        row_id = row["id"]
        if not isinstance(row_id, str) or not row_id or row_id in seen:
            raise StateMappingError(f"fixture row {index} has invalid or duplicate id")
        seen.add(row_id)
        expected = row["expected"]
        if not isinstance(expected, Mapping) or set(expected) != expected_fields:
            raise StateMappingError(f"fixture row {row_id!r} expected fields do not match")
        if expected["effect_eligibility"] not in _EFFECT_ELIGIBILITY:
            raise StateMappingError(
                f"fixture row {row_id!r} has unknown effect eligibility"
            )
        domain = row["domain"]
        state_value = row["value"]
        context = row["context"]
        if (
            not isinstance(domain, str)
            or not isinstance(state_value, str)
            or not isinstance(context, Mapping)
            or any(type(key) is not str for key in context)
            or any(type(item) not in (bool, str) for item in context.values())
        ):
            raise StateMappingError(
                f"fixture row {row_id!r} context key is invalid"
            )
        row_keys.append(
            (domain, state_value, tuple(sorted(context.items())))
        )
        actual = meaning_for(
            domain, state_value, context=context
        )
        if asdict(actual) != dict(expected):
            raise StateMappingError(f"fixture row {row_id!r} meaning mismatch")
        covered[domain].add(state_value)

    accepted_keys = set(_accepted_context_keys())
    if len(row_keys) != len(set(row_keys)) or set(row_keys) != accepted_keys:
        raise StateMappingError(
            "fixture accepted context keys do not match current v1"
        )

    expected_coverage = {
        domain: set(values) for domain, values in expected_sources.items()
    }
    if covered != expected_coverage:
        raise StateMappingError("fixture does not cover every source value")
    return len(rows), len(expected_sources)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate the observational compact-state v1 fixture"
    )
    parser.add_argument("--check-fixture", required=True, type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    arguments = _parser().parse_args(argv)
    try:
        payload: Any = json.loads(
            arguments.check_fixture.read_text(encoding="utf-8")
        )
        row_count, domain_count = _fixture_result(payload)
    except (OSError, UnicodeError, json.JSONDecodeError, StateMappingError) as exc:
        print(f"compact-state-mapping: {exc}", file=sys.stderr)
        return 1
    print(f"validated {row_count} mappings across {domain_count} domains")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
