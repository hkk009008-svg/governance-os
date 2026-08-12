"""Coverage for scripts/overseer_plan.py load_decision (previously untested)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

import overseer_plan


def _decision(**overrides) -> dict:
    base = {
        "schema": overseer_plan.SCHEMA,
        "candidate_id": "cand-1",
        "brief_id": "brief-1",
        "tier": "T1",
        "allowed_paths": ["scripts/"],
        "assignment": {
            "pair": "A",
            "builder": "director",
            "builder_provider": "codex",
            "primary_verifier": "operator",
            "primary_verifier_provider": "claude",
            "executing_coordinator": "coordinator",
        },
    }
    base.update(overrides)
    return base


def _write(tmp_path: Path, decision: dict) -> Path:
    path = tmp_path / "decision.json"
    path.write_text(json.dumps(decision), encoding="utf-8")
    return path


def test_valid_decision_loads_and_applies_defaults(tmp_path: Path) -> None:
    loaded = overseer_plan.load_decision(_write(tmp_path, _decision()))
    assert loaded["candidate_id"] == "cand-1"
    assert loaded["brief_version"] == 1
    assert loaded["policy_digest"] is None
    assert loaded["approvers"] == []


def test_missing_file_is_a_decision_error(tmp_path: Path) -> None:
    with pytest.raises(overseer_plan.DecisionError, match="not found"):
        overseer_plan.load_decision(tmp_path / "absent.json")


def test_bad_json_is_a_decision_error(tmp_path: Path) -> None:
    path = tmp_path / "decision.json"
    path.write_text("{not json", encoding="utf-8")
    with pytest.raises(overseer_plan.DecisionError, match="not valid JSON"):
        overseer_plan.load_decision(path)


def test_wrong_schema_is_rejected(tmp_path: Path) -> None:
    with pytest.raises(overseer_plan.DecisionError, match="schema must be"):
        overseer_plan.load_decision(_write(tmp_path, _decision(schema="other/1")))


@pytest.mark.parametrize(
    "field", ("candidate_id", "brief_id", "tier", "allowed_paths", "assignment")
)
def test_missing_required_field_is_rejected(tmp_path: Path, field: str) -> None:
    decision = _decision()
    decision.pop(field)
    with pytest.raises(overseer_plan.DecisionError, match="missing required field"):
        overseer_plan.load_decision(_write(tmp_path, decision))


def test_invalid_tier_is_rejected(tmp_path: Path) -> None:
    with pytest.raises(overseer_plan.DecisionError, match="tier"):
        overseer_plan.load_decision(_write(tmp_path, _decision(tier="T9")))


def test_t3_requires_two_distinct_approvers(tmp_path: Path) -> None:
    with pytest.raises(overseer_plan.DecisionError, match="2 distinct"):
        overseer_plan.load_decision(
            _write(tmp_path, _decision(tier="T3", approvers=["only-one"]))
        )
    ok = overseer_plan.load_decision(
        _write(tmp_path, _decision(tier="T3", approvers=["a", "b"]))
    )
    assert ok["tier"] == "T3"


def test_empty_allowed_paths_is_rejected(tmp_path: Path) -> None:
    with pytest.raises(overseer_plan.DecisionError, match="allowed_paths"):
        overseer_plan.load_decision(_write(tmp_path, _decision(allowed_paths=[])))


def test_assignment_missing_subfield_is_rejected(tmp_path: Path) -> None:
    decision = _decision()
    decision["assignment"].pop("primary_verifier")
    with pytest.raises(overseer_plan.DecisionError, match="assignment missing"):
        overseer_plan.load_decision(_write(tmp_path, decision))
