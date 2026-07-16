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

if __package__:
    from scripts import (
        protocol_capacity,
        route_capability,
    )
else:
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
_LOCAL_VERDICTS = frozenset({"GO", "NITS", "FAIL", "unable_to_verify"})


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


def _local_verdict_meaning(
    value: str, context: Mapping[str, object]
) -> StateMeaning:
    if value == "unable_to_verify":
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
    if value not in {"NITS", "FAIL"}:
        raise StateMappingError(f"unsupported local verdict value {value!r}")
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


def _context(context: Mapping[str, object] | None) -> Mapping[str, object]:
    if context is None:
        return {}
    if not isinstance(context, Mapping):
        raise StateMappingError("context must be a mapping")
    return context


def _work_result_meaning(
    value: str, context: Mapping[str, object]
) -> StateMeaning:
    if value not in _WORK_MEANINGS:
        raise StateMappingError(f"unsupported work result value {value!r}")
    _strict_context(context, frozenset())
    return _WORK_MEANINGS[value]


def meaning_for(
    domain: str,
    value: str,
    *,
    context: Mapping[str, object] | None = None,
) -> StateMeaning:
    normalized_context = _context(context)
    if domain == "capacity":
        return _capacity_meaning(value, normalized_context)
    if domain == "capability":
        return _capability_meaning(value, normalized_context)
    if domain == "local_verdict":
        return _local_verdict_meaning(value, normalized_context)
    if domain == "work_result":
        return _work_result_meaning(value, normalized_context)
    raise StateMappingError("unknown domain")


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
