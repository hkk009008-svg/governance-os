"""Unit tests for the three-way activation and unread scripts:
- scripts/agy_observer.py
- scripts/sign_ci_result.py
- scripts/run_merge_gate.py
- scripts/bus_unread.py

Hermetic: runs within a temporary Git repository generated via tmp_path,
independent of any live repo configuration — fixture porcelain git is scrubbed
of global/system config and GIT_INDEX_FILE (see _git), and the keystore is
redirected via THREEWAY_KEYSTORE.
"""
from __future__ import annotations

import os
import subprocess

import pytest

import agy_observer
import bus_unread
import run_merge_gate
import sign_ci_result
from threeway import keys, keys_bootstrap
from threeway.envelope import Event
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


def _ev(kind, *, signer, payload=None, candidate_id=None, brief_id="b1",
        brief_version=1, subject_sha=None, recipient="all", ev_id=None,
        supersedes_event_id=None) -> Event:
    """A minimal Event with this suite's boilerplate defaulted (the _ev()
    builder convention of test_reducer.py). id derives from kind/signer/
    candidate_id unless a test must reference it explicitly."""
    return Event(
        id=ev_id if ev_id is not None else f"{kind}-{signer}-{candidate_id}",
        seq=0,
        bus_id="prod",
        schema_version="threeway/1",
        kind=kind,
        sender=signer.split(":", 1)[0],
        recipient=recipient,
        signer=signer,
        payload={} if payload is None else payload,
        brief_id=brief_id,
        brief_version=brief_version,
        candidate_id=candidate_id,
        subject_sha=subject_sha,
        supersedes_event_id=supersedes_event_id,
    )


def _cand_payload(temp_git_repo, integration_sha):
    """The canonical candidate payload against the fixture's two commits."""
    return {
        "pair": "A",
        "staging_base_sha": temp_git_repo["base_sha"],
        "branch_sha": temp_git_repo["branch_sha"],
        "integration_sha": integration_sha,
        "risk_tier_claimed": "T1",
    }


@pytest.fixture
def temp_git_repo(tmp_path, monkeypatch):
    repo_dir = tmp_path / "repo"
    repo_dir.mkdir()

    _git(repo_dir, "init", "-b", "main")
    _git(repo_dir, "config", "user.email", "test@example.com")
    _git(repo_dir, "config", "user.name", "Test")

    # Setup the registry and keystore directories
    registry_dir = repo_dir / "coordination" / "threeway" / "keys"
    registry_dir.mkdir(parents=True)
    keystore_dir = tmp_path / "keystore"
    keystore_dir.mkdir()

    # Bootstrap the seat keys
    seats = [
        "director",
        "director2",
        "operator",
        "operator2",
        "coordinator",
        "coordinator2",
        "ci",
        "overseer",
        "merge-gate",
    ]
    keys_bootstrap.main(
        [
            "--registry",
            str(registry_dir),
            "--keystore",
            str(keystore_dir),
            "--seats",
        ]
        + seats
    )

    monkeypatch.setenv("THREEWAY_KEYSTORE", str(keystore_dir))

    # Create dummy commits to use in the tests
    file1 = repo_dir / "file1.txt"
    file1.write_text("base content\n", encoding="utf-8")
    _git(repo_dir, "add", "file1.txt")
    _git(repo_dir, "commit", "-m", "initial commit")
    base_sha = _git(repo_dir, "rev-parse", "HEAD")

    # Feature branch commit
    _git(repo_dir, "checkout", "-b", "feature")
    file1.write_text("base content\nfeature content\n", encoding="utf-8")
    _git(repo_dir, "add", "file1.txt")
    _git(repo_dir, "commit", "-m", "feature commit")
    branch_sha = _git(repo_dir, "rev-parse", "HEAD")

    # Switch back to main
    _git(repo_dir, "checkout", "main")

    return {
        "repo_dir": repo_dir,
        "registry_dir": registry_dir,
        "keystore_dir": keystore_dir,
        "base_sha": base_sha,
        "branch_sha": branch_sha,
    }


def test_agy_observer_summarize(temp_git_repo):
    repo_dir = temp_git_repo["repo_dir"]
    store = RefEventStore(repo_dir)

    # 1. Empty bus
    res = agy_observer.summarize(store)
    assert res["total_events"] == 0
    assert res["briefs"] == {}
    assert res["candidates"] == {}
    assert res["ci_results"] == {}

    # 2. One event of each summarized kind
    overseer_priv = keys.load_private("overseer")
    coord_priv = keys.load_private("coordinator")
    store.append(
        _ev("brief", signer="overseer:mech:s1", ev_id="brief-1",
            payload={"brief_id": "b1", "assigned_tier": "T1",
                     "allowed_paths": ["file1.txt"]}),
        overseer_priv)
    store.append(
        _ev("candidate", signer="coordinator:claude:s1",
            candidate_id="A:c1", subject_sha="fake_integ_sha",
            payload=_cand_payload(temp_git_repo, "fake_integ_sha")),
        coord_priv)
    store.append(
        _ev("attestation", signer="operator:claude:s1",
            candidate_id="A:c1", subject_sha=temp_git_repo["branch_sha"],
            payload={"kind": "preliminary", "verdict": "GO"}),
        keys.load_private("operator"))
    store.append(
        _ev("release_requested", signer="coordinator:claude:s1",
            candidate_id="A:c1", payload={"candidate_id": "A:c1"}),
        coord_priv)
    store.append(
        _ev("release_order", signer="overseer:mech:s1",
            candidate_id="A:c1", payload={"candidate_id": "A:c1"}),
        overseer_priv)
    store.append(
        _ev("ci_result", signer="ci:mech:s1",
            subject_sha="fake_integ_sha", payload={"result": "PASS"}),
        keys.load_private("ci"))

    # Verify parsing and count state mapping
    res = agy_observer.summarize(store)
    assert res["total_events"] == 6
    assert "b1" in res["briefs"]
    assert "A:c1" in res["candidates"]
    c = res["candidates"]["A:c1"]
    assert c["integration_sha"] == "fake_integ_sha"
    assert c["attestations"] == 1
    assert c["release_requested"] is True
    assert c["release_order"] is True
    assert res["ci_results"].get("fake_integ_sha") == "PASS"

    # 3. A re-emitted candidate updates integration_sha/signer in place,
    #    preserving accumulated attestation/release state.
    store.append(
        _ev("candidate", signer="coordinator:claude:s2",
            candidate_id="A:c1", subject_sha="fake_integ_sha_v2",
            payload=_cand_payload(temp_git_repo, "fake_integ_sha_v2")),
        coord_priv)
    res = agy_observer.summarize(store)
    assert res["candidates"]["A:c1"]["integration_sha"] == "fake_integ_sha_v2"
    assert res["candidates"]["A:c1"]["signer"] == "coordinator:claude:s2"
    assert res["candidates"]["A:c1"]["attestations"] == 1  # preserved

    # 4. Brief supersession pops the brief
    store.append(
        _ev("brief_superseded", signer="overseer:mech:s1",
            payload={"supersedes_event_id": "brief-1"},
            supersedes_event_id="brief-1"),
        overseer_priv)
    res = agy_observer.summarize(store)
    assert "b1" not in res["briefs"]


def test_sign_ci_result_script(temp_git_repo):
    repo_dir = temp_git_repo["repo_dir"]
    store = RefEventStore(repo_dir)

    # Setup candidate on bus
    coord_priv = keys.load_private("coordinator")
    store.append(
        _ev("candidate", signer="coordinator:claude:s1",
            candidate_id="A:c1", subject_sha="some_integ_sha",
            payload=_cand_payload(temp_git_repo, "some_integ_sha")),
        coord_priv)

    # Emit CI result
    ci_priv = keys.load_private("ci")
    ev = sign_ci_result.emit_ci_result(store, "some_integ_sha", "PASS", ci_priv)
    assert ev.kind == "ci_result"
    assert ev.subject_sha == "some_integ_sha"
    assert ev.payload["result"] == "PASS"
    assert ev.candidate_id == "A:c1"

    # Handle unknown integration SHA gracefully (candidate_id = None)
    ev2 = sign_ci_result.emit_ci_result(store, "unknown_sha", "FAIL", ci_priv)
    assert ev2.candidate_id is None


def test_run_merge_gate_script(temp_git_repo):
    repo_dir = temp_git_repo["repo_dir"]
    registry_dir = temp_git_repo["registry_dir"]
    store = RefEventStore(repo_dir)

    # Empty store has no candidate IDs
    assert run_merge_gate.collect_candidate_ids(store) == set()

    # Setup candidate and release requested events
    coord_priv = keys.load_private("coordinator")
    store.append(
        _ev("candidate", signer="coordinator:claude:s1",
            candidate_id="A:c1", subject_sha="some_integ_sha",
            payload=_cand_payload(temp_git_repo, "some_integ_sha")),
        coord_priv)
    store.append(
        _ev("release_requested", signer="coordinator:claude:s1",
            candidate_id="A:c1", payload={"candidate_id": "A:c1"}),
        coord_priv)

    assert run_merge_gate.collect_candidate_ids(store) == {"A:c1"}

    # Poll once: PENDING because no overseer `assignment` fact is on the bus —
    # the gate bails with "no candidate from executing coordinator" before any
    # approval clause is evaluated (threeway/predicate.py).
    res = run_merge_gate.poll_once(
        store,
        repo=repo_dir,
        registry_dir=registry_dir,
        bus_id="prod",
        main_ref="refs/threeway/test-main",
    )
    assert len(res) == 1
    cid, gate_res = res[0]
    assert cid == "A:c1"
    assert gate_res.outcome == "PENDING"
    # Pin the reason: a broken/empty registry ALSO yields PENDING (but with
    # "no candidate fact yet" after every event drops as unknown-signer), so
    # outcome alone cannot prove the signature/registry plumbing worked.
    assert gate_res.reason == "no candidate from executing coordinator"


def test_bus_unread_script(temp_git_repo):
    repo_dir = temp_git_repo["repo_dir"]
    store = RefEventStore(repo_dir)

    # Test migrated cursor classification
    assert bus_unread.is_migrated_cursor("42") is True
    assert bus_unread.is_migrated_cursor(" 123 ") is True
    assert bus_unread.is_migrated_cursor("2026-05-28T20:38:34Z") is False
    assert bus_unread.is_migrated_cursor("not-a-digit") is False
    assert bus_unread.is_migrated_cursor("") is False

    # Initialize live ref cursor
    store.advance_cursor("operator", 0)

    # Verify no unread events initially
    assert bus_unread.bus_unread_count(repo_dir, "operator") == 0

    # Append event addressed to operator
    coord_priv = keys.load_private("coordinator")
    store.append(
        _ev("candidate", signer="coordinator:claude:s1",
            candidate_id="A:c1", recipient="operator", ev_id="directed-event"),
        coord_priv)

    # Operator should now have 1 unread event
    assert bus_unread.bus_unread_count(repo_dir, "operator") == 1
    unread_evs = bus_unread.bus_unread_events(repo_dir, "operator")
    assert len(unread_evs) == 1
    assert unread_evs[0].id == "directed-event"
    assert (
        bus_unread.format_unread(unread_evs[0]) == "seq1:candidate:coordinator->operator:A:c1"
    )

    # Advance operator cursor to cover the event
    store.advance_cursor("operator", 1)
    assert bus_unread.bus_unread_count(repo_dir, "operator") == 0
