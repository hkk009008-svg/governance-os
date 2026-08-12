"""Tests for the AGY-only runtime identity adapter."""

from __future__ import annotations

import inspect

import agy_protocol_model as protocol


def test_advisory_runtime_is_agy_named_and_has_no_shared_seat_identity() -> None:
    values = protocol.infer_runtime_env(
        profile="director",
        mode=protocol.ADVISORY_MODE,
    )

    assert values == {
        "AGY_SEAT": "agy-advisory",
        "AGY_AGENT_MODE": "advisory-readiness",
        "AGY_AGENT_ROLE": "readiness-bridge",
        "AGY_BEHAVIOR_SOURCE": "advisory-read-only",
    }
    assert not any(key.startswith("CODEX_") for key in values)


def test_single_model_runtime_is_explicitly_namespaced() -> None:
    values = protocol.infer_runtime_env(
        profile="operator2",
        mode=protocol.SINGLE_MODEL_MODE,
    )

    assert values["AGY_SEAT"] == "agy-unit-operator2"
    assert values["AGY_AGENT_MODE"] == "single-model-autonomous"
    assert values["AGY_AGENT_ROLE"] == "agy-unit-operator2"
    assert values["AGY_BEHAVIOR_SOURCE"] == "agy-unit-operator2"


def test_infer_runtime_env_defaults_to_single_model_autonomous() -> None:
    values = protocol.infer_runtime_env(profile="director")

    assert values["AGY_SEAT"] == "agy-unit-director"
    assert values["AGY_AGENT_MODE"] == "single-model-autonomous"
    assert values["AGY_AGENT_ROLE"] == "agy-unit-director"
    assert values["AGY_BEHAVIOR_SOURCE"] == "agy-unit-director"


def test_runtime_identity_carries_no_index_binding() -> None:
    """A profile selects a model, not a Git index.

    AGY was the last side exporting `GIT_INDEX_FILE` and seeding a per-seat
    index. Identity that lives in an inherited environment variable can be
    forged by any process and cannot be set by a desktop app at all; every
    worktree now uses its native index.
    """
    assert "index_path" not in inspect.signature(protocol.infer_runtime_env).parameters

    for mode in protocol.MODES:
        values = protocol.infer_runtime_env(profile="director", mode=mode)
        assert not any("INDEX" in key for key in values)
