"""Unit tests for scripts/chief_emit.py `_build_revoke` — the chief-approver
authority boundary: a chief may revoke ONLY a fact its own seat previously
signed onto the bus (`PermissionError` when the target id resolves to no event
or to another seat's event), and a permitted revoke yields a well-formed
`attestation_revoked` event inheriting the TARGET's candidate_id/subject_sha.

Hermetic: runs within a temporary Git repository generated via tmp_path,
independent of any live repo configuration — fixture porcelain git is scrubbed
of global/system config and GIT_INDEX_FILE (see _git), and the keystore is
redirected via THREEWAY_KEYSTORE (mirrors test_threeway_activation_scripts.py).
"""
from __future__ import annotations

import argparse
import os
import subprocess

import pytest

import chief_emit
from threeway import keys, keys_bootstrap
from threeway.envelope import Event, well_formed
from threeway.refstore import RefEventStore


def _git(repo_dir, *args):
    """Porcelain git scrubbed of ambient state: GIT_INDEX_FILE (the per-seat
    index-corruption vector threeway/gitcas.py strips on every call) and
    global/system config (a developer's commit.gpgsign=true would break the
    fixture's commits)."""
    env = {k: v for k, v in os.environ.items() if k != "GIT_INDEX_FILE"}
    env["GIT_CONFIG_GLOBAL"] = os.devnull
    env["GIT_CONFIG_SYSTEM"] = os.devnull
    return subprocess.run(
        ["git", "-C", str(repo_dir), *args],
        check=True, capture_output=True, text=True, env=env,
    ).stdout.strip()


def _ev(kind, *, signer, ev_id, candidate_id=None, subject_sha=None,
        payload=None) -> Event:
    """A minimal Event with this suite's boilerplate defaulted (the _ev()
    builder convention of test_threeway_activation_scripts.py)."""
    return Event(
        id=ev_id, seq=0, bus_id="prod", schema_version="threeway/1", kind=kind,
        sender=signer.split(":", 1)[0], recipient="all", signer=signer,
        payload={} if payload is None else payload,
        candidate_id=candidate_id, subject_sha=subject_sha,
    )


def _chief_approval(ev_id="human_approval-chief-A:c1", signer="chief:human:cli"):
    """A prior chief fact of the shape _build_human_approval emits."""
    approver = signer.split(":", 1)[0]
    return _ev(
        "human_approval", signer=signer, ev_id=ev_id, candidate_id="A:c1",
        subject_sha="integ-sha-1",
        payload={"approver_identity": approver, "integration_sha": "integ-sha-1",
                 "decision": "approve"})


def _args(temp_git_repo, *, approver, revokes_event_id):
    """Exactly the argparse surface _build_revoke reads (chief_emit.main
    defaults: bus prod; remote=None => local ref store)."""
    return argparse.Namespace(
        approver=approver, revokes_event_id=revokes_event_id,
        repo_dir=str(temp_git_repo["repo_dir"]),
        registry_dir=str(temp_git_repo["registry_dir"]),
        remote=None, bus_id="prod",
    )


@pytest.fixture
def temp_git_repo(tmp_path, monkeypatch):
    repo_dir = tmp_path / "repo"
    repo_dir.mkdir()
    _git(repo_dir, "init", "-b", "main")
    _git(repo_dir, "config", "user.email", "test@example.com")
    _git(repo_dir, "config", "user.name", "Test")

    registry_dir = repo_dir / "coordination" / "threeway" / "keys"
    registry_dir.mkdir(parents=True)
    keystore_dir = tmp_path / "keystore"
    keystore_dir.mkdir()
    # chief2 exists to prove the seat check is exact, not a prefix match.
    keys_bootstrap.main([
        "--registry", str(registry_dir), "--keystore", str(keystore_dir),
        "--seats", "chief", "chief2", "operator",
    ])
    monkeypatch.setenv("THREEWAY_KEYSTORE", str(keystore_dir))
    return {"repo_dir": repo_dir, "registry_dir": registry_dir}


def test_revoke_nonexistent_event_id_denied(temp_git_repo):
    # Populated bus (the chief HAS a prior fact) but the target id names no
    # event -> denied. Target resolution failure IS an authority failure.
    store = RefEventStore(temp_git_repo["repo_dir"])
    store.append(_chief_approval(), keys.load_private("chief"))
    with pytest.raises(PermissionError,
                       match="chief may only revoke its own prior fact"):
        chief_emit._build_revoke(
            _args(temp_git_repo, approver="chief",
                  revokes_event_id="no-such-event"))


def test_revoke_other_seats_event_denied(temp_git_repo):
    # The operator's attestation is on the bus; the chief may not revoke it.
    store = RefEventStore(temp_git_repo["repo_dir"])
    store.append(
        _ev("attestation", signer="operator:claude:s1", ev_id="att-1",
            candidate_id="A:c1", subject_sha="branch-sha-1",
            payload={"kind": "preliminary", "verdict": "GO"}),
        keys.load_private("operator"))
    with pytest.raises(PermissionError,
                       match="chief may only revoke its own prior fact"):
        chief_emit._build_revoke(
            _args(temp_git_repo, approver="chief", revokes_event_id="att-1"))


def test_revoke_prefix_seat_near_miss_denied(temp_git_repo):
    # chief2's fact is NOT chief's own: signer_seat compares the exact first
    # ':'-field of the signer, never a string prefix.
    store = RefEventStore(temp_git_repo["repo_dir"])
    store.append(_chief_approval(ev_id="ha-chief2", signer="chief2:human:cli"),
                 keys.load_private("chief2"))
    with pytest.raises(PermissionError,
                       match="chief may only revoke its own prior fact"):
        chief_emit._build_revoke(
            _args(temp_git_repo, approver="chief", revokes_event_id="ha-chief2"))


def test_revoke_own_prior_fact_builds_well_formed_revoke(temp_git_repo):
    store = RefEventStore(temp_git_repo["repo_dir"])
    chief_priv = keys.load_private("chief")
    store.append(_chief_approval(), chief_priv)

    ev = chief_emit._build_revoke(
        _args(temp_git_repo, approver="chief",
              revokes_event_id="human_approval-chief-A:c1"))

    assert ev.kind == "attestation_revoked"
    assert ev.id == "attestation_revoked-chief-human_approval-chief-A:c1"
    assert ev.sender == "chief"
    assert ev.recipient == "all"
    assert ev.signer == "chief:human:cli"
    assert ev.payload == {}
    assert ev.revokes_event_id == "human_approval-chief-A:c1"
    # candidate_id/subject_sha are inherited from the TARGET fact, not caller input.
    assert ev.candidate_id == "A:c1"
    assert ev.subject_sha == "integ-sha-1"
    assert ev.bus_id == "prod"
    assert ev.schema_version == "threeway/1"
    assert well_formed(ev)
    # And the built event is genuinely bus-appendable under the chief's own key
    # (main()'s next step): the store allocates the next seq and signs cleanly.
    appended = store.append(ev, chief_priv)
    assert appended.seq == 2


def test_main_denied_revoke_exits_2_and_emits_nothing(temp_git_repo, capsys):
    # CLI wiring of the gate: PermissionError -> exit 2, message on stderr,
    # and the denied revoke never reaches the bus.
    store = RefEventStore(temp_git_repo["repo_dir"])
    store.append(
        _ev("attestation", signer="operator:claude:s1", ev_id="att-1",
            candidate_id="A:c1", subject_sha="branch-sha-1",
            payload={"kind": "preliminary", "verdict": "GO"}),
        keys.load_private("operator"))
    rc = chief_emit.main([
        "chief", "attestation_revoked", "--candidate-id", "A:c1",
        "--revokes-event-id", "att-1",
        "--registry-dir", str(temp_git_repo["registry_dir"]),
        "--repo-dir", str(temp_git_repo["repo_dir"]),
        "--remote", "none", "--bus-id", "prod",
    ])
    assert rc == 2
    assert "chief may only revoke its own prior fact" in capsys.readouterr().err
    assert [e.id for e in store.all_events()] == ["att-1"]
