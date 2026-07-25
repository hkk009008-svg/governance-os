#!/usr/bin/env python3
"""AGY-only runtime identity for isolated local launch profiles."""

from __future__ import annotations


ADVISORY_MODE = "advisory"
SINGLE_MODEL_MODE = "single-model-autonomous"
MODES = (ADVISORY_MODE, SINGLE_MODEL_MODE)


class RuntimeIdentityError(ValueError):
    """Raised when an AGY launch mode cannot be represented safely."""


def infer_runtime_env(*, profile: str, mode: str = SINGLE_MODEL_MODE, index_path: str) -> dict[str, str]:
    """Return only AGY-owned identity for one local launch profile.

    A profile selects local model and index settings. It is never a shared
    Codex, Claude, or Cursor seat identity.
    """

    if mode == ADVISORY_MODE:
        return {
            "AGY_SEAT": "agy-advisory",
            "AGY_AGENT_MODE": "advisory-readiness",
            "AGY_AGENT_ROLE": "readiness-bridge",
            "AGY_BEHAVIOR_SOURCE": "advisory-read-only",
            "AGY_GIT_INDEX_FILE": index_path,
        }
    if mode == SINGLE_MODEL_MODE:
        identity = f"agy-unit-{profile}"
        return {
            "AGY_SEAT": identity,
            "AGY_AGENT_MODE": SINGLE_MODEL_MODE,
            "AGY_AGENT_ROLE": identity,
            "AGY_BEHAVIOR_SOURCE": identity,
            "AGY_GIT_INDEX_FILE": index_path,
        }
    raise RuntimeIdentityError(f"unsupported AGY mode: {mode}")
