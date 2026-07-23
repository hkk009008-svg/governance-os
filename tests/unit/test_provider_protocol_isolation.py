"""Cross-provider environment containment regressions."""

from __future__ import annotations

import pytest

from scripts import agy_protocol_model as agy
from scripts import codex_protocol_model as codex


FOREIGN_PREFIXES = ("AGY", "ANTIGRAVITY", "CLAUDE", "CURSOR")
AGY_PROFILE_LABELS = ("director", "director2", "operator", "operator2", "coordinator")
FOREIGN_IDENTITY_VALUES = {
    "SEAT": "director",
    "AGENT_MODE": "live-seat",
    "AGENT_ROLE": "director",
    "BEHAVIOR_SOURCE": "foreign-behavior-source",
    "GIT_INDEX_FILE": "/foreign/.git/index",
}
FOREIGN_POLICY_VALUES = {
    "CAPABILITY_MODE": "foreign-capability",
    "MUTATION_SCOPE": "foreign-mutation",
    "AUTHORITY_SCOPE": "foreign-authority",
    "MAILBOX_POLICY": "foreign-mailbox",
    "GIT_POLICY": "foreign-git",
    "VERIFICATION_POLICY": "foreign-verification",
    "CONTEXT_SOURCES": "foreign-context",
    "OUTPUT_CONTRACT": "foreign-output",
    "DECISION_BOUNDARY": "foreign-decision",
    "NEXT_ACTION_POLICY": "foreign-next-action",
}


def _codex_baseline() -> dict[str, str]:
    return codex.infer_runtime_env({})


@pytest.mark.parametrize("prefix", FOREIGN_PREFIXES)
@pytest.mark.parametrize("profile", AGY_PROFILE_LABELS)
def test_foreign_profile_labels_never_select_a_codex_live_seat(
    prefix: str, profile: str
) -> None:
    values = codex.infer_runtime_env({f"{prefix}_SEAT": profile})

    assert values == _codex_baseline()
    assert values["CODEX_AGENT_MODE"] == "readiness-bridge"
    assert values["CODEX_SEAT"] == "(unset)"


@pytest.mark.parametrize("prefix", FOREIGN_PREFIXES)
@pytest.mark.parametrize("suffix", FOREIGN_IDENTITY_VALUES)
def test_every_foreign_identity_input_is_inert_to_every_codex_output(
    prefix: str, suffix: str
) -> None:
    values = codex.infer_runtime_env(
        {f"{prefix}_{suffix}": FOREIGN_IDENTITY_VALUES[suffix]}
    )

    assert values == _codex_baseline()


@pytest.mark.parametrize("prefix", FOREIGN_PREFIXES)
@pytest.mark.parametrize("suffix", FOREIGN_POLICY_VALUES)
def test_every_foreign_policy_input_is_inert_to_every_codex_output(
    prefix: str, suffix: str
) -> None:
    values = codex.infer_runtime_env(
        {f"{prefix}_{suffix}": FOREIGN_POLICY_VALUES[suffix]}
    )

    assert values == _codex_baseline()


@pytest.mark.parametrize("profile", AGY_PROFILE_LABELS)
def test_all_agy_profile_runtime_labels_are_inert_to_codex(profile: str) -> None:
    agy_runtime = agy.infer_runtime_env(
        profile=profile,
        mode=agy.SINGLE_MODEL_MODE,
        index_path=f"/repo/.git/index-agy-{profile}",
    )

    assert set(agy_runtime) == {
        "AGY_SEAT",
        "AGY_AGENT_MODE",
        "AGY_AGENT_ROLE",
        "AGY_BEHAVIOR_SOURCE",
        "AGY_GIT_INDEX_FILE",
    }
    assert codex.infer_runtime_env(agy_runtime) == _codex_baseline()


def test_genuine_codex_inputs_continue_to_drive_codex_contract() -> None:
    policy = {
        f"CODEX_{suffix}": f"codex-{value}"
        for suffix, value in FOREIGN_POLICY_VALUES.items()
    }
    values = codex.infer_runtime_env(
        {
            "CODEX_SEAT": "operator2",
            "CODEX_AGENT_MODE": "live-seat",
            "CODEX_AGENT_ROLE": "operator2",
            **policy,
        }
    )

    assert values["CODEX_AGENT_MODE"] == "live-seat"
    assert values["CODEX_AGENT_ROLE"] == "operator2"
    assert values["CODEX_SEAT"] == "operator2"
    assert values["CODEX_BEHAVIOR_SOURCE"] == "operator2"
    for suffix, value in policy.items():
        assert values[suffix] == value
