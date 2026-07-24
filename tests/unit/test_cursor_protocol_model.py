from __future__ import annotations

import pytest

from scripts import codex_protocol_model as canonical
from scripts import cursor_protocol_model as cursor


@pytest.mark.parametrize(
    ("seat", "mode", "role", "behavior", "verification"),
    [
        ("director", "live-seat", "director", "director", "request-operator-go"),
        ("director2", "live-seat", "director2", "director", "request-operator-go"),
        ("operator", "live-seat", "operator", "operator2", "independent-go-nits-fail"),
        ("operator2", "live-seat", "operator2", "operator2", "independent-go-nits-fail"),
        ("coordinator", "coordinator", "coordinator", "(none)", "reconcile-operator-go-only"),
    ],
)
def test_cursor_runtime_maps_concrete_seats_to_canonical_contract(
    seat: str,
    mode: str,
    role: str,
    behavior: str,
    verification: str,
) -> None:
    values = cursor.infer_runtime_env({"CURSOR_SEAT": seat})
    assert values["CURSOR_AGENT_MODE"] == mode
    assert values["CURSOR_AGENT_ROLE"] == role
    assert values["CURSOR_SEAT"] == seat
    assert values["CURSOR_BEHAVIOR_SOURCE"] == behavior
    assert values["CURSOR_VERIFICATION_POLICY"] == verification
    assert values["CURSOR_SIDE_EFFECT_POLICY"] == "user-consent-required"


def test_cursor_runtime_defaults_to_readiness_without_seat_authority() -> None:
    values = cursor.infer_runtime_env({})
    assert values["CURSOR_AGENT_MODE"] == "readiness-bridge"
    assert values["CURSOR_SEAT"] == "(unset)"
    assert values["CURSOR_MUTATION_SCOPE"] == "none"
    assert values["CURSOR_MAILBOX_POLICY"] == "read-only-no-consume"


def test_cursor_subagent_stays_parent_scoped_even_with_inherited_seat() -> None:
    values = cursor.infer_runtime_env(
        {
            "CURSOR_AGENT_MODE": "subagent",
            "CURSOR_AGENT_ROLE": "lane-v-verifier",
            "CURSOR_SEAT": "operator",
        }
    )
    assert values["CURSOR_AGENT_MODE"] == "subagent"
    assert values["CURSOR_SEAT"] == "(ignored: operator)"
    assert values["CURSOR_AUTHORITY_SCOPE"] == "parent-scoped"


def test_cursor_adapter_does_not_emit_codex_authority_keys() -> None:
    values = cursor.infer_runtime_env({"CURSOR_SEAT": "director"})
    assert values
    assert not any(key.startswith("CODEX_") for key in values)


def test_cursor_contract_tracks_canonical_mode_semantics() -> None:
    cursor_values = cursor.infer_runtime_env({"CURSOR_SEAT": "operator2"})
    canonical_values = canonical.infer_runtime_env({"CODEX_SEAT": "operator2"})
    pairs = {
        "CURSOR_AGENT_MODE": "CODEX_AGENT_MODE",
        "CURSOR_AGENT_ROLE": "CODEX_AGENT_ROLE",
        "CURSOR_BEHAVIOR_SOURCE": "CODEX_BEHAVIOR_SOURCE",
        "CURSOR_CAPABILITY_MODE": "CODEX_CAPABILITY_MODE",
        "CURSOR_MUTATION_SCOPE": "CODEX_MUTATION_SCOPE",
        "CURSOR_AUTHORITY_SCOPE": "CODEX_AUTHORITY_SCOPE",
        "CURSOR_MAILBOX_POLICY": "CODEX_MAILBOX_POLICY",
        "CURSOR_VERIFICATION_POLICY": "CODEX_VERIFICATION_POLICY",
        "CURSOR_DECISION_BOUNDARY": "CODEX_DECISION_BOUNDARY",
    }
    for cursor_key, canonical_key in pairs.items():
        assert cursor_values[cursor_key] == canonical_values[canonical_key]


def test_cursor_app_overrides_only_provider_specific_git_mechanics() -> None:
    director = cursor.infer_runtime_env({"CURSOR_SEAT": "director"})
    operator = cursor.infer_runtime_env({"CURSOR_SEAT": "operator"})
    assert director["CURSOR_GIT_POLICY"] == "native-worktree-index"
    assert (
        operator["CURSOR_GIT_POLICY"]
        == "native-worktree-index-read-only-except-own-fixed-writer-event"
    )


def test_cursor_contract_documents_app_native_transport() -> None:
    rendered = cursor.render_runtime_env_contract({})
    assert "Cursor Desktop/Agents Window" in rendered
    assert "cursor-seat/<seat>" in rendered
    assert "conversation id" in rendered
    assert "selected model-id" in rendered
    assert "native Git index" in rendered
    assert "review-next" in rendered
    assert "one manual app handoff" in rendered
    assert "provider_side=cursor" in rendered
    assert "foreign_launch=denied" in rendered
    assert "cursor-agent" not in rendered
