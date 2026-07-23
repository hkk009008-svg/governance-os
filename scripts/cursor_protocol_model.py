#!/usr/bin/env python3
"""Cursor naming adapter for Pipeline's canonical seat runtime contract."""

from __future__ import annotations

from collections.abc import Mapping

try:
    from scripts import codex_protocol_model as canonical
except ModuleNotFoundError:
    import codex_protocol_model as canonical


_INPUT_KEYS = {
    "CURSOR_AGENT_MODE": "CODEX_AGENT_MODE",
    "CURSOR_AGENT_ROLE": "CODEX_AGENT_ROLE",
    "CURSOR_SEAT": "CODEX_SEAT",
    "CURSOR_BEHAVIOR_SOURCE": "CODEX_BEHAVIOR_SOURCE",
    "CURSOR_CAPABILITY_MODE": "CODEX_CAPABILITY_MODE",
    "CURSOR_MUTATION_SCOPE": "CODEX_MUTATION_SCOPE",
    "CURSOR_AUTHORITY_SCOPE": "CODEX_AUTHORITY_SCOPE",
    "CURSOR_MAILBOX_POLICY": "CODEX_MAILBOX_POLICY",
    "CURSOR_GIT_POLICY": "CODEX_GIT_POLICY",
    "CURSOR_VERIFICATION_POLICY": "CODEX_VERIFICATION_POLICY",
    "CURSOR_CONTEXT_SOURCES": "CODEX_CONTEXT_SOURCES",
    "CURSOR_OUTPUT_CONTRACT": "CODEX_OUTPUT_CONTRACT",
    "CURSOR_DECISION_BOUNDARY": "CODEX_DECISION_BOUNDARY",
    "CURSOR_NEXT_ACTION_POLICY": "CODEX_NEXT_ACTION_POLICY",
}


def infer_runtime_env(environ: Mapping[str, str] | None = None) -> dict[str, str]:
    """Infer Cursor's contract without presenting Codex variables as authority."""

    source = environ or {}
    translated = {
        canonical_key: source[cursor_key]
        for cursor_key, canonical_key in _INPUT_KEYS.items()
        if cursor_key in source
    }
    if "GIT_INDEX_FILE" in source:
        translated["GIT_INDEX_FILE"] = source["GIT_INDEX_FILE"]
    values = canonical.infer_runtime_env(translated)
    result = {
        key.replace("CODEX_", "CURSOR_", 1): value
        for key, value in values.items()
        if key.startswith("CODEX_")
    }
    result["CURSOR_GIT_INDEX_FILE"] = values["GIT_INDEX_FILE"]
    return result


def render_runtime_env_contract(
    environ: Mapping[str, str] | None = None,
) -> str:
    """Render the Cursor-specific names and canonical inferred values."""

    values = infer_runtime_env(environ)
    lines = ["Cursor runtime env contract:"]
    lines.extend(f"{key}={value}" for key, value in values.items())
    lines.extend(
        (
            "contract rules:",
            "- ordinary Cursor chat defaults to readiness-bridge.",
            "- only the Cursor seat launcher binds a top-level live seat.",
            "- Cursor subagents remain parent-scoped and never inherit seat authority.",
            "- environment values describe identity and never authorize external effects.",
        )
    )
    return "\n".join(lines)
