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


# --- atomic one-time consumption + supersession-revocation binding (Task 4) ---

import route_lineage


def _lr(route_id, generation):
    return route_lineage.LineageRoute(route_id, route_lineage.RouteLineage(generation, None, None))


def _evidence():
    return {"result": "ok", "command": "git push", "output": "To origin/main", "commit": "deadbee"}


def test_consume_writes_receipt_and_succeeds(tmp_path):
    res = route_capability.consume(_cap(), _evidence(), store_dir=tmp_path)
    assert res.ok and res.receipt_path is not None
    from pathlib import Path
    assert Path(res.receipt_path).exists()


def test_second_consume_fails_already_consumed(tmp_path):
    first = route_capability.consume(_cap(), _evidence(), store_dir=tmp_path)
    assert first.ok
    second = route_capability.consume(_cap(), _evidence(), store_dir=tmp_path)
    assert not second.ok and second.reason == "already_consumed"


def test_consume_refuses_invalid_capability(tmp_path):
    res = route_capability.consume(_cap(state="live"), _evidence(), store_dir=tmp_path)
    assert not res.ok and "invalid capability" in res.reason


def test_consume_refuses_vacuous_evidence(tmp_path):
    ev = {"result": "ok", "command": "git push", "output": "done"}  # no commit/logs_ref
    res = route_capability.consume(_cap(), ev, store_dir=tmp_path)
    assert not res.ok and "evidence" in res.reason
    # and NO receipt file was written (fail-closed before O_EXCL)
    assert list(tmp_path.iterdir()) == []


def test_capability_current_only_at_bound_generation():
    cap = _cap(bound_route_id="r5", bound_generation=5)
    assert route_capability.capability_is_current(cap, _lr("r5", 5))
    # superseded: newer generation is authoritative -> stale
    assert not route_capability.capability_is_current(cap, _lr("r6", 6))
    # different route entirely -> stale
    assert not route_capability.capability_is_current(cap, _lr("other", 5))


def test_capability_not_current_when_generation_none():
    # Defense-in-depth: a None generation on EITHER side means NOT current, so an
    # invalid capability (bound_generation=None) can never ride a legacy
    # no-generation route into "current" and inherit authority it never had.
    cap_none = _cap(bound_route_id="r7", bound_generation=None)
    assert not route_capability.capability_is_current(cap_none, _lr("r7", None))
    # even a well-formed cap generation is not current against a legacy route
    # whose generation is None (route side None).
    cap_ok = _cap(bound_route_id="r7", bound_generation=5)
    assert not route_capability.capability_is_current(cap_ok, _lr("r7", None))


def test_consume_write_failure_does_not_brick_capability(tmp_path, monkeypatch):
    """A failed durability sync must leave NO final receipt — the capability is
    not bricked and a legitimate retry still succeeds.

    Forces an OSError at the durability barrier (os.fsync) that runs AFTER the
    complete receipt is written to a temp file but BEFORE it is atomically linked
    into place. The fix's contract: the canonical receipt path never appears with
    partial/empty content, the temp scratch is always cleaned, and the grant is
    not permanently consumed by a write that never landed.
    """
    from pathlib import Path
    cap = _cap()
    final = tmp_path / f"{cap['capability_id']}.receipt.json"

    def _raise(*_a, **_k):
        raise OSError("simulated durability-sync failure (ENOSPC/EIO)")

    monkeypatch.setattr(route_capability.os, "fsync", _raise)

    # (a) the durability failure must surface — consume must NOT report success.
    result = None
    try:
        result = route_capability.consume(cap, _evidence(), store_dir=tmp_path)
    except OSError:
        pass  # surfaced as an exception — acceptable, and NOT ok=True
    assert result is None or result.ok is False, "a failed sync must not report ok=True"

    # (b) NO final receipt (empty or partial) is left at the canonical path, and
    #     no stray temp scratch remains — nothing for a retry to trip over.
    assert not final.exists(), "final receipt must never appear with partial/no content"
    assert list(tmp_path.iterdir()) == [], "temp scratch must be cleaned up on failure"

    # (c) with durability restored, a legitimate retry SUCCEEDS — proving the
    #     earlier failure did not permanently brick the capability.
    monkeypatch.undo()
    retry = route_capability.consume(cap, _evidence(), store_dir=tmp_path)
    assert retry.ok and retry.reason == "consumed"
    assert final.exists()


# --- consume enforces the capability's allowed_command_class (F2) -------------
#
# A capability names ONE allowed command literal (allowed_command_class). consume
# must refuse evidence whose executed command is not that literal (exact match or
# a `<literal> …` prefix), fail-closed BEFORE any receipt is written — otherwise a
# grant for `git push` could be spent recording a `git tag` that actually ran.

def test_consume_refuses_command_class_mismatch(tmp_path):
    # cap allows "git push"; evidence command is "git tag unexpected" -> mismatch.
    ev = {"result": "ok", "command": "git tag unexpected", "output": "created tag", "commit": "deadbee"}
    res = route_capability.consume(_cap(), ev, store_dir=tmp_path)
    assert not res.ok
    assert "command_class_mismatch" in res.reason
    # fail-closed BEFORE any write — the store stays empty.
    assert list(tmp_path.iterdir()) == []


def test_consume_allows_command_class_prefix(tmp_path):
    # "git push origin main" is a prefix-extension of allowed "git push" -> allowed.
    ev = {"result": "ok", "command": "git push origin main", "output": "To origin/main", "commit": "deadbee"}
    res = route_capability.consume(_cap(), ev, store_dir=tmp_path)
    assert res.ok and res.reason == "consumed"


# --- consume refuses shell-control operators in the evidence command (F2 residual)
#
# The prefix match `cmd.startswith(allowed + " ")` alone lets a COMPOUND command
# through: "git push origin main && git tag unexpected" starts with "git push "
# but chains an UNAUTHORIZED second command. A capability authorizes exactly ONE
# simple command matching its class — never a shell composition. consume must
# reject any evidence command containing a control/chaining/substitution/
# redirection metacharacter (; & | ` $ < > ( )), fail-closed BEFORE any write.

def test_consume_refuses_compound_command(tmp_path):
    # cap allows "git push"; the `&&` chains an unauthorized `git tag` -> refused.
    ev = {"result": "ok", "command": "git push origin main && git tag unexpected",
          "output": "To origin/main", "commit": "deadbee"}
    res = route_capability.consume(_cap(), ev, store_dir=tmp_path)
    assert not res.ok
    assert "command_class_mismatch" in res.reason
    assert list(tmp_path.iterdir()) == []  # fail-closed BEFORE any write


def test_consume_refuses_command_substitution(tmp_path):
    # `$(...)` command substitution smuggles an unauthorized command -> refused.
    ev = {"result": "ok", "command": "git push $(rm -rf /tmp/x)",
          "output": "To origin/main", "commit": "deadbee"}
    res = route_capability.consume(_cap(), ev, store_dir=tmp_path)
    assert not res.ok
    assert "command_class_mismatch" in res.reason
    assert list(tmp_path.iterdir()) == []


def test_consume_refuses_piped_command(tmp_path):
    # a pipe redirects output through an unauthorized second command -> refused.
    ev = {"result": "ok", "command": "git push origin main | tee log",
          "output": "To origin/main", "commit": "deadbee"}
    res = route_capability.consume(_cap(), ev, store_dir=tmp_path)
    assert not res.ok
    assert "command_class_mismatch" in res.reason
    assert list(tmp_path.iterdir()) == []


def test_consume_allows_plain_args_with_flags(tmp_path):
    # a single simple command with flags (no shell metacharacters) still passes.
    ev = {"result": "ok", "command": "git push origin main --force-with-lease",
          "output": "To origin/main", "commit": "deadbee"}
    res = route_capability.consume(_cap(), ev, store_dir=tmp_path)
    assert res.ok and res.reason == "consumed"


# --- consume enforces revocation-on-supersession at the enforcement point (F3) -
#
# capability_is_current is correct but nothing called it at consume time. With an
# authoritative route supplied, a capability bound to a superseded generation is
# refused fail-closed (no receipt); when the capability is current it consumes.

def test_consume_refuses_stale_capability(tmp_path):
    cap = _cap(bound_route_id="r6", bound_generation=3)
    authoritative = _lr("r6", 6)  # a newer generation is authoritative -> stale
    res = route_capability.consume(cap, _evidence(), store_dir=tmp_path, authoritative=authoritative)
    assert not res.ok
    assert "stale_capability" in res.reason
    assert list(tmp_path.iterdir()) == []  # no receipt on a stale grant


def test_consume_allows_current_capability(tmp_path):
    cap = _cap(bound_route_id="r5", bound_generation=5)
    authoritative = _lr("r5", 5)  # bound generation == authoritative generation
    res = route_capability.consume(cap, _evidence(), store_dir=tmp_path, authoritative=authoritative)
    assert res.ok and res.reason == "consumed"


def test_consume_authoritative_none_skips_currency(tmp_path):
    # Backward-compatible default: authoritative=None does NOT enforce currency,
    # so an otherwise-valid capability consumes even though it is not checked.
    res = route_capability.consume(_cap(), _evidence(), store_dir=tmp_path, authoritative=None)
    assert res.ok and res.reason == "consumed"


# --- CLI main() — the mechanical enforcement point (Task 5) -------------------
#
# main() is the "script that accepts a token at execution time and refuses
# replay" — the general form of the operator2 BLOCKER. Exit codes are the
# contract: validate 0/1; consume 0 (first) / 3 (already_consumed) / 2 (any
# other refusal: invalid capability or vacuous evidence).

import json


def _write_cap(tmp_path, **overrides):
    path = tmp_path / "cap.json"
    path.write_text(json.dumps(_cap(**overrides)))
    return str(path)


def _write_route(tmp_path, route_id, generation):
    """Write a coordinator-to-all route .md carrying a lineage generation header,
    under the mailbox layout route_lineage.load_routes globs (…/sent/*)."""
    sent = tmp_path / "coordination" / "mailbox" / "sent"
    sent.mkdir(parents=True, exist_ok=True)
    (sent / f"{route_id}.md").write_text(
        f"# {route_id}\n\nRoute generation: {generation}\n"
    )
    return route_id


def test_cli_validate_good_capability_exit_0(tmp_path, capsys):
    good = _write_cap(tmp_path)
    assert route_capability.main(["validate", "--capability", good]) == 0
    assert "capability valid" in capsys.readouterr().out


def test_cli_validate_bad_capability_exit_1(tmp_path, capsys):
    bad = _write_cap(tmp_path, state="live")  # invalid lifecycle state
    assert route_capability.main(["validate", "--capability", bad]) == 1
    assert "state must be one of" in capsys.readouterr().out


def test_cli_validate_nonexistent_path_exit_1(tmp_path, capsys):
    missing = str(tmp_path / "does-not-exist.json")
    assert route_capability.main(["validate", "--capability", missing]) == 1
    assert capsys.readouterr().out.strip() != ""


def test_cli_validate_unparseable_file_exit_1(tmp_path, capsys):
    bad = tmp_path / "bad.json"
    bad.write_text("{ not valid json")
    assert route_capability.main(["validate", "--capability", str(bad)]) == 1
    assert capsys.readouterr().out.strip() != ""


def test_cli_consume_first_exit_0_then_replay_exit_3(tmp_path, capsys):
    good = _write_cap(tmp_path)
    store = tmp_path / "store"
    argv = [
        "consume", "--capability", good, "--store", str(store),
        "--result", "ok", "--command", "git push",
        "--output", "To origin/main", "--commit", "deadbee",
    ]
    assert route_capability.main(argv) == 0
    assert "consumed:" in capsys.readouterr().out
    # a SECOND identical consume is the replay — refused with already_consumed.
    assert route_capability.main(argv) == 3
    assert "already_consumed" in capsys.readouterr().out


def test_cli_consume_vacuous_evidence_exit_2(tmp_path, capsys):
    good = _write_cap(tmp_path)
    store = tmp_path / "store"
    # no --commit and no --logs-ref -> vacuous evidence, refused fail-closed.
    argv = [
        "consume", "--capability", good, "--store", str(store),
        "--result", "ok", "--command", "git push", "--output", "done",
    ]
    assert route_capability.main(argv) == 2
    assert "evidence" in capsys.readouterr().out
    assert not store.exists() or list(store.iterdir()) == []


def test_cli_consume_invalid_capability_exit_2(tmp_path, capsys):
    bad = _write_cap(tmp_path, state="live")
    store = tmp_path / "store"
    argv = [
        "consume", "--capability", bad, "--store", str(store),
        "--result", "ok", "--command", "git push",
        "--output", "To origin/main", "--commit", "deadbee",
    ]
    assert route_capability.main(argv) == 2
    assert "invalid capability" in capsys.readouterr().out


def test_cli_consume_with_logs_ref_exit_0(tmp_path, capsys):
    good = _write_cap(tmp_path)
    store = tmp_path / "store"
    # command matches allowed_command_class "git push"; anchored by a logs/ ref
    # (no commit) — the test exercises the logs-ref evidence path to exit 0.
    argv = [
        "consume", "--capability", good, "--store", str(store),
        "--result", "ok", "--command", "git push origin main",
        "--output", "To origin/main", "--logs-ref", "logs/run-2026-07-12.txt",
    ]
    assert route_capability.main(argv) == 0
    assert "consumed:" in capsys.readouterr().out


# --- CLI: command-class + currency enforcement (F2/F3) exit codes -------------
#
# Exit-code contract additions: command_class_mismatch -> 2; a stale capability
# (or a route-root with no lineage generation to check against) -> 4; a current
# capability with --route-root -> 0.

def test_cli_consume_command_class_mismatch_exit_2(tmp_path, capsys):
    good = _write_cap(tmp_path)  # allowed_command_class "git push"
    store = tmp_path / "store"
    argv = [
        "consume", "--capability", good, "--store", str(store),
        "--result", "ok", "--command", "git tag unexpected",
        "--output", "created tag", "--commit", "deadbee",
    ]
    assert route_capability.main(argv) == 2
    assert "command_class_mismatch" in capsys.readouterr().out
    assert not store.exists() or list(store.iterdir()) == []


def test_cli_consume_compound_command_exit_2(tmp_path, capsys):
    good = _write_cap(tmp_path)  # allowed_command_class "git push"
    store = tmp_path / "store"
    # the `&&` chains an unauthorized second command -> command_class_mismatch -> 2.
    argv = [
        "consume", "--capability", good, "--store", str(store),
        "--result", "ok", "--command", "git push origin main && git tag x",
        "--output", "To origin/main", "--commit", "deadbee",
    ]
    assert route_capability.main(argv) == 2
    assert "command_class_mismatch" in capsys.readouterr().out
    assert not store.exists() or list(store.iterdir()) == []


def test_cli_consume_refuses_stale_with_route_root(tmp_path, capsys):
    route_id = "2026-07-12T20-00-00Z-coordinator-to-all-coordination"
    _write_route(tmp_path, route_id, 6)  # authoritative generation 6
    store = tmp_path / "store"
    # capability bound to generation 3 of that route -> stale -> exit 4.
    cap_path = _write_cap(tmp_path, bound_route_id=route_id, bound_generation=3)
    argv = [
        "consume", "--capability", cap_path, "--store", str(store),
        "--result", "ok", "--command", "git push",
        "--output", "To origin/main", "--commit", "deadbee",
        "--route-root", str(tmp_path),
    ]
    assert route_capability.main(argv) == 4
    assert "stale_capability" in capsys.readouterr().out
    assert not store.exists() or list(store.iterdir()) == []
    # rebind the capability to the authoritative generation 6 -> exit 0.
    _write_cap(tmp_path, bound_route_id=route_id, bound_generation=6)
    assert route_capability.main(argv) == 0
    assert "consumed:" in capsys.readouterr().out


def test_cli_consume_route_root_no_lineage_exit_4(tmp_path, capsys):
    # --route-root with no coordinator routes: no lineage generation to establish
    # supersession, so the requested currency check fails closed with exit 4.
    good = _write_cap(tmp_path)
    store = tmp_path / "store"
    empty_root = tmp_path / "empty"
    empty_root.mkdir()
    argv = [
        "consume", "--capability", good, "--store", str(store),
        "--result", "ok", "--command", "git push",
        "--output", "To origin/main", "--commit", "deadbee",
        "--route-root", str(empty_root),
    ]
    assert route_capability.main(argv) == 4
    assert capsys.readouterr().out.strip() != ""
    assert not store.exists() or list(store.iterdir()) == []
