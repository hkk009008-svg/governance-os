"""What a peer's output is allowed to say about itself.

The receipt's headline fact is the model the peer's OWN output reported. These
controls are the ways that fact was wrong: a JSON null rendered as the four
characters "None", valid JSON that was not an object raising out of run(), an
arbitrary modelUsage key naming a model that may not have done the work, and a
missing model returning with empty notes while the contract promised absence is
always narrated.
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

import peer
import peer_backends

from test_peer import _spec, peers_on_path  # noqa: F401 — fixture re-export


def test_a_null_result_is_absence_not_the_string_None(tmp_path: Path) -> None:
    """Codex finding: str(payload.get("result")) rendered JSON null as "None".

    Those four characters were printed to the operator as the peer's answer and
    hashed into result_sha256.
    """

    def null_result(argv, **kwargs):
        return subprocess.CompletedProcess(argv, 0, json.dumps({"result": None}), "")

    outcome = peer.run(_spec(tmp_path, "claude"), "prompt", runner=null_result)

    assert outcome.result == ""
    assert "None" not in outcome.result


def test_json_that_is_not_an_object_does_not_lose_the_run(tmp_path: Path) -> None:
    """Valid JSON that is not a dict used to raise out of run(), losing the receipt."""

    def a_bare_list(argv, **kwargs):
        return subprocess.CompletedProcess(argv, 0, json.dumps([1, 2, 3]), "")

    outcome = peer.run(_spec(tmp_path, "claude"), "prompt", runner=a_bare_list)

    assert outcome.model_reported is None
    assert any("not an object" in note for note in outcome.notes)


def test_two_models_are_reported_as_neither(tmp_path: Path) -> None:
    """Picking an arbitrary modelUsage key names a model that may not have worked."""

    def multi(argv, **kwargs):
        return subprocess.CompletedProcess(
            argv, 0,
            json.dumps({"modelUsage": {"claude-opus-5": {}, "claude-haiku-4-5": {}},
                        "result": "done"}),
            "",
        )

    outcome = peer.run(_spec(tmp_path, "claude"), "prompt", runner=multi)

    assert outcome.model_reported is None
    assert any("multiple models" in note for note in outcome.notes)


def test_an_absent_model_is_always_narrated(tmp_path: Path) -> None:
    """docs/protocol/peer.md states an empty notes with a null model is impossible.

    It was possible on the claude side: a payload with no model and no
    modelUsage returned (None, ..., []). The doc asserted an invariant the code
    did not hold.
    """

    def silent(argv, **kwargs):
        return subprocess.CompletedProcess(argv, 0, json.dumps({"result": "done"}), "")

    outcome = peer.run(_spec(tmp_path, "claude"), "prompt", runner=silent)

    assert outcome.model_reported is None
    assert outcome.notes, "a null model with empty notes is the documented impossibility"


@pytest.mark.parametrize(
    "role,read_only,expected",
    [("implement", True, "pass --write"), ("challenge", False, "no meaning for agy role")],
)
def test_agy_write_intent_must_match_its_role(tmp_path: Path, role, read_only, expected) -> None:
    """--write and read_only were silently inert for agy, promising containment.

    The wrapper has no read-only flag, so accepting --write without effect let a
    caller believe in a boundary that was never applied.
    """

    with pytest.raises(peer_backends.PeerError, match=expected):
        peer_backends.build(_spec(tmp_path, "agy", role=role, read_only=read_only))
