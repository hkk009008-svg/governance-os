"""Tests for the AGY-only runtime identity adapter."""

from __future__ import annotations

from scripts import agy_protocol_model as protocol


def test_advisory_runtime_is_agy_named_and_has_no_shared_seat_identity() -> None:
    values = protocol.infer_runtime_env(
        profile="director",
        mode=protocol.ADVISORY_MODE,
        index_path="/repo/.git/index-agy-director",
    )

    assert values == {
        "AGY_SEAT": "agy-advisory",
        "AGY_AGENT_MODE": "advisory-readiness",
        "AGY_AGENT_ROLE": "readiness-bridge",
        "AGY_BEHAVIOR_SOURCE": "advisory-read-only",
        "AGY_GIT_INDEX_FILE": "/repo/.git/index-agy-director",
    }
    assert not any(key.startswith("CODEX_") for key in values)


def test_single_model_runtime_is_explicitly_namespaced() -> None:
    values = protocol.infer_runtime_env(
        profile="operator2",
        mode=protocol.SINGLE_MODEL_MODE,
        index_path="/repo/.git/index-agy-operator2",
    )

    assert values["AGY_SEAT"] == "agy-unit-operator2"
    assert values["AGY_AGENT_MODE"] == "single-model-autonomous"
    assert values["AGY_AGENT_ROLE"] == "agy-unit-operator2"
    assert values["AGY_BEHAVIOR_SOURCE"] == "agy-unit-operator2"
