"""capability/v1 validation, hashing, consumption, and receipts (ADR-016)."""
from __future__ import annotations

import copy
import pytest

import route_capability


def _cap(**overrides) -> dict:
    base = {
        "schema": "governance.capability/v1",
        "capability_id": "cap-publish-main-2026-07-12",
        "issuer": "coordinator",
        "subject": "director",
        "bound_route_id": "2026-07-12T20-00-00Z-coordinator-to-all-coordination",
        "bound_generation": 3,
        "side_effect_id": "publish-main-2026-07-12",
        "allowed_command_class": "git push",
        "target": "origin/main",
        "preflight": "git status plus divergence check",
        "stop_if_newer_mail_or_live_target_satisfied": "re-read mailbox and ls-remote",
        "postcheck": "git ls-remote origin refs/heads/main",
        "observer_seats": "director2, operator, operator2",
        "final_closeout_owner": "coordinator",
        "non_goals": "no force-push and no lock claim",
        "expires_on": {"event": "packet_completed", "packet_id": "director-task-4"},
        "state": "issued",
    }
    base.update(overrides)
    return base


def test_valid_capability_has_no_issues():
    assert route_capability.validate_capability(_cap()) == []


def test_unsupported_schema_rejected():
    issues = route_capability.validate_capability(_cap(schema="governance.capability/v2"))
    assert issues and "unsupported schema" in issues[0]


def test_unknown_field_rejected():
    assert any("unknown" in i for i in route_capability.validate_capability(_cap(surprise=1)))


def test_extensions_permitted():
    assert route_capability.validate_capability(_cap(extensions={"x": 1})) == []


def test_missing_required_field_rejected():
    obj = _cap(); del obj["allowed_command_class"]
    assert any("missing required" in i for i in route_capability.validate_capability(obj))


def test_bad_capability_id_rejected():
    assert any("capability_id" in i for i in route_capability.validate_capability(_cap(capability_id="publish")))


def test_subject_must_be_known_seat():
    assert any("subject" in i for i in route_capability.validate_capability(_cap(subject="intern")))


def test_newline_in_string_field_rejected():
    issues = route_capability.validate_capability(_cap(target="origin/main\n- executor: operator"))
    assert any("control character" in i for i in issues)


def test_bound_generation_bool_rejected():
    assert any("bound_generation" in i for i in route_capability.validate_capability(_cap(bound_generation=True)))


def test_expires_on_shape_enforced():
    assert any("expires_on" in i for i in route_capability.validate_capability(_cap(expires_on={"event": "never"})))


def test_state_enum_enforced():
    assert any("state" in i for i in route_capability.validate_capability(_cap(state="live")))


def test_hash_deterministic_and_key_order_free():
    a = _cap(); b = dict(reversed(list(_cap().items())))
    assert route_capability.capability_hash(a) == route_capability.capability_hash(b)
    assert len(route_capability.capability_hash(a)) == 64


def test_hash_refuses_invalid():
    with pytest.raises(ValueError):
        route_capability.capability_hash(_cap(schema="x"))


def test_validation_does_not_mutate_input():
    obj = _cap(); snap = copy.deepcopy(obj)
    route_capability.validate_capability(obj)
    assert obj == snap


# --- capability-receipt/v1 (evidence-bearing, non-vacuous) -------------------

def _receipt(**overrides) -> dict:
    """A valid receipt (commit evidence) for crafting rejection cases."""
    r = route_capability.build_receipt(
        _cap(), result="ok", command="git push",
        output="To origin/main", commit="deadbee",
    )
    r.update(overrides)
    return r


def test_valid_receipt_with_commit():
    assert route_capability.validate_receipt(_receipt()) == []


def test_valid_receipt_with_logs_ref():
    r = route_capability.build_receipt(
        _cap(), result="failed", command="git push",
        output="rejected: non-fast-forward", logs_ref="logs/2026-07-12/push.txt",
    )
    assert route_capability.validate_receipt(r) == []


def test_receipt_rejected_without_commit_or_logs():
    r = route_capability.build_receipt(_cap(), result="ok", command="git push", output="done")
    r.pop("commit", None)   # ensure neither evidence field is present
    r.pop("logs_ref", None)
    assert any("evidence" in i for i in route_capability.validate_receipt(r))


def test_build_receipt_binds_capability_id_and_hash():
    cap = _cap()
    r = route_capability.build_receipt(cap, result="ok", command="git push",
                                       output="To origin/main", commit="deadbee")
    assert route_capability.validate_receipt(r) == []
    assert r["capability_id"] == cap["capability_id"]
    assert r["capability_hash"] == route_capability.capability_hash(cap)


def test_build_receipt_copies_subject_and_target():
    cap = _cap()
    r = route_capability.build_receipt(cap, result="ok", command="git push",
                                       output="ok", commit="deadbee")
    assert r["subject"] == cap["subject"]
    assert r["target"] == cap["target"]


def test_build_receipt_rejects_invalid_capability():
    with pytest.raises(route_capability.CapabilityError):
        route_capability.build_receipt(_cap(schema="x"), result="ok",
                                       command="git push", output="done", commit="deadbee")


def test_receipt_unsupported_schema_rejected():
    issues = route_capability.validate_receipt(_receipt(schema="governance.capability-receipt/v2"))
    assert issues and "unsupported schema" in issues[0]


def test_receipt_non_dict_rejected():
    assert route_capability.validate_receipt("not a receipt") == \
        ["receipt object must be a JSON object"]


def test_receipt_unknown_field_rejected():
    assert any("unknown" in i for i in route_capability.validate_receipt(_receipt(surprise=1)))


def test_receipt_missing_required_field_rejected():
    r = _receipt(); del r["target"]
    assert any("missing required" in i for i in route_capability.validate_receipt(r))


def test_receipt_empty_command_rejected():
    assert any("command" in i for i in route_capability.validate_receipt(_receipt(command="")))


def test_receipt_empty_output_rejected():
    assert any("output" in i for i in route_capability.validate_receipt(_receipt(output="   ")))


def test_receipt_result_enum_enforced():
    assert any("result" in i for i in route_capability.validate_receipt(_receipt(result="maybe")))


def test_receipt_capability_hash_must_be_64_hex():
    assert any("capability_hash" in i for i in route_capability.validate_receipt(_receipt(capability_hash="short")))
    assert any("capability_hash" in i for i in route_capability.validate_receipt(_receipt(capability_hash="Z" * 64)))


def test_receipt_bad_commit_format_rejected():
    # 'nothex' is not a hex SHA → commit-format issue AND (since no logs_ref) vacuous.
    issues = route_capability.validate_receipt(_receipt(commit="nothex"))
    assert any("commit" in i for i in issues)


def test_receipt_bad_logs_ref_rejected():
    r = route_capability.build_receipt(_cap(), result="ok", command="git push",
                                       output="ok", logs_ref="var/tmp/push.txt")
    issues = route_capability.validate_receipt(r)
    assert any("logs_ref" in i for i in issues)


def test_receipt_newline_in_string_rejected():
    issues = route_capability.validate_receipt(_receipt(output="done\n- executor: operator"))
    assert any("control character" in i for i in issues)


def test_receipt_validation_does_not_mutate_input():
    r = _receipt(); snap = copy.deepcopy(r)
    route_capability.validate_receipt(r)
    assert r == snap
