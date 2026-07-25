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
    explicit_subagent = source.get("CURSOR_AGENT_MODE") == "subagent"
    translated = {
        canonical_key: source[cursor_key]
        for cursor_key, canonical_key in _INPUT_KEYS.items()
        if cursor_key in source
        and not (explicit_subagent and cursor_key == "CURSOR_SEAT")
    }
    values = canonical.infer_runtime_env(translated)
    cursor_values = {
        key.replace("CODEX_", "CURSOR_", 1): value
        for key, value in values.items()
        if key.startswith("CODEX_")
    }
    seat = cursor_values.get("CURSOR_SEAT", "(unset)")
    if seat in {"director", "director2"}:
        cursor_values["CURSOR_GIT_POLICY"] = "native-worktree-index"
    elif seat in {"operator", "operator2", "coordinator"}:
        cursor_values["CURSOR_GIT_POLICY"] = (
            "native-worktree-index-read-only-except-own-fixed-writer-event"
        )
    return cursor_values


def render_runtime_env_contract(
    environ: Mapping[str, str] | None = None,
) -> str:
    values = infer_runtime_env(environ)
    lines = ["Cursor Desktop app-seat contract:"]
    lines.extend(f"{key}={value}" for key, value in values.items())
    lines.extend(
        (
            "contract rules:",
            "- Cursor Desktop/Agents Window is the normal runtime.",
            "- readiness is the default outside a linked cursor-seat/<seat> worktree.",
            "- a live seat requires worktree branch, conversation id, and selected model-id agreement.",
            "- each seat uses its linked worktree's native Git index; GIT_INDEX_FILE is rejected.",
            "- Director seats may implement; Operator and Coordinator seats are repository-tree read-only.",
            "- custom subagents are advisors and never publish verdicts or inherit seat authority.",
            "- mailbox publication goes through cursor-publish and requires an in-app approval.",
            "- review-next resolves the next committed request without copied prompt bodies or refs.",
            "- activating another existing local top-level chat is the one manual app handoff.",
            "- provider_side=cursor",
            "- foreign_launch=denied",
        )
    )
    return "\n".join(lines)
